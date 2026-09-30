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
    if(s>=50) return '오늘 일몰은 '+sunsetHm+'쯤입니다. 색이 크게 타오르진 않아도, 해 질 녘은 남아 있습니다.';
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
    document.getElementById('dusk-score').innerHTML=score+'<span class="dusk-score-unit">/100</span>';
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
      week+='<div class="dusk-wday'+cls+'"><div class="dusk-bar"><i style="height:'+ht+'px"></i></div>'+
        '<span class="dusk-wd">'+label+'</span><span class="dusk-ws">'+sc+'</span></div>';
    }
    document.getElementById('dusk-week').innerHTML=week;
    var n=new Date();
    document.getElementById('dusk-updated').textContent=
      n.getHours()+':'+pad(n.getMinutes())+' 기준 · 제천';
  }).catch(fail);
})();
