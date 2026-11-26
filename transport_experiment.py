"""Paired comparison using the actual synthetic gateway and transport model."""
from random import Random
from statistics import mean
from revocation import Gateway, sign, schedule

KEY = b'synthetic demonstration key'
POLICIES = [('FIFO', False, None), ('Priority', True, None),
            ('FIFO + expiry', False, 120), ('Priority + expiry', True, 120)]

def run(seed=20261126, episodes=1000):
    rng = Random(seed)
    results = {name: [] for name, _, _ in POLICIES}
    for _ in range(episodes):
        withdrawal = rng.randrange(1, 360)
        contacts = sorted(rng.sample(range(1, 720), 12)) + list(range(720, 1441, 10))
        backlog = rng.choice([512, 4096, 16384])
        capacity = rng.choice([128, 512, 2048])
        event = sign(KEY, 'p1', 'd1', 2, withdrawal)
        # Count the encoded event, not an invented fixed message length.
        import json
        from dataclasses import asdict
        size = len(json.dumps(asdict(event), separators=(',', ':')).encode())
        for name, priority, expiry in POLICIES:
            delivered, upload_done, upload_left, control_left = schedule(withdrawal, contacts, backlog, capacity, priority, size)
            gateway = Gateway('p1', 'd1', KEY, expiry)
            allowed_after, denied_before = 0, 0
            for minute in range(1441):
                if minute == delivered:
                    assert gateway.receive(event, minute)
                try:
                    gateway.read('p1', 'd1', minute)
                    allowed_after += minute >= withdrawal
                except PermissionError:
                    denied_before += minute < withdrawal
            results[name].append((delivered-withdrawal if delivered is not None else None,
                                  allowed_after, denied_before, upload_done, upload_left, control_left))
    return results

if __name__ == '__main__':
    print('policy,delivered,mean_latency_minutes,mean_post_withdrawal_reads,mean_pre_withdrawal_denials,uploads_completed,mean_upload_completion_minutes,mean_upload_bytes_pending')
    for name, rows in run().items():
        latency = [r[0] for r in rows if r[0] is not None]
        uploads = [r[3] for r in rows if r[3] is not None]
        latency_text = f'{mean(latency):.2f}' if latency else 'NA'
        upload_text = f'{mean(uploads):.2f}' if uploads else 'NA'
        print(f'{name},{len(latency)},{latency_text},{mean(r[1] for r in rows):.2f},{mean(r[2] for r in rows):.2f},{len(uploads)},{upload_text},{mean(r[4] for r in rows):.2f}')
