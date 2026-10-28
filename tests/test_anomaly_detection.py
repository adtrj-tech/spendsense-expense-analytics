
import pandas as pd
import pytest

from anomaly_detection import flag_unusual_transactions


def test_flags_extreme_transaction():
    df = pd.DataFrame({
        "category": ["Shopping"] * 9,
        "amount": [
            100, 120, 130, 150, 170,
            200, 250, 300, 10000,
        ],
    })

    result = flag_unusual_transactions(df)

    assert result["is_unusual"].iloc[-1]
    assert not result["is_unusual"].iloc[0]
    assert result["anomaly_reason"].iloc[-1] != ""


def test_uses_category_specific_threshold():
    df = pd.DataFrame({
        "category": ["Shopping"] * 9,
        "amount": [
            100, 120, 130, 150, 170,
            200, 250, 300, 10000,
        ],
    })

    result = flag_unusual_transactions(df)

    assert (
        result["anomaly_scope"] == "Shopping category"
    ).all()

    assert result["is_unusual"].iloc[-1]


def test_small_categories_use_global_fallback():
    df = pd.DataFrame({
        "category": [
            "Food", "Food",
            "Transport", "Transport",
        ],
        "amount": [100, 120, 150, 200],
    })

    result = flag_unusual_transactions(df)

    assert (
        result["anomaly_scope"] == "Overall baseline"
    ).all()


def test_regular_transactions_are_not_flagged():
    df = pd.DataFrame({
        "category": ["Food"] * 6,
        "amount": [100, 110, 120, 130, 140, 150],
    })

    result = flag_unusual_transactions(df)

    assert not result["is_unusual"].any()


def test_requires_enough_transactions():
    df = pd.DataFrame({
        "category": ["Food"] * 3,
        "amount": [100, 200, 300],
    })

    with pytest.raises(ValueError):
        flag_unusual_transactions(df)


def test_rejects_invalid_amounts():
    df = pd.DataFrame({
        "category": ["Food"] * 4,
        "amount": [100, None, 200, 300],
    })

    with pytest.raises(ValueError):
        flag_unusual_transactions(df)


def test_requires_category_column():
    df = pd.DataFrame({
        "amount": [100, 200, 300, 400],
    })

    with pytest.raises(ValueError):
        flag_unusual_transactions(df)


def test_rejects_invalid_minimum_category_size():
    df = pd.DataFrame({
        "category": ["Food"] * 4,
        "amount": [100, 120, 140, 160],
    })

    with pytest.raises(ValueError):
        flag_unusual_transactions(
            df,
            min_category_size=3,
        )
