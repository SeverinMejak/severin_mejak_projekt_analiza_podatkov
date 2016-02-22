import requests
import re
import csv


print('Prosimo počakajte, obdelujem podatke...')
print('Postopek bo trajal približno tri minute.')

def ali_ni_prazno(komentarji):
    r = re.search(r'<div class="newscomments">\s*</div>',komentarji)
    r2 = re.search(r'<div style="padding: 10px">Ta novica trenutno še nima komentarjev.</div>',komentarji)
    
    if (r is None) and (r2 is None):
        return True
    else:
        return False

def zapisi_tabelo(slovarji, imena_polj, ime_datoteke):
    with open(ime_datoteke, 'w') as csv_dat:
        writer = csv.DictWriter(csv_dat, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

linki = {'sport' : [], 'novice' : [], 'kultura' : [], 'zabava' : [], 'tureavanture' : []}
identiteta = {'sport' : [], 'novice' : [], 'kultura' : [], 'zabava' : [], 'tureavanture' : []}


seznam_tem = ['sport', 'novice', 'kultura', 'zabava', 'tureavanture']
for a in seznam_tem:
    r = requests.get('http://www.rtvslo.si/{0}/arhiv/'.format(a))
    besedilo =  r.text
    linki[a].extend(re.findall(r'<a href="(.+?)" class="title">(?:.+?)</a>', besedilo))

seznam_slovarjev_stevilk = []

for tema, sez_linkov in linki.items():
    for i in sez_linkov:
        d = re.findall(r'(\d+)$', i)
        identiteta[tema].extend(d)

vsi = {'predznak': 'vseh_komentarjev', 'stevilo' : 0}
pozitivni = {'predznak': 'pozitivnivnih_ocen', 'stevilo' : 0}
negativni = {'predznak': 'negativninih_ocen', 'stevilo': 0}

slovar_pozitivnih = {'predznak': 'pozitivninih_ocen', 'sport' : 0, 'novice' : 0, 'kultura' : 0, 'zabava' : 0, 'tureavanture' : 0}
slovar_negativnih = {'predznak': 'negativninih_ocen', 'sport' : 0, 'novice' : 0, 'kultura' : 0, 'zabava' : 0, 'tureavanture' : 0}
slovar_vseh = {'predznak': 'vseh_komentarjev', 'sport' : 0, 'novice' : 0, 'kultura' : 0, 'zabava' : 0, 'tureavanture' : 0}


for tema, sez_cifr in identiteta.items():
    for i in sez_cifr:
        r1 = requests.get('http://www.rtvslo.si/{0}/arhiv/{1}'.format(tema, i))
        text1 = r1.text
        ocene_na_vrhu = re.findall(r'<span class="fl" id="rate_results">Ocena (\d+\.?\d*) od (\d+) glasov</span>', text1)
        if not ocene_na_vrhu:
            ocena_novice = -1
            stevilo_ocen = 0
        else:
            ocena_novice = float(ocene_na_vrhu[0][0])
            stevilo_ocen = int(ocene_na_vrhu[0][1])
        stevilo_komentarjev = 0
        a = 0
        b = 0
        j = 0
        r = requests.get('http://www.rtvslo.si/index.php?&c_mod=news&op=comments&func=ajax&id={0}&page={1}&hash=0&sort=asc'.format(i,j))
        komentarji = r.text
        kljucar = ali_ni_prazno(komentarji)
        while kljucar:
            ocene = re.findall(r'<span>(.)(\d+)</span>', komentarji)
            for u,v in ocene:
                if u == '+':
                    pozitivni['stevilo'] += int(v)
                    slovar_pozitivnih[tema] += int(v)
                    a += int(v)
                else:
                    negativni['stevilo'] += int(v)
                    slovar_negativnih[tema] += int(v)
                    b += int(v)
                    
                stevilo_komentarjev +=1
                slovar_vseh[tema] += 1
                vsi['stevilo'] += 1
                
                
            j += 1
            r = requests.get('http://www.rtvslo.si/index.php?&c_mod=news&op=comments&func=ajax&id={0}&page={1}&hash=0&sort=asc'.format(i,j))
            komentarji = r.text
            kljucar = ali_ni_prazno(komentarji)

        seznam_slovarjev_stevilk.append({'id': i, 'tema': tema, 'stevilo_komentarjev': stevilo_komentarjev, 'stevilo_ocen_komentarjev': a+b, 'stevilo_pozitivnih': a, 'stevilo_negativnih': b, 'ocena_novice': ocena_novice, 'stevilo_ocen':stevilo_ocen}) 
            

seznam_slovarjev_po_temah = [slovar_vseh, slovar_pozitivnih, slovar_negativnih]
seznam_slovarjev_po_stevilu = [vsi, pozitivni, negativni]

print('Shranjujem datoteke...')

zapisi_tabelo(seznam_slovarjev_po_temah, ['predznak', 'sport','novice', 'kultura', 'zabava', 'tureavanture'], 'projekt_podatki1.csv')
zapisi_tabelo(seznam_slovarjev_po_stevilu, ['predznak', 'stevilo'], 'projekt_podatki2.csv')
zapisi_tabelo(seznam_slovarjev_stevilk, ['id', 'tema', 'stevilo_komentarjev', 'stevilo_ocen_komentarjev', 'stevilo_pozitivnih', 'stevilo_negativnih', 'ocena_novice', 'stevilo_ocen'], 'projekt_tabela.csv')


print('Podrobnosti analize so shranjene v datotekah!')
