import subprocess,time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8765','-d','public'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for n,w,h in [('desk',1512,852),('phone',390,844)]:
      pg=b.new_page(viewport={'width':w,'height':h});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.route('**/fonts.g*/**',lambda r:r.abort())
      pg.goto('http://localhost:8765/');pg.wait_for_timeout(600);pg.evaluate("document.getElementById('preview').scrollIntoView()");pg.wait_for_timeout(400);pg.screenshot(path=f'/tmp/fog0_{n}.png');pg.fill('#pv-name','Zed Supply Co');pg.wait_for_timeout(300);pg.screenshot(path=f'/tmp/fog1_{n}.png')
      pg.click('#pv-go');pg.wait_for_timeout(300);steps=0;bad=[]
      while pg.is_visible('.tr-pop'):
        pg.wait_for_timeout(500)
        r=pg.evaluate("(()=>{var p=document.querySelector('.tr-pop').getBoundingClientRect(),h=document.querySelector('.tr-hole').getBoundingClientRect();return{pt:p.top,pb:p.bottom,pl:p.left,pr:p.right,hw:h.width,hh:h.height,t:document.querySelector('.tr-pop h4').textContent,vw:innerWidth,vh:innerHeight}})()")
        steps+=1
        if r['pt']<-1 or r['pb']>r['vh']+1 or r['pl']<-1 or r['pr']>r['vw']+1 or r['hw']<20: bad.append(r)
        if steps in(3,8,15):pg.screenshot(path=f'/tmp/tour_{n}_{steps}.png')
        pg.click('.tr-pop .tr-go');pg.wait_for_timeout(120)
        if steps>20:break
      print(n,'steps',steps,'bad',len(bad),bad[:2],'errors',errs);pg.close()
    b.close()
finally: srv.terminate()
