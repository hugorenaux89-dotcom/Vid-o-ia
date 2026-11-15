// Mixage v3 : bruitages épurés, musique qui s'efface sous la voix, normalisation -14 LUFS (2 passes)
const path = require('path');
const { execFileSync } = require('child_process');
const { TL, S, wt } = require('./ep01v3');
const B = path.join(__dirname, '../build/ep01v3');
const SFX = path.join(__dirname, '../build/ep01/sfx');
const VX = path.join(__dirname, '../build/ep01v2/voix');
require('fs').mkdirSync(B, { recursive: true });

const voix = [], fx = [];
for (const sc of TL.scenes) for (const v of sc.voices) voix.push([`${VX}/${v.id}.mp3`, sc.start + v.start, 1.0]);
const at = (id, local) => S[id].start + local;
const sfx = (n, id, local, v) => fx.push([`${SFX}/${n}.mp3`, at(id, local), v, n]);
let s;
s = S.hook; sfx('choc', 'hook', s.voices[0].dur + 0.02, 0.45); sfx('scratch', 'hook', s.voices[0].dur + 0.05, 0.6);
s = S.telephone; sfx('vibration', 'telephone', 0.0, 0.55); sfx('notif', 'telephone', s.notif, 0.45);
sfx('grillons', 'couette', 0, 0.28);
s = S.presentation; sfx('pop', 'presentation', wt(s, 'Sandrine', 0, 'e') + 0.02, 0.45);
s = S.pates; sfx('miaou', 'pates', wt(s, 'Lui'), 0.5); sfx('valise', 'pates', wt(s, 'demandé'), 0.5);
s = S.message; sfx('choc', 'message', wt(s, 'sera'), 0.5);
sfx('scratch', 'lycee', 0, 0.55); sfx('magie', 'lycee', 0.3, 0.32);
s = S.chute; const tSlip = s.voices[0].start + s.voices[0].dur + 0.2;
sfx('whoosh', 'chute', 0, 0.35); sfx('glissade', 'chute', tSlip - 0.05, 0.6); sfx('boing', 'chute', tSlip + 0.8, 0.35);
s = S.miroir; sfx('tambour', 'miroir', wt(s, 'trente') - 0.1, 0.38); sfx('ding', 'miroir', wt(s, 'toi'), 0.45);
s = S.vote; sfx('whoosh', 'vote', 0, 0.35); sfx('pop', 'vote', wt(s, 'sourcils'), 0.4);
s = S.fin; sfx('pop', 'fin', wt(s, 'mot') - 0.3, 0.4);
sfx('tambour', 'teaser', 0, 0.38); sfx('pop', 'teaser', 0.35, 0.45); sfx('ding', 'teaser', 1.5, 0.42);

const T = TL.total.toFixed(2);
const all = [...voix, ...fx];
const args = ['-y', '-loglevel', 'error'];
all.forEach(([f]) => args.push('-i', f));
args.push('-stream_loop', '-1', '-i', `${SFX}/musique.mp3`);
const m = all.length;
const fl = all.map(([, t, v], i) => `[${i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=${v},adelay=${Math.round(t * 1000)}|${Math.round(t * 1000)}[a${i}]`);
fl.push(`${voix.map((_, i) => `[a${i}]`).join('')}amix=inputs=${voix.length}:normalize=0:duration=longest,apad,atrim=0:${T},asplit=2[vx][sc]`);
fl.push(`${fx.map((_, j) => `[a${voix.length + j}]`).join('')}amix=inputs=${fx.length}:normalize=0:duration=longest,apad,atrim=0:${T}[fx]`);
fl.push(`[${m}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:${T},volume=0.22,afade=t=in:d=0.6,afade=t=out:st=${(TL.total - 1.8).toFixed(2)}:d=1.8[mu]`);
fl.push(`[mu][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350:makeup=1[duck]`);
fl.push(`[vx][fx][duck]amix=inputs=3:normalize=0:duration=first,atrim=0:${T}[out]`);
args.push('-filter_complex', fl.join(';'), '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', `${B}/premix.wav`);
execFileSync('ffmpeg', args, { stdio: 'inherit' });

// normalisation en 2 passes
const err = execFileSync('bash', ['-c', `ffmpeg -hide_banner -i "${B}/premix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p'`]).toString();
const j = JSON.parse(err);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', `${B}/premix.wav`, '-af',
  `loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=${j.input_i}:measured_TP=${j.input_tp}:measured_LRA=${j.input_lra}:measured_thresh=${j.input_thresh}:offset=${j.target_offset}:linear=true`,
  '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', `${B}/audio.m4a`], { stdio: 'inherit' });
console.log('audio v3 ok :', T, 's,', fx.length, 'bruitages (avant : 46)');
