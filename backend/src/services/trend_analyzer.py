import numpy as np
import ruptures as rpt
import db
from config import settings as config


def compute_trend(values):
    """
    Fits an ordinary-least-squares linear trend to a sequence of risk probabilities
    (indexed by post order) and classifies its slope into a human-readable label.

    Args:
        values: sequence of prob_suicide floats in chronological order.

    Returns:
        dict with "slope" (change in probability per post) and "label" (one of
        "Escalating", "De-escalating", "Stable", or "Insufficient Data" when there
        are fewer than 2 data points to fit a trend through).
    """
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n < 2:
        return {"slope": 0.0, "label": "Insufficient Data"}

    x = np.arange(n, dtype=float)
    slope, _intercept = np.polyfit(x, values, 1)
    slope = float(slope)

    if slope >= config.TREND_ESCALATING_SLOPE_THRESHOLD:
        label = "Escalating"
    elif slope <= config.TREND_DEESCALATING_SLOPE_THRESHOLD:
        label = "De-escalating"
    else:
        label = "Stable"

    return {"slope": slope, "label": label}


def detect_change_point(values):
    """
    Detects a single most-likely abrupt shift in a probability history using Binary
    Segmentation (Truong, Oudre & Vayatis, 2020), complementing the overall linear trend
    from compute_trend() -- a sharp deterioration after one specific post is a different,
    more urgent signal than the same net change spread gradually across many posts.

    Deliberately conservative: with only a handful of data points, a formal significance
    test has very little statistical power, so this only reports a change point once
    there's enough history to fit one at all (config.TREND_MIN_HISTORY_FOR_CHANGE_POINT)
    AND the resulting mean shift clears a minimum magnitude
    (config.TREND_CHANGE_POINT_MIN_MAGNITUDE) -- otherwise it honestly reports "not
    detected" instead of overclaiming a shift from small-sample noise.

    Args:
        values: sequence of prob_suicide floats in chronological order.

    Returns:
        dict with "detected" (bool), "index" (int or None -- position of the first post
        after the shift), and "magnitude" (float, |mean_after - mean_before|).
    """
    values = np.asarray(values, dtype=float)
    n = len(values)

    if n < config.TREND_MIN_HISTORY_FOR_CHANGE_POINT:
        return {"detected": False, "index": None, "magnitude": 0.0}

    # jump=1 evaluates every index as a candidate breakpoint (ruptures' default jump=5
    # silently has no valid candidates -- and raises BadSegmentationParameters -- on the
    # short histories (as few as 4-6 posts) this app deals with). min_size=1 similarly
    # avoids ruling out breakpoints near the edges of a short sequence.
    algo = rpt.Binseg(model="l2", jump=1, min_size=1).fit(values.reshape(-1, 1))
    breakpoints = algo.predict(n_bkps=1)
    change_index = breakpoints[0]  # first (only) breakpoint; ruptures always appends n last

    before, after = values[:change_index], values[change_index:]
    magnitude = float(abs(after.mean() - before.mean()))
    detected = magnitude >= config.TREND_CHANGE_POINT_MIN_MAGNITUDE

    return {
        "detected": detected,
        "index": change_index if detected else None,
        "magnitude": magnitude,
    }


def get_all_user_trends(limit_per_user=None):
    """
    Builds a risk-trajectory snapshot for every synthetic user seen in the live monitor
    feed so far: their probability history, trend classification, and latest risk level.
    Used to power the Live Monitor's Escalation Watch panel.
    """
    limit_per_user = config.TREND_HISTORY_LIMIT if limit_per_user is None else limit_per_user

    snapshots = []
    for user_id in db.get_tracked_user_ids():
        history = db.get_user_history(user_id, limit=limit_per_user)
        if not history:
            continue

        probabilities = [row["prob_suicide"] for row in history]
        trend = compute_trend(probabilities)
        change_point = detect_change_point(probabilities)
        latest = history[-1]

        snapshots.append({
            "user_id": user_id,
            "n_posts": len(history),
            "history": probabilities,
            "trend_slope": trend["slope"],
            "trend_label": trend["label"],
            "change_point_detected": change_point["detected"],
            "change_point_index": change_point["index"],
            "change_point_magnitude": change_point["magnitude"],
            "latest_prob_suicide": latest["prob_suicide"],
            "latest_tier_label": latest["tier_label"],
            "latest_timestamp": latest["timestamp"],
        })

    return snapshots


if __name__ == "__main__":
    print("Escalating example:", compute_trend([0.1, 0.2, 0.35, 0.5, 0.7, 0.9]))
    print("Stable example:", compute_trend([0.3, 0.32, 0.29, 0.31, 0.3, 0.33]))
    print("De-escalating example:", compute_trend([0.8, 0.65, 0.5, 0.4, 0.25, 0.15]))
    print("Insufficient data example:", compute_trend([0.5]))

    print("\nSharp step-shift example:", detect_change_point([0.1, 0.12, 0.11, 0.13, 0.85, 0.9, 0.88]))
    print("Flat/noisy example:", detect_change_point([0.3, 0.31, 0.29, 0.32, 0.28, 0.3]))
    print("Gradual linear example:", detect_change_point([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]))
    print("Too-short example:", detect_change_point([0.1, 0.2, 0.3]))
