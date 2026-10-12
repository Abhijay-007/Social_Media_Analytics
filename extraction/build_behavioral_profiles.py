"""
SIH Social Media Analytics
Phase 3: Corrected Behavioral Audience Profile Builder

Fixes over the original:
1. Correctly propagates Phase-2 age: phase2["age"]["bracket"].
2. Correctly parses Firebase epoch-millisecond timestamps.
3. Calculates active_days from unique UTC calendar dates.
4. Normalizes behavioral-interest scores per user to 0..1.
5. Keeps explainable evidence counts for every behavioral interest.
6. Adds declared-vs-observed interest alignment.
7. Adds topic affinity/concentration and temporal interest activity.
8. Adds aggregate age x interest and age x sentiment matrices.
9. Does not rerun any ML model.
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

USER_EVIDENCE_FILE = PROCESSED_DIR / "user_evidence.json"
INTEREST_FILE = PROCESSED_DIR / "interest_profiles.json"
ENRICHED_FILE = PROCESSED_DIR / "enriched_text.json"
TOPIC_FILE = PROCESSED_DIR / "topic_analysis.json"
POSTS_FILE = PROCESSED_DIR / "posts.json"
COMMENTS_FILE = PROCESSED_DIR / "comments.json"

OUTPUT_FILE = PROCESSED_DIR / "behavioral_profiles.json"

INTEREST_CATEGORIES = [
    "Technology & Engineering",
    "Sports",
    "Entertainment & Cinema",
    "Arts & Design",
    "Travel & Lifestyle",
    "Science & Research",
    "Business & Entrepreneurship",
    "Education & Learning",
    "Health & Wellness",
]

# Topics 0 and 4 are primarily conversational/interaction topics.
# They are deliberately NOT converted directly into interests.
TOPIC_CATEGORY_MAP = {
    0: None,
    1: "Sports",
    2: "Travel & Lifestyle",
    3: None,
    4: None,
    5: "Technology & Engineering",
    6: "Travel & Lifestyle",
    7: "Arts & Design",
    8: "Sports",
    9: "Entertainment & Cinema",
    10: None,
    11: None,
    12: None,
    13: "Travel & Lifestyle",
    14: None,
}

KEYWORDS = {
    "Technology & Engineering": [
        "technology", "tech", "software", "developer", "coding",
        "programming", "python", "ai", "artificial intelligence",
        "machine learning", "data", "engineering", "engineer",
        "robotics", "cybersecurity", "cloud", "algorithm", "linux",
    ],
    "Sports": [
        "sport", "sports", "cricket", "football", "soccer", "f1",
        "formula 1", "motorsport", "racing", "ipl", "tennis",
        "athletics", "running", "cycling", "basketball",
        "premier league", "championship", "match", "player",
    ],
    "Entertainment & Cinema": [
        "movie", "movies", "cinema", "film", "films", "filmmaking",
        "mcu", "marvel", "avengers", "hollywood", "actor", "actress",
        "acting", "series", "box office", "scifi",
    ],
    "Arts & Design": [
        "art", "arts", "design", "designer", "ux", "ui", "photography",
        "photographer", "illustration", "creative", "style", "fashion",
        "visual", "music", "drawing", "beauty", "skincare", "makeup",
        "thrift", "secondhand",
    ],
    "Travel & Lifestyle": [
        "travel", "travelling", "tour", "explorer", "lifestyle",
        "food", "foodie", "cuisine", "culture", "mindset", "routine",
        "minimalist", "confidence", "daily", "thrifting",
    ],
    "Science & Research": [
        "science", "scientist", "research", "researcher", "biology",
        "biologist", "marine", "ocean", "climate", "physics",
        "chemistry", "space", "astronomy", "experiment",
    ],
    "Business & Entrepreneurship": [
        "business", "entrepreneur", "startup", "founder", "marketing",
        "finance", "investing", "investment", "brand", "commerce",
        "sales",
    ],
    "Education & Learning": [
        "education", "learning", "student", "teacher", "teaching",
        "school", "college", "university", "study", "course", "exam",
        "tutorial",
    ],
    "Health & Wellness": [
        "health", "wellness", "fitness", "mental health", "skincare",
        "skin", "nutrition", "gym", "meditation", "wellbeing",
        "workout", "healthy",
    ],
}

GENERIC_WORDS = {
    "nice", "good", "great", "true", "agree", "agreed", "fair",
    "yes", "yep", "okay", "post", "liked", "love", "looks", "well",
    "said", "same", "one", "take", "really", "just", "think",
    "thing",
}


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def timestamp_to_datetime(value):
    """Parse Firebase/Firestore epoch milliseconds or ISO timestamps."""
    if value is None or value == "":
        return None

    try:
        ts = float(value)

        # Dataset timestamps are epoch milliseconds.
        if ts < 10_000_000_000:
            ts *= 1000

        return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)

    except (TypeError, ValueError, OverflowError, OSError):
        pass

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).astimezone(timezone.utc)
        except ValueError:
            return None

    return None


def timestamp_to_date(value):
    dt = timestamp_to_datetime(value)
    return dt.date().isoformat() if dt else None


def normalize_token(value):
    if value is None:
        return ""
    value = str(value).lower().strip().replace("#", "")
    return re.sub(r"[^a-z0-9_ -]", "", value)


def normalized_distribution(scores):
    total = sum(max(0.0, float(v)) for v in scores.values())
    if total <= 0:
        return {}

    return {
        key: round(float(value) / total, 4)
        for key, value in sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        if value > 0
    }


def confidence_for(record_count):
    if record_count >= 20:
        return "high"
    if record_count >= 5:
        return "medium"
    if record_count > 0:
        return "low"
    return "insufficient"


def classify_text(text):
    """Return keyword-hit counts by behavioral-interest category."""
    if not isinstance(text, str) or not text.strip():
        return Counter()

    normalized = text.lower()
    scores = Counter()

    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[category] += 1

    return scores


def classify_hashtag(hashtag):
    token = normalize_token(hashtag)

    if not token or token in GENERIC_WORDS:
        return Counter()

    scores = Counter()

    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            compact_keyword = keyword.replace(" ", "").replace("-", "")
            compact_token = token.replace("_", "").replace("-", "")

            if token == keyword or compact_token == compact_keyword:
                scores[category] += 1
                break

    return scores


def extract_hashtags(value):
    if isinstance(value, list):
        return [str(x) for x in value]

    if isinstance(value, str):
        return re.findall(r"#\w+", value)

    return []


def phase2_interests(profile):
    """Get declared interests from the real Phase-2 schema."""
    entries = []

    for key in ("general_interests", "professional_interest_signals"):
        values = profile.get(key, [])

        if not isinstance(values, list):
            continue

        for item in values:
            if not isinstance(item, dict):
                continue

            category = item.get("category")
            if category not in INTEREST_CATEGORIES:
                continue

            entries.append({
                "category": category,
                "score": float(item.get("score", 0) or 0),
                "source": key,
            })

    # Keep the strongest occurrence of each category.
    strongest = {}
    for item in entries:
        cat = item["category"]
        if cat not in strongest or item["score"] > strongest[cat]["score"]:
            strongest[cat] = item

    return sorted(
        strongest.values(),
        key=lambda x: x["score"],
        reverse=True
    )


def interest_alignment(declared, observed):
    declared_set = {x["category"] for x in declared}
    observed_set = {x["category"] for x in observed}

    if not declared_set or not observed_set:
        return "insufficient"

    overlap = declared_set & observed_set

    if not overlap:
        return "low"

    ratio = len(overlap) / len(declared_set)

    if ratio >= 0.67:
        return "high"

    return "medium"


def main():
    print("=" * 70)
    print("       SIH PHASE 3 — CORRECTED BEHAVIORAL PROFILES")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------
    print("\n[1/8] Loading existing analytics...")

    user_evidence = load_json(USER_EVIDENCE_FILE)
    interest_profiles = load_json(INTEREST_FILE)
    enriched_text = load_json(ENRICHED_FILE)
    topic_analysis = load_json(TOPIC_FILE)
    posts = load_json(POSTS_FILE)
    comments = load_json(COMMENTS_FILE)

    users = user_evidence.get("users", user_evidence)

    if not isinstance(users, dict):
        raise ValueError("Unexpected user_evidence.json structure")

    print(f"      Users: {len(users)}")
    print(f"      Enriched records: {len(enriched_text)}")
    print(f"      Topic assignments: {len(topic_analysis.get('assignments', []))}")

    # ------------------------------------------------------------
    # 2. Index existing NLP results ONCE
    # ------------------------------------------------------------
    print("\n[2/8] Indexing NLP and topic evidence...")

    text_by_user = defaultdict(list)
    topic_by_user = defaultdict(list)

    valid_timestamps = 0

    for record in enriched_text:
        uid = record.get("author_id")
        if not uid:
            continue

        text_by_user[uid].append(record)

        if timestamp_to_datetime(record.get("created_at")):
            valid_timestamps += 1

    for assignment in topic_analysis.get("assignments", []):
        uid = assignment.get("author_id")
        if uid:
            topic_by_user[uid].append(assignment)

    # ------------------------------------------------------------
    # 3. Build activity / engagement evidence
    # ------------------------------------------------------------
    print("\n[3/8] Building activity and engagement evidence...")

    posts_by_user = Counter()
    comments_by_user = Counter()
    meaningful_comments_by_user = Counter()
    reactions_by_user = Counter()
    hashtags_by_user = defaultdict(list)
    active_dates_by_user = defaultdict(set)

    for post in posts:
        uid = post.get("author_id")
        if not uid:
            continue

        posts_by_user[uid] += 1

        liked_by = post.get("liked_by")
        if liked_by is None:
            liked_by = post.get("likedBy", [])

        if isinstance(liked_by, list):
            reactions_by_user[uid] += len(liked_by)

        hashtags_by_user[uid].extend(
            extract_hashtags(post.get("hashtags"))
        )
        hashtags_by_user[uid].extend(
            extract_hashtags(post.get("description"))
        )

        day = timestamp_to_date(post.get("created_at"))
        if day:
            active_dates_by_user[uid].add(day)

    for comment in comments:
        uid = comment.get("author_id")
        if not uid:
            continue

        comments_by_user[uid] += 1

        text = str(comment.get("text") or "").strip()
        if len(text) >= 8:
            meaningful_comments_by_user[uid] += 1

        day = timestamp_to_date(comment.get("created_at"))
        if day:
            active_dates_by_user[uid].add(day)

    # Also include enriched records, since they are the authoritative
    # timestamped content used by the NLP pipeline.
    for uid, records in text_by_user.items():
        for record in records:
            day = timestamp_to_date(record.get("created_at"))
            if day:
                active_dates_by_user[uid].add(day)

    # ------------------------------------------------------------
    # 4. Build user profiles
    # ------------------------------------------------------------
    print("\n[4/8] Building corrected user profiles...")

    output_users = {}

    aggregate_sentiment = Counter()
    aggregate_emotion = Counter()
    aggregate_segments = Counter()
    aggregate_interest_users = Counter()
    aggregate_age_interest = defaultdict(Counter)
    aggregate_age_sentiment = defaultdict(Counter)

    for user_id in users:
        phase2 = interest_profiles.get(user_id, {})

        # FIX #1:
        # The actual Phase-2 schema is:
        # users[user_id]["age"]["bracket"]
        age = phase2.get("age") or {}
        age_bracket = age.get("bracket") or "Unknown"
        age_source = age.get("source") or "unknown"

        records = text_by_user.get(user_id, [])
        assignments = topic_by_user.get(user_id, [])

        # ----------------------------
        # Sentiment
        # ----------------------------
        sentiment_counts = Counter(
            record.get("sentiment")
            for record in records
            if record.get("sentiment")
        )

        sentiment_total = sum(sentiment_counts.values())

        sentiment_distribution = (
            {
                label: round(count / sentiment_total, 4)
                for label, count in sentiment_counts.items()
            }
            if sentiment_total
            else {}
        )

        dominant_sentiment = (
            sentiment_counts.most_common(1)[0][0]
            if sentiment_counts
            else "insufficient_data"
        )

        # ----------------------------
        # Emotion
        # ----------------------------
        emotion_counts = Counter(
            record.get("emotion")
            for record in records
            if record.get("emotion")
        )

        top_emotions = [
            {"emotion": label, "count": count}
            for label, count in emotion_counts.most_common(5)
        ]

        # ----------------------------
        # Topic activity
        # ----------------------------
        topic_counts = Counter(
            str(a.get("topic_id"))
            for a in assignments
            if a.get("topic_id") is not None
        )

        topic_total = sum(topic_counts.values())

        top_topics = [
            {
                "topic_id": topic_id,
                "mentions": count,
                "share": round(count / topic_total, 4)
                if topic_total else 0.0,
            }
            for topic_id, count in topic_counts.most_common(10)
        ]

        topic_diversity = len(topic_counts)
        topic_concentration = (
            top_topics[0]["share"] if top_topics else 0.0
        )

        # ----------------------------
        # Activity
        # ----------------------------
        post_count = posts_by_user.get(user_id, 0)
        comment_count = comments_by_user.get(user_id, 0)
        meaningful_count = meaningful_comments_by_user.get(user_id, 0)
        reaction_count = reactions_by_user.get(user_id, 0)

        total_actions = post_count + comment_count

        # FIX #2:
        # Unique calendar dates from real epoch-ms timestamps.
        active_days = len(active_dates_by_user.get(user_id, set()))

        if total_actions == 0:
            activity_level = "inactive"
        elif total_actions >= 50:
            activity_level = "high"
        elif total_actions >= 10:
            activity_level = "medium"
        else:
            activity_level = "low"

        if total_actions == 0:
            engagement_level = "insufficient_data"
        elif reaction_count >= 20:
            engagement_level = "high"
        elif reaction_count >= 5:
            engagement_level = "medium"
        else:
            engagement_level = "low"

        # ----------------------------
        # Declared interests
        # ----------------------------
        declared_entries = phase2_interests(phase2)

        declared_interests = [
            item["category"]
            for item in declared_entries[:5]
        ]

        # ----------------------------
        # Behavioral interest evidence
        # ----------------------------
        # FIX #3:
        # Scores are built from explainable evidence and normalized
        # to a per-user 0..1 distribution.

        evidence = {
            category: {
                "post_signals": 0,
                "comment_signals": 0,
                "topic_mentions": 0,
                "hashtag_mentions": 0,
                "keyword_mentions": 0,
            }
            for category in INTEREST_CATEGORIES
        }

        # Existing Phase-2 observed content preferences.
        observed_preferences = phase2.get(
            "observed_content_preferences", []
        )

        if isinstance(observed_preferences, list):
            for item in observed_preferences:
                if not isinstance(item, dict):
                    continue

                category = item.get("category")
                if category not in evidence:
                    continue

                mentions = float(
                    item.get("mentions", 0)
                    or item.get("score", 0)
                    or 0
                )

                # Retain this as content evidence.
                evidence[category]["keyword_mentions"] += mentions

        # Hashtag evidence.
        for hashtag in hashtags_by_user.get(user_id, []):
            for category, hits in classify_hashtag(hashtag).items():
                evidence[category]["hashtag_mentions"] += hits

        # Actual post/comment text evidence.
        for record in records:
            text = str(record.get("text") or "")
            source = record.get("source_type")

            mapped = classify_text(text)

            for category, hits in mapped.items():
                evidence[category]["keyword_mentions"] += hits

                if source == "post":
                    evidence[category]["post_signals"] += hits
                elif source == "comment":
                    evidence[category]["comment_signals"] += hits

        # Topic evidence.
        for assignment in assignments:
            try:
                topic_id = int(assignment.get("topic_id"))
            except (TypeError, ValueError):
                continue

            category = TOPIC_CATEGORY_MAP.get(topic_id)

            if category:
                evidence[category]["topic_mentions"] += 1

        raw_scores = {}

        for category, ev in evidence.items():
            post_signal = min(ev["post_signals"] / 5.0, 1.0)
            comment_signal = min(ev["comment_signals"] / 10.0, 1.0)
            topic_signal = min(ev["topic_mentions"] / 10.0, 1.0)
            hashtag_signal = min(ev["hashtag_mentions"] / 5.0, 1.0)
            keyword_signal = min(ev["keyword_mentions"] / 10.0, 1.0)

            raw = (
                0.25 * post_signal +
                0.20 * comment_signal +
                0.20 * topic_signal +
                0.15 * hashtag_signal +
                0.20 * keyword_signal
            )

            if raw > 0:
                raw_scores[category] = raw

        normalized_scores = normalized_distribution(raw_scores)

        behavioral_interests = []

        for category, score in list(normalized_scores.items())[:5]:
            ev = evidence[category]

            behavioral_interests.append({
                "category": category,
                "score": score,
                "evidence": ev,
            })

            aggregate_interest_users[category] += 1
            aggregate_age_interest[age_bracket][category] += 1

        # ----------------------------
        # Interest alignment
        # ----------------------------
        observed_for_alignment = [
            {"category": item["category"]}
            for item in behavioral_interests
            if item["score"] >= 0.10
        ]

        alignment = interest_alignment(
            declared_entries,
            observed_for_alignment,
        )

        overlap = sorted(
            {x["category"] for x in declared_entries}
            &
            {x["category"] for x in observed_for_alignment}
        )

        # ----------------------------
        # Temporal interest profile
        # ----------------------------
        daily_category_counts = defaultdict(Counter)

        for record in records:
            day = timestamp_to_date(record.get("created_at"))
            if not day:
                continue

            for category, hits in classify_text(
                str(record.get("text") or "")
            ).items():
                daily_category_counts[day][category] += hits

        temporal_days = []

        for day in sorted(daily_category_counts):
            temporal_days.append({
                "date": day,
                "top_interests": [
                    {"category": category, "signals": count}
                    for category, count
                    in daily_category_counts[day].most_common(3)
                ],
            })

        # ----------------------------
        # Behavioral segment
        # ----------------------------
        if total_actions == 0:
            segment = "Low Activity"
        elif post_count >= 5 and reaction_count >= 10:
            segment = "High-Engagement Creator"
        elif post_count >= 5 and comment_count >= 5:
            segment = "Creator & Participant"
        elif post_count >= 5:
            segment = "Content Creator"
        elif comment_count >= 10:
            segment = "Highly Interactive User"
        elif topic_diversity == 1 and total_actions >= 5:
            segment = "Topic Specialist"
        elif topic_diversity >= 4 and total_actions >= 5:
            segment = "Multi-Topic Participant"
        elif comment_count > 0:
            segment = "Community Participant"
        else:
            segment = "Light Participant"

        aggregate_segments[segment] += 1

        # ----------------------------
        # Confidence
        # ----------------------------
        confidence = confidence_for(len(records))

        # ----------------------------
        # Aggregate age x sentiment
        # ----------------------------
        if sentiment_total:
            aggregate_age_sentiment[age_bracket].update(
                sentiment_counts
            )

        # ----------------------------
        # Final user profile
        # ----------------------------
        output_users[user_id] = {
            "user_id": user_id,

            "demographics": {
                "age_bracket": age_bracket,
                "age_source": age_source,
            },

            "declared_interests": declared_interests,

            "behavioral_interests": behavioral_interests,

            "topic_affinity": {
                "top_topics": top_topics,
                "topic_count": topic_diversity,
                "topic_concentration": round(
                    topic_concentration,
                    4
                ),
                "classification": (
                    "Topic Specialist"
                    if topic_diversity == 1
                    and topic_total >= 5
                    else "Multi-topic User"
                    if topic_diversity >= 4
                    else "General Participant"
                    if topic_diversity > 0
                    else "Insufficient Data"
                ),
            },

            "sentiment_profile": {
                "distribution": sentiment_distribution,
                "dominant": dominant_sentiment,
                "total_analyzed": sentiment_total,
            },

            "emotion_profile": {
                "top_emotions": top_emotions,
                "total_analyzed": sum(
                    emotion_counts.values()
                ),
            },

            "engagement_profile": {
                "reactions_received": reaction_count,
                "engagement_level": engagement_level,
            },

            "activity_profile": {
                "posts": post_count,
                "comments": comment_count,
                "meaningful_comments": meaningful_count,
                "meaningful_comment_ratio": round(
                    meaningful_count / comment_count,
                    4,
                ) if comment_count else 0.0,
                "active_days": active_days,
                "total_actions": total_actions,
                "activity_level": activity_level,
            },

            "interest_alignment": {
                "label": alignment,
                "declared_count": len(declared_entries),
                "observed_count": len(observed_for_alignment),
                "overlap": overlap,
            },

            "temporal_interest_profile": {
                "days_with_observed_interest": len(
                    temporal_days
                ),
                "daily": temporal_days,
            },

            "behavioral_segment": segment,

            "confidence": {
                "overall": confidence,
                "content_records": len(records),
                "note": (
                    "Confidence reflects evidence volume, not "
                    "certainty about the person."
                ),
            },
        }

        aggregate_sentiment.update(sentiment_counts)
        aggregate_emotion.update(emotion_counts)

    # ------------------------------------------------------------
    # 5. Aggregate statistics
    # ------------------------------------------------------------
    print("\n[5/8] Building aggregate audience statistics...")

    age_distribution = Counter(
        profile["demographics"]["age_bracket"]
        for profile in output_users.values()
    )

    total_sentiment = sum(aggregate_sentiment.values())
    sentiment_distribution = (
        {
            label: round(count / total_sentiment, 4)
            for label, count in aggregate_sentiment.items()
        }
        if total_sentiment
        else {}
    )

    total_emotion = sum(aggregate_emotion.values())
    emotion_distribution = (
        {
            label: round(count / total_emotion, 4)
            for label, count in aggregate_emotion.most_common()
        }
        if total_emotion
        else {}
    )

    # Age x interest: user counts, not raw post counts.
    age_interest_matrix = {}

    for age_group, counts in aggregate_age_interest.items():
        user_count = age_distribution.get(age_group, 0)

        age_interest_matrix[age_group] = {
            "user_count": user_count,
            "interest_user_counts": dict(counts),
            "interest_user_percent": {
                category: round(
                    count / user_count,
                    4,
                )
                if user_count
                else 0.0
                for category, count in counts.items()
            },
        }

    # Age x sentiment.
    age_sentiment_matrix = {}

    for age_group, counts in aggregate_age_sentiment.items():
        total = sum(counts.values())
        users_in_group = age_distribution.get(age_group, 0)

        age_sentiment_matrix[age_group] = {
            "user_count": users_in_group,
            "content_records": total,
            "sentiment_distribution": (
                {
                    label: round(count / total, 4)
                    for label, count in counts.items()
                }
                if total
                else {}
            ),
            "warning": (
                "Small age group; do not treat as representative."
                if users_in_group < 10
                else None
            ),
        }

    # ------------------------------------------------------------
    # 6. Data quality
    # ------------------------------------------------------------
    print("\n[6/8] Validating data quality...")

    active_day_values = [
        profile["activity_profile"]["active_days"]
        for profile in output_users.values()
    ]

    data_quality = {
        "users_processed": len(output_users),
        "enriched_records": len(enriched_text),
        "valid_timestamp_records": valid_timestamps,
        "timestamp_coverage": round(
            valid_timestamps / len(enriched_text),
            4,
        ) if enriched_text else 0.0,
        "unique_utc_dates": sorted({
            timestamp_to_date(record.get("created_at"))
            for record in enriched_text
            if timestamp_to_date(record.get("created_at"))
        }),
        "users_with_behavioral_evidence": sum(
            1
            for profile in output_users.values()
            if profile["confidence"]["content_records"] > 0
        ),
        "users_with_multiple_active_days": sum(
            1
            for days in active_day_values
            if days >= 2
        ),
        "max_active_days": max(
            active_day_values,
            default=0,
        ),
        "geography": (
            "insufficient_data — no reliable location field "
            "is available in the current schema"
        ),
    }

    # ------------------------------------------------------------
    # 7. Save
    # ------------------------------------------------------------
    print("\n[7/8] Saving corrected behavioral_profiles.json...")

    result = {
        "metadata": {
            "phase": "Phase 3 — Behavioral Audience Profiles",
            "users_processed": len(output_users),
            "design": "corrected_prototype",
            "models_rerun": False,
            "corrections": [
                "Phase-2 age bracket propagation fixed.",
                "Firebase epoch-millisecond timestamps parsed correctly.",
                "Active days calculated from unique UTC calendar dates.",
                "Behavioral interest scores normalized per user.",
                "Interest evidence breakdown added.",
                "Declared-vs-observed alignment added.",
                "Topic affinity and concentration added.",
                "Temporal interest activity added.",
                "Age x interest matrix added.",
                "Age x sentiment matrix added.",
            ],
        },

        "aggregate": {
            "age_distribution": dict(age_distribution),

            "behavioral_interest_distribution": dict(
                aggregate_interest_users.most_common()
            ),

            "sentiment_distribution": sentiment_distribution,

            "emotion_distribution": emotion_distribution,

            "behavioral_segments": dict(
                aggregate_segments
            ),

            "interest_alignment": dict(
                Counter(
                    profile["interest_alignment"]["label"]
                    for profile in output_users.values()
                )
            ),

            "age_interest_matrix": age_interest_matrix,

            "age_sentiment_matrix": age_sentiment_matrix,
        },

        "data_quality": data_quality,

        "methodology": {
            "behavioral_interest_score_weights": {
                "post_signals": 0.25,
                "comment_signals": 0.20,
                "topic_mentions": 0.20,
                "hashtag_mentions": 0.15,
                "keyword_mentions": 0.20,
            },

            "interest_principle": (
                "Observed interests are evidence-based signals from "
                "posts, comments, hashtags and topic assignments. "
                "Broad conversational topics are not automatically "
                "treated as interests."
            ),

            "demographic_principle": (
                "Age is used only when explicitly present in public "
                "bio evidence."
            ),

            "privacy": [
                "Usernames are not used to infer demographics.",
                "Names are not used to infer demographics.",
                "Sensitive attributes are not inferred.",
                "Geography is not inferred without reliable location evidence.",
            ],

            "confidence": (
                "Evidence-volume indicator, not a probability, "
                "psychological assessment, or ground truth."
            ),
        },

        "users": output_users,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\n[8/8] Complete.")
    print(f"      Output: {OUTPUT_FILE}")
    print(f"      Users processed: {len(output_users)}")
    print(f"      Valid timestamps: {valid_timestamps}/{len(enriched_text)}")
    print(f"      Unique UTC dates: {data_quality['unique_utc_dates']}")

    print("\nBehavioral segments:")
    for label, count in aggregate_segments.items():
        print(f"      {label}: {count}")


if __name__ == "__main__":
    main()
