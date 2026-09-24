(function(){
  var root=document.documentElement;
  var I18N={tr:{none:'Henüz cevaplanmadı',partial:function(ok,done,n){return 'Doğru: '+ok+' / '+done+' cevaplanan ('+n+' soru)';},
      final:function(ok,n){return 'Sonuç: '+ok+' / '+n+(ok/n>=0.8?' — geçme eşiği aşıldı ✓':' — hedef 8+/10, tekrar dene');},
      right:'Doğru!',wrong:function(a){return 'Yanlış — doğru cevap '+a;}},
    en:{none:'Not answered yet',partial:function(ok,done,n){return 'Correct: '+ok+' / '+done+' answered ('+n+' questions)';},
      final:function(ok,n){return 'Score: '+ok+' / '+n+(ok/n>=0.8?' — passing threshold reached ✓':' — aim for 8+/10, try again');},
      right:'Correct!',wrong:function(a){return 'Wrong — the correct answer is '+a;}}};
  function T(){return I18N[root.dataset.lang]||I18N.tr;}
  var updaters=[];
  function setLang(l){root.dataset.lang=l;root.lang=l;try{localStorage.setItem('cca-lang',l);}catch(e){}updaters.forEach(function(f){f();});}
  try{var saved=localStorage.getItem('cca-lang');if(saved==='en'||saved==='tr')root.dataset.lang=saved;}catch(e){}
  root.lang=root.dataset.lang;
  document.getElementById('langtoggle').addEventListener('click',function(){setLang(root.dataset.lang==='tr'?'en':'tr');});

  var pages=document.querySelectorAll('.page');
  function route(){
    var h=(location.hash||'#home').slice(1);
    var target=h, el=document.getElementById(h);
    // allow sub-anchors like domain-1-quiz
    var page=el?el.closest('.page'):null;
    if(!page){page=document.getElementById('home');el=page;}
    pages.forEach(function(p){p.classList.toggle('active',p===page);});
    if(el===page){window.scrollTo({top:0});}
    else{el.scrollIntoView();}
  }
  window.addEventListener('hashchange',route);
  route();

  /* ---------- lesson narration + Domain Playlist + Listening Position + Media Session ---------- */
  (function(){
    if(typeof resolveNarrationSrc!=='function'||typeof nextLessonInDomain!=='function'||typeof previousLessonInDomain!=='function'||typeof parseListeningPosition!=='function')return;
    var audio=new Audio(); audio.preload='none';
    var registry={}; // lessonId -> {el, btn}
    var current=null; // {id, btn, el} - lesson loaded into `audio`, whether playing or paused
    var POSITION_KEY='cca-position';
    var lastPersistAt=0;
    var pendingResume=null;
    try{ pendingResume=parseListeningPosition(localStorage.getItem(POSITION_KEY)); }catch(e){}

    function persistPosition(lessonId,lang,time){
      try{ localStorage.setItem(POSITION_KEY,JSON.stringify({lessonId:lessonId,lang:lang,time:time})); }catch(e){}
    }
    function setBtnState(btn,playing){
      btn.classList.toggle('playing',playing);
      btn.setAttribute('aria-label',playing?'Pause narration':'Play narration');
      btn.textContent=playing?'⏸':'▶';
    }
    function clearCurrent(){ if(current){setBtnState(current.btn,false); current=null;} }
    function domainLessons(lessonEl){
      var page=lessonEl.closest('.page.domain');
      return Array.prototype.slice.call(page.querySelectorAll('.lesson')).map(function(el){
        return {id:el.dataset.lessonId, hasNarration:!!resolveNarrationSrc(el.dataset,root.dataset.lang)};
      });
    }
    function lessonTitle(lessonEl,lang){
      var el=lessonEl.querySelector('.ltitle .l-'+lang);
      return el?el.textContent.trim():'';
    }
    function domainTitle(lessonEl,lang){
      var el=lessonEl.closest('.page.domain').querySelector('.dhead h1 .l-'+lang);
      return el?el.textContent.trim():'';
    }
    function updateMediaSessionMetadata(lessonEl){
      if(!('mediaSession' in navigator)||typeof MediaMetadata==='undefined')return;
      var lang=root.dataset.lang;
      navigator.mediaSession.metadata=new MediaMetadata({
        title:lessonTitle(lessonEl,lang),
        artist:domainTitle(lessonEl,lang),
        album:'Claude Certified Architect (Foundations)'
      });
    }
    function playLesson(lessonEl){
      var src=resolveNarrationSrc(lessonEl.dataset,root.dataset.lang);
      if(!src)return;
      var reg=registry[lessonEl.dataset.lessonId];
      if(current&&current.el!==lessonEl)setBtnState(current.btn,false);
      audio.src=src;
      var lessonId=lessonEl.dataset.lessonId, lang=root.dataset.lang, startTime=0;
      if(pendingResume&&pendingResume.lessonId===lessonId&&pendingResume.lang===lang){
        startTime=pendingResume.time; pendingResume=null;
        audio.addEventListener('loadedmetadata',function once(){
          audio.removeEventListener('loadedmetadata',once);
          audio.currentTime=startTime;
        });
      }
      audio.play();
      current={id:lessonId,btn:reg.btn,el:lessonEl};
      updateMediaSessionMetadata(lessonEl);
      lastPersistAt=Date.now();
      persistPosition(lessonId,lang,startTime);
    }
    audio.addEventListener('play',function(){
      if(current)setBtnState(current.btn,true);
      if('mediaSession' in navigator)navigator.mediaSession.playbackState='playing';
    });
    audio.addEventListener('pause',function(){
      if(current)setBtnState(current.btn,false);
      if('mediaSession' in navigator)navigator.mediaSession.playbackState='paused';
    });
    audio.addEventListener('timeupdate',function(){
      if(!current)return;
      var now=Date.now();
      if(now-lastPersistAt<3000)return;
      lastPersistAt=now;
      persistPosition(current.id,root.dataset.lang,audio.currentTime);
    });
    audio.addEventListener('ended',function(){
      if(!current)return;
      var lessonEl=current.el;
      var nextId=nextLessonInDomain(current.id,domainLessons(lessonEl));
      if(nextId&&registry[nextId])playLesson(registry[nextId].el);
      else clearCurrent();
    });

    if('mediaSession' in navigator){
      navigator.mediaSession.setActionHandler('play',function(){ audio.play(); });
      navigator.mediaSession.setActionHandler('pause',function(){ audio.pause(); });
      navigator.mediaSession.setActionHandler('previoustrack',function(){
        if(!current)return;
        var prevId=previousLessonInDomain(current.id,domainLessons(current.el));
        if(prevId&&registry[prevId])playLesson(registry[prevId].el);
      });
      navigator.mediaSession.setActionHandler('nexttrack',function(){
        if(!current)return;
        var nextId=nextLessonInDomain(current.id,domainLessons(current.el));
        if(nextId&&registry[nextId])playLesson(registry[nextId].el);
      });
    }

    document.querySelectorAll('.lesson').forEach(function(lessonEl){
      var summary=lessonEl.querySelector('summary');
      var btn=document.createElement('button');
      btn.type='button'; btn.className='lesson-play'; setBtnState(btn,false);
      summary.appendChild(btn);
      registry[lessonEl.dataset.lessonId]={el:lessonEl,btn:btn};

      function refresh(){
        var src=resolveNarrationSrc(lessonEl.dataset,root.dataset.lang);
        btn.hidden=!src;
        if(!src&&current&&current.el===lessonEl){audio.pause(); clearCurrent();}
      }

      btn.addEventListener('click',function(e){
        e.preventDefault();
        if(current&&current.el===lessonEl){
          if(audio.paused)audio.play(); else audio.pause();
          return;
        }
        playLesson(lessonEl);
      });

      updaters.push(refresh);
      refresh();
    });

    if(pendingResume&&registry[pendingResume.lessonId]&&resolveNarrationSrc(registry[pendingResume.lessonId].el.dataset,pendingResume.lang)){
      setLang(pendingResume.lang);
    }else{
      pendingResume=null;
    }
  })();

  document.querySelectorAll('.quiz').forEach(function(quiz){
    var qs=quiz.querySelectorAll('.q'), scoreTxt=quiz.querySelector('.scoretxt');
    function update(){
      var done=0,ok=0;
      qs.forEach(function(q){if(q.classList.contains('answered')){done++;if(q.dataset.ok==='1')ok++;}});
      var t=T();
      scoreTxt.textContent= done===0 ? t.none : (done<qs.length ? t.partial(ok,done,qs.length) : t.final(ok,qs.length));
      qs.forEach(function(q){var v=q.querySelector('.verdict');if(q.classList.contains('answered'))v.textContent=(q.dataset.ok==='1')?t.right:t.wrong(q.dataset.ans);});
    }
    updaters.push(update);
    qs.forEach(function(q){
      var ans=q.dataset.ans;
      q.querySelectorAll('.opt').forEach(function(btn){
        btn.addEventListener('click',function(){
          if(q.classList.contains('answered'))return;
          var k=btn.dataset.k, v=q.querySelector('.verdict');
          q.classList.add('answered'); q.dataset.ok=(k===ans)?'1':'0';
          q.querySelectorAll('.opt').forEach(function(b){
            b.disabled=true;
            if(b.dataset.k===ans)b.classList.add('correct');
            else if(b===btn)b.classList.add('wrong');
          });
          v.className='verdict '+((k===ans)?'ok':'bad');
          update();
        });
      });
    });
    quiz.querySelector('.reset').addEventListener('click',function(){
      qs.forEach(function(q){
        q.classList.remove('answered'); delete q.dataset.ok;
        q.querySelectorAll('.opt').forEach(function(b){b.disabled=false;b.classList.remove('correct','wrong');});
        var v=q.querySelector('.verdict'); v.textContent=''; v.className='verdict';
      });
      update(); quiz.scrollIntoView({block:'start'});
    });
    update();
  });

  /* ---------- mock exam ---------- */
  var M={tr:{q:'Soru',of:'/',flag:'İşaretle',unflag:'İşareti kaldır',finish:'Sınavı bitir',
      confirm:function(n){return n>0?n+' soru cevaplanmadı. Yine de bitirmek istiyor musun?':'Sınavı bitirmek istiyor musun?';},
      timeup:'Süre doldu — sınav otomatik teslim edildi.',score:'puan',pass:'Geçti',fail:'Kaldı',
      correct:'doğru',domain:'Domain',all:'Tüm sorular',wrong:'Sadece yanlışlar',unans:'Cevapsız',
      again:'Yeni deneme',home:'← Ana sayfa',history:'Önceki denemeler',your:'Senin cevabın',right:'Doğru cevap',noans:'—',
      timeused:'Kullanılan süre'},
    en:{q:'Question',of:'/',flag:'Flag',unflag:'Unflag',finish:'Finish exam',
      confirm:function(n){return n>0?n+' questions are unanswered. Finish anyway?':'Finish the exam?';},
      timeup:'Time is up — the exam was submitted automatically.',score:'points',pass:'Pass',fail:'Fail',
      correct:'correct',domain:'Domain',all:'All questions',wrong:'Only wrong',unans:'Unanswered',
      again:'New attempt',home:'← Home',history:'Previous attempts',your:'Your answer',right:'Correct answer',noans:'—',
      timeused:'Time used'}};
  function MT(){return M[root.dataset.lang]||M.tr;}
  var PER_Q=120, LIMIT=0, exam=null, tick=null;
  function QF(q,f){var en=root.dataset.lang==='en';if(en&&q.en)return q.en[f];if(en&&f==='body')return NOTE_EN+q[f];return q[f];}
  var NOTE_EN='<p class="langnote">English version of this question is not available yet — showing the Turkish text.</p>';
  function scName(id){var sc=MOCK_SCEN.filter(function(s){return s.id===id;})[0];return sc?(root.dataset.lang==='en'?sc.en:sc.tr):'';}
  function scCtx(id){var sc=MOCK_SCEN.filter(function(s){return s.id===id;})[0];return sc?sc.ctx:'';}
  var $=function(id){return document.getElementById(id);};
  function shuffle(a){for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;}return a;}
  function buildExam(){
    var scs=shuffle([1,2,3,4,5,6]).slice(0,4), qs=[];
    scs.forEach(function(sc){
      var pool=shuffle(MOCK_POOL.filter(function(q){return q.sc===sc;}).slice()).slice(0,15);
      qs=qs.concat(pool);
    });
    LIMIT=qs.length*PER_Q;
    return {scs:scs,qs:qs,ans:new Array(qs.length).fill(null),flag:new Array(qs.length).fill(false),i:0,start:Date.now(),done:false};
  }
  function fmt(s){s=Math.max(0,s);var m=Math.floor(s/60),x=s%60;return (m<10?'0':'')+m+':'+(x<10?'0':'')+x;}
  function renderQ(){
    var t=MT(),i=exam.i,q=exam.qs[i];
    $('mock-progress').textContent=t.q+' '+(i+1)+' '+t.of+' '+exam.qs.length;
    var sb=$('mock-scen'); sb.querySelector('summary').textContent=(root.dataset.lang==='en'?'Scenario ':'Senaryo ')+q.sc+': '+scName(q.sc); sb.querySelector('p').innerHTML=scCtx(q.sc);
    if(i===0||exam.qs[i-1].sc!==q.sc){sb.open=true;}
    var h='<article class="q"><div class="qhead"><span class="qn">'+t.q+' '+(i+1)+'</span><span class="qts">'+q.ts+'</span></div><div class="prose qbody">'+QF(q,'body')+'</div><div class="opts">';
    var op=QF(q,'opts');
    ['A','B','C','D'].forEach(function(k){h+='<button class="opt'+(exam.ans[i]===k?' picked':'')+'" data-k="'+k+'"><span class="k">'+k+'</span><span class="t">'+op[k]+'</span></button>';});
    h+='</div></article>';
    $('mock-q').innerHTML=h;
    $('mock-q').querySelectorAll('.opt').forEach(function(b){b.addEventListener('click',function(){exam.ans[i]=(exam.ans[i]===b.dataset.k)?null:b.dataset.k;renderQ();});});
    $('mock-flag').textContent=exam.flag[i]?t.unflag:t.flag; $('mock-flag').className='reset'+(exam.flag[i]?' on':'');
    $('mock-prev').disabled=i===0; $('mock-next').disabled=i===exam.qs.length-1;
    var p='',last=null;exam.qs.forEach(function(qq,k){if(qq.sc!==last){p+='<div class="phead">'+(root.dataset.lang==='en'?'Scenario ':'Senaryo ')+qq.sc+' — '+scName(qq.sc)+'</div>';last=qq.sc;}p+='<button data-i="'+k+'" class="'+(exam.ans[k]?'done ':'')+(exam.flag[k]?'flag ':'')+(k===i?'cur':'')+'">'+(k+1)+'</button>';});
    $('mock-palette').innerHTML=p;
    $('mock-palette').querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){exam.i=+b.dataset.i;renderQ();window.scrollTo({top:0});});});
  }
  function startExam(){
    exam=buildExam();
    $('mock-intro').hidden=true;$('mock-result').hidden=true;$('mock-exam').hidden=false;
    renderQ();window.scrollTo({top:0});
    clearInterval(tick);
    tick=setInterval(function(){
      var left=LIMIT-Math.floor((Date.now()-exam.start)/1000);
      $('mock-timer').textContent=fmt(left); $('mock-timer').classList.toggle('low',left<600);
      if(left<=0){finish(true);}
    },500);
    $('mock-timer').textContent=fmt(LIMIT);
  }
  function score(){
    var per={};
    exam.qs.forEach(function(q,i){var d=q.d;per[d]=per[d]||{n:0,ok:0};per[d].n++;if(exam.ans[i]===q.ans)per[d].ok++;});
    var w=0,tot=0;
    Object.keys(per).forEach(function(d){var wt=MOCK_META.weights[d];w+=wt*(per[d].ok/per[d].n);tot+=wt;});
    return {per:per,scaled:Math.round(100+900*(w/tot))};
  }
  function finish(auto){
    if(exam.done)return;
    var t=MT();
    if(!auto){var un=exam.ans.filter(function(a){return !a;}).length;if(!confirm(t.confirm(un)))return;}
    exam.done=true;clearInterval(tick);
    var used=Math.min(LIMIT,Math.floor((Date.now()-exam.start)/1000));
    var r=score();
    try{var hist=JSON.parse(localStorage.getItem('cca-mock')||'[]');hist.unshift({t:Date.now(),s:r.scaled,used:used});localStorage.setItem('cca-mock',JSON.stringify(hist.slice(0,10)));}catch(e){}
    lastResult={r:r,used:used,auto:auto};
    renderResult(r,used,auto);
  }
  function renderResult(r,used,auto){
    var t=MT(),lang=root.dataset.lang,passed=r.scaled>=720;
    var h='<a class="back" href="#home">'+t.home+'</a><p class="kicker">'+(lang==='en'?'Result':'Sonuç')+'</p>';
    if(auto)h+='<p class="langnote">'+t.timeup+'</p>';
    h+='<div class="resultcard"><div class="bigscore">'+r.scaled+'<small>/ 1000 '+t.score+'</small></div><span class="passtag '+(passed?'ok':'bad')+'">'+(passed?t.pass:t.fail)+' · '+(passed?'≥':'<')+' 720</span>';
    h+='<p style="color:var(--muted);margin:14px 0 0">'+t.timeused+': '+fmt(used)+'</p><ul class="dombreak">';
    Object.keys(r.per).sort().forEach(function(d){var p=r.per[d],pc=Math.round(100*p.ok/p.n);
      h+='<li style="--c:'+MOCK_META.hues[d]+'"><span>'+t.domain+' '+d+' — '+(lang==='en'?MOCK_META.titles_en[d]:MOCK_META.titles_tr[d])+' <span style="color:var(--muted)">(%'+MOCK_META.weights[d]+')</span></span><b>'+p.ok+' / '+p.n+' '+t.correct+'</b><span class="bar"><i style="width:'+pc+'%"></i></span></li>';});
    h+='</ul><ul class="scenbreak">';
    exam.scs.forEach(function(sc){var n=0,ok=0;exam.qs.forEach(function(q,i){if(q.sc===sc){n++;if(exam.ans[i]===q.ans)ok++;}});h+='<li><span>'+(lang==='en'?'Scenario ':'Senaryo ')+sc+' — '+scName(sc)+'</span><b>'+ok+' / '+n+'</b></li>';});
    h+='</ul></div>';
    h+='<div class="revfilter"><button class="reset on" data-f="all">'+t.all+'</button><button class="reset" data-f="wrong">'+t.wrong+'</button><button class="reset" data-f="unans">'+t.unans+'</button></div><div id="mock-review">';
    var lastsc=null;
    exam.qs.forEach(function(q,i){var a=exam.ans[i],ok=a===q.ans;
      if(q.sc!==lastsc){h+='<h3 class="secttl" style="font-size:1.2rem">'+(lang==='en'?'Scenario ':'Senaryo ')+q.sc+' — '+scName(q.sc)+'</h3>';lastsc=q.sc;}
      var op=QF(q,'opts');
      h+='<article class="q rev answered" data-state="'+(a?(ok?'ok':'wrong'):'unans')+'"><div class="qhead"><span class="qn">'+t.q+' '+(i+1)+'</span><span class="qts">'+q.ts+'</span></div><div class="prose qbody">'+QF(q,'body')+'</div><div class="opts">';
      ['A','B','C','D'].forEach(function(k){h+='<button class="opt'+(k===q.ans?' correct':(k===a?' wrong':''))+'" disabled><span class="k">'+k+'</span><span class="t">'+op[k]+'</span></button>';});
      h+='</div><div class="verdict '+(a?(ok?'ok':'bad'):'bad')+'">'+t.your+': '+(a||t.noans)+' · '+t.right+': '+q.ans+'</div><div class="expl prose"><div class="explhd">'+t.right+': <b>'+q.ans+'</b></div>'+QF(q,'expl')+'</div></article>';});
    h+='</div><p class="pagenav"><a href="#home">'+t.home+'</a><a href="#mock" id="mock-again">'+t.again+' →</a></p>';
    $('mock-exam').hidden=true;$('mock-result').hidden=false;$('mock-result').innerHTML=h;window.scrollTo({top:0});
    $('mock-result').querySelectorAll('.revfilter button').forEach(function(b){b.addEventListener('click',function(){
      $('mock-result').querySelectorAll('.revfilter button').forEach(function(x){x.classList.remove('on');});b.classList.add('on');
      var f=b.dataset.f;$('mock-review').querySelectorAll('.q').forEach(function(q){q.style.display=(f==='all'||(f==='wrong'&&q.dataset.state==='wrong')||(f==='unans'&&q.dataset.state==='unans'))?'':'none';});});});
    $('mock-again').addEventListener('click',function(e){e.preventDefault();showIntro();});
  }
  function showIntro(){
    var t=MT();
    $('mock-exam').hidden=true;$('mock-result').hidden=true;$('mock-intro').hidden=false;
    var h='';try{var hist=JSON.parse(localStorage.getItem('cca-mock')||'[]');if(hist.length){h='<div class="hist"><b>'+t.history+'</b><ul>'+hist.map(function(x){var d=new Date(x.t);return '<li>'+d.toLocaleDateString(root.dataset.lang==='en'?'en-GB':'tr-TR')+' '+d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})+' — <b>'+x.s+'</b>/1000 · '+fmt(x.used)+'</li>';}).join('')+'</ul></div>';}}catch(e){}
    $('mock-history').innerHTML=h; window.scrollTo({top:0});
  }
  $('mock-start').addEventListener('click',startExam);
  $('mock-finish').addEventListener('click',function(){finish(false);});
  $('mock-prev').addEventListener('click',function(){if(exam.i>0){exam.i--;renderQ();window.scrollTo({top:0});}});
  $('mock-next').addEventListener('click',function(){if(exam.i<exam.qs.length-1){exam.i++;renderQ();window.scrollTo({top:0});}});
  $('mock-flag').addEventListener('click',function(){exam.flag[exam.i]=!exam.flag[exam.i];renderQ();});
  var lastResult=null;
  updaters.push(function(){if(exam&&!exam.done&&!$('mock-exam').hidden)renderQ();if(!$('mock-intro').hidden)showIntro();if(exam&&exam.done&&lastResult&&!$('mock-result').hidden){var y=window.scrollY;renderResult(lastResult.r,lastResult.used,lastResult.auto);window.scrollTo({top:y});}});
  window.addEventListener('hashchange',function(){if(location.hash==='#mock'&&(!exam||exam.done))showIntro();});
  if(location.hash==='#mock')showIntro();
})();