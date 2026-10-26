(function(){
  var root=document.documentElement;
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
  var cp=document.getElementById('cp');
  if(cp){
    var label=cp.textContent;
    cp.onclick=function(){
      var done=cp.getAttribute('data-done')||'Copied';
      function ok(){cp.textContent=done;setTimeout(function(){cp.textContent=label},1800)}
      try{navigator.clipboard.writeText('hello@nastaliq.co').then(ok,function(){})}catch(e){}
    };
  }
})();
