// 제천 노을지수와 일출·일몰을 Open-Meteo로 계산해 홈 패널에 그린다
(function(){
  var root=document.getElementById('dusk-strip');
  if(!root) return;
  var LAT=37.13, LON=128.19;
  var DOW=['일','월','화','수','목','금','토'];
  var FX='https://api.open-meteo.com/v1/forecast?latitude='+LAT+'&longitude='+LON+
    '&daily=sunrise,sunset,precipitation_sum,weather_code,cloud_cover_mean'+
    '&hourly=cloud_cover,relative_humidity_2m,precipitation'+
    '&timezone=Asia%2FSeoul&forecast_days=7';
  var AQ='https://air-quality-api.open-meteo.com/v1/air-quality?latitude='+LAT+'&longitude='+LON+
    '&hourly=pm10&timezone=Asia%2FSeoul&forecast_days=7';

  function pad(n){return String(n).padStart(2,'0');}
  function hm(iso){
    if(!iso) return '—';
    var d=new Date(iso);
    return pad(d.getHours())+':'+pad(d.getMinutes());
  }
  function addMin(iso,min){
    return new Date(new Date(iso).getTime()+min*60000);
  }
  function dayLen(a,b){
    var m=Math.max(0,Math.round((new Date(b)-new Date(a))/60000));
    return Math.floor(m/60)+'시간 '+pad(m%60)+'분';
  }
  function nearestHour(times,iso){
    var t=new Date(iso).getTime(), best=0, gap=Infinity;
    for(var i=0;i<times.length;i++){
      var g=Math.abs(new Date(times[i]).getTime()-t);
      if(g<gap){gap=g;best=i;}
    }
    return best;
  }
  function cloudScore(c){
    if(c==null) return 50;
    if(c<=5) return 48;
    if(c<35) return Math.round(48+(c-5)*(52/30));
    if(c<=55) return 100;
    if(c<85) return Math.round(100-(c-55)*(70/30));
    return Math.max(12,Math.round(30-(c-85)));
  }
  function pmScore(pm){
    if(pm==null) return 70;
    if(pm<=30) return 95;
    if(pm<=50) return 80;
    if(pm<=80) return 55;
    if(pm<=150) return 30;
    return 12;
  }
  function rhScore(rh){
    if(rh==null) return 70;
    if(rh<=45) return 95;
    if(rh<=65) return 82;
    if(rh<=80) return 60;
    return 32;
  }
  function rainScore(mm){
    if(mm==null||mm<=0) return 100;
    if(mm<0.2) return 70;
    if(mm<1) return 35;
    return 8;
  }
  function total(c,pm,rh,rain){
    return Math.round(c*0.42+rain*0.22+pm*0.18+rh*0.18);
  }
  function grade(s){
    if(s>=80) return '화려함';
    if(s>=65) return '좋음';
    if(s>=50) return '은은함';
    if(s>=35) return '흐릿';
    return '흐림';
  }
  function pmWord(pm){
    if(pm==null) return '자료 없음';
    if(pm<=30) return '맑음';
    if(pm<=50) return '보통';
    if(pm<=80) return '나쁨 쪽';
    return '탁함';
  }
  function note(s,sunsetHm,cloud){
    if(cloud!=null&&cloud<15) return '오늘 일몰은 '+sunsetHm+'쯤입니다. 하늘이 맑아 색은 은은한 쪽으로 남을 수 있습니다.';
    if(s>=80) return '오늘 일몰은 '+sunsetHm+'쯤입니다. 구름이 빛을 받아 제천 서쪽 하늘이 진하게 물들 수 있습니다.';
    if(s>=65) return '오늘 일몰은 '+sunsetHm+'쯤입니다. 자리를 잡으면 괜찮은 노을을 기대해도 좋을 듯합니다.';
    if(s>=50) return '오늘 일몰은 '+sunsetHm+'쯤입니다. 색이 크게 타오르진 않아도, 은은한 저녁노을은 볼 수 있습니다.';
    if(s>=35) return '오늘 일몰은 '+sunsetHm+'쯤입니다. 하늘이 탁하거나 가려 색은 옅을 수 있습니다.';
    return '오늘 일몰은 '+sunsetHm+'쯤입니다. 구름이나 비가 빛을 많이 가릴 듯합니다.';
  }
  function fact(k,v,s){
    return '<div class="dusk-fact"><span class="dusk-fact-k">'+k+'</span>'+
      '<span class="dusk-fact-v">'+v+'</span>'+
      (s?'<span class="dusk-fact-s">'+s+'</span>':'')+'</div>';
  }
  function fail(){
    var box=document.getElementById('dusk-note');
    if(box) box.textContent='제천 하늘 정보를 불러오지 못했습니다.';
  }

  var REDUCE=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // 패널이 화면에 들어온 뒤 한 번만 fn 실행 (모션이 보이지 않는 곳에서 끝나지 않게)
  var seen=false, waiting=[];
  function whenVisible(fn){ if(seen) fn(); else waiting.push(fn); }
  if(!('IntersectionObserver' in window)){ seen=true; root.classList.add('is-in'); }
  else new IntersectionObserver(function(es,io){
    if(!es[0].isIntersecting) return;
    io.disconnect(); seen=true; root.classList.add('is-in');
    waiting.splice(0).forEach(function(f){f();});
  },{threshold:0.25}).observe(root);

  function tween(ms,step){
    if(REDUCE){ step(1); return; }
    var t0=performance.now();
    (function f(now){
      var k=Math.min(1,(now-t0)/ms);
      step(1-Math.pow(1-k,3));
      if(k<1) requestAnimationFrame(f);
    })(t0);
  }
  // 호를 상자 실제 픽셀 크기로 그린다 (늘린 SVG는 선 굵기와 점선 길이가 틀어짐)
  function sizeArc(){
    var svg=document.getElementById('dusk-arc'), W=svg.clientWidth, H=svg.clientHeight;
    if(!W||!H) return;
    svg.setAttribute('viewBox','0 0 '+W+' '+H);
    var d='M0,'+H+' A'+(W/2)+','+H+' 0 0 1 '+W+','+H;
    svg.querySelectorAll('path').forEach(function(p){p.setAttribute('d',d);});
  }
  sizeArc();
  window.addEventListener('resize',sizeArc);
  // 일출~일몰 사이 현재 위치까지 해가 호를 따라 움직인다
  function placeSun(rise,set){
    var sun=document.getElementById('dusk-sun'), done=document.getElementById('dusk-arc-done');
    var now=Date.now(), a=new Date(rise).getTime(), b=new Date(set).getTime();
    var f=Math.max(0,Math.min(1,(now-a)/(b-a)));
    if(now>b) sun.classList.add('is-set');
    if(now<a) sun.classList.add('is-before');
    whenVisible(function(){
      tween(1600,function(k){
        var x=f*k, th=Math.PI*x;
        sun.style.left=(50-50*Math.cos(th))+'%';
        sun.style.bottom=(Math.sin(th)*100)+'%';
        done.style.strokeDashoffset=String(100-x*100);
      });
    });
  }
  function countUp(el,to){
    whenVisible(function(){
      tween(1200,function(k){
        el.innerHTML=Math.round(to*k)+'<span class="dusk-score-unit">/100</span>';
      });
    });
  }

  // 오늘의 달: 모양(위상)과 뜨고 지는 시각·방위를 SunCalc로 계산
  var DIRS=['북','북북동','북동','동북동','동','동남동','남동','남남동','남','남남서','남서','서남서','서','서북서','북서','북북서'];
  function bearing(t){
    var az=SunCalc.getMoonPosition(t,LAT,LON).azimuth*180/Math.PI;
    return (az+180+360)%360;
  }
  function moonPhase(p){
    if(p<0.035||p>0.965) return ['삭','해와 같은 쪽에 있어 하늘에서 거의 보이지 않습니다.'];
    if(p<0.215) return ['초승달','해 진 뒤 서쪽 하늘 낮은 곳에 가는 눈썹처럼 잠깐 걸립니다.'];
    if(p<0.285) return ['상현달','낮에 떠서 해 질 무렵 남쪽 하늘에 오른쪽 반이 밝게 보입니다.'];
    if(p<0.465) return ['차오르는 달','해 질 무렵 남동쪽 하늘에 떠 있어 저녁노을과 함께 볼 수 있습니다.'];
    if(p<0.535) return ['보름달','해가 질 때쯤 동쪽에서 떠올라 밤새 하늘을 가로지릅니다.'];
    if(p<0.715) return ['기우는 달','밤이 깊어진 뒤 동쪽에서 떠올라 새벽까지 남쪽 하늘에 남습니다.'];
    if(p<0.785) return ['하현달','자정 무렵 떠서 새벽 남쪽 하늘에 왼쪽 반이 밝게 보입니다.'];
    return ['그믐달','해 뜨기 전 새벽, 동쪽 하늘 낮은 곳에서 가늘게 보입니다.'];
  }
  // 북반구 기준: 차오를 때 오른쪽, 기울 때 왼쪽이 밝다
  function moonPath(p,r){
    var c=Math.cos(2*Math.PI*p), rx=(Math.abs(c)*r).toFixed(2), wax=p<0.5;
    var outer=wax?1:0, term=wax?(c>0?0:1):(c>0?1:0);
    return 'M0,'+(-r)+' A'+r+','+r+' 0 0 '+outer+' 0,'+r+' A'+rx+','+r+' 0 0 '+term+' 0,'+(-r)+' Z';
  }
  function drawMoon(){
    if(!window.SunCalc) return;
    var now=new Date();
    var ill=SunCalc.getMoonIllumination(now);
    // ponytail: 뜨고 지는 시각은 방문자 브라우저의 날짜 기준. 해외 시간대에서는 하루 어긋날 수 있다
    var tm=SunCalc.getMoonTimes(now,LAT,LON);
    var ph=moonPhase(ill.phase);
    document.getElementById('dusk-moon-lit').setAttribute('d',moonPath(ill.phase,44));
    document.getElementById('dusk-moon-name').textContent='오늘의 달 · '+ph[0];
    document.getElementById('dusk-moon-meta').textContent=
      '밝기 '+Math.round(ill.fraction*100)+'% · 월령 '+(ill.phase*29.53).toFixed(1)+'일';
    document.getElementById('dusk-moon-desc').textContent=ph[1];
    function pos(label,t){
      if(!t) return fact(label,'—','오늘은 없음');
      var b=bearing(t);
      return fact(label,hm(t),DIRS[Math.round(b/22.5)%16]+'쪽 지평선 · 방위 '+Math.round(b)+'°');
    }
    var parts=[['뜨는 곳',tm.rise],['지는 곳',tm.set]];
    if(tm.rise&&tm.set&&tm.set<tm.rise) parts.reverse();
    document.getElementById('dusk-moon-pos').innerHTML=
      tm.alwaysUp?fact('달','종일 떠 있음',''):tm.alwaysDown?fact('달','뜨지 않음',''):
      parts.map(function(x){return pos(x[0],x[1]);}).join('');
    document.getElementById('dusk-moon').hidden=false;
  }
  drawMoon();

  Promise.all([
    fetch(FX).then(function(r){return r.json();}),
    fetch(AQ).then(function(r){return r.json();}).catch(function(){return null;})
  ]).then(function(pair){
    var fx=pair[0], aq=pair[1];
    if(!fx||!fx.daily||!fx.hourly){fail();return;}
    var today=new Date().toLocaleDateString('sv-SE');
    var di=fx.daily.time.indexOf(today);
    if(di<0) di=0;
    var rise=fx.daily.sunrise[di], set=fx.daily.sunset[di];
    var hi=nearestHour(fx.hourly.time,set);
    var cloud=fx.hourly.cloud_cover[hi];
    var rh=fx.hourly.relative_humidity_2m[hi];
    var rain=fx.hourly.precipitation[hi];
    var pm=null;
    if(aq&&aq.hourly&&aq.hourly.time){
      pm=aq.hourly.pm10[nearestHour(aq.hourly.time,set)];
    }
    var score=total(cloudScore(cloud),pmScore(pm),rhScore(rh),rainScore(rain));
    var setHm=hm(set);
    var goldFrom=hm(addMin(set,-20));
    var goldTo=hm(addMin(set,15));

    document.getElementById('dusk-sunrise').textContent=hm(rise);
    document.getElementById('dusk-sunset').textContent=setHm;
    countUp(document.getElementById('dusk-score'),score);
    placeSun(rise,set);
    document.getElementById('dusk-grade').textContent=grade(score);
    document.getElementById('dusk-note').textContent=note(score,setHm,cloud);
    document.getElementById('dusk-facts').innerHTML=
      fact('구름',Math.round(cloud)+'%','일몰 무렵')+
      fact('미세먼지',pm==null?'—':Math.round(pm)+'㎍/㎥',pmWord(pm))+
      fact('습도',Math.round(rh)+'%','낮을수록 색이 선명')+
      fact('골든아워',goldFrom+'–'+goldTo,'낮 길이 '+dayLen(rise,set));

    var week='';
    for(var i=0;i<fx.daily.time.length;i++){
      var dt=fx.daily.time[i];
      var seti=fx.daily.sunset[i];
      var h=nearestHour(fx.hourly.time,seti);
      var c=fx.hourly.cloud_cover[h];
      var rhh=fx.hourly.relative_humidity_2m[h];
      var rr=fx.hourly.precipitation[h];
      if(c==null) c=fx.daily.cloud_cover_mean[i];
      if(rr==null) rr=fx.daily.precipitation_sum[i];
      var pmi=null;
      if(aq&&aq.hourly&&aq.hourly.time) pmi=aq.hourly.pm10[nearestHour(aq.hourly.time,seti)];
      var sc=total(cloudScore(c),pmScore(pmi),rhScore(rhh),rainScore(rr));
      var ht=Math.max(8,Math.round(sc*0.48));
      var cls=dt===today?' is-today':'';
      var label=dt===today?'오늘':DOW[new Date(dt+'T12:00:00').getDay()];
      week+='<div class="dusk-wday'+cls+'" style="--i:'+i+'"><div class="dusk-bar"><i style="height:'+ht+'px"></i></div>'+
        '<span class="dusk-wd">'+label+'</span><span class="dusk-ws">'+sc+'</span></div>';
    }
    document.getElementById('dusk-week').innerHTML=week;
    var n=new Date();
    document.getElementById('dusk-updated').textContent=
      n.getHours()+':'+pad(n.getMinutes())+' 기준 · 제천';
  }).catch(fail);
})();
