const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('console', m => console.log('page:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('http://127.0.0.1:8765/index.html'); await p.waitForFunction('window.READY === true', null, { timeout: 60000 });
  await p.evaluate(() => document.fonts.ready);
  for (const t of process.argv.slice(2)) { const s = Date.now(); await p.evaluate(t => window.renderAt(t), parseFloat(t)); await p.screenshot({ path: `still_${t}.png` }); console.log(t, Date.now() - s, 'ms'); }
  await b.close();
})();
