from __future__ import annotations

import pytest

from neuroprivacy.kappa import cohens_kappa, precision_recall_f1


def test_perfect_agreement() -> None:
    labels = [True, False, True, False]
    assert cohens_kappa(labels, labels) == 1.0


def test_empty_and_length_mismatch() -> None:
    assert cohens_kappa([], []) == 0.0
    with pytest.raises(ValueError):
        cohens_kappa([True], [True, False])


def test_expected_chance_agreement() -> None:
    r1 = [True, True, False, False]
    r2 = [False, False, True, True]
    assert cohens_kappa(r1, r2) == pytest.approx(-1.0)


def test_all_true_is_defined() -> None:
    assert cohens_kappa([True, True], [True, True]) == 1.0


def test_precision_recall_f1() -> None:
    pred = [True, True, False, False]
    gold = [True, False, True, False]
    precision, recall, f1 = precision_recall_f1(pred, gold)
    assert precision == pytest.approx(0.5)
    assert recall == pytest.approx(0.5)
    assert f1 == pytest.approx(0.5)
    assert precision_recall_f1([False], [False]) == (0.0, 0.0, 0.0)
