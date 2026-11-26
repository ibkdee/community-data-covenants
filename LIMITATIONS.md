# Scope and safeguards

## Technical boundaries

The reference decision model assumes trusted inputs. It does not implement authentication, network access enforcement, persistent storage or offline synchronisation. Its one-minute lease and five-minute freshness limit are illustrative settings, distinct from the expiry policies in the comparative experiment.

An institution cannot detect a withdrawal that has not reached it. Expiry can bound reliance on stale authorisation under specified assumptions; it cannot recall exported data or reverse training of an existing AI model.

## Evidence boundaries

All experimental inputs are synthetic. Outage lengths and withdrawal probabilities are stress-test assumptions, not estimates of Nigerian field conditions. Request-level error rates are not participant-level harms or clinical outcomes. The experiment does not establish the security of the reference model or the superiority of any policy in practice.

## Ethical safeguards

Individual refusal takes precedence over collective approval. Access to healthcare must remain independent of agreement to secondary research. Community governance requires legitimate representation, accessible appeals and independent verification of obligations. Software can evaluate a verification record; it cannot establish the truth of the underlying evidence.

No community deployment, host partnership or independent security assessment has been established. Any sensitive-data implementation would require participatory design, appropriate legal and ethics review, and security assessment.

## Development provenance

ChatGPT assisted with concept development, software implementation, test design and documentation. The repository records an exploratory technical contribution rather than evidence of independently authored production software.
