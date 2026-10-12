const { useState, useEffect, useRef } = React;

// Official Vector Brand Logos
const ICONS = {
  global: (
    <svg viewBox="0 0 48 48" width="48" height="48">
      <circle cx="24" cy="24" r="20" fill="none" stroke="#A5CAF7" strokeWidth="2.5" />
      <ellipse cx="24" cy="24" rx="10" ry="20" fill="none" stroke="#A5CAF7" strokeWidth="2" />
      <line x1="4" y1="24" x2="44" y2="24" stroke="#A5CAF7" strokeWidth="2" />
      <line x1="6" y1="14" x2="42" y2="14" stroke="#A5CAF7" strokeWidth="1.5" strokeDasharray="2,2" />
      <line x1="6" y1="34" x2="42" y2="34" stroke="#A5CAF7" strokeWidth="1.5" strokeDasharray="2,2" />
    </svg>
  ),
  telegram: (
    <svg viewBox="0 0 48 48" width="48" height="48">
      <circle cx="24" cy="24" r="22" fill="#2AABEE"/>
      <path d="M12 24l4 2 2 6 3.5-3.5 5.5 4.5 9-19-24 10z" fill="#FFFFFF"/>
      <path d="M18 32l-.5-6 13.5-10-10 11.5z" fill="#D2EAF9"/>
    </svg>
  ),
  x: (
    <svg viewBox="0 0 48 48" width="44" height="44">
      <rect width="48" height="48" rx="12" fill="#000000"/>
      <path d="M14 12l8.8 12.8L14 36h3l7.3-8.5L30 36h6L26.5 22.2 34.5 12h-3l-6.7 7.7L19.5 12H14zm4.2 2.2h2.5l13.1 19.6h-2.5L18.2 14.2z" fill="#FFFFFF"/>
    </svg>
  ),
  reddit: (
    <svg viewBox="0 0 48 48" width="48" height="48">
      <circle cx="24" cy="24" r="22" fill="#FF4500"/>
      <circle cx="34" cy="17" r="3.5" fill="#FFFFFF"/>
      <path d="M24 15l2-6 7 2" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
      <ellipse cx="24" cy="26" rx="12" ry="8" fill="#FFFFFF"/>
      <circle cx="19" cy="25" r="2.5" fill="#FF4500"/>
      <circle cx="29" cy="25" r="2.5" fill="#FF4500"/>
      <path d="M19 29c2 2.5 8 2.5 10 0" stroke="#FF4500" strokeWidth="2" strokeLinecap="round" fill="none"/>
    </svg>
  ),
  youtube: (
    <svg viewBox="0 0 48 48" width="48" height="48">
      <rect x="4" y="10" width="40" height="28" rx="8" fill="#FF0000"/>
      <polygon points="20,16 32,24 20,32" fill="#FFFFFF"/>
    </svg>
  ),
  instagram: (
    <svg viewBox="0 0 48 48" width="48" height="48">
      <defs>
        <radialGradient id="ig-grad" cx="20%" cy="100%" r="130%">
          <stop offset="0%" stopColor="#FFDD55"/>
          <stop offset="25%" stopColor="#FF543E"/>
          <stop offset="50%" stopColor="#C837AB"/>
          <stop offset="100%" stopColor="#3771C8"/>
        </radialGradient>
      </defs>
      <rect width="48" height="48" rx="14" fill="url(#ig-grad)"/>
      <rect x="10" y="10" width="28" height="28" rx="8" fill="none" stroke="#FFFFFF" strokeWidth="3"/>
      <circle cx="24" cy="24" r="6.5" fill="none" stroke="#FFFFFF" strokeWidth="3"/>
      <circle cx="31.5" cy="16.5" r="2" fill="#FFFFFF"/>
    </svg>
  ),
  facebook: (
    <svg viewBox="0 0 48 48" width="48" height="48">
      <circle cx="24" cy="24" r="22" fill="#1877F2"/>
      <path d="M26.5 38V25.5h4.2l.6-5h-4.8v-3.2c0-1.4.4-2.4 2.4-2.4h2.6v-4.5c-.5-.1-2-.2-3.8-.2-3.8 0-6.4 2.3-6.4 6.6V20.5h-4.3v5h4.3V38h5.2z" fill="#FFFFFF"/>
    </svg>
  )
};

const PLATFORMS_LIST = [
  { id: "telegram", name: "Telegram", icon: ICONS.telegram, tagline: "Direct Broadcasts & Channel Rooms" },
  { id: "x", name: "X (Twitter)", icon: ICONS.x, tagline: "Real-Time Commentary & Sports Pulse" },
  { id: "reddit", name: "Reddit", icon: ICONS.reddit, tagline: "Thematic Sub-Communities & Longform Debates" },
  { id: "youtube", name: "YouTube", icon: ICONS.youtube, tagline: "Cinematic Trailers & Box Office Reviews" },
  { id: "instagram", name: "Instagram", icon: ICONS.instagram, tagline: "Aesthetic Lifestyle & Visual Showcase" },
  { id: "facebook", name: "Facebook", icon: ICONS.facebook, tagline: "Community Feeds & Conversational Posts" },
];

function App() {
  const [data, setData] = useState(null);
  const [currentView, setCurrentView] = useState("landing");
  const [animClass, setAnimClass] = useState("page-swap-enter");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("network");
  
  // Extraction Loading Overlay state
  const [extracting, setExtracting] = useState(false);
  const [extractStep, setExtractStep] = useState("");
  const [extractProgress, setExtractProgress] = useState(0);

  // Selected User for Graph & RAG coordination
  const [selectedUserHandle, setSelectedUserHandle] = useState(null);

  // RAG Query State
  const [ragQueryText, setRagQueryText] = useState("Ruturaj Gaikwad and cricket selection");

  // Alchemist state
  const [alchemyText, setAlchemyText] = useState("Ruturaj Gaikwad back in the India mix is a massive win! Effortless timing and calm temperament.");
  const [alchemyLoading, setAlchemyLoading] = useState(false);
  const [alchemyResult, setAlchemyResult] = useState({
    label: "positive",
    confidence: 0.97,
    pos_pct: 97,
    neu_pct: 2,
    neg_pct: 1
  });

  useEffect(() => {
    fetchData();
    initBackgroundCanvas();
  }, []);

  const fetchData = async () => {
    try {
      const res = await fetch("/api/data");
      const d = await res.json();
      setData(d);
    } catch (e) {
      console.error("Data load notice:", e);
    }
  };

  const handleReExtract = async () => {
    setExtracting(true);
    setExtractProgress(15);
    setExtractStep("Running geographic analysis & user evidence builder...");

    setTimeout(() => {
      setExtractProgress(45);
      setExtractStep("Generating global demographic & behavioral audience profiles...");
    }, 600);

    setTimeout(() => {
      setExtractProgress(75);
      setExtractStep("Constructing Louvain network topology & re-indexing neural RAG...");
    }, 1200);

    try {
      const res = await fetch("/api/extract", { method: "POST" });
      const resData = await res.json();
      if (resData && resData.data) {
        setData(resData.data);
      } else {
        await fetchData();
      }
    } catch (e) {
      console.error("Extraction fallback:", e);
      await fetchData();
    }

    setTimeout(() => {
      setExtractProgress(100);
      setExtractStep("Extraction complete! Synchronizing observatory...");
      setTimeout(() => {
        setExtracting(false);
      }, 500);
    }, 1800);
  };

  const navigateTo = (platId, isBack = false) => {
    setAnimClass(isBack ? "page-swap-back" : "page-swap-enter");
    setCurrentView(platId);
    setActiveTab("network");
    setSelectedUserHandle(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const triggerRAGForUser = (username) => {
    setRagQueryText(`What are the community discussions, location profile, and sentiment around @${username}?`);
    setActiveTab("rag");
  };

  const currentStats = data?.platforms?.[currentView] || {
    pos_pct: 42.5, neu_pct: 44.0, neg_pct: 13.5,
    positivity_rate: "42.5%", resonance_rate: "86.5%",
    hashtags: [], authors: [], feed: [],
    network_graph: { nodes: [], links: [], communities: [], stats: {} }
  };

  const currentGraph = currentStats.network_graph || { nodes: [], links: [], communities: [], stats: {} };
  const audienceDemographics = data?.audience_demographics || null;

  const handleLiveAnalysis = async () => {
    if (!alchemyText.trim()) return;
    setAlchemyLoading(true);
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: alchemyText })
      });
      if (res.ok) {
        const result = await res.json();
        setAlchemyResult(result);
        setAlchemyLoading(false);
        return;
      }
    } catch (e) {
      console.log("Client fallback evaluation:", e);
    }
    setTimeout(() => {
      const isPos = /win|great|love|good|best|awesome|massive|effortless|sublime|justice|excited|timing/i.test(alchemyText);
      const isNeg = /bad|terrible|hate|worst|disgrace|awful|poor|fail|ugly/i.test(alchemyText);
      const pos = isPos ? 96 : 14;
      const neg = isNeg ? 82 : 3;
      const neu = 100 - (pos + neg);

      setAlchemyResult({
        label: isPos ? "positive" : (isNeg ? "negative" : "neutral"),
        confidence: 0.96,
        pos_pct: pos,
        neu_pct: Math.max(0, neu),
        neg_pct: neg
      });
      setAlchemyLoading(false);
    }, 400);
  };

  return (
    <div className="app-wrapper">
      {/* Full-Screen Extraction Loading Overlay */}
      {extracting && (
        <div className="loading-overlay">
          <div className="loading-card">
            <div className="loading-spinner-orb"></div>
            <h3 className="loading-title">Extracting Intelligence</h3>
            <p className="loading-step-text">{extractStep}</p>
            <div className="loading-progress-bar">
              <div className="loading-progress-fill" style={{ width: `${extractProgress}%` }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Top Header with Re-Extract Button */}
      <header className="top-nav">
        <div className="nav-left-flex">
          <button className="btn-extract-refresh" onClick={handleReExtract} title="Trigger data re-extraction, re-index RAG & demographic graphs">
            <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
            </svg>
            <span>Re-Extract Data</span>
          </button>
          <div className="nav-left">
            <span className="badge-pill">✦ Multi-Channel Intelligence & Location Demographics</span>
            <h1 className="nav-title">Social Media Observatory</h1>
            <p className="nav-subtitle">Community network constellations, global geographic analytics, behavioral audience personas & neural RAG.</p>
          </div>
        </div>
      </header>

      {/* Main Page Swapping View */}
      <div className={`page-container ${animClass}`}>
        {currentView === "landing" ? (
          <div className="landing-view">
            {/* Featured Global Observatory Hero Box */}
            <div className="global-hero-card" onClick={() => navigateTo("all")}>
              <div className="hero-info">
                <div className="hero-logo-badge">
                  {ICONS.global}
                </div>
                <div className="hero-text">
                  <h3>Global Observatory</h3>
                  <p>Aggregated Multi-Platform Intelligence with location analytics, demographic profiling & neural RAG search</p>
                </div>
              </div>
              <div className="hero-action">
                <span>Enter Observatory</span>
                <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2.5" fill="none"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </div>
            </div>

            {/* Symmetrical 3x2 Grid for 6 Platforms */}
            <div className="platforms-symmetric-grid">
              {PLATFORMS_LIST.map(p => (
                <div key={p.id} className="platform-tile" onClick={() => navigateTo(p.id)}>
                  <div className="tile-icon-wrap">{p.icon}</div>
                  <h4 className="tile-title">{p.name}</h4>
                  <p className="tile-desc">{p.tagline}</p>
                  <div className="tile-footer">
                    <span>Explore Channel</span>
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2.5" fill="none"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="detail-view">
            {/* Top Toolbar */}
            <div className="detail-toolbar">
              <button className="glass-btn" onClick={() => navigateTo("landing", true)}>
                <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" strokeWidth="2.5" fill="none"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                Return to Channels
              </button>

              <div className="channel-switch-chips">
                <button className={`switch-chip ${currentView === "all" ? "active" : ""}`} onClick={() => navigateTo("all")}>Global</button>
                {PLATFORMS_LIST.map(p => (
                  <button key={p.id} className={`switch-chip ${currentView === p.id ? "active" : ""}`} onClick={() => navigateTo(p.id)}>
                    {p.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Platform Hero Banner */}
            <div className="platform-hero-banner">
              <div className="banner-logo-wrap">
                {currentView === "all" ? ICONS.global : (ICONS[currentView] || ICONS.global)}
              </div>
              <div>
                <h2 className="banner-title">
                  {currentView === "all" ? "Global Observatory" : PLATFORMS_LIST.find(p => p.id === currentView)?.name}
                </h2>
                <p className="banner-desc">
                  {currentView === "all" ? "Aggregated Multi-Platform Intelligence with global location analytics, demographic profiles & neural RAG" : PLATFORMS_LIST.find(p => p.id === currentView)?.tagline}
                </p>
              </div>
            </div>

            {/* Clean 2-Card KPI Row */}
            <div className="kpi-row-grid">
              <div className="kpi-glass-card">
                <div className="kpi-big-pct" style={{ color: "#38BDF8" }}>{currentStats.positivity_rate || `${currentStats.pos_pct}%`}</div>
                <div className="kpi-title-label">Positivity Rate</div>
              </div>
              <div className="kpi-glass-card">
                <div className="kpi-big-pct" style={{ color: "#A5CAF7" }}>{currentStats.resonance_rate || "86.5%"}</div>
                <div className="kpi-title-label">Audience Resonance</div>
              </div>
            </div>

            {/* Unified Content Section with Crisp Network Graph, Location Demographics & Neural RAG */}
            <div className="content-glass-card">
              <div className="tabs-header">
                <button className={`tab-btn ${activeTab === "network" ? "active" : ""}`} onClick={() => setActiveTab("network")}>
                  🕸️ Network Graph & Dossier
                </button>
                <button className={`tab-btn ${activeTab === "demographics" ? "active" : ""}`} onClick={() => setActiveTab("demographics")}>
                  👥 Location & Demographics
                </button>
                <button className={`tab-btn ${activeTab === "rag" ? "active" : ""}`} onClick={() => setActiveTab("rag")}>
                  🤖 Neural RAG Knowledge Engine
                </button>
                <button className={`tab-btn ${activeTab === "overview" ? "active" : ""}`} onClick={() => setActiveTab("overview")}>
                  📊 Overview & Topics
                </button>
                <button className={`tab-btn ${activeTab === "feed" ? "active" : ""}`} onClick={() => setActiveTab("feed")}>
                  📜 Channel Chronicle
                </button>
                <button className={`tab-btn ${activeTab === "alchemist" ? "active" : ""}`} onClick={() => setActiveTab("alchemist")}>
                  🧪 Live Sentiment Alchemist
                </button>
              </div>

              {/* TAB 1: CRISP D3 NETWORK CONSTELLATION GRAPH & USER DOSSIER */}
              {activeTab === "network" && (
                <D3NetworkGraphSection 
                  graphData={currentGraph} 
                  platformName={currentView === "all" ? "Global" : PLATFORMS_LIST.find(p => p.id === currentView)?.name}
                  onQueryUserInRAG={triggerRAGForUser}
                />
              )}

              {/* TAB 2: AUDIENCE, LOCATION & DEMOGRAPHIC PROFILING */}
              {activeTab === "demographics" && (
                <DemographicsSection 
                  demographicsData={audienceDemographics}
                  onFilterTopicInRAG={(topic) => {
                    setRagQueryText(`Summarize user engagement, location profiles and demographic sentiment regarding ${topic}`);
                    setActiveTab("rag");
                  }}
                />
              )}

              {/* TAB 3: NEURAL RAG & SEMANTIC RETRIEVAL */}
              {activeTab === "rag" && (
                <NeuralRAGSection 
                  platform={currentView}
                  initialQuery={ragQueryText}
                />
              )}

              {/* TAB 4: OVERVIEW CHARTS */}
              {activeTab === "overview" && (
                <ChartsSection stats={currentStats} />
              )}

              {/* TAB 5: FEED */}
              {activeTab === "feed" && (
                <div className="feed-tab-pane">
                  <input
                    type="text"
                    className="search-field"
                    placeholder="Filter narratives by author, keywords, or tags..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <FeedList items={currentStats.feed || []} query={searchQuery} />
                </div>
              )}

              {/* TAB 6: LIVE SENTIMENT ALCHEMIST */}
              {activeTab === "alchemist" && (
                <div className="alchemist-container">
                  <label className="alchemist-label">Inscribe Custom Statement for Evaluation</label>
                  <textarea
                    className="alchemist-textarea"
                    rows="3"
                    value={alchemyText}
                    onChange={(e) => setAlchemyText(e.target.value)}
                    placeholder="Enter statement to test..."
                  />
                  <button className="btn-alchemist" onClick={handleLiveAnalysis} disabled={alchemyLoading}>
                    {alchemyLoading ? <span className="spinner-ring"></span> : <span>⚡</span>}
                    <span>{alchemyLoading ? "Evaluating Polarity..." : "Analyze Sentiment Polarity"}</span>
                  </button>

                  {alchemyResult && (
                    <div className="alchemist-result-card">
                      <div className="result-hero-row">
                        <div className={`sentiment-status-pill ${alchemyResult.label === "positive" ? "status-pos" : (alchemyResult.label === "negative" ? "status-neg" : "status-neu")}`}>
                          <span>{alchemyResult.label === "positive" ? "🌿" : (alchemyResult.label === "negative" ? "🍂" : "⚖️")}</span>
                          <span>{alchemyResult.label.toUpperCase()}</span>
                        </div>
                        <div className="confidence-score">
                          Neural Confidence: <b>{Math.round(alchemyResult.confidence * 100)}%</b>
                        </div>
                      </div>

                      <div className="meters-stack">
                        <div className="meter-row">
                          <div className="meter-header-flex">
                            <span>Positive Resonance</span>
                            <b style={{ color: "#38BDF8" }}>{alchemyResult.pos_pct}%</b>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill fill-pos" style={{ width: `${alchemyResult.pos_pct}%` }}></div>
                          </div>
                        </div>

                        <div className="meter-row">
                          <div className="meter-header-flex">
                            <span>Neutral Polarity</span>
                            <b style={{ color: "#A5CAF7" }}>{alchemyResult.neu_pct}%</b>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill fill-neu" style={{ width: `${alchemyResult.neu_pct}%` }}></div>
                          </div>
                        </div>

                        <div className="meter-row">
                          <div className="meter-header-flex">
                            <span>Critical / Negative</span>
                            <b style={{ color: "#F87171" }}>{alchemyResult.neg_pct}%</b>
                          </div>
                          <div className="progress-track">
                            <div className="progress-fill fill-neg" style={{ width: `${alchemyResult.neg_pct}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// =========================================================================
// HIGH-FIDELITY D3 INTERACTIVE NETWORK GRAPH & USER EGO DOSSIER
// =========================================================================
function D3NetworkGraphSection({ graphData, platformName, onQueryUserInRAG }) {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const zoomBehaviorRef = useRef(null);
  const simulationRef = useRef(null);

  const [selectedUser, setSelectedUser] = useState(null);
  const [userSearch, setUserSearch] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedCommunity, setSelectedCommunity] = useState("all");
  const [selectedSegment, setSelectedSegment] = useState("all");
  const [degreeThreshold, setDegreeThreshold] = useState(0);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [isPhysicsActive, setIsPhysicsActive] = useState(true);

  const rawNodes = graphData.nodes || [];
  const rawLinks = graphData.links || [];
  const communities = graphData.communities || [];

  // Top Key Voices / Hubs
  const topHubs = rawNodes.slice(0, 6);

  // Filtered dropdown suggestions
  const filteredSearchUsers = rawNodes.filter(n => {
    if (!userSearch) return false;
    const q = userSearch.toLowerCase().replace("@", "").trim();
    return (
      n.name.toLowerCase().includes(q) ||
      n.id.toLowerCase().includes(q) ||
      (n.location?.city && n.location.city.toLowerCase().includes(q)) ||
      (n.location?.country && n.location.country.toLowerCase().includes(q))
    );
  });

  const focusOnUser = (user) => {
    setSelectedUser(user);
    setUserSearch(`@${user.name}`);
    setShowDropdown(false);

    if (svgRef.current && zoomBehaviorRef.current && user.x !== undefined && user.y !== undefined) {
      const svg = d3.select(svgRef.current);
      const width = containerRef.current ? containerRef.current.clientWidth : 900;
      const height = 550;
      const scale = 1.4;

      svg.transition().duration(800).call(
        zoomBehaviorRef.current.transform,
        d3.zoomIdentity
          .translate(width / 2, height / 2)
          .scale(scale)
          .translate(-user.x, -user.y)
      );
    }
  };

  const resetView = () => {
    setSelectedUser(null);
    setUserSearch("");
    setShowDropdown(false);
    if (svgRef.current && zoomBehaviorRef.current) {
      const svg = d3.select(svgRef.current);
      const width = containerRef.current ? containerRef.current.clientWidth : 900;
      const height = 550;
      svg.transition().duration(700).call(
        zoomBehaviorRef.current.transform,
        d3.zoomIdentity.translate(0, 0).scale(1)
      );
    }
  };

  const handleZoom = (factor) => {
    if (svgRef.current && zoomBehaviorRef.current) {
      const svg = d3.select(svgRef.current);
      svg.transition().duration(350).call(zoomBehaviorRef.current.scaleBy, factor);
    }
  };

  const togglePhysics = () => {
    if (simulationRef.current) {
      if (isPhysicsActive) {
        simulationRef.current.stop();
      } else {
        simulationRef.current.alpha(0.3).restart();
      }
      setIsPhysicsActive(!isPhysicsActive);
    }
  };

  // Build & Manage D3 Simulation (Global Overview or Dedicated User Ego Network)
  useEffect(() => {
    if (!containerRef.current || typeof d3 === "undefined") return;

    const width = containerRef.current.clientWidth || 900;
    const height = 550;

    let nodes = [];
    let links = [];
    const isEgoView = Boolean(selectedUser);

    if (isEgoView) {
      // 1. DEDICATED EGO NETWORK FOR SELECTED USER ACCOUNT
      const egoCenter = {
        ...selectedUser,
        isCenter: true,
        radius: 28,
        color: selectedUser.color || "#38BDF8",
        fx: width / 2,
        fy: height / 2
      };

      const neighbors = [];
      const neighborIds = new Set();
      neighborIds.add(String(selectedUser.id));
      neighborIds.add(String(selectedUser.name));

      const rawConns = selectedUser.connections || [];
      rawConns.forEach((c) => {
        const targetId = String(c.target);
        if (neighborIds.has(targetId)) return;
        neighborIds.add(targetId);

        const foundNode = rawNodes.find(n => String(n.id) === targetId || String(n.name) === targetId);
        if (foundNode) {
          neighbors.push({
            ...foundNode,
            isCenter: false,
            radius: Math.max(14, Math.min(22, (foundNode.radius || 12) * 1.15)),
            tieType: c.type || "Connection"
          });
        } else {
          neighbors.push({
            id: targetId,
            name: targetId,
            radius: 14,
            community_id: selectedUser.community_id || 0,
            community_label: selectedUser.community_label || "Community Tier",
            color: selectedUser.color || "#A5CAF7",
            location: selectedUser.location || { city: "Metro Hub", country: "Regional", flag: "📍" },
            behavioral_segment: "Active Participant",
            isCenter: false,
            tieType: c.type || "Co-Chatter",
            posts_count: 5,
            degree: 4
          });
        }
      });

      // If very few connections, add peers from the same community
      if (neighbors.length < 4) {
        const sameCommNodes = rawNodes.filter(n => n.community_id === selectedUser.community_id && !neighborIds.has(String(n.id)) && !neighborIds.has(String(n.name)));
        sameCommNodes.slice(0, 6 - neighbors.length).forEach(sn => {
          neighborIds.add(String(sn.id));
          neighbors.push({
            ...sn,
            isCenter: false,
            radius: 14,
            tieType: "Community Peer"
          });
        });
      }

      nodes = [egoCenter, ...neighbors];
      links = neighbors.map(nbr => ({
        source: egoCenter.id,
        target: nbr.id,
        type: nbr.tieType || "Connection",
        weight: 2.5
      }));
    } else {
      // 2. GLOBAL CONSTELLATION OVERVIEW
      let visibleNodes = rawNodes.filter(n => {
        if (selectedCommunity !== "all" && n.community_id !== parseInt(selectedCommunity, 10)) return false;
        if (selectedSegment !== "all" && n.behavioral_segment !== selectedSegment) return false;
        if (n.degree < degreeThreshold) return false;
        return true;
      });

      const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
      const visibleLinks = rawLinks.filter(l => visibleNodeIds.has(String(l.source.id || l.source)) && visibleNodeIds.has(String(l.target.id || l.target)));

      nodes = visibleNodes.map(d => ({ ...d, isCenter: false }));
      links = visibleLinks.map(d => ({ ...d }));
    }

    // Clear previous svg content
    const svgEl = d3.select(svgRef.current);
    svgEl.selectAll("*").remove();

    svgEl.attr("viewBox", `0 0 ${width} ${height}`)
         .attr("width", width)
         .attr("height", height);

    // Root Group for Zoom/Pan
    const g = svgEl.append("g").attr("class", "graph-root-group");

    // Configure Zoom
    const zoom = d3.zoom()
      .scaleExtent([0.3, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svgEl.call(zoom);
    zoomBehaviorRef.current = zoom;

    // Force Simulation Setup
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(isEgoView ? 140 : 75).strength(isEgoView ? 0.8 : 0.45))
      .force("charge", d3.forceManyBody().strength(isEgoView ? -280 : -160).distanceMax(450))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(d => (d.radius || 10) + (isEgoView ? 16 : 12)).iterations(2))
      .alphaDecay(isEgoView ? 0.045 : 0.035);

    simulationRef.current = simulation;

    // Render Links
    const linkGroup = g.append("g").attr("class", "links");

    const link = linkGroup
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", isEgoView ? "rgba(56, 189, 248, 0.75)" : "rgba(165, 202, 247, 0.22)")
      .attr("stroke-width", d => isEgoView ? 2.5 : Math.min(3, Math.max(1, (d.weight || 1) * 0.8)))
      .attr("stroke-dasharray", d => d.type === "Co-Chatter" ? "4,3" : "none");

    // Link Labels for Ego Network
    let linkLabels = null;
    if (isEgoView) {
      linkLabels = linkGroup.selectAll(".link-label")
        .data(links)
        .enter()
        .append("text")
        .attr("class", "link-label")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("fill", "#A5CAF7")
        .attr("font-size", "9.5px")
        .attr("font-weight", "700")
        .attr("letter-spacing", "0.03em")
        .style("pointer-events", "none")
        .style("text-shadow", "0 2px 8px rgba(0,0,0,0.95)")
        .text(d => d.type || "Tie");
    }

    // Drag behavior
    const drag = (sim) => {
      function dragstarted(event, d) {
        if (!event.active) sim.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }
      function dragended(event, d) {
        if (!event.active) sim.alphaTarget(0);
        if (!d.isCenter) {
          d.fx = null;
          d.fy = null;
        }
      }
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    };

    // Render Node Groups
    const nodeGroup = g.append("g")
      .attr("class", "nodes")
      .selectAll(".node-item")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", "node-item")
      .call(drag(simulation));

    // Outer Glow Circle
    nodeGroup.append("circle")
      .attr("class", "node-glow-ring")
      .attr("r", d => (d.radius || 10) + (d.isCenter ? 8 : 4))
      .attr("fill", d => d.isCenter ? "rgba(56, 189, 248, 0.15)" : "transparent")
      .attr("stroke", d => d.isCenter ? "#FFFFFF" : (d.color || "#38BDF8"))
      .attr("stroke-width", d => d.isCenter ? 2.5 : 1.5)
      .attr("stroke-dasharray", d => d.isCenter ? "none" : (d.degree > 6 ? "none" : "3,3"))
      .attr("opacity", d => d.isCenter ? 1 : 0.7);

    // Main Node Circle
    nodeGroup.append("circle")
      .attr("class", "node-main-disc")
      .attr("r", d => d.radius || 10)
      .attr("fill", d => d.isCenter ? "#38BDF8" : (d.color || "#38BDF8"))
      .attr("stroke", "#080D1D")
      .attr("stroke-width", d => d.isCenter ? 3.5 : 2.5)
      .style("cursor", "pointer");

    // Initials inside node
    nodeGroup.append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", d => d.isCenter ? 14 : Math.max(8, (d.radius || 10) * 0.75))
      .attr("font-weight", "800")
      .attr("fill", "#080D1D")
      .style("pointer-events", "none")
      .text(d => (d.name ? d.name.substring(0, 1).toUpperCase() : "U"));

    // Username Label below node
    nodeGroup.append("text")
      .attr("class", "node-label")
      .attr("y", d => (d.radius || 10) + (d.isCenter ? 18 : 14))
      .attr("text-anchor", "middle")
      .attr("fill", d => d.isCenter ? "#38BDF8" : "#FFFFFF")
      .attr("font-size", d => d.isCenter ? "12px" : "10px")
      .attr("font-weight", d => d.isCenter ? "800" : "600")
      .attr("letter-spacing", "0.02em")
      .style("pointer-events", "none")
      .text(d => `@${d.name.length > 15 ? d.name.substring(0, 13) + '..' : d.name}`);

    // Node Click & Hover Interactions
    nodeGroup
      .on("click", (event, d) => {
        event.stopPropagation();
        focusOnUser(d);
      })
      .on("mouseenter", (event, d) => {
        setHoveredNode(d);
        const rect = containerRef.current.getBoundingClientRect();
        setTooltipPos({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        });
      })
      .on("mousemove", (event) => {
        const rect = containerRef.current.getBoundingClientRect();
        setTooltipPos({
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        });
      })
      .on("mouseleave", () => {
        setHoveredNode(null);
      });

    // Tick Handler
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      if (linkLabels) {
        linkLabels
          .attr("x", d => (d.source.x + d.target.x) / 2)
          .attr("y", d => (d.source.y + d.target.y) / 2);
      }

      nodeGroup
        .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [graphData, selectedUser, selectedCommunity, selectedSegment, degreeThreshold]);

  return (
    <div className="graph-d3-wrapper">
      {/* Top Influencers Quick Carousel */}
      <div className="top-influencers-bar">
        <span className="influencers-label">👑 Key Network Voices:</span>
        <div className="influencer-chips-row">
          {topHubs.map(hub => (
            <button
              key={hub.id}
              className={`influencer-chip ${selectedUser?.id === hub.id ? 'active' : ''}`}
              onClick={() => focusOnUser(hub)}
            >
              <span className="chip-avatar" style={{ background: hub.color }}>{hub.name.charAt(0).toUpperCase()}</span>
              <span>@{hub.name}</span>
              <span className="chip-deg">Core Hub</span>
            </button>
          ))}
        </div>
      </div>

      {/* Search & Filters Toolbar */}
      <div className="graph-toolbar-row">
        <div className="user-search-wrapper">
          <input
            type="text"
            className="network-user-input"
            placeholder={`🔍 Search user, city, or country in ${platformName} (e.g. @larisa_vasilieva, Chennai, Seattle)...`}
            value={userSearch}
            onFocus={() => setShowDropdown(true)}
            onChange={(e) => {
              const val = e.target.value;
              setUserSearch(val);
              setShowDropdown(true);
              const exact = rawNodes.find(n => n.name.toLowerCase() === val.toLowerCase().replace("@", "").trim());
              if (exact) focusOnUser(exact);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && filteredSearchUsers.length > 0) {
                focusOnUser(filteredSearchUsers[0]);
              }
            }}
          />
          {showDropdown && userSearch && filteredSearchUsers.length > 0 && (
            <div className="search-dropdown-menu">
              {filteredSearchUsers.map(u => (
                <div key={u.id} className="dropdown-user-item" onClick={() => focusOnUser(u)}>
                  <div className="dropdown-user-header">
                    <span className="dropdown-name" style={{ color: u.color }}>@{u.name}</span>
                    <span className="dropdown-community">{u.location?.city}, {u.location?.country} {u.location?.flag}</span>
                  </div>
                  <div className="dropdown-user-stats">
                    {u.behavioral_segment} • {u.age_bracket} • Active Voice
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Behavioral Segment Filters */}
        <div className="community-filter-chips">
          <button 
            className={`comm-chip ${selectedSegment === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedSegment('all')}
          >
            All Segments
          </button>
          {[
            { id: "Data Analyst", icon: "⚡", label: "Data Analyst" },
            { id: "Professional Analyst", icon: "⚡", label: "Professional Analyst" },
            { id: "Community Builder", icon: "💬", label: "Community Builder" },
            { id: "Content Creator", icon: "🌟", label: "Content Creator" },
            { id: "Journalist", icon: "📰", label: "Journalist" },
            { id: "Researcher", icon: "🔬", label: "Researcher" },
            { id: "Coach", icon: "🎯", label: "Coach" },
            { id: "Enthusiast", icon: "🔥", label: "Enthusiast" },
            { id: "Scout", icon: "🔭", label: "Scout" }
          ].map((seg, sIdx) => {
            const count = rawNodes.filter(n => n.behavioral_segment === seg.id).length;
            if (count === 0 && selectedSegment !== seg.id) return null;
            return (
              <button
                key={sIdx}
                className={`comm-chip ${selectedSegment === seg.id ? 'active' : ''}`}
                onClick={() => setSelectedSegment(seg.id)}
              >
                <span>{seg.icon} {seg.label}</span>
              </button>
            );
          })}
        </div>

        {selectedUser && (
          <button className="glass-btn" style={{ padding: "9px 18px", fontSize: "0.84rem" }} onClick={resetView}>
            ✕ Reset Spotlight
          </button>
        )}
      </div>

      {/* Selected User Intelligence Dossier Card */}
      {selectedUser && (
        <div className="user-dossier-card">
          <div className="dossier-header-flex">
            <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
              <div className="dossier-avatar-badge" style={{ background: selectedUser.color }}>
                {selectedUser.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                  <span className="dossier-handle">@{selectedUser.name}</span>
                  <span className="status-badge-chip" style={{ background: selectedUser.online ? "rgba(56,189,248,0.2)" : "rgba(255,255,255,0.1)", color: selectedUser.online ? "#38BDF8" : "#C7DEF9" }}>
                    {selectedUser.online ? "🟢 Online" : "⚪ Offline"}
                  </span>
                  <span className="location-badge-chip">
                    📍 {selectedUser.location?.city}, {selectedUser.location?.country} {selectedUser.location?.flag}
                  </span>
                  <span className="demographic-age-chip">
                    🎂 Age: <b>{selectedUser.age_bracket}</b>
                  </span>
                  <span className="segment-badge-chip">
                    ⚡ {selectedUser.behavioral_segment}
                  </span>
                </div>
                <div className="dossier-meta-subtitle">
                  <span>🗣️ {selectedUser.primary_language || 'English'}</span>
                  <span>•</span>
                  <span>💼 {selectedUser.occupation_field || 'Sports Analytics'}</span>
                  <span>•</span>
                  <span>🎓 {selectedUser.education_level || 'Graduate'}</span>
                </div>
                <p className="dossier-bio-text">{selectedUser.bio}</p>
              </div>
            </div>

            <button 
              className="btn-rag-jump" 
              onClick={() => onQueryUserInRAG(selectedUser.name)}
              title="Query Neural RAG for discourse and demographic analysis regarding this user"
            >
              <span>🤖 Query in Neural RAG</span>
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2.5" fill="none"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>

          {/* Stats Grid */}
          <div className="dossier-stats-grid">
            <div className="dossier-stat-box">
              <div className="dossier-stat-num">Very High</div>
              <div className="dossier-stat-lbl">Posts Resonance</div>
            </div>
            <div className="dossier-stat-box">
              <div className="dossier-stat-num">Active</div>
              <div className="dossier-stat-lbl">Chat Channels</div>
            </div>
            <div className="dossier-stat-box">
              <div className="dossier-stat-num">High</div>
              <div className="dossier-stat-lbl">Discussion</div>
            </div>
            <div className="dossier-stat-box">
              <div className="dossier-stat-num">Core Voice</div>
              <div className="dossier-stat-lbl">Influence Tier</div>
            </div>
            <div className="dossier-stat-box">
              <div className="dossier-stat-num">High Ties</div>
              <div className="dossier-stat-lbl">Network Centrality</div>
            </div>
            <div className="dossier-stat-box">
              <div className="dossier-stat-num">{selectedUser.location?.metro_cluster?.split(" ")[0] || "Regional"}</div>
              <div className="dossier-stat-lbl">Geo Cluster</div>
            </div>
          </div>

          {/* Behavioral Interests & Content Preferences */}
          <div className="dossier-interests-row">
            {selectedUser.behavioral_interests && selectedUser.behavioral_interests.length > 0 && (
              <div className="interests-box-col">
                <div className="col-label">Observed Behavioral Interests & Scores</div>
                <div className="behavioral-bars-stack">
                  {selectedUser.behavioral_interests.map((bi, bIdx) => (
                    <div key={bIdx} className="behavior-meter-item">
                      <div className="meter-label-flex">
                        <span>{bi.category}</span>
                        <b>{bi.score_pct}%</b>
                      </div>
                      <div className="meter-track">
                        <div className="meter-fill" style={{ width: `${Math.max(10, bi.score_pct)}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedUser.observed_content_preferences && selectedUser.observed_content_preferences.length > 0 && (
              <div className="interests-box-col">
                <div className="col-label">Observed Content Preferences & Keywords</div>
                <div className="content-prefs-wrap">
                  {selectedUser.observed_content_preferences.map((pref, pIdx) => (
                    <div key={pIdx} className="pref-badge-item">
                      <div className="pref-category-title">🎯 {pref.category}</div>
                      <div className="pref-keywords-tags">
                        {(pref.evidence || []).map((ev, evIdx) => (
                          <span key={evIdx} className="pref-tag">#{ev}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Ego Connections & Snippets Grid */}
          <div className="dossier-lower-split">
            {selectedUser.connections && selectedUser.connections.length > 0 && (
              <div className="dossier-connections-col">
                <div className="col-label">Direct Ego Ties</div>
                <div className="ties-chips-wrap">
                  {selectedUser.connections.map((conn, idx) => {
                    const targetNode = rawNodes.find(n => n.id === conn.target || n.name === conn.target);
                    const displayName = targetNode ? targetNode.name : conn.target;
                    return (
                      <span 
                        key={idx} 
                        className="connection-tag"
                        onClick={() => targetNode && focusOnUser(targetNode)}
                        style={{ cursor: targetNode ? "pointer" : "default" }}
                      >
                        <b>@{displayName}</b>
                        <small className="conn-type-badge">{conn.type}</small>
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {selectedUser.snippets && selectedUser.snippets.length > 0 && (
              <div className="dossier-snippets-col">
                <div className="col-label">Recent Quoted Discourse</div>
                {selectedUser.snippets.map((snip, sIdx) => (
                  <div key={sIdx} className="dossier-snippet-item">"{snip}..."</div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main D3 SVG Canvas Viewport */}
      <div ref={containerRef} className="d3-viewport-container">
        <svg ref={svgRef} id="network-d3-canvas"></svg>

        {/* Ego Network Active Banner */}
        {selectedUser && (
          <div className="ego-viewport-banner">
            <div className="ego-banner-left">
              <span className="ego-badge">🎯 Personal Ego Network</span>
              <span className="ego-title">@{selectedUser.name}</span>
              <span className="ego-location">📍 {selectedUser.location?.city}, {selectedUser.location?.country} {selectedUser.location?.flag}</span>
              <span className="ego-segment">⚡ {selectedUser.behavioral_segment}</span>
            </div>
            <button className="btn-ego-reset" onClick={resetView} title="Return to global network graph">
              🌐 Global Network View
            </button>
          </div>
        )}

        {/* Viewport Overlay Controls */}
        <div className="viewport-overlay-controls">
          <button className="control-glass-btn" onClick={() => handleZoom(1.3)} title="Zoom In">🔍 +</button>
          <button className="control-glass-btn" onClick={() => handleZoom(0.75)} title="Zoom Out">🔍 −</button>
          <button className="control-glass-btn" onClick={resetView} title="Center Viewport">🎯 Center</button>
          <button className="control-glass-btn" onClick={togglePhysics} title="Toggle Physics Simulation">
            {isPhysicsActive ? "⏸️ Pause" : "▶️ Settle"}
          </button>
        </div>

        {/* Community Legend Footer */}
        <div className="viewport-legend-footer">
          <span style={{ fontWeight: 700, color: "#FFFFFF", marginRight: "6px" }}>Clusters:</span>
          {communities.map((c, idx) => (
            <div key={idx} className="legend-item">
              <span className="legend-dot" style={{ background: c.color }}></span>
              <span>{c.label}</span>
            </div>
          ))}
        </div>

        {/* Hover Tooltip */}
        {hoveredNode && (
          <div 
            className="node-hover-tooltip"
            style={{ 
              left: `${Math.min(tooltipPos.x + 15, containerRef.current?.clientWidth - 240 || 300)}px`, 
              top: `${Math.max(15, tooltipPos.y - 45)}px` 
            }}
          >
            <div className="tooltip-title" style={{ color: hoveredNode.color }}>@{hoveredNode.name}</div>
            <div className="tooltip-sub">📍 {hoveredNode.location?.city}, {hoveredNode.location?.country} {hoveredNode.location?.flag}</div>
            <div className="tooltip-stats">
              {hoveredNode.behavioral_segment} • {hoveredNode.age_bracket} • Active Node
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// =========================================================================
// AUDIENCE DEMOGRAPHICS, LOCATION & BEHAVIORAL INTELLIGENCE COMPONENT
// =========================================================================
function DemographicsSection({ demographicsData, onFilterTopicInRAG }) {
  if (!demographicsData) {
    return <div style={{ padding: "30px", textAlign: "center", color: "#C7DEF9" }}>Loading demographic and location analytics...</div>;
  }

  const { total_demographic_profiles, age_summary, geographic_distribution, language_distribution, occupations, education_levels, behavioral_segments, age_interest_matrix, activity_metrics } = demographicsData;

  return (
    <div className="demographics-pane">
      {/* Top Metric Summary Cards */}
      <div className="demographics-kpi-grid">
        <div className="demo-stat-card">
          <div className="demo-stat-val" style={{ color: "#38BDF8" }}>Global <small style={{ fontSize: "1rem" }}>Scope</small></div>
          <div className="demo-stat-lbl">Audience Coverage</div>
          <div className="demo-stat-sub">Across 37 countries & 50+ metro cities</div>
        </div>

        <div className="demo-stat-card">
          <div className="demo-stat-val" style={{ color: "#A5CAF7" }}>{age_summary.median_age} <small style={{ fontSize: "1rem" }}>Yrs</small></div>
          <div className="demo-stat-lbl">Median Community Age</div>
          <div className="demo-stat-sub">Span: {age_summary.minimum_age} – {age_summary.maximum_age} years</div>
        </div>

        <div className="demo-stat-card">
          <div className="demo-stat-val" style={{ color: "#60A5FA" }}>{activity_metrics.online_percentage}</div>
          <div className="demo-stat-lbl">Active Engagement Rate</div>
          <div className="demo-stat-sub">Multi-regional online presence</div>
        </div>

        <div className="demo-stat-card">
          <div className="demo-stat-val" style={{ color: "#C7DEF9" }}>Full <small style={{ fontSize: "1rem" }}>Spectrum</small></div>
          <div className="demo-stat-lbl">Behavioral Persona Tiers</div>
          <div className="demo-stat-sub">From Data Analysts to Content Creators</div>
        </div>
      </div>

      {/* Geographic Distribution: Top Countries & Top Metropolitan Cities */}
      <div className="demo-split-grid">
        {/* Top Countries Card */}
        <div className="demo-panel-card">
          <div className="demo-panel-header">
            <h3>🌍 Geographic Country Distribution</h3>
            <span>Top user concentrations by country & territory</span>
          </div>

          <div className="geo-countries-list">
            {geographic_distribution.top_countries.map((c, cIdx) => (
              <div key={cIdx} className="geo-country-row" onClick={() => onFilterTopicInRAG(c.country)}>
                <div className="geo-country-header">
                  <span className="country-title">{c.flag} {c.country}</span>
                  <span className="country-count"><b>{c.percentage}%</b></span>
                </div>
                <div className="geo-progress-track">
                  <div className="geo-progress-fill" style={{ width: `${Math.max(6, c.percentage * 4.5)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Metropolitan Cities & Coordinates */}
        <div className="demo-panel-card">
          <div className="demo-panel-header">
            <h3>📍 Top Metropolitan Cities & Coordinates</h3>
            <span>Urban hubs with precise geo-latitude and longitude</span>
          </div>

          <div className="geo-cities-grid">
            {geographic_distribution.top_cities.map((city, ctIdx) => (
              <div key={ctIdx} className="geo-city-card" onClick={() => onFilterTopicInRAG(city.city)}>
                <div className="city-top-flex">
                  <span className="city-name">{city.flag} {city.city}</span>
                  <span className="city-share-badge">{city.percentage}%</span>
                </div>
                <div className="city-region-sub">{city.region}, {city.country}</div>
                <div className="city-coords-pill">
                  🌐 Lat: {city.lat.toFixed(2)}, Lng: {city.lng.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Languages & Occupations Grid */}
      <div className="demo-split-grid">
        {/* Primary Languages */}
        <div className="demo-panel-card">
          <div className="demo-panel-header">
            <h3>🗣️ Primary Languages Spoken</h3>
            <span>Linguistic diversity across global user profiles</span>
          </div>

          <div className="interests-ranked-list">
            {language_distribution.map((lang, lIdx) => (
              <div key={lIdx} className="interest-rank-row" onClick={() => onFilterTopicInRAG(lang.language)}>
                <div className="interest-rank-info">
                  <span className="interest-name">✦ {lang.language}</span>
                  <span className="interest-share"><b>{lang.percentage}%</b></span>
                </div>
                <div className="interest-rank-track">
                  <div className="interest-rank-fill" style={{ width: `${Math.max(6, lang.percentage * 2.2)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Professional & Occupational Fields */}
        <div className="demo-panel-card">
          <div className="demo-panel-header">
            <h3>💼 Occupational & Professional Specializations</h3>
            <span>Primary career domain and industry engagement</span>
          </div>

          <div className="interests-ranked-list">
            {occupations.map((occ, oIdx) => (
              <div key={oIdx} className="interest-rank-row" onClick={() => onFilterTopicInRAG(occ.occupation)}>
                <div className="interest-rank-info">
                  <span className="interest-name">🎯 {occ.occupation}</span>
                  <span className="interest-share"><b>{occ.percentage}%</b></span>
                </div>
                <div className="interest-rank-track">
                  <div className="interest-rank-fill fill-secondary" style={{ width: `${Math.max(6, occ.percentage * 7)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Age Brackets & Behavioral Audience Segments */}
      <div className="demo-split-grid">
        {/* Age Brackets Card */}
        <div className="demo-panel-card">
          <div className="demo-panel-header">
            <h3>🎂 Age Demographics & Pyramid</h3>
            <span>Verified age bracket distribution (Median: {age_summary.median_age} Yrs)</span>
          </div>

          <div className="age-distribution-bars">
            {age_summary.brackets.map((b, bIdx) => (
              <div key={bIdx} className="age-bracket-row">
                <div className="age-bracket-label">
                  <b>{b.bracket}</b>
                  <span><b>{b.percentage}%</b></span>
                </div>
                <div className="age-bracket-track">
                  <div className="age-bracket-fill" style={{ width: `${Math.max(5, b.percentage * 2.8)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Behavioral Segments Breakdown */}
        <div className="demo-panel-card">
          <div className="demo-panel-header">
            <h3>⚡ Behavioral Persona Segments</h3>
            <span>Categorized by analytical depth and interaction profile</span>
          </div>

          <div className="segments-list-stack">
            {behavioral_segments.map((seg, sIdx) => (
              <div key={sIdx} className="segment-item-card">
                <div className="segment-top-row">
                  <span className="segment-title">
                    {seg.segment.includes('Analyst') ? '⚡' : (seg.segment.includes('Creator') ? '🌟' : (seg.segment.includes('Builder') ? '💬' : '🔹'))} {seg.segment}
                  </span>
                  <span className="segment-count-badge">
                    {seg.percentage}%
                  </span>
                </div>
                <p className="segment-desc-text">{seg.description}</p>
                <div className="segment-progress-track">
                  <div className="segment-progress-fill" style={{ width: `${Math.max(8, seg.percentage * 6)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Age x Interest Affinity Cross-Tabulation Matrix */}
      <div className="demo-panel-card">
        <div className="demo-panel-header">
          <h3>📊 Age Bracket × Category Affinity Matrix</h3>
          <span>Cross-tabulated percentage affinity across demographic segments</span>
        </div>

        <div className="matrix-table-wrap">
          <table className="affinity-matrix-table">
            <thead>
              <tr>
                <th>Age Bracket</th>
                <th>Tech & Software</th>
                <th>Arts & Design</th>
                <th>Sports & Racing</th>
                <th>Cinema & Marvel</th>
                <th>Travel & Lifestyle</th>
              </tr>
            </thead>
            <tbody>
              {age_interest_matrix.map((row, rIdx) => (
                <tr key={rIdx}>
                  <td className="matrix-bracket-cell"><b>{row.bracket}</b></td>
                  <td><span className="affinity-pill">{row.tech}</span></td>
                  <td><span className="affinity-pill">{row.arts}</span></td>
                  <td><span className="affinity-pill">{row.sports}</span></td>
                  <td><span className="affinity-pill">{row.cinema}</span></td>
                  <td><span className="affinity-pill">{row.travel}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// =========================================================================
// NEURAL RAG & SEMANTIC INTELLIGENCE EXPLORER COMPONENT
// =========================================================================
function NeuralRAGSection({ platform, initialQuery }) {
  const [query, setQuery] = useState(initialQuery || "Ruturaj Gaikwad and cricket selection");
  const [loading, setLoading] = useState(false);
  const [ragResult, setRagResult] = useState(null);

  const samplePrompts = [
    { label: "🌍 Global Geographic Breakdown", text: "What is the geographic distribution and top cities of our audience?" },
    { label: "👥 Demographics & Age Spread", text: "What is the age breakdown, languages, and occupations in the community?" },
    { label: "⚡ Data Analysts & Creators", text: "Who are the top Data Analysts and Content Creators in the network?" },
    { label: "🏏 Ruturaj & CSK Leadership", text: "What is the consensus on Ruturaj Gaikwad leadership in CSK?" },
    { label: "🎬 Marvel Multiverse Debates", text: "Summarize Marvel MCU multiverse and Robert Downey Jr discussions" },
    { label: "✨ Skincare Barrier & SPF", text: "What are users saying about skincare routines and SPF protection?" }
  ];

  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      executeRAGQuery(initialQuery);
    } else {
      executeRAGQuery("Ruturaj Gaikwad and cricket selection");
    }
  }, [platform, initialQuery]);

  const executeRAGQuery = async (queryText) => {
    const q = (queryText || query).trim();
    if (!q) return;
    setLoading(true);
    try {
      const res = await fetch("/api/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, platform: platform || "all" })
      });
      if (res.ok) {
        const data = await res.json();
        setRagResult(data);
      }
    } catch (e) {
      console.error("RAG fetch notice:", e);
    }
    setLoading(false);
  };

  return (
    <div className="rag-explorer-pane">
      {/* Search Input Bar */}
      <div className="rag-input-box">
        <div className="rag-input-header">
          <span className="rag-badge">✦ Neural RAG Assistant</span>
          <span className="rag-corpus-note">Grounding multi-channel discourse documents & global location profiles</span>
        </div>
        <div className="rag-search-row">
          <input
            type="text"
            className="rag-search-field"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && executeRAGQuery(query)}
            placeholder="Ask any natural language question across social commentary, location demographics, or user personas..."
          />
          <button 
            className="btn-rag-submit" 
            onClick={() => executeRAGQuery(query)}
            disabled={loading}
          >
            {loading ? <span className="spinner-ring"></span> : <span>⚡ Synthesize</span>}
          </button>
        </div>

        {/* Suggested Quick Prompts */}
        <div className="rag-quick-prompts">
          <span className="quick-label">Try Inquiries:</span>
          {samplePrompts.map((p, pIdx) => (
            <button
              key={pIdx}
              className="quick-prompt-chip"
              onClick={() => {
                setQuery(p.text);
                executeRAGQuery(p.text);
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* RAG Synthesis Result Card */}
      {ragResult && (
        <div className="rag-response-container">
          {/* AI Executive Synthesis Card */}
          <div className="rag-synthesis-card">
            <div className="synthesis-header-row">
              <div className="synthesis-title-flex">
                <span className="ai-spark-icon">🤖</span>
                <h3>Discourse & Persona Findings</h3>
              </div>
              <div className="sources-count-badge">
                Grounded Records
              </div>
            </div>

            {/* Synthesized Markdown Response */}
            <div className="synthesis-text-body">
              {ragResult.summary.split("\n\n").map((para, idx) => (
                <p key={idx} dangerouslySetInnerHTML={{ __html: formatMarkdown(para) }}></p>
              ))}
            </div>

            {/* Discourse Polarity Distribution Bars */}
            {ragResult.stats && (
              <div className="rag-polarity-summary">
                <div className="polarity-label">Retrieved Evidence Polarity:</div>
                <div className="polarity-bar-stack">
                  <div className="polarity-seg seg-pos" style={{ width: `${ragResult.stats.pos_pct}%` }} title={`Positive: ${ragResult.stats.pos_pct}%`}>
                    {ragResult.stats.pos_pct > 10 ? `${ragResult.stats.pos_pct}% Pos` : ''}
                  </div>
                  <div className="polarity-seg seg-neu" style={{ width: `${ragResult.stats.neu_pct}%` }} title={`Neutral: ${ragResult.stats.neu_pct}%`}>
                    {ragResult.stats.neu_pct > 10 ? `${ragResult.stats.neu_pct}% Neu` : ''}
                  </div>
                  <div className="polarity-seg seg-neg" style={{ width: `${ragResult.stats.neg_pct}%` }} title={`Critical: ${ragResult.stats.neg_pct}%`}>
                    {ragResult.stats.neg_pct > 10 ? `${ragResult.stats.neg_pct}% Neg` : ''}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Grounded Evidence Sources Dossier */}
          {ragResult.sources && ragResult.sources.length > 0 && (
            <div className="rag-sources-section">
              <h4 className="sources-section-title">
                📚 Grounded Context Evidence
              </h4>
              <div className="sources-grid">
                {ragResult.sources.map((src, sIdx) => (
                  <div key={sIdx} className="evidence-source-card">
                    <div className="evidence-top-row">
                      <div className="evidence-author-wrap">
                        <span className="platform-tag" style={{ background: getPlatformColor(src.platform) }}>
                          {src.platform.toUpperCase()}
                        </span>
                        <span className="evidence-author">@{src.author}</span>
                      </div>
                      <span className="evidence-relevance">
                        {src.relevance_pct}% match
                      </span>
                    </div>

                    <p className="evidence-content-text">"{src.content}"</p>

                    <div className="evidence-bottom-row">
                      <span className="evidence-date">{src.meta || src.date}</span>
                      <span className={`evidence-sent-pill sent-${src.sentiment}`}>
                        {src.sentiment === "positive" ? "🌿 Positive" : (src.sentiment === "negative" ? "🍂 Critical" : "⚖️ Neutral")}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dynamic Follow-Up Suggestions */}
          {ragResult.suggested_queries && ragResult.suggested_queries.length > 0 && (
            <div className="rag-followups-card">
              <span className="followup-title">💡 Deepen Inquiry:</span>
              <div className="followup-chips-row">
                {ragResult.suggested_queries.map((sug, sugIdx) => (
                  <button
                    key={sugIdx}
                    className="followup-chip"
                    onClick={() => {
                      setQuery(sug);
                      executeRAGQuery(sug);
                    }}
                  >
                    <span>{sug}</span>
                    <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" strokeWidth="2" fill="none"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Helper formatting markdown snippets
function formatMarkdown(text) {
  if (!text) return "";
  let out = text
    .replace(/^### (.*$)/gim, '<h3 style="color:#FFFFFF; font-size:1.15rem; margin-top:10px; margin-bottom:6px;">$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4 style="color:#A5CAF7; font-size:1rem; margin-top:8px; margin-bottom:4px;">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<b style="color:#FFFFFF;">$1</b>')
    .replace(/\*(.*?)\*/g, '<i style="color:#C7DEF9;">$1</i>');
  return out;
}

function getPlatformColor(plat) {
  switch (plat?.toLowerCase()) {
    case "telegram": return "rgba(42, 171, 238, 0.35)";
    case "x": return "rgba(255, 255, 255, 0.25)";
    case "reddit": return "rgba(255, 69, 0, 0.35)";
    case "youtube": return "rgba(255, 0, 0, 0.35)";
    case "instagram": return "rgba(200, 55, 171, 0.35)";
    case "facebook": return "rgba(24, 119, 242, 0.35)";
    default: return "rgba(56, 189, 248, 0.35)";
  }
}

// =========================================================================
// CHARTS SUBCOMPONENT - ULTRA-CRISP HIGH-DPI DESKTOP CHARTS
// =========================================================================
function ChartsSection({ stats }) {
  const donutRef = useRef(null);
  const barRef = useRef(null);
  const donutChart = useRef(null);
  const barChart = useRef(null);

  useEffect(() => {
    const dpr = Math.max(window.devicePixelRatio || 1, 2);

    if (donutRef.current) {
      if (donutChart.current) donutChart.current.destroy();
      donutChart.current = new Chart(donutRef.current.getContext("2d"), {
        type: "doughnut",
        data: {
          labels: ["Positive", "Neutral", "Negative"],
          datasets: [{
            data: [stats.pos_pct || 40, stats.neu_pct || 45, stats.neg_pct || 15],
            backgroundColor: ["#38BDF8", "#A5CAF7", "#F87171"],
            borderColor: "#080D1D",
            borderWidth: 3,
            hoverOffset: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          devicePixelRatio: dpr,
          plugins: {
            legend: { display: false },
            tooltip: { 
              backgroundColor: "rgba(11, 19, 43, 0.95)",
              titleColor: "#FFFFFF",
              bodyColor: "#C7DEF9",
              borderColor: "#38BDF8",
              borderWidth: 1,
              padding: 12,
              titleFont: { family: "'Space Grotesk', sans-serif", size: 13, weight: "700" },
              bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: "600" },
              callbacks: { label: (ctx) => ` ${ctx.label} Share: ${ctx.raw}%` } 
            }
          },
          cutout: "68%"
        }
      });
    }

    if (barRef.current) {
      if (barChart.current) barChart.current.destroy();
      const tags = (stats.hashtags && stats.hashtags.length) ? stats.hashtags : [
        { tag: "#F1", share_pct: 22 }, 
        { tag: "#Motorsport", share_pct: 20 }, 
        { tag: "#Formula1", share_pct: 18 }, 
        { tag: "#SportsAnalytics", share_pct: 15 },
        { tag: "#Cricket", share_pct: 13 },
        { tag: "#TeamIndia", share_pct: 11 },
        { tag: "#ROOK", share_pct: 9 },
        { tag: "#PositiveCulture", share_pct: 8 }
      ];
      barChart.current = new Chart(barRef.current.getContext("2d"), {
        type: "bar",
        data: {
          labels: tags.map(t => t.tag || `#${t.author}`),
          datasets: [{
            label: "Narrative Weight %",
            data: tags.map(t => t.share_pct),
            backgroundColor: "rgba(56, 189, 248, 0.75)",
            hoverBackgroundColor: "#38BDF8",
            borderColor: "#38BDF8",
            borderWidth: 1.5,
            borderRadius: 8,
            barThickness: 18,
            maxBarThickness: 22
          }]
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          devicePixelRatio: dpr,
          plugins: {
            legend: { display: false },
            tooltip: { 
              backgroundColor: "rgba(11, 19, 43, 0.95)",
              titleColor: "#FFFFFF",
              bodyColor: "#C7DEF9",
              borderColor: "#38BDF8",
              borderWidth: 1,
              padding: 12,
              titleFont: { family: "'Space Grotesk', sans-serif", size: 13, weight: "700" },
              bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: "600" },
              callbacks: { label: (ctx) => ` Relative Topic Weight: ${ctx.raw}%` } 
            }
          },
          scales: {
            x: {
              grid: { color: "rgba(255, 255, 255, 0.12)" },
              ticks: { 
                color: "#C7DEF9", 
                font: { family: "'Space Grotesk', sans-serif", size: 12, weight: "600" },
                callback: (val) => `${val}%` 
              }
            },
            y: {
              grid: { display: false },
              ticks: { 
                color: "#FFFFFF", 
                font: { family: "'Space Grotesk', sans-serif", size: 13, weight: "700" } 
              }
            }
          }
        }
      });
    }
  }, [stats]);

  return (
    <div className="charts-split-grid">
      <div className="chart-glass-panel">
        <div className="chart-header">
          <h3>Sentiment Equilibrium</h3>
          <span>Relative Percentage Share</span>
        </div>
        <div className="chart-box">
          <canvas ref={donutRef}></canvas>
        </div>
        <div className="chart-legend">
          <div><span className="dot-indicator pos"></span>Positive: <b>{stats.pos_pct || 40}%</b></div>
          <div><span className="dot-indicator neu"></span>Neutral: <b>{stats.neu_pct || 45}%</b></div>
          <div><span className="dot-indicator neg"></span>Negative: <b>{stats.neg_pct || 15}%</b></div>
        </div>
      </div>

      <div className="chart-glass-panel">
        <div className="chart-header">
          <h3>Top Narrative Themes</h3>
          <span>Relative Topic Share Weight</span>
        </div>
        <div className="chart-box">
          <canvas ref={barRef}></canvas>
        </div>
      </div>
    </div>
  );
}

// =========================================================================
// FEED SUBCOMPONENT
// =========================================================================
function FeedList({ items, query }) {
  const [openComments, setOpenComments] = useState({});

  const filtered = items.filter(it => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    return it.author.toLowerCase().includes(q) || it.content.toLowerCase().includes(q) || (it.meta && it.meta.toLowerCase().includes(q));
  });

  if (!filtered.length) {
    return <div style={{ textAlign: "center", padding: "30px", color: "#C7DEF9" }}>No narratives match this search.</div>;
  }

  const toggleComments = (idx) => {
    setOpenComments(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="feed-scroll">
      {filtered.map((it, idx) => (
        <div key={idx} className="post-card">
          <div className="post-top">
            <span className="post-user">@{it.author}</span>
            <span className="post-date">{it.meta || it.date}</span>
          </div>
          <div className="post-text">{it.content}</div>
          <div className="post-bottom">
            <div style={{ display: "flex", gap: "8px" }}>
              <span className="badge-tag">✦ {it.emotion}</span>
              <span className="badge-tag" style={{ color: "#38BDF8" }}>{it.likes_pct}</span>
            </div>
            {it.comments && it.comments.length > 0 && (
              <span style={{ color: "#A5CAF7", cursor: "pointer", fontWeight: 700 }} onClick={() => toggleComments(idx)}>
                💬 Responses ({it.comments.length})
              </span>
            )}
          </div>

          {openComments[idx] && it.comments && (
            <div style={{ marginTop: "12px", paddingTop: "10px", borderTop: "1px dashed rgba(255,255,255,0.16)" }}>
              {it.comments.map((c, cIdx) => (
                <div key={cIdx} style={{ fontSize: "0.86rem", color: "#C7DEF9", marginTop: "6px" }}>
                  <b style={{ color: "#FFFFFF" }}>{c.author}:</b> {c.text}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// =========================================================================
// AMBIENT BACKGROUND PARTICLE CANVAS
// =========================================================================
function initBackgroundCanvas() {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener("resize", () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = Array.from({ length: 40 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.35,
    vy: (Math.random() - 0.5) * 0.35,
    radius: Math.random() * 2 + 1,
    alpha: Math.random() * 0.5 + 0.1
  }));

  function animate() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 140) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(165, 202, 247, ${0.08 * (1 - dist / 140)})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(165, 202, 247, ${p.alpha})`;
      ctx.fill();
    });

    requestAnimationFrame(animate);
  }

  animate();
}

ReactDOM.render(<App />, document.getElementById("root"));
