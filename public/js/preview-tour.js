// Preview flow: fog over the dashboard until a name is entered -> guided tour -> fog lifts -> ends on "Book a demo".
(function(){
  var root=document.getElementById('preview'),win=document.getElementById('pv-win'),nm=document.getElementById('pv-name');
  if(!root||!win||!nm)return;
  var S=[
    {s:'#pv-name',t:'Your business',d:'Your company name flows through the whole dashboard, sidebar and address bar.'},
    {s:'#pv-ind',t:'Your industry',d:'Each industry loads real figures from a public company in that field.'},
    {s:'.pv-up',t:'Your logo',d:'Drop in a logo. We pull your brand colours from it and use them everywhere.'},
    {s:'#pv-sws',t:'Your colours',d:'Use a colour from your logo, a preset, or pick your own.'},
    {s:'#pv-win .top',t:'Your own address',d:'Pick a prefix like hq or portal, and type your real domain.',reveal:1},
    {s:'#pv-win aside ul',t:'Every part of the business',d:'Sales, stock, purchasing, accounting and reports in one place.',v:'home'},
    {s:'#pv-win .kpis',t:'Numbers that matter',d:'Click any card to jump to the screen behind it.',v:'home'},
    {s:'#pv-win .pvc.chart',t:'Charts you can poke',d:'Hover the line, switch between breakdown and over time, click any bar for the record.',v:'home'},
    {s:'#pv-win .lsel',t:'Your language',d:'The interface switches between 20 languages. Try Arabic or Urdu for right-to-left.',v:'home'},
    {s:'#pv-win .plus',t:'Create anything fast',d:'Start a sale or a purchase order from anywhere.',v:'home'},
    {s:'#pv-win .thm[data-theme]',t:'Light or dark',d:'One tap. Your team picks what suits them.',v:'home'},
    {s:'#pv-win [data-bell]',t:'Your day in one place',d:'Tasks and alerts collect here, so the home screen stays clear.',v:'home'},
    {s:'#pv-win .rpt',t:'Reports with detail',d:'Overview, breakdown, trend and financials, each exportable to CSV.',v:'reports'},
    {s:'#pv-win .apps',t:'Connect your apps',d:'Gmail, Slack, QuickBooks, Shopify and more through Composio.',v:'integrations'},
    {s:'#lead button[type=submit]',t:'Say hi',d:'Send us your details and we will build this for your business, with your own numbers.',last:1,v:'home'}
  ],i=0,ov,pop,hole,on=false,fog,revealed=false;
  function q(x){return document.querySelector(x)}
  function nav(v){var b=win.querySelector('[data-view="'+v+'"]');if(b&&!b.hasAttribute('aria-current'))b.click()}

  /* ---- fog ---- */
  var wrap=document.createElement('div');wrap.className='pv-stage';win.parentNode.insertBefore(wrap,win);wrap.appendChild(win);
  fog=document.createElement('div');fog.className='pv-fog';fog.setAttribute('role','status');wrap.appendChild(fog);
  function paintFog(){
    var n=nm.value.trim();
    if(n.length<2){fog.innerHTML='<i class="m1"></i><i class="m2"></i><i class="m3"></i><div class="fc"><h4>Make it yours</h4><p>Type your business name above and your dashboard appears.</p></div>';nm.classList.add('nudge')}
    else{nm.classList.remove('nudge');fog.innerHTML='<i class="m1"></i><i class="m2"></i><i class="m3"></i><div class="fc"><h4>Welcome to '+n.replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})+'</h4><div><button type="button" class="tr-go" id="pv-go">Take the tour</button></div></div>'}
  }
  function reveal(){
    if(revealed)return;revealed=true;nm.classList.remove('nudge');root.classList.add('revealed');fog.classList.add('gone');
    setTimeout(function(){fog.remove()},1500);
  }
  nm.addEventListener('input',function(){if(!revealed&&!on)paintFog()});
  paintFog();
  window.nqReveal=reveal;

  /* ---- tour ---- */
  function mk(){
    hole=document.createElement('div');hole.className='tr-hole';
    pop=document.createElement('div');pop.className='tr-pop';pop.setAttribute('role','dialog');pop.setAttribute('aria-live','polite');
    ov=document.createElement('div');ov.className='tr-ov';ov.addEventListener('click',function(){end()});
    document.body.appendChild(ov);document.body.appendChild(hole);document.body.appendChild(pop);
  }
  function place(el,pad){var r=el.getBoundingClientRect();hole.style.cssText='top:'+(r.top-pad)+'px;left:'+(r.left-pad)+'px;width:'+(r.width+pad*2)+'px;height:'+(r.height+pad*2)+'px';return r}
  function show(n){
    i=n;var s=S[i];if(s.reveal)reveal();if(s.v)nav(s.v);
    var el=q(s.s);if(!el||!el.getClientRects().length){return i<S.length-1?show(i+1):end()}
    el.scrollIntoView({block:'center',behavior:'instant'});
    requestAnimationFrame(function(){
      var pad=8,r=place(el,pad);
      pop.className='tr-pop'+(s.last?' last':'');
      pop.innerHTML='<div class="tr-n">'+(i+1)+' / '+S.length+'</div><h4>'+s.t+'</h4><p>'+s.d+'</p><div class="tr-b"><button type="button" data-k="skip" class="tr-skip">Skip</button><span>'
        +(i?'<button type="button" data-k="back">Back</button>':'')+'<button type="button" data-k="next" class="tr-go">'+(s.last?'Book a demo':'Next')+'</button></span></div>';
      var pw=pop.offsetWidth,ph=pop.offsetHeight,vw=innerWidth,vh=innerHeight,small=vw<=700,top,left;
      if(small){pop.style.cssText='left:12px;right:12px;bottom:12px;top:auto';top=vh-12-ph;left=12}
      else{var below=r.bottom+pad+14+ph<vh;top=below?r.bottom+pad+14:Math.max(12,r.top-pad-14-ph);left=Math.min(vw-pw-12,Math.max(12,r.left+r.width/2-pw/2));
        if(r.height>vh*.55){top=Math.max(12,Math.min(vh-ph-12,r.top+20));left=r.right+pad+14+pw<vw?r.right+pad+14:Math.max(12,r.left-pw-pad-14)}
        if(s.last)top=Math.max(12,Math.min(vh-ph-12,r.bottom+pad+14));
        pop.style.cssText='top:'+top+'px;left:'+left+'px'}
      var g=pop.querySelector('.tr-go');if(g)g.focus({preventScroll:true});
    });
  }
  function start(){if(on)return;on=true;mk();document.documentElement.classList.add('tr-on');addEventListener('keydown',key,true);addEventListener('resize',rs);addEventListener('scroll',sc,true);show(0)}
  function end(go){if(!on)return;on=false;[ov,hole,pop].forEach(function(x){x&&x.remove()});document.documentElement.classList.remove('tr-on');removeEventListener('keydown',key,true);removeEventListener('resize',rs);removeEventListener('scroll',sc,true);
    reveal();
    if(go===true){var c=q('#contact');if(c)c.scrollIntoView({behavior:'smooth',block:'start'})}}
  function rs(){if(on)show(i)}
  var rq=0;function sc(){if(!on||rq)return;rq=requestAnimationFrame(function(){rq=0;var el=q(S[i].s);if(!el)return;place(el,8);hole.style.transition='none'})}
  function key(e){if(!on)return;if(e.key==='Escape'){e.preventDefault();end()}else if(e.key==='ArrowRight'||e.key==='Enter'&&e.target.tagName!=='BUTTON'){e.preventDefault();nx()}else if(e.key==='ArrowLeft'){e.preventDefault();if(i)show(i-1)}}
  function nx(){S[i].last?end(true):i<S.length-1?show(i+1):end()}
  document.addEventListener('click',function(e){
    var c=e.target.closest&&e.target.closest.bind(e.target);if(!c)return;
    var b=c('.tr-pop button');if(b){var k=b.dataset.k;k==='next'?nx():k==='back'?show(i-1):end();return}
    if(c('#pv-go'))start();else if(c('#pv-sk'))reveal();else if(c('#pv-tour')){if(!revealed)reveal();start()}
  });
  var host=root.querySelector('.pv-bar .f:last-child')||root.querySelector('.pv-bar');
  if(host){var t=document.createElement('button');t.type='button';t.id='pv-tour';t.className='pv-tour';t.textContent='Replay tour';host.appendChild(t)}
  if(new URLSearchParams(location.search).get('pv'))setTimeout(paintFog,0);
  window.nqTour=start;
})();
