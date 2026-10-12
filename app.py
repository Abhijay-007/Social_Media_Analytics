"""
Social Media Analysis Observatory
Emerald Ink & Champagne · Illustrative Multi-Platform Dashboard
"""

import html
import gradio as gr
import pandas as pd
import torch
from transformers import pipeline

from dashboard.data_loader import PlatformDataManager, PLATFORMS, _fmt_ts
from dashboard.theme import (
    ILLUSTRATIVE_CSS,
    plot_sentiment_donut,
    plot_top_bars,
)

dm = PlatformDataManager()

# Lazy NLP Pipeline Cache
_nlp_sentiment = None
_nlp_emotion = None

def get_pipelines():
    global _nlp_sentiment, _nlp_emotion
    if _nlp_sentiment is None:
        device = 0 if torch.cuda.is_available() else -1
        try:
            _nlp_sentiment = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=device,
                truncation=True,
            )
            _nlp_emotion = pipeline(
                "text-classification",
                model="SamLowe/roberta-base-go_emotions",
                tokenizer="SamLowe/roberta-base-go_emotions",
                top_k=3,
                device=device,
                truncation=True,
            )
        except Exception as e:
            print(f"Model load notice: {e}")
    return _nlp_sentiment, _nlp_emotion

# ── HTML Renderers ───────────────────────────────────────────────────

def render_landing_page() -> str:
    """Renders the front-page platform catalog without post count numbers."""
    cards = []
    platform_keys = ["telegram", "x", "reddit", "youtube", "instagram", "facebook"]
    for k in platform_keys:
        p = PLATFORMS[k]
        cards.append(f"""
        <div class="platform-card">
            <span class="platform-card-icon">{p['icon']}</span>
            <div class="platform-card-title">{p['label']}</div>
            <div class="platform-card-tag">{p['tagline']}</div>
        </div>
        """)
    
    return f"""
    <div class="hero-banner">
        <div class="hero-subtitle">✦ Multi-Channel Intelligence ✦</div>
        <h1>Social Media Analysis Observatory</h1>
        <p class="hero-desc">
            Explore sentiment polarity, emotional resonance, author dynamics, and narrative themes across 6 major social platforms.
        </p>
    </div>
    <div class="platform-grid">{''.join(cards)}</div>
    """

def render_header(plat: str) -> str:
    p = PLATFORMS.get(plat, PLATFORMS["all"])
    return f"""
    <div class="hero-banner">
        <div class="hero-subtitle">✦ Platform Intelligence Report ✦</div>
        <h1>{p['icon']} {p['label']}</h1>
        <p class="hero-desc">{p['tagline']}</p>
    </div>
    """

def render_kpis(plat: str) -> str:
    s = dm.get_summary(plat)
    cards = [
        f'<div class="kpi-card"><div class="kpi-val">{s["total_items"]:,}</div><div class="kpi-lbl">{s.get("item_type", "Items")}</div></div>',
        f'<div class="kpi-card"><div class="kpi-val">{s["unique_voices"]}</div><div class="kpi-lbl">Active Voices</div></div>',
    ]
    if "comments" in s:
        cards.append(f'<div class="kpi-card"><div class="kpi-val">{s["comments"]:,}</div><div class="kpi-lbl">Comments</div></div>')
    if "engagements" in s:
        cards.append(f'<div class="kpi-card"><div class="kpi-val">{s["engagements"]:,}</div><div class="kpi-lbl">Engagements</div></div>')
    if "channels" in s:
        cards.append(f'<div class="kpi-card"><div class="kpi-val">{s["channels"]}</div><div class="kpi-lbl">Guild Channels</div></div>')

    pos = s.get("pos", 0)
    total = pos + s.get("neu", 0) + s.get("neg", 0)
    pos_pct = round(pos / total * 100, 1) if total else 0.0
    cards.append(f'<div class="kpi-card"><div class="kpi-val" style="color:#0E7A53;">{pos_pct}%</div><div class="kpi-lbl">Positivity Index</div></div>')

    return f'<div class="kpi-row">{"".join(cards)}</div>'

def render_feed(plat: str, search: str = "") -> str:
    q = (search or "").lower().strip()
    if plat == "telegram":
        msgs = dm.chats
        if q:
            msgs = [m for m in msgs if q in m.get("text", "").lower() or q in m.get("author", "").lower()]
        cards = []
        for m in msgs[:30]:
            author = html.escape(m.get("author", "Anonymous"))
            text = html.escape(m.get("text", ""))
            room = html.escape(m.get("room_name", "Global"))
            ts = m.get("timestamp", "")[:16].replace("T", " ")
            cards.append(f"""
            <div class="story-card">
                <div class="story-header">
                    <div class="story-author">✈️ {author}</div>
                    <div class="story-meta">#{room} • {ts}</div>
                </div>
                <div class="story-body">{text}</div>
            </div>
            """)
        return "".join(cards) if cards else "<p style='color:#8C6A24; text-align:center;'>No messages match criteria.</p>"

    posts = dm.posts if plat == "all" else dm.platform_posts.get(plat, [])
    if q:
        posts = [p for p in posts if q in (p.get("description") or "").lower() or q in (p.get("author_name") or "").lower()]

    cards = []
    for p in posts[:25]:
        pid = p.get("post_id", "")
        author = html.escape(p.get("author_name") or p.get("author_id", "Anonymous"))
        content = html.escape(p.get("description", ""))
        nlp = dm.enriched_map.get(pid, {})
        sent = (nlp.get("sentiment") or "neutral").lower()
        emo = (nlp.get("emotion") or "neutral").capitalize()
        date_str = _fmt_ts(p.get("created_at"))
        
        badge_cls = "badge-pos" if sent == "positive" else ("badge-neg" if sent == "negative" else "badge-neu")
        icon = "🌿" if sent == "positive" else ("⚖️" if sent == "neutral" else "🍂")
        
        tags_html = "".join(f'<span class="badge-tag">#{html.escape(t)}</span> ' for t in (p.get("hashtags") or []))
        likes = len(p.get("liked_by") or [])
        comments = p.get("comments") or []

        comments_drawer = ""
        if comments:
            comments_drawer = f"""
            <details style="margin-top:10px; background:#F3EBD9; border:1px solid #DFCBB0; border-radius:10px; padding:8px 12px; cursor:pointer;">
                <summary style="font-family:'Cinzel', serif; font-weight:700; font-size:0.8rem; color:#0B3B2C;">
                    💬 {len(comments)} Recorded Community Responses
                </summary>
                <div style="margin-top:8px; display:flex; flex-direction:column; gap:6px;">
            """
            for c in comments[:4]:
                c_author = html.escape(c.get("authorName") or c.get("authorId", "Anonymous"))
                c_text = html.escape(c.get("text", ""))
                comments_drawer += f"""
                    <div style="background:#FAF6ED; border-left:3px solid #D4AF37; padding:6px 10px; border-radius:4px 8px 8px 4px; font-size:0.85rem;">
                        <b>{c_author}</b>: {c_text}
                    </div>
                """
            comments_drawer += "</div></details>"

        cards.append(f"""
        <div class="story-card">
            <div class="story-header">
                <div class="story-author">❦ {author}</div>
                <div class="story-meta">{date_str}</div>
            </div>
            <div class="story-body">{content}</div>
            {f'<div style="margin-bottom:10px;">{tags_html}</div>' if tags_html else ''}
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed #DFCBB0; padding-top:10px;">
                <div style="display:flex; gap:8px;">
                    <span class="badge-wax {badge_cls}">{icon} {sent.upper()}</span>
                    <span class="badge-wax" style="background:#0B3B2C; color:#FAF6ED; border:1px solid #D4AF37;">✨ {emo}</span>
                </div>
                <div style="color:#8C6A24; font-size:0.82rem; font-weight:600;">❤️ {likes} Likes • 💬 {len(comments)} Comments</div>
            </div>
            {comments_drawer}
        </div>
        """)

    return "".join(cards) if cards else "<p style='color:#8C6A24; text-align:center;'>No stories found matching your filter.</p>"

def run_live_nlp(text: str):
    if not text or not text.strip():
        return "<p style='color:#8C6A24;'>Please inscribe text for evaluation.</p>", {}, {}
    
    sent_pipe, emo_pipe = get_pipelines()
    sent_label = "Neutral"
    sent_conf = 0.5
    sent_dict = {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
    emo_dict = {}

    if sent_pipe:
        try:
            res = sent_pipe(text)[0]
            raw = res["label"].lower()
            sent_conf = res["score"]
            sent_label = "Positive" if "pos" in raw else ("Negative" if "neg" in raw else "Neutral")
            sent_dict = {
                "positive": sent_conf if sent_label == "Positive" else (1 - sent_conf) / 2,
                "neutral": sent_conf if sent_label == "Neutral" else (1 - sent_conf) / 2,
                "negative": sent_conf if sent_label == "Negative" else (1 - sent_conf) / 2,
            }
        except Exception as e:
            print(f"Sentiment error: {e}")

    if emo_pipe:
        try:
            emo_res = emo_pipe(text)[0]
            emo_dict = {item["label"].capitalize(): round(item["score"], 3) for item in emo_res}
        except Exception as e:
            print(f"Emotion error: {e}")

    badge = "badge-pos" if sent_label == "Positive" else ("badge-neu" if sent_label == "Neutral" else "badge-neg")
    icon = "🌿" if sent_label == "Positive" else ("⚖️" if sent_label == "Neutral" else "🍂")
    
    summary = f"""
    <div style="background:#F3EBD9; border:2px solid #0B3B2C; border-radius:14px; padding:18px; box-shadow:3px 4px 0px #0B3B2C;">
        <div style="font-family:'Cinzel', serif; color:#8C6A24; font-size:0.8rem; margin-bottom:4px;">✦ Divined Evaluation ✦</div>
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <span class="badge-wax {badge}" style="font-size:0.95rem; padding:6px 14px;">{icon} {sent_label.upper()}</span>
            <span style="font-family:'Playfair Display'; font-size:1.1rem; color:#07241A;">Confidence: <b>{int(sent_conf*100)}%</b></span>
        </div>
        <p style="font-size:0.88rem; color:#0E3529; margin:0;"><b>Input:</b> <i>"{html.escape(text)}"</i></p>
    </div>
    """
    return summary, sent_dict, emo_dict

# ── App Builder ──────────────────────────────────────────────────────

def build_app():
    platform_choices = [
        ("🌟 All Channels (Global)", "all"),
        ("✈️ Telegram", "telegram"),
        ("𝕏  X (Twitter)", "x"),
        ("🤖 Reddit", "reddit"),
        ("▶️ YouTube", "youtube"),
        ("📸 Instagram", "instagram"),
        ("📘 Facebook", "facebook"),
    ]

    with gr.Blocks(title="Social Media Analysis Observatory") as app:
        current_plat = gr.State(value="landing")

        # ── LANDING VIEW ──────────────────────────────────────────────
        with gr.Group(visible=True) as view_landing:
            gr.HTML(render_landing_page())
            
            gr.HTML('<div style="text-align:center; font-family:Cinzel,serif; color:#8C6A24; margin:10px 0 16px; font-weight:700;">— CLICK A CHANNEL TO ENTER ANALYSIS —</div>')
            with gr.Row():
                btn_all = gr.Button("🌟 Global Observatory", variant="primary", size="lg")
                btn_tg = gr.Button("✈️ Telegram", variant="secondary", size="lg")
                btn_x = gr.Button("𝕏  X (Twitter)", variant="secondary", size="lg")
                btn_rd = gr.Button("🤖 Reddit", variant="secondary", size="lg")
                btn_yt = gr.Button("▶️ YouTube", variant="secondary", size="lg")
                btn_ig = gr.Button("📸 Instagram", variant="secondary", size="lg")
                btn_fb = gr.Button("📘 Facebook", variant="secondary", size="lg")

        # ── PLATFORM DETAIL VIEW ──────────────────────────────────────
        with gr.Group(visible=False) as view_detail:
            with gr.Row():
                btn_back = gr.Button("← Return to All Channels Catalog", variant="secondary", scale=1)
                plat_dropdown = gr.Dropdown(
                    label="⚡ Switch Channel / Platform",
                    choices=platform_choices,
                    value="all",
                    scale=2,
                )

            header_html = gr.HTML()
            kpi_html = gr.HTML()

            with gr.Tabs():
                with gr.Tab("🏛️ Observatory Overview"):
                    with gr.Row():
                        plot_sent = gr.Plot(show_label=False)
                        plot_authors = gr.Plot(show_label=False)
                    plot_tags = gr.Plot(show_label=False)

                with gr.Tab("📜 Chronicle Feed"):
                    feed_search = gr.Textbox(label="🔍 Filter by author, hashtag, or keyword", placeholder="Type keywords...")
                    feed_html = gr.HTML()
                    feed_search.change(fn=render_feed, inputs=[current_plat, feed_search], outputs=feed_html)

                with gr.Tab("🗃️ Tabular Vault"):
                    table_view = gr.Dataframe(interactive=False, wrap=True)

                with gr.Tab("🧪 Sentiment & Emotion Alchemist"):
                    gr.HTML("<div style='font-family:Cinzel,serif; color:#8C6A24; font-size:0.85rem; margin-bottom:8px;'>✦ Real-time Neural Text Inspector ✦</div>")
                    with gr.Row():
                        with gr.Column(scale=1):
                            alch_in = gr.Textbox(
                                label="🖋️ Inscribe Text to Analyze",
                                placeholder="Type any sentence or social commentary...",
                                lines=3,
                                value="Ruturaj Gaikwad back in the India mix is a massive win! Effortless timing and calm temperament.",
                            )
                            alch_btn = gr.Button("⚡ Analyze Sentiment & Emotion", variant="primary")
                        with gr.Column(scale=1):
                            alch_out_summary = gr.HTML("<p style='color:#8C6A24;'>Click analyze to divine sentiment.</p>")
                            alch_out_sent = gr.Label(label="🌿 Sentiment Meter", num_top_classes=3)
                            alch_out_emo = gr.Label(label="✨ Emotion Meter", num_top_classes=3)
                    
                    alch_btn.click(
                        fn=run_live_nlp,
                        inputs=alch_in,
                        outputs=[alch_out_summary, alch_out_sent, alch_out_emo],
                    )

        # ── Navigation Wire ───────────────────────────────────────────
        def show_platform(plat_key):
            s = dm.get_summary(plat_key)
            label = PLATFORMS.get(plat_key, PLATFORMS["all"])["label"]
            hdr = render_header(plat_key)
            kpis = render_kpis(plat_key)
            donut = plot_sentiment_donut(s["pos"], s["neu"], s["neg"], label)
            authors = plot_top_bars(dm.get_top_authors(plat_key), f"Top Influencers ({label})", "Publications")
            tags = plot_top_bars(dm.get_top_hashtags(plat_key), f"Trending Hashtags ({label})", "Mentions")
            feed = render_feed(plat_key, "")
            df = dm.get_posts_df(plat_key)
            return (
                gr.update(visible=False), # landing
                gr.update(visible=True),  # detail
                plat_key,                 # state
                plat_key,                 # dropdown
                hdr, kpis, donut, authors, tags, feed, df,
            )

        def go_landing():
            return gr.update(visible=True), gr.update(visible=False), "landing"

        btn_all.click(fn=lambda: show_platform("all"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_tg.click(fn=lambda: show_platform("telegram"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_x.click(fn=lambda: show_platform("x"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_rd.click(fn=lambda: show_platform("reddit"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_yt.click(fn=lambda: show_platform("youtube"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_ig.click(fn=lambda: show_platform("instagram"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_fb.click(fn=lambda: show_platform("facebook"), outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])

        plat_dropdown.change(fn=show_platform, inputs=plat_dropdown, outputs=[view_landing, view_detail, current_plat, plat_dropdown, header_html, kpi_html, plot_sent, plot_authors, plot_tags, feed_html, table_view])
        btn_back.click(fn=go_landing, outputs=[view_landing, view_detail, current_plat])

    return app

if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860, css=ILLUSTRATIVE_CSS)
