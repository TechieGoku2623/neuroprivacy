# statute_coverage results

Encoded clauses: 22. Policy-text checkable: 14 (0.636). Network/product: 2. Internal record: 3. Cannot check: 3.

Decision: 14/22 = 0.636 of encoded provisions are machine-checkable from policy text. Phase 2 should center on extraction + deterministic scoring. Network capture stays optional.

## By statute

| statute | n | policy-text | fraction |
| --- | --- | --- | --- |
| CA_SB_1223 | 10 | 6 | 0.600 |
| CO_HB24_1058 | 12 | 8 | 0.667 |

## Clauses

| clause_id | statute | citation | checkability | policy-text? |
| --- | --- | --- | --- | --- |
| CO-DEF-NEURAL | CO_HB24_1058 | C.R.S. § 6-1-1303 (as amended by HB24-1058) | policy_text | yes |
| CO-SENSITIVE | CO_HB24_1058 | C.R.S. § 6-1-1303 (sensitive data definition) | policy_text | yes |
| CO-CONSENT | CO_HB24_1058 | C.R.S. § 6-1-1308(7) | policy_text | yes |
| CO-DELETE | CO_HB24_1058 | C.R.S. § 6-1-1306(1)(d) | policy_text | yes |
| CO-ACCESS | CO_HB24_1058 | C.R.S. § 6-1-1306(1)(b) | policy_text | yes |
| CO-CORRECT | CO_HB24_1058 | C.R.S. § 6-1-1306(1)(c) | policy_text | yes |
| CO-OPTOUT | CO_HB24_1058 | C.R.S. § 6-1-1306(1)(a) | policy_text | yes |
| CO-PURPOSE | CO_HB24_1058 | C.R.S. § 6-1-1308(1)–(3) | policy_text | yes |
| CO-DPA | CO_HB24_1058 | C.R.S. § 6-1-1309 | internal_record | no |
| CO-PROCESSOR | CO_HB24_1058 | C.R.S. § 6-1-1305 | internal_record | no |
| CO-THRESHOLD | CO_HB24_1058 | C.R.S. § 6-1-1304 | cannot_check | no |
| CO-TRANSMIT | CO_HB24_1058 | C.R.S. § 6-1-1308 (processing duties) applied to device telemetry | network_or_product | no |
| CA-DEF-NEURAL | CA_SB_1223 | Cal. Civ. Code § 1798.140 (SB 1223 amendment) | policy_text | yes |
| CA-SPI | CA_SB_1223 | Cal. Civ. Code § 1798.140 (sensitive personal information) | policy_text | yes |
| CA-NOTICE | CA_SB_1223 | Cal. Civ. Code § 1798.100 | policy_text | yes |
| CA-POLICY-LIST | CA_SB_1223 | Cal. Civ. Code § 1798.130 | policy_text | yes |
| CA-LIMIT | CA_SB_1223 | Cal. Civ. Code § 1798.121 | policy_text | yes |
| CA-SALE | CA_SB_1223 | Cal. Civ. Code § 1798.120 | policy_text | yes |
| CA-INFERENCE | CA_SB_1223 | Cal. Civ. Code § 1798.140 neural-data definition (non-inference clause) | cannot_check | no |
| CA-CONTRACT | CA_SB_1223 | Cal. Civ. Code § 1798.140 (service provider / contractor) | internal_record | no |
| CA-ENFORCE | CA_SB_1223 | Cal. Civ. Code § 1798.199.40 et seq. (CPPA / AG enforcement) | cannot_check | no |
| CA-DEVICE | CA_SB_1223 | Cal. Civ. Code § 1798.121 applied to on-device neural streams | network_or_product | no |
