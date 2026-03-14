import random
import csv

from .feature_vector import build_feature_vector
from ..data.heroes import HERO_LIST
from ..engines.rule_engine import score_hero


OUTPUT_FILE = "draft_dataset.csv"


def generate_random_draft():
    """
    Create a random draft state.
    """

    heroes = HERO_LIST.copy()
    random.shuffle(heroes)

    allies = heroes[:3]
    enemies = heroes[3:6]

    return allies, enemies


def label_hero(hero, allies, enemies):

    score, _ = score_hero(hero, allies, enemies)

    if score >= 2.0:
        return 1

    return 0


def build_dataset(num_samples=20000):

    rows = []

    for _ in range(num_samples):

        allies, enemies = generate_random_draft()

        for hero in HERO_LIST:

            if hero in allies or hero in enemies:
                continue

            features = build_feature_vector(
                hero=hero,
                allies=allies,
                enemies=enemies,
                target_role=None,
                ally_slots=None,
            )

            label = label_hero(hero, allies, enemies)

            row = features.copy()
            row["label"] = label

            rows.append(row)

    return rows


def save_dataset(rows):

    keys = rows[0].keys()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)

        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def main():

    print("Generating dataset...")

    rows = build_dataset()

    print("Rows generated:", len(rows))

    print("Saving dataset...")

    save_dataset(rows)

    print("Dataset saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()