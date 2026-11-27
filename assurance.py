"""Synthetic contributor-facing summary of authenticated custodian acknowledgements."""
from dataclasses import dataclass
import hmac
from custodian import Receipt, receipt_tag, status
from revocation import Revocation, sign

@dataclass(frozen=True)
class Delivery:
    custodian: str
    event_tag: str
    received_at: int
    tag: str

def delivery_ack(event, custodian, received_at, key):
    """Model a trusted receiver attesting to delivery; not a network operation."""
    if type(received_at) is not int or received_at < event.issued:
        raise ValueError('invalid receipt time')
    fields = ('delivery-v1', custodian, event.tag, received_at)
    return Delivery(custodian, event.tag, received_at, receipt_tag(key, fields))

def assurance(event, event_key, expected_keys, deliveries, receipts, now):
    """Report only verified evidence within the caller-supplied custodian scope."""
    if not isinstance(event, Revocation) or type(now) is not int:
        raise ValueError('invalid event or clock')
    if type(event.issued) is not int or type(event.version) is not int or not 0 <= event.issued <= now or event.version < 2:
        raise ValueError('invalid event version or time')
    if not isinstance(event.tag, str) or not hmac.compare_digest(event.tag, sign(event_key, event.contributor, event.dataset, event.version, event.issued).tag):
        raise ValueError('invalid withdrawal authentication')
    verified = status(event, expected_keys, [r for r in receipts if isinstance(r, Receipt) and type(r.enforced_at) is int and r.enforced_at <= now])
    for d in deliveries:
        if not isinstance(d, Delivery) or d.custodian not in expected_keys or d.event_tag != event.tag:
            continue
        if type(d.received_at) is not int or not event.issued <= d.received_at <= now:
            continue
        fields = ('delivery-v1', d.custodian, d.event_tag, d.received_at)
        if isinstance(d.tag, str) and hmac.compare_digest(d.tag, receipt_tag(expected_keys[d.custodian], fields)) and verified[d.custodian] == 'awaiting confirmation':
            verified[d.custodian] = 'receipt acknowledged'
    count = sum(v == 'enforcement acknowledged' for v in verified.values())
    return {'institutions': verified, 'confirmed': count, 'known': len(verified), 'all_known_acknowledged': bool(verified) and count == len(verified)}
