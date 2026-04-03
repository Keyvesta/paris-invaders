#!/usr/bin/env python3
import json,re,time,math,random,datetime
import requests
from bs4 import BeautifulSoup

DATA_FILE='data.json'
BASE='https://www.invader-spotter.art'
STATUS={'ok':'OK','damaged':'damaged','destroyed':'destroyed','hidden':'hidden'}

def obf(lat,lng,r=8):
    random.seed(int((lat+lng)*1e6))
    return round(lat+random.uniform(-r,r)/111320,6),round(lng+random.uniform(-r,r)/(111320*math.cos(math.radians(lat))),6)

def fetch_list():
    res=requests.get(f'{BASE}/ville.php?ville=paris',timeout=15,headers={'User-Agent':'ParisinvadersApp/1.0'})
    soup=BeautifulSoup(res.text,'html.parser')
    out=[]
    for row in soup.select('tr'):
        cells=row.find_all('td')
        if not cells:continue
        id_=cells[0].get_text(strip=True)
        if not re.match(r'PA_\d+',id_):continue
        st=STATUS.get(cells[1].get_text(strip=True).lower() if len(cells)>1 else 'ok','OK')
        pts=int(re.search(r'\d+',cells[2].get_text(strip=True)).group()) if len(cells)>2 and re.search(r'\d+',cells[2].get_text(strip=True)) else 10
        out.append({'id':id_,'status':st,'points':pts})
    return out

def fetch_coords(inv_id):
    try:
        r=requests.get(f'{BASE}/invader.php?id={inv_id}',timeout=10,headers={'User-Agent':'ParisinvadersApp/1.0'})
        lat=re.search(r'lat[":\s=]+(-?\d+\.\d+)',r.text)
        lng=re.search(r'l(?:ng|on)[":\s=]+(-?\d+\.\d+)',r.text)
        if lat and lng:return float(lat.group(1)),float(lng.group(1))
    except:pass
    return None,None

def main():
    with open(DATA_FILE) as f:data=json.load(f)
    existing={d['id']:d for d in data}
    today=datetime.date.today().isoformat()
    changes=0
    try:
        remote=fetch_list()
        print(f'{len(remote)} invaders sur invader-spotter')
        for r in remote:
            if r['id'] in existing:
                if existing[r['id']].get('status')!=r['status']:
                    existing[r['id']]['status']=r['status'];changes+=1;print(f"Status {r['id']}: {r['status']}")
            else:
                lat,lng=fetch_coords(r['id'])
                if lat and lng:
                    ola,oln=obf(lat,lng)
                    existing[r['id']]={'id':r['id'],'status':r['status'],'points':r['points'],'obf_lat':ola,'obf_lng':oln,'added':today,'is_new':True}
                    changes+=1;print(f"Nouveau {r['id']}")
                time.sleep(0.5)
    except Exception as e:print(f'Erreur:{e}')
    for d in existing.values():
        if d.get('is_new') and d.get('added'):
            try:
                if (datetime.date.today()-datetime.date.fromisoformat(d['added'])).days>30:
                    d['is_new']=False;changes+=1
            except:pass
    if changes:
        out=sorted(existing.values(),key=lambda d:int(d['id'].replace('PA_','')) if d['id'].startswith('PA_') and d['id'].replace('PA_','').isdigit() else 9999)
        with open(DATA_FILE,'w') as f:json.dump(out,f,ensure_ascii=False,separators=(',',':'))
        print(f'{changes} changements sauvegardés')
    else:print('Aucun changement')

if __name__=='__main__':main()
