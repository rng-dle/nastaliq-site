import subprocess,time
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8765','-d','public'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox']);errs=[]
    pg=b.new_page(viewport={'width':1512,'height':852});pg.on('pageerror',lambda e:errs.append(str(e)));pg.route('**/fonts.g*/**',lambda r:r.abort())
    pg.goto('http://localhost:8765/');pg.wait_for_timeout(600);pg.fill('#pv-name','Zed Supply Co');pg.evaluate('nqReveal()');pg.wait_for_timeout(1600);pg.fill('#pv-me','Sam')
    pg.evaluate("document.getElementById('preview').scrollIntoView({block:'start'})");pg.wait_for_timeout(500)
    print('home scroll?',pg.evaluate("(m=>[m.scrollHeight,m.clientHeight])(document.querySelector('#pv-win main'))"))
    pg.locator('#preview').screenshot(path='/tmp/h_home.png')
    pg.click('[data-theme]');pg.click('[data-bell]');pg.wait_for_timeout(300);pg.locator('#preview').screenshot(path='/tmp/h_dark_bell.png');pg.click('[data-bell]')
    for tab in ['overview','breakdown','trend','fin']:
        pg.click('[data-view=reports]');pg.click(f'[data-rep={tab}]');pg.wait_for_timeout(900);pg.locator('#pv-win').screenshot(path=f'/tmp/h_rep_{tab}.png')
    pg.click('[data-view=integrations]');pg.click('[data-app=Gmail]');pg.click('[data-app=Slack]');pg.locator('#pv-win').screenshot(path='/tmp/h_int.png')
    langs=pg.eval_on_selector_all('#pv-lang option','o=>o.map(x=>x.value)')
    for l in langs:
        pg.select_option('#pv-lang',l);pg.click('[data-view=home]')
        if l in('ar','ja','de','ur'):pg.locator('#pv-win').screenshot(path=f'/tmp/h_{l}.png')
    print('langs',len(langs),'last nav:',pg.inner_text('aside li >> nth=0'))
    pg.select_option('#pv-lang','en');pg.click('[data-theme]');pg.click('[data-view=reports]');pg.click('[data-csv]')if False else None
    print('errors',errs);b.close()
finally: srv.terminate()
