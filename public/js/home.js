(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tabs button')),sec=document.getElementById('sectors'),cur=0,timer,stopped=false;
  function show(i){
    cur=i;
    tabs.forEach(function(x,k){x.setAttribute('aria-selected',k===i)});
    document.querySelectorAll('.sp').forEach(function(p){p.hidden=p.id!==tabs[i].dataset.p});
  }
  tabs.forEach(function(b,i){b.onclick=function(){stopped=true;clearInterval(timer);show(i)}});
  if(!sec||tabs.length<2||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  var paused=false,visible=false;
  function tick(){if(!stopped&&!paused&&visible&&!document.hidden)show((cur+1)%tabs.length)}
  timer=setInterval(tick,6000);
  sec.addEventListener('mouseenter',function(){paused=true});sec.addEventListener('mouseleave',function(){paused=false});
  sec.addEventListener('focusin',function(){paused=true});sec.addEventListener('focusout',function(){paused=false});
  sec.addEventListener('touchstart',function(){stopped=true},{passive:true});
  if('IntersectionObserver' in window)new IntersectionObserver(function(e){visible=e[0].isIntersecting}).observe(sec);else visible=true;
})();
(function(){
  var mb=document.querySelector('.menu-btn'),nv=document.getElementById('nav');
  if(mb&&nv){
    mb.onclick=function(){var o=nv.classList.toggle('open');mb.setAttribute('aria-expanded',o)};
    nv.addEventListener('click',function(e){if(e.target.closest('a')){nv.classList.remove('open');mb.setAttribute('aria-expanded','false')}});
  }
})();
(function(){
  var f=document.getElementById('lead');
  if(!f)return;
  var sel=f.querySelector('#ind'),wrap=f.querySelector('#other-wrap'),other=f.querySelector('#other');
  if(sel&&wrap){sel.addEventListener('change',function(){
    var on=sel.value==='Other';wrap.hidden=!on;
    if(on)other.focus();else other.value='';
  })}
  var t0=Date.now(),note=f.querySelector('#lead-note'),btn=f.querySelector('button[type=submit]'),biz=f.querySelector('[name=business]'),bizTouched=false;
  biz.addEventListener('input',function(){bizTouched=true});
  var fnm=f.querySelector('[name=name]');if(fnm)fnm.addEventListener('input',function(){fnm.dataset.t=1});var pn=document.getElementById('pv-name');
  if(pn)pn.addEventListener('input',function(){if(!bizTouched)biz.value=pn.value});
  function mailto(lines){location.href='mailto:hello@nastaliq.co?subject='+encodeURIComponent(f.getAttribute('data-subject'))+'&body='+encodeURIComponent(lines.join('\n'))}
  f.addEventListener('submit',function(e){
    e.preventDefault();
    if(!f.reportValidity())return;
    var body={t:Date.now()-t0},lines=[];
    f.querySelectorAll('[name]').forEach(function(el){body[el.name]=el.value.trim();if(el.name!=='hp'&&el.value.trim())lines.push(el.getAttribute('data-l')+': '+el.value.trim())});
    var pv=window.nqPreview?window.nqPreview():{};
    if(pv.preview){body.preview=pv.preview;body.logo=pv.logo;lines.push('Preview: '+pv.preview.name+', '+pv.preview.industry+', '+pv.preview.accent)}
    btn.disabled=true;note.textContent='Sending...';
    fetch('/api/lead',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)})
      .then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{s:r.status,j:j}})})
      .then(function(x){
        if(x.s===200){f.reset();note.textContent='Thank you. We will reply by email with a demo, a plan and a price.';btn.textContent='Sent';return}
        btn.disabled=false;
        if(x.s===400||x.s===413){note.textContent=x.j.error||'Please check the form.';return}
        fail();
      })
      .catch(fail);
    function fail(){btn.disabled=false;note.textContent='We could not send that. Opening your email app instead.';mailto(lines)}
  });
})();
