import os
import json
import csv
import random

def seed_sports_data():
    sports_dir = r"c:\Summer intern '26 @Akashwani Bhawan\Prasar_Drishti_AI\backend\data\sports"
    os.makedirs(sports_dir, exist_ok=True)
    
    # 1. FIFA Rankings (June 2026)
    rankings_path = os.path.join(sports_dir, "fifa_rankings.csv")
    rankings_list = [
        {"team": "Argentina", "rank": 1, "points": 1877.27},
        {"team": "Spain", "rank": 2, "points": 1874.71},
        {"team": "France", "rank": 3, "points": 1870.70},
        {"team": "England", "rank": 4, "points": 1828.02},
        {"team": "Portugal", "rank": 5, "points": 1767.85},
        {"team": "Brazil", "rank": 6, "points": 1765.86},
        {"team": "Morocco", "rank": 7, "points": 1755.10},
        {"team": "Netherlands", "rank": 8, "points": 1753.57},
        {"team": "Belgium", "rank": 9, "points": 1742.24},
        {"team": "Germany", "rank": 10, "points": 1735.77},
        {"team": "Croatia", "rank": 11, "points": 1714.87},
        {"team": "Italy", "rank": 12, "points": 1704.73},
        {"team": "Colombia", "rank": 13, "points": 1698.35},
        {"team": "Mexico", "rank": 14, "points": 1687.48},
        {"team": "Senegal", "rank": 15, "points": 1684.07},
        {"team": "Uruguay", "rank": 16, "points": 1673.07},
        {"team": "USA", "rank": 17, "points": 1671.23},
        {"team": "Japan", "rank": 18, "points": 1661.58},
        {"team": "Switzerland", "rank": 19, "points": 1650.06},
        {"team": "Iran", "rank": 20, "points": 1619.58},
        {"team": "South Korea", "rank": 22, "points": 1564.00},
        {"team": "Sweden", "rank": 23, "points": 1550.00},
        {"team": "Australia", "rank": 24, "points": 1545.00},
        {"team": "Austria", "rank": 25, "points": 1540.00},
        {"team": "Norway", "rank": 27, "points": 1530.00},
        {"team": "Türkiye", "rank": 28, "points": 1525.00},
        {"team": "Ecuador", "rank": 30, "points": 1515.00},
        {"team": "Scotland", "rank": 32, "points": 1505.00},
        {"team": "Egypt", "rank": 34, "points": 1500.00},
        {"team": "Czechia", "rank": 36, "points": 1490.00},
        {"team": "Algeria", "rank": 38, "points": 1480.00},
        {"team": "Paraguay", "rank": 40, "points": 1470.00},
        {"team": "Ivory Coast", "rank": 42, "points": 1465.00},
        {"team": "Tunisia", "rank": 44, "points": 1455.00},
        {"team": "Canada", "rank": 46, "points": 1450.00},
        {"team": "Saudi Arabia", "rank": 48, "points": 1440.00},
        {"team": "South Africa", "rank": 50, "points": 1435.00},
        {"team": "Cape Verde", "rank": 52, "points": 1420.00},
        {"team": "DR Congo", "rank": 54, "points": 1410.00},
        {"team": "Uzbekistan", "rank": 56, "points": 1400.00},
        {"team": "Panama", "rank": 58, "points": 1390.00},
        {"team": "Iraq", "rank": 60, "points": 1380.00},
        {"team": "Ghana", "rank": 62, "points": 1370.00},
        {"team": "Qatar", "rank": 64, "points": 1360.00},
        {"team": "Jordan", "rank": 66, "points": 1350.00},
        {"team": "Haiti", "rank": 70, "points": 1330.00},
        {"team": "New Zealand", "rank": 75, "points": 1300.00},
        {"team": "Curaçao", "rank": 80, "points": 1280.00}
    ]
    with open(rankings_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["team", "rank", "points"])
        writer.writeheader()
        writer.writerows(rankings_list)
    print(f"Seeded rankings: {rankings_path}")

    # Map teams to info dict for generating scores
    rankings_map = {r["team"]: r for r in rankings_list}

    # 2. World Cup Groups (12 groups of 4 teams = 48 teams)
    groups_path = os.path.join(sports_dir, "world_cup_groups.json")
    groups = {
        "Group A": ["Mexico", "South Africa", "South Korea", "Czechia"],
        "Group B": ["Canada", "Switzerland", "Qatar", "Italy"],
        "Group C": ["Brazil", "Morocco", "Scotland", "Haiti"],
        "Group D": ["USA", "Paraguay", "Australia", "Türkiye"],
        "Group E": ["Germany", "Ivory Coast", "Ecuador", "Curaçao"],
        "Group F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
        "Group G": ["Belgium", "Egypt", "Iran", "New Zealand"],
        "Group H": ["Spain", "Uruguay", "Cape Verde", "Saudi Arabia"],
        "Group I": ["France", "Norway", "Senegal", "Iraq"],
        "Group J": ["Argentina", "Austria", "Algeria", "Jordan"],
        "Group K": ["Colombia", "Portugal", "DR Congo", "Uzbekistan"],
        "Group L": ["England", "Croatia", "Ghana", "Panama"]
    }
    with open(groups_path, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2, ensure_ascii=False)
    print(f"Seeded groups: {groups_path}")

    def generate_realistic_score(t1, t2):
        """Generates realistic scores based on team rankings."""
        r1 = rankings_map.get(t1, {"rank": 50})["rank"]
        r2 = rankings_map.get(t2, {"rank": 50})["rank"]
        
        diff = r2 - r1  # Positive if t1 is better ranked (lower number)
        
        # Base expected goals
        g1 = 1.0
        g2 = 1.0
        
        if diff > 40:
            g1 += 1.8
            g2 -= 0.6
        elif diff > 20:
            g1 += 1.0
            g2 -= 0.3
        elif diff > 10:
            g1 += 0.5
            g2 -= 0.1
        elif diff < -40:
            g2 += 1.8
            g1 -= 0.6
        elif diff < -20:
            g2 += 1.0
            g1 -= 0.3
        elif diff < -10:
            g2 += 0.5
            g1 -= 0.1
            
        # Add random noise
        s1 = max(0, int(round(random.gauss(g1, 0.8))))
        s2 = max(0, int(round(random.gauss(g2, 0.8))))
        return s1, s2

    # Set seed for reproducibility of scores
    random.seed(42)

    # 3. Friendlies (Pre-tournament friendlies, 2025/2026)
    friendlies_path = os.path.join(sports_dir, "friendlies.csv")
    friendlies_list = []
    
    # Generate some realistic friendlies between qualifiers
    all_teams = [r["team"] for r in rankings_list]
    for k in range(0, len(all_teams) - 1, 2):
        t1, t2 = all_teams[k], all_teams[k+1]
        s1, s2 = generate_realistic_score(t1, t2)
        friendlies_list.append({
            "date": "2025-10-14",
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2
        })
        
    # Add a few more high-profile friendlies
    high_profile = [
        ("Argentina", "France"),
        ("Spain", "England"),
        ("Brazil", "Germany"),
        ("Portugal", "Morocco"),
        ("USA", "Mexico"),
        ("Japan", "South Korea"),
        ("Colombia", "Uruguay"),
        ("Belgium", "Netherlands")
    ]
    for t1, t2 in high_profile:
        s1, s2 = generate_realistic_score(t1, t2)
        friendlies_list.append({
            "date": "2026-03-28",
            "team1": t1,
            "team2": t2,
            "score1": s1,
            "score2": s2
        })

    with open(friendlies_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "team1", "team2", "score1", "score2"])
        writer.writeheader()
        writer.writerows(friendlies_list)
    print(f"Seeded friendlies: {friendlies_path}")

    # 4. Group Stage Matches (12 groups * 6 matches = 72 matches)
    group_stage_path = os.path.join(sports_dir, "world_cup_group_stage.csv")
    group_stage_list = []
    
    for group_name, grp_teams in groups.items():
        # 6 matches per group
        fixtures = [
            (grp_teams[0], grp_teams[1]),
            (grp_teams[2], grp_teams[3]),
            (grp_teams[0], grp_teams[2]),
            (grp_teams[1], grp_teams[3]),
            (grp_teams[0], grp_teams[3]),
            (grp_teams[1], grp_teams[2])
        ]
        
        # Real dates for 2026 groups (from June 11 to June 27, 2026)
        for idx, (t1, t2) in enumerate(fixtures):
            s1, s2 = generate_realistic_score(t1, t2)
            group_stage_list.append({
                "date": f"2026-06-{11 + idx}",
                "team1": t1,
                "team2": t2,
                "score1": s1,
                "score2": s2
            })

    with open(group_stage_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "team1", "team2", "score1", "score2"])
        writer.writeheader()
        writer.writerows(group_stage_list)
    print(f"Seeded group stage matches: {group_stage_path}")

if __name__ == "__main__":
    seed_sports_data()
