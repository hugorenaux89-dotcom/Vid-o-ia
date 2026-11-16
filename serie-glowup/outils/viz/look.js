// Apparence de Yanis jour après jour (tête + corps) : ensureY('Y12') crée C.Y12 et OUTFIT.Y12
const { C } = require('./toon2');
const { OUTFIT } = require('./rig');
function ensureY(id) {
  const m = /^Y(\d+)(s?)$/.exec(id); if (!m || C[id]) return;
  const d = +m[1], suit = m[2] === 's';
  const c = { skin: '#c98e62', hc: '#1c1511', w: +(1.42 - (d - 1) * (0.36 / 29)).toFixed(3) };
  c.hair = d < 7 ? 'bald' : d < 13 ? 'thick' : 'curly';
  c.glasses = d < 5 ? 'broken' : d < 19 ? 'rect' : 'thin';
  if (d < 6) c.teeth = 'dirty';
  if (d < 8) c.pimples = true; else if (d < 10) c.pimplesLight = true;
  if (d < 14) c.unibrow = true;
  c.beard = d < 12 ? 'cuts' : 'neat';
  if (d < 20) c.chin = true;
  if (d < 12) c.jowls = true;
  c.outfit = suit ? 'suit' : d < 3 ? 'hoodieDirty' : d < 19 ? 'hoodie' : 'bomber';
  if (d === 1) Object.assign(c, { ugly: true, headset: true, w: 1.48 });
  C[id] = c;
  const fat = d === 1 ? 62 : Math.max(4, 50 - (d - 1) * 1.6);
  let o;
  if (suit) o = { top: '#22325a', pants: '#22325a', shoes: '#1a1a1a', tie: '#9a1d2a', fat: Math.min(fat, 8) };
  else if (d < 3) o = { top: '#8d9096', short: true, stains: true, belly: true, pants: '#4b5878', shoes: '#ececec', stink: d < 2, fat: d === 1 ? 62 : 50 };
  else if (d < 19) o = { top: '#8d9096', short: fat > 30, pants: '#3e4a66', shoes: '#f4f4f4', fat };
  else if (d < 24) o = { top: '#8a1730', sleeve: '#f2e6d0', long: true, varsity: true, number: 'Y', pants: '#2a2a33', shoes: '#f4f4f4', fat };
  else o = { top: '#23345e', polo: true, pants: '#d8c3a0', shoes: '#f4f4f4', fat };
  OUTFIT[id] = o;
}
module.exports = { ensureY };
