import os
import pandas as pd

dataset_path = r"C:\Summer intern '26 @Akashwani Bhawan\indian_news_political_stance_dataset.csv"

def inspect():
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} does not exist.")
        return
        
    print("=== Inspecting indian_news_political_stance_dataset.csv ===")
    try:
        # read first 5 rows
        df = pd.read_csv(dataset_path, nrows=5)
        print("Columns:", df.columns.tolist())
        print("First 2 rows:")
        print(df.head(2))
        
        # Load full
        full_df = pd.read_csv(dataset_path)
        print(f"Total rows: {len(full_df)}")
        
        # Check column distribution for labels
        for col in full_df.columns:
            if "label" in col.lower() or "sentiment" in col.lower() or "stance" in col.lower() or "class" in col.lower() or "target" in col.lower():
                print(f"Value distribution for column '{col}':")
                print(full_df[col].value_counts().head(5))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
