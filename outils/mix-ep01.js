// Mixage audio de l'épisode 1 : voix + bruitages synchronisés + musique
const path = require('path');
const { execFileSync } = require('child_process');
const { TL, S, wt } = require('./ep01');
const B = path.join(__dirname, '../build/ep01');
const ev = []; // [fichier, temps absolu, volume]
const at = (id, local) => S[id].start + local;
const sfx = (n, id, local, v = 0.8) => ev.push([`${B}/sfx/${n}.mp3`, at(id, local), v]);

for (const sc of TL.scenes) for (const v of sc.voices) ev.push([`${B}/voix/${v.id}.mp3`, sc.start + v.start, 1.0]);
let s;
s = S.telephone; sfx('vibration', 'telephone', 0.05, 0.9); sfx('notif', 'telephone', 0.9, 0.7);
s = S.couette; sfx('grillons', 'couette', 0, 0.35); sfx('pop', 'couette', wt(s, 'Lana'), 0.6); sfx('pop', 'couette', wt(s, 'volets'), 0.6);
s = S.presentation; sfx('whoosh', 'presentation', 0, 0.5); sfx('pop', 'presentation', wt(s, 'service'), 0.6); sfx('pop', 'presentation', wt(s, 'Sandrine') + 0.05, 0.7);
s = S.pates; sfx('whoosh', 'pates', 0, 0.5); sfx('miaou', 'pates', wt(s, 'Lui'), 0.8); sfx('pop', 'pates', wt(s, 'Lui') + 0.3, 0.5); sfx('valise', 'pates', wt(s, 'demandé'), 0.8);
s = S.message; sfx('whoosh', 'message', 0, 0.5); sfx('pop', 'message', wt(s, "d'Inès"), 0.6); sfx('choc', 'message', wt(s, 'sera'), 0.75);
s = S.lycee; sfx('scratch', 'lycee', 0, 0.8); sfx('magie', 'lycee', 0.3, 0.5);
s = S.jean; sfx('whoosh', 'jean', 0, 0.6); sfx('pop', 'jean', wt(s, 'jean'), 0.6);
s = S.chute; const tSlip = s.voices[0].start + 3.4; sfx('pop', 'chute', wt(s, 'décidée'), 0.4); sfx('glissade', 'chute', tSlip - 0.05, 1.0); sfx('boing', 'chute', tSlip + 0.8, 0.6); sfx('pop', 'chute', s.voices[1].start + 1.2, 0.6);
s = S.miroir; sfx('whoosh', 'miroir', 0, 0.5); sfx('pop', 'miroir', wt(s, 'trente'), 0.6); sfx('ding', 'miroir', wt(s, 'toi'), 0.6);
s = S.vote; sfx('whoosh', 'vote', 0, 0.5); sfx('pop', 'vote', 0.25, 0.5); sfx('pop', 'vote', wt(s, 'appart'), 0.6); sfx('pop', 'vote', wt(s, 'sourcils'), 0.6);
s = S.fin; sfx('pop', 'fin', wt(s, 'mot') - 0.3, 0.6); sfx('pop', 'fin', wt(s, 'mot') + 0.1, 0.5); sfx('pop', 'fin', wt(s, 'mot') + 0.25, 0.5); sfx('ding', 'fin', wt(s, 'toujours', 0, 'e') + 0.4, 0.7);

const T = TL.total;
const args = ['-y', '-loglevel', 'error'];
ev.forEach(([f]) => args.push('-i', f));
args.push('-stream_loop', '-1', '-i', `${B}/sfx/musique.mp3`);
const fl = ev.map(([, t, v], i) => `[${i}:a]aresample=44100,aformat=channel_layouts=stereo,volume=${v},adelay=${Math.round(t * 1000)}|${Math.round(t * 1000)}[a${i}]`);
const m = ev.length;
fl.push(`[${m}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:${T.toFixed(2)},volume=0.14,afade=t=in:d=0.8,afade=t=out:st=${(T - 1.8).toFixed(2)}:d=1.8[mus]`);
fl.push(`${ev.map((_, i) => `[a${i}]`).join('')}[mus]amix=inputs=${m + 1}:normalize=0:duration=longest,atrim=0:${T.toFixed(2)},loudnorm=I=-14:TP=-1.5:LRA=11[out]`);
args.push('-filter_complex', fl.join(';'), '-map', '[out]', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', `${B}/audio.m4a`);
execFileSync('ffmpeg', args, { stdio: 'inherit' });
console.log('audio ok', T.toFixed(2), 's,', ev.length, 'pistes');
