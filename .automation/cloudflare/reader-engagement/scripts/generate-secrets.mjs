import {webcrypto, randomBytes} from 'node:crypto';
import {mkdir,open} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
const args = process.argv.slice(2);
const option = (name,fallback) => args.includes(name) ? args[args.indexOf(name)+1] : fallback;
const target = resolve(option('--out','.secrets/reader-engagement.env'));
const subject = option('--subject','');
let validSubject=/^mailto:[^\s@]+@[^\s@]+$/.test(subject);
try {
  const url=new URL(subject);
  validSubject ||= url.protocol==='https:' && !!url.hostname && !url.username && !url.password && !/\s/.test(subject);
} catch {}
if (!validSubject) throw new Error('Pass --subject mailto:YOUR_CONTACT_EMAIL or --subject https://YOUR_SITE/');
const pair = await webcrypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);
const [privateKey,publicKey] = await Promise.all([
  webcrypto.subtle.exportKey('jwk',pair.privateKey),webcrypto.subtle.exportKey('raw',pair.publicKey),
]);
const values = {
  VAPID_PUBLIC_KEY:Buffer.from(publicKey).toString('base64url'),
  VAPID_PRIVATE_KEY:privateKey.d,
  VAPID_SUBJECT:subject,
  READER_PUBLISH_TOKEN:randomBytes(32).toString('base64url'),
  RATE_LIMIT_SALT:randomBytes(32).toString('base64url'),
};
await mkdir(dirname(target),{recursive:true,mode:0o700});
const file = await open(target,'wx',0o600);
try { await file.writeFile(Object.entries(values).map(([key,value]) => `${key}=${value}`).join('\n')+'\n'); }
finally { await file.close(); }
console.log(`Secrets written to ${target}. Values were not printed. Keep this ignored file private.`);
