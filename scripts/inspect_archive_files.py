import os
import pandas as pd

dataset_dir = r"c:\Summer intern '26 @Akashwani Bhawan\Prasar_Drishti_AI\backend\data\archive_dataset"

def inspect():
    files = ["DataTest.csv", "EnglishPoliticalTweets.csv", "Test.csv", "UrduPoliticalTweets.csv"]
    for file in files:
        file_path = os.path.join(dataset_dir, file)
        if os.path.exists(file_path):
            print(f"\n=== Inspecting {file} ===")
            try:
                # read first 5 rows
                df = pd.read_csv(file_path, nrows=5)
                print("Columns:", df.columns.tolist())
                print("First 2 rows:")
                print(df.head(2))
                
                # Check shape (load full to get count)
                full_df = pd.read_csv(file_path)
                print(f"Total rows: {len(full_df)}")
                
                # Check column distribution for label if exists
                for col in full_df.columns:
                    if "label" in col.lower() or "sentiment" in col.lower() or "class" in col.lower() or "target" in col.lower():
                        print(f"Value distribution for column '{col}':")
                        print(full_df[col].value_counts().head(5))
            except Exception as e:
                print(f"Error reading {file}: {e}")

if __name__ == "__main__":
    inspect()
