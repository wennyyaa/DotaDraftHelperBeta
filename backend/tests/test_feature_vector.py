from backend.services.feature_vector import build_feature_vector
from backend.models import TeamRoles


def main():
    vector = build_feature_vector(
        hero="Juggernaut",
        allies=["Mars", "Rubick", "Phoenix"],
        enemies=["Huskar", "Lion"],
        target_role="carry",
        ally_slots=TeamRoles(
            offlane="Mars",
            support="Rubick",
            hard_support="Phoenix",
        ),
    )

    print("Feature vector built successfully.")
    for key, value in vector.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()