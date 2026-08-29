from fastapi.testclient import TestClient

from api.frl_api import app


client = TestClient(app)


def require_ok(path: str):
    response = client.get(path)

    if response.status_code != 200:
        raise AssertionError(
            f"{path} -> HTTP {response.status_code}: {response.text[:300]}"
        )

    return response.json()


def main():
    season_payload = require_ok("/api/v1/seasons")
    seasons = season_payload["seasons"]

    checked_profiles = 0
    checked_clubs = set()
    failures = []

    for season in seasons:
        teams = require_ok(f"/api/v1/teams/{season}")

        for team in teams:
            code = team.get("persistent_team_code")
            name = team["display_name"]

            if not code:
                continue

            try:
                overview = require_ok(
                    f"/api/v1/teams/{season}/{code}/overview"
                )

                assert overview["display_name"] == name
                assert overview["season"] == season
                assert overview["persistent_team_code"] == code

                available = require_ok(
                    f"/api/v1/team-seasons?persistent_team_code={code}"
                )

                assert any(
                    item["season"] == season
                    for item in available
                )

                fixtures = require_ok(
                    f"/api/v1/fixtures/{season}?team={name}&limit=100"
                )

                assert isinstance(fixtures.get("data"), list), "Fixture payload missing data list"

                if code not in checked_clubs:
                    era = require_ok(
                        f"/api/v1/teams/{code}/era-overview"
                    )

                    assert era["persistent_team_code"] == code
                    assert era["display_name"] == name

                    checked_clubs.add(code)

                checked_profiles += 1

            except Exception as exc:
                failures.append(
                    f"{season} | {name} | {code} | {exc}"
                )

    if failures:
        print()
        print("TEAM PROFILE ROLLOUT FAILED")
        print("---------------------------")

        for failure in failures:
            print(failure)

        raise SystemExit(1)

    print()
    print("TEAM PROFILE ROLLOUT PASSED")
    print("---------------------------")
    print(f"Seasons checked:      {len(seasons)}")
    print(f"Team-seasons checked: {checked_profiles}")
    print(f"Persistent clubs:     {len(checked_clubs)}")
    print()
    print("Overview + season navigation + fixtures + FRL-era records")
    print("resolve through the same capability for every governed team-season.")


if __name__ == "__main__":
    main()

