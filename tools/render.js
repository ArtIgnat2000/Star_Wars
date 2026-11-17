const { Resvg } = require(process.env.RESVG || '/tmp/svgtool/node_modules/@resvg/resvg-js');
const fs = require('fs'), path = require('path');
const args = process.argv.slice(2);
const scale = parseFloat(process.env.SCALE || '2');
const bg = process.env.BG || 'rgba(0,0,0,0)';
for (const file of args) {
  const svg = fs.readFileSync(file, 'utf8');
  const r = new Resvg(svg, { fitTo: { mode: 'zoom', value: scale }, background: bg });
  const png = r.render().asPng();
  const out = file.replace(/\.svg$/i, '.png');
  fs.writeFileSync(out, png);
  console.log(out);
}
