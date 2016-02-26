import requests
import re
import csv

print('Prosimo počakajte, obdelujem podatke...')
print('Postopek bo trajal približno 35 minut.')

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

identiteta = {'sport' : [], 'zdravje': [], 'kultura' : [], 'zabava' : [], 'tureavanture' : [], 'svet':[], 'slovenija':[], 'gospodarstvo':[], 'znanost-in-tehnologija':[]}

seznam_tem = ['sport', 'zdravje', 'kultura', 'zabava', 'tureavanture', 'svet', 'slovenija', 'gospodarstvo', 'znanost-in-tehnologija']

seznam_slovarjev_stevilk = []

for a in seznam_tem:
    for i in range(5):
        r = requests.get('http://www.rtvslo.si/{0}/arhiv/?&page={1}'.format(a, i))
        besedilo =  r.text
        identiteta[a].extend(re.findall(r'<a href=".+?{0}.+?(\d+)" class="title">(?:.+?)</a>'.format(a), besedilo))
    
for tema, sez_cifr in identiteta.items():
    for i in sez_cifr:
        r1 = requests.get('http://www.rtvslo.si/arhiv/{0}'.format(i))
        text1 = r1.text
        ocene_na_vrhu = re.findall(r'>Ocena (\d+\.\d) od (\d+) glasov<', text1)
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
                    a += int(v)
                else:
                    b += int(v)
                    
                stevilo_komentarjev +=1
                
            j += 1
            r = requests.get('http://www.rtvslo.si/index.php?&c_mod=news&op=comments&func=ajax&id={0}&page={1}&hash=0&sort=asc'.format(i,j))
            komentarji = r.text
            kljucar = ali_ni_prazno(komentarji)

        seznam_slovarjev_stevilk.append({'id': i, 'tema': tema, 'stevilo_komentarjev': (stevilo_komentarjev//2), 'stevilo_ocen_komentarjev': a+b, 'stevilo_pozitivnih': a, 'stevilo_negativnih': b, 'ocena_novice': ocena_novice, 'stevilo_ocen':stevilo_ocen}) 

print('Shranjujem datoteke...')

zapisi_tabelo(seznam_slovarjev_stevilk, ['id', 'tema', 'stevilo_komentarjev', 'stevilo_ocen_komentarjev', 'stevilo_pozitivnih', 'stevilo_negativnih', 'ocena_novice', 'stevilo_ocen'], 'projekt_tabela.csv')

print('Podrobnosti analize so shranjene v datotekah!')
