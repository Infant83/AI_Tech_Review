import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {normalizeFeed} from '../src/worker.js';
import {sha256} from '../src/security.js';

const args=process.argv.slice(2);
if(args.length!==1) throw new Error('Usage: node scripts/seed-local.mjs /path/to/reader-publications.json');
const feed=normalizeFeed(JSON.parse(await readFile(resolve(args[0]),'utf8')));
const quote=value=>`'${String(value).replaceAll("'","''")}'`;
const now=Date.now();
const sql=[
  `UPDATE articles SET active=0,updated_at=${now};`,
  ...feed.articles.map(item=>`INSERT INTO articles(id,path,title,published_at,topic,active,created_at,updated_at) VALUES(${[item.id,item.path,item.title,item.publishedAt,item.topic].map(quote).join(',')},1,${now},${now}) ON CONFLICT(id) DO UPDATE SET path=excluded.path,title=excluded.title,published_at=excluded.published_at,topic=excluded.topic,active=1,updated_at=excluded.updated_at;`),
  `INSERT INTO publication_state(id,revision,initialized_at,updated_at) VALUES(1,${quote(feed.revision)},${now},${now}) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,updated_at=excluded.updated_at;`,
  `INSERT OR IGNORE INTO sync_revisions(revision,feed_hash,applied_at) VALUES(${quote(feed.revision)},${quote(await sha256(JSON.stringify(feed)))},${now});`,
];
// This helper only writes SQL. It never connects to any database or service.
const output=resolve('.wrangler/reader-local-seed.sql');
await mkdir(dirname(output),{recursive:true});
await writeFile(output,sql.join('\n')+'\n');
console.log(`Local-only seed written: ${output} (${feed.articles.length} articles; no notification events)`);
console.log('Apply with: npx wrangler d1 execute DB --local --file=.wrangler/reader-local-seed.sql');
