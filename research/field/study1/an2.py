import json,csv,os,statistics as st
from collections import Counter,defaultdict
S=os.path.dirname(os.path.abspath(__file__))
TOW={'PAINT_TOWER','MONEY_TOWER','DEFENSE_TOWER'}
def rd(p):
    with open(p) as f:
        r=csv.reader(f,delimiter='\t'); h=next(r); return [dict(zip(h,x)) for x in r]
def med(x):
    x=[v for v in x if v is not None]; return round(st.median(x),1) if x else '-'
for grp,name in (([8,9,10,11,13,27,28],'LOST'),([12,14,6,7],'WON')):
  agg=defaultdict(lambda:defaultdict(list))
  for m in grp:
    for g in range(3):
      d=f'{S}/m{m}'; sm=json.load(open(f'{d}/g{g}.summary.json'))
      us=1 if sm['teamA']=='vibe25b' else 2
      acts=rd(f'{d}/g{g}.actions.tsv'); turns=rd(f'{d}/g{g}.turns.tsv')
      team={};typ={}
      for t in turns: team[t['id']]=int(t['team']); typ[t['id']]=t['type']
      # tower paint stock at checkpoints
      last={}
      tp={}
      ti=0
      for R in (50,100,150,200,300):
        while ti<len(turns) and int(turns[ti]['round'])<=R:
          t=turns[ti]; ti+=1
          last[t['id']]=t
        for side in (1,2):
          s=sum(int(t['paint']) for i,t in last.items() if t['type'] in TOW and int(t['team'])==side and int(t['round'])>=R-1)
          if R<=sm['rounds']: agg[f'towerpaint r{R}']['us' if side==us else 'op'].append(s)
      # mopper paint drain on enemy robots (damage by moppers to robots)
      c=Counter(); ta=Counter(); spawns=defaultdict(Counter)
      for a in acts:
        tm=int(a['team']); r=int(a['round'])
        if a['action']=='damage' and a['type']=='MOPPER' and typ.get(a['a']) not in TOW: c[tm]+=int(a['b'])
        if a['action']=='attack' and a['type'] in TOW and typ.get(a['a'])!=None: ta[tm]+=1
        if a['action']=='spawn' and a['b'] in ('SOLDIER','SPLASHER','MOPPER'): spawns[tm][min(r//100,4)]+=1
      for side in (1,2):
        k='us' if side==us else 'op'
        agg['mopper paint drained from enemy robots'][k].append(c[side])
        agg['tower attacks'][k].append(ta[side])
        for b in range(4):
          if b*100<sm['rounds']: agg[f'robot spawns r{b*100}-{b*100+99}'][k].append(spawns[side][b])
      # our robot deaths: round histogram, paint-at-death standing on enemy paint unknown
      dr=[int(a['round']) for a in acts if a['action']=='die' and team.get(a['a'])==us and a['c'] not in TOW]
      agg['our robot deaths <=100']['us'].append(sum(1 for x in dr if x<=100))
      # first tower loss
      fl={1:None,2:None}
      for a in acts:
        if a['action']=='die' and a['c'] in TOW and team.get(a['a']) in (1,2):
          s=team[a['a']]
          if fl[s] is None: fl[s]=int(a['round'])
      agg['first own tower lost']['us'].append(fl[us]); agg['first own tower lost']['op'].append(fl[3-us])
  print('==',name)
  for k,v in agg.items(): print(f"{k:<42} us {med(v['us']):>7} op {med(v.get('op',[])):>7}  us{v['us']} op{v.get('op')}")
