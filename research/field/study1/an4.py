import json,csv,os,statistics as st
from collections import Counter,defaultdict
S=os.path.dirname(os.path.abspath(__file__))
def rd(p):
    with open(p) as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); return [dict(zip(h,x)) for x in r]
def med(x):
    x=[v for v in x if v is not None]; return round(st.median(x),2) if x else '-'
for grp,name in (([8,9,10,11,13,27,28],'LOST'),([12,14,6,7],'WON')):
  A=defaultdict(lambda:defaultdict(list))
  for m in grp:
    for g in range(3):
      d=f'{S}/m{m}'; sm=json.load(open(f'{d}/g{g}.summary.json'))
      us=1 if sm['teamA']=='vibe25b' else 2
      acts=rd(f'{d}/g{g}.actions.tsv'); turns=rd(f'{d}/g{g}.turns.tsv')
      typ={t['id']:t['type'] for t in turns}
      for side in (1,2):
        k='us' if side==us else 'op'
        st_=[t for t in turns if int(t['team'])==side and t['type']=='SOLDIER' and int(t['round'])<=200]
        A['soldier-turns paint<20 (r<=200) frac'][k].append(round(sum(1 for t in st_ if int(t['paint'])<20)/max(1,len(st_)),2))
        A['soldier-turns paint==0 frac'][k].append(round(sum(1 for t in st_ if int(t['paint'])==0)/max(1,len(st_)),2))
        A['withdrawals from towers (n)'][k].append(sum(1 for a in acts if int(a['team'])==side and a['action']=='transfer' and int(a['b'])<0 and typ.get(a['a'],'').endswith('TOWER')))
        A['paint given to allies by moppers'][k].append(sum(int(a['b']) for a in acts if int(a['team'])==side and a['action']=='transfer' and int(a['b'])>0 and a['type']=='MOPPER'))
        A['soldier-turns r<=200'][k].append(len(st_))
        # robot turns avg per round
  print('==',name)
  for kk,v in A.items(): print(f"{kk:<40} us {med(v['us']):>6} op {med(v.get('op',[])):>6}  us{v['us']} op{v.get('op')}")
