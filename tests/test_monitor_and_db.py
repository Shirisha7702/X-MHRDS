import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/src')))

import db
from main import app
from services import trend_analyzer
from services.feed_simulator import SIMULATED_USER_STREAMS, get_next_post

db.init_db()
client = TestClient(app)


def test_db_init_seeds_cases():
    cases = db.get_all_cases()
    assert len(cases) >= 5
    ids = {c["id"] for c in cases}
    assert "CASE-101" in ids


def test_db_init_is_idempotent():
    db.init_db()
    db.init_db()
    cases = db.get_all_cases()
    # Re-running init_db must not duplicate the seed rows.
    assert len(cases) == len({c["id"] for c in cases})


def test_db_insert_and_fetch_analysis():
    db.insert_analysis(
        processed_text="regression test monitor post",
        model_choice="Logistic Regression",
        prob_suicide=0.42,
        tier_num=1,
        tier_label="Mild Distress",
        dominant_emotion="anxiety",
        source="monitor",
    )
    events = db.get_recent_monitor_events(limit=5)
    assert len(events) > 0
    assert any(e["processed_text"] == "regression test monitor post" for e in events)


def test_manual_analyze_is_logged_to_db():
    before = len(db.get_recent_monitor_events(limit=1000))
    client.post("/api/analyze", json={
        "text": "I am feeling okay today, just a bit tired.",
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
    })
    # Manual analyses are logged with source='manual', so the monitor-only count is unchanged.
    after = len(db.get_recent_monitor_events(limit=1000))
    assert after == before


def test_monitor_start_stop_lifecycle():
    status = client.get("/api/monitor/status").json()
    assert status["running"] is False

    start_res = client.post("/api/monitor/start", json={"model_choice": "Logistic Regression"})
    assert start_res.status_code == 200
    assert start_res.json()["running"] is True

    status = client.get("/api/monitor/status").json()
    assert status["running"] is True
    assert status["model_choice"] == "Logistic Regression"

    stop_res = client.post("/api/monitor/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["running"] is False


def test_monitor_start_rejects_unavailable_model():
    res = client.post("/api/monitor/start", json={"model_choice": "Nonexistent Model"})
    assert res.status_code == 404


def test_monitor_websocket_receives_history():
    with client.websocket_connect("/api/ws/monitor") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "history"
        assert isinstance(data["events"], list)


def test_db_user_history_is_chronological_and_tracked():
    user_id = "test-user-history"
    db.init_db()
    conn = db.get_connection()
    conn.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    for prob in (0.1, 0.3, 0.5):
        db.insert_analysis(
            processed_text=f"post at prob {prob}",
            model_choice="Logistic Regression",
            prob_suicide=prob,
            tier_num=0,
            tier_label="No Risk",
            dominant_emotion="anxiety",
            source="monitor",
            user_id=user_id,
        )

    assert user_id in db.get_tracked_user_ids()

    history = db.get_user_history(user_id, limit=10)
    assert [row["prob_suicide"] for row in history] == [0.1, 0.3, 0.5]


def test_manual_analyses_have_no_user_id():
    client.post("/api/analyze", json={
        "text": "Just a manual sandbox check-in.",
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
    })
    # Manual /analyze calls aren't tied to a synthetic monitor user_id.
    assert "manual" not in db.get_tracked_user_ids()


def test_compute_trend_classifies_direction():
    assert trend_analyzer.compute_trend([0.1, 0.3, 0.5, 0.7, 0.9])["label"] == "Escalating"
    assert trend_analyzer.compute_trend([0.8, 0.6, 0.45, 0.3, 0.15])["label"] == "De-escalating"
    assert trend_analyzer.compute_trend([0.3, 0.31, 0.29, 0.3, 0.32])["label"] == "Stable"
    assert trend_analyzer.compute_trend([0.5])["label"] == "Insufficient Data"


def test_monitor_users_route_reflects_seeded_history():
    user_id = "test-user-route"
    db.init_db()
    conn = db.get_connection()
    conn.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    for prob in (0.1, 0.2, 0.4, 0.6, 0.85):
        db.insert_analysis(
            processed_text=f"post at prob {prob}",
            model_choice="Logistic Regression",
            prob_suicide=prob,
            tier_num=1,
            tier_label="Mild Distress",
            dominant_emotion="anxiety",
            source="monitor",
            user_id=user_id,
        )

    res = client.get("/api/monitor/users")
    assert res.status_code == 200
    data = res.json()

    row = next(r for r in data if r["user_id"] == user_id)
    assert row["n_posts"] == 5
    assert row["trend_label"] == "Escalating"
    assert row["latest_prob_suicide"] == 0.85
    assert row["history"] == [0.1, 0.2, 0.4, 0.6, 0.85]


def test_detect_change_point_flags_sharp_shift():
    res = trend_analyzer.detect_change_point([0.1, 0.12, 0.11, 0.13, 0.85, 0.9, 0.88])
    assert res["detected"] is True
    assert res["index"] is not None
    assert res["magnitude"] > trend_analyzer.config.TREND_CHANGE_POINT_MIN_MAGNITUDE


def test_detect_change_point_ignores_flat_noise():
    res = trend_analyzer.detect_change_point([0.3, 0.31, 0.29, 0.32, 0.28, 0.3])
    assert res["detected"] is False
    assert res["index"] is None


def test_detect_change_point_requires_minimum_history():
    res = trend_analyzer.detect_change_point([0.1, 0.9])
    assert res["detected"] is False
    assert res["index"] is None


def test_monitor_users_route_includes_change_point_fields():
    user_id = "test-user-changepoint"
    for prob in (0.1, 0.12, 0.11, 0.13, 0.9, 0.92):
        db.insert_analysis(
            processed_text=f"post at prob {prob}",
            model_choice="Logistic Regression",
            prob_suicide=prob,
            tier_num=1,
            tier_label="Mild Distress",
            dominant_emotion="anxiety",
            source="monitor",
            user_id=user_id,
        )

    res = client.get("/api/monitor/users")
    assert res.status_code == 200
    row = next(r for r in res.json() if r["user_id"] == user_id)

    assert row["change_point_detected"] is True
    assert row["change_point_index"] is not None
    assert row["change_point_magnitude"] > 0


def test_feed_simulator_returns_known_user_and_sequential_story():
    seen_posts_per_user = {user_id: [] for user_id in SIMULATED_USER_STREAMS}

    for _ in range(200):
        user_id, post = get_next_post()
        assert user_id in SIMULATED_USER_STREAMS
        assert post in SIMULATED_USER_STREAMS[user_id]
        seen_posts_per_user[user_id].append(post)

    # Every user should show up at least once across 200 draws from 5 users.
    assert all(len(posts) > 0 for posts in seen_posts_per_user.values())

    # Each user's own storyline must always advance in-order (wrapping is allowed, but
    # posts must never come back out of the original sequence).
    for user_id, posts in seen_posts_per_user.items():
        story = SIMULATED_USER_STREAMS[user_id]
        indices = [story.index(post) for post in posts]
        for prev_idx, next_idx in zip(indices, indices[1:]):
            assert next_idx == (prev_idx + 1) % len(story)
