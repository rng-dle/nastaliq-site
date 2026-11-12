(function(){
  var tabs=document.querySelectorAll('.tabs button');
  tabs.forEach(function(b){b.onclick=function(){
    tabs.forEach(function(x){x.setAttribute('aria-selected',x===b)});
    document.querySelectorAll('.sp').forEach(function(p){p.hidden=p.id!==b.dataset.p});
  }});
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
  f.addEventListener('submit',function(e){
    e.preventDefault();
    if(!f.reportValidity())return;
    var lines=[];
    f.querySelectorAll('[name]').forEach(function(el){if(el.value.trim())lines.push(el.getAttribute('data-l')+': '+el.value.trim())});
    location.href='mailto:hello@nastaliq.co?subject='+encodeURIComponent(f.getAttribute('data-subject'))+'&body='+encodeURIComponent(lines.join('\n'));
  });
})();
