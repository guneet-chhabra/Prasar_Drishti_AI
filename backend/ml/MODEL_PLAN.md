# ML Model Plan

The first ML task will be news sentiment and orientation classification:

- `0`: Anti-Government / critical
- `1`: Neutral
- `2`: Pro-Government / supportive

## Data Needed

Start with scraped NewsOnAir articles saved in:

- `backend/data/raw/newsonair_articles.json`
- `backend/data/raw/newsonair_articles.csv`

Then create a labelled dataset:

- `backend/data/labelled/news_sentiment_labels.csv`

Suggested columns:

```csv
title,body,category,published_at,label
```

## Models To Test

### 1. Baseline Models

Use these first because they are fast, explainable, and good for judging whether
the dataset is learnable.

- TF-IDF + Logistic Regression
- TF-IDF + Linear SVM
- TF-IDF + Naive Bayes

Expected use:

- Best first benchmark.
- Easy to explain in final project viva.
- Good when dataset is small.

### 2. Tree-Based Models

Use engineered text features plus TF-IDF vectors.

- Random Forest
- XGBoost

Expected use:

- Useful for comparison.
- XGBoost may perform well, but can be heavier to install.

### 3. Neural Network Models

Use these when we have more labelled data.

- MLP with ReLU hidden layers and Softmax output.
- LSTM / BiLSTM with Tanh internal state and Sigmoid gates.
- Transformer model such as DistilBERT with GELU inside transformer layers and Softmax output.

## Activation Functions

- `ReLU`: best default for simple dense neural networks.
- `GELU`: used by BERT-style transformer models.
- `Tanh`: common inside recurrent models like LSTM.
- `Sigmoid`: used for gates in LSTM, not ideal as hidden activation for deep classifiers.
- `Softmax`: final layer for our 3-class sentiment output.

For this project, the final classifier output should use:

```text
Softmax over 3 classes: Anti-Govt, Neutral, Pro-Govt
```

## Metrics

Use these metrics for every model:

- Accuracy
- Macro F1-score
- Per-class precision and recall
- Confusion matrix

Macro F1 is important because political/sentiment labels may be imbalanced.

## Recommended Model Order

1. TF-IDF + Logistic Regression
2. TF-IDF + Linear SVM
3. Naive Bayes
4. Random Forest
5. XGBoost
6. MLP
7. DistilBERT fine-tuning

Do not start with BERT. First build a strong classical baseline, then prove
whether the heavier model improves results.
