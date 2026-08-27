/* ── GLOBE ── */
(function(){
var canvas=document.getElementById('globe-canvas');
var heroEl=document.getElementById('hero');
if(!canvas||!heroEl||typeof THREE==='undefined')return;
var W=canvas.offsetWidth,H=canvas.offsetHeight;
var renderer=new THREE.WebGLRenderer({canvas:canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setSize(W,H);
renderer.setClearColor(0x07011a,1);

var scene=new THREE.Scene();
var camera=new THREE.PerspectiveCamera(40,W/H,0.1,500);
camera.position.set(0,0,4.5);

/* STARS — 분포 개선, 구면균일 분포 */
var N_STARS=5500;
var sP=new Float32Array(N_STARS*3);
for(var i=0;i<N_STARS;i++){
  var th=Math.acos(2*Math.random()-1);
  var ph=Math.random()*Math.PI*2;
  var r=90+Math.random()*30;
  sP[i*3]=r*Math.sin(th)*Math.cos(ph);
  sP[i*3+1]=r*Math.cos(th);
  sP[i*3+2]=r*Math.sin(th)*Math.sin(ph);
}
var sG=new THREE.BufferGeometry();sG.setAttribute('position',new THREE.BufferAttribute(sP,3));
/* 작은 별들 */
scene.add(new THREE.Points(sG,new THREE.PointsMaterial({color:0xff2a6d,size:0.048,transparent:true,opacity:0.70})));
/* 밝은 별 소수 */
var sP2=new Float32Array(120*3);
for(var i=0;i<120;i++){
  var th=Math.acos(2*Math.random()-1);var ph=Math.random()*Math.PI*2;var r=92+Math.random()*20;
  sP2[i*3]=r*Math.sin(th)*Math.cos(ph);sP2[i*3+1]=r*Math.cos(th);sP2[i*3+2]=r*Math.sin(th)*Math.sin(ph);
}
var sG2=new THREE.BufferGeometry();sG2.setAttribute('position',new THREE.BufferAttribute(sP2,3));
scene.add(new THREE.Points(sG2,new THREE.PointsMaterial({color:0x05d9e8,size:0.10,transparent:true,opacity:0.90})));

/* ── EARTH TEXTURE: real photo first, canvas fallback ── */
function buildCanvasEarth(){
  var TW=2048,TH=1024;
  var tc=document.createElement('canvas');tc.width=TW;tc.height=TH;
  var ctx=tc.getContext('2d');

  function xy(lon,lat){return[(lon+180)/360*TW,(90-lat)/180*TH];}
  function land(pts,col){
    ctx.beginPath();
    var q=xy(pts[0][0],pts[0][1]);ctx.moveTo(q[0],q[1]);
    for(var i=1;i<pts.length;i++){q=xy(pts[i][0],pts[i][1]);ctx.lineTo(q[0],q[1]);}
    ctx.closePath();ctx.fillStyle=col;ctx.fill();
  }

  /* OCEAN */
  var og=ctx.createLinearGradient(0,0,0,TH);
  og.addColorStop(0,'#082040');og.addColorStop(0.18,'#0D4A7A');
  og.addColorStop(0.5,'#186090');og.addColorStop(0.82,'#0D4A7A');og.addColorStop(1,'#082040');
  ctx.fillStyle=og;ctx.fillRect(0,0,TW,TH);

  /* subtle equatorial brightness */
  var eq=ctx.createRadialGradient(TW/2,TH/2,TH*0.05,TW/2,TH/2,TH*0.55);
  eq.addColorStop(0,'rgba(30,110,160,0.3)');eq.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=eq;ctx.fillRect(0,0,TW,TH);

  var G='#3E7C42',D='#BFA055',T='#2E7A3A',S='#9EC8A0';

  /* North America */
  land([[-168,72],[-140,62],[-130,55],[-125,48],[-120,37],[-117,32],[-97,22],[-87,15],[-83,8],[-77,8],[-80,0],[-92,15],[-97,22],[-104,20],[-110,22],[-117,32],[-125,48],[-130,55],[-140,62],[-168,62],[-168,72]],G);
  /* Alaska */
  land([[-168,72],[-165,60],[-158,56],[-148,60],[-135,59],[-140,62],[-168,72]],G);
  /* Mexico/Central */
  land([[-92,15],[-87,15],[-83,8],[-83,10],[-78,8],[-77,8],[-80,0],[-83,8],[-87,15],[-92,15]],G);
  /* Greenland */
  land([[-68,76],[-50,60],[-20,62],[-18,72],[-22,83],[-45,84],[-65,83],[-68,76]],S);
  /* Iceland */
  land([[-24,64],[-14,64],[-14,66],[-22,66],[-24,64]],S);

  /* South America */
  land([[-80,12],[-62,10],[-50,0],[-35,-5],[-35,-15],[-40,-23],[-52,-34],[-65,-56],[-74,-50],[-68,-38],[-65,-30],[-70,-18],[-78,-5],[-80,0],[-80,12]],G);
  /* Amazon darker */
  land([[-75,5],[-50,5],[-50,-10],[-68,-10],[-75,0],[-75,5]],T);

  /* Europe */
  land([[-10,36],[28,35],[38,37],[42,42],[38,47],[28,48],[20,54],[15,58],[28,65],[20,70],[10,70],[5,62],[0,58],[-3,51],[-5,44],[-10,36]],G);
  /* Scandinavia */
  land([[5,58],[15,58],[20,60],[28,65],[28,70],[20,70],[10,70],[5,62],[5,58]],G);
  /* British Isles */
  land([[-5,50],[-2,51],[-2,58],[-5,58],[-5,50]],G);
  land([[-10,51],[-5,51],[-5,55],[-10,55],[-10,51]],G);

  /* Africa */
  land([[-17,15],[32,15],[42,12],[52,10],[44,-1],[42,-12],[35,-18],[32,-26],[25,-35],[15,-35],[10,-30],[-16,-27],[-18,-17],[-16,0],[-10,5],[2,5],[10,4],[-17,15]],G);
  /* Sahara */
  land([[-17,15],[32,15],[42,12],[38,22],[25,23],[10,23],[2,15],[-10,15],[-17,15]],D);
  /* Arabian */
  land([[38,30],[56,22],[58,12],[50,10],[42,12],[38,22],[38,30]],D);

  /* Eurasia main */
  land([[28,35],[42,37],[50,40],[60,44],[80,44],[100,40],[105,35],[115,38],[120,32],[122,22],[110,20],[102,2],[100,2],[104,0],[108,-5],[115,-4],[120,0],[120,10],[128,20],[130,35],[140,40],[145,45],[145,55],[140,60],[130,65],[100,72],[70,74],[40,73],[20,70],[28,65],[20,60],[15,58],[20,54],[28,48],[38,47],[42,42],[38,37],[28,35]],G);
  /* Central Asia */
  land([[55,40],[80,44],[80,52],[55,52],[55,40]],D);
  /* Gobi */
  land([[95,40],[120,40],[120,45],[95,48],[95,40]],D);
  /* India */
  land([[66,24],[80,28],[90,28],[92,22],[80,8],[74,8],[68,22],[66,24]],G);
  /* SE Asia */
  land([[100,22],[110,20],[120,16],[122,8],[108,2],[100,4],[98,18],[100,22]],G);
  /* Japan */
  land([[130,31],[132,31],[132,34],[130,34],[130,31]],G);
  land([[140,35],[142,35],[142,45],[140,45],[140,35]],G);
  land([[141,33],[144,33],[144,35],[141,35],[141,33]],G);
  /* Korean Peninsula */
  land([[126,34],[130,34],[130,38],[128,38],[126,37],[126,34]],G);

  /* Australia */
  land([[115,-25],[120,-35],[124,-34],[128,-32],[132,-25],[136,-18],[138,-16],[145,-15],[148,-22],[150,-36],[145,-39],[138,-38],[130,-36],[122,-34],[115,-30],[115,-25]],D);
  land([[142,-15],[150,-22],[152,-26],[148,-38],[145,-39],[142,-28],[142,-15]],G);
  /* New Zealand */
  land([[172,-40],[175,-44],[172,-46],[170,-44],[172,-40]],G);
  land([[174,-36],[177,-38],[175,-42],[173,-40],[174,-36]],G);
  /* Madagascar */
  land([[44,-13],[50,-16],[50,-25],[44,-25],[44,-13]],G);

  /* POLAR ICE CAPS */
  var arcG=ctx.createLinearGradient(0,0,0,TH*0.14);
  arcG.addColorStop(0,'rgba(220,238,250,0.98)');arcG.addColorStop(0.6,'rgba(210,230,245,0.6)');arcG.addColorStop(1,'rgba(210,230,245,0)');
  ctx.fillStyle=arcG;ctx.fillRect(0,0,TW,TH*0.14);

  var antG=ctx.createLinearGradient(0,TH*0.87,0,TH);
  antG.addColorStop(0,'rgba(210,230,248,0)');antG.addColorStop(0.4,'rgba(218,235,250,0.65)');antG.addColorStop(1,'rgba(225,240,255,0.98)');
  ctx.fillStyle=antG;ctx.fillRect(0,TH*0.87,TW,TH*0.13);

  /* CLOUDS - elliptical wisps */
  var seed=42;function rng(){seed=(seed*1664525+1013904223)&0x7fffffff;return seed/0x7fffffff;}
  for(var ci=0;ci<280;ci++){
    var cx2=rng()*TW,cy2=rng()*TH;
    var rx=25+rng()*160,ry=5+rng()*28;
    var angle=rng()*Math.PI;
    var op=0.12+rng()*0.40;
    ctx.save();ctx.translate(cx2,cy2);ctx.rotate(angle);
    var cg=ctx.createRadialGradient(0,0,0,0,0,Math.max(rx,ry));
    cg.addColorStop(0,'rgba(255,255,255,'+op+')');
    cg.addColorStop(0.5,'rgba(255,255,255,'+(op*0.5)+')');
    cg.addColorStop(1,'rgba(255,255,255,0)');
    ctx.scale(rx/Math.max(rx,ry),ry/Math.max(rx,ry));
    ctx.beginPath();ctx.arc(0,0,Math.max(rx,ry),0,Math.PI*2);
    ctx.fillStyle=cg;ctx.fill();ctx.restore();
  }
  /* Extra cloud band along ITCZ ~5-10N */
  for(var ci=0;ci<80;ci++){
    var cx2=rng()*TW,cy2=((90-8)/180*TH)+(rng()-0.5)*TH*0.06;
    var rx=30+rng()*200,ry=4+rng()*16;
    var op=0.18+rng()*0.35;
    ctx.save();ctx.translate(cx2,cy2);
    var cg=ctx.createRadialGradient(0,0,0,0,0,Math.max(rx,ry));
    cg.addColorStop(0,'rgba(255,255,255,'+op+')');cg.addColorStop(1,'rgba(255,255,255,0)');
    ctx.scale(rx/Math.max(rx,ry),ry/Math.max(rx,ry));
    ctx.beginPath();ctx.arc(0,0,Math.max(rx,ry),0,Math.PI*2);
    ctx.fillStyle=cg;ctx.fill();ctx.restore();
  }
  return tc;
}

/* Material — MeshPhongMaterial: ocean specular highlight */
var earthMat=new THREE.MeshPhongMaterial({shininess:9,specular:new THREE.Color(0x1a3f66)});
var texLoaded=false;

function tryLoad(urls,idx){
  if(idx>=urls.length){
    if(!texLoaded){earthMat.map=new THREE.CanvasTexture(buildCanvasEarth());earthMat.needsUpdate=true;}
    return;
  }
  var loader=new THREE.TextureLoader();loader.crossOrigin='anonymous';
  loader.load(urls[idx],
    function(tex){if(!texLoaded){texLoaded=true;earthMat.map=tex;earthMat.needsUpdate=true;}},
    undefined,function(){tryLoad(urls,idx+1);});
  if(idx===0){earthMat.map=new THREE.CanvasTexture(buildCanvasEarth());earthMat.needsUpdate=true;}
}
tryLoad(['/img/earth.jpg','https://unpkg.com/three@0.128.0/examples/textures/planets/earth_atmos_2048.jpg','https://cdn.jsdelivr.net/npm/three@0.128.0/examples/textures/planets/earth_atmos_2048.jpg'],0);

var earth=new THREE.Mesh(new THREE.SphereGeometry(1.5,80,80),earthMat);
scene.add(earth);


/* LIGHTS — 강한 태양광 + 낮은 앰비언트 (대비 강화) */
scene.add(new THREE.AmbientLight(0x223344,0.36));
var sun=new THREE.DirectionalLight(0xfff8ee,1.40);sun.position.set(5,2,4);scene.add(sun);
var fill=new THREE.DirectionalLight(0x1133bb,0.14);fill.position.set(-4,-1,-3);scene.add(fill);

earth.rotation.y=-2.0;

/* ── CITIES ── */
var CITIES=[
  {k:'제천시청',e:'Jecheon City Hall, Korea',lat:37.13,lon:128.19,url:'https://www.google.com/maps/place/%EC%A0%9C%EC%B2%9C%EC%8B%9C%EC%B2%AD/@37.1327,128.1918,15z',sp:true},
  {k:'서울',e:'Seoul, South Korea',lat:37.57,lon:126.98,url:'https://www.google.com/maps/search/Seoul+City+Hall'},
  {k:'도쿄',e:'Tokyo, Japan',lat:35.68,lon:139.69,url:'https://www.google.com/maps/search/Tokyo'},
  {k:'베이징',e:'Beijing, China',lat:39.90,lon:116.41,url:'https://www.google.com/maps/search/Beijing'},
  {k:'상하이',e:'Shanghai, China',lat:31.23,lon:121.47,url:'https://www.google.com/maps/search/Shanghai'},
  {k:'싱가포르',e:'Singapore',lat:1.35,lon:103.82,url:'https://www.google.com/maps/search/Singapore'},
  {k:'방콕',e:'Bangkok, Thailand',lat:13.76,lon:100.50,url:'https://www.google.com/maps/search/Bangkok'},
  {k:'뭄바이',e:'Mumbai, India',lat:19.08,lon:72.88,url:'https://www.google.com/maps/search/Mumbai'},
  {k:'두바이',e:'Dubai, UAE',lat:25.20,lon:55.27,url:'https://www.google.com/maps/search/Dubai'},
  {k:'이스탄불',e:'Istanbul, Turkey',lat:41.01,lon:28.98,url:'https://www.google.com/maps/search/Istanbul'},
  {k:'모스크바',e:'Moscow, Russia',lat:55.76,lon:37.62,url:'https://www.google.com/maps/search/Moscow'},
  {k:'카이로',e:'Cairo, Egypt',lat:30.04,lon:31.24,url:'https://www.google.com/maps/search/Cairo'},
  {k:'런던',e:'London, UK',lat:51.51,lon:-0.13,url:'https://www.google.com/maps/search/London'},
  {k:'파리',e:'Paris, France',lat:48.86,lon:2.35,url:'https://www.google.com/maps/search/Paris'},
  {k:'로마',e:'Rome, Italy',lat:41.90,lon:12.50,url:'https://www.google.com/maps/search/Rome'},
  {k:'뉴욕',e:'New York, USA',lat:40.71,lon:-74.01,url:'https://www.google.com/maps/search/New+York'},
  {k:'로스앤젤레스',e:'Los Angeles, USA',lat:34.05,lon:-118.24,url:'https://www.google.com/maps/search/Los+Angeles'},
  {k:'상파울루',e:'Sao Paulo, Brazil',lat:-23.55,lon:-46.63,url:'https://www.google.com/maps/search/Sao+Paulo'},
  {k:'시드니',e:'Sydney, Australia',lat:-33.87,lon:151.21,url:'https://www.google.com/maps/search/Sydney'},
  {k:'요하네스버그',e:'Johannesburg, S. Africa',lat:-26.20,lon:28.04,url:'https://www.google.com/maps/search/Johannesburg'}
];

function ll2v(lat,lon,r){
  var ph=(90-lat)*Math.PI/180,th=(lon+180)*Math.PI/180;
  return new THREE.Vector3(-r*Math.sin(ph)*Math.cos(th),r*Math.cos(ph),r*Math.sin(ph)*Math.sin(th));
}

/* Tiny 3D dots (anchor) */
CITIES.forEach(function(c){
  var dot=new THREE.Mesh(
    new THREE.SphereGeometry(c.sp?0.018:0.012,8,8),
    new THREE.MeshBasicMaterial({color:c.sp?0xe07828:0xaaccff})
  );
  dot.position.copy(ll2v(c.lat,c.lon,1.51));
  earth.add(dot);c._dot=dot;
  c._sx=-999;c._sy=-999;c._vis=false;
});

/* Jecheon pulse ring */
var jc=CITIES[0];
var ringM=new THREE.Mesh(new THREE.RingGeometry(0.028,0.044,24),new THREE.MeshBasicMaterial({color:0xe07828,transparent:true,opacity:0.6,side:THREE.DoubleSide}));
ringM.position.copy(ll2v(jc.lat,jc.lon,1.515));ringM.lookAt(new THREE.Vector3(0,0,0));
earth.add(ringM);var ringMat=ringM.material;

/* HTML city pin badges */
var heroRect=heroEl.getBoundingClientRect();
CITIES.forEach(function(c){
  var el=document.createElement('div');
  el.className='city-pin'+(c.sp?' sp':'');
  el.innerHTML='<div class="pin-body"><div class="pin-dot"></div>'+c.k+'</div><div class="pin-tail"></div>';
  el.title=c.e;
  el.addEventListener('click',function(e){e.stopPropagation();window.open(c.url,'_blank');});
  document.body.appendChild(el);
  c._el=el;
});

/* Visibility flag */
var pinsOK=true;
window.addEventListener('scroll',function(){
  pinsOK=window.scrollY<(heroEl.offsetTop+heroEl.offsetHeight-80);
  if(!pinsOK)CITIES.forEach(function(c){c._el.style.display='none';});
});

/* ANIMATE */
var frame=0;
var wp=new THREE.Vector3();
(function animate(){
  requestAnimationFrame(animate);frame++;
  earth.rotation.y+=0.0011;
  var pulse=0.5+0.5*Math.sin(frame*0.055);
  ringMat.opacity=0.22+pulse*0.6;ringM.scale.setScalar(1+pulse*0.40);

  if(pinsOK){
    var rect=canvas.getBoundingClientRect();
    CITIES.forEach(function(c){
      c._dot.getWorldPosition(wp);
      var pr=wp.clone().project(camera);
      var camDot=wp.dot(camera.position); /* 양수 = 카메라 방향, 음수 = 뒷면 */
      if(camDot>0&&Math.abs(pr.x)<0.96&&Math.abs(pr.y)<0.94){
        c._sx=(pr.x*0.5+0.5)*W;c._sy=(-pr.y*0.5+0.5)*H;c._vis=true;
        c._el.style.left=(c._sx+rect.left)+'px';
        c._el.style.top=(c._sy+rect.top)+'px';
        c._el.style.display='block';
        c._el.style.opacity=Math.min(1,camDot/0.5); /* 가장자리 근처에서 서서히 사라짐 */
      }else{
        c._vis=false;c._el.style.display='none';
      }
    });
  }
  renderer.render(scene,camera);
})();

/* RESIZE */
window.addEventListener('resize',function(){
  W=canvas.offsetWidth;H=canvas.offsetHeight;
  camera.aspect=W/H;camera.updateProjectionMatrix();renderer.setSize(W,H);
});

/* DRAG */
var dragging=false,dragMoved=false,lastX=0,lastY=0;
canvas.style.cursor='grab';
canvas.addEventListener('mousedown',function(e){dragging=true;dragMoved=false;lastX=e.clientX;lastY=e.clientY;canvas.style.cursor='grabbing';});
window.addEventListener('mouseup',function(){dragging=false;canvas.style.cursor='grab';});
window.addEventListener('mousemove',function(e){
  if(!dragging)return;
  var dx=e.clientX-lastX,dy=e.clientY-lastY;
  if(Math.abs(dx)+Math.abs(dy)>3)dragMoved=true;
  earth.rotation.y+=dx*0.005;
  earth.rotation.x=Math.max(-0.75,Math.min(0.75,earth.rotation.x+dy*0.003));
  lastX=e.clientX;lastY=e.clientY;
});
canvas.addEventListener('touchstart',function(e){if(e.touches.length===1){dragging=true;dragMoved=false;lastX=e.touches[0].clientX;lastY=e.touches[0].clientY;}});
canvas.addEventListener('touchend',function(){dragging=false;});
canvas.addEventListener('touchmove',function(e){
  if(!dragging||e.touches.length!==1)return;
  var dx=e.touches[0].clientX-lastX;if(Math.abs(dx)>3)dragMoved=true;
  earth.rotation.y+=dx*0.005;lastX=e.touches[0].clientX;lastY=e.touches[0].clientY;e.preventDefault();
},{passive:false});
})();
