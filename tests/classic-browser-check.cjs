const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
  const browser = await chromium.launch({headless:true, channel:process.env.BROWSER_CHANNEL || (process.platform === 'win32' ? 'msedge' : undefined), args:['--enable-webgl','--ignore-gpu-blocklist']});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    const errors=[]; page.on('pageerror', e=>errors.push(e.message));
    await page.goto(process.env.DRONEVERSE_URL || 'http://127.0.0.1:5173', {waitUntil:'domcontentloaded'});
    async function select(value) {
      await page.locator('#settings').click();
      await page.locator('#location').selectOption(value);
      await page.locator('#settings-dialog .button.close-dialog').click();
    }
    await select('4');
    await page.locator('#world.classic-scenery canvas[aria-label="Interactive 3D drone flight environment"]').waitFor();
    await page.waitForFunction(()=>!document.getElementById('launch').disabled);
    assert.match(await page.locator('#map-status').textContent(), /Classic airfield ready/);
    fs.mkdirSync('tests/artifacts',{recursive:true});
    await page.screenshot({path:'tests/artifacts/classic.png',fullPage:true});
    await page.locator('#launch').click();
    await page.keyboard.down('Space'); await page.waitForTimeout(1200); await page.keyboard.up('Space');
    assert.ok(Number(await page.locator('#altitude').textContent()) > 3);
    await page.keyboard.down('w'); await page.waitForTimeout(700); await page.keyboard.up('w');
    assert.ok(Number(await page.locator('#speed').textContent()) > 3);
    for (const mode of ['FPV','Orbit','Chase']) await page.locator(`[data-camera="${mode}"]`).click();
    await page.locator('#settings').click(); await page.locator('#night').check(); await page.locator('#settings-dialog .button.close-dialog').click();
    await page.setViewportSize({width:1000,height:800});
    await page.screenshot({path:'tests/artifacts/classic-night.png'});
    await select('0');
    await page.waitForFunction(()=>document.querySelector('#map-status').textContent.includes('Textured 3D capture ready'), null, {timeout:60000});
    assert.equal(await page.locator('.classic-world').count(),0);
    assert.equal(await page.locator('#world .maplibregl-canvas').isVisible(),true);
    await select('4');
    assert.equal(await page.locator('.classic-world canvas').count(),1);
    assert.equal(await page.locator('.classic-minimap').count(),1);
    assert.match(await page.locator('#map-coords').textContent(), /X .* m/);
    assert.deepEqual(errors,[]);
    console.log('PASS: classic scene, keyboard flight, cameras, blue hour, resize, real map return, repeated switching');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});

