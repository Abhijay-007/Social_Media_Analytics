/**
 * Social Media Intelligence Observatory - Client Logic
 * Glassmorphic & Minimalist Single Page Application
 */

const PLATFORM_META = {
  all: { name: "Global Observatory", icon: "🌐", tag: "Aggregated Intelligence", desc: "Holistic multi-platform conversational sentiment & thematic resonance." },
  telegram: { name: "Telegram", icon: "✈️", tag: "Broadcasts & Rooms", desc: "Direct channel transmissions, guild room discussions, and peer messages." },
  x: { name: "X (Twitter)", icon: "𝕏", tag: "Real-Time Commentary", desc: "Short-form breaking updates, sports commentary, and trending hashtags." },
  reddit: { name: "Reddit", icon: "🤖", tag: "Thematic Sub-Reddits", desc: "Longform discussions, cinematic debates, and community theories." },
  youtube: { name: "YouTube", icon: "▶️", tag: "Video Discourse", desc: "Audiovisual trailer breakdowns, cinematic critiques, and box office opinions." },
  instagram: { name: "Instagram", icon: "📸", tag: "Aesthetic Showcase", desc: "Lifestyle curation, skincare advice, and visual culture discussions." },
  facebook: { name: "Facebook", icon: "📘", tag: "Community Feeds", desc: "Conversational group posts, advice queries, and community shares." }
};

let rawData = null;
let currentPlatform = "all";
let donutChart = null;
let topicsChart = null;

// Initialize App
document.addEventListener("DOMContentLoaded", async () => {
  await loadData();
  setupEvents();
});

async function loadData() {
  try {
    const res = await fetch("/api/data");
    if (res.ok) {
      rawData = await res.json();
    } else {
      const fallback = await fetch("/data/processed/ui_data.json");
      rawData = await fallback.json();
    }
  } catch (e) {
    console.error("Data load fallback:", e);
  }
}

function setupEvents() {
  // Click on landing platform cards
  document.querySelectorAll(".platform-card").forEach(card => {
    card.addEventListener("click", () => {
      const plat = card.getAttribute("data-platform");
      openPlatform(plat);
    });
  });

  // Back button
  document.getElementById("btn-back").addEventListener("click", () => {
    switchView("view-landing");
  });

  // Quick tab chips
  document.querySelectorAll(".tab-chip").forEach(btn => {
    btn.addEventListener("click", () => {
      const plat = btn.getAttribute("data-plat");
      openPlatform(plat);
    });
  });

  // Content tabs (Feed vs Inspector)
  document.querySelectorAll(".view-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".view-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      const target = tab.getAttribute("data-target");
      document.getElementById(target).classList.add("active");
    });
  });

  // Feed search
  document.getElementById("feed-search").addEventListener("input", (e) => {
    renderFeed(e.target.value);
  });

  // Live Inspector
  document.getElementById("btn-analyze").addEventListener("click", runLiveAnalysis);
}

function switchView(viewId) {
  document.querySelectorAll(".view-section").forEach(s => s.classList.remove("active"));
  document.getElementById(viewId).classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openPlatform(plat) {
  currentPlatform = plat;
  const meta = PLATFORM_META[plat] || PLATFORM_META.all;
  const platData = (rawData && rawData.platforms && rawData.platforms[plat]) || {
    pos_pct: 42.5, neu_pct: 44.0, neg_pct: 13.5,
    positivity_rate: "42.5%", resonance_rate: "86.5%", community_health: "98.2%",
    top_emotion: "Approval", hashtags: [], authors: [], feed: []
  };

  // Update Header
  document.getElementById("detail-icon").textContent = meta.icon;
  document.getElementById("detail-title").textContent = meta.name;
  document.getElementById("detail-tag").textContent = meta.tag;
  document.getElementById("detail-desc").textContent = meta.desc;

  // Update Active Tab Chip
  document.querySelectorAll(".tab-chip").forEach(btn => {
    if (btn.getAttribute("data-plat") === plat) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update Percentage KPIs
  document.getElementById("kpi-positivity").textContent = platData.positivity_rate || `${platData.pos_pct}%`;
  document.getElementById("kpi-resonance").textContent = platData.resonance_rate || "85.4%";
  document.getElementById("kpi-health").textContent = platData.community_health || "97.8%";
  document.getElementById("kpi-emotion").textContent = platData.top_emotion || "Approval";

  // Update Legends
  document.getElementById("leg-pos").textContent = `${platData.pos_pct}%`;
  document.getElementById("leg-neu").textContent = `${platData.neu_pct}%`;
  document.getElementById("leg-neg").textContent = `${platData.neg_pct}%`;

  // Render Charts
  renderDonut(platData);
  renderBarChart(platData);

  // Render Feed
  renderFeed();

  // Switch View
  switchView("view-detail");
}

function renderDonut(data) {
  const ctx = document.getElementById("sentimentDonut").getContext("2d");
  if (donutChart) donutChart.destroy();

  donutChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [{
        data: [data.pos_pct, data.neu_pct, data.neg_pct],
        backgroundColor: ["#5bc5cf", "#94dcd2", "#f87171"],
        borderColor: "#15221b",
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw}%`
          }
        }
      },
      cutout: "70%"
    }
  });
}

function renderBarChart(data) {
  const ctx = document.getElementById("topicsBar").getContext("2d");
  if (topicsChart) topicsChart.destroy();

  const tags = (data.hashtags && data.hashtags.length) ? data.hashtags : [
    { tag: "#Cinema", share_pct: 35 }, { tag: "#Sports", share_pct: 28 }, { tag: "#Tech", share_pct: 22 }, { tag: "#Style", share_pct: 15 }
  ];

  topicsChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: tags.map(t => t.tag || `#${t.author}`),
      datasets: [{
        label: "Topic Weight %",
        data: tags.map(t => t.share_pct),
        backgroundColor: "rgba(91, 197, 207, 0.75)",
        borderColor: "#5bc5cf",
        borderWidth: 1,
        borderRadius: 8
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` Narrative Share: ${ctx.raw}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(148, 220, 210, 0.1)" },
          ticks: { color: "#8fb2ab", callback: (val) => `${val}%` }
        },
        y: {
          grid: { display: false },
          ticks: { color: "#f0fdf9", font: { family: "'Space Grotesk', sans-serif" } }
        }
      }
    }
  });
}

function renderFeed(searchQuery = "") {
  const container = document.getElementById("feed-container");
  const platData = (rawData && rawData.platforms && rawData.platforms[currentPlatform]) || { feed: [] };
  let items = platData.feed || [];

  const q = (searchQuery || "").toLowerCase().trim();
  if (q) {
    items = items.filter(it => it.author.toLowerCase().includes(q) || it.content.toLowerCase().includes(q) || (it.meta && it.meta.toLowerCase().includes(q)));
  }

  if (!items.length) {
    container.innerHTML = '<div style="text-align:center; padding:30px; color:#8fb2ab;">No narratives match this filter.</div>';
    return;
  }

  container.innerHTML = items.map(it => `
    <div class="feed-card">
      <div class="feed-header">
        <span class="feed-author">@${escapeHtml(it.author)}</span>
        <span class="feed-meta">${escapeHtml(it.meta || it.date || '')}</span>
      </div>
      <div class="feed-body">${escapeHtml(it.content)}</div>
      <div class="feed-footer">
        <div class="feed-tags">
          <span class="feed-tag">✦ ${escapeHtml(it.emotion)}</span>
          <span class="feed-tag" style="color:#5eead4;">${it.likes_pct}</span>
        </div>
        ${it.comments && it.comments.length ? `<span style="color:#8fb2ab; cursor:pointer;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display==='block'?'none':'block'">💬 View Responses (${it.comments.length})</span>` : ''}
      </div>
      ${it.comments && it.comments.length ? `
        <div style="display:none; margin-top:10px; padding-top:8px; border-top:1px dashed rgba(148,220,210,0.15);">
          ${it.comments.map(c => `<div style="font-size:0.82rem; color:#8fb2ab; margin-top:4px;"><b style="color:#94dcd2;">${escapeHtml(c.author)}:</b> ${escapeHtml(c.text)}</div>`).join('')}
        </div>
      ` : ''}
    </div>
  `).join("");
}

async function runLiveAnalysis() {
  const text = document.getElementById("inspector-input").value.trim();
  if (!text) return;

  const resBox = document.getElementById("inspector-result");
  resBox.style.display = "block";

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("res-badge").textContent = data.label.toUpperCase();
      document.getElementById("res-confidence").innerHTML = `Confidence: <b>${Math.round(data.confidence * 100)}%</b>`;
      document.getElementById("meter-pos").style.width = `${data.pos_pct}%`;
      document.getElementById("meter-pos-val").textContent = `${data.pos_pct}%`;
      document.getElementById("meter-neu").style.width = `${data.neu_pct}%`;
      document.getElementById("meter-neu-val").textContent = `${data.neu_pct}%`;
      document.getElementById("meter-neg").style.width = `${data.neg_pct}%`;
      document.getElementById("meter-neg-val").textContent = `${data.neg_pct}%`;
      return;
    }
  } catch (e) {
    console.log("Using client heuristics:", e);
  }

  // Client-side fallback heuristics
  const isPos = /win|great|love|good|best|awesome|massive|effortless|sublime|justice|excited/i.test(text);
  const isNeg = /bad|terrible|hate|worst|disgrace|awful|poor|fail|ugly/i.test(text);
  const pos = isPos ? 88 : 15;
  const neg = isNeg ? 78 : 10;
  const neu = 100 - (pos + neg);

  const label = isPos ? "POSITIVE" : (isNeg ? "NEGATIVE" : "NEUTRAL");
  document.getElementById("res-badge").textContent = label;
  document.getElementById("meter-pos").style.width = `${pos}%`;
  document.getElementById("meter-pos-val").textContent = `${pos}%`;
  document.getElementById("meter-neu").style.width = `${Math.max(0, neu)}%`;
  document.getElementById("meter-neu-val").textContent = `${Math.max(0, neu)}%`;
  document.getElementById("meter-neg").style.width = `${neg}%`;
  document.getElementById("meter-neg-val").textContent = `${neg}%`;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
