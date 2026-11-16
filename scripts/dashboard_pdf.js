// Print the dashboard for given dates to A4 PDFs that look like the page: node scripts/dashboard_pdf.js <repo root> D [D ...]
// Writes exports/Punjab_press_dashboard_D.pdf. Run after build.py. The All stories table is expanded so every row prints.
const { chromium } = require('playwright');
(async () => {
  const [,, root, ...dates] = process.argv;
  const b = await chromium.launch();
  for (const d of dates) {
    const p = await b.newPage({ viewport: { width: 1200, height: 900 }, colorScheme: 'light' });
    await p.goto(`file://${root}/index.html#d=${d}`); await p.waitForTimeout(1800);
    await p.emulateMedia({ media: 'screen', colorScheme: 'light' });
    await p.addStyleTag({ content: '.pp-scroll{max-height:none!important;overflow:visible!important} .pp-card,.pp-sec-head,tr{break-inside:avoid}' });
    await p.pdf({ path: `${root}/exports/Punjab_press_dashboard_${d}.pdf`, format: 'A4', printBackground: true, scale: 0.62,
      margin: { top: '10mm', bottom: '10mm', left: '8mm', right: '8mm' } });
    console.log('wrote', d);
    await p.close();
  }
  await b.close();
})();
