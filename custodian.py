"""Durable, synthetic withdrawal enforcement with custodian-specific receipts."""
import sqlite3
import json
import hmac
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from contextlib import closing
from revocation import Revocation, sign

@dataclass(frozen=True)
class Receipt:
    custodian: str
    contributor: str
    dataset: str
    version: int
    event_tag: str
    enforced_at: int
    tag: str

def receipt_tag(key, fields):
    return hmac.new(key, json.dumps(fields, separators=(',', ':')).encode(), hashlib.sha256).hexdigest()

class Custodian:
    """Synthetic single-scope SQLite store. Explicit provisioning; missing state denies."""
    def __init__(self, path, name, contributor, dataset, event_key, receipt_key):
        self.path = Path(path).resolve()
        self.scope = (name, contributor, dataset)
        self.event_key, self.receipt_key = event_key, receipt_key

    def connect(self):
        if not self.path.is_file():
            raise PermissionError('state unavailable')
        db = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True)
        return db

    def provision(self):
        # Exclusive creation prevents accidental reinitialisation of existing state.
        with self.path.open('xb'):
            pass
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE state (custodian TEXT, contributor TEXT, dataset TEXT, version INTEGER, revoked INTEGER, event_tag TEXT, enforced_at INTEGER)')
            db.execute('INSERT INTO state VALUES (?,?,?,1,0,NULL,NULL)', self.scope)

    def state(self, db):
        rows = db.execute('SELECT * FROM state').fetchall()
        if len(rows) != 1 or tuple(rows[0][:3]) != self.scope:
            raise PermissionError('invalid state scope')
        return rows[0]

    def read(self):
        try:
            with closing(self.connect()) as db:
                if self.state(db)[4]:
                    raise PermissionError('withdrawn')
                return {'synthetic': True}
        except sqlite3.Error as exc:
            raise PermissionError('state unavailable') from exc

    def receive(self, event, now):
        if not isinstance(event, Revocation) or (event.contributor,event.dataset) != self.scope[1:]:
            return None
        if type(now) is not int or type(event.issued) is not int or type(event.version) is not int or not 0 <= event.issued <= now:
            return None
        expected = sign(self.event_key,event.contributor,event.dataset,event.version,event.issued)
        if not isinstance(event.tag,str) or not hmac.compare_digest(expected.tag,event.tag):
            return None
        with closing(self.connect()) as db:
            with db:
                db.execute('BEGIN IMMEDIATE')
                state = self.state(db)
                if event.version < state[3]:
                    return None
                if event.version == state[3]:
                    if not state[4] or state[5] != event.tag:
                        return None
                    applied = state[6]
                else:
                    applied = now
                    db.execute('UPDATE state SET version=?,revoked=1,event_tag=?,enforced_at=?',
                               (event.version,event.tag,applied))
            # Receipt is generated only after the transaction commits.
            fields = (*self.scope,event.version,event.tag,applied)
            return Receipt(*fields,receipt_tag(self.receipt_key,fields))

def status(event, expected_keys, receipts):
    """Confirm only receipts matching this exact event and expected custodian."""
    confirmed = set()
    for r in receipts:
        if not isinstance(r,Receipt) or r.custodian not in expected_keys:
            continue
        if (r.contributor,r.dataset,r.version,r.event_tag) != (event.contributor,event.dataset,event.version,event.tag):
            continue
        if type(r.enforced_at) is not int or r.enforced_at < event.issued:
            continue
        fields = (r.custodian,r.contributor,r.dataset,r.version,r.event_tag,r.enforced_at)
        if isinstance(r.tag,str) and hmac.compare_digest(receipt_tag(expected_keys[r.custodian],fields),r.tag):
            confirmed.add(r.custodian)
    return {name: 'enforcement acknowledged' if name in confirmed else 'awaiting confirmation' for name in expected_keys}
