"""End-to-end synthetic scenario; no real data or network access."""
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from pathlib import Path
from covenant import Consent, Duty, Request, evaluate
from custodian import Custodian
from assurance import assurance, delivery_ack
from revocation import sign, schedule
from dataclasses import asdict
import json


def run():
    epoch = datetime(2026, 1, 1, tzinfo=timezone.utc)
    event_key = b'synthetic event key'
    keys = {'A': b'synthetic A key', 'B': b'synthetic B key'}
    consent = Consent(1, True, frozenset({'academic', 'commercial_ai'}))
    community = {'academic'}
    event = sign(event_key, 'p1', 'd1', 2, 10)
    size = len(json.dumps(asdict(event), separators=(',', ':')).encode())
    delivered, _, _, _ = schedule(10, [12, 20], 512, 512, True, size)
    with TemporaryDirectory() as folder:
        stores = {name: Custodian(Path(folder)/(name+'.db'), name, 'p1', 'd1', event_key, key) for name, key in keys.items()}
        for store in stores.values():
            store.provision()
        def access(name, purpose, minute, snapshot, duties=()):
            now = epoch + timedelta(minutes=minute)
            decision = evaluate(Request(name, 'd1', purpose, 1, 1), consent, community, 1, duties, now, snapshot_at=epoch+timedelta(minutes=snapshot), approved_recipient=True)
            if not decision.allowed:
                return list(decision.reasons)
            try:
                stores[name].read()
                return ['synthetic access permitted']
            except PermissionError:
                return ['custodian denied access']
        result = {'academic_before': access('A','academic',9,9), 'commercial_before': access('A','commercial_ai',9,9), 'overdue_obligation': access('A','academic',9,9,[Duty('A','d1',epoch)])}
        result['withdrawal_delivery_minute'] = delivered
        d = delivery_ack(event, 'A', delivered, keys['A'])
        result['delivery_only'] = assurance(event,event_key,keys,[d],[],delivered)
        r = stores['A'].receive(event, delivered)
        result['partial'] = assurance(event,event_key,keys,[d],[r],delivered)
        result['access_A_after'] = access('A','academic',delivered,9)
        result['access_B_stale'] = access('B','academic',20,9)
        b = stores['B'].receive(event,20)
        result['all_known'] = assurance(event,event_key,keys,[d],[r,b],20)
        result['access_B_after'] = access('B','academic',20,20)
        return result

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
