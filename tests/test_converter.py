import copy
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from naisi_qx.converter import (Conversion, ConversionError, FILTER_TYPES, cats_compare,
    finite_hosts, host_globs, host_matches, jq_error, parse_filter, parse_rewrite, validate_outputs)
from naisi_qx.network import PublicRedirect, audit_dependency, canonical_url, digest, resolve_commit
from naisi_qx.pipeline import promote, stable_audits, verify_candidate
from naisi_qx.reporting import dumps, validation_report
from tools.icu_regex import ICURegex


class SyntaxTests(unittest.TestCase):
    def test_split_never_mixes_rule_families(self):
        c = Conversion('# > 测试\nhost-suffix, ads.example.com, reject\n^https://api\\.example\\.com/ads url reject\nhostname = api.example.com\n')
        self.assertEqual(validate_outputs(c, c.render('rewrite'), c.render('filter')), [])
        active = lambda t: [x for x in t.splitlines() if x and not x.startswith(('#',';','//'))]
        self.assertFalse(any(x.startswith('host-suffix,') for x in active(c.render('rewrite'))))
        self.assertFalse(any(' url ' in x for x in active(c.render('filter'))))

    def test_output_validator_rejects_cross_contamination(self):
        c = Conversion('^https://example.com/ad url reject')
        self.assertTrue(validate_outputs(c, c.render('rewrite') + 'host, bad.example, reject\n', ''))
        self.assertTrue(validate_outputs(c, c.render('rewrite'), '^https://x/ad url reject\n'))

    def test_alias_case_and_subnet_normalization(self):
        self.assertEqual(parse_filter('DOMAIN, Ads.Example.com, REJECT').output, 'host, ads.example.com, reject')
        self.assertEqual(parse_filter('IP-CIDR, 203.107.1.1/24, reject').value, '203.107.1.0/24')

    def test_cidr_families_and_other_policies_fail(self):
        for value in ['ip-cidr, ::1/128, reject', 'ip6-cidr, 1.2.3.4/32, reject', 'host, x.com, direct']:
            with self.subTest(value=value), self.assertRaises(ConversionError):
                parse_filter(value)

    def test_unknown_rule_and_invalid_domain_are_visible(self):
        c = Conversion('^https://x.com/ad url reject\nweird, x.com, reject\nhost-suffix, -bad.example.com, reject\n')
        self.assertEqual([r.status for r in c.rules], ['kept', 'quarantined', 'quarantined'])
        self.assertTrue(all(r.raw and r.evidence and r.alternative for r in c.rules[1:]))

    def test_user_agent_not_confused_with_domain_or_rewrite(self):
        c = Conversion('USER-AGENT,AVOS*,reject\n^http://example.com/ad url reject')
        self.assertEqual(c.rules[0].status, 'quarantined')
        self.assertIn('QX 官方支持', c.rules[0].alternative)

    def test_surge_hyphen_rewrite_and_http_typo(self):
        r = parse_rewrite(r'^http?:\/\/static.psbc.com:8090/a - reject-200')
        self.assertEqual(r.action, 'reject-200')
        self.assertTrue(r.pattern.startswith('^https?:'))
        self.assertEqual(len(r.fixes), 2)

    def test_valid_icu_specific_syntax_is_not_deleted_by_python(self):
        pattern = r'^https://(?>csc|osg)-service\.sgcc\.com\.cn:\d+/ad'
        self.assertIsNone(ICURegex().error(pattern))
        c = Conversion(pattern + ' url reject\nhostname = osg-service.sgcc.com.cn')
        self.assertEqual(c.rules[0].status, 'kept')

    def test_invalid_regex_is_quarantined_with_original(self):
        c = Conversion(r'^https://example.com/[ url reject' + '\n^https://ok.com/ad url reject')
        self.assertEqual(c.rules[0].status, 'quarantined')
        self.assertIn('ICU', ' '.join(c.rules[0].risks))
        self.assertIn('[', c.rules[0].raw)

    def test_response_body_second_pattern_is_checked(self):
        c = Conversion(r'^https://example.com/ad url response-body [ response-body ok')
        self.assertEqual(c.rules[0].status, 'quarantined')

    def test_all_supported_actions_survive(self):
        rules = [
            '^https://a.com/1 url reject-array',
            '^https://a.com/2 url script-request-body https://example.com/a.js',
            '^https://a.com/3 url script-response-body https://example.com/b.js',
            '^https://a.com/4 url response-body foo response-body bar',
            "^https://a.com/5 url jsonjq-response-body '.data = []'",
            '^http://a.com/6 ^POST url-and-header reject',
        ]
        c = Conversion('\n'.join(rules))
        self.assertEqual(len(c.kept()), len(rules))

    def test_unknown_action_not_invented(self):
        c = Conversion('^https://a.com/ad url magical-action yes')
        self.assertEqual(c.rules[0].status, 'quarantined')
        self.assertIn('magical-action', ' '.join(c.rules[0].risks))

    def test_jsonjq_is_compiled_and_quote_repaired(self):
        r = parse_rewrite('^https://a.com/ad url jsonjq-response-body .data = []')
        self.assertEqual(r.argument, "'.data = []'")
        self.assertIsNone(jq_error(r.argument))
        with self.assertRaises(ConversionError):
            parse_rewrite("^https://a.com/ad url jsonjq-response-body 'del('")

    def test_jsonjq_same_match_compose_both_effects(self):
        c = Conversion("^https://a.com/ad url jsonjq-response-body '.a = []'\n^https://a.com/ad url jsonjq-response-body '.b = []'")
        self.assertEqual(c.rules[1].status, 'merged')
        result = subprocess.run(['jq', c.rules[0].argument[1:-1]], input='{"a":[1],"b":[2],"normal":3}', text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), {'a': [], 'b': [], 'normal': 3})

    def test_conflicts_keep_first_and_show_original_second(self):
        c = Conversion('^https://a.com/ad url reject-dict\n^https://a.com/ad url reject-img')
        self.assertEqual(c.kept()[0].action, 'reject-dict')
        self.assertEqual(c.rules[1].status, 'quarantined')
        self.assertEqual(c.rules[1].references, [1])

    def test_dedup_preserves_app_provenance_and_literal_slashes(self):
        c = Conversion('# > AppA\n^https:\\/\\/a\\.com/ad url reject\n# > AppB\n^https://a\\.com/ad url reject')
        self.assertEqual(c.rules[1].status, 'duplicate')
        self.assertEqual(c.rules[1].app, 'AppB')
        self.assertEqual(c.rules[1].references, [2])
        self.assertEqual(c.coverage()['apps']['AppB']['represented'], 1)

    def test_regex_case_is_never_lowercased_for_dedup(self):
        c = Conversion('^https://a.com/AD url reject\n^https://a.com/ad url reject')
        self.assertEqual(len(c.kept()), 2)

    def test_critical_semantic_typos_fixed_narrowly(self):
        r = parse_rewrite(r'^http?:\/\/(114\.115\.217\.129)|(home\.umetrip\.com)\/gateway\/api\/umetrip\/native$ url reject')
        self.assertNotIn(')|(', r.pattern)
        r = parse_rewrite(r'^https?:\/\/res\.kfc\.com.\cn\/advertisement\/ url reject')
        self.assertIn(r'com\.cn', r.pattern)


class MITMTests(unittest.TestCase):
    def test_hostnames_trace_to_active_https_rewrites(self):
        c = Conversion('^https://a\\.example\\.com/ad url reject\nhostname = a.example.com, unused.example.com')
        self.assertEqual(c.hosts, ['a.example.com'])
        self.assertEqual(c.hostname_audit[0]['source_lines'], [1])
        self.assertEqual(c.hostname_audit[1]['status'], 'inactive')

    def test_http_does_not_expand_mitm(self):
        c = Conversion('^http://a\\.example\\.com/ad url reject\nhostname = a.example.com')
        self.assertEqual(c.hosts, [])

    def test_optional_and_pinning_do_not_enable_hosts(self):
        c = Conversion('# > 测试\n# hostname = a.example.com\n# 已无法MITM\n^https://a\\.example\\.com/ad url reject\nhostname = a.example.com')
        self.assertEqual(c.hosts, [])
        self.assertEqual(c.mitm_rule_audit[0]['status'], 'optional')

    def test_negative_exclusion_survives_without_unconfirmed_minus_syntax(self):
        c = Conversion('^https://ad\\.iqiyi\\.com/ad url reject\n^https://i\\.vip\\.iqiyi\\.com/ad url reject\nhostname = -i.vip.iqiyi.com, *.iqiyi.com')
        self.assertIn('ad.iqiyi.com', c.hosts)
        self.assertNotIn('*.iqiyi.com', c.hosts)
        self.assertNotIn('i.vip.iqiyi.com', c.hosts)

    def test_finite_host_expansion_and_ports(self):
        self.assertEqual(finite_hosts(r'^https://(cl-)?gateway\.tuhu\.cn(/cl)?/ad'), ['cl-gateway.tuhu.cn', 'gateway.tuhu.cn'])
        self.assertTrue(host_matches(r'appapi\.huazhu\.com:\d+', 'appapi.huazhu.com'))
        self.assertIn('*.byteimg.com', host_globs(r'^https://.+\.byteimg\.com/ad'))

    def test_host_crossing_path_alternatives_keep_all_hints(self):
        c = Conversion('# > 测试\n# hostname = a.example.com, b.example.com\n^https://(a\\.example\\.com/ads|b\\.example\\.com/feed) url reject\nhostname = a.example.com, b.example.com')
        self.assertEqual(c.hosts, ['a.example.com','b.example.com'])

    def test_dynamic_ip_never_creates_global_star(self):
        c = Conversion(r'^https://[\d\.]+/ad url reject')
        self.assertEqual(c.hosts, [])
        self.assertEqual(c.mitm_rule_audit[0]['status'], 'unresolved')

    def test_finite_missing_hostname_can_be_added(self):
        c = Conversion('^https://missing\\.example\\.com/ad url reject')
        self.assertEqual(c.hosts, ['missing.example.com'])


class DependencyAndReleaseTests(unittest.TestCase):
    def test_api_limit_falls_back_to_existing_readonly_gh(self):
        info={'sha':'a'*40,'commit':{'committer':{'date':'2026-01-01T00:00:00Z'}}}
        process=subprocess.CompletedProcess([],0,json.dumps(info),'')
        with patch('naisi_qx.network.get',side_effect=RuntimeError('403 rate limit')), \
             patch('naisi_qx.network.shutil.which',return_value='/usr/bin/gh'), \
             patch('naisi_qx.network.subprocess.run',return_value=process) as run:
            result=resolve_commit('fmz200/wool_scripts','main')
        self.assertEqual(result['commit'],'a'*40)
        self.assertEqual(run.call_args.args[0],['gh','api','repos/fmz200/wool_scripts/commits/main'])

    def test_token_not_forwarded_to_raw_or_script_host(self):
        from urllib.request import Request
        request=Request('https://api.github.com/repos/a/b',headers={'Authorization':'Bearer fake-test-only'})
        new=PublicRedirect().redirect_request(request,None,302,'redirect',{},'https://raw.githubusercontent.com/a/b/main/a.js')
        self.assertFalse(new.has_header('Authorization'))

    def test_github_raw_normalization_keeps_ref_path_and_fragment(self):
        self.assertEqual(canonical_url('https://github.com/a/b/raw/main/dir/a.js#key=1'),
                         'https://raw.githubusercontent.com/a/b/main/dir/a.js#key=1')

    def test_failed_or_missing_script_never_silent(self):
        source = '^https://a.com/ad url script-response-body https://x.com/a.js'
        for checks in [{}, {'https://x.com/a.js': {'ok': False, 'error': 'HTTP 404'}}]:
            c = Conversion(source, dependencies=checks)
            self.assertTrue(c.gate_errors)
            self.assertEqual(c.rules[0].status, 'quarantined')

    def test_html_payload_rejected_even_if_200(self):
        with tempfile.TemporaryDirectory() as tmp, patch('naisi_qx.network.get', return_value=(b'<html>Not a script</html>', {'status':200,'final_url':'https://x/a.js','content_type':'text/html'})):
            result = audit_dependency('https://x/a.js', Path(tmp))
        self.assertFalse(result['ok'])
        self.assertIn('HTML', result['error'])

    def test_javascript_syntax_failure_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp, patch('naisi_qx.network.get', return_value=(b'function {', {'status':200,'final_url':'https://x/a.js','content_type':'text/plain'})):
            result = audit_dependency('https://x/a.js', Path(tmp))
        self.assertFalse(result['ok'])
        self.assertFalse(result['syntax']['ok'])

    def test_remote_echo_becomes_identical_local_data(self):
        url = 'https://x.com/data.json'
        data = b'{"data":[]}'
        checks = {url: {'ok':True,'cache_file':'body.json','sha256':digest(data)}}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,'body.json').write_bytes(data)
            c = Conversion('^https://a.com/ad url echo-response application/json echo-response ' + url,
                           dependencies=checks,data_cache=Path(tmp))
        self.assertEqual(list(c.assets.values()), [data])
        self.assertNotIn('https://x', c.kept()[0].argument)

    def test_identical_network_inputs_are_idempotent(self):
        a = {'x': {'ok':True,'sha256':'a','checked_at':'old'}}
        b = {'x': {'ok':True,'sha256':'a','checked_at':'new'}}
        self.assertEqual(stable_audits(b,a), a)
        b['x']['sha256'] = 'b'
        b['x']['checked_at'] = 'latest'
        self.assertEqual(stable_audits(b,a)['x']['checked_at'], 'latest')

    def test_invalid_candidate_preserves_last_valid_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate, output = root/'candidate', root/'output'
            candidate.mkdir(); output.mkdir()
            (output/'Naisi-QX-Rewrite.conf').write_text('last-valid')
            (candidate/'manifest.json').write_text(dumps({'valid':False,'files':{}}))
            with self.assertRaises(ConversionError):
                promote(candidate, output)
            self.assertEqual((output/'Naisi-QX-Rewrite.conf').read_text(), 'last-valid')

    def test_manifest_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'Naisi-QX-Rewrite.conf').write_text('changed')
            (root/'manifest.json').write_text(dumps({'valid':True,'files':{'Naisi-QX-Rewrite.conf':digest(b'original')}}))
            with self.assertRaises(ConversionError):
                verify_candidate(root)

    def test_manifest_cannot_write_source_or_escape(self):
        for name in ['../danger', '.git/config', 'update.py', 'README.md']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                (root/'manifest.json').write_text(dumps({'valid':True,'files':{name:'fake'}}))
                with self.assertRaises(ConversionError):
                    verify_candidate(root)

    def test_publish_rolls_back_if_second_file_cannot_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); candidate=root/'candidate'; output=root/'output'
            candidate.mkdir(); output.mkdir()
            files=['Naisi-QX-Rewrite.conf','Naisi-QX-Filter.list']
            for name in files:
                (candidate/name).write_text('new'); (output/name).write_text('old')
            (candidate/'manifest.json').write_text(dumps({'valid':True,'files':{name:digest(b'new') for name in files}}))
            real_replace=os.replace
            def replace(source,target):
                if Path(target).name=='Naisi-QX-Filter.list':
                    raise OSError('simulated disk failure')
                return real_replace(source,target)
            with patch('naisi_qx.pipeline.os.replace',side_effect=replace),self.assertRaises(OSError):
                promote(candidate,output)
            self.assertTrue(all((output/name).read_text()=='old' for name in files))


class CatsTests(unittest.TestCase):
    def test_exact_and_parent_suffix_semantic_coverage(self):
        rules = [parse_filter(x) for x in ['host, ad.example.com, reject', 'host-suffix, example.com, reject', 'host-suffix, unique.cn, reject']]
        result = cats_compare(rules,'host-suffix, example.com, reject')
        self.assertEqual((result['exact'],result['covered'],result['residual']), (1,1,1))

    def test_narrow_cats_rule_does_not_cover_broad_naisi(self):
        result = cats_compare([parse_filter('host-suffix, example.com, reject')], 'host, ad.example.com, reject')
        self.assertEqual(result['residual'],1)

    def test_cidr_and_keywords(self):
        rules = [parse_filter(x) for x in ['ip-cidr, 10.1.1.0/24, reject', 'host, track.example.com, reject']]
        result = cats_compare(rules,'ip-cidr, 10.0.0.0/8, reject\nhost-keyword, track, reject')
        self.assertEqual(result['covered'],2)


class FullSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ.get('NAISI_CANDIDATE', Path(__file__).resolve().parents[1]))
        cls.source_path = cls.root/'upstream/naisi-original.snippet'
        if not cls.source_path.exists():
            raise unittest.SkipTest('没有官方快照；先运行 update.py --bootstrap')
        cls.conversion = Conversion(cls.source_path.read_text())

    def test_every_rule_and_source_line_is_accounted(self):
        c=self.conversion
        s=c.stats()
        self.assertEqual(s['source_rules'],s['output_rewrites']+s['output_filters']+s['duplicates']+s['merged']+s['quarantined'])
        self.assertEqual(len(c.ledger),len(c.source.splitlines()))
        self.assertTrue(all(r.raw for r in c.rules))

    def test_focus_apps_preserve_both_splash_and_in_app_rules(self):
        c=self.conversion
        for app in ['闲鱼','菜鸟裹裹','淘宝','美团','京东','高德地图','滴滴出行','小红书']:
            with self.subTest(app=app):
                # The source uses short names in some headings; the assertion
                # below matches a literal source heading family, not a guessed count.
                matches=[r for r in c.rules if app in r.app or r.app in app]
                self.assertTrue(matches, '重点 App 没有识别到原作者分类')
                self.assertTrue(any(r.status=='kept' for r in matches))
                self.assertTrue(all(r.status!='quarantined' or r.references for r in matches),
                                '重点 App 出现没有替代代表规则的隔离')
        fish=[r for r in c.kept('rewrite') if r.app=='闲鱼']
        self.assertTrue(any('script-response-body'==r.action for r in fish))
        self.assertTrue(any('jsonjq-response-body'==r.action for r in fish))
        self.assertTrue(any('splash' in r.pattern for r in fish))

    def test_no_category_is_wholesale_removed(self):
        c=self.conversion
        for action in ['jsonjq-response-body','script-response-body','response-body','script-request-body','script-analyze-echo-response']:
            self.assertTrue(any(r.action==action and r.status=='kept' for r in c.rules),action)

    def test_original_scripts_and_jsonjq_remain_represented(self):
        c=self.conversion
        selected=[r for r in c.rules if r.action.startswith(('script-','jsonjq-'))]
        self.assertTrue(selected)
        self.assertTrue(all(r.status in {'kept','duplicate','merged'} for r in selected),
                        '脚本或 JSONJQ 出现未保留来源；必须审阅上游功能变化')

    def test_exported_candidate_is_parseable_and_audited(self):
        rewrite=self.root/'Naisi-QX-Rewrite.conf'
        if not rewrite.exists():
            self.skipTest('尚未生成候选文件')
        self.assertEqual(validate_outputs(self.conversion,rewrite.read_text(),(self.root/'Naisi-QX-Filter.list').read_text()),[])
        inventory=json.loads((self.root/'rule-inventory.json').read_text())
        self.assertEqual(len(inventory),len(self.conversion.rules))
        for r in inventory:
            if r['status']!='kept':
                self.assertTrue(r['raw'] and (r['references'] or r['evidence']))
        dependencies=json.loads((self.root/'dependency-audit.json').read_text())
        for url in self.conversion.dependency_urls():
            self.assertIn(url,dependencies)
            self.assertTrue(dependencies[url]['ok'],url)

    def test_mitm_has_provenance_without_universal_hostname(self):
        c=self.conversion
        self.assertNotIn('*',c.hosts)
        self.assertTrue(all(x['source_lines'] for x in c.hostname_audit if x['status']=='active'))


if __name__=='__main__':
    unittest.main()
