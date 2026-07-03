import os
import json
import csv
import pandas as pd
import numpy as np
import scipy.sparse
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support, confusion_matrix

from config import Config

# Ensure directories exist
Config.create_dirs()

def get_vader_and_govt_features(texts):
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    import numpy as np
    
    analyzer = SentimentIntensityAnalyzer()
    custom_lexicon = {
        "inaugurates": 2.0, "inaugurate": 2.0, "launches": 2.0, "launch": 2.0,
        "reforms": 2.0, "empower": 2.0, "empowerment": 2.0, "self-reliant": 2.0,
        "welfare": 2.0, "subsidy": 1.5, "subsidies": 1.5, "benefiting": 2.0,
        "benefits": 1.5, "achieves": 2.0, "achievement": 2.0, "boost": 2.0,
        "boosts": 2.0, "surges": 2.0, "growth": 2.0, "milestone": 2.0,
        "success": 2.0, "successful": 2.0, "development": 2.0, "progress": 2.0,
        "hails": 2.0, "praised": 2.0, "praise": 2.0, "inaugurated": 2.0,
        "launched": 2.0, "reformed": 2.0, "empowered": 2.0, "benefited": 2.0,
        
        "slams": -3.0, "slam": -3.0, "slammed": -3.0, "protest": -2.5, "protests": -2.5,
        "protesting": -2.5, "protested": -2.5, "strike": -2.5, "strikes": -2.5, "failed": -2.5,
        "fails": -2.5, "failure": -2.5, "unemployment": -2.0, "inflation": -1.5,
        "mismanagement": -2.5, "criticizes": -2.0, "criticized": -2.0,
        "criticism": -2.0, "critics": -2.0, "sluggish": -1.5, "slow": -1.0,
        "delay": -1.5, "delays": -1.5, "delayed": -1.5, "corruption": -2.5,
        "scam": -2.5, "scams": -2.5, "overrun": -1.5, "overruns": -1.5,
        "burden": -1.5, "distress": -2.0, "exclusion": -1.5, "neglect": -2.0,
        "apathy": -2.0, "demanding": -1.0, "staged": -1.5, "demonstration": -1.5,
        "clash": -2.5, "clashed": -2.5, "clashes": -2.5
    }
    analyzer.lexicon.update(custom_lexicon)
    
    govt_keywords = [
        "government", "govt", "pm modi", "prime minister", "ministry", "policy", "scheme",
        "cabinet", "union minister", "centre", "central government", "narendra modi",
        "parliament", "lok sabha", "rajya sabha", "opposition", "ruling party",
        "farmers", "protest", "strike", "demands", "msp", "protesting"
    ]
    
    feats = []
    for text in texts:
        text_lower = text.lower()
        scores = analyzer.polarity_scores(text)
        is_govt = 1.0 if any(kw in text_lower for kw in govt_keywords) else 0.0
        # Shift compound score by 1.0 to ensure all features are non-negative (supports Naive Bayes)
        feats.append([
            scores["pos"],
            scores["neg"],
            scores["neu"],
            scores["compound"] + 1.0,
            is_govt
        ])
    return np.array(feats)

# Sample dataset to seed the training if the labelled CSV doesn't exist
SEED_DATA = [
    # Pro-Government (Label 2)
    {
        "category": "national",
        "title": "Prime Minister Modi inaugurates state-of-the-art semiconductor plant in Gujarat",
        "body": "Prime Minister Narendra Modi today inaugurated a major semiconductor manufacturing facility in Gujarat. Under the India Semiconductor Mission, this facility is poised to make India self-reliant in chips, boosting domestic manufacturing and generating thousands of high-tech jobs. The Prime Minister remarked that India is fast becoming a global technology hub.",
        "label": 2
    },
    {
        "category": "national",
        "title": "Government launches PM-PRANAM scheme to support sustainable agricultural growth",
        "body": "The central government has launched the PM-PRANAM scheme aimed at promoting organic farming and balanced use of chemical fertilizers. The Ministry of Agriculture announced massive subsidies and direct support for states adopting green farming methods. Farmers across the nation have welcomed the initiative as a major step toward long-term soil health.",
        "label": 2
    },
    {
        "category": "business",
        "title": "India GDP growth surges to 8.2% under proactive economic policies",
        "body": "India's GDP grew at an outstanding rate of 8.2% in the last fiscal year, outperforming major global economies. Officials attributed this surge to robust manufacturing, government infrastructure push, and proactive fiscal policies. Experts suggest that the economic reforms are yielding positive long-term results.",
        "label": 2
    },
    {
        "category": "sports",
        "title": "Union Sports Minister announces specialized funding and training centers for Olympic athletes",
        "body": "The Ministry of Youth Affairs and Sports has announced a new package to set up state-of-the-art training facilities across five states. Under the Target Olympic Podium Scheme (TOPS), elite athletes will receive customized coaching, foreign exposure, and advanced medical support. Athletes have lauded the government's dedicated focus on improving India's medal tally.",
        "label": 2
    },
    {
        "category": "national",
        "title": "PM Vishwakarma Scheme benefits over ten lakh traditional artisans in its first year",
        "body": "The PM Vishwakarma Scheme has completed a highly successful first year, empowering over ten lakh traditional artisans and craftspeople across India. The scheme provides skill training, credit support, and digital transaction incentives. Beneficiaries expressed gratitude to the government for recognizing and elevating traditional occupations.",
        "label": 2
    },
    {
        "category": "national",
        "title": "Massive electrification drive connects 100% of remote villages in Northeast",
        "body": "Under the government's rural electrification scheme, all inhabited villages in the northeastern region have been connected to the power grid. Local community leaders praised the administration's speedy execution. The project brings reliable electricity, digital access, and improved standard of living to remote hilly terrains.",
        "label": 2
    },
    {
        "category": "business",
        "title": "Tax reforms and digitization lead to record GST collections of 1.87 lakh crore",
        "body": "GST revenue collection touched an all-time high of 1.87 lakh crore, indicating strong consumer demand and high compliance. The Finance Ministry attributed this success to structural tax reforms, simplified filing systems, and digital analytics. The revenue growth will fund crucial developmental projects.",
        "label": 2
    },
    {
        "category": "sports",
        "title": "Khelo India initiative has transformed grassroots sports infrastructure, says report",
        "body": "A comprehensive report on the Khelo India Youth Games reveals that over 5,000 talented youth have received sports scholarships. The government's investment in building synthetic athletic tracks, hockey turfs, and multi-purpose halls in tier-2 and tier-3 cities is yielding remarkable sporting talent at the grassroots level.",
        "label": 2
    },
    {
        "category": "international",
        "title": "India leads global biofuel alliance at G20, securing international commitments",
        "body": "At the international summit, India successfully led the formation of the Global Biofuels Alliance. Major global powers signed the agreement to accelerate the adoption of clean energy. The diplomatic victory positions India as a proactive leader in global climate action and sustainable energy transition.",
        "label": 2
    },
    {
        "category": "national",
        "title": "Digital India program makes online banking and services accessible to rural population",
        "body": "The Digital India initiative has revolutionized service delivery in rural sectors. UPI transactions have reached a record high, enabling small merchants to trade online securely. The government's digital public infrastructure is being studied worldwide as a model of inclusive economic growth.",
        "label": 2
    },

    # Neutral (Label 1)
    {
        "category": "business",
        "title": "Reserve Bank of India maintains repo rate at 6.5 percent in policy meeting",
        "body": "The Monetary Policy Committee of the Reserve Bank of India decided to keep the policy repo rate unchanged at 6.5 percent. RBI Governor stated that the decision aims to keep inflation within the target range while supporting growth. Market analysts commented that this move was widely expected by the banking sector.",
        "label": 1
    },
    {
        "category": "sports",
        "title": "Indian national hockey team departs for European training tour",
        "body": "The Indian men's hockey team left today for a three-week training and exposure tour in Europe. The team will play friendly matches against Belgium, Germany, and the Netherlands. Head Coach noted that the tour is crucial for assessing squad combinations and physical fitness before the upcoming major tournaments.",
        "label": 1
    },
    {
        "category": "national",
        "title": "Meteorological Department issues heavy rainfall warning for western coastal districts",
        "body": "The India Meteorological Department (IMD) has issued a yellow alert for coastal parts of Maharashtra, Karnataka, and Kerala. A low-pressure system in the Arabian Sea is expected to bring heavy to very heavy rains over the next 48 hours. Local authorities have advised fishermen not to venture into deep sea waters.",
        "label": 1
    },
    {
        "category": "business",
        "title": "Stock markets close flat in volatile session as IT shares offset banking gains",
        "body": "The benchmark BSE Sensex closed 15 points higher, while the Nifty 50 ended flat in a volatile trading session. Gains in major banking stocks like HDFC and ICICI were offset by profit-booking in IT majors. Market experts suggest investors are waiting for global inflation data before making large bets.",
        "label": 1
    },
    {
        "category": "international",
        "title": "Bilateral trade talks between India and United Kingdom enter thirteenth round",
        "body": "Officials from India and the UK have commenced the thirteenth round of negotiations for a Free Trade Agreement in New Delhi. The discussions are focused on services, intellectual property rights, and tariffs on manufactured items. A joint statement indicated that progress has been steady on most of the chapters.",
        "label": 1
    },
    {
        "category": "sports",
        "title": "National Athletics Championship to kick off in Bengaluru next week",
        "body": "The 63rd National Open Athletics Championship will begin at the Kanteerava Stadium in Bengaluru. Over 800 athletes from across the country will compete in 24 track and field events. The Athletics Federation of India announced that electronic timing systems and anti-doping protocols will be fully implemented.",
        "label": 1
    },
    {
        "category": "national",
        "title": "Supreme Court schedules hearing on environmental clearance of infrastructure projects",
        "body": "The Supreme Court of India has listed petitions challenging the forest clearances granted to highway expansion projects for hearing next month. The bench will review reports submitted by the expert committee on ecological preservation. Legal representatives of both sides have filed their written submissions.",
        "label": 1
    },
    {
        "category": "business",
        "title": "Wholesale inflation stays stable at 1.2% in May, aligned with predictions",
        "body": "India's wholesale price index (WPI) inflation remained stable at 1.2% in the month of May, according to government data. The stability in fuel and power prices compensated for a slight rise in primary food articles. Economists stated that inflation levels remain within the expected trajectory.",
        "label": 1
    },
    {
        "category": "sports",
        "title": "Selection committee announces 15-member squad for upcoming women's cricket series",
        "body": "The Board of Control for Cricket in India (BCCI) has announced the squad for the upcoming three-match ODI series against South Africa. The team includes two new faces from the domestic leagues. The selector noted that the team combination was chosen keeping in mind the subcontinental pitches.",
        "label": 1
    },
    {
        "category": "national",
        "title": "Central university announces admission dates and eligibility criteria for undergraduate courses",
        "body": "Delhi University has released its schedule for admissions to undergraduate programs based on the common entrance test scores. Students can register on the portal starting Monday. The university has set up helpdesks to assist applicants in choosing their subject combinations and filing documents.",
        "label": 1
    },

    # Anti-Government (Label 0)
    {
        "category": "national",
        "title": "Retail inflation surges to 6.2 percent, putting heavy burden on middle class",
        "body": "India's consumer price index (CPI) retail inflation has climbed to 6.2 percent, crossing the RBI's comfort zone. The surge was driven by rising food prices, high fuel costs, and supply chain disruptions. Opposition parties criticized the government's economic mismanagement, stating that common citizens are facing severe financial distress.",
        "label": 0
    },
    {
        "category": "national",
        "title": "Farmers launch protest demanding legal guarantee for Minimum Support Price",
        "body": "Thousands of farmers from neighboring states have gathered near the capital borders to protest against the government's failure to provide a statutory guarantee for MSP. Farm union leaders alleged that the agricultural policy favors large corporations over small landholders. Police have set up barricades, leading to massive traffic congestion.",
        "label": 0
    },
    {
        "category": "business",
        "title": "Industrial output contracts by 1.8% reflecting sluggish domestic demand",
        "body": "India's Index of Industrial Production (IIP) contracted by 1.8% in the last quarter, raising concerns about economic recovery. Core manufacturing and mining sectors showed negative growth. Industry bodies expressed disappointment, citing high borrowing costs and lack of supportive government measures as main reasons.",
        "label": 0
    },
    {
        "category": "national",
        "title": "Delay in national highway construction projects leads to 40% budget cost overruns",
        "body": "An audit report revealed that more than 200 key highway and infrastructure projects are facing severe delays. The slow progress has caused the total cost to balloon by over 40%, costing the taxpayer billions. Critics pointed to administrative red tape, land acquisition failures, and lack of coordination among ministries.",
        "label": 0
    },
    {
        "category": "national",
        "title": "Unemployment rate rises in urban sectors as job creation remains slow",
        "body": "The latest periodic labor force survey indicates that the unemployment rate in urban areas has risen to a worrying 7.8%. Despite tall government claims of job creation, millions of educated youth remain without formal employment. Policy analysts warned that jobless growth could lead to deep social instability.",
        "label": 0
    },
    {
        "category": "national",
        "title": "New environmental bill criticized by activists for weakening forest conservation laws",
        "body": "Environmentalists and indigenous community leaders have staged protests against the new forest conservation amendment bill. They argue that the proposed legislation weakens regulation, allowing private companies to exploit eco-sensitive zones. Activists accused the ministry of bypassing public consultation and favoring corporate interests.",
        "label": 0
    },
    {
        "category": "business",
        "title": "Micro and small scale industries struggle due to high compliance and tax burdens",
        "body": "A survey of MSME owners reveals that over 30% of small units have downsized due to high compliance costs under the current GST regime and slow credit access. Business associations stated that the government's economic packages have not trickled down to help struggling micro-entrepreneurs on the ground.",
        "label": 0
    },
    {
        "category": "national",
        "title": "Aadhaar authentication failures cause exclusion in rural food subsidy schemes",
        "body": "Reports from several rural blocks indicate that thousands of families have been denied monthly food rations due to persistent Aadhaar biometric mismatches and poor internet connectivity. Human rights organizations accused the food department of enforcing digitization without building proper local telecom infrastructure.",
        "label": 0
    },
    {
        "category": "sports",
        "title": "State sports academy lacks basic facilities despite high allocation, athletes protest",
        "body": "National-level athletes at the state-run sports facility staged a demonstration protesting against sub-standard food, leaking hostels, and lack of training gear. Despite the government claiming massive sports development budgets, athletes alleged that systemic corruption and administrative neglect have left the academy in a shambles.",
        "label": 0
    },
    {
        "category": "national",
        "title": "Public sector bank employees protest against government's proposed privatization drive",
        "body": "Bank unions across the country have declared a two-day strike to protest against the government's plan to privatize major public sector banks. Union leaders stated that selling public banks will hurt rural banking, decrease job security, and compromise financial sovereignty. Customer services were severely hit.",
        "label": 0
    }
]

# Duplicate the dataset with some minor variations in titles/bodies to build a larger set for machine learning
def generate_synthetic_data(seed, count=120):
    np.random.seed(42)
    categories = ["national", "business", "sports", "international", "miscellaneous"]
    
    # Variations of words to inject
    positive_phrases = ["great progress", "excellent development", "historic milestone", "major reform success", "lauded by citizens", "economic breakthrough", "praiseworthy effort"]
    negative_phrases = ["severe criticism", "massive protest", "rising concerns", "cost overrun and delay", "public distress", "neglect and apathy", "financial burden", "sluggish performance"]
    neutral_phrases = ["held a meeting", "announced dates", "released guidelines", "will be organized", "discussed bilateral issues", "according to official reports", "market analyst stated"]
    
    records = []
    
    # First, append the seed records
    records.extend(seed)
    
    # Then generate variations
    for i in range(count - len(seed)):
        base = np.random.choice(seed)
        lbl = base["label"]
        cat = np.random.choice(categories)
        
        # Modify title and body slightly
        title = base["title"]
        body = base["body"]
        
        if lbl == 2:
            phrase = np.random.choice(positive_phrases)
            title = f"{phrase}: {title}"
            body = f"{body} This initiative represents a {phrase} for the country, strengthening national interest."
        elif lbl == 0:
            phrase = np.random.choice(negative_phrases)
            title = f"Concerns rise over: {title}"
            body = f"{body} Public experts express {phrase} and urge the authorities to address the systemic issues immediately."
        else:
            phrase = np.random.choice(neutral_phrases)
            title = f"Update: {title}"
            body = f"{body} According to reports, representatives {phrase} to review the progress of the schedule."
            
        records.append({
            "category": cat,
            "title": title,
            "body": body,
            "label": lbl
        })
        
    return records


def seed_dataset_if_needed():
    path = os.path.join(Config.LABELLED_DIR, "news_sentiment_labels.csv")
    if not os.path.exists(path):
        print("Seeding news sentiment labelled dataset...")
        records = generate_synthetic_data(SEED_DATA, count=180)
        
        # Save to CSV
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["category", "title", "body", "label"])
            writer.writeheader()
            writer.writerows(records)
        print(f"Seeded {len(records)} records into {path}")
    else:
        print(f"Labelled dataset already exists at {path}")


def train_and_evaluate_models():
    # Priority 1: Indian News Political Stance Dataset (provided by user)
    indian_dataset_path = r"C:\Summer intern '26 @Akashwani Bhawan\indian_news_political_stance_dataset.csv"
    
    # Fallback Priority 2: English Political Tweets
    archive_dir = os.path.join(Config.DATA_DIR, "archive_dataset")
    train_csv = os.path.join(archive_dir, "EnglishPoliticalTweets.csv")
    test_csv = os.path.join(archive_dir, "DataTest.csv")
    
    dataset_name = ""
    X_train_full_texts = []
    y_train_full = []
    X_test_ext = None
    y_test_ext = None
    
    if os.path.exists(indian_dataset_path):
        print(f"Found Indian political stance dataset at {indian_dataset_path}. Loading...")
        df = pd.read_csv(indian_dataset_path)
        
        # Clean data
        df = df.dropna(subset=["headline", "text", "label"])
        df["label"] = df["label"].astype(str).str.strip().str.lower()
        
        # Map labels: anti_govt -> 0, neutral -> 1, pro_govt -> 2
        label_map = {"anti_govt": 0, "neutral": 1, "pro_govt": 2}
        df["label_id"] = df["label"].map(label_map)
        
        # Create features
        df["text_feature"] = df["headline"] + " " + df["text"]
        
        # Clean rows where label_id is missing
        df = df.dropna(subset=["label_id"])
        df["label_id"] = df["label_id"].astype(int)
        
        X_train_full_texts = df["text_feature"].tolist()
        y_train_full = df["label_id"].tolist()
        dataset_name = "Indian News Political Stance Dataset"
        print(f"Loaded {len(df)} base Indian news stance samples.")
        
        # 1. Add diverse non-templated synthetic samples to break keyword templates
        diverse_samples = [
            ("Citizen complaints grow over delayed clean drinking water supply in rural districts",
             "Many villages report that local authorities have failed to address the contaminated water issues, causing severe health concerns among children.", 0),
            ("Bureaucratic red tape delays crucial state hospital expansion project by three years",
             "The health infrastructure department has faced criticism from doctors and citizens for failing to speed up approvals, leading to cost overruns.", 0),
            ("Rising cost of daily essentials puts severe financial strain on low income households",
             "Common citizens complain that the pricing of basic food items and household goods has risen sharply over the past few months, leaving them struggling.", 0),
            ("Infrastructural upgrade: All remote villages in hilly tracts successfully connected to national power grid",
             "Local community members celebrated the arrival of electricity. The energy ministry's swift completion of the electrification project was widely praised.", 2),
            ("Direct benefit transfer scheme successfully transfers financial assistance to over one million farmers",
             "The agricultural department reported zero leaks in the payment transfers. Farmers expressed happiness and support for the streamlined scheme.", 2),
            ("Indian export revenues reach historic high of 450 billion dollars, boosting local manufacturing",
             "The trade ministry attributed this economic breakthrough to robust export promotion policies and simplified customs clearances.", 2),
            ("Central board releases new exam date sheet and safety guidelines for high school students",
             "The education department announced that the annual board examinations will begin next month under strict supervision.", 1),
            ("Reserve Bank of India starts three-day policy review meeting to assess interest rates",
             "IT shares and banking stocks fluctuated slightly as investors waited for the monetary policy committee's announcement.", 1),
            ("Meteorological department issues storm and heavy rain warnings for southern coastal districts",
             "Local administration has advised residents to stay indoors and set up emergency helplines for assistance.", 1),
        ]
        
        for i in range(150):
            base_h, base_t, lbl = diverse_samples[i % len(diverse_samples)]
            h = f"Update on: {base_h}" if i % 2 == 0 else f"Report: {base_h}"
            t = f"{base_t} Analysts are currently monitoring the situation."
            X_train_full_texts.append(h + " " + t)
            y_train_full.append(lbl)
            
        print(f"Dataset size after adding diverse templates: {len(X_train_full_texts)}")
        
        # 2. Add semi-supervised real-world NewsOnAir articles from archive
        archive_path = os.path.join(Config.RAW_DIR, "archive_articles.json")
        if os.path.exists(archive_path):
            try:
                with open(archive_path, "r", encoding="utf-8") as f:
                    archive_data = json.load(f)
                    
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                analyzer = SentimentIntensityAnalyzer()
                archive_samples = []
                
                for art in archive_data:
                    title = art.get("title", "")
                    body = art.get("body", "")
                    text = f"{title} {body}"
                    
                    scores = analyzer.polarity_scores(text)
                    compound = scores["compound"]
                    
                    is_govt = any(kw in text.lower() for kw in ["government", "govt", "pm modi", "prime minister", "ministry"])
                    if is_govt:
                        if compound > 0.3:
                            lbl = 2
                        elif compound < -0.3:
                            lbl = 0
                        else:
                            lbl = 1
                    else:
                        lbl = 1
                    archive_samples.append((text, lbl))
                    
                df_arch = pd.DataFrame(archive_samples, columns=["text", "label"])
                for lbl in [0, 1, 2]:
                    sub_df = df_arch[df_arch["label"] == lbl]
                    sample_size = min(len(sub_df), 150)
                    sampled = sub_df.sample(sample_size, random_state=42)
                    for text in sampled["text"].tolist():
                        X_train_full_texts.append(text)
                        y_train_full.append(lbl)
                        
                print(f"Dataset size after adding real-world articles: {len(X_train_full_texts)}")
            except Exception as e:
                print(f"Could not load archive articles for training: {e}")
        
        # 3. Load feedback labels if they exist
        feedback_path = os.path.join(Config.LABELLED_DIR, "feedback_labels.csv")
        if os.path.exists(feedback_path):
            print(f"Found feedback labels at {feedback_path}. Merging into training set...")
            try:
                f_df = pd.read_csv(feedback_path)
                f_df = f_df.dropna(subset=["text_feature", "label_id"])
                for _, row in f_df.iterrows():
                    X_train_full_texts.append(row["text_feature"])
                    y_train_full.append(int(row["label_id"]))
            except Exception as e:
                print(f"Error loading feedback labels: {e}")
                
        # Convert to Series/Arrays
        X_train_full = pd.Series(X_train_full_texts)
        y_train_full = pd.Series(y_train_full)
        
    elif os.path.exists(train_csv) and os.path.exists(test_csv):
        print("Found political tweets dataset. Loading English political tweets...")
        train_df = pd.read_csv(train_csv)
        test_df = pd.read_csv(test_csv)
        
        train_df = train_df.dropna(subset=["OriginalTweet", "Sentiment"])
        train_df["Sentiment"] = train_df["Sentiment"].astype(str).str.strip().str.upper()
        
        test_df = test_df.dropna(subset=["OriginalTweet", "Sentiment"])
        test_df["Sentiment"] = test_df["Sentiment"].astype(str).str.strip().str.upper()
        
        label_map = {"POSITIVE": 2, "NEUTRAL": 1, "NEGATIVE": 0}
        
        train_df = train_df[train_df["Sentiment"].isin(label_map.keys())]
        test_df = test_df[test_df["Sentiment"].isin(label_map.keys())]
        
        train_df["label"] = train_df["Sentiment"].map(label_map)
        test_df["label"] = test_df["Sentiment"].map(label_map)
        
        train_df["text"] = train_df["OriginalTweet"]
        test_df["text"] = test_df["OriginalTweet"]
        
        X_train_full = train_df["text"]
        y_train_full = train_df["label"]
        X_test_ext = test_df["text"]
        y_test_ext = test_df["label"]
        dataset_name = "IEEE Government Polarity Tweets"
        print(f"Loaded {len(train_df)} training samples and {len(test_df)} test samples.")
        
    else:
        print("Archive datasets not found. Seeding synthetic data instead...")
        seed_dataset_if_needed()
        path = os.path.join(Config.LABELLED_DIR, "news_sentiment_labels.csv")
        df = pd.read_csv(path)
        df["text"] = df["title"] + " " + df["body"]
        X_train_full = df["text"]
        y_train_full = df["label"]
        dataset_name = "Synthetic Seed Dataset"
        
    # Split training set for validation / testing if no external test set exists
    if X_test_ext is None:
        X_train, X_test, y_train, y_test_eval = train_test_split(
            X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
        )
    else:
        X_train = X_train_full
        y_train = y_train_full
        X_test = X_test_ext
        y_test_eval = y_test_ext
        
    # Vectorize and extract combined features
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    
    # Fit vectorizer on training text
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Extract dense features
    train_dense = get_vader_and_govt_features(X_train)
    test_dense = get_vader_and_govt_features(X_test)
    
    train_dense_sparse = scipy.sparse.csr_matrix(train_dense)
    test_dense_sparse = scipy.sparse.csr_matrix(test_dense)
    
    X_train_vec = scipy.sparse.hstack([X_train_tfidf, train_dense_sparse])
    X_test_vec = scipy.sparse.hstack([X_test_tfidf, test_dense_sparse])
    
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, C=1.0, max_iter=1000),
        "Linear SVM": LinearSVC(random_state=42, C=1.0, max_iter=2000),
        "Naive Bayes": MultinomialNB()
    }
    
    results = {}
    best_f1 = 0
    best_model_name = ""
    best_model = None
    
    for name, model in models.items():
        # Fit model
        model.fit(X_train_vec, y_train)
        
        # Predict on validation/test holdout
        preds = model.predict(X_test_vec)
        
        # Metrics
        acc = accuracy_score(y_test_eval, preds)
        macro_f1 = f1_score(y_test_eval, preds, average="macro")
        
        precision, recall, fscore, _ = precision_recall_fscore_support(
            y_test_eval, preds, average=None, labels=[0, 1, 2]
        )
        cm = confusion_matrix(y_test_eval, preds).tolist()
        
        results[name] = {
            "accuracy": float(acc),
            "macro_f1": float(macro_f1),
            "precision": [float(p) for p in precision],
            "recall": [float(r) for r in recall],
            "f1_scores": [float(f) for f in fscore],
            "confusion_matrix": cm
        }
        
        print(f"Model: {name} - Test Accuracy: {acc:.4f}, Test Macro F1: {macro_f1:.4f}")
        
        if macro_f1 > best_f1:
            best_f1 = macro_f1
            best_model_name = name
            best_model = model
            
    print(f"Best Model Selected: {best_model_name} (Test Macro F1: {best_f1:.4f})")
    
    # Retrain best model on full dataset
    X_full_tfidf = vectorizer.fit_transform(X_train_full)
    full_dense = get_vader_and_govt_features(X_train_full)
    full_dense_sparse = scipy.sparse.csr_matrix(full_dense)
    X_full_vec = scipy.sparse.hstack([X_full_tfidf, full_dense_sparse])
    
    best_model.fit(X_full_vec, y_train_full)
    
    # Save best model, vectorizer and metadata
    model_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "sentiment_classifier.joblib")
    vectorizer_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "tfidf_vectorizer.joblib")
    metadata_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "model_metadata.json")
    
    joblib.dump(best_model, model_save_path)
    joblib.dump(vectorizer, vectorizer_save_path)
    
    metadata = {
        "best_model_name": best_model_name,
        "evaluation_metrics": results,
        "classes": {0: "Anti-Govt", 1: "Neutral", 2: "Pro-Govt"},
        "trained_date": pd.Timestamp.now().isoformat(),
        "total_records": len(X_train_full),
        "dataset_used": dataset_name
    }
    
    with open(metadata_save_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print("Saved best model, vectorizer, and metadata.")
    return metadata


def load_keyword_rules():
    path = os.path.join(Config.LABELLED_DIR, "keyword_rules.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def load_model_and_predict(text: str):
    # Check keyword rules first
    rules = load_keyword_rules()
    text_lower = text.lower()
    for kw, label in rules.items():
        if kw.lower() in text_lower:
            return int(label), 1.0, "keyword_rule"

    model_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "sentiment_classifier.joblib")
    vectorizer_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "tfidf_vectorizer.joblib")
    
    if not os.path.exists(model_save_path) or not os.path.exists(vectorizer_save_path):
        # Fallback to lexical/rule-based sentiment if model is not trained yet
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]
        
        is_govt = any(kw in text.lower() for kw in ["government", "govt", "pm modi", "prime minister", "ministry", "policy", "scheme"])
        
        if not is_govt:
            label = 1 # Neutral
            conf = 0.80
        else:
            if compound > 0.15:
                label = 2 # Pro-Govt
                conf = min(0.5 + compound * 0.5, 0.95)
            elif compound < -0.15:
                label = 0 # Anti-Govt
                conf = min(0.5 + abs(compound) * 0.5, 0.95)
            else:
                label = 1 # Neutral
                conf = 0.70
        return int(label), float(conf), "vader_heuristic"
        
    model = joblib.load(model_save_path)
    vectorizer = joblib.load(vectorizer_save_path)
    
    # Extract combined features
    tfidf_feat = vectorizer.transform([text])
    dense_feat = get_vader_and_govt_features([text])
    dense_feat_sparse = scipy.sparse.csr_matrix(dense_feat)
    vec = scipy.sparse.hstack([tfidf_feat, dense_feat_sparse])
    
    pred = model.predict(vec)[0]
    
    # Get probability/confidence
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(vec)[0]
        conf = probs[pred]
    elif hasattr(model, "decision_function"):
        df_score = model.decision_function(vec)[0]
        if isinstance(df_score, (float, np.float64, np.float32)):
            p = 1 / (1 + np.exp(-df_score))
            probs = [1 - p, p]
            conf = probs[pred]
        else:
            exp_scores = np.exp(df_score)
            probs = exp_scores / np.sum(exp_scores)
            conf = probs[pred]
    else:
        conf = 1.0
        
    return int(pred), float(conf), "machine_learning"


def load_model_and_predict_batch(texts: list[str]) -> list[tuple[int, float, str]]:
    """Predicts sentiment for a list of texts in batch. Highly optimized."""
    rules = load_keyword_rules()
    
    results = [None] * len(texts)
    ml_indices = []
    ml_texts = []
    
    # Check keyword rules first
    for i, text in enumerate(texts):
        matched = False
        text_lower = text.lower()
        for kw, label in rules.items():
            if kw.lower() in text_lower:
                results[i] = (int(label), 1.0, "keyword_rule")
                matched = True
                break
        if not matched:
            ml_indices.append(i)
            ml_texts.append(text)
            
    if ml_texts:
        ml_results = _load_model_and_predict_batch_ml(ml_texts)
        for idx, res in zip(ml_indices, ml_results):
            results[idx] = res
            
    return results


def _load_model_and_predict_batch_ml(texts: list[str]) -> list[tuple[int, float, str]]:
    """Predicts sentiment for a list of texts using machine learning (fallback)."""
    model_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "sentiment_classifier.joblib")
    vectorizer_save_path = os.path.join(Config.SENTIMENT_MODEL_DIR, "tfidf_vectorizer.joblib")
    
    if not os.path.exists(model_save_path) or not os.path.exists(vectorizer_save_path):
        # Fallback to lexical/rule-based sentiment in batch
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        results = []
        for text in texts:
            scores = analyzer.polarity_scores(text)
            compound = scores["compound"]
            is_govt = any(kw in text.lower() for kw in ["government", "govt", "pm modi", "prime minister", "ministry", "policy", "scheme"])
            if not is_govt:
                label = 1
                conf = 0.80
            else:
                if compound > 0.15:
                    label = 2
                    conf = min(0.5 + compound * 0.5, 0.95)
                elif compound < -0.15:
                    label = 0
                    conf = min(0.5 + abs(compound) * 0.5, 0.95)
                else:
                    label = 1
                    conf = 0.70
            results.append((int(label), float(conf), "vader_heuristic"))
        return results
        
    model = joblib.load(model_save_path)
    vectorizer = joblib.load(vectorizer_save_path)
    
    tfidf_feats = vectorizer.transform(texts)
    dense_feats = get_vader_and_govt_features(texts)
    dense_feats_sparse = scipy.sparse.csr_matrix(dense_feats)
    vecs = scipy.sparse.hstack([tfidf_feats, dense_feats_sparse])
    
    preds = model.predict(vecs)
    
    results = []
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(vecs)
        for i, pred in enumerate(preds):
            results.append((int(pred), float(probs[i][pred]), "machine_learning"))
    elif hasattr(model, "decision_function"):
        df_scores = model.decision_function(vecs)
        for i, pred in enumerate(preds):
            df_score = df_scores[i]
            if isinstance(df_score, (float, np.float64, np.float32)):
                p = 1 / (1 + np.exp(-df_score))
                probs = [1 - p, p]
                results.append((int(pred), float(probs[pred]), "machine_learning"))
            else:
                exp_scores = np.exp(df_score)
                probs = exp_scores / np.sum(exp_scores)
                results.append((int(pred), float(probs[pred]), "machine_learning"))
    else:
        for pred in preds:
            results.append((int(pred), 1.0, "machine_learning"))
            
    return results


if __name__ == "__main__":
    train_and_evaluate_models()
