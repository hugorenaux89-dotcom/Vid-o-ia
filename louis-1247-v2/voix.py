# Voix retravaillée : chaque phrase est générée séparément avec son propre ton
# (vitesse / hauteur), puis assemblée avec de vraies respirations et pauses.
import asyncio, json, os, ssl, subprocess, edge_tts, edge_tts.communicate as ec
ec._SSL_CTX=ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
V="fr-FR-RemyMultilingualNeural"; PX=os.environ.get("HTTPS_PROXY")
# ton : (rate, pitch)
T={"cri":("+22%","+12Hz"),"vif":("+14%","+4Hz"),"normal":("+8%","+0Hz"),"blase":("+0%","-6Hz"),"chuchote":("-4%","-8Hz"),"fier":("+10%","+6Hz")}
# chaque plan : liste de (ton, phrase, pause_après_en_s)
P=[
 ("p01",[("cri","Non, non, non, non !",0.1),("cri","Pourquoi il y a un cochon dans mon lit ?!",0.3)]),
 ("p02",[("blase","Attends.",0.15),("normal","On reprend depuis le début.",0.3)]),
 ("p03",[("vif","Hier soir, je me suis couché en 2026.",0.25),("normal","Ce matin… plus de chambre. Plus de téléphone.",0.2),("blase","Juste… de la paille.",0.3)]),
 ("p04",[("chuchote","Petit défi.",0.15),("vif","Un objet de 2026 est caché dans cette vidéo. Trouve-le, et écris-le en commentaire.",0.3)]),
 ("p05",[("normal","Les toilettes ?",0.2),("blase","Un seau. Bon courage.",0.3)]),
 ("p06",[("vif","Question !",0.15),("normal","Au Moyen Âge, on buvait quoi ? De la bière… ou de l'eau ?",1.6)]),
 ("p07",[("fier","De l'eau !",0.15),("vif","La bière à tous les repas parce que l'eau était sale, c'est un mythe.",0.2),("normal","Bon, il y avait aussi de la petite bière, très légère.",0.3)]),
 ("p08",[("normal","Petit-déj : pain noir et bouillie.",0.2),("blase","Et non. Pas de Nutella.",0.3)]),
 ("p09",[("vif","Six heures, direction les champs.",0.2),("blase","Le bœuf me regarde comme si c'était moi, l'animal.",0.3)]),
 ("p10",[("vif","Ici, on bosse du lever au coucher du soleil.",0.2),("normal","Repos ? Le dimanche… et les fêtes religieuses.",0.3)]),
 ("p11",[("chuchote","Attends…",0.3),("vif","Tu entends ça ?",0.3)]),
 ("p12",[("normal","Le seigneur.",0.2),("vif","Il prend sa part de ma récolte.",0.15),("normal","Et la semaine prochaine, je travaille gratuitement sur ses terres.",0.15),("blase","Ça s'appelle la corvée.",0.3)]),
 ("p13",[("blase","Et en plus, faut dire merci.",0.2),("fier","Merci, monseigneur !",0.3)]),
 ("p14",[("vif","Et toi, t'aurais fait quoi ?",0.15),("normal","Commente : courbette… ou révolte ?",0.4)]),
 ("p15",[("normal","Quinze heures. Je me coupe avec la faucille.",0.2),("blase","Et les antibiotiques… c'est dans sept cents ans.",0.3)]),
 ("p16",[("vif","Donc, direction le barbier.",0.15),("normal","Il coupe les cheveux, arrache les dents… et soigne les blessures.",0.3)]),
 ("p17",[("normal","Il met du vin et du miel sur ma plaie.",0.2),("fier","Ça, franchement, c'est malin.",0.3)]),
 ("p18",[("normal","Et après… il me propose une saignée.",0.3),("cri","Non. Merci !",0.3)]),
 ("p19",[("normal","Le soir, toute la famille dort dans la même pièce…",0.2),("vif","et les animaux aussi. Leur chaleur chauffe la maison.",0.3)]),
 ("p20",[("blase","Voilà.",0.2),("blase","Le cochon.",0.2),("vif","Tout s'explique.",0.3)]),
 ("p21",[("chuchote","L'espérance de vie ? Environ trente ans.",0.2),("normal","Mais surtout parce que beaucoup d'enfants mouraient jeunes. Les adultes vivaient souvent bien plus longtemps.",0.3)]),
 ("p22",[("vif","Alors, t'aurais tenu combien de jours ?",0.2),("normal","Et l'objet caché, tu l'as trouvé ?",0.2),("fier","Partie deux… si je survis.",0.6)]),
]
async def tts(text,ton,out):
    r,p=T[ton]
    await edge_tts.Communicate(text,V,rate=r,pitch=p,proxy=PX).save(out)
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
async def main():
    os.makedirs("tmp",exist_ok=True); plans=[]; t=0
    for pid,lines in P:
        parts=[]
        for i,(ton,txt,pause) in enumerate(lines):
            f=f"tmp/{pid}_{i}.mp3"; await tts(txt,ton,f)
            parts.append((f,pause))
        # assemble le plan : phrases + silences (respirations)
        inputs=[];flt=[]
        for j,(f,pause) in enumerate(parts):
            inputs+=["-i",f]; flt.append(f"[{j}:a]aresample=44100,aformat=channel_layouts=mono,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur={pause}[a{j}]")
        flt.append("".join(f"[a{j}]" for j in range(len(parts)))+f"concat=n={len(parts)}:v=0:a=1[o]")
        out=f"voix/{pid}.mp3"
        subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(flt),"-map","[o]","-b:a","192k",out],check=True)
        d=dur(out); plans.append({"plan":pid,"debut":round(t,2),"duree":round(d,2),"texte":" ".join(x[1] for x in lines)}); t+=d
    lst="\n".join(f"file 'voix/{p['plan']}.mp3'" for p in plans)
    open("tmp/list.txt","w").write(lst.replace("file 'voix/","file '../voix/"))
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","tmp/list.txt","-af","loudnorm=I=-14:TP=-1.5","-b:a","192k","Louis_1247_voix_off_complete.mp3"],check=True)
    json.dump(plans,open("timings.json","w"),ensure_ascii=False,indent=1)
    print(round(t,1))
asyncio.run(main())
