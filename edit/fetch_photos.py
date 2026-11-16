"""Download the CC-licensed photos used by the edit from Wikimedia Commons
(standard thumbnail sizes, polite pacing) and record author/licence in credits.json."""
import json, urllib.request, urllib.parse, time, os, sys, re
UA="Mozilla/5.0 (compatible; edit-renderer/1.0; +https://www.mediawiki.org/wiki/API:Etiquette)"
SEL = {
 'back10': 'File:Kylian Mbappe France v Senegal 16 June 2026-376.jpg',
 'closeup': 'File:Kylian Mbappe France v Paraguay 4 July 2026-201.jpg',
 'sprint': 'File:Kylian Mbappe -10 France v Sweden at 2026 Fifa World Cup by YantsImages 02.jpg',
 'sprint2': 'File:Kylian Mbappe -10 France v Sweden at 2026 Fifa World Cup by YantsImages 01.jpg',
 'trophy18': 'File:Kylian Mbappé with the 2018 Soccer World Cup trophy.jpg',
 'psgface': 'File:2019-07-17 SG Dynamo Dresden vs. Paris Saint-Germain by Sandro Halank–129 (cropped).jpg',
 'madrid': 'File:Kylian Mbappé against Málaga, match valid for the third round of La Liga on August 30, 2026.png',
 'volley': 'File:Kylian Mbappe France v Paraguay 4 July 2026-107.jpg',
 'champs18': 'File:France champion of the Football World Cup Russia 2018.jpg',
 'celeb18': 'File:Kylian Mbappe celebrating - March 2018.jpg',
 'flex': 'File:Kylian Mbappe France v Sweden 6.30.26-216.jpg',
 'keeper': 'File:Unai Simon Kylian Mbappe France v Spain 7.24.26-132.jpg',
 'shot': 'File:Leo Ostigard Kylian Mbappe France v Norway 26 June 26-074.jpg',
 'chest': 'File:Kylian Mbappe France v Sweden 6.30.26-222.jpg',
 'profile': 'File:Kylian Mbappe France v Spain 7.24.26-135.jpg',
 'dribble': 'File:Fabian Ruiz Kylian Mbappe France v Spain 7.24.26-048.jpg',
 'armswide': 'File:Kylian Mbappe France v Sweden 6.30.26-225.jpg',
 'jump': 'File:Kylian Mbappe France v Morocco 9 July 2026-173.jpg',
 'fist': 'File:Kylian Mbappe France v Senegal 16 June 2026-521.jpg',
 'thumbs': 'File:Kylian Mbappe France v Senegal 16 June 2026-391.jpg',
 'run': 'File:Kylian Mbappe France v Spain 7.24.26-052.jpg',
 'kick': 'File:Elliot Stroud Kylian Mbappe France v Sweden 6.30.26-116.jpg',
 'volley2': 'File:Kylian Mbappe France v Paraguay 4 July 2026-111.jpg',
 'psgdrib': 'File:2019-07-17 SG Dynamo Dresden vs. Paris Saint-Germain by Sandro Halank–569.jpg',
 'psgthumb': 'File:2019-07-17 SG Dynamo Dresden vs. Paris Saint-Germain by Sandro Halank–129 (cropped2).jpg',
 'psgshot': 'File:2019-07-17 SG Dynamo Dresden vs. Paris Saint-Germain by Sandro Halank–243.jpg',
 'young18': 'File:Kylian Mbappé 2018.jpg',
 'trophyrain': 'File:Kylian Mbappé World Cup Trophy.jpg',
}
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def api(titles):
    q=urllib.parse.urlencode({'action':'query','format':'json','titles':'|'.join(titles),'prop':'imageinfo',
        'iiprop':'url|size|extmetadata','iiextmetadatafilter':'LicenseShortName|Artist'})
    return json.loads(fetch('https://commons.wikimedia.org/w/api.php?'+q))

out=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'assets','photos'); os.makedirs(out, exist_ok=True)
STD=[1280,1920,3840]
def fetch(url):
    for i in range(30):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':UA}), timeout=120)
            data=r.read()
            if data[:20].lstrip().lower().startswith(b'<!doctype') : raise RuntimeError('html')
            return data
        except urllib.error.HTTPError as e:
            if e.code==429:
                print('  429, waiting 90', flush=True); time.sleep(90); continue
            raise
    raise SystemExit('gave up '+url)
by={}
for p in api(list(SEL.values()))['query']['pages'].values():
    by[p['title']]=p.get('imageinfo',[{}])[0]
credits=[]
for key,t in SEL.items():
    ii=by.get(t)
    if not ii: print('MISSING',key,t,flush=True); continue
    orig=ii['url'].split('?')[0]
    w,h=ii['width'],ii['height']
    ext=os.path.splitext(orig)[1].lower()
    # pick a standard thumbnail width giving >= ~2600 px on the long side, else original
    want = 2600*w/max(w,h)
    tw = next((s for s in STD if s>=want and s<w), None)
    if tw:
        base=orig.split('/wikipedia/commons/')[1]
        name=base.split('/')[-1]
        url='https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%dpx-%s'%(base,tw,name)
        if ext=='.png': url+='.png'
    else:
        url=orig
    fn=os.path.join(out,key+('.png' if ext=='.png' else '.jpg'))
    if not (os.path.exists(fn) and os.path.getsize(fn)>10000):
        print('get',key,tw or 'orig',flush=True)
        data=fetch(url)
        open(fn,'wb').write(data)
        time.sleep(15)
    em=ii.get('extmetadata',{})
    artist=re.sub('<[^>]+>','',(em.get('Artist') or {}).get('value','')).strip()
    credits.append({'key':key,'file':os.path.basename(fn),'title':t,'author':artist,
        'license':(em.get('LicenseShortName') or {}).get('value',''),'source':ii.get('descriptionurl','')})
json.dump(credits, open(os.path.join(out,'credits.json'),'w'), indent=1, ensure_ascii=False)
print('DONE',len(credits),flush=True)
