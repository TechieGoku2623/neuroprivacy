"""Per-field accuracy and Cohen's kappa on 20 labeled policy snippets."""

from __future__ import annotations

import sys
from pathlib import Path

from neuroprivacy.extractor import (
    extract_keyword_baseline,
    extract_policy,
    extract_rater2,
    extract_rules,
    field_vector,
)
from neuroprivacy.kappa import cohens_kappa, precision_recall_f1
from neuroprivacy.schemas import FIELD_NAMES, GoldLabel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import md_table, pct, read_json, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent
PROBE = HERE / "probe_set" / "documents.json"
RESULTS = HERE / "results"
VIABLE_F1 = 0.80
VIABLE_RATER_KAPPA = 0.60


def main() -> None:
    raw = read_json(PROBE)
    docs = {item["doc_id"]: item["html"] for item in raw["documents"]}
    labels = [GoldLabel.model_validate(item) for item in raw["labels"]]

    gold_vecs: dict[str, list[bool]] = {}
    ext_vecs: dict[str, list[bool]] = {}
    key_vecs: dict[str, list[bool]] = {}
    r2_vecs: dict[str, list[bool]] = {}
    status_match = 0
    keyword_misses_generic = 0
    generic_gold = 0

    for label in labels:
        html = str(docs[label.doc_id])
        gold = [label.values[name] for name in FIELD_NAMES]
        extraction = extract_policy(
            html, doc_id=label.doc_id, cache_path=HERE / "probe_set" / "llm_cache.json"
        )
        if extraction.extractor != "cache":
            extraction = extract_rules(html, doc_id=label.doc_id)
        keyword = extract_keyword_baseline(html, doc_id=label.doc_id)
        rater2 = extract_rater2(html, doc_id=label.doc_id)
        gold_vecs[label.doc_id] = gold
        ext_vecs[label.doc_id] = field_vector(extraction)
        key_vecs[label.doc_id] = field_vector(keyword)
        r2_vecs[label.doc_id] = field_vector(rater2)
        if extraction.status == label.status:
            status_match += 1
        if label.values["covers_generic_device_data"]:
            generic_gold += 1
            if not keyword.field_value("covers_generic_device_data") and not keyword.field_value(
                "names_neural_data"
            ):
                keyword_misses_generic += 1

    rows_md: list[list[str]] = []
    fields_out: dict[str, object] = {}
    f1s: list[float] = []
    for index, name in enumerate(FIELD_NAMES):
        gold_col = [gold_vecs[label.doc_id][index] for label in labels]
        ext_col = [ext_vecs[label.doc_id][index] for label in labels]
        key_col = [key_vecs[label.doc_id][index] for label in labels]
        r2_col = [r2_vecs[label.doc_id][index] for label in labels]
        precision, recall, f1 = precision_recall_f1(ext_col, gold_col)
        f1s.append(f1)
        kappa_kw = cohens_kappa(ext_col, key_col)
        kappa_r2 = cohens_kappa(gold_col, r2_col)
        fields_out[name] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "kappa_vs_keyword": kappa_kw,
            "kappa_gold_vs_rater2": kappa_r2,
            "gold_positive": sum(gold_col),
        }
        rows_md.append(
            [
                name,
                str(sum(gold_col)),
                pct(precision),
                pct(recall),
                pct(f1),
                pct(kappa_kw),
                pct(kappa_r2),
            ]
        )

    flat_gold = [bit for label in labels for bit in gold_vecs[label.doc_id]]
    flat_ext = [bit for label in labels for bit in ext_vecs[label.doc_id]]
    flat_key = [bit for label in labels for bit in key_vecs[label.doc_id]]
    flat_r2 = [bit for label in labels for bit in r2_vecs[label.doc_id]]
    mean_f1 = sum(f1s) / len(f1s)
    kappa_ext_kw = cohens_kappa(flat_ext, flat_key)
    kappa_gold_r2 = cohens_kappa(flat_gold, flat_r2)
    viable = mean_f1 >= VIABLE_F1 and kappa_gold_r2 >= VIABLE_RATER_KAPPA
    if viable:
        decision = (
            "LLM extraction is viable on this schema: mean field F1 "
            f"({mean_f1:.3f}) ≥ {VIABLE_F1:.2f} and gold-vs-rater2 kappa "
            f"({kappa_gold_r2:.3f}) ≥ {VIABLE_RATER_KAPPA:.2f}."
        )
    elif kappa_gold_r2 < VIABLE_RATER_KAPPA:
        decision = (
            "Schema needs narrowing before an LLM extractor is worth calling: "
            f"gold-vs-rater2 kappa = {kappa_gold_r2:.3f} < {VIABLE_RATER_KAPPA:.2f}."
        )
    else:
        decision = (
            f"Extractor mean field F1 = {mean_f1:.3f} is below {VIABLE_F1:.2f}. "
            "Tighten rules or narrow the schema."
        )

    payload = {
        "n_documents": len(labels),
        "mean_field_f1": mean_f1,
        "status_accuracy": status_match / len(labels),
        "kappa_extractor_vs_keyword": kappa_ext_kw,
        "kappa_gold_vs_rater2": kappa_gold_r2,
        "keyword_misses_generic": keyword_misses_generic,
        "n_generic_gold": generic_gold,
        "viable": viable,
        "decision": decision,
        "fields": fields_out,
    }
    write_json(RESULTS / "results.json", payload)
    table = md_table(
        ["field", "gold+", "precision", "recall", "F1", "κ vs keyword", "κ gold vs rater2"],
        rows_md,
    )
    md = (
        "# extraction_accuracy results\n\n"
        f"n = {len(labels)} labeled synthetic policy documents.\n\n"
        f"Mean field F1: {mean_f1:.3f}. Status accuracy: {status_match}/{len(labels)} "
        f"= {status_match / len(labels):.3f}.\n\n"
        f"Cohen's kappa extractor vs keyword (micro): {kappa_ext_kw:.3f}.\n\n"
        f"Cohen's kappa gold (pass 1) vs rater 2 (micro): {kappa_gold_r2:.3f}.\n\n"
        f"Keyword baseline missed generic-only coverage on "
        f"{keyword_misses_generic}/{generic_gold} gold-generic documents.\n\n"
        f"Decision: {decision}\n\n"
        f"{table}\n"
    )
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "results.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
