const { chromium } = require('playwright');
const assert = require('node:assert/strict');
require('node:fs').mkdirSync('tests/artifacts', {recursive:true});
(async () => {
 const browser = await chromium.launch({headless:true, ...(process.env.BROWSER_CHANNEL ? {channel:process.env.BROWSER_CHANNEL} : {}), args:['--enable-webgl','--ignore-gpu-blocklist']});
 try {
 const page = await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true});
 const errors=[]; let capturedTiles=0, mapTiles=0; page.on('pageerror',e=>errors.push(e.message)); page.on('response',r=>{if(r.ok() && r.url().includes('.b3dm'))capturedTiles++;if(r.ok() && r.url().includes('.pbf'))mapTiles++;});
 await page.goto(process.env.DRONEVERSE_URL || 'http://127.0.0.1:5173', {waitUntil:'domcontentloaded'});
 await page.locator('#map-status[data-ready=true]').waitFor({timeout:60000}); await page.waitForFunction(()=>!document.getElementById('launch').disabled); await page.waitForTimeout(1500);
 assert.equal(await page.locator('#world-error').isVisible(),false);
 assert.match(await page.locator('#map-status').textContent(), /Textured 3D capture ready/); await page.screenshot({path:'tests/artifacts/desktop.png',fullPage:true});
 await page.locator('#record').click(); await page.locator('#launch').click();
 await page.keyboard.down('Space'); await page.waitForTimeout(1200); await page.keyboard.up('Space');
 assert.ok(Number(await page.locator('#altitude').textContent()) > 3, 'takeoff and climb');
 await page.keyboard.down('w'); await page.waitForTimeout(1000); await page.keyboard.up('w');
 assert.ok(Number(await page.locator('#speed').textContent()) > 5, 'forward keyboard flight'); await page.screenshot({path:'tests/artifacts/chase.png',fullPage:true});
 await page.keyboard.press('p'); const frozen = await page.locator('#altitude').textContent();
 await page.waitForTimeout(400); assert.equal(await page.locator('#altitude').textContent(),frozen);
 assert.equal(await page.locator('#pause-overlay').isVisible(),true); await page.locator('#resume').click();
 await page.locator('[data-camera="FPV"]').click(); assert.match(await page.locator('[data-camera="FPV"]').getAttribute('class'), /active/);
 await page.locator('[data-camera="Orbit"]').click(); await page.locator('[data-camera="Chase"]').click();
 await page.locator('#settings').click(); await page.locator('#night').check(); await page.locator('#trail').uncheck(); await page.locator('#wind').fill('5');
 await page.locator('#settings-dialog .close-dialog').first().click(); assert.equal(await page.locator('#time-label').textContent(),'Blue hour');
 await page.locator('#record').click(); await page.locator('#nav-log').click(); assert.equal(await page.locator('#export').isEnabled(),true);
 const [download] = await Promise.all([page.waitForEvent('download'),page.locator('#export').click()]);
 assert.equal(download.suggestedFilename(),'droneverse-flight.csv');
 await page.locator('#log-dialog .close-dialog').click();
 await page.locator('#reset').click(); assert.equal(await page.locator('#altitude').textContent(),'0.0');
 await page.locator('#launch').click(); await page.waitForTimeout(1300); await page.locator('#land').click();
 await page.waitForFunction(()=>document.getElementById('aircraft-status').textContent === 'Ready',null,{timeout:8000});
 const [shot] = await Promise.all([page.waitForEvent('download'),page.locator('#screenshot').click()]); assert.match(shot.suggestedFilename(),/^droneverse-.*\.png$/);
 await page.locator('#settings').click(); await page.locator('#night').uncheck(); await page.locator('#settings-dialog .close-dialog').first().click(); await page.locator('#reset').click();
 await page.setViewportSize({width:390,height:844}); await page.screenshot({path:'tests/artifacts/mobile.png',fullPage:true});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth > innerWidth),false,'no mobile horizontal overflow');
 console.log(JSON.stringify({passed:['WebGL scene','takeoff','keyboard climb','keyboard forward','pause','resume','FPV / Orbit / Chase','environment controls','recording','CSV download','reset','landing','screenshot download','mobile layout'],errors}));
 assert.ok(capturedTiles>0,'real 3D capture tiles fetched'); assert.ok(mapTiles>0,'geographic map tiles decoded'); assert.deepEqual(errors,[]);
 } finally { await browser.close(); }
})();

