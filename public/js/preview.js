// "The fix" live preview: a working mini dashboard the visitor can brand. Data comes from preview-data.js.
(function(){
  var root=document.getElementById('preview'),D=window.NQ_DATA;
  if(!root||!D)return;
  var $=function(id){return document.getElementById(id)},win=$('pv-win');
  var VIEWS=[['home','Home'],['sales','Sales'],['inventory','Inventory'],['purchasing','Purchasing'],['accounting','Accounting'],['reports','Reports'],['integrations','Integrations']];
  var PRESETS=['#ffc23a','#2f6fed','#1d8a4c','#e0483a','#7a3fd1','#0f172a'];
  var st={name:'',ind:'Distribution',accent:'#ffc23a',from:'preset',logo:null,palette:[],dirty:false,view:'home',chart:'auto',pre:'hq',host:'',done:{},me:'',dark:false,rep:'overview',apps:{},lang:'en',plus:false,sort:null,q:'',low:false,sel:null,bell:false,orders:{},approved:{},seen:{home:1}};

  var I=window.NQ_I18N||{names:[['en','English']],T:{},rtl:{}};
  (function(){var n=((navigator.language||'en')+'').slice(0,2).toLowerCase();if(I.T[n])st.lang=n})();
  function tr(s){var m=I.T[st.lang];return m&&m[s]||s}
  /* ---------- helpers ---------- */
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function money(m){var d=m*1000;if(st.lang!=='en'){try{return new Intl.NumberFormat(st.lang,{style:'currency',currency:'USD',currencyDisplay:'narrowSymbol',notation:'compact',maximumFractionDigits:d>=1e7?1:2}).format(d)}catch(e){}}return d>=1e6?'$'+(d/1e6).toFixed(d>=1e7?1:2)+'M':'$'+Math.round(d/1e3)+'K'}
  function val(d,v){return d.unit==='%'?v+'%':money(v)}
  function chg(c,p){return p==null||!p?null:(c-p)/p*100}
  function fmtChg(x){return x==null?'—':(x>=0?'+':'')+x.toFixed(1)+'%'}
  function lum(h){var n=parseInt(h.slice(1),16),c=[n>>16&255,n>>8&255,n&255].map(function(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]}
  function rng(seed){var a=0;for(var i=0;i<seed.length;i++)a=(a*31+seed.charCodeAt(i))|0;return function(){a=(a+0x6D2B79F5)|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
  function cur(){return D[st.ind]}
  function rows(){ // sales rows for the current industry, filtered and sorted
    var d=cur(),r=d.mix.map(function(m){var c=chg(m[1],m[2]);return{l:m[0],v:m[1],p:m[2],g:c!=null?c:m[3]!=null?m[3]:null}});
    var tot=r.reduce(function(a,x){return a+x.v},0);r.forEach(function(x){x.s=x.v/tot*100});
    if(st.q)r=r.filter(function(x){return x.l.toLowerCase().indexOf(st.q.toLowerCase())>-1});
    if(st.sort){var k=st.sort.k,s=st.sort.d;r.sort(function(a,b){var x=k==='l'?a.l.localeCompare(b.l):(a[k]==null?-1e9:a[k])-(b[k]==null?-1e9:b[k]);return s*x})}
    return r;
  }
  function stock(){var d=cur(),R=rng(st.ind);return d.mix.map(function(m){var re=40+Math.round(R()*80),oh=Math.round(R()*190)+10;return{l:m[0],oh:oh,re:re,id:'s-'+m[0]}})}
  function pos(){var d=cur(),R=rng(st.ind+'po'),out=d.mix.slice(0,5).map(function(m,i){return{id:'PO-'+(4180+i*7+Math.round(R()*5)),l:m[0],amt:Math.round(m[1]*(d.unit==='%'?30:.011)*10)/10,key:'p-'+m[0]}});
    Object.keys(st.orders).forEach(function(k){if(st.orders[k])out.unshift({id:'PO-'+(4300+Object.keys(st.orders).indexOf(k)),l:k,amt:Math.round(cur().mix[0][1]*.004*10)/10,key:'o-'+k,fresh:1})});return out}
  function sortTh(k,l,cls){var a=st.sort&&st.sort.k===k;return'<th class="'+(cls||'')+'"><button type="button" data-sort="'+k+'"'+(a?' aria-sort="'+(st.sort.d>0?'ascending':'descending')+'"':'')+'>'+l+(a?(st.sort.d>0?' ▲':' ▼'):'')+'</button></th>'}
  var ICONS=['M4 18 9 12l4 3 7-9','M4 7h16v11H4zM4 11h16M16 15h2','M12 4 3 20h18zM12 10v5M12 17.5v.1','M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 7v5l3 2'];
  var SL=['var(--ac)','var(--t)','color-mix(in srgb,var(--ac) 55%,var(--w))','var(--m)','color-mix(in srgb,var(--ac) 30%,var(--w))','var(--l2)','color-mix(in srgb,var(--ac) 75%,#000)'],PRE=['hq','ops','portal','cloud','app'];
  function slug(){return(st.name||'').toLowerCase().replace(/[^a-z0-9]+/g,'')||'yourcompany'}
  function eff(d){return st.chart==='auto'?(d.trend.length>=3?'trend':'mix'):st.chart}
  function curve(p){var s='M'+p[0][0].toFixed(1)+','+p[0][1].toFixed(1);for(var i=0;i<p.length-1;i++){var a=p[i-1]||p[i],b=p[i],c=p[i+1],e=p[i+2]||c,t=.2;s+=' C'+(b[0]+(c[0]-a[0])*t).toFixed(1)+','+(b[1]+(c[1]-a[1])*t).toFixed(1)+' '+(c[0]-(e[0]-b[0])*t).toFixed(1)+','+(c[1]-(e[1]-b[1])*t).toFixed(1)+' '+c[0].toFixed(1)+','+c[1].toFixed(1)}return s}
  function area(d){
    var s=d.trend,W=640,H=230,L=14,R=14,T=16,B=30,vs=s.map(function(x){return x[1]}),hi=Math.max.apply(null,vs),lo0=Math.min.apply(null,vs),lo=Math.max(0,lo0-(hi-lo0||hi*.1)*1.1),top=hi+(hi-lo)*.12,
      P=s.map(function(x,i){return[L+i*(W-L-R)/Math.max(1,s.length-1),T+(1-(x[1]-lo)/(top-lo))*(H-T-B)]}),ln=curve(P),g='';
    for(var k=0;k<4;k++){var y=T+k*(H-T-B)/3;g+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y.toFixed(1)+'" y2="'+y.toFixed(1)+'"/>'}
    var ch=chg(vs[vs.length-1],vs[0]);
    return'<div class="cw"><div class="big"><b>'+money(vs[vs.length-1])+'</b><i class="pl '+(ch>=0?'up':'dn')+'">'+(ch>=0?'▲ ':'▼ ')+Math.abs(ch).toFixed(1)+'% since '+esc(s[0][0].replace(' (derived)',''))+'</i></div>'
      +'<svg viewBox="0 0 '+W+' '+H+'" class="area" role="img" aria-label="'+esc(d.trendLabel)+'"><defs><linearGradient id="pvg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--ac);stop-opacity:.38"/><stop offset="1" style="stop-color:var(--ac);stop-opacity:0"/></linearGradient></defs><g class="gl">'+g+'</g>'
      +'<path d="'+ln+' L'+P[P.length-1][0].toFixed(1)+','+(H-B)+' L'+P[0][0].toFixed(1)+','+(H-B)+' Z" fill="url(#pvg)"/><path d="'+ln+'" class="ln"/>'
      +P.map(function(q,i){return'<circle class="pt" data-i="'+i+'" cx="'+q[0].toFixed(1)+'" cy="'+q[1].toFixed(1)+'" r="5"/><text x="'+q[0].toFixed(1)+'" y="'+(H-8)+'" text-anchor="'+(i===0?'start':i===P.length-1?'end':'middle')+'">'+esc(s[i][0].replace(' (derived)',''))+'</text><rect data-pt="'+i+'" x="'+(q[0]-(W/s.length)/2).toFixed(1)+'" y="0" width="'+(W/s.length).toFixed(1)+'" height="'+H+'" fill="transparent"/>'}).join('')
      +'</svg><div class="tip" id="pv-tip" hidden></div></div>'}
  function hbars(d){
    var m=d.mix,mx=Math.max.apply(null,m.map(function(x){return Math.max(x[1],x[2]||0)})),prior=m.some(function(x){return x[2]!=null});
    return'<div class="hb">'+m.map(function(x,i){var g=chg(x[1],x[2]);if(g==null)g=x[3];
      return'<button type="button" class="hbr" data-bar="'+i+'" data-w="mix"><span class="hbl">'+esc(x[0].replace(' (derived)',''))+'</span><span class="hbt">'+(x[2]!=null?'<u class="gh" style="width:'+(x[2]/mx*100).toFixed(1)+'%"></u>':'')+'<u style="width:'+(x[1]/mx*100).toFixed(1)+'%"></u></span><b>'+val(d,x[1])+'</b><i class="'+(g==null?'':g>=0?'up':'dn')+'">'+fmtChg(g)+'</i></button>'}).join('')+'</div>'+(prior?'<p class="note">The pale bar behind each one is the prior period.</p>':'')}
  function chartCard(d){var e=eff(d);return'<section class="pvc chart"><div class="pvh"><h5>'+esc(e==='trend'?d.trendLabel:d.mixLabel)+'</h5><div class="seg" role="tablist"><button type="button" data-chart="mix" aria-pressed="'+(e==='mix')+'">Breakdown</button><button type="button" data-chart="trend" aria-pressed="'+(e==='trend')+'">Over time</button></div></div>'+(e==='trend'?area(d):hbars(d))+'</section>'}
  function donut(d){
    var m=d.mix,tot=m.reduce(function(a,x){return a+x[1]},0),C=2*Math.PI*54,off=0,seg='';
    m.forEach(function(x,i){var len=x[1]/tot*C;seg+='<circle class="sl" data-slice="'+i+'" r="54" cx="70" cy="70" style="stroke:'+SL[i%SL.length]+'" stroke-dasharray="'+Math.max(0,len-2).toFixed(2)+' '+C.toFixed(2)+'" stroke-dashoffset="'+(-off).toFixed(2)+'"><title>'+esc(x[0])+'</title></circle>';off+=len});
    return'<section class="pvc"><div class="pvh"><h5>'+tr('Share of total')+'</h5></div><div class="dn2"><svg viewBox="0 0 140 140" role="img" aria-label="'+esc(d.mixLabel)+'">'+seg+'<text x="70" y="75" text-anchor="middle" class="dv"'+((d.unit==='%'?'100%':money(tot)).length>8?' style="font-size:11px"':'')+'>'+(d.unit==='%'?'100%':money(tot))+'</text></svg><ul class="lg">'+m.slice(0,5).map(function(x,i){return'<li><button type="button" data-slice="'+i+'"><s style="background:'+SL[i%SL.length]+'"></s><span>'+esc(x[0].replace(' (derived)','').split(',')[0])+'</span><b>'+(x[1]/tot*100).toFixed(0)+'%</b></button></li>'}).join('')+'</ul></div></section>'}
  function todo(d){
    var m=d.mix,R=rng(st.ind+'t'),T=['Approve purchase order PO-'+(4180+Math.round(R()*9)),'Review '+m[0][0].replace(' (derived)','').split(',')[0]+' numbers','Follow up on the overdue bill','Send the morning digest to the team'],n=0;
    var li=T.map(function(x,i){var k=st.ind+i,on=st.done[k];if(on)n++;return'<li><button type="button" class="tk'+(on?' on':'')+'" data-task="'+k+'" aria-pressed="'+!!on+'"><i></i><span>'+esc(x)+'</span></button></li>'}).join('');
    return{html:li,n:n,total:T.length}}
  function vHome(d){
    var k=d.kpis.map(function(x,i){return'<button type="button" class="kpi" data-go="'+x[4]+'"><span class="ki"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="'+ICONS[i%4]+'"/></svg></span><span class="kl">'+esc(x[0])+'</span><b>'+esc(x[1])+'</b><i class="pl '+(x[3]?'up':'dn')+'">'+esc(x[2])+'</i></button>'}).join('');
    return'<div class="kpis">'+k+'</div><div class="g32">'+chartCard(d)+donut(d)+'</div>'}
  function tableCard(d,short){
    var r=rows(),h=short?'<h5>'+esc(tt(d))+'</h5><button type="button" class="lnk" data-go="sales">See all</button>':'<h5>'+esc(tt(d))+'</h5>';
    var body=r.length?r.map(function(x){return'<tr data-row="'+esc(x.l)+'" tabindex="0"><td>'+esc(x.l)+'</td><td class="n">'+val(d,x.v)+'</td><td class="n '+(x.g==null?'':x.g>=0?'up':'dn')+'">'+fmtChg(x.g)+'</td><td class="pvs"><u style="width:'+x.s.toFixed(0)+'%"></u></td></tr>'}).join(''):'<tr><td colspan="4" class="empty">Nothing matches "'+esc(st.q)+'".</td></tr>';
    return'<section class="pvc tbl"><div class="pvh">'+h+'</div><table><thead><tr>'+sortTh('l','Name')+sortTh('v','Amount','n')+sortTh('g','Change','n')+sortTh('s','Share','pvs')+'</tr></thead><tbody>'+body+'</tbody></table></section>'}
  function tt(d){return d.unit==='%'?d.mixLabel:'Sales by '+d.mixLabel.split(',')[0].toLowerCase()}
  function vSales(d){return tableCard(d,false)}
  function vInventory(d){
    var s=stock().filter(function(x){return(!st.low||x.oh<x.re)&&(!st.q||x.l.toLowerCase().indexOf(st.q.toLowerCase())>-1)});
    var b=s.map(function(x){var low=x.oh<x.re,on=st.orders[x.l];return'<tr><td>'+esc(x.l)+'</td><td class="n">'+x.oh+'</td><td class="n">'+x.re+'</td><td><span class="gauge"><u class="'+(low?'lo':'')+'" style="width:'+Math.min(100,Math.round(x.oh/(x.re*2)*100))+'%"></u></span></td><td class="n">'+(on?'<span class="pill ok">Ordered</span>':low?'<button type="button" class="pvm" data-order="'+esc(x.l)+'">Reorder</button>':'<span class="pill">OK</span>')+'</td></tr>'}).join('')||'<tr><td colspan="5" class="empty">Nothing to show.</td></tr>';
    return'<section class="pvc tbl"><div class="pvh"><h5>Stock by '+esc(d.mixLabel.split(',')[0].toLowerCase())+'</h5><div class="seg"><button type="button" data-low="0" aria-pressed="'+!st.low+'">All</button><button type="button" data-low="1" aria-pressed="'+st.low+'">Low stock</button></div></div><table><thead><tr><th>Item group</th><th class="n">On hand</th><th class="n">Reorder at</th><th>Level</th><th class="n"></th></tr></thead><tbody>'+b+'</tbody></table><p class="note">Stock levels here are illustrative. '+esc(d.co)+' does not publish them.</p></section>'}
  function vPurchasing(d){
    var p=pos().filter(function(x){return!st.q||x.l.toLowerCase().indexOf(st.q.toLowerCase())>-1});
    var b=p.map(function(x){var ok=st.approved[x.key];return'<tr><td>'+x.id+(x.fresh?' <span class="pill ok">New</span>':'')+'</td><td>'+esc(x.l)+'</td><td class="n">'+money(x.amt)+'</td><td class="n">'+(ok?'<span class="pill ok">Approved</span>':'<button type="button" class="pvm" data-approve="'+esc(x.key)+'">Approve</button>')+'</td></tr>'}).join('')||'<tr><td colspan="4" class="empty">Nothing to show.</td></tr>';
    return'<section class="pvc tbl"><div class="pvh"><h5>Purchase orders</h5><span class="pill">'+p.filter(function(x){return!st.approved[x.key]}).length+' waiting</span></div><table><thead><tr><th>Order</th><th>Item group</th><th class="n">Amount</th><th class="n"></th></tr></thead><tbody>'+b+'</tbody></table><p class="note">Orders are illustrative. Reorder something in Inventory and it lands here.</p></section>'}
  function vAccounting(d){
    var b=d.fin.map(function(x){var c=chg(x[1],x[2]);return'<tr data-fin="'+esc(x[0])+'" tabindex="0"><td>'+esc(x[0])+'</td><td class="n">'+money(x[1])+'</td><td class="n">'+(x[2]==null?'—':money(x[2]))+'</td><td class="n '+(c==null?'':c>=0?'up':'dn')+'">'+fmtChg(c)+'</td></tr>'}).join('');
    return'<section class="pvc tbl"><div class="pvh"><h5>Reported figures, '+esc(d.per)+'</h5></div><table><thead><tr><th>Line</th><th class="n">This year</th><th class="n">Last year</th><th class="n">Change</th></tr></thead><tbody>'+b+'</tbody></table></section>'}
  function stat(l,v,s){return'<div class="pvst"><span>'+esc(l)+'</span><b>'+esc(v)+'</b><i>'+esc(s)+'</i></div>'}
  function lbl(x){return x.replace(' (derived)','')}
  function movers(d){var r=d.mix.map(function(m,i){var g=chg(m[1],m[2]);return{i:i,l:lbl(m[0]),g:g!=null?g:m[3]}}).filter(function(x){return x.g!=null}).sort(function(a,b){return b.g-a.g});
    if(!r.length)return'';return'<section class="pvc"><div class="pvh"><h5>'+tr('Growth')+'</h5></div><ul class="mv">'+r.map(function(x){return'<li><button type="button" data-bar="'+x.i+'" data-w="mix"><span>'+esc(x.l)+'</span><i class="pl '+(x.g>=0?'up':'dn')+'">'+fmtChg(x.g)+'</i></button></li>'}).join('')+'</ul></section>'}
  function vReports(d){
    var tabs=[['overview','Overview'],['breakdown','Breakdown'],['trend','Over time'],['fin','Financials']],r=st.rep,m=d.mix,body='';
    var hi=m.reduce(function(a,x){return x[1]>a[1]?x:a},m[0]),lo=m.reduce(function(a,x){return x[1]<a[1]?x:a},m[0]),tot=m.reduce(function(a,x){return a+x[1]},0),tr0=d.trend,gr=tr0.length>1?chg(tr0[tr0.length-1][1],tr0[0][1]):null;
    if(r==='overview'){
      body='<div class="pvsts">'+stat(tr('Highest'),val(d,hi[1]),lbl(hi[0]))+stat(tr('Lowest'),val(d,lo[1]),lbl(lo[0]))+stat(tr('Average'),val(d,d.unit==='%'?Math.round(tot/m.length*10)/10:tot/m.length),m.length+' · '+d.mixLabel.split(',')[0].toLowerCase())+stat(tr('Growth'),gr==null?'—':fmtChg(gr),gr==null?d.trendLabel:lbl(tr0[0][0])+' → '+lbl(tr0[tr0.length-1][0]))+'</div><div class="g32">'+chartCard(d)+movers(d)+'</div>'}
    else if(r==='breakdown')body=tableCard(d,false);
    else if(r==='trend'){
      var rows=tr0.map(function(x,i){var c=i?chg(x[1],tr0[i-1][1]):null;return'<tr><td>'+esc(lbl(x[0]))+'</td><td class="n">'+money(x[1])+'</td><td class="n '+(c==null?'':c>=0?'up':'dn')+'">'+(c==null?'—':fmtChg(c))+'</td></tr>'}).join('');
      body='<section class="pvc"><div class="pvh"><h5>'+esc(d.trendLabel)+'</h5></div>'+(tr0.length>=3?area(d):'<p class="note">Only '+tr0.length+' periods are filed for this company.</p>')+'</section><section class="pvc tbl"><table><thead><tr><th>Period</th><th class="n">Amount</th><th class="n">'+tr('Growth')+'</th></tr></thead><tbody>'+rows+'</tbody></table></section>'}
    else body=vAccounting(d);
    return'<div class="rpt"><div class="seg" role="tablist">'+tabs.map(function(x){return'<button type="button" data-rep="'+x[0]+'" aria-pressed="'+(r===x[0])+'">'+tr(x[1])+'</button>'}).join('')+'</div><div><button type="button" class="pvm ghost" data-act="mail">Email weekly</button><button type="button" class="pvm" data-csv="1">'+tr('Download CSV')+'</button></div></div>'+body}
  var APPS=[['Gmail','Email'],['Slack','Chat'],['Google Sheets','Spreadsheets'],['QuickBooks','Accounting'],['Shopify','Ecommerce'],['HubSpot','CRM'],['Stripe','Payments'],['Notion','Docs'],['Outlook','Email'],['Microsoft Teams','Chat'],['Xero','Accounting'],['Google Calendar','Calendar']];
  function vIntegrations(d){
    var n=Object.keys(st.apps).filter(function(k){return st.apps[k]}).length;
    return'<section class="pvc int"><div><h3>Connect your apps</h3><p>Nastaliq connects to 1,000+ apps through <b>Composio</b>, so orders, invoices and customers flow in and out without custom work.</p></div><span class="pill'+(n?' ok':'')+'">'+n+' '+tr('Connected').toLowerCase()+'</span></section><div class="apps">'+APPS.map(function(a){var on=st.apps[a[0]];return'<div class="app-t"><span class="lo">'+esc(a[0].charAt(0))+'</span><div><b>'+esc(a[0])+'</b><i>'+esc(a[1])+'</i></div><button type="button" class="pvm'+(on?' ghost':'')+'" data-app="'+esc(a[0])+'" aria-pressed="'+!!on+'">'+(on?'✓ '+tr('Connected'):tr('Connect'))+'</button></div>'}).join('')+'</div><p class="note">Plus 1,000+ more. Logos omitted in this preview.</p>'}
  var VF={home:vHome,sales:vSales,inventory:vInventory,purchasing:vPurchasing,accounting:vAccounting,reports:vReports,integrations:vIntegrations};

  /* ---------- shell ---------- */
  function shell(){
    var d=cur(),name=st.name||'Your Company',logo=st.logo?'<span class="lo img"><img alt="" src="'+st.logo+'"></span>':'<span class="lo">'+esc(name.charAt(0).toUpperCase())+'</span>';
    var nav=VIEWS.map(function(v){return'<li><button type="button" data-view="'+v[0]+'"'+(st.view===v[0]?' aria-current="page"':'')+'>'+tr(v[1])+'</button></li>'}).join('');
    var v=VF[st.view](d);
    var title=st.view==='home'?tr('Good morning')+', <input id="pv-me" class="me" value="'+esc(st.me)+'" placeholder="'+esc(tr('your name'))+'" maxlength="30" size="'+Math.max(9,st.me.length+1)+'" autocomplete="off" aria-label="Your first name">':tr(VIEWS.filter(function(x){return x[0]===st.view})[0][1]);
    var td=todo(d),open=td.total-td.n+d.hl.length;
    var bell='<div class="pop" id="pv-pop"'+(st.bell?'':' hidden')+'><h6>'+tr('Today')+' <span class="pill'+(td.n===td.total?' ok':'')+'">'+td.n+'/'+td.total+'</span></h6><ul class="tks">'+td.html+'</ul><h6>'+tr('Notifications')+'</h6>'+d.hl.map(function(x,i){return'<button type="button" data-hl="'+i+'"><b>'+esc(x[0])+'</b><span>'+esc(x[1])+'</span></button>'}).join('')+'</div>';
    win.innerHTML='<div class="top"><i></i><i></i><i></i><span class="url"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg><select id="pv-pre" aria-label="Address prefix">'+PRE.map(function(p){return'<option'+(p===st.pre?' selected':'')+'>'+p+'</option>'}).join('')+'</select><em>.</em><input id="pv-host" value="'+esc(st.host)+'" placeholder="'+slug()+'.com" aria-label="Your website address" maxlength="40" spellcheck="false" autocomplete="off"></span></div>'
      +'<div class="app"><aside><div class="brand">'+logo+'<b>'+esc(name)+'</b></div><ul>'+nav+'</ul><p class="co">'+tr('Sample data')+' · <b>'+esc(d.co)+'</b></p></aside>'
      +'<main><div class="pvt"><h4>'+title+'</h4><label class="srch"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg><input id="pv-q" type="search" placeholder="'+esc(tr('Search'))+'" value="'+esc(st.q)+'" aria-label="Search this page"></label><select id="pv-lang" class="lsel" aria-label="'+esc(tr('Language'))+'">'+I.names.map(function(n){return'<option value="'+n[0]+'"'+(n[0]===st.lang?' selected':'')+' title="'+n[1]+'">'+n[0].toUpperCase()+'</option>'}).join('')+'</select><div class="bellw"><button type="button" class="thm plus" data-plus="1" aria-label="New" aria-expanded="'+st.plus+'"><svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></button><div class="pop pm"'+(st.plus?'':' hidden')+'><button type="button" data-act="sale"><b>+ '+esc(tr('New sale'))+'</b></button><button type="button" data-act="po"><b>+ '+esc(tr('Purchase order'))+'</b></button></div></div><button type="button" class="thm" data-theme="1" aria-pressed="'+st.dark+'" aria-label="'+esc(st.dark?tr('Light'):tr('Dark'))+'" title="'+esc(st.dark?tr('Light'):tr('Dark'))+'"><svg viewBox="0 0 24 24">'+(st.dark?'<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M5.6 18.4 7 17M17 7l1.4-1.4"/>':'<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>')+'</svg></button><div class="bellw"><button type="button" class="bell" data-bell="1" aria-label="Notifications" aria-expanded="'+st.bell+'"><svg viewBox="0 0 24 24"><path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5h4"/></svg><em>'+open+'</em></button>'+bell+'</div></div>'
      +'<div class="view" key="'+st.view+'">'+v+'</div></main>'
      +'<div class="drawer" id="pv-drawer"'+(st.sel?'':' hidden')+'>'+drawer(d)+'</div></div><div class="toast" id="pv-toast" role="status" aria-live="polite"></div>';
    var q=$('pv-q');if(q&&document.activeElement===document.body&&st._focusQ){q.focus();q.setSelectionRange(q.value.length,q.value.length)}
    paint();
  }
  function drawer(d){
    if(!st.sel)return'';var s=st.sel,body='';
    if(s.t==='row'){var x=rows().concat(d.mix.map(function(m){return{l:m[0],v:m[1],p:m[2],g:chg(m[1],m[2])!=null?chg(m[1],m[2]):m[3]}})).filter(function(r){return r.l===s.k})[0];if(!x)return'';var tot=d.mix.reduce(function(a,m){return a+m[1]},0);
      body='<h3>'+esc(x.l)+'</h3><dl><dt>'+(d.unit==='%'?'Share':'Amount')+'</dt><dd>'+val(d,x.v)+'</dd><dt>Prior period</dt><dd>'+(x.p==null?'—':val(d,x.p))+'</dd><dt>Change</dt><dd class="'+(x.g==null?'':x.g>=0?'up':'dn')+'">'+fmtChg(x.g)+'</dd><dt>Share of total</dt><dd>'+(x.v/tot*100).toFixed(1)+'%</dd></dl><div class="gauge big"><u style="width:'+(x.v/tot*100).toFixed(0)+'%"></u></div>'}
    else if(s.t==='fin'){var f=d.fin.filter(function(r){return r[0]===s.k})[0];if(!f)return'';var c=chg(f[1],f[2]);body='<h3>'+esc(f[0])+'</h3><dl><dt>This year</dt><dd>'+money(f[1])+'</dd><dt>Last year</dt><dd>'+(f[2]==null?'—':money(f[2]))+'</dd><dt>Change</dt><dd class="'+(c==null?'':c>=0?'up':'dn')+'">'+fmtChg(c)+'</dd></dl>'}
    else{var h=d.hl[s.k];body='<h3>'+esc(h[0])+'</h3><p>'+esc(h[1])+'</p>'}
    return'<button type="button" class="x" data-close="1" aria-label="Close">&times;</button>'+body+'<p class="note">In Nastaliq this opens the full record: documents, history and who changed what.</p>'}
  function toast(m){var t=$('pv-toast');if(!t)return;t.textContent=m;t.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(function(){t.classList.remove('on')},2200)}
  function paint(){ // accent colours live in CSS variables so changing colour does not rebuild the dashboard
    var a=st.accent;win.style.setProperty('--ac',a);win.style.setProperty('--on-ac',lum(a)>.4?'#1a1200':'#fff');
    win.style.setProperty('--ac-ink',st.dark?'color-mix(in srgb,'+a+' 65%,#fff)':lum(a)>.5?'#6b5200':a);win.classList.toggle('dk',st.dark);win.dir=I.rtl[st.lang]?'rtl':'ltr';
  }

  /* ---------- events (delegated) ---------- */
  win.addEventListener('click',function(e){
    var t=e.target.closest('button,tr[data-row],tr[data-fin],[data-slice]');
    if(!t){if(st.bell||st.plus){st.bell=false;st.plus=false;shell()}return}
    var D2=cur();
    if(t.dataset.view){st.view=t.dataset.view;st.q='';st.sel=null;st.bell=false;st.seen[st.view]=1;st.dirty=true;shell();win.scrollIntoView({block:'nearest'})}
    else if(t.dataset.go){st.view=t.dataset.go;st.q='';st.seen[st.view]=1;st.dirty=true;shell()}
    else if(t.dataset.sort){var k=t.dataset.sort;st.sort=st.sort&&st.sort.k===k?(st.sort.d>0?{k:k,d:-1}:null):{k:k,d:1};shell()}
    else if(t.dataset.chart){st.chart=t.dataset.chart;shell()}
    else if(t.dataset.slice!=null){st.sel={t:'row',k:D2.mix[+t.dataset.slice][0]};shell()}
    else if(t.dataset.plus){st.plus=!st.plus;st.bell=false;shell()}
    else if(t.dataset.theme){st.dark=!st.dark;st.dirty=true;shell()}
    else if(t.dataset.rep){st.rep=t.dataset.rep;st.sort=null;st.q='';shell()}
    else if(t.dataset.app){var ap=t.dataset.app;st.apps[ap]=!st.apps[ap];st.dirty=true;shell();if(st.apps[ap])toast('In Nastaliq this opens a secure sign-in with '+ap+'.')}
    else if(t.dataset.act==='mail'){toast('Weekly email set up (sample).')}
    else if(t.dataset.task){st.done[t.dataset.task]=!st.done[t.dataset.task];shell()}
    else if(t.dataset.act==='sale'){st.plus=false;shell();toast('In Nastaliq this opens a new sales order.')}
    else if(t.dataset.act==='po'){st.plus=false;st.view='purchasing';st.seen.purchasing=1;st.dirty=true;shell();toast('New purchase order started.')}
    else if(t.dataset.low){st.low=t.dataset.low==='1';shell()}
    else if(t.dataset.order){st.orders[t.dataset.order]=1;shell();toast('Purchase order created. See Purchasing.')}
    else if(t.dataset.approve){st.approved[t.dataset.approve]=1;shell();toast('Order approved.')}
    else if(t.dataset.hl!=null){st.sel={t:'hl',k:+t.dataset.hl};st.bell=false;shell()}
    else if(t.dataset.bell){st.bell=!st.bell;st.plus=false;shell()}
    else if(t.dataset.close){st.sel=null;shell()}
    else if(t.dataset.csv){csv()}
    else if(t.dataset.bar!=null){var i=+t.dataset.bar;if(t.dataset.w==='mix'){st.sel={t:'row',k:D2.mix[i][0]};shell()}}
    else if(t.dataset.row){st.sel={t:'row',k:t.dataset.row};shell()}
    else if(t.dataset.fin){st.sel={t:'fin',k:t.dataset.fin};shell()}
  });
  win.addEventListener('keydown',function(e){var t=e.target;if((e.key==='Enter'||e.key===' ')&&t.matches&&t.matches('tr[data-row],tr[data-fin]')){e.preventDefault();t.click()}if(e.key==='Escape'&&(st.sel||st.bell)){st.sel=null;st.bell=false;shell()}});
  win.addEventListener('input',function(e){if(e.target.id==='pv-me'){var v=e.target.value.slice(0,30);st.me=v.trim();e.target.size=Math.max(9,v.length+1);st.dirty=true;var fn=document.querySelector('#lead [name=name]');if(fn&&!fn.dataset.t)fn.value=st.me;return}if(e.target.id==='pv-host'){st.host=e.target.value.toLowerCase().replace(/[^a-z0-9.\-]/g,'');st.dirty=true;return}if(e.target.id==='pv-lang'){st.lang=e.target.value;st.dirty=true;shell();return}if(e.target.id==='pv-pre'){st.pre=e.target.value;st.dirty=true;return}if(e.target.id==='pv-q'){st.q=e.target.value;st._focusQ=1;var v=win.querySelector('.view'),d=cur();v.innerHTML=VF[st.view](d)}});
  win.addEventListener('mouseover',function(e){var h=e.target.closest('[data-pt]');if(!h)return;var d=cur(),i=+h.dataset.pt,s=d.trend[i],tip=$('pv-tip'),c=win.querySelector('.pt[data-i="'+i+'"]');if(!tip||!s||!c)return;
    win.querySelectorAll('.pt.on').forEach(function(x){x.classList.remove('on')});c.classList.add('on');var r=c.getBoundingClientRect(),p=tip.parentNode.getBoundingClientRect();tip.hidden=false;tip.textContent=s[0].replace(' (derived)','')+': '+money(s[1]);
    tip.style.left=Math.min(p.width-tip.offsetWidth-4,Math.max(4,r.left-p.left+r.width/2-tip.offsetWidth/2))+'px';tip.style.top=Math.max(0,r.top-p.top-38)+'px'});
  win.addEventListener('mouseout',function(e){if(e.target.closest('[data-pt]')){var t=$('pv-tip');if(t)t.hidden=true;win.querySelectorAll('.pt.on').forEach(function(x){x.classList.remove('on')})}});
  function csv(){var d=cur(),h,r;
    if(st.view==='reports'&&st.rep==='trend'){h='"Period","Amount ($M)"';r=d.trend.map(function(x){return'"'+x[0]+'",'+x[1]})}
    else if(st.view==='reports'&&st.rep==='fin'||st.view==='accounting'){h='"Line","This year ($M)","Last year ($M)"';r=d.fin.map(function(x){return'"'+x[0]+'",'+x[1]+','+(x[2]==null?'':x[2])})}
    else{h='"'+d.mixLabel+'","This period","Prior period"';r=d.mix.map(function(m){return'"'+m[0]+'",'+m[1]+','+(m[2]==null?'':m[2])})}
    var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([[h].concat(r).join('\n')],{type:'text/csv'}));a.download='sample-report.csv';document.body.appendChild(a);a.click();a.remove();toast('Exported sample-report.csv')}

  /* ---------- controls: name, industry, logo, colour ---------- */
  var ind=$('pv-ind'),nm=$('pv-name'),lg=$('pv-logo'),cs=$('pv-color'),er=$('pv-err'),sw=$('pv-sws'),chip=$('pv-chip');
  Object.keys(D).forEach(function(k){var o=document.createElement('option');o.textContent=k;ind.appendChild(o)});
  function swatches(){
    var h='';
    if(st.palette.length)h+='<span class="grp">From your logo</span>'+st.palette.map(function(c){return'<button type="button" class="sw" data-c="'+c+'" data-f="logo" aria-label="Use logo colour '+c+'" aria-pressed="'+(st.accent===c)+'" style="background:'+c+'"></button>'}).join('')+'<span class="grp">Presets</span>';
    h+=PRESETS.map(function(c){return'<button type="button" class="sw" data-c="'+c+'" data-f="preset" aria-label="Use colour '+c+'" aria-pressed="'+(st.accent===c)+'" style="background:'+c+'"></button>'}).join('');
    sw.innerHTML=h;
  }
  function setColor(h,from){if(/^#[0-9a-f]{6}$/i.test(h)){st.accent=h.toLowerCase();st.from=from||'custom';cs.value=st.accent;st.dirty=true;swatches();paint()}}
  sw.addEventListener('click',function(e){var b=e.target.closest('.sw');if(b)setColor(b.dataset.c,b.dataset.f)});
  cs.addEventListener('input',function(){setColor(cs.value,'custom')});
  nm.addEventListener('input',function(){st.name=nm.value.trim().slice(0,40);st.dirty=true;var m=win.querySelector('.brand b'),h=win.querySelector('.pvt h4'),l=win.querySelector('.brand .lo:not(.img)'),hi=$('pv-host');
    if(m){m.textContent=st.name||'Your Company';if(l)l.textContent=(st.name||'Y').charAt(0).toUpperCase();if(hi)hi.placeholder=slug()+'.com'}});
  ind.addEventListener('change',function(){st.ind=ind.value;st.chart='auto';st.sort=null;st.q='';st.sel=null;st.orders={};st.approved={};st.dirty=true;shell()});

  // Pull up to 4 distinct brand colours out of the logo: bucket pixels, drop near-white and transparent, favour saturated colours.
  function palette(img){
    var c=document.createElement('canvas'),s=64;c.width=c.height=s;var x=c.getContext('2d',{willReadFrequently:true});x.drawImage(img,0,0,s,s);
    var px=x.getImageData(0,0,s,s).data,b={},i,n=0;
    for(i=0;i<px.length;i+=4){if(px[i+3]<200)continue;var r=px[i],g=px[i+1],bl=px[i+2],mx=Math.max(r,g,bl),mn=Math.min(r,g,bl);if(mn>235)continue;n++;
      var k=(r>>4)+','+(g>>4)+','+(bl>>4),e=b[k]||(b[k]={r:0,g:0,b:0,n:0,sat:(mx-mn)/(mx||1)});e.r+=r;e.g+=g;e.b+=bl;e.n++}
    var L=Object.keys(b).map(function(k){var e=b[k];return{r:e.r/e.n,g:e.g/e.n,b:e.b/e.n,w:e.n*(.35+e.sat*1.65)}}).sort(function(a,z){return z.w-a.w}),out=[];
    L.forEach(function(p){if(out.length>=4||p.w<n*.01)return;if(out.every(function(o){return Math.abs(o.r-p.r)+Math.abs(o.g-p.g)+Math.abs(o.b-p.b)>110}))out.push(p)});
    return out.map(function(p){return'#'+[p.r,p.g,p.b].map(function(v){return('0'+Math.round(v).toString(16)).slice(-2)}).join('')});
  }
  function setLogo(f){
    er.textContent='';if(!f)return;
    if(!/^image\/(png|jpeg|webp)$/.test(f.type)){er.textContent='Use a PNG, JPG or WebP file.';return}
    if(f.size>3e6){er.textContent='That file is over 3 MB.';return}
    var u=URL.createObjectURL(f),im=new Image();
    im.onload=function(){ // re-draw at <=256px: small to send, and any odd file data is dropped
      var r=Math.min(1,256/Math.max(im.width,im.height)),c=document.createElement('canvas');
      c.width=Math.max(1,Math.round(im.width*r));c.height=Math.max(1,Math.round(im.height*r));
      c.getContext('2d').drawImage(im,0,0,c.width,c.height);URL.revokeObjectURL(u);
      st.logo=c.toDataURL('image/png');var l2=new Image();
      l2.onload=function(){st.palette=palette(l2);if(st.palette.length)st.accent=st.palette[0],st.from='logo';cs.value=st.accent;st.dirty=true;chip.hidden=false;$('pv-chip-img').src=st.logo;swatches();shell();
        if(!st.palette.length)er.textContent='No clear colour in that logo. Pick one below.'};
      l2.src=st.logo;
    };
    im.onerror=function(){URL.revokeObjectURL(u);er.textContent='We could not read that image.'};
    im.src=u;
  }
  lg.addEventListener('change',function(){setLogo(lg.files&&lg.files[0]);lg.value=''});
  $('pv-clear').addEventListener('click',function(){st.logo=null;st.palette=[];if(st.from==='logo')st.from='preset';chip.hidden=true;er.textContent='';swatches();shell()});
  ['dragover','dragenter'].forEach(function(t){root.addEventListener(t,function(e){if(e.dataTransfer&&Array.prototype.indexOf.call(e.dataTransfer.types,'Files')>-1){e.preventDefault();root.classList.add('drop')}})});
  ['dragleave','drop'].forEach(function(t){root.addEventListener(t,function(e){if(t==='dragleave'&&root.contains(e.relatedTarget))return;root.classList.remove('drop')})});
  root.addEventListener('drop',function(e){e.preventDefault();setLogo(e.dataTransfer.files&&e.dataTransfer.files[0])});

  // Reopen a shared preview: ?pv=<base64url {n,i,a}> (links in our lead emails). The logo is never in the link.
  try{
    var q=new URLSearchParams(location.search).get('pv');
    if(q){var j=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(q.replace(/-/g,'+').replace(/_/g,'/')),function(c){return c.charCodeAt(0)})));
      if(typeof j.n==='string'){st.name=j.n.slice(0,40);nm.value=st.name}
      if(D[j.i]){st.ind=j.i;ind.value=j.i}
      if(/^#[0-9a-f]{6}$/i.test(j.a)){st.accent=j.a.toLowerCase();st.from='custom';cs.value=st.accent}
      st.dirty=true}
  }catch(e){}
  swatches();shell();

  // What the demo form sends along. Only set once the visitor has touched the preview.
  window.nqPreview=function(){return st.dirty?{preview:{name:st.name,industry:st.ind,accent:st.accent,hasLogo:!!st.logo,colourFrom:st.from,me:st.me,lang:st.lang,theme:st.dark?'dark':'light',host:st.pre+'.'+(st.host||slug()+'.com'),views:Object.keys(st.seen)},logo:st.logo}:{}};
})();
