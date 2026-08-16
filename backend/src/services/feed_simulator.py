import random

# Each synthetic user has a fixed sequential storyline (rather than one flat pool of
# unrelated posts), so the live feed has something real to detect a *trend* in: some
# storylines escalate, some stay flat at a low or high level, and one de-escalates.
# Mirrors the tone of App.jsx's samplePosts and fairness_auditor's cohort texts.
SIMULATED_USER_STREAMS = {
    # Escalating: academic/financial stress building toward a crisis.
    "anon-1042": [
        "ngl this semester has been rough, so much coursework piling up",
        "failed another quiz today, starting to feel really behind",
        "can't keep up with anything anymore, feels like everything's falling apart",
        "haven't been sleeping, just feel numb most days now",
        "i don't see the point of any of this anymore honestly",
        "i have a plan to end things tonight, i just can't do this anymore",
    ],
    # Flat / benign: ordinary day-to-day chatter, no distress.
    "anon-7788": [
        "just finished dinner, cooking pizza. recommend a good anime to watch tonight?",
        "went for a run this morning and the weather was perfect",
        "does anyone know a good recipe for banana bread? mine always comes out dry",
        "my cat knocked a plant off the shelf again, classic tuesday",
        "finally organized my closet, feels so satisfying",
        "trying out a new coffee shop downtown this weekend",
    ],
    # Flat / moderate: persistent mild distress that neither escalates nor resolves.
    "anon-3391": [
        "feeling a bit lonely lately, friends have been busy",
        "work has been stressful but i'm managing okay",
        "still feeling kinda down, but talking to my therapist helps",
        "rough week again, just tired of feeling like this honestly",
        "starting to feel a little better today, small steps i guess",
        "still not great but i'm hanging in there",
    ],
    # De-escalating: a recovery arc after reaching out for support.
    "anon-5566": [
        "i've been in such a dark place, don't know how much more i can take",
        "talked to someone about how i've been feeling, it helped a little",
        "started seeing a counselor this week, still rough but trying",
        "had a decent day today for once, small win",
        "feeling a lot more hopeful lately, therapy is really helping",
        "things are looking up, grateful for the people supporting me",
    ],
    # Flat / high risk: already in sustained crisis, not escalating further but never clearing.
    "anon-9012": [
        "i've been thinking about ending it for weeks now, nothing feels worth it",
        "still feel like giving up most days, don't know why i'm still here",
        "thought about my plan again today, just feels like the only way out",
        "everyone would be better off without me, i keep thinking about ending it",
        "still stuck in the same dark thoughts, wish it would just stop",
        "keep thinking about ending things, can't shake these thoughts",
    ],
}

# Tracks each synthetic user's position in their own storyline across successive ticks.
_user_cursors = {user_id: 0 for user_id in SIMULATED_USER_STREAMS}


def get_next_post():
    """
    Picks a random synthetic user and returns their next sequential post, standing in for
    a live multi-user social-media stream. Each user's storyline wraps back to its start
    once exhausted, so the feed runs indefinitely.

    Returns:
        tuple[str, str]: (user_id, post_text).
    """
    user_id = random.choice(list(SIMULATED_USER_STREAMS.keys()))
    story = SIMULATED_USER_STREAMS[user_id]
    idx = _user_cursors[user_id]
    post = story[idx]
    _user_cursors[user_id] = (idx + 1) % len(story)
    return user_id, post
