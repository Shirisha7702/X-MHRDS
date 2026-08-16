import sqlite3
from datetime import datetime, timezone
from config import settings as config
from logging_config import get_logger

logger = get_logger("db")

# Seed data used to populate the `cases` table the first time it's empty.
# This is the same content that used to live as a hardcoded list in semantic_search.py.
SEED_CASES = [
    {
        "id": "CASE-101",
        "post": "I'm failing my college classes and my parents will hate me. I feel like there's no point in trying anymore.",
        "resolution": "Operator contacted the user's university student counseling center. User was scheduled for an academic support check-in.",
        "tier": "Tier 1: Mild Distress",
        "emotion": "anxiety",
    },
    {
        "id": "CASE-102",
        "post": "I have been sitting in my room for three weeks. No one calls me, no one texts me. I am completely alone and invisible.",
        "resolution": "Operator engaged in active validation. Shared community meetup groups and a warm-line support phone number.",
        "tier": "Tier 1: Mild Distress",
        "emotion": "sadness",
    },
    {
        "id": "CASE-103",
        "post": "I want to end it. I have accumulated my medication and am planning to swallow it tonight. Goodbye.",
        "resolution": "Operator immediately escalated to emergency support. Provided 988 direct SMS and stayed online until user confirmed safety.",
        "tier": "Tier 3: Severe Active Risk",
        "emotion": "hopelessness",
    },
    {
        "id": "CASE-104",
        "post": "My partner broke up with me and my chest hurts so much. I can't stop crying. I feel like my life is over.",
        "resolution": "Operator validated the relationship trauma. Replaced thoughts of ending life with a list of immediate local emergency friends.",
        "tier": "Tier 2: Moderate Risk",
        "emotion": "sadness",
    },
    {
        "id": "CASE-105",
        "post": "I am so stressed about my job search. 100 rejections. I am a complete failure and a burden to my family.",
        "resolution": "Operator reframed failure concepts, directed to resume review workshops, and provided general mental health warmline numbers.",
        "tier": "Tier 1: Mild Distress",
        "emotion": "hopelessness",
    },
]


def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                post TEXT NOT NULL,
                resolution TEXT NOT NULL,
                tier TEXT NOT NULL,
                emotion TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                processed_text TEXT NOT NULL,
                model_choice TEXT NOT NULL,
                prob_suicide REAL NOT NULL,
                tier_num INTEGER NOT NULL,
                tier_label TEXT NOT NULL,
                dominant_emotion TEXT,
                source TEXT NOT NULL,
                user_id TEXT
            )
        """)
        conn.commit()

        # Migration for databases created before user_id existed: CREATE TABLE IF NOT
        # EXISTS above is a no-op against an already-existing table, so add the column
        # explicitly if an older analyses table is missing it.
        existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(analyses)").fetchall()}
        if "user_id" not in existing_columns:
            conn.execute("ALTER TABLE analyses ADD COLUMN user_id TEXT")
            conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        if count == 0:
            for case in SEED_CASES:
                insert_case(case, conn=conn)
            conn.commit()
        logger.info("Database schema ready (cases + analyses tables).")
    except Exception:
        logger.exception("Database initialization failed")
        raise
    finally:
        conn.close()


def insert_case(case, conn=None):
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO cases (id, post, resolution, tier, emotion) VALUES (?, ?, ?, ?, ?)",
            (case["id"], case["post"], case["resolution"], case["tier"], case["emotion"]),
        )
        if owns_conn:
            conn.commit()
    except Exception:
        logger.exception(f"Failed to insert case {case.get('id')}")
        raise
    finally:
        if owns_conn:
            conn.close()


def get_all_cases():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, post, resolution, tier, emotion FROM cases").fetchall()
        return [dict(row) for row in rows]
    except Exception:
        logger.exception("Failed to fetch cases")
        raise
    finally:
        conn.close()


def insert_analysis(processed_text, model_choice, prob_suicide, tier_num, tier_label, dominant_emotion, source, user_id=None):
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO analyses
               (timestamp, processed_text, model_choice, prob_suicide, tier_num, tier_label, dominant_emotion, source, user_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                processed_text,
                model_choice,
                prob_suicide,
                tier_num,
                tier_label,
                dominant_emotion,
                source,
                user_id,
            ),
        )
        conn.commit()
    except Exception:
        logger.exception(f"Failed to insert analysis (source={source}, model_choice={model_choice})")
        raise
    finally:
        conn.close()


def get_recent_monitor_events(limit=25):
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT timestamp, processed_text, model_choice, prob_suicide, tier_num, tier_label, dominant_emotion, user_id
               FROM analyses WHERE source = 'monitor' ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    except Exception:
        logger.exception("Failed to fetch recent monitor events")
        raise
    finally:
        conn.close()


def get_tracked_user_ids():
    """Distinct synthetic user_ids seen in monitor-sourced analyses, most recently active first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT user_id, MAX(id) AS last_id FROM analyses
               WHERE source = 'monitor' AND user_id IS NOT NULL
               GROUP BY user_id ORDER BY last_id DESC"""
        ).fetchall()
        return [row["user_id"] for row in rows]
    except Exception:
        logger.exception("Failed to fetch tracked user ids")
        raise
    finally:
        conn.close()


def get_user_history(user_id, limit=20):
    """Chronological (oldest-first) monitor-sourced analysis history for one synthetic user,
    used to compute their risk trend/escalation trajectory."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT timestamp, processed_text, prob_suicide, tier_num, tier_label
               FROM analyses WHERE source = 'monitor' AND user_id = ?
               ORDER BY id DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in reversed(rows)]
    except Exception:
        logger.exception(f"Failed to fetch history for user_id={user_id}")
        raise
    finally:
        conn.close()
