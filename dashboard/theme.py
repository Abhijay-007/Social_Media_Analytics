"""
Theme: Emerald Ink & Champagne · Illustrative Design
Custom CSS and Plotly chart builders for the Social Analytics Observatory.
"""

import plotly.graph_objects as go
from typing import Dict, List, Tuple

# Palette Constants
EMERALD_INK = "#0B3B2C"
EMERALD_DARK = "#062A1F"
EMERALD_MID = "#0D5C45"
EMERALD_VIBRANT = "#10B981"
CHAMPAGNE_BG = "#FAF6ED"
CHAMPAGNE_CARD = "#F3EBD9"
CHAMPAGNE_BORDER = "#DFCBB0"
CHAMPAGNE_GOLD = "#D4AF37"
CHAMPAGNE_DARK = "#8C6A24"
TEXT_INK = "#07241A"

ILLUSTRATIVE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

.gradio-container {
    background-color: #FAF6ED !important;
    background-image: 
        radial-gradient(#D4AF37 0.75px, transparent 0.75px), 
        radial-gradient(#0B3B2C 0.75px, #FAF6ED 0.75px) !important;
    background-size: 28px 28px !important;
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    color: #07241A !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* Hero Banner */
.hero-banner {
    background: linear-gradient(135deg, #062A1F 0%, #0B3B2C 55%, #125E47 100%);
    border: 2px solid #D4AF37;
    border-radius: 20px;
    padding: 30px 36px;
    color: #FAF6ED;
    position: relative;
    box-shadow: 0 12px 28px rgba(7,36,26,0.18), inset 0 0 0 1px rgba(212,175,55,0.4);
    margin-bottom: 24px;
}
.hero-banner h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.2rem;
    color: #FAF6ED !important;
    margin: 4px 0 6px 0;
}
.hero-subtitle {
    font-family: 'Cinzel', serif;
    color: #D4AF37;
    font-size: 0.85rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
.hero-desc {
    color: #E2D7C5;
    font-size: 0.98rem;
    margin: 0;
    max-width: 80%;
}

/* Platform Cards Grid */
.platform-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 18px;
    margin-bottom: 24px;
}
.platform-card {
    background: #F3EBD9;
    border: 2px solid #0B3B2C;
    border-radius: 16px;
    padding: 24px 18px;
    text-align: center;
    box-shadow: 4px 5px 0px #0B3B2C;
    transition: all 0.2s ease;
}
.platform-card:hover {
    transform: translateY(-4px);
    box-shadow: 6px 8px 0px #0B3B2C;
    background: #EFE4CE;
}
.platform-card-icon {
    font-size: 2.8rem;
    margin-bottom: 10px;
    display: block;
}
.platform-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #07241A;
    margin-bottom: 4px;
}
.platform-card-tag {
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    color: #8C6A24;
    letter-spacing: 0.08em;
}

/* KPI Ledger Boxes */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
.kpi-card {
    background: #F3EBD9;
    border: 2px solid #0B3B2C;
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    box-shadow: 3px 4px 0px #0B3B2C;
}
.kpi-val {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #0B3B2C;
    margin-bottom: 2px;
}
.kpi-lbl {
    font-family: 'Cinzel', serif;
    font-size: 0.74rem;
    color: #8C6A24;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Feed Cards */
.story-card {
    background: #FAF6ED;
    border: 2px solid #0B3B2C;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 3px 4px 0px #0B3B2C;
}
.story-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px dashed #DFCBB0;
    padding-bottom: 8px;
    margin-bottom: 10px;
}
.story-author {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #07241A;
}
.story-meta {
    font-size: 0.8rem;
    color: #8C6A24;
}
.story-body {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #0E3529;
    margin-bottom: 12px;
}

/* Badges */
.badge-wax {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 14px;
    font-family: 'Cinzel', serif;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-pos { background: #E2F6EE; color: #086146; border: 1.5px solid #10B981; }
.badge-neu { background: #FDF5E3; color: #8A641A; border: 1.5px solid #D4AF37; }
.badge-neg { background: #FDE8E8; color: #991B1B; border: 1.5px solid #EF4444; }
.badge-tag { background: #EFE4CE; color: #0B3B2C; border: 1px solid #D4AF37; padding: 2px 7px; border-radius: 6px; font-size: 0.75rem; }

/* Tabs & UI Elements */
div[role="tablist"] {
    background: #F3EBD9 !important;
    border: 2px solid #DFCBB0 !important;
    border-radius: 14px !important;
    padding: 5px !important;
}
button[role="tab"] {
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    color: #0B3B2C !important;
    border-radius: 10px !important;
}
button[role="tab"][aria-selected="true"] {
    background: #0B3B2C !important;
    color: #FAF6ED !important;
    box-shadow: 2px 3px 0px #D4AF37 !important;
}
button.primary {
    background: #0B3B2C !important;
    color: #FAF6ED !important;
    border: 2px solid #D4AF37 !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    box-shadow: 3px 4px 0px #062A1F !important;
}
.gradio-dataframe {
    border: 2px solid #0B3B2C !important;
    border-radius: 14px !important;
    box-shadow: 3px 4px 0px #0B3B2C !important;
    background: #F3EBD9 !important;
}
.gradio-dataframe th {
    background: #0B3B2C !important;
    color: #FAF6ED !important;
    font-family: 'Cinzel', serif !important;
}
"""

def plot_sentiment_donut(pos: int, neu: int, neg: int, title: str) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=["Positive", "Neutral", "Negative"],
        values=[pos, neu, neg],
        hole=0.55,
        marker=dict(
            colors=["#10B981", "#D4AF37", "#B91C1C"],
            line=dict(color="#062A1F", width=2),
        ),
        textinfo="label+percent",
        textfont=dict(family="Cinzel, serif", size=12, color="#07241A"),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title} — Sentiment</b>", font=dict(family="Playfair Display, serif", size=16, color="#07241A"), x=0.5),
        paper_bgcolor="#F3EBD9", plot_bgcolor="#F3EBD9",
        legend=dict(font=dict(color="#07241A", size=11), orientation="h", y=-0.12, x=0.5, xanchor="center"),
        margin=dict(t=50, b=30, l=20, r=20),
    )
    return fig

def plot_top_bars(items: List[Tuple[str, int]], title: str, x_label: str) -> go.Figure:
    if not items:
        items = [("No data", 0)]
    labels = [i[0] for i in items][::-1]
    counts = [i[1] for i in items][::-1]
    fig = go.Figure(go.Bar(
        y=labels, x=counts, orientation="h",
        marker=dict(color="#0B3B2C", line=dict(color="#D4AF37", width=1.5)),
        text=counts, textposition="outside", textfont=dict(color="#07241A", size=11),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(family="Playfair Display, serif", size=16, color="#07241A"), x=0.5),
        paper_bgcolor="#F3EBD9", plot_bgcolor="#F3EBD9",
        xaxis=dict(gridcolor="#E4D5C0", tickfont=dict(color="#07241A"), title=dict(text=x_label, font=dict(family="Cinzel", size=11))),
        yaxis=dict(tickfont=dict(color="#07241A", size=11)),
        margin=dict(t=50, b=30, l=110, r=30),
    )
    return fig
