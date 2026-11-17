// Рендер всех SVG набора в PNG для галереи/превью.
// Запуск: node tools/render_all.js <manifest.json> <outDir> <scale>
const { Resvg } = require(process.env.RESVG || '/tmp/svgtool/node_modules/@resvg/resvg-js');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outDir = process.argv[3];
const scale = parseFloat(process.argv[4] || '2');
fs.mkdirSync(outDir, { recursive: true });

function render(src, dst, bg = 'rgba(0,0,0,0)') {
  const svg = fs.readFileSync(path.join(root, 'assets', src), 'utf8');
  const r = new Resvg(svg, { fitTo: { mode: 'zoom', value: scale }, background: bg });
  fs.writeFileSync(dst, r.render().asPng());
}

const made = [];
for (const b of manifest.backdrops) {
  const dst = path.join(outDir, `backdrop-${b.slug}.png`);
  render(b.file, dst, '#101018');
  made.push(dst);
}
for (const s of manifest.sprites) {
  s.costumes.forEach((c, i) => {
    const dst = path.join(outDir, `sprite-${s.slug}-${String(i + 1).padStart(2, '0')}.png`);
    render(c.file, dst);
    made.push(dst);
  });
}
console.log(`отрендерено ${made.length} png`);
