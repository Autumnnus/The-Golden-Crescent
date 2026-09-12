/* Offline review integration. The approval downloaded here is a synthetic test receipt. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs/promises');
const {pathToFileURL}=require('node:url');
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.TGC_CHROME?{executablePath:process.env.TGC_CHROME}:{})});
  const output=path.resolve('build/flavor-tests/browser');await fs.mkdir(output,{recursive:true});
  try{
    const page=await browser.newPage({viewport:{width:1600,height:1050}}),errors=[],requests=[];
    page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
    await page.goto(pathToFileURL(path.resolve('build/flavor/ve_academy_demo/review/index.html')).href);
    await page.waitForSelector('.node');assert.equal(await page.locator('.node').count(),5);
    assert.match(await page.locator('.scene-title').innerText(),/kütüphaneden/);
    await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
    await page.locator('[data-option="support"]').click();
    await page.locator('.route').click();assert.match(await page.locator('.scene-title').innerText(),/Her çocuk/);
    await page.locator('[data-outcome="on_complete"]').click();await page.locator('.route').click();
    assert.match(await page.locator('.scene-title').innerText(),/İlk ders/);assert.equal(await page.locator('#trail li').count(),2);
    await page.locator('#language').selectOption('en');assert.match(await page.locator('.scene-title').innerText(),/Morning/);
    await page.locator('#reset-walk').click();assert.equal(await page.locator('#trail li').count(),0);
    await page.locator('#review-open').click();assert.equal(await page.locator('#approve').isDisabled(),true);
    await page.locator('#confirm').check();await page.locator('#review-note').fill('AUTOMATED TEST ONLY; not user approval');
    const pending=page.waitForEvent('download');await page.locator('#approve').click();
    await (await pending).saveAs(path.join(output,'synthetic-test-approval.json'));
    const approval=JSON.parse(await fs.readFile(path.join(output,'synthetic-test-approval.json'),'utf8'));
    const data=JSON.parse(await page.locator('#flavor-data').textContent());
    assert.equal(approval.fingerprint,data.fingerprint);assert.equal(approval.approved,true);
    await page.keyboard.press('Escape');assert.equal(await page.locator('#review').isVisible(),false);
    await page.setViewportSize({width:390,height:844});await page.locator('#fit').click();
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
    assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
    console.log('PASS: offline diagram, choice → journal → outcome walkthrough, translation, guarded approval download, dialog keyboard, mobile layout, no browser errors/network');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
