import unittest
from workflow_demo import run

class WorkflowTests(unittest.TestCase):
    def test_integrated_scenario(self):
        r = run()
        self.assertEqual(r['academic_before'], ['synthetic access permitted'])
        self.assertIn('community_purpose_denied', r['commercial_before'])
        self.assertIn('overdue_duty', r['overdue_obligation'])
        self.assertEqual(r['withdrawal_delivery_minute'], 12)
        self.assertEqual(r['delivery_only']['institutions']['A'], 'receipt acknowledged')
        self.assertEqual(r['delivery_only']['confirmed'], 0)
        self.assertEqual(r['partial']['confirmed'], 1)
        self.assertFalse(r['partial']['all_known_acknowledged'])
        self.assertEqual(r['access_A_after'], ['custodian denied access'])
        self.assertIn('stale_or_future_snapshot', r['access_B_stale'])
        self.assertTrue(r['all_known']['all_known_acknowledged'])
        self.assertEqual(r['access_B_after'], ['custodian denied access'])
