async(driver)=>{
 const context=await driver.context().browser().newContext(),page=await context.newPage();
 const origin='http://localhost:8767/AI_Tech_Review/lectures/reader/';
 try{
  await context.route('**/storage-qa.html',route=>route.fulfill({contentType:'text/html',body:'<!doctype html><title>Storage migration QA</title>'}));
  await page.goto(origin+'storage-qa.html');
  return await page.evaluate(async()=>{
   const assert=(value,message)=>{if(!value)throw Error(message)};
   const a='a'.repeat(64),b='b'.repeat(64),c='c'.repeat(64);
   const original=new Uint8Array(2*1024*1024);original.fill(7);original.set([37,80,68,70,45,49]);
   const hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');
   const expected=await hash(original);
   await new Promise((resolve,reject)=>{
    const r=indexedDB.open('atr-lecture-notebooks',1);
    r.onupgradeneeded=()=>{r.result.createObjectStore('documents',{keyPath:'fingerprint'});r.result.createObjectStore('pages',{keyPath:'key'});};
    r.onerror=()=>reject(r.error);r.onsuccess=()=>{
     const db=r.result,tx=db.transaction(['documents','pages'],'readwrite');
     for(const fingerprint of [a,b])tx.objectStore('documents').put({fingerprint,title:'Legacy original',pdf:original.buffer.slice(0),pageCount:3,position:2,bookmarks:[2],annotatedPages:[1],updatedAt:1});
     tx.objectStore('pages').put({key:a+':00001',fingerprint:a,number:1,strokes:[{id:'legacy-ink',color:'#243746',width:.002,points:[{x:.1,y:.2,p:.5}]}]});
     tx.oncomplete=()=>{db.close();resolve()};tx.onerror=tx.onabort=()=>reject(tx.error);
    };
   });
   const storage=await import('./storage.mjs?storage-v2-browser-qa');
   const migrated=await storage.getDocument(a);assert(migrated.position===2&&migrated.bookmarks[0]===2,'legacy metadata changed');assert(await hash(await migrated.pdf.arrayBuffer())===expected,'legacy PDF changed');assert((await storage.loadPage(a,1))[0].id==='legacy-ink','legacy ink lost');
   const accesses=[],methods=['get','getAll','put','add'],old=new Map();
   for(const method of methods){old.set(method,IDBObjectStore.prototype[method]);IDBObjectStore.prototype[method]=function(...args){accesses.push({store:this.name,method});return old.get(method).apply(this,args)}}
   let list=await storage.listDocuments();assert(list.length===2&&list.every(d=>d.hasPDF&&!('pdf'in d)),'list loaded PDF bytes');assert(accesses.every(x=>x.store==='document_metadata'),'list touched binary store');
   accesses.length=0;await storage.saveMetadata(a,{position:3,bookmarks:[3]});await storage.savePage(a,2,[{id:'new-ink',color:'#243746',width:.002,points:[{x:.2,y:.3,p:.7}]}]);assert(accesses.every(x=>!['documents','pdf_originals'].includes(x.store)),'a normal save touched PDF bytes');
   accesses.length=0;const fresh={fingerprint:c,title:'New original',pdf:new Blob([original]),pageCount:3,position:1,bookmarks:[],annotatedPages:[],updatedAt:Date.now()};
   await Promise.all([storage.putDocument(fresh),storage.putDocument(fresh)]);assert(accesses.filter(x=>x.store==='pdf_originals'&&x.method==='add').length===1,'concurrent opens duplicated original writes');
   accesses.length=0;await storage.putDocument({...fresh,pdf:new Blob(['replacement bytes']),position:2});assert(!accesses.some(x=>x.store==='pdf_originals'&&['put','add'].includes(x.method)),'an existing original was rewritten');assert(await hash(await(await storage.getDocument(c)).pdf.arrayBuffer())===expected,'immutable original replaced');
   await storage.trashDocument(a);assert(!(await storage.listDocuments()).some(d=>d.fingerprint===a),'trash remained in active list');assert((await storage.listDocuments({includeTrash:true})).some(d=>d.fingerprint===a&&d.deletedAt),'trash not recoverable');assert((await storage.loadPage(a,1))[0].id==='legacy-ink','trash removed ink');await storage.restoreDocument(a);assert((await storage.listDocuments()).some(d=>d.fingerprint===a&&!d.deletedAt),'restore failed');
   await storage.importPages(a,[{number:3,strokes:[{id:'restored-ink',color:'#243746',width:.002,points:[{x:.3,y:.4,p:.5}]}]}],[3],3);const final=await storage.getDocument(a);assert(final.position===3&&final.bookmarks[0]===3,'new metadata lost');assert(await hash(await final.pdf.arrayBuffer())===expected,'editing or restoring changed original');
   for(const [method,implementation]of old)IDBObjectStore.prototype[method]=implementation;
   return{version:(await storage.openDatabase()).version,legacyPDFAndInkPreserved:true,metadataOnlyListing:true,noPDFIOOnNormalSaves:true,concurrentOriginalWrittenOnce:true,sourceImmutable:true,localTrashRestore:true,originalBytes:original.length,sha256:expected};
  });
 }finally{await context.close()}
}
