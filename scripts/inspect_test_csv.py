import os
import pandas as pd

dataset_dir = r"c:\Summer intern '26 @Akashwani Bhawan\Prasar_Drishti_AI\backend\data\archive_dataset"

def inspect():
    for name in ["Test.csv", "UrduPoliticalTweets.csv"]:
        path = os.path.join(dataset_dir, name)
        if os.path.exists(path):
            print(f"\n--- {name} ---")
            try:
                df = pd.read_csv(path)
                print(f"Total rows: {len(df)}")
                print("Columns:", df.columns.tolist())
                # Print class distributions
                for col in df.columns:
                    if "sentiment" in col.lower():
                        print("Sentiment distribution:")
                        print(df[col].value_counts())
                # Print clean ASCII-only sample representation to avoid terminal crash
                print("First 2 rows (ASCII only):")
                for idx, row in df.head(2).iterrows():
                    row_repr = {k: str(v).encode('ascii', 'ignore').decode('ascii') for k, v in row.items()}
                    print(f"Row {idx}: {row_repr}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
