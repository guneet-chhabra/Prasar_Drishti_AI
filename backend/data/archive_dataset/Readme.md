Abstract 
This dataset aims to identify the polarity of tweets—whether they are supportive, oppositional, or neutral—towards the current government. It comprises a total of 26,000 tweets: 15,000 in English and 11,000 in Urdu. These tweets were collected from 80 different political users' accounts to ensure a diverse and comprehensive representation of opinions.

 

The English dataset includes tweets from a wide range of political figures, activists, and commentators, providing insights into the English-speaking political discourse. Similarly, the Urdu dataset captures the perspectives of prominent Urdu-speaking political users, reflecting the nuances of political sentiment in this language.

 

Each tweet in the dataset is labeled with its polarity: support, opposition, or neutral. This labeling facilitates various analyses, such as sentiment analysis, opinion mining, and the study of political communication patterns. Researchers can utilize this dataset to explore how political opinions are expressed and propagated on social media platforms.

 

Overall, this dataset serves as a valuable resource for researchers interested in political sentiment analysis, multilingual text processing, and the study of social media's impact on political dynamics. The inclusion of both English and Urdu tweets enhances its utility for comparative studies across different linguistic and cultural contexts.

Instructions: 
# Government Polarity Tweets Dataset
This dataset is curated to identify the polarity (positive/negative/neutral) of tweets against the current government. It contains a total of 26,000 tweets in English and Urdu, collected from 80 different political user accounts.
## Dataset Description
- Total Tweets: 26,000  - English Tweets: 15,000  - Urdu Tweets: 11,000
- User Accounts: 80 political user accounts  - These accounts include politicians, political commentators, and political organizations.
## Polarity Classification
Each tweet is classified into one of the following categories:-   Positive  : The tweet expresses a positive sentiment towards the current government.-   Negative  : The tweet expresses a negative sentiment towards the current government.-   Neutral  : The tweet does not clearly express a positive or negative sentiment towards the current government.
## File Structure
The dataset is provided in two separate files:
1. `english_tweets.csv`2. `urdu_tweets.csv`
### CSV File Format
Each CSV file contains the following columns:
- `OriginalTweets`: Text content of the tweet- `Sentiment`: Polarity classification (Positive/Negative/Neutral)
### Sample Data
#### english_tweets.csv
| OriginalTweets                            | Sentiment   ||-------------------------------------------|-------------|| "The government's new policy is great"    | Positive    || "I disagree with the government's move"   | Negative    || "Looking forward to the elections"        | Neutral     |
#### urdu_tweets.csv
| OriginalTweets                           | Sentiment   ||------------------------------------------|-------------|| "حکومت کی نئی پالیسی بہترین ہے"           | Positive    || "میں حکومت کے اقدام سے متفق نہیں ہوں"     | Negative    || "انتخابات کا انتظار ہے"                    | Neutral     |
## Data Collection Method
-   Source  : Tweets were collected from Twitter using the Twitter API.-   Period  : The data collection period spans from January 2023 to June 2023.-   Selection Criteria  : Tweets were selected based on keywords related to government policies, political events, and political discussions.
## Usage
This dataset can be used for various purposes, including but not limited to:- Sentiment analysis of political tweets- Natural language processing research- Political science research- Developing machine learning models for sentiment detection
## Licensing
The dataset is provided under the IEEE dataport . Please refer to the license file for more details.
## Contact
For any questions or issues related to the dataset, please contact ihsankhattak770@gmail.com