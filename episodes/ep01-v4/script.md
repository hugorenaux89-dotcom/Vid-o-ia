# Lana 30 jours — Épisode 1 (version 4, nouveau script) — 1 min 38

2D · 1080 × 1920 · voix 100 % locale (Piper : Tom = narrateur, Siwis = Lana, Jessica = Inès) · aucune génération ElevenLabs
Bruitages limités à ceux qui racontent quelque chose (10 au total) · musique coupée pendant le souvenir du bal · -14 LUFS

| Temps | Scène | Voix | À l'écran |
|---|---|---|---|
| 0:00 | Lana au lit, éclairée par son téléphone | N : Dans trente jours, Lana va revoir le garçon qu'elle aime depuis le lycée. | « SON CRUSH REVIENT DANS 30 JOURS », polaroïd « NATHAN · 2016 ❤ » |
| 0:04 | Révélation, arrêt sur image | N : Et là, maintenant… elle ressemble à ça. | « ÇA. 👆 » + flèches : chignon nid d'oiseau, sourcils sauvages, pyjama depuis 2023 (disque rayé) |
| 0:07 | Couchée avec son ordi | N : Lana. Vingt-cinq ans. Record personnel : onze jours sans sortir de chez elle. | « 🏠 11 JOURS SANS SORTIR » |
| 0:13 | Le livreur de pizza | N : Son seul contact humain ? Le livreur de pizza. Et hier, il lui a demandé si elle allait bien. | Bulle « …ça va ? 😟 » |
| 0:19 | Pâtes refuse la caresse | N : Lui, c'est Pâtes. Il ne l'aime pas. Il reste pour les croquettes. | « PÂTES · 9 KG DE MÉPRIS » (miaulement) |
| 0:24 | La nuit, le téléphone vibre | N : Mais cette nuit, à trois heures quarante-sept, son téléphone vibre. | « 03:47 » (vibration) |
| 0:28 | Le message | INÈS : Coucou ma belle ! La soirée des dix ans du lycée, c'est dans trente jours. Tu viens ? / N : Inès. Son ex-meilleure amie. Elles ne se parlent plus depuis un certain bal de fin d'année. | Bulle de message, fiche « INÈS · 💔 DEPUIS LE BAL 2016 » |
| 0:39 | Le refus, puis le 2e message | LANA : Hors de question. / N : Deuxième message. / INÈS : Au fait… Nathan m'a demandé si tu venais. | Téléphone jeté, bras croisés, « 📳 2E MESSAGE », bulle 😏 |
| 0:44 | Le cri | LANA : Quoi ?! Nathan ?! | « NATHAN ?! », tremblement, flash rouge (« dun dun dun ») |
| 0:46 | Souvenir du bal 2016 | N : Nathan. Le seul garçon qui riait à toutes ses blagues. Le soir du bal, il lui avait donné rendez-vous, pour lui dire quelque chose d'important. Il n'est jamais venu. Et elle n'a jamais su pourquoi. | Lana ado seule avec un cadeau, « 23:59 », lumières qui s'éteignent, musique coupée |
| 0:59 | La décision | LANA : D'accord. Trente jours. Je change tout. | « J-30 », poings serrés |
| 1:01 | Au ralenti… la chute | N : Lana se lève. Pour la première fois depuis des semaines… et elle glisse sur une boîte de nuggets. | « ✨ AU RALENTI ✨ », « PAF ! », « NUGGETS 1 · LANA 0 » |
| 1:08 | Le miroir | N : Trente jours pour devenir méconnaissable. Mais seule, elle n'y arrivera pas. Alors c'est toi qui choisis. Chaque jour, une décision. Et ce qui est fait… est fait pour toujours. | « 👉 C'EST TOI QUI CHOISIS », tampon « DÉFINITIF » |
| 1:20 | Le vote | N : Premier choix. Son appart, qui sent la pizza froide depuis deux mille vingt-deux. Ou ses sourcils, qui ont leur propre code postal. | APPART / OU / SOURCILS |
| 1:28 | Appel au vote | N : Écris un seul mot en commentaire. Le plus voté gagne demain. | « ÉCRIS UN MOT 👇 », APPART / SOURCILS |
| 1:32 | La porte | N : Et demain… quelqu'un sonne à sa porte. | « DING DONG 🔔 », ombre de pieds sous la porte (sonnette) |
| 1:35 | Écran final | — | « JOUR 2 — QUI EST DERRIÈRE LA PORTE ? 👀 », abonne-toi, vote, partage |

## Légende TikTok
Son crush revient dans 30 jours… et elle ne sort plus de chez elle 😬 Jour 1/30 : c'est TOI qui décides de sa transformation. Commente APPART ou SOURCILS 👇 #30joursdetransformation #glowup #transformation #animation #histoire

## Refaire
python3 outils/voix_locale.py episodes/ep01-3d/voix-off.json build/ep01-3d/voix
node outils/mix-ep2d.js
DSF=1.5 node outils/render.js ./ep2d.js video build/ep01-2d/video.mp4 30 4
