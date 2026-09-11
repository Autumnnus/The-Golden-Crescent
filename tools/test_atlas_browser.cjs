/* Integration test against the real generated demo atlas.
 * Generate: .venv/bin/python tools/tgc.py atlas --region 08_middle_east
 *   --scenario tools/examples/ve_atlas_scenario.yml --out build/maps/ve_demo.html
 * Requires Playwright; set TGC_CHROME to an existing Chrome executable if needed.
 * NODE_PATH may point at a separate development install of Playwright.
 */
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

(async () => {
  const output = path.resolve("build/atlas-tests");
  await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.TGC_CHROME ? { executablePath: process.env.TGC_CHROME } : {}),
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
    const errors = [], network = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("request", (request) => {
      if (/^https?:/.test(request.url())) network.push(request.url());
    });
    await page.goto(pathToFileURL(path.resolve(process.argv[2] || "build/maps/ve_demo.html")).href);
    await page.waitForFunction(() => document.getElementById("loading").hidden);
    await page.screenshot({ path: path.join(output, "desktop.png"), fullPage: true });
    assert.match(await page.locator("#change-count").innerText(), /1 eyalet/);
    await page.locator("#search").fill("x895074");
    await page.locator(".state-row").first().click();
    assert.equal(await page.locator("#state-id").innerText(), "STATE_ERZURUM");
    assert.match(await page.locator("#province option:checked").innerText(), /x895074/);
    await page.locator("#owner").fill("PER");
    await page.locator("#assign-province").click();
    assert.match(await page.locator("#province-info").innerText(), /Şimdi: PER/);
    assert.match(await page.locator("#ownership").innerText(), /ZZT/);
    await page.locator("#undo").click();
    assert.match(await page.locator("#province-info").innerText(), /Şimdi: ZZT/);
    await page.locator("#assign-state").click();
    assert.match(await page.locator("#ownership").innerText(), /PER\n27 il/);
    await page.locator("#undo").click();
    await page.locator("#redo").click();
    assert.match(await page.locator("#ownership").innerText(), /PER\n27 il/);
    for (const mode of ["reference", "religion", "phase", "changes", "political"]) {
      await page.locator("#mode").selectOption(mode);
      assert.ok((await page.locator("#legend").innerText()).length > 0);
    }
    await page.locator("#compare").fill("50");
    await page.waitForFunction(() => document.getElementById("compare-value").textContent === "%50 önce");
    await page.screenshot({ path: path.join(output, "compare.png"), fullPage: true });
    for (const [button, name] of [["export", "exported.json"], ["context", "context.json"], ["png", "browser-map.png"]]) {
      const pending = page.waitForEvent("download");
      await page.locator("#" + button).click();
      await (await pending).saveAs(path.join(output, name));
    }
    const exported = JSON.parse(await fs.readFile(path.join(output, "exported.json")));
    assert.equal(exported.states.STATE_ERZURUM.owner, "PER");
    assert.ok(!("split" in exported.states.STATE_ERZURUM));
    const context = JSON.parse(await fs.readFile(path.join(output, "context.json")));
    assert.equal(context.states.find(s => s.id === "STATE_ERZURUM").owners[0].tag, "PER");
    assert.ok(!context.hitImage && !context.catalog_states && !context.base_countries);
    for (const [source, expected] of [
      ['{"version":1,"states":{"WRONG":"TUR"}}', "kapsamı dışında"],
      ['{"version":1,"states":{"STATE_ERZURUM":"TUR","STATE_ERZURUM":"PER"}}', "Tekrarlanan"],
      ['{"version":1,"states":{"STATE_ERZURUM":{"split":[{"owner":"TUR","provinces":["x895074"]}]}}}', "sahipsiz il"],
      ['{"version":1,"countries":{"ZZZ":{"color":[999,0,0]}}}', "color"],
    ]) {
      await page.locator("#file").setInputFiles({ name: "bad.json", mimeType: "application/json", buffer: Buffer.from(source) });
      await page.waitForFunction(text => document.getElementById("status").textContent.includes(text), expected);
      assert.match(await page.locator("#ownership").innerText(), /PER\n27 il/);
    }
    await page.locator("#file").setInputFiles(path.join(output, "exported.json"));
    await page.waitForFunction(() => document.getElementById("status").textContent.includes("Senaryo yüklendi"));
    await page.locator("#reset").click();
    await page.reload();
    await page.waitForFunction(() => document.getElementById("loading").hidden);
    assert.match(await page.locator("#change-count").innerText(), /1 eyalet/);
    // HTML names are text, never executable markup.
    await page.locator("#scenario-title").fill('<img src=x onerror="window.INJECTED=1">');
    await page.locator("#scenario-title").press("Tab");
    assert.equal(await page.locator("#title img").count(), 0);
    assert.equal(await page.evaluate(() => window.INJECTED), undefined);
    await page.locator("#undo").click();
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: path.join(output, "mobile.png"), fullPage: true });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    assert.deepEqual(network, [], "The standalone atlas must not use a network service");
    assert.deepEqual(errors, []);
    console.log("PASS: province/state editing, undo/redo, all modes, comparison, JSON/PNG exports, import validation, persistence, text safety, mobile layout, offline operation");
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
