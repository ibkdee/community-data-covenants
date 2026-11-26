import unittest
from datetime import datetime, timezone, timedelta
from covenant import Consent, Duty, Request, evaluate
from experiment import run, decide

class CovenantTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,26,tzinfo=timezone.utc)
        self.consent=Consent(1,True,frozenset({'academic'}))
        self.request=Request('researcher','synthetic-a','academic',1,1)
    def check(self, **kwargs):
        defaults=dict(request=self.request,consent=self.consent,community_purposes={'academic'},policy_version=1,duties=[],now=self.now,snapshot_at=self.now,approved_recipient=True)
        defaults.update(kwargs)
        return evaluate(**defaults)
    def test_valid(self): self.assertTrue(self.check().allowed)
    def test_withdrawal(self): self.assertFalse(self.check(consent=Consent(1,False,frozenset())).allowed)
    def test_community_veto(self): self.assertFalse(self.check(community_purposes=set()).allowed)
    def test_conflict(self): self.assertFalse(self.check(conflict=True).allowed)
    def test_stale(self): self.assertFalse(self.check(snapshot_at=self.now-timedelta(minutes=6)).allowed)
    def test_future(self): self.assertFalse(self.check(snapshot_at=self.now+timedelta(seconds=1)).allowed)
    def test_recipient(self): self.assertFalse(self.check(approved_recipient=False).allowed)
    def test_version(self): self.assertFalse(self.check(policy_version=2).allowed)
    def test_overdue(self): self.assertFalse(self.check(duties=[Duty('researcher','synthetic-a',self.now)]).allowed)
    def test_verified(self): self.assertTrue(self.check(duties=[Duty('researcher','synthetic-a',self.now,True)]).allowed)
    def test_unrelated(self): self.assertTrue(self.check(duties=[Duty('other','synthetic-a',self.now)]).allowed)
    def test_expiry(self): self.assertEqual(self.check().expires,self.now+timedelta(minutes=1))
    def test_duty_expiry(self): self.assertEqual(self.check(duties=[Duty('researcher','synthetic-a',self.now+timedelta(seconds=30))]).expires,self.now+timedelta(seconds=30))
    def test_individual_veto(self): self.assertFalse(self.check(request=Request('researcher','synthetic-a','commercial_ai',1,1),community_purposes={'commercial_ai'}).allowed)

class ExperimentTests(unittest.TestCase):
    def test_boundary(self): self.assertFalse(decide('fixed_30',30,True,True))
    def test_cached_veto(self): self.assertFalse(decide('persistent',0,False,False))
    def test_reproducible(self): self.assertEqual(run(n=5),run(n=5))
    def test_counts(self):
        c=run(n=5)
        self.assertEqual(sum(v[0]+v[2] for k,v in c.items() if k[-1]=='persistent'),9*5*30)
        for u,a,l,d in c.values():
            self.assertTrue(0<=a<=u and 0<=d<=l)

if __name__=='__main__': unittest.main()
