// Mixage épisode 1 (2D, voix locale) : uniquement les bruitages qui racontent quelque chose
const path = require('path');
const { execFileSync } = require('child_process');
const { TL, P, wt, vstart: vs, vend: ve } = require('./ep3d');
const B = process.env.OUT_DIR || path.join(__dirname, '../build/ep01-2d');
const SFX = path.join(__dirname, '../build/ep01/sfx');
const VX = process.env.VOIX_DIR || path.join(__dirname, '../build/ep01-3d/voix');
const voix = [], fx = [];
for (const p of TL.plans) for (const v of p.voices) voix.push([`${VX}/${v.id}.wav`, p.start + v.start, 1.0]);
const at = (id, local) => P[id].start + local;
const sfx = (f, id, local, v) => fx.push([f.includes('/') ? f : `${SFX}/${f}.mp3`, at(id, local), v]);
let p;
p = P.hook; sfx('scratch', 'hook', wt(p, 'ça', 0, 'e') + 0.05, 0.55);                       // arrêt sur image
p = P.pates; sfx('miaou', 'pates', wt(p, 'croquettes'), 0.45);               // le chat réclame
p = P.nuit; sfx('vibration', 'nuit', wt(p, 'vibre', 0, 'e') + 0.05, 0.5);                   // le téléphone vibre
p = P.message; sfx('notif', 'message', vs(p, 'e2') - 0.15, 0.4);              // le message arrive
p = P.refus; sfx('vibration', 'refus', vs(p, 'f2') - 0.2, 0.5);              // 2e message
p = P.cri; sfx('choc', 'cri', ve(p, 'f4') + 0.02, 0.45);                                     // « Nathan ?! »
sfx('magie', 'bal', 0.0, 0.3);                                                // entrée dans le souvenir
p = P.chute; const tSlip = ve(p, 'h2') + 0.05;
sfx('glissade', 'chute', tSlip - 0.05, 0.55); sfx('boing', 'chute', tSlip + 0.8, 0.3);   // glissade + étourdie
p = P.porte; sfx(`${B}/sonnette.wav`, 'porte', wt(p, 'sonne'), 0.7);          // la sonnette

const T = TL.total.toFixed(2);
const all = [...voix, ...fx];
const args = ['-y', '-loglevel', 'error'];
all.forEach(([f]) => args.push('-i', f));
args.push('-stream_loop', '-1', '-i', `${SFX}/musique.mp3`);
const m = all.length;
const fl = all.map(([, t, v], i) => `[${i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=${v},adelay=${Math.round(t * 1000)}|${Math.round(t * 1000)}[a${i}]`);
fl.push(`${voix.map((_, i) => `[a${i}]`).join('')}amix=inputs=${voix.length}:normalize=0:duration=longest,apad,atrim=0:${T},asplit=2[vx][sc]`);
fl.push(`${fx.map((_, j) => `[a${voix.length + j}]`).join('')}amix=inputs=${fx.length}:normalize=0:duration=longest,apad,atrim=0:${T}[fx]`);
// musique : coupée pendant le souvenir du bal (émotion), reprise à la décision
const b0 = P.bal.start, b1 = P.decision.start;
fl.push(`[${m}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:${T},volume=0.2,afade=t=in:d=0.6,volume='if(between(t,${(b0 + 0.3).toFixed(2)},${b1.toFixed(2)}),max(0.08,1-(t-${(b0 + 0.3).toFixed(2)})/1.2),1)':eval=frame,afade=t=out:st=${(TL.total - 2).toFixed(2)}:d=2[mu]`);
fl.push(`[mu][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[duck]`);
fl.push(`[vx][fx][duck]amix=inputs=3:normalize=0:duration=first,atrim=0:${T}[out]`);
args.push('-filter_complex', fl.join(';'), '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', `${B}/premix.wav`);
execFileSync('ffmpeg', args, { stdio: 'inherit' });
const j = JSON.parse(execFileSync('bash', ['-c', `ffmpeg -hide_banner -i "${B}/premix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p'`]).toString());
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', `${B}/premix.wav`, '-af', `loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=${j.input_i}:measured_TP=${j.input_tp}:measured_LRA=${j.input_lra}:measured_thresh=${j.input_thresh}:offset=${j.target_offset}:linear=true`, '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', `${B}/audio.m4a`], { stdio: 'inherit' });
console.log('audio ok', T, 's,', fx.length, 'bruitages');
