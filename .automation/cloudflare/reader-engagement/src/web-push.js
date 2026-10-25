// RFC 8291 aes128gcm content encryption and RFC 8292 VAPID authentication.
// Private keys stay in Worker secrets. No Node compatibility layer is required.
import {ApiError, base64url, decode64} from './security.js';
const encode = value => new TextEncoder().encode(value);
const concat = (...values) => {
  const result = new Uint8Array(values.reduce((n,v) => n + v.byteLength, 0));
  let offset = 0;
  for (const value of values) { result.set(new Uint8Array(value), offset); offset += value.byteLength; }
  return result;
};

async function hmac(key, data) {
  const imported = await crypto.subtle.importKey('raw', key, {name:'HMAC',hash:'SHA-256'}, false, ['sign']);
  return new Uint8Array(await crypto.subtle.sign('HMAC', imported, data));
}
async function expand(key, info, length) {
  return (await hmac(key, concat(info, new Uint8Array([1])))).slice(0,length);
}

export async function encryptedPayload(subscription, payload) {
  const data = encode(JSON.stringify(payload));
  if (data.length > 3000) throw new ApiError('push_payload_too_large', 500);
  const userPublic = decode64(subscription.keys.p256dh, 65);
  const auth = decode64(subscription.keys.auth, 16);
  const ephemeral = await crypto.subtle.generateKey({name:'ECDH',namedCurve:'P-256'}, true, ['deriveBits']);
  const serverPublic = new Uint8Array(await crypto.subtle.exportKey('raw', ephemeral.publicKey));
  const userKey = await crypto.subtle.importKey('raw', userPublic, {name:'ECDH',namedCurve:'P-256'}, false, []);
  const shared = new Uint8Array(await crypto.subtle.deriveBits({name:'ECDH',public:userKey},ephemeral.privateKey,256));
  const keyInfo = concat(encode('WebPush: info\0'), userPublic, serverPublic);
  const ikm = await expand(await hmac(auth,shared),keyInfo,32);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const prk = await hmac(salt,ikm);
  const [key,nonce] = await Promise.all([
    expand(prk,encode('Content-Encoding: aes128gcm\0'),16),
    expand(prk,encode('Content-Encoding: nonce\0'),12),
  ]);
  const aes = await crypto.subtle.importKey('raw',key,'AES-GCM',false,['encrypt']);
  const encrypted = await crypto.subtle.encrypt({name:'AES-GCM',iv:nonce,tagLength:128},aes,concat(data,new Uint8Array([2])));
  const size = new Uint8Array(4);
  new DataView(size.buffer).setUint32(0,4096,false);
  return concat(salt,size,new Uint8Array([serverPublic.length]),serverPublic,encrypted);
}

export async function vapidAuthorization(endpoint, env) {
  const publicKey = decode64(env.VAPID_PUBLIC_KEY,65);
  const privateKey = decode64(env.VAPID_PRIVATE_KEY,32);
  if (publicKey[0] !== 4 || !/^(?:mailto:[^\s@]+@[^\s@]+|https:\/\/[^\s]+)$/.test(env.VAPID_SUBJECT || '')) throw new ApiError('invalid_vapid_config',503);
  const key = await crypto.subtle.importKey('jwk',{
    kty:'EC',crv:'P-256',x:base64url(publicKey.slice(1,33)),y:base64url(publicKey.slice(33,65)),d:base64url(privateKey),ext:true,
  },{name:'ECDSA',namedCurve:'P-256'},false,['sign']);
  const header = base64url(encode(JSON.stringify({typ:'JWT',alg:'ES256'})));
  const claims = base64url(encode(JSON.stringify({aud:new URL(endpoint).origin,exp:Math.floor(Date.now()/1000)+43200,sub:env.VAPID_SUBJECT})));
  const unsigned = `${header}.${claims}`;
  const signature = await crypto.subtle.sign({name:'ECDSA',hash:'SHA-256'},key,encode(unsigned));
  return `vapid t=${unsigned}.${base64url(signature)}, k=${env.VAPID_PUBLIC_KEY}`;
}

export async function webPushRequest(subscription, payload, env) {
  const [body, authorization] = await Promise.all([encryptedPayload(subscription,payload),vapidAuthorization(subscription.endpoint,env)]);
  return new Request(subscription.endpoint,{
    method:'POST',redirect:'manual',body,
    headers:{'Authorization':authorization,'Content-Encoding':'aes128gcm','Content-Type':'application/octet-stream','TTL':'86400','Urgency':'normal',
      'Topic':String(payload.tag || '').replace(/[^A-Za-z0-9_-]/g,'').slice(0,32)},
  });
}
