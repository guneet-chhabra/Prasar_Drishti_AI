const hostName = window.location.hostname || "localhost";
const API_BASE_URL = (hostName === "localhost" || hostName === "127.0.0.1")
  ? `http://${hostName}:5000/api`
  : "https://your-render-app-name.onrender.com/api"; // <-- Replace with your actual Render service URL (must start with https://)

const loginForm = document.querySelector("#loginForm");
const message = document.querySelector("#message");
const dashboard = document.querySelector("#dashboard");
const welcomeText = document.querySelector("#welcomeText");
const roleText = document.querySelector("#roleText");
const adminButton = document.querySelector("#adminButton");
const scrapeButton = document.querySelector("#scrapeButton");
const loadArticlesButton = document.querySelector("#loadArticlesButton");
const loadArchiveButton = document.querySelector("#loadArchiveButton");
const lastMonthButton = document.querySelector("#lastMonthButton");
const archiveTodayButton = document.querySelector("#archiveTodayButton");
const logoutButton = document.querySelector("#logoutButton");
const articlesPanel = document.querySelector("#articlesPanel");
const articlesList = document.querySelector("#articlesList");
const articleCount = document.querySelector("#articleCount");
const TOKEN_KEY = "prasar_drishti_token";

function showMessage(text, isError = true) {
  message.textContent = text;
  message.style.color = isError ? "var(--danger)" : "var(--green)";
}

function showDashboard(user) {
  window.location.href = "dashboard.html";
}

function showLogin() {
  loginForm.classList.remove("hidden");
  dashboard.classList.add("hidden");
  adminButton.classList.add("hidden");
  scrapeButton.classList.add("hidden");
  lastMonthButton.classList.add("hidden");
  archiveTodayButton.classList.add("hidden");
  articlesPanel.classList.add("hidden");
}

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
    message: "Backend returned a non-JSON error. Check the Flask terminal.",
  }));
  if (!response.ok) {
    throw new Error(data.error ? `${data.message}: ${data.error}` : data.message || "Request failed");
  }
  return data;
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);

  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: formData.get("username"),
        password: formData.get("password"),
      }),
    });
    localStorage.setItem(TOKEN_KEY, data.token);
    showDashboard(data.user);
  } catch (error) {
    showMessage(error.message);
  }
});

adminButton.addEventListener("click", async () => {
  try {
    const data = await api("/auth/admin/overview");
    showMessage(data.message, false);
  } catch (error) {
    showMessage(error.message);
  }
});

function renderArticles(articles) {
  articleCount.textContent = `${articles.length} item${articles.length === 1 ? "" : "s"}`;
  articlesPanel.classList.remove("hidden");

  if (!articles.length) {
    articlesList.innerHTML = `<p>No scraped articles found yet. Login as admin and run the scraper.</p>`;
    return;
  }

  articlesList.innerHTML = articles
    .map(
      (article) => `
        <article class="article-card">
          <h4>${escapeHtml(article.title)}</h4>
          <p>${escapeHtml(article.summary)}</p>
          <div class="article-meta">
            <span>${escapeHtml(article.category)}</span>
            <span>${escapeHtml(article.published_at || "date unavailable")}</span>
            <span>${article.word_count || 0} words</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadArticles(dataset = "today") {
  try {
    const data = await api(`/news/articles?dataset=${dataset}&limit=50`);
    renderArticles(data.articles);
    showMessage(data.message || `Loaded ${data.count} ${dataset} articles.`, false);
  } catch (error) {
    showMessage(error.message);
  }
}

loadArticlesButton.addEventListener("click", () => loadArticles("today"));
loadArchiveButton.addEventListener("click", () => loadArticles("archive"));

scrapeButton.addEventListener("click", async () => {
  scrapeButton.disabled = true;
  showMessage("Scraper running. This may take a few seconds...", false);

  try {
    const data = await api("/news/scrape", {
      method: "POST",
      body: JSON.stringify({
        categories: ["sports", "national", "international", "business"],
        limit: 40,
        days: 1,
        pages: 3,
        dataset: "today",
        government_only: false,
      }),
    });
    showMessage(data.message, false);
    const articles = await api("/news/articles?dataset=today&limit=50");
    renderArticles(articles.articles);
  } catch (error) {
    showMessage(error.message);
  } finally {
    scrapeButton.disabled = false;
  }
});

lastMonthButton.addEventListener("click", async () => {
  lastMonthButton.disabled = true;
  showMessage("Scraping last month's news across government, sports, business, and international categories. This may take a while...", false);

  try {
    const data = await api("/news/scrape-last-month", { method: "POST" });
    showMessage(`${data.message}. Added ${data.count} articles.`, false);
    await loadArticles("archive");
  } catch (error) {
    showMessage(error.message);
  } finally {
    lastMonthButton.disabled = false;
  }
});

archiveTodayButton.addEventListener("click", async () => {
  try {
    const data = await api("/news/archive-today", { method: "POST" });
    showMessage(data.message, false);
    await loadArticles("archive");
  } catch (error) {
    showMessage(error.message);
  }
});

logoutButton.addEventListener("click", () => {
  // Clear token and update UI immediately for responsive UX
  localStorage.removeItem(TOKEN_KEY);
  showLogin();
  showMessage("Logged out.", false);
  
  // Trigger backend session clearance in the background
  api("/auth/logout", { method: "POST" }).catch(err => {
    console.warn("Background logout error:", err);
  });
});

api("/auth/me")
  .then((data) => showDashboard(data.user))
  .catch(() => showLogin());
