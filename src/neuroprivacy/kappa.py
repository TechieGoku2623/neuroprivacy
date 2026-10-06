"""Cohen's kappa for binary raters."""

from __future__ import annotations


def cohens_kappa(rater1: list[bool], rater2: list[bool]) -> float:
    """Cohen's kappa for two binary label sequences of equal length."""

    if len(rater1) != len(rater2):
        raise ValueError("rater sequences must have the same length")
    n = len(rater1)
    if n == 0:
        return 0.0
    agreed = sum(a == b for a, b in zip(rater1, rater2, strict=True))
    p_o = agreed / n
    p1_yes = sum(rater1) / n
    p2_yes = sum(rater2) / n
    p_e = p1_yes * p2_yes + (1.0 - p1_yes) * (1.0 - p2_yes)
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def precision_recall_f1(pred: list[bool], gold: list[bool]) -> tuple[float, float, float]:
    tp = sum(p and g for p, g in zip(pred, gold, strict=True))
    fp = sum(p and not g for p, g in zip(pred, gold, strict=True))
    fn = sum((not p) and g for p, g in zip(pred, gold, strict=True))
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return precision, recall, f1
