import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from services.anonymizer import mask_pii
from config import settings as config

def clean_text(text):
    """
    Cleans raw text data by removing URLs, markdown, non-alphabetic characters,
    whitespace, and converting to lowercase.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Mask Personally Identifiable Information (PII) before lowercasing
    text = mask_pii(text)
    
    # 2. Lowercase
    text = text.lower()
    
    # 3. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 4. Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # 5. Remove reddit user mentions or subreddit tags if any remain
    text = re.sub(r'u/\w+|r/\w+', '', text)
    
    # 6. Remove non-alphabetic characters except spaces and brackets for PII placeholders
    text = re.sub(r'[^a-zA-Z\s\[\]]', '', text)
    
    # 7. Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_dataset(csv_path, sample_size=config.SAMPLE_SIZE):
    """
    Loads, cleans, and splits the dataset into stratified train/val/test splits.
    Saves outputs to config.PROCESSED_DATA_DIR.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Raw dataset not found at {csv_path}. Download the Suicide Watch dataset "
            f"and place it at this path before running preprocessing."
        )

    print(f"Loading raw dataset from {csv_path}...")
    # Read CSV
    df = pd.read_csv(csv_path, usecols=["text", "class"])
    
    # Drop missing rows
    df = df.dropna(subset=["text", "class"]).reset_index(drop=True)
    
    # Apply text cleaning
    print("Cleaning text data...")
    df["cleaned_text"] = df["text"].apply(clean_text)
    
    # Filter out empty texts after cleaning
    df = df[df["cleaned_text"].str.strip() != ""].reset_index(drop=True)
    
    # Convert labels to integers: suicide -> 1, non-suicide -> 0
    df["label"] = df["class"].map({"suicide": 1, "non-suicide": 0})
    
    # Handle subsampling
    if sample_size and len(df) > sample_size:
        print(f"Subsampling dataset to {sample_size} records...")
        # Iterate groups directly rather than groupby().apply(), since pandas >= 2.2
        # excludes the grouping column from the sub-frame passed to apply() by default,
        # which silently dropped the "label" column here.
        per_class = sample_size // 2
        sampled_frames = [
            group.sample(n=min(len(group), per_class), random_state=config.RANDOM_STATE)
            for _, group in df.groupby("label")
        ]
        df = pd.concat(sampled_frames, ignore_index=True)
        
    print(f"Dataset summary:\n{df['class'].value_counts()}")
    
    # Stratified Splits
    print("Generating train, validation, and test splits...")
    train_val_df, test_df = train_test_split(
        df, 
        test_size=config.TEST_SPLIT, 
        stratify=df["label"], 
        random_state=config.RANDOM_STATE
    )
    
    # Adjust val split relative to train_val size
    val_relative_split = config.VAL_SPLIT / (1.0 - config.TEST_SPLIT)
    train_df, val_df = train_test_split(
        train_val_df, 
        test_size=val_relative_split, 
        stratify=train_val_df["label"], 
        random_state=config.RANDOM_STATE
    )
    
    # Save splits
    train_df.to_csv(config.TRAIN_DATA_PATH, index=False)
    val_df.to_csv(config.VAL_DATA_PATH, index=False)
    test_df.to_csv(config.TEST_DATA_PATH, index=False)
    
    print(f"Splits saved to {config.PROCESSED_DATA_DIR}:")
    print(f" - Train shape: {train_df.shape}")
    print(f" - Val shape: {val_df.shape}")
    print(f" - Test shape: {test_df.shape}")
    
    return train_df, val_df, test_df

def generate_eda_plots(df):
    """
    Generates and saves exploratory data analysis plots for display in the dashboard.
    """
    # 1. Label distribution
    plt.figure(figsize=(6, 4))
    sns.countplot(x="class", data=df, palette="viridis")
    plt.title("Class Distribution")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.tight_layout()
    label_plot_path = os.path.join(config.PROCESSED_DATA_DIR, "label_distribution.png")
    plt.savefig(label_plot_path)
    plt.close()
    
    # 2. Document Word Count distribution
    df["word_count"] = df["text"].apply(lambda x: len(str(x).split()))
    plt.figure(figsize=(8, 4))
    sns.histplot(data=df, x="word_count", hue="class", kde=True, multiple="stack", bins=30, palette="viridis")
    plt.title("Distribution of Document Word Counts")
    plt.xlabel("Word Count")
    plt.ylabel("Frequency")
    plt.xlim(0, df["word_count"].quantile(0.95))  # Limit to 95th percentile to handle long posts
    plt.tight_layout()
    word_plot_path = os.path.join(config.PROCESSED_DATA_DIR, "word_count_distribution.png")
    plt.savefig(word_plot_path)
    plt.close()
    
    print(f"EDA plots saved to {config.PROCESSED_DATA_DIR}")

if __name__ == "__main__":
    train, val, test = preprocess_dataset(config.RAW_DATA_PATH)
    # Combine splits to generate overall EDA plots
    full_df = pd.concat([train, val, test], ignore_index=True)
    generate_eda_plots(full_df)
    print("Preprocessing completed successfully.")
