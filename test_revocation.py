import unittest
from dataclasses import replace
from revocation import Gateway, sign, delivery_time, schedule
from transport_experiment import run

class RevocationTests(unittest.TestCase):
    def setUp(self):
        self.key = b'test'
        self.g = Gateway('p1','d1',self.key,120)
        self.event = sign(self.key,'p1','d1',2,10)

    def test_scope(self):
        with self.assertRaises(PermissionError):
            self.g.read('p2','d1',0)

    def test_dataset(self):
        with self.assertRaises(PermissionError):
            self.g.read('p1','d2',0)

    def test_revocation(self):
        self.assertTrue(self.g.receive(self.event,20))
        with self.assertRaises(PermissionError):
            self.g.read('p1','d1',20)

    def test_replay(self):
        self.assertTrue(self.g.receive(self.event,20))
        self.assertFalse(self.g.receive(self.event,21))

    def test_tamper(self):
        self.assertFalse(self.g.receive(replace(self.event,issued=11),20))
        self.assertTrue(self.g.read('p1','d1',20))

    def test_wrong_scope(self):
        self.assertFalse(self.g.receive(sign(self.key,'p2','d1',2,10),20))

    def test_future(self):
        self.assertFalse(self.g.receive(self.event,9))

    def test_expiry(self):
        self.g.read('p1','d1',119)
        with self.assertRaises(PermissionError):
            self.g.read('p1','d1',120)

    def test_clock(self):
        self.g.read('p1','d1',10)
        with self.assertRaises(ValueError):
            self.g.read('p1','d1',9)

    def test_priority(self):
        args=(10,[10,20,30],200,100)
        self.assertEqual(delivery_time(*args,True,50),10)
        self.assertEqual(delivery_time(*args,False,50),30)

    def test_partial(self):
        self.assertEqual(delivery_time(10,[10,20],0,100,True,150),20)

    def test_no_contact(self):
        self.assertIsNone(delivery_time(10,[1,2],0,100,True,50))

    def test_shared_budget(self):
        self.assertEqual(schedule(10,[10,20,30],200,100,True,50),(10,30,0,0))
        self.assertEqual(schedule(10,[10,20,30],200,100,False,50),(30,20,0,0))

    def test_censored_upload(self):
        self.assertEqual(schedule(10,[10],200,100,True,50),(10,None,150,0))

    def test_no_prewithdrawal_control(self):
        self.assertEqual(schedule(20,[10],0,100,True,50),(None,0,0,50))

    def test_paired_experiment(self):
        result=run(episodes=10)
        for fifo, priority in zip(result['FIFO'],result['Priority']):
            if fifo[0] is not None:
                self.assertIsNotNone(priority[0])
                self.assertLessEqual(priority[0],fifo[0])
            self.assertLessEqual(priority[1],fifo[1])
            self.assertEqual(priority[2],fifo[2])

if __name__ == '__main__':
    unittest.main()
