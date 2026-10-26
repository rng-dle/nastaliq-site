(function(){
  var root=document.documentElement;
  function setLang(l){root.lang=l;document.getElementById('b-en').setAttribute('aria-pressed',l==='en');document.getElementById('b-fr').setAttribute('aria-pressed',l==='fr');try{localStorage.setItem('nq-lang',l)}catch(e){}}
  var s='en';try{s=localStorage.getItem('nq-lang')||'en'}catch(e){}
  setLang(s==='fr'?'fr':'en');
  document.getElementById('b-en').onclick=function(){setLang('en')};
  document.getElementById('b-fr').onclick=function(){setLang('fr')};
  var tabs=document.querySelectorAll('.tabs button');
  tabs.forEach(function(b){b.onclick=function(){
    tabs.forEach(function(x){x.setAttribute('aria-selected',x===b)});
    document.querySelectorAll('.sp').forEach(function(p){p.hidden=p.id!==b.dataset.p});
  }});
  document.getElementById('cp').onclick=function(){var b=this;
    try{navigator.clipboard.writeText('hello@nastaliq.co').then(function(){b.textContent='Copied'},function(){b.textContent='Select and copy'})}catch(e){b.textContent='Select and copy'}};
  var mb=document.querySelector('.menu-btn'),nv=document.getElementById('nav');
  if(mb&&nv){mb.onclick=function(){var o=nv.classList.toggle('open');mb.setAttribute('aria-expanded',o)};nv.addEventListener('click',function(e){if(e.target.closest('a')){nv.classList.remove('open');mb.setAttribute('aria-expanded','false')}})}
})();
