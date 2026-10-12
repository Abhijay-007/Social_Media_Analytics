"""
SIH SOCIAL MEDIA ANALYTICS
Automated Demographic Profiling

Input:
    data/processed/users.json

Output:
    data/processed/demographic_analysis.json

Purpose:
    Build aggregate, anonymized demographic and behavioral
    profiles from public user profile information.
"""

from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import re
import statistics


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "users.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "demographic_analysis.json"


# ============================================================
# PROFESSIONAL / INTEREST CATEGORIES
# ============================================================

CATEGORY_PATTERNS = {

    "Technology & Engineering": [
        r"\bsoftware\b",
        r"\bdeveloper\b",
        r"\bdevelopment\b",
        r"\bcoder\b",
        r"\bcoding\b",
        r"\bprogrammer\b",
        r"\btechnology\b",
        r"\btech\b",
        r"\bengineer\b",
        r"\bengineering\b",
        r"\bai\b",
        r"\bartificial intelligence\b",
        r"\bmachine learning\b",
        r"\bdata scientist\b",
        r"\bdata science\b",
        r"\bopen source\b",
        r"\bsystems engineer\b",
        r"\bfull-stack\b",
        r"\bcyber\b",
        r"\bux\b",
        r"\bui\b",
    ],

    "Business & Entrepreneurship": [
        r"\bentrepreneur\b",
        r"\bentrepreneurship\b",
        r"\bfounder\b",
        r"\bstartup\b",
        r"\bbusiness\b",
        r"\bmarketing\b",
        r"\bfinance\b",
        r"\binvestor\b",
        r"\binvest\b",
        r"\bmentor\b",
    ],

    "Arts & Design": [
        r"\bartist\b",
        r"\bart\b",
        r"\bdesigner\b",
        r"\bdesign\b",
        r"\bphotographer\b",
        r"\bphotography\b",
        r"\bfilmmaker\b",
        r"\bfilm\b",
        r"\bdance\b",
        r"\bdancer\b",
        r"\bmusic\b",
        r"\bmusician\b",
        r"\bproducer\b",
        r"\bbeats\b",
        r"\billustrator\b",
        r"\bcreative\b",
    ],

    "Science & Research": [
        r"\bscience\b",
        r"\bscientist\b",
        r"\bastrophysics\b",
        r"\bphysics\b",
        r"\bbiologist\b",
        r"\bbiology\b",
        r"\bresearch\b",
        r"\bresearcher\b",
        r"\bmarine\b",
        r"\bclimate\b",
        r"\bsustainable\b",
        r"\bsustainability\b",
    ],

    "Education": [
        r"\bstudent\b",
        r"\bteacher\b",
        r"\bteaching\b",
        r"\beducation\b",
        r"\blearning\b",
        r"\bcollege\b",
        r"\bschool\b",
        r"\bdegree\b",
        r"\baspiring\b",
    ],

    "Sports & Fitness": [
        r"\bcricket\b",
        r"\bfootball\b",
        r"\bsports\b",
        r"\bfitness\b",
        r"\brunner\b",
        r"\brunning\b",
        r"\bathlete\b",
        r"\bgym\b",
        r"\bf1\b",
        r"\bformula 1\b",
    ],

    "Travel & Lifestyle": [
        r"\btravel\b",
        r"\btraveller\b",
        r"\btraveler\b",
        r"\bexplorer\b",
        r"\bbackpacking\b",
        r"\badventure\b",
        r"\bfoodie\b",
        r"\bcuisines\b",
        r"\bsunsets\b",
        r"\bcoffee\b",
        r"\bchai\b",
        r"\bbooks\b",
        r"\bbookworm\b",
        r"\bminimalist\b",
    ],

    "Media & Entertainment": [
        r"\bmeme\b",
        r"\bmarvel\b",
        r"\bmcu\b",
        r"\bgaming\b",
        r"\bgamer\b",
        r"\bmovies\b",
        r"\bcinema\b",
        r"\bcontent creator\b",
        r"\bcontent\b",
        r"\bstoryteller\b",
    ],

    "Healthcare": [
        r"\bdoctor\b",
        r"\bmedical\b",
        r"\bmedicine\b",
        r"\bhealthcare\b",
        r"\bnurse\b",
        r"\bpharma\b",
        r"\bbiomedical\b",
    ],
}


# ============================================================
# INTEREST KEYWORDS
# ============================================================

INTEREST_KEYWORDS = {

    "Technology": [
        "technology",
        "tech",
        "coding",
        "code",
        "developer",
        "software",
        "ai",
        "machine learning",
        "programming",
        "open source",
    ],

    "Science": [
        "science",
        "astrophysics",
        "physics",
        "biology",
        "biologist",
        "research",
        "climate",
        "ocean",
    ],

    "Sports": [
        "cricket",
        "football",
        "sports",
        "fitness",
        "f1",
        "formula",
        "athlete",
        "gym",
    ],

    "Music": [
        "music",
        "musician",
        "producer",
        "beats",
        "playlist",
        "song",
    ],

    "Arts & Photography": [
        "artist",
        "art",
        "photographer",
        "photography",
        "design",
        "designer",
        "filmmaker",
        "dance",
        "dancer",
    ],

    "Travel": [
        "travel",
        "traveler",
        "traveller",
        "explorer",
        "backpacking",
        "adventure",
        "world tour",
    ],

    "Food": [
        "foodie",
        "food",
        "cuisine",
        "cuisines",
        "cooking",
    ],

    "Books & Reading": [
        "book",
        "books",
        "bookworm",
        "reading",
    ],

    "Gaming": [
        "gaming",
        "gamer",
        "game",
        "quest",
    ],

    "Movies & Entertainment": [
        "marvel",
        "mcu",
        "movie",
        "movies",
        "cinema",
        "film",
        "meme",
    ],
}


# ============================================================
# DATA LOADING
# ============================================================

def load_users():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    if not isinstance(users, list):
        raise ValueError("users.json must contain a list of users.")

    return users


# ============================================================
# AGE EXTRACTION
# ============================================================

def extract_age(bio):
    """
    Extract explicit age from bio.

    Examples:
        '21 · Tech enthusiast'
        '28 · Mechanical engineer'
        '17 · Just vibing'

    Does not attempt to infer age from username or name.
    """

    if not bio:
        return None

    # Age normally appears at beginning of bio.
    match = re.match(
        r"^\s*(\d{1,3})\s*(?:·|\||-|,)",
        bio
    )

    if not match:
        return None

    age = int(match.group(1))

    # Reasonable validation range.
    if 13 <= age <= 100:
        return age

    return None


def age_bracket(age):

    if age is None:
        return "unknown"

    if age < 18:
        return "13-17"

    if age <= 24:
        return "18-24"

    if age <= 34:
        return "25-34"

    if age <= 44:
        return "35-44"

    if age <= 54:
        return "45-54"

    return "55+"


# ============================================================
# PROFESSIONAL CATEGORY DETECTION
# ============================================================

def detect_professional_categories(bio):

    if not bio:
        return []

    text = bio.lower()

    categories = []

    for category, patterns in CATEGORY_PATTERNS.items():

        for pattern in patterns:

            if re.search(pattern, text):

                categories.append(category)
                break

    return categories


# ============================================================
# GENERAL INTEREST DETECTION
# ============================================================

def detect_interests(bio):

    if not bio:
        return []

    text = bio.lower()

    interests = []

    for interest, keywords in INTEREST_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                interests.append(interest)
                break

    return interests


# ============================================================
# NETWORK METRICS
# ============================================================

def get_relationship_count(value):

    if isinstance(value, list):
        return len(value)

    if isinstance(value, int):
        return value

    return 0


def calculate_network_metrics(users):

    metrics = []

    for user in users:

        followers = get_relationship_count(
            user.get("followers", [])
        )

        following = get_relationship_count(
            user.get("following", [])
        )

        ratio = followers / max(following, 1)

        metrics.append({
            "followers": followers,
            "following": following,
            "ratio": ratio
        })

    return metrics


# ============================================================
# NETWORK SEGMENTATION
# ============================================================

def network_segment(followers, following):

    ratio = followers / max(following, 1)

    # Strong audience / influence
    if followers >= 20 and ratio >= 1.5:
        return "high_reach"

    # More followers than connections
    if ratio >= 1.25:
        return "audience_oriented"

    # Roughly balanced
    if 0.8 <= ratio <= 1.25:
        return "balanced_network"

    # Follows considerably more accounts
    if ratio < 0.8:
        return "community_explorer"

    return "general"


# ============================================================
# ACTIVITY SEGMENTATION
# ============================================================

def activity_segment(user):

    online = bool(user.get("online", False))

    if online:
        return "currently_active"

    return "currently_inactive"


# ============================================================
# TIMESTAMP UTILITIES
# ============================================================

def timestamp_to_datetime(timestamp):

    if timestamp is None:
        return None

    try:

        timestamp = float(timestamp)

        # Firebase timestamps are milliseconds.
        if timestamp > 10_000_000_000:
            timestamp /= 1000

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc
        )

    except Exception:

        return None


# ============================================================
# ACCOUNT AGE
# ============================================================

def calculate_account_age_days(user):

    joined = timestamp_to_datetime(
        user.get("joined_at")
    )

    if joined is None:
        return None

    last_seen = timestamp_to_datetime(
        user.get("last_seen")
    )

    if last_seen is None:
        return None

    days = (
        last_seen - joined
    ).total_seconds() / 86400

    return max(0, round(days, 2))


# ============================================================
# DEMOGRAPHIC ANALYSIS
# ============================================================

def analyze_age(users):

    ages = []

    for user in users:

        age = extract_age(
            user.get("bio", "")
        )

        if age is not None:
            ages.append(age)

    distribution = Counter(
        age_bracket(age)
        for age in ages
    )

    return {
        "available_profiles": len(ages),
        "missing_profiles": len(users) - len(ages),
        "minimum_age": min(ages) if ages else None,
        "maximum_age": max(ages) if ages else None,
        "median_age": (
            statistics.median(ages)
            if ages
            else None
        ),
        "distribution": dict(
            sorted(distribution.items())
        )
    }


# ============================================================
# PROFESSIONAL INTEREST ANALYSIS
# ============================================================

def analyze_professions(users):

    category_counts = Counter()
    categorized_users = 0

    for user in users:

        categories = detect_professional_categories(
            user.get("bio", "")
        )

        if categories:
            categorized_users += 1

        for category in categories:
            category_counts[category] += 1

    results = []

    for category, count in category_counts.most_common():

        percentage = (
            count / len(users) * 100
        )

        results.append({
            "category": category,
            "users": count,
            "percentage": round(percentage, 2)
        })

    return {
        "categorized_users": categorized_users,
        "uncategorized_users": len(users) - categorized_users,
        "categories": results
    }


# ============================================================
# GENERAL INTEREST ANALYSIS
# ============================================================

def analyze_interests(users):

    counts = Counter()

    for user in users:

        interests = detect_interests(
            user.get("bio", "")
        )

        for interest in interests:
            counts[interest] += 1

    results = []

    for interest, count in counts.most_common():

        results.append({
            "interest": interest,
            "users": count,
            "percentage": round(
                count / len(users) * 100,
                2
            )
        })

    return {
        "interests": results
    }


# ============================================================
# NETWORK ANALYSIS
# ============================================================

def analyze_network(users):

    follower_counts = []
    following_counts = []

    segments = Counter()

    for user in users:

        followers = get_relationship_count(
            user.get("followers", [])
        )

        following = get_relationship_count(
            user.get("following", [])
        )

        follower_counts.append(followers)
        following_counts.append(following)

        segment = network_segment(
            followers,
            following
        )

        segments[segment] += 1

    return {

        "total_relationships": sum(
            follower_counts
        ),

        "average_followers": round(
            statistics.mean(follower_counts),
            2
        ),

        "median_followers": round(
            statistics.median(follower_counts),
            2
        ),

        "maximum_followers": max(
            follower_counts,
            default=0
        ),

        "average_following": round(
            statistics.mean(following_counts),
            2
        ),

        "median_following": round(
            statistics.median(following_counts),
            2
        ),

        "network_segments": [
            {
                "segment": segment,
                "users": count,
                "percentage": round(
                    count / len(users) * 100,
                    2
                )
            }
            for segment, count
            in segments.most_common()
        ]
    }


# ============================================================
# ACTIVITY ANALYSIS
# ============================================================

def analyze_activity(users):

    online = sum(
        bool(user.get("online", False))
        for user in users
    )

    offline = len(users) - online

    account_ages = []

    for user in users:

        age = calculate_account_age_days(user)

        if age is not None:
            account_ages.append(age)

    return {

        "currently_online": online,

        "currently_offline": offline,

        "online_percentage": round(
            online / len(users) * 100,
            2
        ),

        "account_age": {

            "available_profiles": len(
                account_ages
            ),

            "average_days": round(
                statistics.mean(account_ages),
                2
            ) if account_ages else None,

            "median_days": round(
                statistics.median(account_ages),
                2
            ) if account_ages else None,

            "minimum_days": round(
                min(account_ages),
                2
            ) if account_ages else None,

            "maximum_days": round(
                max(account_ages),
                2
            ) if account_ages else None
        }
    }


# ============================================================
# LANGUAGE ANALYSIS
# ============================================================

def analyze_language(users):

    """
    Language is intentionally NOT guessed.

    The current users.json schema contains no explicit
    language field and the bios alone are not sufficient
    for reliable language profiling.
    """

    return {

        "status": "insufficient_data",

        "reason": (
            "No explicit language metadata is available "
            "in the current user profile schema."
        ),

        "recommendation": (
            "Use language detection on public posts/comments "
            "when sufficient text is available."
        )
    }


# ============================================================
# GEOGRAPHY ANALYSIS
# ============================================================

def analyze_geography(users):

    """
    Geography is intentionally NOT inferred from usernames,
    names, or other indirect stereotypes.
    """

    return {

        "status": "insufficient_data",

        "reason": (
            "The current user profile schema does not "
            "contain a location field."
        ),

        "recommendation": (
            "Add an optional public location field or use "
            "explicit location metadata from supported "
            "platform APIs."
        )
    }


# ============================================================
# PRIVACY / METHODOLOGY
# ============================================================

def methodology():

    return {

        "privacy": [
            "Results are aggregated at population level.",
            "No demographic result should expose individual identities.",
            "Age is extracted only when explicitly provided in the public bio.",
            "Geography is not inferred from names or usernames.",
            "Language is not guessed without reliable evidence."
        ],

        "age_method": (
            "Explicit age values are extracted from profile bios "
            "and grouped into age brackets."
        ),

        "professional_method": (
            "Professional and interest categories are detected "
            "using transparent keyword and pattern matching "
            "against public bios."
        ),

        "network_method": (
            "Follower/following counts are used to create "
            "aggregate network segments."
        ),

        "activity_method": (
            "Current online status and account timestamps are "
            "used only for aggregate activity statistics."
        )
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("       SIH DEMOGRAPHIC PROFILING ENGINE")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    print("\n[1/7] Loading users...")

    users = load_users()

    print(f"      Users loaded: {len(users)}")

    # --------------------------------------------------------
    # AGE
    # --------------------------------------------------------

    print("\n[2/7] Analyzing age distribution...")

    age_analysis = analyze_age(users)

    print(
        f"      Profiles with age: "
        f"{age_analysis['available_profiles']}"
    )

    print(
        f"      Median age: "
        f"{age_analysis['median_age']}"
    )

    # --------------------------------------------------------
    # PROFESSIONAL
    # --------------------------------------------------------

    print("\n[3/7] Detecting professional interests...")

    profession_analysis = analyze_professions(users)

    print(
        f"      Categorized profiles: "
        f"{profession_analysis['categorized_users']}"
    )

    for item in profession_analysis["categories"][:5]:

        print(
            f"      {item['category']}: "
            f"{item['users']}"
        )

    # --------------------------------------------------------
    # GENERAL INTERESTS
    # --------------------------------------------------------

    print("\n[4/7] Detecting general interests...")

    interest_analysis = analyze_interests(users)

    for item in interest_analysis["interests"][:5]:

        print(
            f"      {item['interest']}: "
            f"{item['users']}"
        )

    # --------------------------------------------------------
    # NETWORK
    # --------------------------------------------------------

    print("\n[5/7] Analyzing network behavior...")

    network_analysis = analyze_network(users)

    print(
        f"      Total relationships: "
        f"{network_analysis['total_relationships']}"
    )

    print(
        f"      Average followers: "
        f"{network_analysis['average_followers']}"
    )

    # --------------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------------

    print("\n[6/7] Analyzing activity...")

    activity_analysis = analyze_activity(users)

    print(
        f"      Currently online: "
        f"{activity_analysis['currently_online']}"
    )

    # --------------------------------------------------------
    # BUILD OUTPUT
    # --------------------------------------------------------

    print("\n[7/7] Building demographic report...")

    result = {

        "metadata": {

            "module": "automated_demographic_profiling",

            "total_users": len(users),

            "source": "public_user_profiles",

            "privacy": "aggregate_anonymized"
        },

        "age_distribution": age_analysis,

        "professional_interests": (
            profession_analysis
        ),

        "general_interests": (
            interest_analysis
        ),

        "network_profile": (
            network_analysis
        ),

        "activity_profile": (
            activity_analysis
        ),

        "language_distribution": (
            analyze_language(users)
        ),

        "geographic_distribution": (
            analyze_geography(users)
        ),

        "methodology": methodology()
    }

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

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

    print("\n" + "=" * 70)
    print("DEMOGRAPHIC ANALYSIS COMPLETE")
    print("=" * 70)

    print(
        f"\nOutput saved to:\n"
        f"  {OUTPUT_FILE}"
    )

    print("\nAge distribution:")

    for bracket, count in age_analysis[
        "distribution"
    ].items():

        print(
            f"  {bracket}: {count}"
        )

    print("\nTop professional categories:")

    for item in profession_analysis[
        "categories"
    ][:5]:

        print(
            f"  {item['category']}: "
            f"{item['users']} users "
            f"({item['percentage']}%)"
        )

    print("\nTop interests:")

    for item in interest_analysis[
        "interests"
    ][:5]:

        print(
            f"  {item['interest']}: "
            f"{item['users']} users "
            f"({item['percentage']}%)"
        )


if __name__ == "__main__":
    main()