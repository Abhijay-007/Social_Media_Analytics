from pathlib import Path
import argparse
import json
import math
import re
from collections import Counter, defaultdict

# Evidence-based interest profiling.
# Sources used:
#   1) explicit public bio text
#   2) observed post hashtags from Phase 1
#   3) observed content/engagement volume
#
# This module does NOT infer sensitive attributes and does not use
# usernames/names as demographic evidence.

CATEGORY_KEYWORDS = {
    "Technology & Engineering": {
        "tech", "technology", "software", "engineer", "engineering", "developer",
        "coding", "code", "programming", "ai", "artificial intelligence", "machine learning",
        "data", "data science", "data scientist", "analytics", "open source", "startup",
        "robotics", "cyber", "cloud", "app", "web", "ui", "ux", "computer", "systems",
        "mechanical", "inventor"
    },
    "Sports": {
        "sport", "sports", "football", "soccer", "cricket", "ipl", "basketball", "nba",
        "tennis", "rugby", "hockey", "nhl", "f1", "formula1", "motorsport", "racing",
        "athletics", "track", "fitness", "gym", "cycling", "cyclist", "esports", "gaming",
        "worldcup", "premierleague", "biomechanics", "sportsscience", "sportsanalytics"
    },
    "Entertainment & Cinema": {
        "movie", "movies", "cinema", "film", "filmmaker", "filmmaking", "hollywood",
        "marvel", "mcu", "avengers", "spiderman", "anime", "television", "tv", "series",
        "supernatural", "missionimpossible", "dune", "scifi", "horror", "acting",
        "screenwriting", "storytelling", "boxoffice", "movienews", "popculture"
    },
    "Arts & Design": {
        "artist", "art", "design", "designer", "illustrator", "illustration", "photographer",
        "photography", "creative", "visualart", "ui", "ux", "fashion", "style", "interior",
        "cinematography", "visual", "dancer", "dance", "music", "musician", "producer",
        "beats", "jazz"
    },
    "Travel & Lifestyle": {
        "travel", "traveller", "traveler", "travel blogger", "explorer", "backpacking",
        "adventure", "world tour", "cultures", "cuisines", "foodie", "city", "sunsets",
        "coffee", "minimalist", "lifestyle"
    },
    "Science & Research": {
        "science", "scientist", "astrophysics", "physics", "biology", "biologist",
        "marine", "ocean", "conservation", "climate", "sustainable", "sustainability",
        "research", "space", "astronomy", "environment", "environmental"
    },
    "Business & Entrepreneurship": {
        "entrepreneur", "entrepreneurship", "startup", "business", "founder", "founding",
        "mentor", "mentoring", "finance", "marketing", "professional", "career"
    },
    "Education & Learning": {
        "student", "learning", "learn", "education", "teacher", "teaching", "academic",
        "degree", "school", "university", "books", "bookworm", "curious", "knowledge"
    },
    "Health & Wellness": {
        "health", "wellness", "skincare", "fitness", "mental health", "nutrition",
        "medicine", "medical", "sportsmedicine", "yoga", "self-care", "beauty"
    },
}

# More specific phrases receive more weight than generic single words.
PHRASE_WEIGHTS = {
    "data scientist": 3.0,
    "software engineer": 3.0,
    "ai systems engineer": 3.0,
    "machine learning": 3.0,
    "artificial intelligence": 3.0,
    "full-stack developer": 3.0,
    "climate activist": 3.0,
    "marine biologist": 3.0,
    "environmental lawyer": 3.0,
    "foodie & travel blogger": 3.0,
    "ux designer": 3.0,
    "interior designer": 3.0,
    "digital artist": 3.0,
    "music producer": 3.0,
    "e-sports player": 3.0,
    "content creator": 2.5,
    "photographer": 2.5,
    "filmmaker": 2.5,
}

STOP_HASH = {
    "the", "and", "for", "with", "from", "this", "that", "one", "day", "daily",
    "life", "good", "best", "love", "new", "news", "team", "people", "world"
}

def normalize(text):
    text = str(text or "").lower()
    text = text.replace("#", " ")
    text = re.sub(r"[_/|]+", " ", text)
    text = re.sub(r"[^a-z0-9+#&.\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def clean_hashtag_key(raw):
    raw = normalize(raw)
    # Phase 1 can contain either a single hashtag or a bundled hashtag string.
    return raw

def extract_age(bio):
    m = re.search(r"\b(1[3-9]|[2-9]\d)\b", str(bio or ""))
    if not m:
        return None
    age = int(m.group(1))
    return age if 13 <= age <= 99 else None

def age_bracket(age):
    if age is None:
        return "Unknown"
    if age <= 17:
        return "13–17"
    if age <= 24:
        return "18–24"
    if age <= 34:
        return "25–34"
    if age <= 44:
        return "35–44"
    if age <= 54:
        return "45–54"
    return "55+"

def category_scores(bio, hashtags):
    bio_n = normalize(bio)
    hash_text = " ".join(normalize(h) for h in hashtags)
    combined = f"{bio_n} {hash_text}".strip()
    scores = Counter()
    evidence = defaultdict(list)

    # Explicit phrase evidence from bio.
    for phrase, weight in PHRASE_WEIGHTS.items():
        p = normalize(phrase)
        if p in bio_n:
            for category, words in CATEGORY_KEYWORDS.items():
                if any(p == normalize(w) or p in normalize(w) or normalize(w) in p
                       for w in words):
                    scores[category] += weight
                    evidence[category].append({
                        "source": "bio",
                        "match": phrase,
                        "weight": weight
                    })

    # Token/phrase matching across bio and hashtag evidence.
    for category, words in CATEGORY_KEYWORDS.items():
        for word in words:
            w = normalize(word)
            if not w:
                continue
            if w in combined:
                # Hashtag matches are stronger than a generic word in a bio.
                in_hash = w in hash_text
                weight = 2.0 if in_hash else 1.25
                if len(w) <= 4 and not in_hash:
                    weight *= 0.7
                scores[category] += weight
                evidence[category].append({
                    "source": "hashtag" if in_hash else "bio",
                    "match": word,
                    "weight": round(weight, 2)
                })

    return scores, evidence

def confidence(score, evidence_count, source_types):
    # Confidence is evidence strength, not statistical certainty.
    if score >= 5 and evidence_count >= 3 and len(source_types) >= 2:
        return "high"
    if score >= 3 or (score >= 2 and evidence_count >= 2):
        return "medium"
    return "low"

def classify_user(user_id, record):
    profile = record.get("profile", {})
    content = record.get("content", {})
    behavior = record.get("behavior", {})
    bio = str(profile.get("bio") or "")
    hashtags = list((content.get("post_hashtags") or {}).keys())

    scores, evidence = category_scores(bio, hashtags)
    # Drop weak categories.
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    interests = []
    for category, score in ranked:
        ev = evidence[category]
        if score < 1.4:
            continue
        source_types = {x["source"] for x in ev}
        interests.append({
            "category": category,
            "score": round(score, 3),
            "confidence": confidence(score, len(ev), source_types),
            "evidence": ev[:12]
        })

    interests = interests[:5]

    total_evidence = sum(len(v) for v in evidence.values())
    if not interests:
        interest_breadth = "unknown"
        overall_conf = "insufficient"
    else:
        breadth_n = len([x for x in interests if x["score"] >= 2.0])
        interest_breadth = (
            "broad" if breadth_n >= 4 else
            "multi_interest" if breadth_n >= 2 else
            "focused"
        )
        high = sum(x["confidence"] == "high" for x in interests)
        medium = sum(x["confidence"] == "medium" for x in interests)
        if high >= 1 or (medium >= 2 and total_evidence >= 4):
            overall_conf = "high"
        elif medium >= 1:
            overall_conf = "medium"
        else:
            overall_conf = "low"

    # Content preference is deliberately based only on observed hashtags/content,
    # not on bio-only claims.
    observed_scores = Counter()
    observed_evidence = defaultdict(list)
    for category, words in CATEGORY_KEYWORDS.items():
        for raw in hashtags:
            h = normalize(raw)
            for word in words:
                w = normalize(word)
                if w and w in h:
                    observed_scores[category] += 1
                    observed_evidence[category].append(word)

    observed_ranked = sorted(observed_scores.items(), key=lambda x: x[1], reverse=True)
    content_preferences = [
        {
            "category": cat,
            "mentions": count,
            "evidence": sorted(set(observed_evidence[cat]))[:10]
        }
        for cat, count in observed_ranked[:5]
    ]

    age = extract_age(bio)

    return {
        "user_id": user_id,
        "age": {
            "value": age,
            "bracket": age_bracket(age),
            "source": "explicit_bio" if age is not None else "unknown"
        },
        "professional_interest_signals": [
            x for x in interests
            if x["category"] in {
                "Technology & Engineering",
                "Business & Entrepreneurship",
                "Science & Research",
                "Education & Learning",
                "Health & Wellness",
                "Arts & Design"
            }
        ][:3],
        "general_interests": interests,
        "observed_content_preferences": content_preferences,
        "interest_breadth": interest_breadth,
        "confidence": overall_conf,
        "behavior": {
            "activity_segment": behavior.get("activity_segment", "unknown"),
            "network_segment": behavior.get("network_segment", "unknown"),
            "posts": content.get("posts", 0),
            "comments": content.get("comments", 0),
            "meaningful_comments": content.get("meaningful_comments", 0),
            "post_reactions_received": content.get("post_reactions_received", 0),
            "active_days": behavior.get("active_days", 0)
        },
        "method": {
            "bio_evidence": bool(bio.strip()),
            "hashtag_evidence": bool(hashtags),
            "username_used_for_interest_inference": False,
            "sensitive_attribute_inference": False
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    here = Path(__file__).resolve()
    base = here.parent.parent
    input_path = Path(args.input) if args.input else base / "data" / "processed" / "user_evidence.json"
    output_path = Path(args.output) if args.output else base / "data" / "processed" / "interest_profiles.json"

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    users = data.get("users", {})
    profiles = {}
    age_counts = Counter()
    interest_counts = Counter()
    professional_counts = Counter()
    content_interest_counts = Counter()
    confidence_counts = Counter()
    breadth_counts = Counter()

    for uid, record in users.items():
        result = classify_user(uid, record)
        profiles[uid] = result
        age_counts[result["age"]["bracket"]] += 1
        confidence_counts[result["confidence"]] += 1
        breadth_counts[result["interest_breadth"]] += 1
        for x in result["general_interests"]:
            interest_counts[x["category"]] += 1
        for x in result["professional_interest_signals"]:
            professional_counts[x["category"]] += 1
        for x in result["observed_content_preferences"]:
            content_interest_counts[x["category"]] += 1

    output = {
        "metadata": {
            "stage": "phase_2_content_and_interest_profiling",
            "source_stage": data.get("metadata", {}).get("stage"),
            "profile_users": len(profiles),
            "method": "evidence_based_bio_and_hashtag_classification",
            "important_limitations": [
                "Interests are evidence-based signals, not ground truth.",
                "Age is used only when explicitly present in public bio text.",
                "Geography is not inferred from names, usernames, language, or writing style.",
                "Sensitive attributes are not inferred.",
                "Content preference requires observed hashtag/content evidence; bio-only claims remain profile interest signals."
            ]
        },
        "aggregate": {
            "age_distribution": dict(sorted(age_counts.items())),
            "interest_distribution": dict(interest_counts.most_common()),
            "professional_interest_distribution": dict(professional_counts.most_common()),
            "observed_content_interest_distribution": dict(content_interest_counts.most_common()),
            "interest_breadth_distribution": dict(breadth_counts.most_common()),
            "confidence_distribution": dict(confidence_counts.most_common())
        },
        "users": profiles
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Users processed: {len(profiles)}")
    print("Age distribution:")
    for k, v in sorted(age_counts.items()):
        print(f"  {k}: {v}")
    print("Top interests:")
    for k, v in interest_counts.most_common(10):
        print(f"  {k}: {v}")
    print("Confidence:")
    for k, v in confidence_counts.most_common():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
