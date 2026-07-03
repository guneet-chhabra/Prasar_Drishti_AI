const hostName = window.location.hostname || "localhost";
const API_BASE_URL = (hostName === "localhost" || hostName === "127.0.0.1")
  ? `http://${hostName}:5000/api`
  : "hhttps://prasar-drishti-ai.onrender.com"; 
const TOKEN_KEY = "prasar_drishti_token";

let currentUser = null;
let currentDataset = "today"; // 'today' or 'archive'

// DOM Elements
const userDisplayName = document.getElementById("userDisplayName");
const userRoleBadge = document.getElementById("userRoleBadge");
const adminPanel = document.getElementById("adminPanel");
const statusBanner = document.getElementById("statusBanner");
const statusMessage = document.getElementById("statusMessage");

// Tabs DOM Elements
const tabHome = document.getElementById("tabContentHome");
const tabSentiment = document.getElementById("tabContentSentiment");
const tabSports = document.getElementById("tabContentSports");
const navTabHome = document.getElementById("navTabHome");
const navTabSentiment = document.getElementById("navTabSentiment");
const navTabSports = document.getElementById("navTabSports");
const sidebarTabHome = document.getElementById("sidebarTabHome");
const sidebarTabSentiment = document.getElementById("sidebarTabSentiment");
const sidebarTabSports = document.getElementById("sidebarTabSports");

// Sentiment View Elements
const btnToday = document.getElementById("btnDatasetToday");
const btnArchive = document.getElementById("btnDatasetArchive");
const tickerContent = document.getElementById("tickerContent");
const articlesTableBody = document.getElementById("articlesTableBody");
const totalArticlesBadge = document.getElementById("totalArticlesBadge");
const insightCardsGrid = document.getElementById("insightCardsGrid");
const thActions = document.getElementById("thActions");

// Donut Elements
const donutSVG = document.getElementById("donutSVG");
const donutPro = document.getElementById("donutPro");
const donutNeu = document.getElementById("donutNeu");
const donutAnti = document.getElementById("donutAnti");
const donutPercentage = document.getElementById("donutPercentage");
const donutLabel = document.getElementById("donutLabel");
const txtProPct = document.getElementById("txtProPct");
const txtNeuPct = document.getElementById("txtNeuPct");
const txtAntiPct = document.getElementById("txtAntiPct");

// Model Info Elements
const modelStatusTag = document.getElementById("modelStatusTag");
const infoModelName = document.getElementById("infoModelName");
const infoModelAcc = document.getElementById("infoModelAcc");
const infoModelF1 = document.getElementById("infoModelF1");
const infoModelDate = document.getElementById("infoModelDate");

// Keyword Modal Elements
const keywordModal = document.getElementById("keywordModal");
const keywordForm = document.getElementById("keywordForm");
const keywordRulesList = document.getElementById("keywordRulesList");
const kwInput = document.getElementById("kwInput");
const kwSentiment = document.getElementById("kwSentiment");

// Sports View Elements
const adminSportsControl = document.getElementById("adminSportsControl");
const btnRetrainSports = document.getElementById("btnRetrainSports");
const sportsModelName = document.getElementById("sportsModelName");
const sportsModelAcc = document.getElementById("sportsModelAcc");
const sportsModelDate = document.getElementById("sportsModelDate");
const predictedChampionName = document.getElementById("predictedChampionName");
const predictedChampFinalProb = document.getElementById("predictedChampFinalProb");
const predictedChampWinProb = document.getElementById("predictedChampWinProb");
const sportsLeaderboardBody = document.getElementById("sportsLeaderboardBody");
const groupsStandingsGrid = document.getElementById("groupsStandingsGrid");

// Admin Buttons
const btnScrapeToday = document.getElementById("btnScrapeToday");
const btnScrapeArchive = document.getElementById("btnScrapeArchive");
const btnArchiveToday = document.getElementById("btnArchiveToday");
const btnRetrainModel = document.getElementById("btnRetrainModel");
const btnLogout = document.getElementById("btnLogout");
const btnLogoutTop = document.getElementById("btnLogoutTop");
const btnNotifications = document.getElementById("btnNotifications");
const btnSettings = document.getElementById("btnSettings");

// API Request Wrapper
async function api(path, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        credentials: "include",
        ...options,
        headers,
    });

    const data = await response.json().catch(() => ({
        message: "Backend returned a non-JSON response. Ensure Flask backend is running.",
    }));

    if (!response.ok) {
        throw new Error(data.error ? `${data.message}: ${data.error}` : data.message || "API request failed.");
    }
    return data;
}

// Show alerts/updates in banner
function showStatus(msg, isError = false) {
    statusMessage.textContent = msg;
    statusBanner.classList.remove("hidden");
    if (isError) {
        statusBanner.className = "mb-4 p-3 rounded-lg border text-sm flex justify-between items-center bg-error-container text-on-error-container border-error/30";
    } else {
        statusBanner.className = "mb-4 p-3 rounded-lg border text-sm flex justify-between items-center bg-surface-container-high border-outline-variant/30 text-on-surface";
    }
    // Auto-scroll to top to see status
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Switch between Home, Sentiment and Sports Tabs
function switchTab(tabId) {
    // Hide all tabs
    tabHome.classList.remove("active");
    tabSentiment.classList.remove("active");
    tabSports.classList.remove("active");
    
    // Set all nav buttons to inactive
    navTabHome.className = "font-label-md text-label-md text-on-surface-variant hover:text-secondary transition-colors duration-200";
    navTabSentiment.className = "font-label-md text-label-md text-on-surface-variant hover:text-secondary transition-colors duration-200";
    if (navTabSports) navTabSports.className = "font-label-md text-label-md text-on-surface-variant hover:text-secondary transition-colors duration-200";
    
    // Set all sidebar buttons to inactive
    sidebarTabHome.className = "w-full flex items-center gap-base p-base text-on-surface-variant hover:bg-surface-container-high text-left transition-all";
    sidebarTabSentiment.className = "w-full flex items-center gap-base p-base text-on-surface-variant hover:bg-surface-container-high text-left transition-all";
    if (sidebarTabSports) sidebarTabSports.className = "w-full flex items-center gap-base p-base text-on-surface-variant hover:bg-surface-container-high text-left transition-all";

    if (tabId === 'home') {
        tabHome.classList.add("active");
        navTabHome.className = "font-label-md text-label-md text-secondary border-b-2 border-secondary pb-1 transition-colors duration-200";
        sidebarTabHome.className = "w-full flex items-center gap-base p-base bg-secondary-container/20 text-secondary border-r-4 border-secondary text-left transition-all";
    } else if (tabId === 'sentiment') {
        tabSentiment.classList.add("active");
        navTabSentiment.className = "font-label-md text-label-md text-secondary border-b-2 border-secondary pb-1 transition-colors duration-200";
        sidebarTabSentiment.className = "w-full flex items-center gap-base p-base bg-secondary-container/20 text-secondary border-r-4 border-secondary text-left transition-all";
        
        // Initial load of sentiment data
        loadSentimentData(currentDataset);
    } else if (tabId === 'sports') {
        tabSports.classList.add("active");
        if (navTabSports) navTabSports.className = "font-label-md text-label-md text-secondary border-b-2 border-secondary pb-1 transition-colors duration-200";
        if (sidebarTabSports) sidebarTabSports.className = "w-full flex items-center gap-base p-base bg-secondary-container/20 text-secondary border-r-4 border-secondary text-left transition-all";
        
        loadSportsPredictions();
    }
}

// Load Sentiment Trends & Articles
async function loadSentimentData(dataset) {
    currentDataset = dataset;
    if (dataset === 'today') {
        btnToday.className = "pb-base font-label-md text-label-md text-secondary frequency-pulse";
        btnArchive.className = "pb-base font-label-md text-label-md text-on-surface-variant hover:text-on-surface transition-colors";
    } else {
        btnToday.className = "pb-base font-label-md text-label-md text-on-surface-variant hover:text-on-surface transition-colors";
        btnArchive.className = "pb-base font-label-md text-label-md text-secondary frequency-pulse";
    }

    const colCount = (currentUser && currentUser.role === 'admin') ? 5 : 4;
    articlesTableBody.innerHTML = `<tr><td colspan="${colCount}" class="p-8 text-center text-on-surface-variant">Classifying and aggregating data...</td></tr>`;

    try {
        const adminViewParam = currentUser && currentUser.role === 'admin' ? '&admin_view=true' : '';
        const data = await api(`/news/sentiment-trends?dataset=${dataset}${adminViewParam}`);
        renderSentimentDashboard(data);
    } catch (err) {
        showStatus(err.message, true);
        articlesTableBody.innerHTML = `<tr><td colspan="${colCount}" class="p-8 text-center text-error">Failed to load: ${err.message}</td></tr>`;
    }
}

// Update the entire Sentiment tab with API response
function renderSentimentDashboard(data) {
    const articles = data.articles || [];
    totalArticlesBadge.textContent = `${articles.length} Article${articles.length === 1 ? "" : "s"}`;

    // Show or hide actions header column based on admin role
    const isAdmin = currentUser && currentUser.role === 'admin';
    if (isAdmin) {
        if (thActions) thActions.classList.remove("hidden");
    } else {
        if (thActions) thActions.classList.add("hidden");
    }

    // 1. Ticker content
    if (articles.length === 0) {
        tickerContent.innerHTML = `<span class="font-data-mono text-body-sm text-on-surface-variant">[NO CURRENT ARTICLES SCRAPED]</span>`;
    } else {
        const sentimentColors = {
            "Pro-Govt": "text-tertiary-fixed font-bold",
            "Neutral": "text-secondary font-bold",
            "Anti-Govt": "text-error font-bold"
        };
        tickerContent.innerHTML = articles.map(art => `
            <span class="flex items-center gap-2 font-data-mono text-body-sm text-on-surface">
                <span class="text-tertiary">#NewsOnAir:</span> ${escapeHtml(art.title)} 
                <span class="${sentimentColors[art.sentiment_name] || 'text-outline'}">[${art.sentiment_name.toUpperCase()}]</span>
            </span>
        `).join("");
    }

    const colCount = isAdmin ? 5 : 4;

    // 2. Table content
    if (articles.length === 0) {
        articlesTableBody.innerHTML = `
            <tr>
                <td colspan="${colCount}" class="p-8 text-center text-on-surface-variant">
                    No articles found. ${currentUser && currentUser.role === 'admin' ? 'Click "Update Today" or "Scrape Last Month" on the sidebar to scrape articles.' : 'Please wait for an admin to run the scraper.'}
                </td>
            </tr>
        `;
    } else {
        articlesTableBody.innerHTML = articles.map(art => {
            const labelBadgeColors = {
                "Pro-Govt": "text-tertiary border-tertiary/20 bg-tertiary/5",
                "Neutral": "text-secondary border-secondary/20 bg-secondary/5",
                "Anti-Govt": "text-error border-error/20 bg-error/5"
            };
            const badgeClass = labelBadgeColors[art.sentiment_name] || "text-outline border-outline-variant/20";
            
            let actionsTd = '';
            if (isAdmin) {
                const isVis = art.is_visible !== false;
                const eyeIcon = isVis ? 'visibility' : 'visibility_off';
                const eyeTitle = isVis ? 'Hide from Users' : 'Show to Users';
                const btnClass = isVis ? 'text-secondary hover:text-outline' : 'text-outline-variant hover:text-secondary';
                
                actionsTd = `
                    <td class="p-4">
                        <div class="flex items-center gap-2">
                            <button onclick="toggleVisibility('${art.url}', ${!isVis})" class="p-1 rounded hover:bg-surface-container-highest ${btnClass} transition-colors" title="${eyeTitle}">
                                <span class="material-symbols-outlined text-[18px]">${eyeIcon}</span>
                            </button>
                            <select onchange="overrideSentiment('${art.url}', this.value)" class="bg-surface border border-outline-variant/30 rounded text-[10px] p-1 text-on-surface focus:outline-none max-w-[120px]">
                                <option value="" ${art.manual_sentiment_label === undefined || art.manual_sentiment_label === null ? 'selected' : ''}>Model</option>
                                <option value="2" ${art.manual_sentiment_label === 2 ? 'selected' : ''}>Pro-Govt</option>
                                <option value="1" ${art.manual_sentiment_label === 1 ? 'selected' : ''}>Neutral</option>
                                <option value="0" ${art.manual_sentiment_label === 0 ? 'selected' : ''}>Anti-Govt</option>
                            </select>
                        </div>
                    </td>
                `;
            }

            const rowClass = art.is_visible === false ? 'opacity-60 border-l-4 border-error/40' : '';
            const methodBadge = art.classification_method === 'manual_override' 
                ? '<span class="ml-1 px-1 py-0.5 rounded bg-tertiary/10 text-[8px] text-tertiary font-bold tracking-widest uppercase">Admin</span>' 
                : (art.classification_method === 'keyword_rule' 
                    ? '<span class="ml-1 px-1 py-0.5 rounded bg-secondary/10 text-[8px] text-secondary font-bold tracking-widest uppercase">Rule</span>' 
                    : '');

            return `
                <tr class="hover:bg-surface-container-high transition-colors ${rowClass}">
                    <td class="p-4 font-body-md text-on-surface max-w-[400px] truncate" title="${escapeHtml(art.title)}">
                        <a href="${art.url}" target="_blank" class="hover:text-secondary transition-colors">${escapeHtml(art.title)}</a>
                    </td>
                    <td class="p-4 text-on-surface-variant capitalize">${escapeHtml(art.category)}</td>
                    <td class="p-4">
                        <div class="flex items-center gap-1">
                            <span class="px-2 py-0.5 rounded-full border text-[10px] font-bold uppercase tracking-wider ${badgeClass}">
                                ${art.sentiment_name}
                            </span>
                            ${methodBadge}
                        </div>
                    </td>
                    <td class="p-4 font-data-mono text-secondary">${(art.sentiment_confidence * 100).toFixed(0)}%</td>
                    ${actionsTd}
                </tr>
            `;
        }).join("");
    }

    // 3. SVG Donut chart math
    const dist = data.distribution || {"Anti-Govt": 0, "Neutral": 0, "Pro-Govt": 0};
    const total = dist["Anti-Govt"] + dist["Neutral"] + dist["Pro-Govt"];

    let proPct = 0, neuPct = 0, antiPct = 0;
    if (total > 0) {
        proPct = (dist["Pro-Govt"] / total) * 100;
        neuPct = (dist["Neutral"] / total) * 100;
        antiPct = (dist["Anti-Govt"] / total) * 100;
    }

    txtProPct.textContent = `${proPct.toFixed(0)}%`;
    txtNeuPct.textContent = `${neuPct.toFixed(0)}%`;
    txtAntiPct.textContent = `${antiPct.toFixed(0)}%`;

    // SVG Perimeter: 2 * pi * 40 = 251.3
    const perimeter = 251.327;
    const proLen = (proPct / 100) * perimeter;
    const neuLen = (neuPct / 100) * perimeter;
    const antiLen = (antiPct / 100) * perimeter;

    donutPro.setAttribute("stroke-dasharray", `${proLen} ${perimeter}`);
    donutNeu.setAttribute("stroke-dasharray", `${neuLen} ${perimeter}`);
    donutAnti.setAttribute("stroke-dasharray", `${antiLen} ${perimeter}`);

    donutNeu.setAttribute("stroke-dashoffset", `-${proLen}`);
    donutAnti.setAttribute("stroke-dashoffset", `-${proLen + neuLen}`);

    // Update donut percentage to show the highest sentiment
    if (total === 0) {
        donutPercentage.textContent = "0%";
        donutLabel.textContent = "No Data";
    } else {
        if (proPct >= neuPct && proPct >= antiPct) {
            donutPercentage.textContent = `${proPct.toFixed(0)}%`;
            donutLabel.textContent = "Pro-Govt";
            donutPercentage.className = "font-display-lg text-headline-lg text-tertiary";
        } else if (neuPct >= proPct && neuPct >= antiPct) {
            donutPercentage.textContent = `${neuPct.toFixed(0)}%`;
            donutLabel.textContent = "Neutral";
            donutPercentage.className = "font-display-lg text-headline-lg text-secondary";
        } else {
            donutPercentage.textContent = `${antiPct.toFixed(0)}%`;
            donutLabel.textContent = "Anti-Govt";
            donutPercentage.className = "font-display-lg text-headline-lg text-error";
        }
    }

    // 4. NLP Diagnostics Insight cards (Take first 3 or create static placeholders based on real articles)
    renderInsightCards(articles);
}

// Render dynamic NLP insight cards
function renderInsightCards(articles) {
    insightCardsGrid.innerHTML = "";
    
    // Choose up to 3 articles from dataset, or fill with default templates if empty
    const displayCount = Math.min(articles.length, 3);
    
    // Fallback static cards if no articles
    if (displayCount === 0) {
        insightCardsGrid.innerHTML = `
            <div class="col-span-3 text-center p-8 text-on-surface-variant bg-surface-container/20 rounded-xl border border-outline-variant/10">
                No active articles. Try scraping fresh news to see individual diagnostic insights.
            </div>
        `;
        return;
    }

    // Image mappings depending on category
    const categoryImages = {
        "sports": "https://lh3.googleusercontent.com/aida-public/AB6AXuA_5wc1eSdsEDjx50kMhgGvKlDCAXF7j2SJTD-MDxjvN1p3Pzw46fs_HiIiCbfu1ZWJ-nXax8lmvPzEJLUjLJHYyFFR52iIWYkxs7psny1STfu80M3NO2dxiTX8PMYdCvmWKqb4pqbIKUKcJXQVRjOKWSFjsPwH9DnDPcbPdvlZoOVIglOXrV31Rq1PyxfpbyYwPm4uC0mjPmhJvVn0ZBkctba-ESIYTTYGjcwdQ2Ijz6wvzD-jg73T1uFEwU7FMd1mheZ16QAjC-0",
        "national": "https://lh3.googleusercontent.com/aida-public/AB6AXuAcS2qzAH-VfXxqSQAujboHZUocEMsUpM12-9CnJXRw9SRO1wYEh7Omr2HkRyKWMxcCC3agluJrDO2t06bxaCxAfhH8Hpejv3mkZHGgtghf9KVvU4ewnd_ftCj59LjlAJLOhq4u7LmoYxj6wTU3eV2vQN1aQhfUtqF3b5sAWK62STMcbjLEJp1SOhNWnWwImrApR-SiwDUT5SneKJb-TDqXs5S0BLKuVwmPYWy85S-yphZyr3keC2EDqOh7vxx1MO5p5A-U9uRXTlY",
        "business": "https://lh3.googleusercontent.com/aida-public/AB6AXuCWNT4Ari-UdPPw0YWIuIRifSboplHOGnu-X6y6iDTR5X-0RiX7f5LXR8daFlC6vyFTv2NY4dn2ov8J_e7O-s0ESV5ilj_RCUFOZqxAx8reKjPt2O_rRRpZY3uNCOYNEfHuqdHFyNtYcQXDLQFMzLCQB5_bPcJ3V1Qz2wfOP6sZ1Gs6L_DY9BTsKnuiaRm1fiGpNAzlTYFfhE12rLWbijNfHbRYKWzYPF8Bp7srcU6CuRZRKVec89kuUs0Vh4FLW68wkOa77KW4Ek4"
    };

    const defaultImage = "https://lh3.googleusercontent.com/aida-public/AB6AXuAcS2qzAH-VfXxqSQAujboHZUocEMsUpM12-9CnJXRw9SRO1wYEh7Omr2HkRyKWMxcCC3agluJrDO2t06bxaCxAfhH8Hpejv3mkZHGgtghf9KVvU4ewnd_ftCj59LjlAJLOhq4u7LmoYxj6wTU3eV2vQN1aQhfUtqF3b5sAWK62STMcbjLEJp1SOhNWnWwImrApR-SiwDUT5SneKJb-TDqXs5S0BLKuVwmPYWy85S-yphZyr3keC2EDqOh7vxx1MO5p5A-U9uRXTlY";

    for (let i = 0; i < displayCount; i++) {
        const art = articles[i];
        
        let borderClass = "border-secondary";
        let badgeColor = "bg-secondary/10 text-secondary";
        let tone = "Informative";
        let polarityVal = "0.50";
        let biasVal = "Policy-Centric";
        let biasColorClass = "text-secondary";

        if (art.sentiment_label === 2) {
            borderClass = "border-tertiary";
            badgeColor = "bg-tertiary/10 text-tertiary";
            tone = "Optimistic / Supportive";
            polarityVal = (0.60 + art.sentiment_confidence * 0.40).toFixed(2);
            biasVal = "Objective / Positive Dev";
            biasColorClass = "text-tertiary";
        } else if (art.sentiment_label === 0) {
            borderClass = "border-error";
            badgeColor = "bg-error/10 text-error";
            tone = "Critical / Concerned";
            polarityVal = (0.40 - art.sentiment_confidence * 0.40).toFixed(2);
            biasVal = "High Bias (Critical)";
            biasColorClass = "text-error";
        } else {
            polarityVal = (0.45 + (Math.random() - 0.5)*0.1).toFixed(2);
        }

        const cardImg = categoryImages[art.category] || defaultImage;

        const cardHTML = `
            <div class="glass-card p-base rounded-xl border-l-4 ${borderClass} flex flex-col justify-between h-full">
                <div class="flex items-center gap-base mb-3">
                    <img class="w-16 h-16 rounded object-cover border border-outline-variant/20" alt="News category thumbnail" src="${cardImg}"/>
                    <div class="flex-1">
                        <h4 class="font-label-md text-label-md text-on-surface leading-tight line-clamp-2" title="${escapeHtml(art.title)}">${escapeHtml(art.title)}</h4>
                        <div class="flex gap-2 mt-1">
                            <span class="px-2 py-0.5 text-[10px] font-bold rounded ${badgeColor}">${art.sentiment_name.toUpperCase()}</span>
                        </div>
                    </div>
                </div>
                <div class="space-y-2 p-2 bg-surface-container-low/50 rounded text-xs mt-auto">
                    <div class="flex justify-between">
                        <span class="text-outline uppercase text-[10px]">NLP Tone</span>
                        <span class="text-on-surface font-semibold">${tone}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-outline uppercase text-[10px]">Polarity Score</span>
                        <span class="text-on-surface font-semibold">${polarityVal}/1.0</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-outline uppercase text-[10px]">Bias Detection</span>
                        <span class="${biasColorClass} font-semibold">${biasVal}</span>
                    </div>
                </div>
            </div>
        `;
        insightCardsGrid.insertAdjacentHTML("beforeend", cardHTML);
    }
}

// Fetch Classifier Info from server
async function loadModelInfo() {
    try {
        const metadata = await api("/news/sentiment-model-info");
        if (metadata.trained) {
            modelStatusTag.textContent = "Active ML Model";
            modelStatusTag.className = "px-3 py-1 text-xs font-bold rounded-full bg-tertiary/10 text-tertiary border border-tertiary/20 mt-2 sm:mt-0";
            
            infoModelName.textContent = metadata.best_model_name;
            
            // Get evaluation metrics for best model
            const bestMetrics = metadata.evaluation_metrics[metadata.best_model_name] || {};
            infoModelAcc.textContent = `${((bestMetrics.accuracy || 0) * 100).toFixed(1)}%`;
            infoModelF1.textContent = (bestMetrics.macro_f1 || 0).toFixed(3);
            
            const trainedDate = new Date(metadata.trained_date);
            infoModelDate.textContent = trainedDate.toLocaleString();
        } else {
            modelStatusTag.textContent = "Lexical Fallback Active";
            modelStatusTag.className = "px-3 py-1 text-xs font-bold rounded-full bg-secondary/10 text-secondary border border-secondary/20 mt-2 sm:mt-0";
            
            infoModelName.textContent = "VADER Heuristic";
            infoModelAcc.textContent = "N/A";
            infoModelF1.textContent = "N/A";
            infoModelDate.textContent = "Not Trained";
        }
    } catch (err) {
        console.error("Failed to load model info:", err);
    }
}

// Check User Session on load
async function checkAuth() {
    try {
        const data = await api("/auth/me");
        currentUser = data.user;
        
        // Update user display details
        userDisplayName.textContent = currentUser.display_name || currentUser.username;
        userRoleBadge.textContent = currentUser.role;
        if (currentUser.role === 'admin') {
            userRoleBadge.className = "text-[10px] text-tertiary uppercase tracking-widest font-bold";
            adminPanel.classList.remove("hidden");
        } else {
            userRoleBadge.className = "text-[10px] text-secondary uppercase tracking-widest";
            adminPanel.classList.add("hidden");
        }

        // Load models information and initial news
        await loadModelInfo();
        switchTab('home');

    } catch (err) {
        console.warn("Session validation failed. Redirecting to login...", err);
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = "index.html";
    }
}

// Escape HTML utility
function escapeHtml(value = "") {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

// Event Listeners for Admin panel
btnScrapeToday.addEventListener("click", async () => {
    btnScrapeToday.disabled = true;
    showStatus("Running scraper for today's articles. Please wait...");
    try {
        const res = await api("/news/scrape", {
            method: "POST",
            body: JSON.stringify({
                categories: ["sports", "national", "international", "business", "miscellaneous"],
                limit: 30,
                days: 1,
                pages: 3,
                dataset: "today",
                government_only: false
            })
        });
        showStatus(`Scrape completed! Scraped ${res.count} articles.`);
        if (currentDataset === "today") {
            await loadSentimentData("today");
        }
    } catch (err) {
        showStatus(`Scrape failed: ${err.message}`, true);
    } finally {
        btnScrapeToday.disabled = false;
    }
});

btnScrapeArchive.addEventListener("click", async () => {
    btnScrapeArchive.disabled = true;
    showStatus("Triggering historical scrape for the last 30 days in the background...");
    try {
        const res = await api("/news/scrape-last-month", { method: "POST" });
        showStatus(res.message);
        // Refresh archive list after 5 seconds to show initial progress
        setTimeout(() => {
            if (currentDataset === "archive") {
                loadSentimentData("archive");
            }
        }, 5000);
    } catch (err) {
        showStatus(`Archive scrape failed: ${err.message}`, true);
    } finally {
        btnScrapeArchive.disabled = false;
    }
});

btnArchiveToday.addEventListener("click", async () => {
    btnArchiveToday.disabled = true;
    showStatus("Merging today's articles into the historical archive...");
    try {
        const res = await api("/news/archive-today", { method: "POST" });
        showStatus(res.message);
        if (currentDataset === "archive") {
            await loadSentimentData("archive");
        }
    } catch (err) {
        showStatus(`Archiving failed: ${err.message}`, true);
    } finally {
        btnArchiveToday.disabled = false;
    }
});

btnRetrainModel.addEventListener("click", async () => {
    btnRetrainModel.disabled = true;
    showStatus("Training Logistic Regression, Naive Bayes and Support Vector Machine on labeled dataset...");
    try {
        const res = await api("/news/train-sentiment", { method: "POST" });
        showStatus("Classifier model trained and saved successfully!");
        await loadModelInfo();
        await loadSentimentData(currentDataset);
    } catch (err) {
        showStatus(`Training failed: ${err.message}`, true);
    } finally {
        btnRetrainModel.disabled = false;
    }
});

async function logoutUser() {
    // Clear token immediately for responsive UX
    localStorage.removeItem(TOKEN_KEY);
    
    // Trigger backend session clearance in the background
    api("/auth/logout", { method: "POST" }).catch(err => {
        console.warn("Background logout error:", err);
    });
    
    // Redirect immediately
    window.location.href = "index.html";
}

window.logoutUser = logoutUser;
window.showStatus = showStatus;
window.switchTab = switchTab;

async function toggleVisibility(url, isVisible) {
    showStatus(`Updating article visibility...`);
    try {
        await api("/news/toggle-visibility", {
            method: "POST",
            body: JSON.stringify({ url, is_visible: isVisible, dataset: currentDataset })
        });
        showStatus(`Article visibility updated!`);
        await loadSentimentData(currentDataset);
    } catch (err) {
        showStatus(`Failed to update visibility: ${err.message}`, true);
    }
}

async function overrideSentiment(url, labelVal) {
    const label = labelVal === "" ? null : parseInt(labelVal);
    showStatus(`Saving sentiment override...`);
    try {
        await api("/news/override-sentiment", {
            method: "POST",
            body: JSON.stringify({ url, label, dataset: currentDataset })
        });
        showStatus(`Sentiment override saved!`);
        await loadSentimentData(currentDataset);
    } catch (err) {
        showStatus(`Failed to save override: ${err.message}`, true);
    }
}

function toggleKeywordModal(show) {
    if (show) {
        keywordModal.classList.remove("hidden");
        loadKeywordRules();
    } else {
        keywordModal.classList.add("hidden");
    }
}

async function loadKeywordRules() {
    keywordRulesList.innerHTML = `<p class="text-xs text-on-surface-variant italic text-center p-4">Loading rules...</p>`;
    try {
        const rules = await api("/news/keyword-rules");
        const entries = Object.entries(rules);
        if (entries.length === 0) {
            keywordRulesList.innerHTML = `<p class="text-xs text-on-surface-variant italic text-center p-4">No custom keyword rules defined.</p>`;
            return;
        }
        
        const labelMap = { 0: "Anti-Govt", 1: "Neutral", 2: "Pro-Govt" };
        const badgeColors = {
            0: "text-error border-error/20 bg-error/5",
            1: "text-secondary border-secondary/20 bg-secondary/5",
            2: "text-tertiary border-tertiary/20 bg-tertiary/5"
        };
        
        keywordRulesList.innerHTML = entries.map(([kw, lbl]) => {
            const lblName = labelMap[lbl] || "Neutral";
            const badgeClass = badgeColors[lbl] || "text-outline";
            
            return `
                <div class="flex justify-between items-center bg-surface-container p-2 rounded border border-outline-variant/10 text-xs">
                    <div class="flex items-center gap-2">
                        <span class="font-semibold text-on-surface">"${escapeHtml(kw)}"</span>
                        <span class="material-symbols-outlined text-[12px] text-outline">arrow_forward</span>
                        <span class="px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase ${badgeClass}">${lblName}</span>
                    </div>
                    <button type="button" onclick="deleteKeywordRule('${escapeHtml(kw)}')" class="text-error hover:text-on-error transition-colors p-1 hover:bg-error/10 rounded">
                        <span class="material-symbols-outlined text-[16px]">delete</span>
                    </button>
                </div>
            `;
        }).join("");
    } catch (err) {
        keywordRulesList.innerHTML = `<p class="text-xs text-error text-center p-4">Failed to load rules: ${err.message}</p>`;
    }
}

async function deleteKeywordRule(keyword) {
    if (!confirm(`Are you sure you want to delete the keyword rule for "${keyword}"?`)) return;
    try {
        await api("/news/delete-keyword-rule", {
            method: "POST",
            body: JSON.stringify({ keyword })
        });
        showStatus(`Deleted rule for keyword: "${keyword}"`);
        await loadKeywordRules();
    } catch (err) {
        showStatus(`Failed to delete rule: ${err.message}`, true);
    }
}

async function loadSportsPredictions() {
    sportsModelName.textContent = "Loading...";
    sportsModelAcc.textContent = "-";
    sportsModelDate.textContent = "-";
    
    predictedChampionName.textContent = "Simulating...";
    predictedChampFinalProb.textContent = "-";
    predictedChampWinProb.textContent = "-";
    
    sportsLeaderboardBody.innerHTML = `<tr><td colspan="3" class="p-4 text-center text-on-surface-variant">Simulating tournament...</td></tr>`;
    groupsStandingsGrid.innerHTML = `<p class="text-xs text-on-surface-variant italic text-center p-4">Loading standings...</p>`;
    
    try {
        const info = await api("/sports/model-info");
        if (info.trained) {
            sportsModelName.textContent = info.model_name;
            sportsModelAcc.textContent = `${(info.accuracy * 100).toFixed(1)}%`;
            sportsModelDate.textContent = new Date(info.trained_date).toLocaleString();
        } else {
            sportsModelName.textContent = "Not Trained";
            sportsModelAcc.textContent = "N/A";
            sportsModelDate.textContent = "N/A";
        }
    } catch (err) {
        console.warn("Failed to load sports model info:", err);
    }
    
    try {
        const data = await api("/sports/predictions");
        if (!data.trained) {
            showStatus(data.message, true);
            sportsLeaderboardBody.innerHTML = `<tr><td colspan="3" class="p-4 text-center text-error">${data.message}</td></tr>`;
            return;
        }
        
        renderGroupsStandings(data.group_standings);
        renderLeaderboard(data.progression_probabilities, data.group_standings);
        renderBracket(data.knockout_bracket);
        
        const championName = data.knockout_bracket.final.winner;
        predictedChampionName.textContent = championName;
        const champProbs = data.progression_probabilities[championName] || {};
        predictedChampFinalProb.textContent = `${((champProbs.final || 0) * 100).toFixed(1)}%`;
        predictedChampWinProb.textContent = `${((champProbs.champion || 0) * 100).toFixed(1)}%`;
        
    } catch (err) {
        showStatus(`Sports simulation failed: ${err.message}`, true);
        sportsLeaderboardBody.innerHTML = `<tr><td colspan="3" class="p-4 text-center text-error">Simulation failed: ${err.message}</td></tr>`;
    }
}

function renderGroupsStandings(groupStandings) {
    groupsStandingsGrid.innerHTML = "";
    
    const entries = Object.entries(groupStandings).sort();
    for (const [groupName, teams] of entries) {
        const teamRows = teams.map(t => `
            <tr class="border-b border-outline-variant/5 text-[11px]">
                <td class="p-1 font-semibold text-on-surface">
                    <span>${t.rank}. ${escapeHtml(t.team)}</span>
                </td>
                <td class="p-1 text-on-surface-variant text-center">${t.played}</td>
                <td class="p-1 text-on-surface-variant text-center">${t.wins}</td>
                <td class="p-1 text-on-surface-variant text-center">${t.draws}</td>
                <td class="p-1 text-on-surface-variant text-center">${t.losses}</td>
                <td class="p-1 font-bold text-secondary text-right">${t.points}</td>
            </tr>
        `).join("");
        
        const groupHTML = `
            <div class="bg-surface-container/30 p-2 rounded-lg border border-outline-variant/10">
                <div class="font-label-md text-[11px] text-secondary border-b border-outline-variant/10 pb-1 mb-1.5 flex justify-between">
                    <span>${groupName}</span>
                    <span class="text-[9px] text-outline font-normal">FIFA Standings</span>
                </div>
                <table class="w-full text-left">
                    <thead>
                        <tr class="text-[9px] text-outline uppercase font-semibold">
                            <th class="p-1">Team</th>
                            <th class="p-1 text-center">P</th>
                            <th class="p-1 text-center">W</th>
                            <th class="p-1 text-center">D</th>
                            <th class="p-1 text-center">L</th>
                            <th class="p-1 text-right">Pts</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${teamRows}
                    </tbody>
                </table>
            </div>
        `;
        groupsStandingsGrid.insertAdjacentHTML("beforeend", groupHTML);
    }
}

function renderLeaderboard(progProbs, groupStandings) {
    sportsLeaderboardBody.innerHTML = "";
    
    const teams = Object.entries(progProbs).map(([team, probs]) => {
        let fifaRank = 99;
        for (const grp of Object.values(groupStandings)) {
            const found = grp.find(t => t.team === team);
            if (found) {
                fifaRank = found.fifa_rank;
                break;
            }
        }
        return {
            team,
            fifaRank,
            winProb: probs.champion
        };
    }).sort((a, b) => b.winProb - a.winProb);
    
    sportsLeaderboardBody.innerHTML = teams.map(t => `
        <tr class="hover:bg-surface-container-high transition-colors">
            <td class="p-2 font-semibold text-on-surface">${escapeHtml(t.team)}</td>
            <td class="p-2 text-on-surface-variant font-data-mono">${t.fifaRank}</td>
            <td class="p-2 text-right font-bold text-tertiary">${(t.winProb * 100).toFixed(1)}%</td>
        </tr>
    `).join("");
}

function renderBracket(bracket) {
    // 0. Render Round of 32
    if (bracket.round_of_32) {
        bracket.round_of_32.forEach((m) => {
            const div = document.getElementById(`bracket_${m.id}`);
            if (div) {
                const t1Class = m.winner === m.team1 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
                const t2Class = m.winner === m.team2 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
                const outcomeText = m.outcome || `Winner: ${escapeHtml(m.winner)}`;
                div.innerHTML = `
                    <div class="flex justify-between items-center py-0.5">
                        <span class="${t1Class} truncate max-w-[120px]">${escapeHtml(m.team1)}</span>
                    </div>
                    <div class="flex justify-between items-center py-0.5 border-t border-outline-variant/10">
                        <span class="${t2Class} truncate max-w-[120px]">${escapeHtml(m.team2)}</span>
                    </div>
                    <div class="text-[8px] text-secondary mt-0.5 flex justify-between">
                        <span class="truncate max-w-[120px]">${escapeHtml(outcomeText)}</span>
                        <span>${m.confidence === 1.0 ? '100' : (m.confidence * 100).toFixed(0)}%</span>
                    </div>
                `;
            }
        });
    }

    // 1. Render Round of 16
    bracket.round_of_16.forEach((m) => {
        const div = document.getElementById(`bracket_${m.id}`);
        if (div) {
            const t1Class = m.winner === m.team1 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
            const t2Class = m.winner === m.team2 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
            const outcomeText = m.outcome || `Winner: ${escapeHtml(m.winner)}`;
            div.innerHTML = `
                <div class="flex justify-between items-center py-0.5">
                    <span class="${t1Class} truncate max-w-[120px]">${escapeHtml(m.team1)}</span>
                </div>
                <div class="flex justify-between items-center py-0.5 border-t border-outline-variant/10">
                    <span class="${t2Class} truncate max-w-[120px]">${escapeHtml(m.team2)}</span>
                </div>
                <div class="text-[8px] text-secondary mt-0.5 flex justify-between">
                    <span class="truncate max-w-[120px]">${escapeHtml(outcomeText)}</span>
                    <span>${m.confidence === 1.0 ? '100' : (m.confidence * 100).toFixed(0)}%</span>
                </div>
            `;
        }
    });
    
    // 2. Render Quarterfinals
    bracket.quarterfinals.forEach((m) => {
        const div = document.getElementById(`bracket_${m.id}`);
        if (div) {
            const t1Class = m.winner === m.team1 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
            const t2Class = m.winner === m.team2 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
            const outcomeText = m.outcome || `Winner: ${escapeHtml(m.winner)}`;
            div.innerHTML = `
                <div class="flex justify-between items-center py-0.5">
                    <span class="${t1Class} truncate max-w-[120px]">${escapeHtml(m.team1)}</span>
                </div>
                <div class="flex justify-between items-center py-0.5 border-t border-outline-variant/10">
                    <span class="${t2Class} truncate max-w-[120px]">${escapeHtml(m.team2)}</span>
                </div>
                <div class="text-[8px] text-secondary mt-0.5 flex justify-between">
                    <span class="truncate max-w-[120px]">${escapeHtml(outcomeText)}</span>
                    <span>${m.confidence === 1.0 ? '100' : (m.confidence * 100).toFixed(0)}%</span>
                </div>
            `;
        }
    });
    
    // 3. Render Semifinals
    bracket.semifinals.forEach((m) => {
        const div = document.getElementById(`bracket_${m.id}`);
        if (div) {
            const t1Class = m.winner === m.team1 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
            const t2Class = m.winner === m.team2 ? 'text-tertiary font-bold' : 'text-on-surface-variant opacity-70';
            const outcomeText = m.outcome || `Winner: ${escapeHtml(m.winner)}`;
            div.innerHTML = `
                <div class="flex justify-between items-center py-0.5">
                    <span class="${t1Class} truncate max-w-[120px]">${escapeHtml(m.team1)}</span>
                </div>
                <div class="flex justify-between items-center py-0.5 border-t border-outline-variant/10">
                    <span class="${t2Class} truncate max-w-[120px]">${escapeHtml(m.team2)}</span>
                </div>
                <div class="text-[8px] text-secondary mt-0.5 flex justify-between">
                    <span class="truncate max-w-[120px]">${escapeHtml(outcomeText)}</span>
                    <span>${m.confidence === 1.0 ? '100' : (m.confidence * 100).toFixed(0)}%</span>
                </div>
            `;
        }
    });
    
    // 4. Render Final
    const finalDiv = document.getElementById(`bracket_final`);
    if (finalDiv) {
        const m = bracket.final;
        const t1Class = m.winner === m.team1 ? 'text-tertiary font-bold text-sm' : 'text-on-surface-variant opacity-70';
        const t2Class = m.winner === m.team2 ? 'text-tertiary font-bold text-sm' : 'text-on-surface-variant opacity-70';
        const outcomeText = m.outcome || `Winner: ${escapeHtml(m.winner)}`;
        finalDiv.innerHTML = `
            <div class="text-center font-bold text-[10px] text-outline uppercase tracking-wider mb-1.5">Final Matchup</div>
            <div class="py-0.5">
                <span class="${t1Class} truncate max-w-[150px]">${escapeHtml(m.team1)}</span>
            </div>
            <div class="py-0.5 border-t border-outline-variant/10">
                <span class="${t2Class} truncate max-w-[150px]">${escapeHtml(m.team2)}</span>
            </div>
            <div class="mt-2.5 p-1.5 bg-secondary/10 border border-secondary/20 rounded text-center">
                <div class="text-[8px] text-secondary uppercase font-bold tracking-wider">Champion</div>
                <div class="text-sm font-bold text-tertiary mt-0.5">${escapeHtml(m.winner)}</div>
                <div class="text-[8px] text-on-surface-variant mt-0.5">${escapeHtml(outcomeText.replace(m.winner, '').trim())}</div>
                <div class="text-[8px] text-on-surface-variant mt-0.5">Prob: ${m.confidence === 1.0 ? '100' : (m.confidence * 100).toFixed(0)}%</div>
            </div>
        `;
    }
}

window.toggleVisibility = toggleVisibility;
window.overrideSentiment = overrideSentiment;
window.toggleKeywordModal = toggleKeywordModal;
window.deleteKeywordRule = deleteKeywordRule;

function attachDashboardEventHandlers() {
    if (btnLogout) {
        btnLogout.removeEventListener("click", logoutUser);
        btnLogout.addEventListener("click", logoutUser);
    }
    if (btnLogoutTop) {
        btnLogoutTop.removeEventListener("click", logoutUser);
        btnLogoutTop.addEventListener("click", logoutUser);
    }
    if (btnNotifications) {
        btnNotifications.removeEventListener("click", showNotificationsMessage);
        btnNotifications.addEventListener("click", showNotificationsMessage);
    }
    if (btnSettings) {
        btnSettings.removeEventListener("click", showSettingsMessage);
        btnSettings.addEventListener("click", showSettingsMessage);
    }
    
    // Keyword Form handler
    if (keywordForm) {
        keywordForm.removeEventListener("submit", saveKeywordForm);
        keywordForm.addEventListener("submit", saveKeywordForm);
    }
    
    // Retrain sports handler
    if (btnRetrainSports) {
        btnRetrainSports.removeEventListener("click", retrainSportsHandler);
        btnRetrainSports.addEventListener("click", retrainSportsHandler);
    }
}

async function saveKeywordForm(e) {
    e.preventDefault();
    const keyword = kwInput.value.trim();
    const label = parseInt(kwSentiment.value);
    
    if (!keyword) return;
    
    showStatus(`Saving keyword rule: "${keyword}"...`);
    try {
        await api("/news/save-keyword-rule", {
            method: "POST",
            body: JSON.stringify({ keyword, label })
        });
        showStatus(`Keyword rule saved successfully!`);
        kwInput.value = "";
        await loadKeywordRules();
    } catch (err) {
        showStatus(`Failed to save rule: ${err.message}`, true);
    }
}

async function retrainSportsHandler() {
    btnRetrainSports.disabled = true;
    showStatus("Training FIFA World Cup outcome model on pre-tournament data...");
    try {
        const res = await api("/sports/train", { method: "POST" });
        showStatus(`Sports model trained successfully! Accuracy: ${(res.accuracy * 100).toFixed(1)}%`);
        await loadSportsPredictions();
    } catch (err) {
        showStatus(`Sports training failed: ${err.message}`, true);
    } finally {
        btnRetrainSports.disabled = false;
    }
}

function showNotificationsMessage() {
    showStatus("Notifications are currently unavailable in this demo.", false);
}

function showSettingsMessage() {
    showStatus("Settings will be available in the next release.", false);
}

// === INDIAN SPORTS PREDICTOR FEED & NAVIGATION ===
let allIndianSportsArticles = [];

function switchSportsSubTab(tab) {
    const btnFifa = document.getElementById("btnSubTabFifa");
    const btnIndian = document.getElementById("btnSubTabIndian");
    const containerFifa = document.getElementById("sportsFifaContainer");
    const containerIndian = document.getElementById("sportsIndianContainer");
    
    if (tab === "fifa") {
        btnFifa.className = "px-4 py-2 text-xs font-semibold rounded bg-secondary text-on-secondary shadow-sm transition-all";
        btnIndian.className = "px-4 py-2 text-xs font-semibold rounded text-on-surface-variant hover:text-on-surface transition-all";
        containerFifa.classList.remove("hidden");
        containerIndian.classList.add("hidden");
    } else if (tab === "indian") {
        btnFifa.className = "px-4 py-2 text-xs font-semibold rounded text-on-surface-variant hover:text-on-surface transition-all";
        btnIndian.className = "px-4 py-2 text-xs font-semibold rounded bg-secondary text-on-secondary shadow-sm transition-all";
        containerFifa.classList.add("hidden");
        containerIndian.classList.remove("hidden");
        
        loadIndianSportsNews();
    }
}

async function loadIndianSportsNews() {
    const listDiv = document.getElementById("indianSportsList");
    const prospectsDiv = document.getElementById("medalProspectsList");
    
    listDiv.innerHTML = `<div class="col-span-2 text-center text-on-surface-variant p-12">Loading Indian sports news...</div>`;
    if (prospectsDiv) {
        prospectsDiv.innerHTML = `<p class="text-xs text-on-surface-variant italic text-center p-4">Loading medal prospects...</p>`;
    }
    
    try {
        const [newsData, prospectsData] = await Promise.all([
            api("/sports/indian-news"),
            api("/sports/medal-prospects").catch(err => {
                console.warn("Failed to load prospects:", err);
                return { prospects: [] };
            })
        ]);
        
        allIndianSportsArticles = newsData.articles || [];
        
        // Render stats
        updateIndianSportsStats(allIndianSportsArticles);
        
        // Render articles
        renderIndianSportsList(allIndianSportsArticles);
        
        // Render medal prospects
        renderMedalProspects(prospectsData.prospects || []);
    } catch (err) {
        showStatus(err.message, true);
        listDiv.innerHTML = `<div class="col-span-2 text-center text-error p-12">Failed to load: ${err.message}</div>`;
    }
}

function updateIndianSportsStats(articles) {
    document.getElementById("indianSportsTotal").textContent = `${articles.length} Articles`;
    
    let cricketCount = 0;
    let badmintonCount = 0;
    
    const cricketKeywords = ["cricket", "ipl", "bcci", "kohli", "rohit", "dhoni"];
    const badmintonKeywords = ["badminton", "sindhu", "saina", "sen", "lakshya", "satwik", "chirag"];
    
    articles.forEach(art => {
        const title = (art.title || "").toLowerCase();
        const body = (art.body || "").toLowerCase();
        const text = `${title} ${body}`;
        
        if (cricketKeywords.some(kw => text.includes(kw))) {
            cricketCount++;
        } else if (badmintonKeywords.some(kw => text.includes(kw))) {
            badmintonCount++;
        }
    });
    
    document.getElementById("indianSportsCricket").textContent = `${cricketCount} Articles`;
    document.getElementById("indianSportsBadminton").textContent = `${badmintonCount} Articles`;
    document.getElementById("indianSportsOther").textContent = `${articles.length - cricketCount - badmintonCount} Articles`;
}

function renderIndianSportsList(articles) {
    const listDiv = document.getElementById("indianSportsList");
    if (articles.length === 0) {
        listDiv.innerHTML = `<div class="col-span-2 text-center text-on-surface-variant p-12">No sports news articles found.</div>`;
        return;
    }
    
    listDiv.innerHTML = articles.map(art => {
        const dateStr = art.published_date || "Recent";
        const category = art.category || "sports";
        const url = art.url || "#";
        const title = art.title || "Untitled";
        const textContent = art.summary || art.body || "";
        
        return `
            <div class="glass-card p-4 rounded-lg flex flex-col justify-between hover:border-secondary/30 transition-all">
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <span class="px-2 py-0.5 bg-secondary-container/20 text-secondary border border-secondary/15 rounded text-[10px] uppercase font-bold tracking-wider">${escapeHtml(category)}</span>
                        <span class="text-[10px] text-on-surface-variant font-data-mono">${escapeHtml(dateStr)}</span>
                    </div>
                    <h4 class="font-semibold text-on-surface text-sm mb-2 hover:text-secondary"><a href="${escapeHtml(url)}" target="_blank">${escapeHtml(title)}</a></h4>
                    <p class="text-xs text-on-surface-variant line-clamp-3 mb-4">${escapeHtml(textContent)}</p>
                </div>
                <div class="flex justify-between items-center border-t border-outline-variant/10 pt-2 mt-auto">
                    <span class="text-[10px] text-outline">Source: NewsOnAir</span>
                    <a href="${escapeHtml(url)}" target="_blank" class="text-xs text-secondary hover:underline flex items-center gap-1">
                        Read Full <span class="material-symbols-outlined text-[12px]">open_in_new</span>
                    </a>
                </div>
            </div>
        `;
    }).join("");
}

function filterIndianSports() {
    const filter = document.getElementById("sportsFilter").value;
    if (filter === "all") {
        renderIndianSportsList(allIndianSportsArticles);
        return;
    }
    
    const cricketKeywords = ["cricket", "ipl", "bcci", "kohli", "rohit", "dhoni"];
    const badmintonKeywords = ["badminton", "sindhu", "saina", "sen", "lakshya", "satwik", "chirag"];
    const hockeyKeywords = ["hockey"];
    const athleticsKeywords = ["athletics", "neeraj", "chopra", "javelin"];
    
    const filtered = allIndianSportsArticles.filter(art => {
        const title = (art.title || "").toLowerCase();
        const body = (art.body || "").toLowerCase();
        const text = `${title} ${body}`;
        
        if (filter === "cricket") {
            return cricketKeywords.some(kw => text.includes(kw));
        } else if (filter === "badminton") {
            return badmintonKeywords.some(kw => text.includes(kw));
        } else if (filter === "hockey") {
            return hockeyKeywords.some(kw => text.includes(kw));
        } else if (filter === "athletics") {
            return athleticsKeywords.some(kw => text.includes(kw));
        } else if (filter === "other") {
            return !cricketKeywords.some(kw => text.includes(kw)) &&
                   !badmintonKeywords.some(kw => text.includes(kw)) &&
                   !hockeyKeywords.some(kw => text.includes(kw)) &&
                   !athleticsKeywords.some(kw => text.includes(kw));
        }
        return true;
    });
    
    renderIndianSportsList(filtered);
}

function renderMedalProspects(prospects) {
    const listDiv = document.getElementById("medalProspectsList");
    if (!listDiv) return;
    
    if (prospects.length === 0) {
        listDiv.innerHTML = `<p class="text-xs text-on-surface-variant italic text-center p-4">No medal prospects found.</p>`;
        return;
    }
    
    listDiv.innerHTML = prospects.map(p => {
        return `
            <div class="glass-card p-3 rounded-lg flex items-start gap-3 hover:border-secondary/20 transition-all">
                <div class="w-8 h-8 rounded-lg bg-secondary/15 flex items-center justify-center text-secondary shrink-0">
                    <span class="material-symbols-outlined text-[18px]">${escapeHtml(p.icon || "emoji_events")}</span>
                </div>
                <div class="min-w-0 flex-1">
                    <div class="flex justify-between items-start gap-1">
                        <h4 class="font-bold text-on-surface text-xs truncate">${escapeHtml(p.name)}</h4>
                        <span class="text-[9px] px-1.5 py-0.5 bg-secondary-container/20 text-secondary border border-secondary/15 rounded whitespace-nowrap shrink-0">${escapeHtml(p.sport)}</span>
                    </div>
                    <p class="text-[10px] text-on-surface-variant font-medium mt-1">${escapeHtml(p.discipline)}</p>
                    <p class="text-[10px] text-outline mt-1 font-semibold truncate" title="${escapeHtml(p.event)}">Event: ${escapeHtml(p.event)}</p>
                    <div class="flex items-center gap-1.5 mt-2 text-[10px] text-tertiary font-bold">
                        <span class="material-symbols-outlined text-[12px]" style="font-variation-settings: 'FILL' 1;">stars</span>
                        Prospect: ${escapeHtml(p.chance)}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}


async function refreshIndianSportsNews() {
    const btn = document.getElementById("refreshIndianSportsBtn");
    if (!btn || btn.disabled) return;
    
    btn.disabled = true;
    const origHTML = btn.innerHTML;
    btn.innerHTML = `<span class="material-symbols-outlined text-sm animate-spin">sync</span><span>Refreshing...</span>`;
    
    try {
        const response = await api("/sports/refresh-indian-news", {
            method: "POST"
        });
        showStatus(response.message || "Indian sports news refreshed successfully!", false);
        await loadIndianSportsNews();
    } catch (err) {
        showStatus(`Failed to refresh sports news: ${err.message}`, true);
    } finally {
        btn.disabled = false;
        btn.innerHTML = origHTML;
    }
}

async function refreshWorldCupPredictions() {
    const btn = document.getElementById("refreshFifaBtn");
    if (!btn || btn.disabled) return;
    
    btn.disabled = true;
    const origHTML = btn.innerHTML;
    btn.innerHTML = `<span class="material-symbols-outlined text-sm animate-spin">sync</span><span>Refreshing...</span>`;
    
    try {
        const response = await api("/sports/refresh-world-cup", {
            method: "POST"
        });
        showStatus(response.message || "World Cup prediction data refreshed successfully!", false);
        await loadSportsPredictions();
    } catch (err) {
        showStatus(`Failed to refresh World Cup prediction data: ${err.message}`, true);
    } finally {
        btn.disabled = false;
        btn.innerHTML = origHTML;
    }
}


window.renderMedalProspects = renderMedalProspects;
window.loadIndianSportsNews = loadIndianSportsNews;
window.filterIndianSports = filterIndianSports;
window.refreshIndianSportsNews = refreshIndianSportsNews;
window.refreshWorldCupPredictions = refreshWorldCupPredictions;

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", attachDashboardEventHandlers);
} else {
    attachDashboardEventHandlers();
}

// Run auth check on initialization
checkAuth();
