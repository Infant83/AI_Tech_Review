const sha = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);

export function editionsFor(doc) {
  if (!doc || !/^[a-z0-9-]+$/.test(doc.id) || !sha(doc.sha256) || doc.href !== `archive/files/${doc.id}.pdf`) return [];
  const seen = new Set([doc.sha256]);
  const result = [{ sha256: doc.sha256, href: doc.href, current: true }];
  for (const row of Array.isArray(doc.editions) ? doc.editions : []) {
    if (!row || !sha(row.sha256) || seen.has(row.sha256) || row.href !== `archive/editions/${doc.id}/${row.sha256}.pdf`) continue;
    seen.add(row.sha256); result.push({ sha256: row.sha256, href: row.href, current: false });
  }
  return result;
}

export function selectEdition(doc, fingerprint = null) {
  return editionsFor(doc).find(row => !fingerprint || row.sha256 === fingerprint) || null;
}
