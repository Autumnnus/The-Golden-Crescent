/* Verify v2 mechanics survive a map edit and outdated reports are invalidated. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.TGC_CHROME?{executablePath:process.env.TGC_CHROME}:{})});
  const out=path.resolve('build/atlas-tests');await fs.mkdir(out,{recursive:true});
  try{
    const page=await browser.newPage({viewport:{width:1600,height:1050}}),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(pathToFileURL(path.resolve('build/maps/ve_subjects_regression.html')).href);
    await page.waitForFunction(()=>document.getElementById('loading').hidden);
    await page.locator('#search').fill('LOWER_EGYPT');await page.locator('.state-row').first().click();
    assert.match(await page.locator('#development').innerText(),/2\.500\.000 kişi/);
    assert.match(await page.locator('#development').innerText(),/%65/);
    await page.screenshot({path:path.join(out,'scenario-v2.png'),fullPage:true});
    const original=await page.locator('#atlas-data').textContent().then(JSON.parse);
    // v2 country and state mechanics-only patches preserve ownership.
    await page.locator('#owner').fill('TUR');await page.locator('#assign-province').click();
    assert.match(await page.locator('#development').innerText(),/Taslak değişti/);
    let pending=page.waitForEvent('download');await page.locator('#export').click();
    const download=await pending;await download.saveAs(path.join(out,'scenario-v2-edited.json'));
    const draft=JSON.parse(await fs.readFile(path.join(out,'scenario-v2-edited.json'),'utf8'));
    assert.equal(draft.version,2);
    assert.deepEqual(draft.countries,original.scenario.countries);
    assert.deepEqual(draft.subject_types,original.scenario.subject_types);
    assert.deepEqual(draft.diplomacy,original.scenario.diplomacy);
    assert.deepEqual(draft.states.STATE_LOWER_EGYPT.population,original.scenario.states.STATE_LOWER_EGYPT.population);
    assert.deepEqual(draft.states.STATE_LOWER_EGYPT.industry,original.scenario.states.STATE_LOWER_EGYPT.industry);
    pending=page.waitForEvent('download');await page.locator('#context').click();
    await (await pending).saveAs(path.join(out,'scenario-v2-context.json'));
    assert.equal(JSON.parse(await fs.readFile(path.join(out,'scenario-v2-context.json'),'utf8')).development,null);
    await page.locator('#undo').click();
    assert.match(await page.locator('#development').innerText(),/2\.500\.000 kişi/);
    await page.locator('#file').setInputFiles({name:'v2.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(original.scenario))});
    await page.waitForFunction(()=>document.getElementById('status').textContent.includes('Senaryo yüklendi'));
    assert.match(await page.locator('#ownership').innerText(),/EGY/);
    assert.deepEqual(errors,[]);
    console.log('PASS: v2 report panel, exact population, country/state mechanics and custom diplomacy round-trip, report invalidation, undo, import');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
