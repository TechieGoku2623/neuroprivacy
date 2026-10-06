"""Build 20 hand-labeled synthetic policy snippets and the LLM response cache."""

from __future__ import annotations

import sys
from pathlib import Path

from neuroprivacy.cache import cache_entry, dump_cache, prompt_hash
from neuroprivacy.config import get_settings
from neuroprivacy.extractor import extract_rules
from neuroprivacy.schemas import GoldLabel

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parents[1]))
from _lib import write_json  # noqa: E402

# Hand labels are labeling pass 1. They are assigned from the document text,
# not copied from extract_rules. Rater 2 is a separate rules lexicon.
DOCS: list[dict[str, object]] = [
    {
        "doc_id": "P01",
        "html": (
            "<h1>P01</h1><p>We collect neural data from the headband.</p>"
            "<p>You have the right to delete neural data.</p>"
            "<p>We obtain consent. Data is used only for the specified purpose.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": True,
            "states_consent_for_sensitive": True,
        },
        "status": "COMPLIANT",
        "notes": "Explicit neural + deletion.",
    },
    {
        "doc_id": "P02",
        "html": (
            "<h1>P02</h1><p>The headset stores device data in the cloud.</p>"
            "<p>You have the right to delete device data.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": True,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "Generic device data. Keyword baseline misses names and generic cover.",
    },
    {
        "doc_id": "P03",
        "html": (
            "<h1>P03</h1><p>We process neural data.</p>"
            "<p>You have the right to delete your records.</p>"
            "<p>We retain all recordings for 7 years and cannot delete archives.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": True,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "INDETERMINATE",
        "notes": "Deletion contradicted by retention.",
    },
    {
        "doc_id": "P04",
        "html": (
            "<h1>P04</h1><p>Neural signals may be sold to research partners.</p>"
            "<p>No deletion mechanism is described.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": False,
            "retention_conflicts_deletion": False,
            "discloses_sale": True,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "GAP",
        "notes": "Sale disclosed, no deletion.",
    },
    {
        "doc_id": "P05",
        "html": "<h1>P05</h1><p>We collect neural data for product analytics.</p>",
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": False,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "GAP",
        "notes": "Neural named, no deletion.",
    },
    {
        "doc_id": "P06",
        "html": (
            "<h1>P06</h1><p>The wearable records EEG during sleep.</p>"
            "<p>You have the right to delete sleep sessions.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "EEG is an explicit neural-data synonym.",
    },
    {
        "doc_id": "P07",
        "html": (
            "<h1>P07</h1><p>Our BCI app shares session logs with third parties.</p>"
            "<p>You have the right to delete session logs.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": True,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "BCI + sharing + deletion.",
    },
    {
        "doc_id": "P08",
        "html": (
            "<h1>P08</h1><p>We store sensor data from the visor.</p>"
            "<p>You may erase your sensor data from the account page.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": True,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "Erase synonym. Keyword and rater2 miss erasure-only deletion.",
    },
    {
        "doc_id": "P09",
        "html": "<h1>P09</h1><p>We care about privacy and your trust.</p>",
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": False,
            "grants_deletion": False,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "GAP",
        "notes": "Empty marketing policy.",
    },
    {
        "doc_id": "P10",
        "html": (
            "<h1>P10</h1><p>We measure brain activity and that data is sold "
            "and shared with advertisers.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": False,
            "retention_conflicts_deletion": False,
            "discloses_sale": True,
            "discloses_sharing": True,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "GAP",
        "notes": "Brain activity + sale + advertisers.",
    },
    {
        "doc_id": "P11",
        "html": (
            "<h1>P11</h1><p>Neural data is processed after opt-in consent.</p>"
            "<p>It is not used for unrelated purposes.</p>"
            "<p>You have the right to delete this information.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": True,
            "states_consent_for_sensitive": True,
        },
        "status": "COMPLIANT",
        "notes": "Consent + purpose + deletion.",
    },
    {
        "doc_id": "P12",
        "html": (
            "<h1>P12</h1><p>Wearable data is uploaded nightly.</p>"
            "<p>You have the right to delete wearable data.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": True,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "Wearable data generic cover.",
    },
    {
        "doc_id": "P13",
        "html": (
            "<h1>P13</h1><p>You may request deletion of neural data.</p>"
            "<p>We will not delete safety logs after a request.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": True,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "INDETERMINATE",
        "notes": "Request deletion vs will not delete.",
    },
    {
        "doc_id": "P14",
        "html": (
            "<h1>P14</h1><p>Physiological data is stored on the phone.</p>"
            "<p>Use the app to erase your physiological data.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": True,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "Physiological data + erase. Rater2 misses both generic synonym and erase.",
    },
    {
        "doc_id": "P15",
        "html": (
            "<h1>P15</h1><p>We sell biometric templates derived from the camera.</p>"
            "<p>This policy does not mention headset telemetry categories.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": False,
            "grants_deletion": False,
            "retention_conflicts_deletion": False,
            "discloses_sale": True,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "GAP",
        "notes": "Biometric sale is not neural data.",
    },
    {
        "doc_id": "P16",
        "html": (
            "<h1>P16</h1><p>Sensitive personal information we collect includes neural data.</p>"
            "<p>You have the right to delete SPI. We do not sell SPI.</p>"
            "<p>We obtain consent and apply purpose limitation.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": True,
            "discloses_sharing": False,
            "states_purpose_limitation": True,
            "states_consent_for_sensitive": True,
        },
        "status": "COMPLIANT",
        "notes": "CCPA-style SPI list. 'do not sell' still discloses sale as a topic.",
    },
    {
        "doc_id": "P17",
        "html": (
            "<h1>P17</h1><p>Biological data, including neural data, is sensitive data.</p>"
            "<p>We obtain consent before processing. You have the right to delete it.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": True,
        },
        "status": "COMPLIANT",
        "notes": "Colorado-style biological + neural.",
    },
    {
        "doc_id": "P18",
        "html": (
            "<h1>P18</h1><p>We may sell your data to grow the business.</p>"
            "<p>Contact us with questions.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": False,
            "grants_deletion": False,
            "retention_conflicts_deletion": False,
            "discloses_sale": True,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "GAP",
        "notes": "Vague sale, no neural category.",
    },
    {
        "doc_id": "P19",
        "html": (
            "<h1>P19</h1><p>The research kit records MEG and fNIRS streams.</p>"
            "<p>You have the right to delete research-kit recordings.</p>"
        ),
        "values": {
            "names_neural_data": True,
            "covers_generic_device_data": False,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": False,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "MEG/fNIRS synonyms. Rater2 lexicon lacks both.",
    },
    {
        "doc_id": "P20",
        "html": (
            "<h1>P20</h1><p>Headset data is processed by service providers.</p>"
            "<p>You have the right to be forgotten.</p>"
        ),
        "values": {
            "names_neural_data": False,
            "covers_generic_device_data": True,
            "grants_deletion": True,
            "retention_conflicts_deletion": False,
            "discloses_sale": False,
            "discloses_sharing": True,
            "states_purpose_limitation": False,
            "states_consent_for_sensitive": False,
        },
        "status": "COMPLIANT",
        "notes": "Headset data + right to be forgotten. Rater2 misses both.",
    },
]


def _sample_html() -> list[tuple[str, str]]:
    sample = get_settings().sample_dir
    names = [
        "vendor-a.html",
        "vendor-b.html",
        "vendor-c.html",
        "vendor-d-2025-01.html",
        "vendor-d-2025-06.html",
    ]
    return [(name, (sample / name).read_text(encoding="utf-8")) for name in names]


def main() -> None:
    labels = []
    payload_docs = []
    cache: dict[str, object] = {}
    for item in DOCS:
        html = str(item["html"])
        doc_id = str(item["doc_id"])
        gold = GoldLabel(
            doc_id=doc_id,
            values=item["values"],  # type: ignore[arg-type]
            status=item["status"],  # type: ignore[arg-type]
            notes=str(item["notes"]),
        )
        labels.append(gold.model_dump(mode="json"))
        payload_docs.append({"doc_id": doc_id, "html": html, "notes": item["notes"]})
        extraction = extract_rules(html, doc_id=doc_id)
        cache[prompt_hash(html)] = cache_entry(extraction)

    write_json(HERE / "documents.json", {"documents": payload_docs, "labels": labels})

    for name, html in _sample_html():
        extraction = extract_rules(html, doc_id=name)
        cache[prompt_hash(html)] = cache_entry(extraction)

    dump_cache(HERE / "llm_cache.json", cache)
    dump_cache(get_settings().llm_cache_path, cache)
    (HERE / "README.md").write_text(
        "# extraction_accuracy probe set\n\n"
        "20 synthetic public-style HTML snippets with hand labels (pass 1).\n"
        "Not scraped. Not behind authentication.\n",
        encoding="utf-8",
    )
    print(f"wrote {len(DOCS)} labeled documents and {len(cache)} cache entries")


if __name__ == "__main__":
    main()
