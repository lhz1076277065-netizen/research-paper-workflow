import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const out = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire('LOCAL_USER_ROOT/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/');
const { marked } = await import(require.resolve('marked'));
const { chromium } = require('playwright');
const body = marked.parse(fs.readFileSync(path.join(out, 'manuscript.md'), 'utf8'));
const html = `<!doctype html><html lang="en"><meta charset="utf-8"><title>Synthetic benchmark manuscript</title><style>
body{font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:40px auto;line-height:1.48;color:#18202a;font-size:15px}h1{font-size:28px;line-height:1.22}h2{font-size:21px;margin-top:30px}h3{font-size:17px}table{width:100%;border-collapse:collapse;margin:16px 0;font-size:13px}th,td{border:1px solid #ccd3da;padding:7px}th{text-align:left;background:#f0f3f6}img{width:100%;height:auto}code{white-space:normal;overflow-wrap:anywhere;font-size:12px}a{color:#176e9c}p{orphans:3;widows:3}h1,h2,h3{break-after:avoid}table,tr,img{break-inside:avoid}@page{size:A4;margin:18mm 17mm}@media print{body{max-width:none;margin:0;font-size:10.5pt;line-height:1.35}h1{font-size:18pt}h2{font-size:14pt}h3{font-size:11.5pt}table{font-size:9pt}th,td{padding:4px}a{color:inherit;text-decoration:none}}
</style><body>${body}</body></html>`;
fs.writeFileSync(path.join(out, 'manuscript.html'), html);
const options = {headless:true,viewport:{width:1100,height:900}};
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (fs.existsSync(chrome)) options.executablePath = chrome;
const context = await chromium.launchPersistentContext(path.join(out,'.browser-profile'), options);
const page = context.pages()[0] || await context.newPage();
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
await page.goto('file://' + path.join(out, 'manuscript.html'));
await page.waitForLoadState('load');
const checks = await page.evaluate(() => ({
  headings:[...document.querySelectorAll('h1,h2,h3')].map(e=>e.textContent),
  tables:document.querySelectorAll('table').length,
  tableRows:[...document.querySelectorAll('table')].map(t=>t.querySelectorAll('tbody tr').length),
  imageLoaded:[...document.images].every(e=>e.complete&&e.naturalWidth>0),
  horizontalOverflow:document.body.scrollWidth>innerWidth,
  textCharacters:document.body.innerText.length
}));
if(errors.length || !checks.imageLoaded || checks.horizontalOverflow || checks.tables!==2) throw new Error(JSON.stringify({checks,errors}));
await page.screenshot({path:path.join(out,'manuscript-preview.png'),fullPage:true});
await page.pdf({path:path.join(out,'manuscript.pdf'),printBackground:true,preferCSSPageSize:true});
await context.close();
fs.writeFileSync(path.join(out,'render-review.json'),JSON.stringify({...checks,pageErrors:errors,renderer:'Chromium via bundled Playwright'},null,2)+'\n');
console.log(JSON.stringify(checks));
