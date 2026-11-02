import * as THREE from './node_modules/three/build/three.module.js';

// New scene from one fixed geometric solid, not an edit of any generated bitmap.
// R/S are visual type names, not a chemical CIP absolute-configuration assignment.
const P={radius:.32,width:.22,height:.94,thickness:.026,segments:256,turns:1,phase:Math.PI/2};
const a=P.height/(2*Math.PI),positions=[],indices=[],centerline=[];
for(let i=0;i<=P.segments;i++){
 const t=-Math.PI+2*Math.PI*i/P.segments,phi=t+P.phase;
 centerline.push([P.radius*Math.cos(phi),a*(t+Math.PI),P.radius*Math.sin(phi)]);
 for(const [u,v] of [[-P.width/2,-P.thickness/2],[P.width/2,-P.thickness/2],[P.width/2,P.thickness/2],[-P.width/2,P.thickness/2]]){
  const r=P.radius+u,L=Math.hypot(r,a);
  // Constant physical thickness along the ruled ribbon's surface normal.
  positions.push(r*Math.cos(phi)+v*a*Math.sin(phi)/L,a*(t+Math.PI)+v*r/L,r*Math.sin(phi)-v*a*Math.cos(phi)/L);
 }
}
for(let i=0;i<P.segments;i++)for(let j=0;j<4;j++){
 const b=4*i+j,c=4*i+(j+1)%4,d=c+4,e=b+4;indices.push(b,c,e,c,d,e);
}
indices.push(0,2,1,0,3,2);const end=4*P.segments;indices.push(end,end+1,end+2,end,end+2,end+3);
const gR=new THREE.BufferGeometry();gR.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));gR.setIndex(indices);gR.computeVertexNormals();gR.computeBoundingBox();
const gS=gR.clone(),sp=gS.attributes.position;
for(let i=0;i<sp.count;i++)sp.setX(i,-sp.getX(i));
const si=gS.index.array;for(let i=0;i<si.length;i+=3)[si[i+1],si[i+2]]=[si[i+2],si[i+1]];
sp.needsUpdate=true;gS.computeVertexNormals();gS.computeBoundingBox();
let reflectionError=0,edgeError=0;
for(let i=0;i<sp.count;i++){reflectionError=Math.max(reflectionError,Math.abs(sp.getX(i)+gR.attributes.position.getX(i)),Math.abs(sp.getY(i)-gR.attributes.position.getY(i)),Math.abs(sp.getZ(i)-gR.attributes.position.getZ(i)));}
function area(g){let sum=0;const p=g.attributes.position,ix=g.index.array,v=[new THREE.Vector3(),new THREE.Vector3(),new THREE.Vector3()];for(let i=0;i<ix.length;i+=3){for(let j=0;j<3;j++)v[j].fromBufferAttribute(p,ix[i+j]);sum+=v[1].clone().sub(v[0]).cross(v[2].clone().sub(v[0])).length()/2;}return sum;}
const areaR=area(gR),areaS=area(gS),length=Math.hypot(2*Math.PI*P.radius,P.height);
const scene=new THREE.Scene();scene.background=new THREE.Color('#f4efe5');
const pairView=new URLSearchParams(location.search).has('pair'),W=pairView?1200:1664,H=pairView?900:936;
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H);renderer.setPixelRatio(1);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;document.body.appendChild(renderer.domElement);
const camera=new THREE.OrthographicCamera(-1,1,1,-1,.1,100);
const span=pairView?3.3:9.0,aspect=W/H;camera.left=-span*aspect/2;camera.right=span*aspect/2;camera.top=span/2;camera.bottom=-span/2;
const target=new THREE.Vector3(pairView?0:.6,pairView?.49:.28,0);camera.position.copy(target).add(new THREE.Vector3(0,pairView?2.0:8.0,pairView?12:17));camera.lookAt(target);camera.updateProjectionMatrix();
scene.add(new THREE.HemisphereLight(0xfff7e9,0x9c9184,2.3));const light=new THREE.DirectionalLight(0xfff1dc,3.0);light.position.set(-4,9,7);light.castShadow=true;light.shadow.mapSize.set(4096,4096);Object.assign(light.shadow.camera,{left:-13,right:13,top:10,bottom:-10,near:.1,far:40});light.shadow.bias=-.0002;light.shadow.normalBias=.012;light.shadow.radius=3;scene.add(light);
const fill=new THREE.DirectionalLight(0xf1f4ff,.7);fill.position.set(7,5,-3);scene.add(fill);
const matR=new THREE.MeshStandardMaterial({color:'#aa602d',roughness:.66,metalness:.38});
const matS=new THREE.MeshStandardMaterial({color:'#454b4e',roughness:.77,metalness:.18});
const paper=new THREE.Mesh(new THREE.PlaneGeometry(80,60),new THREE.MeshStandardMaterial({color:'#f5f0e6',roughness:1}));paper.rotation.x=-Math.PI/2;paper.receiveShadow=true;scene.add(paper);
const instances=[];const lift=-gR.boundingBox.min.y+.018;
function add(type,x,z,group,yaw=0){const m=new THREE.Mesh(type==='R'?gR:gS,type==='R'?matR:matS);m.position.set(x,lift,z);m.rotation.y=yaw;m.castShadow=true;m.receiveShadow=true;scene.add(m);instances.push({type,group,mesh:m,x,z,yaw});return m;}
if(pairView){add('R',-.69,0,'pair-reference');add('S',.69,0,'pair-reference');}
else{
 // A shallow, single paper cutout footprint. This support never changes module geometry.
 const shape=new THREE.Shape();const cx=-1.5,rx=4.9,rz=3.25;
 for(let i=0;i<=160;i++){const t=i*2*Math.PI/160,rr=1+.016*Math.sin(9*t)+.01*Math.sin(17*t);const x=cx+rx*rr*Math.cos(t),y=rz*rr*Math.sin(t);if(i===0)shape.moveTo(x,y);else shape.lineTo(x,y);}
 const inset=new THREE.Mesh(new THREE.ShapeGeometry(shape),new THREE.MeshStandardMaterial({color:'#c8bead',roughness:1}));inset.rotation.x=-Math.PI/2;inset.position.y=.005;inset.receiveShadow=true;scene.add(inset);
 let id=0;for(const [row,n] of [3,5,5,3].entries())for(let c=0;c<n;c++){
  const x=(c-(n-1)/2)*1.82-1.5,z=(row-1.5)*1.57,g='core-pair-'+(++id);
  add('R',x-.46,z,g);add('S',x+.46,z,g);
 }
 for(const [i,[x,z]]of [[4.15,-3.0],[6.0,-2.2],[4.8,-.75],[6.7,.10],[4.0,1.1],[5.7,2.25],[7.0,3.2],[4.1,3.35]].entries())add(i===7?'S':'R',x,z,'fringe-'+(i+1));
}
scene.updateMatrixWorld(true);
let matrixError=0,maxInverseError=0;const sample=new THREE.Vector3();
for(const o of instances){const e=o.mesh.matrixWorld.elements,R=new THREE.Matrix3().setFromMatrix4(o.mesh.matrixWorld),cols=[new THREE.Vector3(e[0],e[1],e[2]),new THREE.Vector3(e[4],e[5],e[6]),new THREE.Vector3(e[8],e[9],e[10])];matrixError=Math.max(matrixError,...cols.map(c=>Math.abs(c.length()-1)),Math.abs(R.determinant()-1));const inv=o.mesh.matrixWorld.clone().invert(),g=o.mesh.geometry.attributes.position;for(let i=0;i<g.count;i+=71){sample.fromBufferAttribute(g,i);const p=sample.clone().applyMatrix4(o.mesh.matrixWorld).applyMatrix4(inv);maxInverseError=Math.max(maxInverseError,p.distanceTo(sample));}}
const counts={coreR:instances.filter(o=>o.group.startsWith('core')&&o.type==='R').length,coreS:instances.filter(o=>o.group.startsWith('core')&&o.type==='S').length,fringeR:instances.filter(o=>o.group.startsWith('fringe')&&o.type==='R').length,fringeS:instances.filter(o=>o.group.startsWith('fringe')&&o.type==='S').length};
if(reflectionError!==0||Math.abs(areaR-areaS)>1e-10||matrixError>1e-12||maxInverseError>1e-12)throw Error('Geometry verification failed');
if(!pairView&&(counts.coreR!==16||counts.coreS!==16||counts.fringeR!==7||counts.fringeS!==1))throw Error('Counts failed');
window.__audit={threeRevision:THREE.REVISION,mode:pairView?'pair':'scene',parameters:P,sourceEquation:'p(t,u,v)=ruled one-turn helix + v times unit surface normal; t in [-pi,pi]',reflection:'M=diag(-1,1,1), determinant=-1, exact vertex x reflection, winding reversed',visualTypeWarning:'R/S are geometric visual-type labels, not a CIP chemical assignment',centerline:{turnAngle:2*Math.PI,turns:1,endpointDelta:centerline.at(-1).map((v,i)=>v-centerline[0][i]),radius:P.radius,analyticLength:length,torsionR:-a/(P.radius**2+a*a),torsionS:a/(P.radius**2+a*a)},mesh:{vertices:sp.count,triangles:gR.index.count/3,reflectionMaxError:reflectionError,areaR,areaS,bboxR:gR.boundingBox,bboxS:gS.boundingBox},placements:{scale:[1,1,1],maxRigidError:matrixError,maxInverseVertexError:maxInverseError,counts,instances:instances.map(({mesh,...o})=>({...o,position:mesh.position.toArray(),quaternion:mesh.quaternion.toArray(),scale:mesh.scale.toArray()}))},camera:{kind:'orthographic',position:camera.position.toArray(),target:target.toArray(),frustum:{left:camera.left,right:camera.right,top:camera.top,bottom:camera.bottom}},dimensions:[W,H]};
renderer.render(scene,camera);window.__ready=true;
