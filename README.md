# 5H01 — chaîne TikTok de motivation (FR)

> **5H01** : la minute qui suit le réveil de 5 h. Celle où tu décides si tu y vas ou pas.

## Identité de la chaîne

| Élément | Règle |
|---|---|
| Nom / filigrane | **5H01** (n'apparaît qu'après l'accroche, jamais à la 1re seconde) |
| Couleurs | noir profond, grain argentique, **or `#F2B33D`** pour les mots-clés |
| Typo | Inter Display Black, MAJUSCULES, contour noir, mots allumés au rythme de la voix (karaoké) |
| Signature visuelle | barre de progression or en haut, compteur « JOUR 001 → 180 », passage nuit → lever de soleil au drop |
| Voix | masculine, grave, posée (ElevenLabs, voix « Adam », multilingual v2) |
| Structure | accroche 0-3 s → identification → déclic → **drop musical** → phrase finale qui boucle |
| Fin | carton « 5H01 — L'heure où tout commence. Épisode N / 30 » (incite à suivre la série) |
| Promesses | jamais de résultat garanti : « tu pourrais », « ça peut », pas de « tu vas devenir riche » |

## Structure du dépôt

```
tools/tts.py             voix off ElevenLabs + timestamps (synchro sous-titres)
tools/build_episode.py   montage auto : voix resserrée, musique + ducking, SFX, scènes, sous-titres, rendu 1080x1920
episodes/epXX/
  episode.json           réglages de l'épisode (scènes, mots surlignés, drop, coupes)
  voiceover.txt          texte de la voix off
  README.md              dossier de production complet (script, plans seconde par seconde, prompts vidéo IA, description, hashtags)
  build/                 voix, alignement, musiques et bruitages générés
  clips/                 (optionnel) vrais plans vidéo : ils remplacent automatiquement les fonds générés
  output/                vidéo finale .mp4 + sous-titres .srt + timeline
```

## Produire un épisode

```bash
python3 tools/tts.py episodes/ep01            # voix off (déjà fait pour l'ép. 1)
python3 tools/build_episode.py episodes/ep01  # rendu final -> episodes/ep01/output/ep01.mp4
python3 tools/build_episode.py episodes/ep01 --preview   # rendu rapide pour vérifier
```

Pour passer en version « images réelles » : générer les plans avec les prompts du README de l'épisode
(Kling, Runway, Veo, Sora…) ou utiliser des rushs libres de droits, les déposer dans `episodes/epXX/clips/`
avec le nom indiqué dans `episode.json`, puis relancer le rendu. Les sous-titres, la musique, le compteur
et la barre de progression restent identiques.

## Les 30 épisodes

| # | Titre / accroche | Thème |
|---|---|---|
| 1 | Dans 6 mois, tu pourrais être méconnaissable. | Effet composé des petits efforts |
| 2 | Personne ne viendra construire ta vie à ta place. | Responsabilité |
| 3 | Pendant que tu regardes cette vidéo, quelqu'un travaille sur ton rêve. | Concurrence / urgence |
| 4 | Imagine où tu serais si tu avais commencé il y a un an. | Le meilleur moment, c'est maintenant |
| 5 | Le plus grand danger, c'est de rester exactement comme tu es. | Zone de confort |
| 6 | La motivation te lâchera. La discipline, non. | Motivation vs discipline |
| 7 | Ton téléphone vole 4 heures de ta journée. | Distraction / temps |
| 8 | Ils ont rigolé. Garde leurs rires comme carburant. | Moqueries / revanche saine |
| 9 | Tu n'as pas besoin d'y croire. Tu as besoin de le faire. | Action avant confiance |
| 10 | Le réveil sonne. C'est là que tout se joue. | Les 10 premières secondes |
| 11 | Tu as déjà survécu à 100 % de tes pires jours. | Résilience |
| 12 | L'échec n'est pas le contraire de la réussite. | Échec = étape |
| 13 | Arrête d'attendre de te sentir prêt. | Perfectionnisme |
| 14 | Ce que tu fais quand personne ne regarde. | Travail invisible |
| 15 | Un euro par jour, ce n'est rien. Sauf dans 10 ans. | Finance / épargne composée |
| 16 | Tes amis définissent ton futur. | Entourage |
| 17 | La dernière répétition est la seule qui compte. | Sport / dépassement |
| 18 | Tu n'es pas fatigué. Tu t'ennuies de ta vie. | Sens / ambition |
| 19 | 1 % meilleur chaque jour = 37 fois meilleur en un an. | Amélioration continue (formule, sans promesse) |
| 20 | Le regret pèse plus lourd que l'effort. | Regret |
| 21 | Personne ne se souviendra de tes excuses. | Excuses |
| 22 | Ton futur toi te regarde en ce moment. | Lettre au futur soi |
| 23 | Les gens forts ont juste eu plus de jours difficiles. | Force mentale |
| 24 | Le dimanche soir décide de ta semaine. | Préparation / routine |
| 25 | Tu veux le résultat, mais tu fuis le processus. | Processus |
| 26 | Seul à la salle à 6 h. Et alors ? | Solitude du travail |
| 27 | Ne compare pas ton chapitre 1 au chapitre 20 d'un autre. | Comparaison / réseaux |
| 28 | Ton corps entend tout ce que ta tête lui dit. | Discours intérieur |
| 29 | Un jour ou jour un. C'est toi qui choisis. | Décision |
| 30 | Jour 180. Regarde le chemin parcouru. | Bilan de série / transformation |
