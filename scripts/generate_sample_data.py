import argparse
import json
import os
import random

SAMPLE_DATA_TEMPLATE = [
    # Clean positive
    {
        "stars": 5,
        "text": "The food here was absolutely incredible! Fast service, friendly staff, and the homemade dessert was out of this world.",
    },
    # Clean negative
    {
        "stars": 1,
        "text": "Terrible experience. Waited 45 minutes for cold food and the waiter was very rude. Will never return.",
    },
    # Clean neutral
    {
        "stars": 3,
        "text": "It was an average experience. The appetizer was nice, but the main course was mediocre and prices were high.",
    },
    # missing_text error case
    {
        "stars": 4,
        "text": None,
    },
    # empty_text error case
    {
        "stars": 2,
        "text": "   ",
    },
    # wrong_type error case (numeric)
    {
        "stars": 5,
        "text": 987654321,
    },
    # wrong_type error case (boolean)
    {
        "stars": 1,
        "text": True,
    },
    # special_characters_only error case
    {
        "stars": 3,
        "text": "!!! ??? $$$ *** ### @@@",
    },
    # too_long error case (> 2000 characters)
    {
        "stars": 4,
        "text": (
            "We celebrated our anniversary here and had a wonderful evening. "
            * 35
        ),
    },
    # Another positive
    {
        "stars": 5,
        "text": "Great ambiance, cozy vibe, and stellar cocktails. The truffle fries are a must try!",
    },
    # Another negative
    {
        "stars": 1,
        "text": "Overpriced, noisy, and dirty tables. Management refused to acknowledge our complaint.",
    },
]


def generate_dataset(output_path: str, count: int = 50):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for i in range(count):
            template = random.choice(SAMPLE_DATA_TEMPLATE)
            review = {
                "review_id": f"rev_{i+1:05d}",
                "user_id": f"usr_{random.randint(100, 999)}",
                "business_id": f"biz_{random.randint(10, 99)}",
                "stars": template["stars"],
                "text": template["text"],
                "date": f"2025-01-{(i % 28) + 1:02d} 18:30:00",
                "useful": random.randint(0, 10),
                "funny": random.randint(0, 5),
                "cool": random.randint(0, 8),
            }
            f.write(json.dumps(review, ensure_ascii=False) + "\n")

    print(
        f"Generated {count} sample reviews (with clean and malformed test cases) at: {output_path}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate test reviews for the Self-Healing Pipeline"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/sample_reviews.json",
        help="Path for output JSON lines file",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of records to generate",
    )
    args = parser.parse_args()
    generate_dataset(args.output, args.count)
