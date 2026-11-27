import unittest
from dataclasses import replace
from tempfile import TemporaryDirectory
from pathlib import Path
from assurance import assurance, delivery_ack
from custodian import Custodian
from revocation import sign

class AssuranceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.key = b'example event key'
        self.keys = {'A': b'example A', 'B': b'example B'}
        self.event = sign(self.key, 'p1', 'd1', 2, 10)
        self.a = Custodian(Path(self.tmp.name)/'a.db', 'A', 'p1', 'd1', self.key, self.keys['A'])
        self.a.provision()
    def view(self, deliveries=(), receipts=(), now=30, keys=None):
        return assurance(self.event, self.key, self.keys if keys is None else keys, deliveries, receipts, now)
    def test_three_states(self):
        d = delivery_ack(self.event, 'B', 15, self.keys['B'])
        self.assertEqual(self.view([d])['institutions'], {'A':'awaiting confirmation','B':'receipt acknowledged'})
        r = self.a.receive(self.event, 20)
        self.assertEqual(self.view([d],[r])['confirmed'], 1)
        self.assertFalse(self.view([d],[r])['all_known_acknowledged'])
    def test_empty_scope(self):
        self.assertFalse(self.view(keys={})['all_known_acknowledged'])
    def test_forged_delivery(self):
        d = delivery_ack(self.event, 'B', 15, self.keys['A'])
        self.assertEqual(self.view([d])['institutions']['B'], 'awaiting confirmation')
    def test_future_enforcement(self):
        r = self.a.receive(self.event, 40)
        self.assertEqual(self.view(receipts=[r])['confirmed'], 0)
    def test_duplicate_and_scope(self):
        r = self.a.receive(self.event, 20)
        self.assertEqual(self.view(receipts=[r,r,replace(r,custodian='B')])['confirmed'], 1)
        self.assertTrue(self.view(receipts=[r],keys={'A':self.keys['A']})['all_known_acknowledged'])
    def test_invalid_event(self):
        with self.assertRaises(ValueError):
            assurance(replace(self.event, issued=11), self.key, self.keys, [], [], 30)
    def test_future_delivery(self):
        d = delivery_ack(self.event, 'A', 40, self.keys['A'])
        self.assertEqual(self.view([d])['institutions']['A'], 'awaiting confirmation')
    def test_no_downgrade(self):
        r = self.a.receive(self.event, 20)
        d = delivery_ack(self.event, 'A', 15, self.keys['A'])
        self.assertEqual(self.view([d],[r])['institutions']['A'], 'enforcement acknowledged')

if __name__ == '__main__':
    unittest.main()
