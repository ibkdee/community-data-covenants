"""Synthetic-only reference decision model; not an access-control service."""
from dataclasses import dataclass
from datetime import datetime, timedelta

PURPOSES = frozenset({'academic', 'noncommercial_ai', 'commercial_ai'})

@dataclass(frozen=True)
class Consent:
    version: int
    active: bool
    purposes: frozenset[str]

@dataclass(frozen=True)
class Duty:
    recipient: str
    dataset: str
    due: datetime
    verified: bool = False

@dataclass(frozen=True)
class Request:
    recipient: str
    dataset: str
    purpose: str
    consent_version: int
    policy_version: int

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reasons: tuple[str, ...]
    expires: datetime | None = None

def evaluate(request, consent, community_purposes, policy_version, duties, now, *, snapshot_at, conflict=False, approved_recipient=False):
    """Pure policy check; caller supplies trusted inputs. No real data released."""
    reasons = []
    if not approved_recipient: reasons.append('recipient_not_approved')
    if conflict: reasons.append('unresolved_consent_conflict')
    if not timedelta(0) <= now-snapshot_at <= timedelta(minutes=5): reasons.append('stale_or_future_snapshot')
    if request.consent_version != consent.version or request.policy_version != policy_version: reasons.append('version_mismatch')
    if not consent.active: reasons.append('withdrawn')
    if request.purpose not in PURPOSES or request.purpose not in consent.purposes: reasons.append('individual_purpose_denied')
    if request.purpose not in community_purposes: reasons.append('community_purpose_denied')
    relevant = [d for d in duties if (d.recipient,d.dataset)==(request.recipient,request.dataset) and not d.verified]
    if any(d.due <= now for d in relevant): reasons.append('overdue_duty')
    if reasons: return Decision(False,tuple(reasons))
    expiry = min([now+timedelta(minutes=1), snapshot_at+timedelta(minutes=5)]+[d.due for d in relevant])
    if expiry <= now: return Decision(False,('no_valid_lease',))
    return Decision(True,(),expiry)
