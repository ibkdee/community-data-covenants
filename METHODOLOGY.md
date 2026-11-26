# Comparative experiment

## Research question

How do alternative access-expiry policies affect post-withdrawal access and legitimate research requests during connectivity outages?

## Design

A seeded pseudorandom generator creates 1,000 episodes for each combination of outage duration (60, 360 or 1,440 minutes) and withdrawal probability (0.05, 0.25 or 0.50). Each episode receives a binary sensitivity category and 30 distinct uniformly sampled request minutes. If withdrawal occurs, its minute is sampled uniformly within the outage. All five policies receive identical requests and underlying consent states.

| Policy | Cached permission expires after |
| --- | --- |
| Persistent | No expiry during the outage |
| Fixed 30 | 30 minutes |
| Fixed 120 | 120 minutes |
| Fixed 480 | 480 minutes |
| Risk-sensitive | 30 minutes for higher sensitivity; 480 minutes otherwise |

At the withdrawal minute and thereafter, access is classified as unauthorised. At the expiry minute and thereafter, the cached policy denies access. No renewal occurs within the simulated outage.

## Outcomes

- Unauthorised access rate: permitted post-withdrawal requests divided by all post-withdrawal requests.
- Legitimate denial rate: denied pre-withdrawal or non-withdrawal requests divided by all such requests.

Aggregate rates pool counts rather than average subgroup percentages. The output retains outage, withdrawal probability and sensitivity category so readers can examine heterogeneous outcomes. Counts are paired across policies; 270,000 underlying requests are evaluated five times.

## Interpretation

The model intentionally isolates expiry behaviour. It does not simulate multiple devices, repeated outages, research demand responses, malicious actors or actual synchronisation. Sensitivity categories and probabilities are illustrative. Results cannot be interpreted as empirical estimates of harm, exclusion or policy effectiveness in Nigeria.

The policy decision model is a separate component with different expiry parameters. A future integrated evaluation would test actual enforcement and participant-level exposure alongside request-level errors.
