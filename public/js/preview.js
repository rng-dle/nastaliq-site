// "The fix" live preview: a mini dashboard the visitor can brand, and the hook that sends it with the demo form.
(function(){
  var root=document.getElementById('preview');
  if(!root)return;
  var $=function(id){return document.getElementById(id)};
  var D={ // sample data per industry: 4 KPIs, 12 weekly values, a table and three alerts
    Distribution:{k:[['Sales this week','$118,420','+7.1%',1],['Open purchase orders','23','4 due today',0],['Stock value','$1.32M','+2.4%',1],['Overdue bills','$14,870','6 bills',0]],c:'Weekly sales',s:[71,76,69,82,88,84,91,87,96,93,102,118],t:'Top customers',h:['Customer','Orders','Revenue'],r:[['Harbour Foods','41','$22,904'],['Dunmore Hardware','33','$18,371'],['Pinecrest Supply','27','$15,126'],['Alder &amp; Pike','19','$9,458']],a:[['Low stock','Pallet wrap 18in: 14 left'],['Due today','PO 1187 from Northline Packaging'],['Overdue','Bill 3320 is 9 days late']]},
    Retail:{k:[['Sales today','$6,284','+5.3%',1],['Transactions','231','+18',1],['Low stock items','17','5 at zero',0],['Gross margin','38.4%','+0.7 pt',1]],c:'Daily sales',s:[41,44,39,52,61,68,57,46,48,43,55,63],t:'Best sellers this week',h:['Item','Sold','Revenue'],r:[['Canvas tote, natural','86','$1,634'],['Stoneware mug, 12oz','74','$1,258'],['Beeswax candle','61','$1,037'],['Linen apron','38','$1,102']],a:[['Low stock','Stoneware mug: 9 left'],['Reorder','Candle wicks from Calder &amp; Rye'],['Count due','Aisle 3 cycle count tomorrow']]},
    Janitorial:{k:[['Jobs done today','47','of 52',1],['Hours on the clock','188','+6 vs plan',0],['Inspection score','94%','+2 pt',1],['Supplies on hand','11 days','2 low',0]],c:'Jobs per day',s:[39,42,45,41,48,47,22,40,44,46,49,47],t:'Sites this week',h:['Client site','Visits','Score'],r:[['Westbrook Medical','12','96%'],['Maple Court Offices','10','93%'],['Oakridge School','9','91%'],['Lakeshore Dental','6','98%']],a:[['Missed','Maple Court, 3rd floor: no check-in'],['Low supplies','Floor cleaner: 2 cases left'],['Client message','Oakridge asks for a deep clean Friday']]},
    Manufacturing:{k:[['Units built today','412','+31',1],['Open work orders','19','3 late',0],['Raw material cover','23 days','-2 days',0],['Scrap rate','1.8%','-0.3 pt',1]],c:'Units per day',s:[352,368,341,390,402,377,120,388,396,409,381,412],t:'Active work orders',h:['Order','Item','Due'],r:[['WO-2041','Bracket assembly','Nov 16'],['WO-2044','Housing, black','Nov 17'],['WO-2046','Gasket kit','Nov 19'],['WO-2049','Control panel','Nov 22']],a:[['Short','Steel sheet 2mm: 9 days of cover'],['Late','WO-2038 waits on powder coat'],['Quality','Batch 77 scrap above target']]},
    'Food and beverage':{k:[['Sales today','$4,912','+8.6%',1],['Covers','318','+24',1],['Food cost','29.7%','-0.9 pt',1],['Waste this week','$412','+$58',0]],c:'Daily sales',s:[3.1,3.4,3.3,3.9,4.8,5.6,4.4,3.2,3.6,3.5,4.2,4.9],t:'Top sellers',h:['Item','Sold','Revenue'],r:[['Sourdough loaf','142','$923'],['Cold brew, 16oz','118','$590'],['Butter croissant','96','$336'],['Breakfast sandwich','71','$639']],a:[['Low stock','Oat milk: 6 cartons left'],['Expiring','Cream cheese, 3 tubs, 2 days'],['Order','Flour due from Millstone tomorrow']]},
    Construction:{k:[['Active jobs','8','2 over budget',0],['Billed this month','$231,400','+12%',1],['Open change orders','5','$18,900',0],['Unpaid by clients','$87,250','4 invoices',0]],c:'Billed per week',s:[41,52,48,57,61,55,64,59,70,66,72,78],t:'Jobs',h:['Job','Budget used','Status'],r:[['Elm Street duplex','72%','On track'],['Rivergate retail fit-out','94%','Over'],['Hillcrest garage','41%','On track'],['Marlow clinic','88%','Watch']],a:[['Over budget','Rivergate: materials +$6,300'],['Approval','Change order 14 awaits client'],['Overdue','Invoice 2209, 21 days']]},
    'Professional services':{k:[['Billable hours','612','+4.8%',1],['Utilisation','78%','+3 pt',1],['Unbilled work','$21,640','9 days old',0],['Invoices overdue','$12,300','3 clients',0]],c:'Billable hours per week',s:[480,512,498,541,560,534,572,590,566,601,598,612],t:'Projects',h:['Client','Hours','Billed'],r:[['Northwind Legal','94','$14,100'],['Bluepeak Capital','71','$10,650'],['Ardent Health','63','$9,450'],['Kestrel Labs','48','$7,200']],a:[['Unbilled','Ardent Health: 31 hours not invoiced'],['Overdue','Bluepeak invoice, 14 days'],['Capacity','2 consultants under 60% next week']]},
    Ecommerce:{k:[['Orders today','186','+11%',1],['Revenue today','$9,730','+9.4%',1],['Awaiting shipment','42','7 over 2 days',0],['Return rate','3.9%','-0.4 pt',1]],c:'Orders per day',s:[121,134,128,149,162,171,158,140,152,167,174,186],t:'Top products',h:['Product','Orders','Revenue'],r:[['Merino beanie','64','$1,792'],['Insulated bottle','52','$1,508'],['Wool socks, 3 pack','47','$1,175'],['Trail pack, 20L','21','$1,869']],a:[['Low stock','Insulated bottle: 22 left'],['Late','7 orders waiting over 2 days'],['Sync','Store and stock matched 4 min ago']]}
  };
  var st={name:'',ind:'Distribution',accent:'#ffc23a',logo:null,dirty:false};
  var ind=$('pv-ind'),nm=$('pv-name'),lg=$('pv-logo'),cs=$('pv-color'),er=$('pv-err');
  Object.keys(D).forEach(function(k){var o=document.createElement('option');o.textContent=k;ind.appendChild(o)});
  function lum(h){var n=parseInt(h.slice(1),16),c=[n>>16&255,n>>8&255,n&255].map(function(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]}
  function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
  function render(){
    var d=D[st.ind],a=st.accent,on=lum(a)>.4?'#1a1200':'#fff',name=st.name||'Your Company',win=$('pv-win');
    win.style.setProperty('--ac',a);win.style.setProperty('--on-ac',on);
    var lo=$('pv-lo');lo.textContent='';
    if(st.logo){var im=new Image();im.src=st.logo;im.alt='';lo.appendChild(im);lo.classList.add('img')}else{lo.textContent=name.charAt(0).toUpperCase();lo.classList.remove('img')}
    $('pv-nm').textContent=name;$('pv-hi').textContent='Good morning, '+(st.name||'team');
    var kp=$('pv-kpis');kp.textContent='';
    d.k.forEach(function(k){var c=el('div','pk');c.appendChild(el('span','',k[0]));c.appendChild(el('b','',k[1]));c.appendChild(el('i',k[3]?'up':'dn',k[2]));kp.appendChild(c)});
    var mx=Math.max.apply(null,d.s),ch=$('pv-bars');ch.textContent='';
    d.s.forEach(function(v,i){var b=el('em');b.style.height=Math.max(8,Math.round(v/mx*100))+'%';if(i===d.s.length-1)b.className='now';ch.appendChild(b)});
    $('pv-ct').textContent=d.c;
    $('pv-tt').textContent=d.t;
    var tb=$('pv-tb');tb.textContent='';
    var hr=el('tr');d.h.forEach(function(h){hr.appendChild(el('th','',h))});tb.appendChild(hr);
    d.r.forEach(function(r){var tr=el('tr');r.forEach(function(c){var td=el('td');td.innerHTML=c;tr.appendChild(td)});tb.appendChild(tr)});
    var al=$('pv-al');al.textContent='';
    d.a.forEach(function(x){var li=el('li');li.appendChild(el('b','',x[0]));var s=el('span');s.innerHTML=x[1];li.appendChild(s);al.appendChild(li)});
  }
  function touch(){st.dirty=true;render()}
  nm.addEventListener('input',function(){st.name=nm.value.trim().slice(0,40);touch()});
  ind.addEventListener('change',function(){st.ind=ind.value;touch()});
  function setColor(h){if(/^#[0-9a-f]{6}$/i.test(h)){st.accent=h.toLowerCase();cs.value=st.accent;root.querySelectorAll('.sw').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.c===st.accent)});touch()}}
  root.querySelectorAll('.sw').forEach(function(b){b.style.background=b.dataset.c;b.addEventListener('click',function(){setColor(b.dataset.c)})});
  cs.addEventListener('input',function(){setColor(cs.value)});
  lg.addEventListener('change',function(){
    er.textContent='';var f=lg.files&&lg.files[0];if(!f)return;
    if(!/^image\/(png|jpeg|webp)$/.test(f.type)){er.textContent='Use a PNG, JPG or WebP file.';lg.value='';return}
    if(f.size>3e6){er.textContent='That file is over 3 MB.';lg.value='';return}
    var u=URL.createObjectURL(f),im=new Image();
    im.onload=function(){ // re-draw at <=256px: small to send, and any odd file data is dropped
      var r=Math.min(1,256/Math.max(im.width,im.height)),c=document.createElement('canvas');
      c.width=Math.max(1,Math.round(im.width*r));c.height=Math.max(1,Math.round(im.height*r));
      c.getContext('2d').drawImage(im,0,0,c.width,c.height);URL.revokeObjectURL(u);
      st.logo=c.toDataURL('image/png');touch();
    };
    im.onerror=function(){URL.revokeObjectURL(u);er.textContent='We could not read that image.';lg.value=''};
    im.src=u;
  });
  $('pv-clear').addEventListener('click',function(){st.logo=null;lg.value='';er.textContent='';touch()});
  // Reopen a shared preview: ?pv=<base64url {n,i,a}> (links in our lead emails). The logo is never in the link.
  try{
    var q=new URLSearchParams(location.search).get('pv');
    if(q){var j=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(q.replace(/-/g,'+').replace(/_/g,'/')),function(c){return c.charCodeAt(0)})));
      if(typeof j.n==='string'){st.name=j.n.slice(0,40);nm.value=st.name}
      if(D[j.i]){st.ind=j.i;ind.value=j.i}
      if(/^#[0-9a-f]{6}$/i.test(j.a)){st.accent=j.a;cs.value=j.a}
      st.dirty=true;root.querySelectorAll('.sw').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.c===st.accent)})}
  }catch(e){}
  render();
  // What the demo form sends along. Only set once the visitor has touched the preview.
  window.nqPreview=function(){return st.dirty?{preview:{name:st.name,industry:st.ind,accent:st.accent,hasLogo:!!st.logo},logo:st.logo}:{}};
  window.nqPreviewName=function(){return st.name};
})();
