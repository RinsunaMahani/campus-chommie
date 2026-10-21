/**
 * CI's npm audit gate: fails on any high or critical advisory in what the
 * app depends on, except the ones accepted in audit-allowlist.json (each
 * with a reason and a review date). An entry past its review date fails
 * too, so an accepted risk is looked at again rather than forgotten.
 *
 *   npm audit --omit=dev --json > audit.json; node scripts/check-audit.mjs audit.json
 */
import { readFileSync } from 'node:fs';

const report = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const allowlist = JSON.parse(readFileSync(new URL('../audit-allowlist.json', import.meta.url), 'utf8')).advisories;
const today = new Date().toISOString().slice(0, 10);

// Root advisories only: an entry's "via" holds objects for its own advisories
// and package names for the ones it inherits.
const found = new Map();
for (const [name, vuln] of Object.entries(report.vulnerabilities ?? {})) {
  for (const via of vuln.via) {
    if (typeof via === 'object' && ['high', 'critical'].includes(via.severity)) {
      const id = via.url.split('/').pop();
      found.set(id, `${via.severity} ${name}: ${via.title} (${via.url})`);
    }
  }
}

const accepted = new Map(allowlist.map((a) => [a.id, a]));
const problems = [];
for (const [id, line] of found) {
  if (!accepted.has(id)) problems.push(`not accepted: ${line}`);
}
for (const a of allowlist) {
  if (a.review_by < today) problems.push(`review date passed (${a.review_by}): ${a.id} ${a.package}. Check for a fix, then update or remove the entry.`);
}

for (const [id, line] of found) if (accepted.has(id)) console.log(`accepted until ${accepted.get(id).review_by}: ${line}`);
if (problems.length) {
  console.error(problems.join('\n'));
  process.exit(1);
}
console.log(`OK: no high or critical advisories beyond the ${found.size} accepted.`);
