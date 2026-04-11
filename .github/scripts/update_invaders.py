#!/usr/bin/env python3
"""
Auto-update data.json depuis pnote.eu/projects/invaders/map/invaders.json
Source de verite : coords + statuts (OK/damaged/destroyed/hidden)
Tourne chaque lundi via GitHub Actions.
"""
import json, math, random, datetime, sys
import urllib.request

PNOTE_URL = 'https://pnote.eu/projects/invaders/map/invaders.json?nocache=1'
DATA_FILE = 'data.json'
TODAY = datetime.date.today().isoformat()
NEW_BADGE_DAYS = 30

def fetch_pnote():
    req = urllib.request.Request(PNOTE_URL, headers={'User-Agent': 'ParisinvadersApp/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    paris = [d for d in data if d.get('id', '').startswith('PA_')]
    print(f'pnote.eu: {len(paris)} invaders Paris')
    return paris

def main():
    # Charger notre data actuel
    with open(DATA_FILE) as f:
        our_data = json.load(f)
    our_map = {d['id']: d for d in our_data}
    print(f'data.json actuel: {len(our_data)} invaders')

    # Fetch pnote
    try:
        pnote = fetch_pnote()
    except Exception as e:
        print(f'Erreur fetch pnote: {e}')
        sys.exit(0)  # Pas d erreur bloquante, on garde l existant

    pnote_map = {d['id']: d for d in pnote}
    changes = 0
    merged = []

    # Pour chaque invader pnote (source de verite coords + statuts)
    for p in pnote:
        ours = our_map.get(p['id'], {})
        entry = {
            'id': p['id'],
            'status': p['status'],
            'obf_lat': p['obf_lat'],
            'obf_lng': p['obf_lng'],
        }
        # Hint : pnote ou le notre
        hint = p.get('hint') or ours.get('hint')
        if hint: entry['hint'] = hint
        # Instagram
        ig = p.get('instagramUrl') or ours.get('instagramUrl')
        if ig: entry['instagramUrl'] = ig
        # Points (pnote n a pas les points)
        if ours.get('points'): entry['points'] = ours['points']
        # Badge nouveau
        if ours.get('is_new'): entry['is_new'] = ours['is_new']
        if ours.get('added'): entry['added'] = ours['added']

        # Tracker les changements
        if ours:
            if ours.get('status') != p['status']:
                print(f"  Status: {p['id']} {ours.get('status')} -> {p['status']}")
                changes += 1
            if abs((ours.get('obf_lat') or 0) - p['obf_lat']) > 0.0001:
                changes += 1
        else:
            print(f"  Nouveau: {p['id']}")
            entry['added'] = TODAY
            entry['is_new'] = True
            changes += 1

        merged.append(entry)

    # Garder nos invaders absents de pnote (ex: PA_1562-1568)
    for d in our_data:
        if d['id'] not in pnote_map:
            merged.append(d)
            print(f"  Preserve (absent pnote): {d['id']}")

    # Expirer badge nouveau apres 30 jours
    for d in merged:
        if d.get('is_new') and d.get('added'):
            try:
                added = datetime.date.fromisoformat(d['added'])
                if (datetime.date.today() - added).days > NEW_BADGE_DAYS:
                    d['is_new'] = False
                    changes += 1
            except: pass

    # Trier par ID numerique
    merged.sort(key=lambda d: int(d['id'].replace('PA_', '')) if d['id'].startswith('PA_') and d['id'].replace('PA_', '').isdigit() else 9999)

    if changes:
        with open(DATA_FILE, 'w') as f:
            json.dump(merged, f, ensure_ascii=False, separators=(',', ':'))
        print(f'\n{changes} changements sauvegardes. Total: {len(merged)} invaders.')
    else:
        print('Aucun changement detecte.')

if __name__ == '__main__':
    main()
