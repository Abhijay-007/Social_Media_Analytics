"""
SIH Social Media Analytics
Phase 1: Unified User Evidence Builder

Inputs:
    data/processed/users.json
    data/processed/posts.json
    data/processed/comments.json

Current local prototype paths are configured below.

Output:
    user_evidence.json

Design principle:
    DO NOT infer demographics here.
    This stage only joins and measures observable evidence.
    Later stages can infer aggregate demographics from this evidence.
"""

from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
import re


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

USERS_FILE = BASE_DIR / "data" / "processed" / "users.json"
POSTS_FILE = BASE_DIR / "data" / "processed" / "posts.json"
COMMENTS_FILE = BASE_DIR / "data" / "processed" / "comments.json"

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "user_evidence.json"
)


# ============================================================
# HELPERS
# ============================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def timestamp_to_iso(value):
    if value is None:
        return None

    try:
        ts = float(value)

        # Firebase milliseconds
        if ts > 10_000_000_000:
            ts /= 1000

        return datetime.fromtimestamp(
            ts,
            tz=timezone.utc
        ).isoformat()

    except (TypeError, ValueError, OverflowError):
        return None


def safe_list(value):
    return value if isinstance(value, list) else []


def meaningful_text(text, min_chars=5):
    """
    Used only to decide whether text is informative enough
    for behavioral/language evidence.

    It does NOT modify the original text.
    """
    if not isinstance(text, str):
        return False

    cleaned = re.sub(
        r"[\W_]+",
        "",
        text,
        flags=re.UNICODE
    )

    return len(cleaned) >= min_chars


def text_length(text):
    if not isinstance(text, str):
        return 0

    return len(text.strip())


def engagement_reaction_count(reactions):
    if not isinstance(reactions, dict):
        return 0

    return sum(
        len(v)
        for v in reactions.values()
        if isinstance(v, list)
    )


# ============================================================
# PROFILE EVIDENCE
# ============================================================

def build_profile_index(users):

    profiles = {}

    for user in users:

        user_id = user.get("user_id")

        if not user_id:
            continue

        followers = user.get("followers", [])
        following = user.get("following", [])

        profiles[user_id] = {
            "user_id": user_id,
            "username": user.get("username"),
            "bio": user.get("bio") or "",
            "verified": bool(user.get("verified", False)),

            "followers_count": (
                len(followers)
                if isinstance(followers, list)
                else int(followers or 0)
            ),

            "following_count": (
                len(following)
                if isinstance(following, list)
                else int(following or 0)
            ),

            "joined_at": user.get("joined_at"),
            "last_seen": user.get("last_seen"),
            "online": bool(user.get("online", False)),
        }

    return profiles


# ============================================================
# POST EVIDENCE
# ============================================================

def process_posts(posts, evidence):

    post_author_counts = Counter()
    post_hashtag_counts = defaultdict(Counter)
    post_reaction_counts = Counter()
    post_timestamps = defaultdict(list)

    total_posts = 0

    for post in posts:

        author_id = post.get("author_id")

        if not author_id:
            continue

        total_posts += 1

        post_author_counts[author_id] += 1

        hashtags = safe_list(post.get("hashtags"))

        for hashtag in hashtags:

            if isinstance(hashtag, str):
                normalized = hashtag.strip().lower()

                if normalized:
                    post_hashtag_counts[
                        author_id
                    ][normalized] += 1

        reaction_count = engagement_reaction_count(
            post.get("reactions")
        )

        post_reaction_counts[
            author_id
        ] += reaction_count

        timestamp = post.get("created_at")

        if timestamp is not None:
            post_timestamps[
                author_id
            ].append(timestamp)

        record = evidence.setdefault(
            author_id,
            {}
        )

        record.setdefault(
            "content",
            {
                "posts": 0,
                "comments": 0,
                "meaningful_comments": 0,
                "post_reactions_received": 0,
                "comments_given": 0,
                "post_hashtags": {},
                "activity_timestamps": []
            }
        )

    for author_id, count in post_author_counts.items():

        record = evidence.setdefault(
            author_id,
            {}
        )

        content = record.setdefault(
            "content",
            {}
        )

        content["posts"] = count

        content["post_reactions_received"] = (
            post_reaction_counts[author_id]
        )

        content["post_hashtags"] = dict(
            post_hashtag_counts[author_id]
        )

        content["activity_timestamps"].extend(
            post_timestamps[author_id]
        )

    return total_posts


# ============================================================
# COMMENT EVIDENCE
# ============================================================

def process_comments(comments, evidence):

    comment_author_counts = Counter()
    meaningful_comment_counts = Counter()
    comment_timestamps = defaultdict(list)

    total_comments = 0

    for comment in comments:

        author_id = comment.get("author_id")

        if not author_id:
            continue

        total_comments += 1

        text = comment.get("text") or ""

        comment_author_counts[
            author_id
        ] += 1

        if meaningful_text(text):
            meaningful_comment_counts[
                author_id
            ] += 1

        timestamp = comment.get("created_at")

        if timestamp is not None:
            comment_timestamps[
                author_id
            ].append(timestamp)

    for author_id, count in comment_author_counts.items():

        record = evidence.setdefault(
            author_id,
            {}
        )

        content = record.setdefault(
            "content",
            {}
        )

        content["comments"] = count

        content["meaningful_comments"] = (
            meaningful_comment_counts[author_id]
        )

        content.setdefault(
            "comments_given",
            count
        )

        content.setdefault(
            "activity_timestamps",
            []
        )

        content["activity_timestamps"].extend(
            comment_timestamps[author_id]
        )

    return total_comments


# ============================================================
# BEHAVIORAL FEATURES
# ============================================================

def calculate_behavioral_features(record):

    profile = record["profile"]
    content = record["content"]

    posts = content.get("posts", 0)
    comments = content.get("comments", 0)
    meaningful_comments = content.get(
        "meaningful_comments",
        0
    )

    followers = profile.get(
        "followers_count",
        0
    )

    following = profile.get(
        "following_count",
        0
    )

    total_activity = posts + comments

    meaningful_ratio = (
        meaningful_comments / comments
        if comments
        else 0.0
    )

    follower_following_ratio = (
        followers / following
        if following
        else float(followers)
    )

    timestamps = [
        t for t in content.get(
            "activity_timestamps",
            []
        )
        if isinstance(t, (int, float))
    ]

    unique_days = set()

    for timestamp in timestamps:

        iso = timestamp_to_iso(timestamp)

        if iso:
            unique_days.add(
                iso[:10]
            )

    active_days = len(unique_days)

    if total_activity == 0:
        activity_type = "inactive"

    elif posts >= 3 and comments >= 10:
        activity_type = "creator_and_participant"

    elif posts >= 3:
        activity_type = "content_creator"

    elif comments >= 10:
        activity_type = "community_participant"

    else:
        activity_type = "light_participant"

    if followers >= 20 and follower_following_ratio >= 1.5:
        network_type = "high_reach"

    elif follower_following_ratio >= 1.25:
        network_type = "audience_oriented"

    elif follower_following_ratio >= 0.8:
        network_type = "balanced"

    else:
        network_type = "community_explorer"

    return {
        "total_content_actions": total_activity,
        "active_days": active_days,

        "meaningful_comment_ratio": round(
            meaningful_ratio,
            4
        ),

        "follower_following_ratio": round(
            follower_following_ratio,
            4
        ),

        "activity_segment": activity_type,

        "network_segment": network_type
    }


# ============================================================
# FINAL RECORD CONSTRUCTION
# ============================================================

def build_evidence(users, posts, comments):

    profiles = build_profile_index(users)

    evidence = {}

    # Every known profile gets a record.
    for user_id, profile in profiles.items():

        evidence[user_id] = {
            "profile": profile,

            "content": {
                "posts": 0,
                "comments": 0,
                "meaningful_comments": 0,
                "comments_given": 0,
                "post_reactions_received": 0,
                "post_hashtags": {},
                "activity_timestamps": []
            },

            "behavior": {}
        }

    total_posts = process_posts(
        posts,
        evidence
    )

    total_comments = process_comments(
        comments,
        evidence
    )

    # Compute behavioral features.
    for record in evidence.values():

        record["behavior"] = (
            calculate_behavioral_features(
                record
            )
        )

        # Activity timestamps are implementation detail.
        # Keep only aggregate temporal features in final output.
        record["content"].pop(
            "activity_timestamps",
            None
        )

    # Detect content authors missing from profile table.
    unknown_content_users = []

    for user_id in evidence:

        if user_id not in profiles:
            unknown_content_users.append(
                user_id
            )

    # Aggregate statistics.
    post_authors = sum(
        1
        for record in evidence.values()
        if record["content"]["posts"] > 0
    )

    comment_authors = sum(
        1
        for record in evidence.values()
        if record["content"]["comments"] > 0
    )

    return {
        "metadata": {
            "stage": "phase_1_unified_user_evidence",
            "profile_users": len(profiles),
            "post_records": total_posts,
            "comment_records": total_comments,
            "post_authors": post_authors,
            "comment_authors": comment_authors,
            "unknown_content_users": unknown_content_users
        },

        "users": evidence
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 72)
    print("       SIH USER EVIDENCE BUILDER")
    print("=" * 72)

    print("\n[1/4] Loading source datasets...")

    users = load_json(USERS_FILE)
    posts = load_json(POSTS_FILE)
    comments = load_json(COMMENTS_FILE)

    print(f"      Users:    {len(users)}")
    print(f"      Posts:    {len(posts)}")
    print(f"      Comments: {len(comments)}")

    print("\n[2/4] Joining profile + content evidence...")

    result = build_evidence(
        users,
        posts,
        comments
    )

    print(
        f"      Profile users: "
        f"{result['metadata']['profile_users']}"
    )

    print(
        f"      Post authors: "
        f"{result['metadata']['post_authors']}"
    )

    print(
        f"      Comment authors: "
        f"{result['metadata']['comment_authors']}"
    )

    print("\n[3/4] Validating joins...")

    unknown = result[
        "metadata"
    ]["unknown_content_users"]

    if unknown:
        print(
            f"      WARNING: {len(unknown)} "
            f"content users missing from profiles"
        )
    else:
        print(
            "      All content authors matched "
            "to known profile IDs."
        )

    print("\n[4/4] Writing unified evidence...")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 72)
    print("PHASE 1 COMPLETE")
    print("=" * 72)

    print(
        f"\nOutput:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
