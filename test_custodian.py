import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import replace
from custodian import Custodian, status
from revocation import sign

class CustodianTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.key = b'synthetic event key'
        self.keys = {'A': b'synthetic A key', 'B': b'synthetic B key'}
        self.event = sign(self.key,'p1','d1',2,10)
        self.a = self.make('A')
        self.b = self.make('B')
        self.a.provision()
        self.b.provision()

    def make(self, name):
        return Custodian(Path(self.tmp.name)/(name+'.sqlite'),name,'p1','d1',self.key,self.keys[name])

    def test_restart(self):
        self.a.read()
        self.a.receive(self.event,20)
        with self.assertRaises(PermissionError):
            self.make('A').read()

    def test_missing_state(self):
        self.a.path.unlink()
        with self.assertRaises(PermissionError):
            self.a.read()

    def test_no_reprovision(self):
        self.a.receive(self.event,20)
        with self.assertRaises(FileExistsError):
            self.make('A').provision()

    def test_partial_confirmation(self):
        receipt = self.a.receive(self.event,20)
        self.assertEqual(status(self.event,self.keys,[receipt]),{'A':'enforcement acknowledged','B':'awaiting confirmation'})
        self.b.read()

    def test_both_confirmed(self):
        receipts = [self.a.receive(self.event,20),self.b.receive(self.event,30)]
        self.assertEqual(set(status(self.event,self.keys,receipts).values()),{'enforcement acknowledged'})

    def test_retry_idempotent(self):
        self.assertEqual(self.a.receive(self.event,20),self.make('A').receive(self.event,30))

    def test_forged_receipt(self):
        r = self.a.receive(self.event,20)
        self.assertEqual(status(self.event,self.keys,[replace(r,custodian='B')])['B'],'awaiting confirmation')

    def test_wrong_event(self):
        r = self.a.receive(self.event,20)
        other = sign(self.key,'p1','d1',3,21)
        self.assertEqual(status(other,self.keys,[r])['A'],'awaiting confirmation')

    def test_modified_withdrawal(self):
        self.assertIsNone(self.a.receive(replace(self.event,issued=11),20))
        self.a.read()

    def test_future_event(self):
        self.assertIsNone(self.a.receive(self.event,9))

    def test_older_version(self):
        self.a.receive(sign(self.key,'p1','d1',3,10),20)
        self.assertIsNone(self.a.receive(self.event,30))

    def test_duplicate_receipt(self):
        r = self.a.receive(self.event,20)
        self.assertEqual(list(status(self.event,self.keys,[r,r]).values()).count('enforcement acknowledged'),1)

if __name__ == '__main__':
    unittest.main()
