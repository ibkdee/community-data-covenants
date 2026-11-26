# Experimental findings

## Access expiry under intermittent connectivity

The comparative experiment evaluates 270,000 distinct synthetic requests across five policies (1,350,000 policy decisions). There are 36,237 post-withdrawal requests and 233,763 legitimate requests per policy.

| Policy | Post-withdrawal requests permitted | Legitimate requests denied | Post-withdrawal permission rate | Legitimate denial rate |
| --- | ---: | ---: | ---: | ---: |
| Persistent | 36,237 | 0 | 100.00% | 0.00% |
| Fixed 30 minutes | 3,181 | 182,807 | 8.78% | 78.20% |
| Fixed 120 minutes | 13,416 | 119,970 | 37.02% | 51.32% |
| Fixed 480 minutes | 25,070 | 48,737 | 69.18% | 20.85% |
| Sensitivity-dependent | 14,240 | 114,923 | 39.30% | 49.16% |

## Interpretation

Shorter expiry periods reduce potential post-withdrawal access at the cost of additional interruptions to legitimate research. The sensitivity-dependent policy permits 824 more post-withdrawal requests than the two-hour policy, while denying 5,047 fewer legitimate requests. The two outcomes use different denominators and neither policy dominates the other on both measures.

These results describe the consequences of the simulated policy rules, not empirical privacy harms or participation losses. Identical request sequences support paired policy comparisons. They do not establish that the sensitivity-dependent policy should be adopted, or that it is superior to established data governance systems.

## Reproduction

Run `python experiment.py` using Python 3.13.5 with the default seed (20261126). The script generates subgroup counts in `results.csv` and prints the aggregate counts and percentages. See [experimental methodology](METHODOLOGY.md) for scenario construction and [scope and safeguards](LIMITATIONS.md) for interpretation boundaries.
