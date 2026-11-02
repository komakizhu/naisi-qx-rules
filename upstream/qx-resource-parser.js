/**
 * @fileoverview Example to parse the resource to the format of Quantumult X.
 *
 * @supported Quantumult X (v1.0.8-build253)
 */


// $resource, $notify(title, subtitle, message)
// HTTP reqeust and persistent storage related APIs are not supported in resource parser.

// $resource.link contains the original URL of the resource or the path if the resource is local.
// $resource.content contains the response(UTF8) from the URL .
// For server related resources of v1.0.10-build277, $resource.info contains the response header of field "subscription-userinfo" from the URL.
// For server related resources of v1.0.10-build277, $resource.tag contains the customized resource tag.

// $done({error : "error description"});
// $done({content : "the modified content"});

var sampleA = "shadowsocks=ui-a.example.com:80, method=chacha20, password=pwd, obfs=http, obfs-host=bing.com, obfs-uri=/resource/file, fast-open=false, udp-relay=false, tag=Tag-A";
var sampleB = "shadowsocks=ui-b.example.com:80, method=chacha20, password=pwd, obfs=http, obfs-host=bing.com, obfs-uri=/resource/file, fast-open=false, udp-relay=false, tag=Tag-B";
var total = sampleA + "\n" + sampleB;
$done({content : total});


// ----------------------------------------------------------------
// User-Agent retry support (Quantumult X v1.5.6-build921)
//
// $resource.user_agent contains the User-Agent used for the current download.
// It is empty on the first attempt (default UA), and equals the retry UA you returned previously when in a retry.
//
// $done({retry: {user_agent: "..."}}) asks native to re-download with the specified UA and parse again.
//
// At most 1 retry per resource: a non-empty $resource.user_agent means you are already in a retry; returning retry again has no effect.
// Older Quantumult X versions ignore the retry field, so it is recommended to return content / error alongside as a fallback.
//
// Priority on new version: retry > content / error. Old versions do not recognize retry and naturally fall back to content / error.
//
// Logic:
//
//   const currentUA = $resource.user_agent;
//   const inRetry = currentUA && currentUA.length > 0;
//
//   const result = {
//       // Normal parse result (kept for old-version compat;
//       // new versions ignore this when retry fires)
//       content: parsed,
//       // or error: "..."
//   };
//
//   const wantRetry = /* your detection logic, e.g. anti-bot signature or user set in the URL hash*/;
//   if (wantRetry && !inRetry) {
//       result.retry = { user_agent: "AnyUserAgent/1.0" };
//   }
//
//   $done(result);
