import json,csv,os,ast,statistics as st
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
      d=f'{S}/m{m}'; sm=json.load(open(f'{d}/g{g}.summary.json')); meta=json.load(open(f'{d}/g{g}.meta.json'))
      us=1 if sm['teamA']=='vibe25b' else 2
      ruins=[tuple(r) for r in (meta['ruins'] if isinstance(meta['ruins'],list) else ast.literal_eval(meta['ruins']))]
      acts=rd(f'{d}/g{g}.actions.tsv'); turns=rd(f'{d}/g{g}.turns.tsv')
      loc={}
      for t in turns:
        if t['id'] not in loc: loc[t['id']]=(int(t['x']),int(t['y']))
      init=[(int(t['x']),int(t['y']),int(t['team'])) for t in turns if t['round']=='1' and 'TOWER' in t['type']]
      firstmark={}; built={}
      for a in acts:
        if a['action']=='mark':
          x,y=map(int,a['a'].split(','))
          for r in ruins:
            if max(abs(r[0]-x),abs(r[1]-y))<=2:
              firstmark.setdefault((r,int(a['team'])),int(a['round']))
        if a['action']=='spawn' and 'TOWER' in a['b']:
          x,y=map(int,a['c'].split(','))
          if (x,y) in ruins: built.setdefault((x,y),[]).append((int(a['round']),int(a['team'])))
      for side in (1,2):
        k='us' if side==us else 'op'
        lat=[];aband=0;stolen=0
        for (r,tm),fr in firstmark.items():
          if tm!=side: continue
          b=[x for x in built.get(r,[]) if x[0]>=fr]
          if b and b[0][1]==side: lat.append(b[0][0]-fr)
          elif b: stolen+=1
          else: aband+=1
        A['ruins marked'][k].append(sum(1 for (r,tm) in firstmark if tm==side))
        A['median mark->build latency'][k].append(med(lat) if lat else None)
        A['marked, never built'][k].append(aband)
        A['marked, enemy built'][k].append(stolen)
        sx=[(x,y) for x,y,t in init if t==side]; ex=[(x,y) for x,y,t in init if t!=side]
        nb=0; far=0; rr=[]
        for r,L in built.items():
          for rd_,tm in L:
            if tm==side and rd_<=200:
              nb+=1
              ds=min((r[0]-a)**2+(r[1]-b)**2 for a,b in sx); de=min((r[0]-a)**2+(r[1]-b)**2 for a,b in ex)
              if de<ds: far+=1
        A['ruin builds<=200'][k].append(nb); A['  of which on enemy half'][k].append(far)
      A['ruins on map'][k].append(len(ruins)) if False else A['ruins on map']['us'].append(len(ruins))
  print('==',name)
  for kk,v in A.items(): print(f"{kk:<30} us {med(v['us']):>6} op {med(v.get('op',[])):>6}  us{v['us']} op{v.get('op')}")
