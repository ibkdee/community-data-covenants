# Consent Assurance Receipt

A contributor-facing view of withdrawal progress across known participating institutions.

The current custodian implementation generates an authenticated enforcement acknowledgement after committing withdrawal state to its local database. The reference receipt model in [assurance.py](assurance.py) extends that mechanism into a readable account of institutional responses.

## Status semantics

- **Awaiting confirmation:** no valid acknowledgement has been verified. This does not establish that the institution is offline or has failed to act.
- **Receipt acknowledged:** an authenticated delivery acknowledgement is available, but enforcement is not yet confirmed. This is implemented as a trusted synthetic receiver attestation, not actual network delivery.
- **Enforcement acknowledged:** the existing local custodian model reports committed withdrawal state.
- **All known custodians acknowledged:** every member of the specified, non-empty custodian set has supplied a matching enforcement acknowledgement.

An acknowledgement is not independent proof of deletion, downstream compliance or removal of influence from trained models. The custodian set is supplied by the caller; completeness is not independently established.

## Historical evidence and scope

An authenticated enforcement acknowledgement reports the time at which a participating custodian committed withdrawal. It does not establish current state after a database rollback, a later policy change or an unauthorised export. A missing acknowledgement is uncertainty, not proof of non-compliance. Irreversibly anonymised records may no longer be linkable to a contributor. The [end-to-end scenario](workflow_demo.py) demonstrates the current reference components under trusted synthetic inputs.

## Research direction

Evaluate comprehension of the receipt, accessibility for contributors with limited digital literacy, delayed acknowledgement, duplicate and conflicting messages, and recovery after interrupted connectivity. Before sensitive-data use, establish representation safeguards, identity and key management, data lifecycle boundaries, independent security assessment and ethical approval.

The demonstration and reference code use fictional institutions and synthetic identifiers only. No clinical deployment or host integration is asserted.
