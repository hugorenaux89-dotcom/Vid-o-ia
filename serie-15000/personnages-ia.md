# 🤖 Fiches IA : personnages, lieux et style

Les prompts des scripts utilisent des **raccourcis** entre accolades, par exemple `{YANIS}` ou `{GARAGE}`.
Avant de générer une vidéo, **remplace chaque raccourci par sa description complète** (copier-coller depuis cette page), puis ajoute `{STYLE}` à la fin du prompt.

> 💡 **Le plus important pour garder les mêmes visages d'un épisode à l'autre :**
> génère d'abord **une image de référence par personnage** (avec le prompt « portrait » ci-dessous), puis donne-la à ton outil vidéo à chaque plan.
> Selon l'outil, cette option s'appelle *image de référence*, *ingredients*, *character reference* ou *image-to-video*.

Les prompts sont en **anglais** parce que la plupart des générateurs vidéo comprennent mieux l'anglais. Les **dialogues restent en français**.

---

## Style global

**{STYLE}**
```
Vertical 9:16 video, photorealistic, shot on a smartphone, slightly handheld camera, natural lighting, shallow depth of field, subtle film grain, contemporary French suburb (banlieue parisienne), no text on screen, no subtitles.
```

**Pour un flash-back**, ajoute :
```
Desaturated colors, soft blur on the edges, slightly overexposed, memory-like.
```

**Si ton outil génère aussi la voix** (son intégré), ajoute à la fin du prompt la réplique du plan :
```
He says in French, in a low tense voice: "J'suis parti vingt minutes. Vingt."
```

---

## Personnages

### {YANIS}, le héros, 24 ans
```
a 24-year-old French man of North African descent, short dark brown hair with a fade, light stubble, tired brown eyes, grey hoodie with small grease stains, thin silver chain, black work pants
```
**Portrait de référence :** `Portrait of {YANIS}, neutral background, facing camera, soft daylight, photorealistic.`
**Voix :** grave, posée, un peu rauque. Parle vite quand il stresse.

### {VIDAL}, le méchant, 55 ans
```
a 55-year-old elegant French man, grey hair slicked back, clean-shaven, navy blue tailored suit, white shirt with open collar, no tie, gold watch, a gold signet ring on the right hand, calm cold smile
```
**Voix :** très calme, lente, polie, jamais un mot plus haut que l'autre.

### {LINA}, 23 ans
```
a 23-year-old French woman, curly dark hair tied up in a bun, small round glasses, warm brown skin, beige bakery apron over a white t-shirt, lively intelligent eyes
```
**Voix :** vive et rapide, avec de l'humour. Devient très sérieuse quand ça compte.

### {SOFIANE}, le meilleur pote, 24 ans
```
a 24-year-old French man, slim, black tracksuit, backwards black cap, small gold earring, very expressive face, always moving his hands
```
**Voix :** forte, drôle, exagère tout.

### {NADIA}, la mère, 50 ans
```
a 50-year-old French woman of North African descent, light patterned headscarf, beige wool cardigan, gentle tired face, warm eyes
```
**Voix :** douce, mais ferme quand elle décide.

### {GERARD}, le patron du garage, 60 ans
```
a 60-year-old French man, heavy build, grey moustache, balding, blue mechanic overalls, reading glasses on his forehead, nervous eyes
```
**Voix :** bourrue, fatiguée.

### {BRUNO}, le chauffeur de Vidal, 40 ans
```
a 40-year-old very tall muscular man, shaved head, short black beard, black bomber jacket, black jeans, expressionless face
```
**Voix :** il parle très peu, d'une voix sourde.

### {KARIM}, le « cousin » prêteur, 30 ans
```
a 30-year-old man, white tracksuit, thick gold chain, perfectly trimmed beard, relaxed confident posture
```

### {INES}, l'influenceuse, 25 ans
```
a 25-year-old glamorous young woman, long straight blonde hair, oversized sunglasses on her head, pink tracksuit, phone always in hand
```

### {BERNARD}, le vieux client, 75 ans
```
a 75-year-old kind old man, white hair, flat cap, brown corduroy jacket, walking slowly
```

### {MALIK}, le père (photos et flash-backs uniquement), 45 ans
```
a 45-year-old French man of North African descent, resembling {YANIS}, short greying hair, warm smile, blue mechanic overalls with the name "Malik" embroidered, wearing a vintage Seiko watch
```

---

## Lieux

| Raccourci | Description à coller |
|---|---|
| **{GARAGE}** | `a small cluttered independent car repair garage in a Paris suburb, concrete floor with oil stains, white neon tube lights, tools on a pegboard wall, a car lift, a half-open metal roller shutter` |
| **{BUREAU}** | `a tiny messy garage office with a glass window onto the workshop, old desktop computer showing security camera footage, papers and invoices everywhere, a calendar with car pictures` |
| **{CHAMBRE}** | `a small bedroom in a social housing apartment, single bed, posters of cars, a gaming chair, a window with a view on apartment towers` |
| **{CUISINE}** | `a warm modest family kitchen, small table with a patterned oilcloth, a steaming tajine pot, family photos on the fridge` |
| **{BOULANGERIE}** | `a small neighborhood French bakery, glass counter full of croissants and baguettes, warm morning light` |
| **{PARKING}** | `an open-air supermarket parking lot in a French suburb, a handmade cardboard sign "YANIS LAVAGE 40€", buckets, sponges and a pressure washer` |
| **{VOITURE}** | `inside an old small car at night, dashboard lights, street lights passing through the windows` |
| **{ENTREPOT}** | `a dark abandoned industrial warehouse at night, only a flashlight beam, dust in the air, car parts on metal shelves, a car covered with a grey tarp` |
| **{TOIT}** | `the rooftop of a suburban apartment tower at night, the lights of Paris in the distance, a low concrete wall` |
| **{PMU}** | `a typical French neighborhood bar-tabac (PMU), horse racing on a TV screen, zinc counter, neon lights` |
| **{CAVE}** | `a narrow basement storage room of an apartment building, bare light bulb, dusty cardboard boxes` |
| **{COMMISSARIAT}** | `the reception desk of a small French police station, grey walls, a tired police officer behind a computer` |

---

## Objets récurrents

- **{PORSCHE}** : `a grey 1990s Porsche 911 in perfect condition`
- **{MONTRE}** : `a vintage Seiko 6139 chronograph watch with a yellow dial`
- **{MERCEDES}** : `a black Mercedes S-Class with tinted windows`

---

## Le compteur (à ajouter au montage, pas dans l'IA)

Les générateurs vidéo écrivent mal le texte. **Ajoute le compteur et les sous-titres au montage**, dans CapCut ou dans l'éditeur de TikTok :
- **Position :** en haut au centre, police grasse blanche avec un contour noir.
- **Format :** `J-17 · 10 300 € / 15 000 €`
- **Quand l'argent baisse :** le compteur passe au rouge pendant 1 seconde, avec un petit bruit sourd.
- **Quand l'argent monte :** il passe au vert, avec un bruit de caisse enregistreuse.
