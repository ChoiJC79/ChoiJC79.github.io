(function() {
  const data = {
    "갈비탕": ["고태봉","대림","미성"],
    "곤드레나물밥": ["호반","산마루","예촌","풀향기","산너울장수촌","뜰안에"],
    "오징어·낙지·쭈꾸미": ["해탄","착한낙지","불끈낙지","알쌈쭈꾸미","왕손쭈꾸미","바보형제","쭈꾸홀릭"],
    "내장탕": ["내토","왕수니","특미로","신사동","용두정육","일품양평"],
    "닭개장": ["산우리","향토칡국수","향촌","이가네"],
    "돈가스": ["이소반","수제","삼소라","봉양수제","미스터빠삭","하루엔소쿠","유나","아랑경영회관","비갬","하얀집스낵","국수무라"],
    "만두전골": ["장군집","제천만두국","엄마보쌈","의림만두국"],
    "부대찌개": ["의정부","두꺼비","놀부","맘모스","땅스","킹콩"],
    "보리밥": ["보릿고개","봉양","다미","산골","보리"],
    "순대국밥": ["최부자","우성","장원","한모네","강화한방","무궁화","내토","괴산","용솟골","충청도"],
    "생선구이": ["노송식당","인사동밥집","진가네","장수가"],
    "쌈밥": ["질고개","왕미","산아래","육순이"],
    "샤브샤브": ["채선당","샤브향","이색","운천","소담촌","샤브올데이","편백상회","등촌"],
    "순두부": ["고향맛집","수가성","옛날"],
    "염소탕": ["역전오거리","가마솥","불로초","토담사철탕","살림터","미락정"],
    "육개장": ["소백산","별이네","보령","횡성한우"],
    "짜글이": ["짜글이","하소정육식당"],
    "짬뽕": ["홍반장","청해","루","취란","짬뽕타운","최고집손","감동","교동","바띠에","강","낭만","이가","금룡각","차이나북경","전가복","제주","도야","화성춘","향화성","자비성","다담"],
    "찜닭": ["나들이","원조안동","일미리금계","경북집","동궁"],
    "한식": ["식도락","부성식당","약수터","두꺼비","열두달밥상","호반","시락국","꿀참나무","식사임당"],
    "한정식": ["원뜰","고향이야기","약채락성현","바우본가","청마루","황금들","뜰이있는집","오디향","대보명가"],
    "해장국": ["양지말","신사동","바우","청진동","솔잎","양평","서울집","은실래","시루향기"]
  };

  const root = document.getElementById('jc-picker');
  if (!root) return;
  const catSelect = root.querySelector('#jc-catSelect');
  if (!catSelect) return;
  const pickBtn = root.querySelector('#jc-pickBtn');
  const excludeBtn = root.querySelector('#jc-excludeBtn');
  const resultDiv = root.querySelector('#jc-result');
  const stamp = root.querySelector('#jc-stamp');
  const ticket = root.querySelector('#jc-ticket');
  const progressBar = root.querySelector('#jc-progress');

  Object.keys(data).forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = `${cat} (${data[cat].length}곳)`;
    catSelect.appendChild(opt);
  });

  let lastPick = null;
  let excluded = new Set();
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function buildPool() {
    const cat = catSelect.value;
    let pool = [];
    if (cat === '__all__') {
      Object.entries(data).forEach(([c, list]) => list.forEach(name => pool.push({cat: c, name})));
    } else {
      data[cat].forEach(name => pool.push({cat, name}));
    }
    return pool.filter(item => !excluded.has(item.cat + '|' + item.name));
  }

  function renderFrame(item, spinning) {
    resultDiv.innerHTML = `
      <div>
        <div class="jc-cat-label">${item.cat}</div>
        <div class="jc-name${spinning ? ' spinning' : ''}">${item.name}</div>
      </div>
    `;
  }

  function renderEmpty() {
    resultDiv.innerHTML = `<p class="jc-placeholder">선택지가 모두 소진되었습니다. 목록을 초기화합니다.</p>`;
    excluded.clear();
    stamp.classList.remove('show');
    progressBar.style.width = '0%';
  }

  // 룰렛처럼 처음엔 빠르게, 뒤로 갈수록 느려지는 딜레이 시퀀스를 만든다.
  function buildSpinDelays(count, minDelay, maxDelay) {
    const delays = [];
    for (let i = 0; i < count; i++) {
      const t = i / (count - 1);
      const eased = t * t; // ease-in: 갈수록 딜레이(간격)가 커져서 느려지는 느낌
      delays.push(Math.round(minDelay + (maxDelay - minDelay) * eased));
    }
    return delays;
  }

  function setSpinningState(active) {
    ticket.classList.toggle('rolling', active);
    pickBtn.disabled = active;
    excludeBtn.disabled = active;
    pickBtn.style.opacity = active ? '0.7' : '1';
    pickBtn.style.cursor = active ? 'default' : 'pointer';
  }

  function pickRandom() {
    if (pickBtn.disabled) return;
    const pool = buildPool();
    if (pool.length === 0) { renderEmpty(); return; }

    const finalChoice = pool[Math.floor(Math.random() * pool.length)];
    stamp.classList.remove('show');

    if (reduceMotion || pool.length === 1) {
      lastPick = finalChoice;
      renderFrame(finalChoice, false);
      requestAnimationFrame(() => stamp.classList.add('show'));
      return;
    }

    const delays = buildSpinDelays(24, 45, 260); // 합계 약 2.3~2.6초
    const total = delays.reduce((a, b) => a + b, 0);
    let elapsed = 0;

    setSpinningState(true);
    progressBar.style.width = '0%';

    function nextTick(i) {
      if (i >= delays.length) {
        setSpinningState(false);
        lastPick = finalChoice;
        renderFrame(finalChoice, false);
        const nameEl = resultDiv.querySelector('.jc-name');
        if (nameEl) nameEl.classList.add('settle');
        progressBar.style.width = '100%';
        setTimeout(() => stamp.classList.add('show'), 80);
        setTimeout(() => { progressBar.style.width = '0%'; }, 500);
        return;
      }
      const spinItem = pool[Math.floor(Math.random() * pool.length)];
      renderFrame(spinItem, true);
      elapsed += delays[i];
      progressBar.style.width = Math.round((elapsed / total) * 100) + '%';
      setTimeout(() => nextTick(i + 1), delays[i]);
    }
    nextTick(0);
  }

  pickBtn.addEventListener('click', pickRandom);
  catSelect.addEventListener('change', () => { excluded.clear(); stamp.classList.remove('show'); });
  excludeBtn.addEventListener('click', () => {
    if (lastPick) excluded.add(lastPick.cat + '|' + lastPick.name);
    pickRandom();
  });
})();
