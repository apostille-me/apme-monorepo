import { readFileSync } from 'node:fs';
const catalog = JSON.parse(readFileSync(new URL('../catalog.json', import.meta.url), 'utf8'));
console.log(`${catalog.title} (${catalog.org})`);
console.log(`apps=${catalog.apps.join(',')}`);
console.log(`packages=${catalog.packages.join(',')}`);
