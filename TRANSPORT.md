# Revocation transport under constrained connectivity

The study compares FIFO upload scheduling with revocation-first scheduling under an identical finite byte budget at each contact. Each policy is evaluated with and without a 120-minute access expiry. The message size is calculated from its serialised representation. A withdrawal cannot be delivered before it exists; partial transmissions accumulate across contacts.

Each synthetic episode shares its withdrawal time, queued upload size, contact times and per-contact capacity across all four policies. One synthetic access attempt occurs per minute. The gateway processes received revocation before reads at that minute. Outcomes are delivery latency, post-withdrawal reads permitted and pre-withdrawal reads denied. Delivery counts are reported alongside mean latency for successfully delivered messages. Undelivered messages are excluded from the latency mean.

The simulator assumes a trusted initial grant and a shared symmetric key. It checks message integrity, scope, version and clock ordering. It does not implement key distribution, identity proofing, real network delivery, durable queues, packet loss, retransmission acknowledgements or a production security boundary. The transport experiment isolates the revocation mechanism; it does not integrate the collective-governance and obligation rules of the original reference model.

Priority scheduling can delay ordinary uploads. The extended experiment tracks completion times, unfinished uploads and remaining bytes under the same per-contact byte budget. Completion times are conditional on completion within the 1,440-minute horizon; unfinished transfers are reported separately. The experiment does not quantify access retry completion or participant-level exclusion. It is a controlled mechanistic comparison rather than evidence that prioritisation is novel or universally beneficial. No patient data are used.

## Reproduction

Run `python -m unittest -v` and `python transport_experiment.py` from the repository root using Python 3.10 or later. The default seed is 20261126 and the default sample is 1,000 paired synthetic episodes.

## Results

| Policy | Revocations delivered / 1,000 | Mean delivery latency among delivered (min) | Mean post-withdrawal reads per episode | Mean pre-withdrawal denials per episode | Uploads completed / 1,000 | Mean upload completion time among completed (min) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FIFO | 884 | 310.30 | 421.10 | 0.00 | 884 | 389.74 |
| Revocation-first | 1,000 | 73.93 | 73.93 | 0.00 | 884 | 417.88 |
| FIFO + expiry | 884 | 310.30 | 18.11 | 78.25 | 884 | 389.74 |
| Revocation-first + expiry | 1,000 | 73.93 | 13.19 | 78.25 | 884 | 417.88 |

Revocation-first scheduling reduces mean post-withdrawal reads by approximately 82.4% relative to FIFO without expiry. Mean upload completion time among completed uploads increases by 28.14 minutes. Both policies complete 884 uploads; the mean pending upload bytes increase from 638.46 to 653.86. Conditional delivery latency comparisons involve different sets of completed revocations, so they are not paired causal estimates. The synthetic scenario uses a single withdrawal per episode and a fixed initial upload backlog; priority scheduling is not claimed to be a novel scheduling algorithm.

[Machine-readable results](transport-results.csv). Executed from source matching Git blobs `4ccd272b905f98c377aa406bf64424b9e9ce6ead` (gateway and scheduler) and `74ce21244e0a186fb2b570220d2bd69958e4f649` (experiment).
