// Parse only. Never execute downloaded third-party code.
const fs = require('node:fs');
const vm = require('node:vm');
const path = process.argv[2];
try {
  new vm.Script(fs.readFileSync(path, 'utf8'), {filename: path});
  process.stdout.write(JSON.stringify({ok: true, engine: process.version}));
} catch (e) {
  process.stdout.write(JSON.stringify({ok: false, error: String(e)}));
  process.exitCode = 1;
}
