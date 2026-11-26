from datetime import datetime, timezone, timedelta
from covenant import Consent, Duty, Request, evaluate

def main():
    now = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)
    request = Request("researcher", "synthetic-a", "academic", 1, 1)
    baseline = dict(request=request, consent=Consent(1, True, frozenset({"academic"})),
                    community_purposes={"academic"}, policy_version=1, duties=[],
                    now=now, snapshot_at=now, approved_recipient=True)
    scenarios = [
        ("Current consent", {}, True),
        ("Individual withdrawal", {"consent": Consent(1, False, frozenset())}, False),
        ("Community restriction", {"community_purposes": set()}, False),
        ("Stale consent", {"snapshot_at": now-timedelta(minutes=6)}, False),
        ("Overdue obligation", {"duties": [Duty("researcher", "synthetic-a", now)]}, False),
    ]
    for title, changes, expected in scenarios:
        decision = evaluate(**(baseline | changes))
        assert decision.allowed == expected, title
        print(title, "|", "ALLOW" if decision.allowed else "DENY",
              "|", decision.expires.isoformat() if decision.expires else ", ".join(decision.reasons))

if __name__ == "__main__":
    main()
