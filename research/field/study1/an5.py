import json,csv,os,statistics as st
from collections import Counter,defaultdict
S=os.path.dirname(os.path.abspath(__file__))
def rd(p):
    with open(p) as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); return [dict(zip(h,x)) for x in r]
def med(x):
    x=[v for v in x if v is not None]; return round(st.median(x),1) if x else '-'
for grp,name in (([8,9,10,11,13,27,28],'LOST'),([12,14,6,7],'WON')):
  A=defaultdict(lambda:defaultdict(list))
  for m in grp:
    for g in range(3):
      d=f'{S}/m{m}'; sm=json.load(open(f'{d}/g{g}.summary.json'))
      us=1 if sm['teamA']=='vibe25b' else 2
      acts=rd(f'{d}/g{g}.actions.tsv'); turns=rd(f'{d}/g{g}.turns.tsv')
      typ={t['id']:t['type'] for t in turns}
      # tower positions alive per round
      towers=defaultdict(dict) # round-> not needed; keep current
      cur={}
      byr=defaultdict(list)
      for t in turns: byr[int(t['round'])].append(t)
      dist=defaultdict(list); enemyp=defaultdict(int)
      for r in sorted(byr):
        if r>200: break
        for t in byr[r]:
          if t['type'].endswith('TOWER'): cur[t['id']]=(int(t['team']),int(t['x']),int(t['y']),r)
        for t in byr[r]:
          if t['type']=='SOLDIER' and int(t['paint'])==0:
            tm=int(t['team']); x,y=int(t['x']),int(t['y'])
            ds=[ (x-a)**2+(y-b)**2 for (tt,a,b,lr) in cur.values() if tt==tm and lr>=r-1]
            if ds: dist[tm].append(min(ds)**.5)
      for side in (1,2):
        k='us' if side==us else 'op'
        A['withdrawals r<=100'][k].append(sum(1 for a in acts if int(a['round'])<=100 and int(a['team'])==side and a['action']=='transfer' and int(a['b'])<0))
        A['dist 0-paint soldier to own tower'][k].append(med(dist[side]) if dist[side] else None)
  print('==',name)
  for kk,v in A.items(): print(f"{kk:<40} us {med(v['us']):>6} op {med(v.get('op',[])):>6}  us{v['us']} op{v.get('op')}")
