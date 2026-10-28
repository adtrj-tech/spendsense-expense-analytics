
import pandas as pd


def flag_unusual_transactions(
    df: pd.DataFrame,
    multiplier: float = 1.5,
    min_category_size: int = 8,
) -> pd.DataFrame:
    """
    Flag unusually high transaction amounts using IQR thresholds.

    Categories with enough transactions get category-specific
    thresholds. Smaller categories use the global threshold.

    Flags indicate statistical outliers, not fraud.
    """
    if "amount" not in df.columns:
        raise ValueError(
            "The DataFrame must contain an 'amount' column."
        )

    if "category" not in df.columns:
        raise ValueError(
            "The DataFrame must contain a 'category' column."
        )

    if multiplier <= 0:
        raise ValueError(
            "The multiplier must be greater than zero."
        )

    if min_category_size < 4:
        raise ValueError(
            "min_category_size must be at least 4."
        )

    result = df.copy()
    amounts = pd.to_numeric(result["amount"], errors="coerce")

    if amounts.isna().any():
        raise ValueError(
            "Amounts must be valid numeric values."
        )

    if (amounts <= 0).any():
        raise ValueError(
            "Amounts must be greater than zero."
        )

    if len(amounts) < 4:
        raise ValueError(
            "At least four transactions are required."
        )

    categories = result["category"]

    if categories.isna().any():
        raise ValueError(
            "Every transaction must have a category."
        )

    if categories.astype(str).str.strip().eq("").any():
        raise ValueError(
            "Categories cannot be empty."
        )

    def upper_iqr_threshold(values):
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        return q3 + multiplier * (q3 - q1)

    # Overall threshold is the fallback for small categories.
    global_threshold = upper_iqr_threshold(amounts)

    result["is_unusual"] = False
    result["anomaly_threshold"] = global_threshold
    result["anomaly_scope"] = "Overall baseline"
    result["anomaly_reason"] = ""

    for category, indices in result.groupby(
        "category",
        sort=False,
    ).groups.items():

        category_amounts = amounts.loc[indices]

        if len(category_amounts) >= min_category_size:
            threshold = upper_iqr_threshold(category_amounts)
            scope = f"{category} category"
        else:
            threshold = global_threshold
            scope = "Overall baseline"

        unusual = category_amounts > threshold

        result.loc[indices, "anomaly_threshold"] = threshold
        result.loc[indices, "anomaly_scope"] = scope
        result.loc[indices, "is_unusual"] = unusual

        unusual_indices = unusual[unusual].index

        result.loc[
            unusual_indices,
            "anomaly_reason",
        ] = (
            "Amount exceeds the IQR-based upper threshold "
            f"of ₹{threshold:,.2f} for {scope}."
        )

    return result
