# Revocation transport under constrained connectivity

The study compares FIFO upload scheduling with revocation-first scheduling under an identical finite byte budget at each contact. Each policy is evaluated with and without a 120-minute access expiry. The message size is calculated from its serialized representation. A withdrawal cannot be delivered before it exists; partial transmissions accumulate across contacts.

Each synthetic episode shares its withdrawal time, queued upload size, contact times and per-contact capacity across all four policies. One synthetic access attempt occurs per minute. The gateway processes received revocation before reads at that minute. Outcomes are delivery latency, post-withdrawal reads permitted and pre-withdrawal reads denied. Report delivery counts alongside conditional mean latency; an undelivered event is not a zero-latency event.

The simulator assumes a trusted initial grant and a shared symmetric key. It checks message integrity, scope, version and clock ordering. It does not implement key distribution, identity proofing, real network delivery, durable queues, packet loss, retransmission acknowledgements or a production security boundary. The transport experiment isolates the revocation mechanism; it does not integrate the collective-governance and obligation rules of the original reference model.

Priority scheduling can delay ordinary uploads. The extended experiment tracks completion times, unfinished uploads and remaining bytes under the same per-contact byte budget. Completion times are conditional on completion within the 1,440-minute horizon; unfinished transfers are reported separately. The experiment does not quantify access retry completion or participant-level exclusion. It is a controlled mechanistic comparison rather than evidence that prioritisation is novel or universally beneficial. No patient data are used.

## Reproduction

Run `python -m unittest -v` and `python transport_experiment.py` from the repository root using Python 3.10 or later. The default seed is 20261126 and the default sample is 1,000 paired synthetic episodes.
