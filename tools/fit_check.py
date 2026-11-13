import subprocess,time,sys
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8765','-d','public'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
S=[('mbp16-default',1728,1117-130),('mbp16-scaled-more',1512,982-130),('mbp14',1512,982-130),('laptop',1440,800),('small-laptop',1280,720),('fhd',1920,1080-120),('ipad',820,1180),('phone',390,844),('small-phone',360,640)]
bad=0
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for n,w,h in S:
      pg=b.new_page(viewport={'width':w,'height':h});pg.route('**/fonts.g*/**',lambda r:r.abort())
      pg.goto('http://localhost:8765/');pg.wait_for_timeout(500);pg.fill('#pv-name','Zed Supply Co')
      pg.evaluate("document.getElementById('preview').scrollIntoView({block:'center'})");pg.wait_for_timeout(500)
      r=pg.evaluate("""()=>{var s=document.getElementById('preview').getBoundingClientRect(),w=document.getElementById('pv-win').getBoundingClientRect(),m=document.querySelector('#pv-win main'),d=document.documentElement;return{stage:Math.round(s.height),win:Math.round(w.height),vh:innerHeight,hscroll:d.scrollWidth>d.clientWidth,inner:m?m.scrollHeight>m.clientHeight:null}}""")
      desk=w>900;ok=(not r['hscroll']) and (r['stage']<=r['vh']+2 if desk and h>=700 else True)
      bad+=0 if ok else 1
      print(('OK ' if ok else 'BAD'),n,w,h,r);pg.screenshot(path=f'/tmp/fit_{n}.png');pg.close()
    b.close()
finally: srv.terminate()
print('bad',bad)
