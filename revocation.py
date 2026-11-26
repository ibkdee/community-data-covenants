"""Local, synthetic-only consent enforcement and revocation transport model."""
from dataclasses import dataclass
import hashlib
import hmac
import json

@dataclass(frozen=True)
class Revocation:
    contributor: str
    dataset: str
    version: int
    issued: int
    tag: str

def payload(contributor, dataset, version, issued):
    return json.dumps([contributor, dataset, version, issued], separators=(',', ':')).encode()

def sign(key, contributor, dataset, version, issued):
    tag = hmac.new(key, payload(contributor, dataset, version, issued), hashlib.sha256).hexdigest()
    return Revocation(contributor, dataset, version, issued, tag)

class Gateway:
    """In-memory synthetic gateway; time in integer minutes, supplied by simulator."""
    def __init__(self, contributor, dataset, key, expiry=None):
        self.contributor, self.dataset = contributor, dataset
        self.key, self.expiry = key, expiry
        self.version, self.revoked, self.clock = 1, False, 0

    def advance(self, now):
        if type(now) is not int or now < self.clock:
            raise ValueError('non-monotonic clock')
        self.clock = now

    def receive(self, event, now):
        self.advance(now)
        if (event.contributor, event.dataset) != (self.contributor, self.dataset):
            return False
        if type(event.version) is not int or type(event.issued) is not int or event.version <= self.version or not 0 <= event.issued <= now:
            return False
        expected = sign(self.key, event.contributor, event.dataset, event.version, event.issued)
        if not hmac.compare_digest(expected.tag, event.tag):
            return False
        self.version, self.revoked = event.version, True
        return True

    def read(self, contributor, dataset, now):
        self.advance(now)
        if (contributor, dataset) != (self.contributor, self.dataset) or self.revoked:
            raise PermissionError('scope or consent')
        if self.expiry is not None and now >= self.expiry:
            raise PermissionError('expired')
        return {'synthetic': True}

def delivery_time(withdrawal, contacts, backlog_bytes, capacity_bytes, priority, message_bytes):
    """One shared contact trace; FIFO backlog or revocation-first scheduling.
    A revocation can be sent only after it exists. Partial messages accumulate.
    """
    remaining = message_bytes
    backlog = backlog_bytes
    for t in contacts:
        if t < withdrawal:
            backlog = max(0, backlog-capacity_bytes)
            continue
        usable = capacity_bytes
        if not priority:
            served = min(backlog, usable)
            backlog -= served
            usable -= served
        remaining -= usable
        if remaining <= 0:
            return t
    return None
