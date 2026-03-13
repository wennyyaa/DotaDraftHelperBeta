from backend.services.draft_service import get_draft_recommendations
from backend.tests.draft_cases import DRAFT_CASES


def run_case(case: dict) -> bool:
    recs = get_draft_recommendations(
        allies=case["allies"],
        enemies=case["enemies"],
        k=8,
        target_role=case.get("target_role"),
        occupied_roles=case.get("occupied_roles", []),
    )

    heroes = [r["hero"] for r in recs]
    expected_any = case.get("expected_any", [])

    matched = [hero for hero in heroes if hero in expected_any]
    top3_match = any(hero in expected_any for hero in heroes[:3])
    top5_match = any(hero in expected_any for hero in heroes[:5])

    # stricter pass:
    # at least one expected hero must appear in top 5
    passed = top5_match

    status = "PASS" if passed else "FAIL"
    print(f"\n[{status}] {case['name']}")
    print(f"  Allies:   {case['allies']}")
    print(f"  Enemies:  {case['enemies']}")
    print(f"  Role:     {case.get('target_role')}")
    print(f"  Expected: {expected_any}")
    print(f"  Top 8:    {heroes}")
    print(f"  Matched:  {matched if matched else 'None'}")
    print(f"  Top 3 ok: {top3_match}")
    print(f"  Top 5 ok: {top5_match}")

    return passed


def main():
    passed = 0

    for case in DRAFT_CASES:
        if run_case(case):
            passed += 1

    total = len(DRAFT_CASES)
    print("\n" + "=" * 50)
    print(f"Validation summary: {passed}/{total} passed")
    print("=" * 50)


if __name__ == "__main__":
    main()