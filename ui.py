import streamlit as st
import pandas as pd
from agent import get_stock_data, get_technical_indicators, get_market_intelligence

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SENTINEL · Market Intelligence",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #080b0f !important;
    color: #c8d0d8 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #0d1117 !important; }
[data-testid="stMainBlockContainer"] { padding: 2rem 3rem !important; max-width: 1400px; margin: 0 auto; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 2px; }

/* ── Top masthead ── */
.masthead {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1a2535;
    padding-bottom: 1.2rem;
    margin-bottom: 2rem;
}
.masthead-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: 0.35em;
    color: #e8f4fd;
    text-transform: uppercase;
}
.masthead-logo span { color: #00d4ff; }
.masthead-tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #3a5070;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* ── Search bar ── */
[data-testid="stTextInput"] > div > div {
    background: #0d1117 !important;
    border: 1px solid #1a2535 !important;
    border-radius: 3px !important;
    color: #e8f4fd !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 1px #00d4ff22 !important;
}
[data-testid="stTextInput"] input {
    color: #e8f4fd !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stTextInput"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    color: #3a5070 !important;
    text-transform: uppercase !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button {
    background: transparent !important;
    border: 1px solid #00d4ff !important;
    color: #00d4ff !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    background: #00d4ff18 !important;
    box-shadow: 0 0 20px #00d4ff22 !important;
}

/* ── Section headers ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #3a5070;
    margin-bottom: 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1a2535;
}

/* ── Ticker hero ── */
.ticker-hero {
    background: #0d1117;
    border: 1px solid #1a2535;
    border-left: 3px solid #00d4ff;
    padding: 1.4rem 1.8rem;
    border-radius: 3px;
    margin-bottom: 1.5rem;
}
.ticker-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #e8f4fd;
    letter-spacing: 0.05em;
}
.ticker-country {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #3a5070;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.ticker-price {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem;
    font-weight: 300;
    color: #00d4ff;
    margin-top: 0.8rem;
    letter-spacing: -0.01em;
}
.ticker-price-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #3a5070;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* ── Intel card ── */
.intel-card {
    background: #0d1117;
    border: 1px solid #1a2535;
    padding: 1.4rem 1.8rem;
    border-radius: 3px;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.intel-card::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 60px; height: 60px;
    background: radial-gradient(circle at top right, #00d4ff08, transparent 70%);
}
.intel-summary {
    font-size: 0.85rem;
    line-height: 1.7;
    color: #8fa8c0;
    margin-bottom: 1rem;
}
.sentiment-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 2px;
    font-weight: 500;
}
.sentiment-Bullish  { background: #0d2b1a; color: #00c853; border: 1px solid #00c85340; }
.sentiment-Bearish  { background: #2b0d0d; color: #ff1744; border: 1px solid #ff174440; }
.sentiment-Neutral  { background: #1a1a2b; color: #7986cb; border: 1px solid #7986cb40; }

/* ── Stat cards ── */
.stat-card {
    background: #0d1117;
    border: 1px solid #1a2535;
    padding: 1.2rem 1.4rem;
    border-radius: 3px;
    text-align: center;
}
.stat-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3a5070;
    margin-bottom: 0.5rem;
}
.stat-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: #e8f4fd;
}
.stat-hint {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.7rem;
    color: #3a5070;
    line-height: 1.4;
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px solid #1a2535;
    text-align: left;
}
.stat-hint b { color: #5a7a95; font-weight: 500; }
.benchmark-bar {
    height: 3px;
    background: #1a2535;
    border-radius: 2px;
    margin-top: 0.5rem;
    position: relative;
}
.benchmark-fill { height: 100%; border-radius: 2px; }
.benchmark-labels {
    display: flex;
    justify-content: space-between;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem;
    color: #2a3a4a;
    margin-top: 0.25rem;
}
.stat-rec {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.rec-Bullish { color: #00c853; }
.rec-Bearish { color: #ff1744; }
.rec-Neutral { color: #7986cb; }

/* ── Chart container ── */
.chart-container {
    background: #0d1117;
    border: 1px solid #1a2535;
    border-radius: 3px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.5rem;
}

/* ── Override Streamlit chart bg ── */
[data-testid="stVegaLiteChart"] { background: transparent !important; }
.stVegaLiteChart > div { background: transparent !important; }

/* ── News cards ── */
.news-card {
    background: #0d1117;
    border: 1px solid #1a2535;
    border-radius: 3px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s;
    cursor: pointer;
}
.news-card:hover { border-color: #00d4ff44; }
.news-title {
    font-size: 0.85rem;
    color: #c8d0d8;
    margin-bottom: 0.4rem;
    line-height: 1.4;
}
.news-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: #3a5070;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.news-link {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #00d4ff;
    text-decoration: none;
    letter-spacing: 0.1em;
}

/* ── Divider ── */
.term-divider {
    border: none;
    border-top: 1px solid #1a2535;
    margin: 2rem 0;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #00d4ff !important; }

/* ── Metrics override (hide default streamlit metrics) ── */
[data-testid="stMetric"] { display: none; }

/* ── Info / warning boxes ── */
[data-testid="stAlert"] {
    background: #0d1117 !important;
    border: 1px solid #1a2535 !important;
    color: #3a5070 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    border-radius: 3px !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
}
.empty-state-symbol {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3rem;
    color: #1a2535;
    margin-bottom: 1rem;
}
.empty-state-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #3a5070;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* ── Scanline overlay ── */
body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def section(label: str):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)


def stat_card(label, value, hint="", benchmark_pct=-1, bar_color="#00d4ff"):
    bar_html = ""
    if hint and 0 <= benchmark_pct <= 100:
        bar_html = (
            '<div class="benchmark-bar">'
            f'<div class="benchmark-fill" style="width:{benchmark_pct:.0f}%;background:{bar_color}"></div>'
            '</div>'
            '<div class="benchmark-labels"><span>0</span><span>50</span><span>100</span></div>'
        )
    hint_html = f'<div class="stat-hint">{hint}{bar_html}</div>' if hint else ""
    return (
        '<div class="stat-card">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div>'
        f'{hint_html}'
        '</div>'
    )


# ── Masthead ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
    <div>
        <div class="masthead-logo">SENTINEL<span>▲</span></div>
        <div class="masthead-tagline">Market Intelligence Terminal</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Search row ────────────────────────────────────────────────────────────────
col_input, col_btn, col_spacer = st.columns([4, 1, 5])
with col_input:
    query = st.text_input("TICKER / COMPANY", value="Reliance", label_visibility="visible")
with col_btn:
    st.markdown("<div style='margin-top:1.75rem'></div>", unsafe_allow_html=True)
    run = st.button("QUERY ▶", type="primary", use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────
if run:
    with st.spinner("FETCHING MARKET DATA..."):
        try:
            price, df, forecast, currency, country, news = get_stock_data(query)
            df   = df   if isinstance(df,   pd.DataFrame) else pd.DataFrame()
            news = news if isinstance(news, list)         else []
            intel = get_market_intelligence(query)
            tech  = get_technical_indicators(df)

        except Exception as e:
            st.error(f"TERMINAL ERROR · {e}")
            st.exception(e)
            st.stop()

    # ── Hero row ──────────────────────────────────────────────────────────────
    col_hero, col_intel = st.columns([2, 3])

    with col_hero:
        price_display = f"{currency} {price:,.2f}" if price > 0 else "N/A"
        st.markdown(f"""
        <div class="ticker-hero">
            <div class="ticker-name">{query.upper()}</div>
            <div class="ticker-country">{country} · LIVE QUOTE</div>
            <div class="ticker-price-label" style="margin-top:1rem">CURRENT PRICE</div>
            <div class="ticker-price">{price_display}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_intel:
        sentiment  = intel.get('sentiment', 'Neutral')
        summary    = intel.get('summary', '')
        st.markdown(f"""
        <div class="intel-card">
            <div class="section-label" style="margin-bottom:0.8rem">▲ AI OUTLOOK</div>
            <div class="intel-summary">{summary}</div>
            <span class="sentiment-badge sentiment-{sentiment}">● {sentiment}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="term-divider">', unsafe_allow_html=True)

    # ── Technical indicators ──────────────────────────────────────────────────
    section("TECHNICAL INDICATORS")
    rec = tech['recommendation']
    c1, c2, c3, c4 = st.columns(4)

    rsi_val = tech["rsi"]
    try:
        rsi_num = float(rsi_val)
        rsi_pct   = rsi_num
        rsi_color = "#ff1744" if rsi_num > 70 else "#00c853" if rsi_num < 30 else "#00d4ff"
    except (ValueError, TypeError):
        rsi_pct, rsi_color = -1, "#00d4ff"

    with c1:
        st.markdown(stat_card(
            "RSI · 14", rsi_val,
            hint="<b>Relative Strength Index.</b> Momentum gauge 0–100. Below 30 = oversold (potential buy). Above 70 = overbought (potential sell). Ideal zone: 40–60.",
            benchmark_pct=rsi_pct, bar_color=rsi_color,
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card(
            "SMA · 50", tech["sma_50"],
            hint="<b>50-day moving average.</b> Short-term trend. If current price is above this, momentum is bullish. Below it = near-term weakness.",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_card(
            "SMA · 200", tech["sma_200"],
            hint="<b>200-day moving average.</b> The long-game benchmark. Price above SMA 200 = healthy uptrend. Below it = structural caution.",
        ), unsafe_allow_html=True)
    with c4:
        signal_hint = {"Bullish": "RSI is low — stock may be undervalued with room to grow.", "Bearish": "RSI is high — stock may be overheated, consider waiting.", "Neutral": "RSI is in mid-range — no strong signal either way."}.get(rec, "")
        st.markdown(
            '<div class="stat-card">' +
            '<div class="stat-label">SIGNAL</div>' +
            f'<div class="stat-value rec-{rec}">{rec.upper()}</div>' +
            f'<div class="stat-hint"><b>Overall read:</b> {signal_hint}</div>' +
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr class="term-divider">', unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        section("1-YEAR PRICE HISTORY")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if not df.empty and 'Close' in df.columns and 'Date' in df.columns:
            st.line_chart(
                df.set_index('Date')['Close'],
                color="#00d4ff",
                height=260,
                use_container_width=True,
            )
        else:
            st.markdown('<div style="color:#3a5070;font-family:IBM Plex Mono;font-size:0.75rem;padding:2rem;text-align:center">NO DATA AVAILABLE</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart2:
        section("30-DAY FORECAST · PROPHET MODEL")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if forecast is not None and not forecast.empty and 'ds' in forecast.columns:
            chart_df = forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']]
            chart_df.columns = ['Forecast', 'Lower Bound', 'Upper Bound']
            st.line_chart(
                chart_df,
                color=["#00d4ff", "#1a3a4a", "#1a3a4a"],
                height=260,
                use_container_width=True,
            )
        else:
            st.markdown('<div style="color:#3a5070;font-family:IBM Plex Mono;font-size:0.75rem;padding:2rem;text-align:center">INSUFFICIENT HISTORICAL DATA</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="term-divider">', unsafe_allow_html=True)

    # ── News feed ─────────────────────────────────────────────────────────────
    section("LATEST INTELLIGENCE FEED")
    if news:
        for item in news[:5]:
            title     = item.get('title') or 'Untitled'
            publisher = item.get('publisher', 'UNKNOWN SOURCE').upper()
            link      = item.get('link', '')
            link_html = f'<a class="news-link" href="{link}" target="_blank">READ FULL REPORT →</a>' if link else ''
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{title}</div>
                <div class="news-meta">{publisher}</div>
                {link_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#3a5070;font-family:IBM Plex Mono;font-size:0.75rem;padding:1rem">NO INTELLIGENCE AVAILABLE</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <hr class="term-divider">
    <div style="font-family:IBM Plex Mono;font-size:0.6rem;color:#1a2535;letter-spacing:0.15em;text-align:center;padding-bottom:1rem">
        SENTINEL · FOR INFORMATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-symbol">▲</div>
        <div class="empty-state-text">Enter a ticker or company name to initialize</div>
    </div>
    """, unsafe_allow_html=True)