"""Paired synthetic stress experiment; not a field evaluation."""
import random, csv, itertools
from collections import defaultdict
from pathlib import Path

POLICIES={'persistent':None,'fixed_30':30,'fixed_120':120,'fixed_480':480,'risk_sensitive':(30,480)}

def decide(policy, age, sensitive, cached):
    limit=POLICIES[policy]
    if isinstance(limit,tuple): limit=limit[0 if sensitive else 1]
    return cached and (limit is None or age < limit)

def run(seed=20261126, n=1000):
    rng=random.Random(seed); counts=defaultdict(lambda:[0,0,0,0])
    for outage,withdraw_prob in itertools.product((60,360,1440),(.05,.25,.5)):
        for i in range(n):
            sensitive=bool(rng.getrandbits(1)); withdraw=rng.randrange(outage) if rng.random()<withdraw_prob else outage+1
            for t in sorted(rng.sample(range(outage),min(outage,30))):
                truth=t<withdraw
                for policy in POLICIES:
                    allowed=decide(policy,t,sensitive,True)
                    c=counts[outage,withdraw_prob,sensitive,policy]
                    c[0]+=not truth; c[1]+=not truth and allowed; c[2]+=truth; c[3]+=truth and not allowed
    return counts

def main():
    counts=run(); path=Path(__file__).parent/'results.csv'
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['outage_minutes','withdrawal_probability','sensitive','policy','unauthorised_requests','unauthorised_allowed','legitimate_requests','legitimate_denied'])
        for k,v in sorted(counts.items()):w.writerow([*k,*v])
    totals=defaultdict(lambda:[0]*4)
    for (*_,p),v in counts.items(): totals[p]=[a+b for a,b in zip(totals[p],v)]
    for p,(u,a,l,d) in totals.items():print(p,u,a,l,d,round(100*a/u,2),round(100*d/l,2))
if __name__=='__main__':main()
