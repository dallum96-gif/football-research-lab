def kelly_fraction(
    probability,
    decimal_odds,
):
    """
    Full Kelly fraction for a binary bet.

    probability: model probability, 0–1
    decimal_odds: decimal bookmaker odds
    """
    p = float(probability)
    odds = float(decimal_odds)

    if not 0 < p < 1:
        raise ValueError(
            "Probability must be between 0 and 1."
        )

    if odds <= 1:
        raise ValueError(
            "Decimal odds must be greater than 1."
        )

    b = odds - 1
    q = 1 - p

    fraction = (
        (b * p) - q
    ) / b

    return max(
        0.0,
        fraction,
    )


def kelly_analysis(
    probability,
    decimal_odds,
    bankroll=None,
):
    """
    Return full, half and quarter Kelly.

    A zero Kelly value means the model does not
    identify a positive-EV wager at the supplied odds.
    """

    p = float(probability)
    odds = float(decimal_odds)

    fair_odds = (
        1.0 / p
    )

    implied_probability = (
        1.0 / odds
    )

    expected_value = (
        p * odds
    ) - 1.0

    full = kelly_fraction(
        p,
        odds,
    )

    half = full / 2
    quarter = full / 4

    result = {
        "model_probability": p,
        "market_implied_probability": implied_probability,
        "fair_odds": fair_odds,
        "bookmaker_odds": odds,
        "expected_value": expected_value,
        "full_kelly": full,
        "half_kelly": half,
        "quarter_kelly": quarter,
    }

    if bankroll is not None:
        bankroll = float(bankroll)

        if bankroll < 0:
            raise ValueError(
                "Bankroll cannot be negative."
            )

        result["stakes"] = {
            "full_kelly": bankroll * full,
            "half_kelly": bankroll * half,
            "quarter_kelly": bankroll * quarter,
        }

    return result
