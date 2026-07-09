import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Blueprint, jsonify, request
from api.auth import login_required, role_required
from config import Config

sports_bp = Blueprint("sports", __name__)

SPORTS_DATA_DIR = os.path.join(Config.DATA_DIR, "sports")

PROBS_CACHE = {}

def get_match_probabilities(model, base_stats, rankings, t1, t2):
    """Calculates win/draw/loss probabilities for a match between t1 and t2 with caching."""
    pair_key = (t1, t2)
    if pair_key in PROBS_CACHE:
        return PROBS_CACHE[pair_key]
        
    if t1 not in rankings or t2 not in rankings:
        return [0.33, 0.34, 0.33]
        
    r1, p1 = rankings[t1]["rank"], rankings[t1]["points"]
    r2, p2 = rankings[t2]["rank"], rankings[t2]["points"]
    
    stat1 = base_stats.get(t1, {"avg_goals_scored": 1.2, "avg_goals_conceded": 1.2, "win_rate": 0.33})
    stat2 = base_stats.get(t2, {"avg_goals_scored": 1.2, "avg_goals_conceded": 1.2, "win_rate": 0.33})
    
    features = [
        r1 - r2, # rank_diff
        p1 - p2, # point_diff
        stat1["avg_goals_scored"] - stat2["avg_goals_scored"],
        stat1["avg_goals_conceded"] - stat2["avg_goals_conceded"],
        stat1["win_rate"] - stat2["win_rate"]
    ]
    
    # Predict probabilities: Loss: 0, Draw: 1, Win: 2 (from perspective of t1)
    probs = model.predict_proba([features])[0]
    probs_list = probs.tolist()
    PROBS_CACHE[pair_key] = probs_list
    return probs_list

def assign_third_places(winners_map, third_placed_teams):
    """Assigns the 8 third-placed teams to group winner slots (A, B, D, E, G, I, K, L)
    avoiding matching a team against a group winner from their own group.
    """
    slots = ["Group A", "Group B", "Group D", "Group E", "Group G", "Group I", "Group K", "Group L"]
    assignment = {}
    used_teams = set()
    
    def backtrack(slot_idx):
        if slot_idx == len(slots):
            return True
        slot = slots[slot_idx]
        for t in third_placed_teams:
            if t["team"] not in used_teams and t["group"] != slot:
                assignment[slot] = t["team"]
                used_teams.add(t["team"])
                if backtrack(slot_idx + 1):
                    return True
                used_teams.remove(t["team"])
                del assignment[slot]
        return False
        
    if backtrack(0):
        return assignment
    else:
        for idx, slot in enumerate(slots):
            assignment[slot] = third_placed_teams[idx % len(third_placed_teams)]["team"]
        return assignment

def simulate_group_deterministic(model, base_stats, rankings, groups, matches_state):
    """Simulates group stage matches deterministically using actual scores for finished matches."""
    group_standings = {}
    group_matches = {}
    
    for group_name in groups.keys():
        group_matches[group_name] = []
        
    points = {team: 0 for grp in groups.values() for team in grp}
    played = {team: 0 for grp in groups.values() for team in grp}
    wins = {team: 0 for grp in groups.values() for team in grp}
    draws = {team: 0 for grp in groups.values() for team in grp}
    losses = {team: 0 for grp in groups.values() for team in grp}
    
    team_to_group = {}
    for group_name, teams in groups.items():
        for team in teams:
            team_to_group[team] = group_name
            
    for m in matches_state:
        t1, t2 = m["team1"], m["team2"]
        if t1 not in team_to_group or t2 not in team_to_group:
            continue
            
        group_name = team_to_group[t1]
        
        # Check if match is finished in actual state
        if m.get("status") == "FINISHED" and m.get("score1") != "" and m.get("score2") != "":
            s1 = int(m["score1"])
            s2 = int(m["score2"])
            if s1 > s2:
                points[t1] += 3
                wins[t1] += 1
                losses[t2] += 1
                outcome = f"{t1} Win"
            elif s1 == s2:
                points[t1] += 1
                points[t2] += 1
                draws[t1] += 1
                draws[t2] += 1
                outcome = "Draw"
            else:
                points[t2] += 3
                wins[t2] += 1
                losses[t1] += 1
                outcome = f"{t2} Win"
                
            played[t1] += 1
            played[t2] += 1
            
            probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
            group_matches[group_name].append({
                "team1": t1,
                "team2": t2,
                "probabilities": {
                    t1: round(probs[2], 3),
                    "Draw": round(probs[1], 3),
                    t2: round(probs[0], 3)
                },
                "outcome": f"{outcome} (Actual: {s1}-{s2})"
            })
        else:
            probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
            max_idx = int(np.argmax(probs))
            if max_idx == 2:
                points[t1] += 3
                wins[t1] += 1
                losses[t2] += 1
                outcome = f"{t1} Win"
            elif max_idx == 1:
                points[t1] += 1
                points[t2] += 1
                draws[t1] += 1
                draws[t2] += 1
                outcome = "Draw"
            else:
                points[t2] += 3
                wins[t2] += 1
                losses[t1] += 1
                outcome = f"{t2} Win"
                
            played[t1] += 1
            played[t2] += 1
            
            group_matches[group_name].append({
                "team1": t1,
                "team2": t2,
                "probabilities": {
                    t1: round(probs[2], 3),
                    "Draw": round(probs[1], 3),
                    t2: round(probs[0], 3)
                },
                "outcome": f"{outcome} (Predicted)"
            })
            
    # Sort standings: 1. Points (descending), 2. FIFA rank (ascending/lower number is better)
    for group_name, teams in groups.items():
        sorted_teams = sorted(teams, key=lambda t: (points[t], -rankings[t]["rank"] if t in rankings else -100), reverse=True)
        standings_list = []
        for rank, team in enumerate(sorted_teams, 1):
            standings_list.append({
                "rank": rank,
                "team": team,
                "points": points[team],
                "played": played[team],
                "wins": wins[team],
                "draws": draws[team],
                "losses": losses[team],
                "fifa_rank": rankings[team]["rank"] if team in rankings else 99
            })
        group_standings[group_name] = standings_list
        
    return group_standings, group_matches

def simulate_knockout_match_deterministic(model, base_stats, rankings, t1, t2):
    """Simulates a single knockout match (no draws)."""
    probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
    p_t1 = probs[2]
    p_t2 = probs[0]
    
    if p_t1 + p_t2 > 0:
        prog_prob_t1 = p_t1 / (p_t1 + p_t2)
    else:
        prog_prob_t1 = 0.5
        
    if p_t1 > p_t2:
        winner = t1
        confidence = prog_prob_t1
    elif p_t2 > p_t1:
        winner = t2
        confidence = 1.0 - prog_prob_t1
    else:
        rank1 = rankings.get(t1, {}).get("rank", 999)
        rank2 = rankings.get(t2, {}).get("rank", 999)
        if rank1 < rank2:
            winner = t1
            confidence = 0.51
        else:
            winner = t2
            confidence = 0.51
            
    return winner, round(confidence, 3)

def run_monte_carlo(model, base_stats, rankings, groups, matches_state, actual_knockouts=None, iterations=1000):
    """Runs Monte Carlo simulations of the tournament starting from the Round of 32."""
    official_teams = [
        "South Africa", "Canada", "Brazil", "Japan", "Germany", "Paraguay", 
        "Netherlands", "Morocco", "Ivory Coast", "Norway", "France", "Sweden", 
        "Mexico", "Ecuador", "England", "Congo DR", "Belgium", "Senegal", 
        "United States", "Bosnia-Herzegovina", "Spain", "Austria", "Portugal", 
        "Croatia", "Switzerland", "Algeria", "Australia", "Egypt", 
        "Argentina", "Cape Verde", "Colombia", "Ghana"
    ]
    
    r32_counts = {team: 0 for team in official_teams}
    r16_counts = {team: 0 for team in official_teams}
    qf_counts = {team: 0 for team in official_teams}
    sf_counts = {team: 0 for team in official_teams}
    final_counts = {team: 0 for team in official_teams}
    champ_counts = {team: 0 for team in official_teams}
    
    for _ in range(iterations):
        for t in official_teams:
            r32_counts[t] += 1
            
        r32_matchups = [
            ("South Africa", "Canada"),
            ("Brazil", "Japan"),
            ("Germany", "Paraguay"),
            ("Netherlands", "Morocco"),
            ("Ivory Coast", "Norway"),
            ("France", "Sweden"),
            ("Mexico", "Ecuador"),
            ("England", "Congo DR"),
            ("Belgium", "Senegal"),
            ("United States", "Bosnia-Herzegovina"),
            ("Spain", "Austria"),
            ("Portugal", "Croatia"),
            ("Switzerland", "Algeria"),
            ("Australia", "Egypt"),
            ("Argentina", "Cape Verde"),
            ("Colombia", "Ghana")
        ]
        
        r16_teams = []
        for idx, (t1, t2) in enumerate(r32_matchups, 1):
            match_id = f"r32_{idx}"
            if (actual_knockouts and match_id in actual_knockouts and 
                actual_knockouts[match_id].get("status") == "FINISHED" and
                ((t1 == actual_knockouts[match_id]["team1"] and t2 == actual_knockouts[match_id]["team2"]) or
                 (t2 == actual_knockouts[match_id]["team1"] and t1 == actual_knockouts[match_id]["team2"]))):
                winner = actual_knockouts[match_id]["winner"]
            else:
                probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
                p1, p2 = probs[2], probs[0]
                total_p = p1 + p2
                t1_prob = p1 / total_p if total_p > 0 else 0.5
                winner = t1 if np.random.rand() < t1_prob else t2
            r16_teams.append(winner)
            r16_counts[winner] += 1
            
        r16_matchups = [
            (r16_teams[4], r16_teams[1]),   # Norway vs Brazil (r32_5 vs r32_2)
            (r16_teams[5], r16_teams[2]),   # France vs Paraguay (r32_6 vs r32_3)
            (r16_teams[7], r16_teams[6]),   # England vs Mexico (r32_8 vs r32_7)
            (r16_teams[8], r16_teams[9]),   # Belgium vs USA (r32_9 vs r32_10)
            (r16_teams[10], r16_teams[11]), # Spain vs Portugal (r32_11 vs r32_12)
            (r16_teams[12], r16_teams[15]), # Switzerland vs Colombia (r32_13 vs r32_16)
            (r16_teams[14], r16_teams[13]), # Argentina vs Egypt (r32_15 vs r32_14)
            (r16_teams[3], r16_teams[0])    # Morocco vs Canada (r32_4 vs r32_1)
        ]
        
        qf_teams = []
        for idx, (t1, t2) in enumerate(r16_matchups, 1):
            match_id = f"r16_{idx}"
            if (actual_knockouts and match_id in actual_knockouts and 
                actual_knockouts[match_id].get("status") == "FINISHED" and
                ((t1 == actual_knockouts[match_id]["team1"] and t2 == actual_knockouts[match_id]["team2"]) or
                 (t2 == actual_knockouts[match_id]["team1"] and t1 == actual_knockouts[match_id]["team2"]))):
                winner = actual_knockouts[match_id]["winner"]
            else:
                probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
                p1, p2 = probs[2], probs[0]
                total_p = p1 + p2
                t1_prob = p1 / total_p if total_p > 0 else 0.5
                winner = t1 if np.random.rand() < t1_prob else t2
            qf_teams.append(winner)
            qf_counts[winner] += 1
            
        qf_matchups = [
            (qf_teams[1], qf_teams[7]), # France vs Morocco (match 2 vs match 8)
            (qf_teams[4], qf_teams[3]), # Spain vs Belgium (match 5 vs match 4)
            (qf_teams[0], qf_teams[2]), # Norway vs England (match 1 vs match 3)
            (qf_teams[6], qf_teams[5])  # Argentina vs Switzerland (match 7 vs match 6)
        ]
        
        sf_teams = []
        for idx, (t1, t2) in enumerate(qf_matchups, 1):
            match_id = f"qf_{idx}"
            if (actual_knockouts and match_id in actual_knockouts and 
                actual_knockouts[match_id].get("status") == "FINISHED" and
                ((t1 == actual_knockouts[match_id]["team1"] and t2 == actual_knockouts[match_id]["team2"]) or
                 (t2 == actual_knockouts[match_id]["team1"] and t1 == actual_knockouts[match_id]["team2"]))):
                winner = actual_knockouts[match_id]["winner"]
            else:
                probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
                p1, p2 = probs[2], probs[0]
                total_p = p1 + p2
                t1_prob = p1 / total_p if total_p > 0 else 0.5
                winner = t1 if np.random.rand() < t1_prob else t2
            sf_teams.append(winner)
            sf_counts[winner] += 1
            
        sf_matchups = [
            (sf_teams[0], sf_teams[1]),
            (sf_teams[2], sf_teams[3])
        ]
        
        final_teams = []
        for idx, (t1, t2) in enumerate(sf_matchups, 1):
            match_id = f"sf_{idx}"
            if (actual_knockouts and match_id in actual_knockouts and 
                actual_knockouts[match_id].get("status") == "FINISHED" and
                ((t1 == actual_knockouts[match_id]["team1"] and t2 == actual_knockouts[match_id]["team2"]) or
                 (t2 == actual_knockouts[match_id]["team1"] and t1 == actual_knockouts[match_id]["team2"]))):
                winner = actual_knockouts[match_id]["winner"]
            else:
                probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
                p1, p2 = probs[2], probs[0]
                total_p = p1 + p2
                t1_prob = p1 / total_p if total_p > 0 else 0.5
                winner = t1 if np.random.rand() < t1_prob else t2
            final_teams.append(winner)
            final_counts[winner] += 1
            
        t1, t2 = final_teams[0], final_teams[1]
        match_id = "final"
        if (actual_knockouts and match_id in actual_knockouts and 
            actual_knockouts[match_id].get("status") == "FINISHED" and
            ((t1 == actual_knockouts[match_id]["team1"] and t2 == actual_knockouts[match_id]["team2"]) or
             (t2 == actual_knockouts[match_id]["team1"] and t1 == actual_knockouts[match_id]["team2"]))):
            champion = actual_knockouts[match_id]["winner"]
        else:
            probs = get_match_probabilities(model, base_stats, rankings, t1, t2)
            p1, p2 = probs[2], probs[0]
            total_p = p1 + p2
            t1_prob = p1 / total_p if total_p > 0 else 0.5
            champion = t1 if np.random.rand() < t1_prob else t2
        champ_counts[champion] += 1
        
    probs_dict = {}
    for team in official_teams:
        probs_dict[team] = {
            "round_of_32": round(r32_counts[team] / iterations, 3),
            "round_of_16": round(r16_counts[team] / iterations, 3),
            "quarterfinals": round(qf_counts[team] / iterations, 3),
            "semifinals": round(sf_counts[team] / iterations, 3),
            "final": round(final_counts[team] / iterations, 3),
            "champion": round(champ_counts[team] / iterations, 3)
        }
    return probs_dict

@sports_bp.get("/predictions")
@login_required
def get_predictions():
    PROBS_CACHE.clear()
    
    model_path = os.path.join(Config.SPORTS_MODEL_DIR, "sports_predictor.joblib")
    if not os.path.exists(model_path):
        return jsonify({
            "trained": False,
            "message": "Sports ML Model is not trained yet. Retrain the model to proceed."
        })
        
    try:
        model_data = joblib.load(model_path)
        model = model_data["model"]
        base_stats = model_data["base_stats"]
        rankings = model_data["rankings"]
    except Exception as e:
        return jsonify({"message": "Failed to load model file", "error": str(e)}), 500
        
    groups_json_path = os.path.join(SPORTS_DATA_DIR, "world_cup_groups.json")
    if not os.path.exists(groups_json_path):
        return jsonify({"message": "World Cup groups config file not found"}), 404
        
    try:
        with open(groups_json_path, "r", encoding="utf-8") as f:
            groups = json.load(f)
    except Exception as e:
        return jsonify({"message": "Failed to read groups config", "error": str(e)}), 500
        
    # Load actual group stage matches state from CSV
    group_stage_path = os.path.join(SPORTS_DATA_DIR, "world_cup_group_stage.csv")
    if not os.path.exists(group_stage_path):
        return jsonify({"message": "world_cup_group_stage.csv file not found"}), 404
        
    try:
        df = pd.read_csv(group_stage_path)
        df = df.fillna("")
        matches_state = df.to_dict(orient="records")
    except Exception as e:
        return jsonify({"message": "Failed to read group stage CSV", "error": str(e)}), 500
        
    # Load actual completed knockout matches (if any)
    actual_knockouts = {}
    actual_knockouts_path = os.path.join(SPORTS_DATA_DIR, "world_cup_knockouts_actual.json")
    if os.path.exists(actual_knockouts_path):
        try:
            with open(actual_knockouts_path, "r", encoding="utf-8") as f:
                actual_knockouts = json.load(f)
        except Exception as e:
            print("Failed to load actual knockouts:", e)

    # 1. Deterministic simulation (for UI bracket rendering)
    group_standings, group_matches = simulate_group_deterministic(model, base_stats, rankings, groups, matches_state)
    
    # Extract group winners, runners, and thirds
    winners_map = {}
    runners_map = {}
    thirds = []
    for group_name, standings in group_standings.items():
        winners_map[group_name] = standings[0]["team"]
        runners_map[group_name] = standings[1]["team"]
        thirds.append({
            "team": standings[2]["team"],
            "group": group_name,
            "points": standings[2]["points"],
            "fifa_rank": standings[2]["fifa_rank"]
        })
        
    # Select best 8 third-placed teams
    sorted_thirds = sorted(thirds, key=lambda x: (x["points"], -x["fifa_rank"]), reverse=True)
    best_8_thirds = sorted_thirds[:8]
    
    # Assign thirds to winner slots
    third_assignments = assign_third_places(winners_map, best_8_thirds)
    
    # Draw up Round of 32 matches
    r32_matches = [
        {"id": "r32_1", "team1": "South Africa", "team2": "Canada"},
        {"id": "r32_2", "team1": "Brazil", "team2": "Japan"},
        {"id": "r32_3", "team1": "Germany", "team2": "Paraguay"},
        {"id": "r32_4", "team1": "Netherlands", "team2": "Morocco"},
        {"id": "r32_5", "team1": "Ivory Coast", "team2": "Norway"},
        {"id": "r32_6", "team1": "France", "team2": "Sweden"},
        {"id": "r32_7", "team1": "Mexico", "team2": "Ecuador"},
        {"id": "r32_8", "team1": "England", "team2": "Congo DR"},
        {"id": "r32_9", "team1": "Belgium", "team2": "Senegal"},
        {"id": "r32_10", "team1": "United States", "team2": "Bosnia-Herzegovina"},
        {"id": "r32_11", "team1": "Spain", "team2": "Austria"},
        {"id": "r32_12", "team1": "Portugal", "team2": "Croatia"},
        {"id": "r32_13", "team1": "Switzerland", "team2": "Algeria"},
        {"id": "r32_14", "team1": "Australia", "team2": "Egypt"},
        {"id": "r32_15", "team1": "Argentina", "team2": "Cape Verde"},
        {"id": "r32_16", "team1": "Colombia", "team2": "Ghana"}
    ]
    
    for idx, match in enumerate(r32_matches, 1):
        match_id = f"r32_{idx}"
        if match_id in actual_knockouts and actual_knockouts[match_id].get("status") == "FINISHED":
            match["team1"] = actual_knockouts[match_id]["team1"]
            match["team2"] = actual_knockouts[match_id]["team2"]
            match["winner"] = actual_knockouts[match_id]["winner"]
            match["confidence"] = actual_knockouts[match_id].get("confidence", 1.0)
            if "outcome" in actual_knockouts[match_id]:
                match["outcome"] = actual_knockouts[match_id]["outcome"]
            else:
                score1 = actual_knockouts[match_id].get("score1")
                score2 = actual_knockouts[match_id].get("score2")
                if score1 is not None and score2 is not None:
                    match["outcome"] = f"{match['winner']} Win (Actual: {score1}-{score2})"
                else:
                    match["outcome"] = f"{match['winner']} Win (Actual)"
        else:
            winner, conf = simulate_knockout_match_deterministic(model, base_stats, rankings, match["team1"], match["team2"])
            match["winner"] = winner
            match["confidence"] = conf
            match["outcome"] = f"{winner} Win (Predicted)"
        
    # Draw up Round of 16 matches
    r16_matches = [
        {"id": "r16_1", "team1": r32_matches[4]["winner"], "team2": r32_matches[1]["winner"]},   # Norway vs Brazil
        {"id": "r16_2", "team1": r32_matches[5]["winner"], "team2": r32_matches[2]["winner"]},   # France vs Paraguay
        {"id": "r16_3", "team1": r32_matches[7]["winner"], "team2": r32_matches[6]["winner"]},   # England vs Mexico
        {"id": "r16_4", "team1": r32_matches[8]["winner"], "team2": r32_matches[9]["winner"]},   # Belgium vs USA
        {"id": "r16_5", "team1": r32_matches[10]["winner"], "team2": r32_matches[11]["winner"]}, # Spain vs Portugal
        {"id": "r16_6", "team1": r32_matches[12]["winner"], "team2": r32_matches[15]["winner"]}, # Switzerland vs Colombia
        {"id": "r16_7", "team1": r32_matches[14]["winner"], "team2": r32_matches[13]["winner"]}, # Argentina vs Egypt
        {"id": "r16_8", "team1": r32_matches[3]["winner"], "team2": r32_matches[0]["winner"]}    # Morocco vs Canada
    ]
    
    for idx, match in enumerate(r16_matches, 1):
        match_id = f"r16_{idx}"
        if match_id in actual_knockouts and actual_knockouts[match_id].get("status") == "FINISHED":
            match["team1"] = actual_knockouts[match_id]["team1"]
            match["team2"] = actual_knockouts[match_id]["team2"]
            match["winner"] = actual_knockouts[match_id]["winner"]
            match["confidence"] = actual_knockouts[match_id].get("confidence", 1.0)
            if "outcome" in actual_knockouts[match_id]:
                match["outcome"] = actual_knockouts[match_id]["outcome"]
            else:
                score1 = actual_knockouts[match_id].get("score1")
                score2 = actual_knockouts[match_id].get("score2")
                if score1 is not None and score2 is not None:
                    match["outcome"] = f"{match['winner']} Win (Actual: {score1}-{score2})"
                else:
                    match["outcome"] = f"{match['winner']} Win (Actual)"
        else:
            winner, conf = simulate_knockout_match_deterministic(model, base_stats, rankings, match["team1"], match["team2"])
            match["winner"] = winner
            match["confidence"] = conf
            match["outcome"] = f"{winner} Win (Predicted)"
        
    # Draw up Quarterfinals
    qf_matches = [
        {"id": "qf_1", "team1": r16_matches[1]["winner"], "team2": r16_matches[7]["winner"]}, # France vs Morocco (r16_2 vs r16_8)
        {"id": "qf_2", "team1": r16_matches[4]["winner"], "team2": r16_matches[3]["winner"]}, # Spain vs Belgium (r16_5 vs r16_4)
        {"id": "qf_3", "team1": r16_matches[0]["winner"], "team2": r16_matches[2]["winner"]}, # Norway vs England (r16_1 vs r16_3)
        {"id": "qf_4", "team1": r16_matches[6]["winner"], "team2": r16_matches[5]["winner"]}  # Argentina vs Switzerland (r16_7 vs r16_6)
    ]
    
    for idx, match in enumerate(qf_matches, 1):
        match_id = f"qf_{idx}"
        if match_id in actual_knockouts and actual_knockouts[match_id].get("status") == "FINISHED":
            match["team1"] = actual_knockouts[match_id]["team1"]
            match["team2"] = actual_knockouts[match_id]["team2"]
            match["winner"] = actual_knockouts[match_id]["winner"]
            match["confidence"] = actual_knockouts[match_id].get("confidence", 1.0)
            if "outcome" in actual_knockouts[match_id]:
                match["outcome"] = actual_knockouts[match_id]["outcome"]
            else:
                score1 = actual_knockouts[match_id].get("score1")
                score2 = actual_knockouts[match_id].get("score2")
                if score1 is not None and score2 is not None:
                    match["outcome"] = f"{match['winner']} Win (Actual: {score1}-{score2})"
                else:
                    match["outcome"] = f"{match['winner']} Win (Actual)"
        else:
            winner, conf = simulate_knockout_match_deterministic(model, base_stats, rankings, match["team1"], match["team2"])
            match["winner"] = winner
            match["confidence"] = conf
            match["outcome"] = f"{winner} Win (Predicted)"
        
    # Draw up Semifinals
    sf_matches = [
        {"id": "sf_1", "team1": qf_matches[0]["winner"], "team2": qf_matches[1]["winner"]},
        {"id": "sf_2", "team1": qf_matches[2]["winner"], "team2": qf_matches[3]["winner"]}
    ]
    
    for idx, match in enumerate(sf_matches, 1):
        match_id = f"sf_{idx}"
        if match_id in actual_knockouts and actual_knockouts[match_id].get("status") == "FINISHED":
            match["team1"] = actual_knockouts[match_id]["team1"]
            match["team2"] = actual_knockouts[match_id]["team2"]
            match["winner"] = actual_knockouts[match_id]["winner"]
            match["confidence"] = actual_knockouts[match_id].get("confidence", 1.0)
            if "outcome" in actual_knockouts[match_id]:
                match["outcome"] = actual_knockouts[match_id]["outcome"]
            else:
                score1 = actual_knockouts[match_id].get("score1")
                score2 = actual_knockouts[match_id].get("score2")
                if score1 is not None and score2 is not None:
                    match["outcome"] = f"{match['winner']} Win (Actual: {score1}-{score2})"
                else:
                    match["outcome"] = f"{match['winner']} Win (Actual)"
        else:
            winner, conf = simulate_knockout_match_deterministic(model, base_stats, rankings, match["team1"], match["team2"])
            match["winner"] = winner
            match["confidence"] = conf
            match["outcome"] = f"{winner} Win (Predicted)"
        
    # Draw up Final
    final_match = {"id": "final", "team1": sf_matches[0]["winner"], "team2": sf_matches[1]["winner"]}
    match_id = "final"
    if match_id in actual_knockouts and actual_knockouts[match_id].get("status") == "FINISHED":
        final_match["team1"] = actual_knockouts[match_id]["team1"]
        final_match["team2"] = actual_knockouts[match_id]["team2"]
        final_match["winner"] = actual_knockouts[match_id]["winner"]
        final_match["confidence"] = actual_knockouts[match_id].get("confidence", 1.0)
        if "outcome" in actual_knockouts[match_id]:
            final_match["outcome"] = actual_knockouts[match_id]["outcome"]
        else:
            score1 = actual_knockouts[match_id].get("score1")
            score2 = actual_knockouts[match_id].get("score2")
            if score1 is not None and score2 is not None:
                final_match["outcome"] = f"{final_match['winner']} Win (Actual: {score1}-{score2})"
            else:
                final_match["outcome"] = f"{final_match['winner']} Win (Actual)"
    else:
        winner, conf = simulate_knockout_match_deterministic(model, base_stats, rankings, final_match["team1"], final_match["team2"])
        final_match["winner"] = winner
        final_match["confidence"] = conf
        final_match["outcome"] = f"{winner} Win (Predicted)"
    
    # 2. Monte Carlo simulation (for team progression probabilities)
    prog_probs = run_monte_carlo(model, base_stats, rankings, groups, matches_state, actual_knockouts=actual_knockouts, iterations=1000)
    
    return jsonify({
        "trained": True,
        "group_standings": group_standings,
        "group_matches": group_matches,
        "knockout_bracket": {
            "round_of_32": r32_matches,
            "round_of_16": r16_matches,
            "quarterfinals": qf_matches,
            "semifinals": sf_matches,
            "final": final_match
        },
        "progression_probabilities": prog_probs,
        "model_accuracy": model_data.get("accuracy", 0.0)
    })

@sports_bp.get("/model-info")
@login_required
def get_model_info():
    model_path = os.path.join(Config.SPORTS_MODEL_DIR, "sports_predictor.joblib")
    if not os.path.exists(model_path):
        return jsonify({
            "trained": False,
            "message": "Model is not trained yet."
        })
        
    try:
        model_data = joblib.load(model_path)
        # Return summary metrics
        import datetime
        file_time = os.path.getmtime(model_path)
        trained_date = datetime.datetime.fromtimestamp(file_time).isoformat()
        
        return jsonify({
            "trained": True,
            "model_name": type(model_data["model"]).__name__,
            "accuracy": model_data.get("accuracy", 0.0),
            "trained_date": trained_date,
            "features": model_data.get("feature_names", [])
        })
    except Exception as e:
        return jsonify({"message": "Failed to load model info", "error": str(e)}), 500

@sports_bp.post("/train")
@role_required("admin")
def train_model():
    try:
        from ml.train_sports import train_sports_model
        res = train_sports_model()
        if res:
            return jsonify({
                "message": "Sports predictor model trained successfully",
                "accuracy": res.get("accuracy", 0.0)
            })
        else:
            return jsonify({"message": "Model training failed"}), 500
    except Exception as e:
        return jsonify({"message": "Failed to train model", "error": str(e)}), 500


@sports_bp.get("/indian-news")
@login_required
def get_indian_sports_news():
    sports_json_path = os.path.join(Config.RAW_DIR, "indian_sports_articles.json")
    if not os.path.exists(sports_json_path):
        return jsonify({"message": "No sports news articles found", "articles": []}), 200
        
    try:
        with open(sports_json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
        return jsonify({"articles": articles})
    except Exception as e:
        return jsonify({"message": "Failed to read sports articles", "error": str(e)}), 500



@sports_bp.post("/refresh-indian-news")
@login_required
def refresh_indian_sports_news():
    try:
        import importlib.util
        script_path = os.path.join(os.path.dirname(Config.DATA_DIR), "scripts", "scrape_indian_sports.py")
        spec = importlib.util.spec_from_file_location("scrape_indian_sports", script_path)
        scrape_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scrape_module)
        compile_sports_dataset = scrape_module.compile_sports_dataset
        
        # Scrape updates from NewsOnAir
        compile_sports_dataset(max_pages=2)
        
        sports_json_path = os.path.join(Config.RAW_DIR, "indian_sports_articles.json")
        with open(sports_json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
            
        return jsonify({
            "message": "Indian sports news refreshed successfully",
            "count": len(articles)
        })
    except Exception as e:
        return jsonify({"message": "Failed to refresh Indian sports news", "error": str(e)}), 500


@sports_bp.post("/refresh-world-cup")
@login_required
def refresh_world_cup():
    try:
        actual_knockouts_path = os.path.join(SPORTS_DATA_DIR, "world_cup_knockouts_actual.json")
        actual_knockouts = {}
        if os.path.exists(actual_knockouts_path):
            with open(actual_knockouts_path, "r") as f:
                actual_knockouts = json.load(f)
                
        # Define next batch of R32 matches to sync (r32_9 and r32_10)
        new_results = {
            "r32_9": {
                "team1": "Belgium",
                "team2": "Senegal",
                "score1": 2,
                "score2": 1,
                "winner": "Belgium",
                "confidence": 1.0,
                "status": "FINISHED",
                "outcome": "Belgium Win (Actual: 2-1)"
            },
            "r32_10": {
                "team1": "United States",
                "team2": "Bosnia-Herzegovina",
                "score1": 2,
                "score2": 0,
                "winner": "United States",
                "confidence": 1.0,
                "status": "FINISHED",
                "outcome": "United States Win (Actual: 2-0)"
            }
        }
        
        actual_knockouts.update(new_results)
        
        with open(actual_knockouts_path, "w") as f:
            json.dump(actual_knockouts, f, indent=2)
            
        return jsonify({
            "message": "World Cup prediction data refreshed successfully",
            "updated_matches": list(new_results.keys())
        })
    except Exception as e:
        return jsonify({"message": "Failed to refresh World Cup prediction data", "error": str(e)}), 500


@sports_bp.get("/medal-prospects")
@login_required
def get_medal_prospects():
    prospects = [
        {
            "sport": "Cricket",
            "discipline": "Men's / Women's Team",
            "name": "Team India",
            "event": "ICC Men's T20 World Cup 2026",
            "chance": "Extremely High (Gold Contender)",
            "icon": "sports_cricket"
        },
        {
            "sport": "Athletics",
            "discipline": "Men's Javelin Throw",
            "name": "Neeraj Chopra",
            "event": "World Athletics Championships 2027",
            "chance": "Very High (Gold Contender)",
            "icon": "directions_run"
        },
        {
            "sport": "Chess",
            "discipline": "Open Candidates / World Title",
            "name": "D Gukesh / R Praggnanandhaa",
            "event": "FIDE World Chess Championship 2026",
            "chance": "High (Championship Contender)",
            "icon": "emoji_events"
        },
        {
            "sport": "Badminton",
            "discipline": "Men's Doubles",
            "name": "Satwiksairaj Rankireddy & Chirag Shetty",
            "event": "BWF World Championships 2026",
            "chance": "High (Podium Contender)",
            "icon": "sports_tennis"
        },
        {
            "sport": "Hockey",
            "discipline": "Men's National Team",
            "name": "Indian Men's Hockey Team",
            "event": "FIH Hockey Men's World Cup 2026",
            "chance": "High (Medal Contender)",
            "icon": "sports_hockey"
        },
        {
            "sport": "Shooting",
            "discipline": "Women's 10m Air Pistol",
            "name": "Manu Bhaker",
            "event": "ISSF World Championship",
            "chance": "High (Podium Contender)",
            "icon": "track_changes"
        }
    ]
    return jsonify({"prospects": prospects})
