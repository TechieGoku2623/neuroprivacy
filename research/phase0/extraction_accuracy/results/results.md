# extraction_accuracy results

n = 20 labeled synthetic policy documents.

Mean field F1: 1.000. Status accuracy: 20/20 = 1.000.

Cohen's kappa extractor vs keyword (micro): 0.722.

Cohen's kappa gold (pass 1) vs rater 2 (micro): 0.740.

Keyword baseline missed generic-only coverage on 5/5 gold-generic documents.

Decision: LLM extraction is viable on this schema: mean field F1 (1.000) ≥ 0.80 and gold-vs-rater2 kappa (0.740) ≥ 0.60.

| field | gold+ | precision | recall | F1 | κ vs keyword | κ gold vs rater2 |
| --- | --- | --- | --- | --- | --- | --- |
| names_neural_data | 12 | 1.000 | 1.000 | 1.000 | 0.898 | 0.706 |
| covers_generic_device_data | 5 | 1.000 | 1.000 | 1.000 | 0.000 | 0.273 |
| grants_deletion | 14 | 1.000 | 1.000 | 1.000 | 0.565 | 0.565 |
| retention_conflicts_deletion | 2 | 1.000 | 1.000 | 1.000 | 0.643 | 1.000 |
| discloses_sale | 5 | 1.000 | 1.000 | 1.000 | 0.692 | 0.692 |
| discloses_sharing | 3 | 1.000 | 1.000 | 1.000 | 0.459 | 0.459 |
| states_purpose_limitation | 3 | 1.000 | 1.000 | 1.000 | 0.459 | 0.773 |
| states_consent_for_sensitive | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
