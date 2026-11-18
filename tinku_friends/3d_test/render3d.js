// node render3d.js t0 t1 out.mp4  — drives the page frame by frame and pipes PNGs into ffmpeg
const { chromium } = require('playwright'); const { spawn } = require('child_process');
(async () => {
  const [t0, t1, out] = [parseFloat(process.argv[2]), parseFloat(process.argv[3]), process.argv[4]];
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  p.on('console', m => console.log('page:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('http://127.0.0.1:8765/index.html'); await p.waitForFunction('window.READY === true', null, { timeout: 60000 });
  await p.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round((t1 - t0) * 30); const st = Date.now();
  for (let f = 0; f < n; f++) {
    await p.evaluate(t => window.renderAt(t), t0 + f / 30);
    const buf = await p.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`frame ${f}/${n} ${((Date.now() - st) / (f + 1)).toFixed(0)} ms/f`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
