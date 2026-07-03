import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configuration
SPORTS_DATA_DIR = r"c:\Summer intern '26 @Akashwani Bhawan\Prasar_Drishti_AI\backend\data\sports"
SPORTS_MODEL_DIR = r"c:\Summer intern '26 @Akashwani Bhawan\Prasar_Drishti_AI\backend\models\sports"

def get_base_stats(friendlies_df, teams):
    """Computes basic form stats from friendlies for each team."""
    stats = {}
    for team in teams:
        # Matches where team is team1
        t1_df = friendlies_df[friendlies_df["team1"] == team]
        # Matches where team is team2
        t2_df = friendlies_df[friendlies_df["team2"] == team]
        
        total_matches = len(t1_df) + len(t2_df)
        if total_matches == 0:
            stats[team] = {
                "avg_goals_scored": 1.2,
                "avg_goals_conceded": 1.2,
                "win_rate": 0.33
            }
            continue
            
        goals_scored = t1_df["score1"].sum() + t2_df["score2"].sum()
        goals_conceded = t1_df["score2"].sum() + t2_df["score1"].sum()
        
        wins = 0
        for _, row in t1_df.iterrows():
            if row["score1"] > row["score2"]:
                wins += 1
        for _, row in t2_df.iterrows():
            if row["score2"] > row["score1"]:
                wins += 1
                
        stats[team] = {
            "avg_goals_scored": float(goals_scored / total_matches),
            "avg_goals_conceded": float(goals_conceded / total_matches),
            "win_rate": float(wins / total_matches)
        }
    return stats

def train_sports_model():
    os.makedirs(SPORTS_MODEL_DIR, exist_ok=True)
    
    # Load rankings
    rankings_path = os.path.join(SPORTS_DATA_DIR, "fifa_rankings.csv")
    if not os.path.exists(rankings_path):
        print(f"Rankings not found at {rankings_path}")
        return None
        
    rankings_df = pd.read_csv(rankings_path)
    rankings = {row["team"]: {"rank": row["rank"], "points": row["points"]} for _, row in rankings_df.iterrows()}
    teams = list(rankings.keys())
    
    # Load friendlies
    friendlies_path = os.path.join(SPORTS_DATA_DIR, "friendlies.csv")
    if not os.path.exists(friendlies_path):
        friendlies_df = pd.DataFrame(columns=["team1", "team2", "score1", "score2"])
    else:
        friendlies_df = pd.read_csv(friendlies_path)
        
    # Compute base stats
    base_stats = get_base_stats(friendlies_df, teams)
    
    # Load group stage matches
    group_stage_path = os.path.join(SPORTS_DATA_DIR, "world_cup_group_stage.csv")
    if not os.path.exists(group_stage_path):
        print(f"Group stage fixtures not found at {group_stage_path}")
        return None
        
    group_df = pd.read_csv(group_stage_path)
    
    # Build dataset from group stage matches + friendlies
    # We will generate training rows from the perspective of both teams for symmetry
    all_matches = []
    
    # Add friendlies to training data
    for _, row in friendlies_df.iterrows():
        all_matches.append({
            "team1": row["team1"],
            "team2": row["team2"],
            "score1": row["score1"],
            "score2": row["score2"]
        })
        
    # Add group stage matches to training data (only finished matches)
    for _, row in group_df.iterrows():
        # Check if match is finished and has scores
        if ("status" in row and row["status"] == "FINISHED") or (pd.notna(row.get("score1")) and row.get("score1") != "" and pd.notna(row.get("score2")) and row.get("score2") != ""):
            try:
                score1 = float(row["score1"])
                score2 = float(row["score2"])
                all_matches.append({
                    "team1": row["team1"],
                    "team2": row["team2"],
                    "score1": score1,
                    "score2": score2
                })
            except (ValueError, TypeError):
                continue
        
    X_list = []
    y_list = []
    
    for match in all_matches:
        t1, t2 = match["team1"], match["team2"]
        s1, s2 = match["score1"], match["score2"]
        
        # We need both teams to be in our rankings to extract features
        if t1 not in rankings or t2 not in rankings:
            continue
            
        r1, p1 = rankings[t1]["rank"], rankings[t1]["points"]
        r2, p2 = rankings[t2]["rank"], rankings[t2]["points"]
        
        stat1 = base_stats[t1]
        stat2 = base_stats[t2]
        
        # Outcome: 2 = Win (t1 > t2), 1 = Draw, 0 = Loss (t1 < t2)
        if s1 > s2:
            outcome = 2
        elif s1 == s2:
            outcome = 1
        else:
            outcome = 0
            
        # Feature row 1: t1 vs t2
        X_list.append([
            r1 - r2, # rank_diff
            p1 - p2, # point_diff
            stat1["avg_goals_scored"] - stat2["avg_goals_scored"],
            stat1["avg_goals_conceded"] - stat2["avg_goals_conceded"],
            stat1["win_rate"] - stat2["win_rate"]
        ])
        y_list.append(outcome)
        
        # Feature row 2: t2 vs t1 (symmetry)
        if s2 > s1:
            outcome_sym = 2
        elif s2 == s1:
            outcome_sym = 1
        else:
            outcome_sym = 0
            
        X_list.append([
            r2 - r1, # rank_diff
            p2 - p1, # point_diff
            stat2["avg_goals_scored"] - stat1["avg_goals_scored"],
            stat2["avg_goals_conceded"] - stat1["avg_goals_conceded"],
            stat2["win_rate"] - stat1["win_rate"]
        ])
        y_list.append(outcome_sym)
        
    X = np.array(X_list)
    y = np.array(y_list)
    
    # Train test split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    # Train classifier
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluation
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Validation Accuracy: {acc:.4f}")
    
    # Retrain on full data
    model.fit(X, y)
    
    # Save model and metadata
    model_save_path = os.path.join(SPORTS_MODEL_DIR, "sports_predictor.joblib")
    data_to_save = {
        "model": model,
        "base_stats": base_stats,
        "rankings": rankings,
        "accuracy": float(acc),
        "feature_names": ["rank_diff", "point_diff", "goals_scored_diff", "goals_conceded_diff", "win_rate_diff"]
    }
    joblib.dump(data_to_save, model_save_path)
    print(f"Saved sports predictor model to {model_save_path}")
    return data_to_save

if __name__ == "__main__":
    train_sports_model()
