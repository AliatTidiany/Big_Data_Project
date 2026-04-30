"""
Bookshop Analytics — Advanced Dashboard
Stack : Streamlit · Snowflake · Plotly · Pandas
"""

import os
import textwrap
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import snowflake.connector
from snowflake.connector import ProgrammingError


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bookshop Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# GLOBAL THEME  (dark, monochrome-accent)
# ─────────────────────────────────────────────
PALETTE = {
    "bg":          "#0d0f14",
    "surface":     "#161a22",
    "border":      "#252b38",
    "text":        "#e4e8f0",
    "muted":       "#6b7590",
    "accent":      "#4f8ef7",
    "green":       "#27d9a2",
    "amber":       "#f5a623",
    "red":         "#e05555",
}

st.markdown(f"""
<style>
    /* ── root ── */
    html, body, [class*="css"] {{
        font-family: 'DM Mono', 'Courier New', monospace;
    }}

    /* force dark bg only on main canvas and sidebar */
    .main, [data-testid="stAppViewContainer"] {{
        background-color: {PALETTE['bg']};
    }}

    /* ── sidebar ── */
    section[data-testid="stSidebar"] {{
        background-color: {PALETTE['surface']};
        border-right: 1px solid {PALETTE['border']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {PALETTE['text']} !important;
    }}

    /* ── main container ── */
    .main .block-container {{
        padding: 2rem 3rem;
        max-width: 1600px;
    }}

    /* ── metric card ── */
    .kpi-card {{
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 6px;
        padding: 24px 28px;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: var(--accent-color, {PALETTE['accent']});
    }}
    .kpi-label {{
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {PALETTE['muted']};
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        color: {PALETTE['text']};
        line-height: 1;
    }}
    .kpi-delta {{
        font-size: 12px;
        margin-top: 6px;
    }}
    .kpi-delta.pos {{ color: {PALETTE['green']}; }}
    .kpi-delta.neg {{ color: {PALETTE['red']}; }}

    /* ── section header ── */
    .section-header {{
        font-size: 11px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {PALETTE['muted']};
        border-bottom: 1px solid {PALETTE['border']};
        padding-bottom: 8px;
        margin-bottom: 18px;
        margin-top: 32px;
    }}

    /* ── page banner (self-contained, always dark) ── */
    .page-banner {{
        position: relative;
        background: linear-gradient(135deg, #0a0e18 0%, #111827 50%, #0d1520 100%);
        border: 1px solid {PALETTE['border']};
        border-radius: 10px;
        padding: 36px 44px;
        overflow: hidden;
        margin-bottom: 32px;
    }}

    /* dot-grid background pattern */
    .page-banner::before {{
        content: '';
        position: absolute;
        inset: 0;
        background-image: radial-gradient(circle, rgba(79,142,247,0.18) 1px, transparent 1px);
        background-size: 28px 28px;
        pointer-events: none;
    }}

    /* glowing accent blob */
    .page-banner::after {{
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(79,142,247,0.12) 0%, transparent 65%);
        pointer-events: none;
    }}

    .banner-inner {{
        position: relative;
        z-index: 2;
    }}

    .banner-eyebrow {{
        font-size: 10px;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: {PALETTE['accent']};
        margin-bottom: 12px;
        font-family: 'DM Mono', 'Courier New', monospace;
    }}

    .banner-title {{
        display: flex;
        align-items: baseline;
        gap: 14px;
        line-height: 1;
        flex-wrap: wrap;
    }}

    .banner-title-main {{
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #ffffff;
        font-family: 'DM Mono', 'Courier New', monospace;
    }}

    .banner-title-accent {{
        font-size: 48px;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: {PALETTE['accent']};
        font-family: 'DM Mono', 'Courier New', monospace;
        opacity: 0.9;
    }}

    .banner-rule {{
        width: 48px;
        height: 3px;
        background: linear-gradient(90deg, {PALETTE['accent']}, transparent);
        border-radius: 2px;
        margin: 16px 0;
    }}

    .banner-meta {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }}

    .banner-badge {{
        font-size: 11px;
        font-family: 'DM Mono', 'Courier New', monospace;
        letter-spacing: 0.08em;
        color: #ffffff;
        background: rgba(79,142,247,0.2);
        border: 1px solid rgba(79,142,247,0.35);
        border-radius: 4px;
        padding: 3px 10px;
    }}

    .banner-sep {{
        color: rgba(255,255,255,0.25);
        font-size: 13px;
    }}

    .banner-rows {{
        font-size: 12px;
        color: rgba(255,255,255,0.45);
        font-family: 'DM Mono', 'Courier New', monospace;
        letter-spacing: 0.04em;
    }}

    /* right-side decorative vertical lines */
    .banner-deco {{
        position: absolute;
        right: 44px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        gap: 8px;
        align-items: flex-end;
        z-index: 2;
        height: 64px;
    }}
    .deco-bar {{
        width: 3px;
        background: linear-gradient(180deg, {PALETTE['accent']}, transparent);
        border-radius: 2px;
        opacity: 0.5;
    }}

    /* ── tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid {PALETTE['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border: none;
        color: {PALETTE['muted']};
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 8px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        color: {PALETTE['accent']} !important;
        border-bottom: 2px solid {PALETTE['accent']} !important;
        background: transparent !important;
    }}

    /* ── dataframe ── */
    .stDataFrame {{ border: 1px solid {PALETTE['border']}; border-radius: 6px; }}

    /* ── divider ── */
    hr {{ border-color: {PALETTE['border']}; }}

    /* ── plotly export buttons ── */
    .modebar {{ background: transparent !important; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PLOTLY TEMPLATE
# ─────────────────────────────────────────────
import plotly.io as pio

pio.templates["bookshop"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["bg"],
        font=dict(family="DM Mono, Courier New, monospace", color=PALETTE["text"], size=11),
        colorway=[PALETTE["accent"], PALETTE["green"], PALETTE["amber"],
                  "#9b59b6", "#e74c3c", "#1abc9c", "#3498db", "#f39c12"],
        xaxis=dict(gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
                   tickcolor=PALETTE["muted"], zerolinecolor=PALETTE["border"]),
        yaxis=dict(gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
                   tickcolor=PALETTE["muted"], zerolinecolor=PALETTE["border"]),
        title=dict(font=dict(size=13, color=PALETTE["text"])),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=PALETTE["border"]),
        margin=dict(t=45, b=40, l=50, r=20),
        hoverlabel=dict(
            bgcolor=PALETTE["surface"],
            bordercolor=PALETTE["border"],
            font=dict(color=PALETTE["text"], size=11)
        ),
    )
)
DEFAULT_TEMPLATE = "bookshop"


# ─────────────────────────────────────────────
# SNOWFLAKE CONNECTION (cached)
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_connection():
    return snowflake.connector.connect(
        user="ATTIDIANY",
        password='Bexzav-xekdy4-kyftaq',
        account="iwledsd-ow30473",
        warehouse="COMPUTE_WH",
        database="BOOKSHOP",
        schema="MARTS",
    )


@st.cache_data(ttl=300, show_spinner=False)
def load_data(query: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(query, conn)
    df.columns = df.columns.str.upper()
    return df


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_num(n: float, prefix: str = "", suffix: str = "") -> str:
    if n >= 1_000_000:
        return f"{prefix}{n/1_000_000:.1f}M{suffix}"
    if n >= 1_000:
        return f"{prefix}{n/1_000:.1f}K{suffix}"
    return f"{prefix}{n:,.0f}{suffix}"


def kpi_card(label: str, value: str, delta: str = "", delta_pos: bool = True,
             accent: str = PALETTE["accent"]) -> str:
    delta_class = "pos" if delta_pos else "neg"
    delta_html = (
        f'<div class="kpi-delta {delta_class}">'
        f'{"+" if delta_pos else ""}{delta}</div>'
        if delta else ""
    )
    return f"""
    <div class="kpi-card" style="--accent-color:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
with st.spinner("Connecting to Snowflake..."):
    try:
        df_raw = load_data("SELECT * FROM OBT_SALES")
    except ProgrammingError as e:
        st.error(f"Snowflake error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

if df_raw.empty:
    st.warning("OBT_SALES returned 0 rows.")
    st.stop()


# ─────────────────────────────────────────────
# DETECT COLUMNS
# ─────────────────────────────────────────────
COLS = set(df_raw.columns)

COL_MONTH   = "MOIS"         if "MOIS"         in COLS else None
COL_AMOUNT  = "TOTAL_AMOUNT" if "TOTAL_AMOUNT"  in COLS else None
COL_QTE     = "QTE"          if "QTE"           in COLS else None
COL_CLIENT  = "NOM"          if "NOM"           in COLS else None
COL_BOOK    = ("INTITULE_BOOK" if "INTITULE_BOOK" in COLS
               else "INTITULE" if "INTITULE" in COLS else None)
COL_CAT     = "CATEGORIE"    if "CATEGORIE"     in COLS else None
COL_PRICE   = "PRIX_UNITAIRE" if "PRIX_UNITAIRE" in COLS else None
COL_DATE    = "DATE_COMMANDE" if "DATE_COMMANDE" in COLS else None


# ─────────────────────────────────────────────
# SIDEBAR  — FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase;'
                f'color:{PALETTE["muted"]};margin-bottom:16px">Filtres</div>',
                unsafe_allow_html=True)

    df = df_raw.copy()

    # Filtre mois
    if COL_MONTH:
        all_months = sorted(df[COL_MONTH].dropna().unique())
        sel_months = st.multiselect("Mois", all_months, default=all_months)
        if sel_months:
            df = df[df[COL_MONTH].isin(sel_months)]

    # Filtre categorie
    if COL_CAT:
        all_cats = sorted(df[COL_CAT].dropna().unique())
        sel_cats = st.multiselect("Categorie", all_cats, default=all_cats)
        if sel_cats:
            df = df[df[COL_CAT].isin(sel_cats)]

    # Plage de chiffre d'affaires
    if COL_AMOUNT:
        min_a, max_a = float(df[COL_AMOUNT].min()), float(df[COL_AMOUNT].max())
        if min_a < max_a:
            rng = st.slider("Plage de CA", min_a, max_a, (min_a, max_a),
                            format="%.0f")
            df = df[df[COL_AMOUNT].between(*rng)]

    st.markdown("---")

    # Selecteur Top N
    top_n = st.selectbox("Top N (classements)", [5, 10, 15, 20], index=1)

    # Export
    st.markdown("---")
    csv_bytes = df.to_csv(index=False).encode()
    st.download_button(
        label="Exporter CSV filtre",
        data=csv_bytes,
        file_name="bookshop_filtre.csv",
        mime="text/csv",
    )

    # Hint cache
    st.markdown(
        f'<div style="font-size:10px;color:{PALETTE["muted"]};margin-top:16px">'
        f'Cache TTL : 5 min — {len(df_raw):,} lignes chargees</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
# PAGE HEADER — banner
# ─────────────────────────────────────────────
bar_heights = [32, 48, 64, 48, 32, 20, 14]
deco_bars = "".join(
    f'<div class="deco-bar" style="height:{h}px"></div>'
    for h in bar_heights
)

st.markdown(f"""
<div class="page-banner">
  <div class="banner-inner">
    <div class="banner-eyebrow">Data Warehouse · Snowflake</div>
    <div class="banner-title">
      <span class="banner-title-main">BOOKSHOP</span>
      <span class="banner-title-accent">ANALYTICS</span>
    </div>
    <div class="banner-rule"></div>
    <div class="banner-meta">
      <span class="banner-badge">OBT_SALES</span>
      <span class="banner-sep">·</span>
      <span class="banner-rows">{len(df):,} rows after filters</span>
    </div>
  </div>
  <div class="banner-deco">{deco_bars}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
section("Indicateurs cles")
k1, k2, k3, k4 = st.columns(4)

total_rev  = df[COL_AMOUNT].sum()  if COL_AMOUNT  else 0
total_qty  = df[COL_QTE].sum()     if COL_QTE     else 0
n_clients  = df[COL_CLIENT].nunique() if COL_CLIENT else 0
n_books    = df[COL_BOOK].nunique()   if COL_BOOK   else 0
avg_basket = (total_rev / len(df)) if len(df) else 0

with k1:
    st.markdown(kpi_card("Chiffre d'affaires", fmt_num(total_rev), accent=PALETTE["accent"]),
                unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Unites vendues", fmt_num(total_qty), accent=PALETTE["green"]),
                unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Clients uniques", fmt_num(n_clients), accent=PALETTE["amber"]),
                unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("Panier moyen", fmt_num(avg_basket), accent="#9b59b6"),
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_trend, tab_products, tab_clients, tab_data = st.tabs(
    ["Tendance", "Produits", "Clients", "Donnees brutes"]
)


# ══════════════════════════════════════════════
# TAB 1 — TREND
# ══════════════════════════════════════════════
with tab_trend:

    if COL_MONTH and COL_AMOUNT:
        section("Chiffre d'affaires et volume dans le temps")

        monthly = (
            df.groupby(COL_MONTH)
            .agg(REVENUE=(COL_AMOUNT, "sum"), ORDERS=(COL_AMOUNT, "count"))
            .reset_index()
            .sort_values(COL_MONTH)
        )
        if COL_QTE:
            monthly["QTE"] = df.groupby(COL_MONTH)[COL_QTE].sum().values

        # Variation mois sur mois
        monthly["MOM_PCT"] = monthly["REVENUE"].pct_change() * 100

        c_left, c_right = st.columns([2, 1])

        with c_left:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=monthly[COL_MONTH], y=monthly["REVENUE"],
                name="CA", marker_color=PALETTE["accent"],
                opacity=0.85,
            ))
            if "QTE" in monthly.columns:
                fig_trend.add_trace(go.Scatter(
                    x=monthly[COL_MONTH], y=monthly["QTE"],
                    name="Unites", yaxis="y2",
                    line=dict(color=PALETTE["green"], width=2),
                    mode="lines+markers",
                    marker=dict(size=5),
                ))
                fig_trend.update_layout(
                    yaxis2=dict(
                        overlaying="y", side="right",
                        gridcolor="rgba(0,0,0,0)",
                        tickfont=dict(color=PALETTE["green"]),
                    )
                )
            fig_trend.update_layout(
                template=DEFAULT_TEMPLATE,
                title="CA mensuel vs Unites vendues",
                barmode="overlay",
                legend=dict(orientation="h", y=1.12),
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with c_right:
            fig_mom = go.Figure(go.Waterfall(
                x=monthly[COL_MONTH].astype(str),
                y=monthly["MOM_PCT"].fillna(0).round(1),
                connector=dict(line=dict(color=PALETTE["border"])),
                increasing=dict(marker_color=PALETTE["green"]),
                decreasing=dict(marker_color=PALETTE["red"]),
                totals=dict(marker_color=PALETTE["muted"]),
                texttemplate="%{y:.1f}%",
                textposition="outside",
            ))
            fig_mom.update_layout(
                template=DEFAULT_TEMPLATE,
                title="Variation MoM du CA (%)",
            )
            st.plotly_chart(fig_mom, use_container_width=True)

        section("CA cumule")
        monthly["CUMULATIVE"] = monthly["REVENUE"].cumsum()
        fig_cum = px.area(
            monthly, x=COL_MONTH, y="CUMULATIVE",
            template=DEFAULT_TEMPLATE,
            title="Chiffre d'affaires cumule",
            color_discrete_sequence=[PALETTE["accent"]],
        )
        fig_cum.update_traces(
            line_color=PALETTE["accent"],
            fillcolor=f"rgba(79,142,247,0.15)"
        )
        st.plotly_chart(fig_cum, use_container_width=True)

    else:
        st.info("Les colonnes MOIS et TOTAL_AMOUNT sont requises pour cet onglet.")


# ══════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ══════════════════════════════════════════════
with tab_products:

    section("Performance des livres")

    if COL_BOOK and COL_QTE:
        top_books = (
            df.groupby(COL_BOOK)
            .agg(UNITS=(COL_QTE, "sum"), REVENUE=(COL_AMOUNT, "sum") if COL_AMOUNT else (COL_QTE, "sum"))
            .reset_index()
            .sort_values("REVENUE", ascending=False)
            .head(top_n)
        )

        c1, c2 = st.columns(2)

        with c1:
            fig_bar = px.bar(
                top_books.sort_values("REVENUE"),
                x="REVENUE", y=COL_BOOK,
                orientation="h",
                template=DEFAULT_TEMPLATE,
                title=f"Top {top_n} — Chiffre d'affaires",
                color="REVENUE",
                color_continuous_scale=["#1c2a45", PALETTE["accent"]],
                text="REVENUE",
            )
            fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_bar.update_coloraxes(showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            fig_units = px.bar(
                top_books.sort_values("UNITS"),
                x="UNITS", y=COL_BOOK,
                orientation="h",
                template=DEFAULT_TEMPLATE,
                title=f"Top {top_n} — Unites vendues",
                color="UNITS",
                color_continuous_scale=["#1a3327", PALETTE["green"]],
                text="UNITS",
            )
            fig_units.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_units.update_coloraxes(showscale=False)
            st.plotly_chart(fig_units, use_container_width=True)

    # Repartition par categorie
    if COL_CAT and COL_AMOUNT:
        section("Repartition par categorie")

        cat_data = (
            df.groupby(COL_CAT)
            .agg(REVENUE=(COL_AMOUNT, "sum"), ORDERS=(COL_AMOUNT, "count"))
            .reset_index()
        )

        c3, c4 = st.columns(2)

        with c3:
            fig_pie = px.pie(
                cat_data, values="REVENUE", names=COL_CAT,
                template=DEFAULT_TEMPLATE,
                title="CA par categorie",
                hole=0.55,
                color_discrete_sequence=[
                    PALETTE["accent"], PALETTE["green"], PALETTE["amber"],
                    "#9b59b6", "#e74c3c", "#1abc9c"
                ],
            )
            fig_pie.update_traces(textinfo="label+percent", textposition="outside")
            st.plotly_chart(fig_pie, use_container_width=True)

        with c4:
            fig_cat_bar = px.bar(
                cat_data.sort_values("REVENUE", ascending=False),
                x=COL_CAT, y="REVENUE",
                template=DEFAULT_TEMPLATE,
                title="Commandes vs CA par categorie",
                text="ORDERS",
                color="REVENUE",
                color_continuous_scale=["#1c2a45", PALETTE["accent"]],
            )
            fig_cat_bar.update_traces(texttemplate="Cmd: %{text}", textposition="outside")
            fig_cat_bar.update_coloraxes(showscale=False)
            st.plotly_chart(fig_cat_bar, use_container_width=True)

    # Scatter: prix vs quantite
    if COL_PRICE and COL_QTE and COL_BOOK:
        section("Prix vs volume")
        scatter_df = (
            df.groupby(COL_BOOK)
            .agg(AVG_PRICE=(COL_PRICE, "mean"), UNITS=(COL_QTE, "sum"))
            .reset_index()
        )
        fig_scatter = px.scatter(
            scatter_df, x="AVG_PRICE", y="UNITS", text=COL_BOOK,
            template=DEFAULT_TEMPLATE,
            title="Prix moyen vs unites vendues (par livre)",
            color="UNITS",
            color_continuous_scale=["#1c2a45", PALETTE["accent"]],
            size="UNITS",
        )
        fig_scatter.update_traces(textposition="top center", textfont_size=9)
        fig_scatter.update_coloraxes(showscale=False)
        st.plotly_chart(fig_scatter, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 — CLIENTS
# ══════════════════════════════════════════════
with tab_clients:

    if COL_CLIENT and COL_AMOUNT:
        section("Classement des clients par CA")

        client_data = (
            df.groupby(COL_CLIENT)
            .agg(
                REVENUE=(COL_AMOUNT, "sum"),
                ORDERS=(COL_AMOUNT, "count"),
                AVG_ORDER=(COL_AMOUNT, "mean"),
            )
            .reset_index()
            .sort_values("REVENUE", ascending=False)
        )

        # Analyse Pareto
        client_data = client_data.reset_index(drop=True)
        client_data["CUMUL_PCT"] = (
            client_data["REVENUE"].cumsum() / client_data["REVENUE"].sum() * 100
        )

        top_clients = client_data.head(top_n)

        c1, c2 = st.columns([3, 2])

        with c1:
            fig_clients = px.bar(
                top_clients.sort_values("REVENUE"),
                x="REVENUE", y=COL_CLIENT,
                orientation="h",
                template=DEFAULT_TEMPLATE,
                title=f"Top {top_n} clients — Chiffre d'affaires",
                color="ORDERS",
                color_continuous_scale=["#1c2a45", PALETTE["amber"]],
                text="REVENUE",
            )
            fig_clients.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            st.plotly_chart(fig_clients, use_container_width=True)

        with c2:
            fig_aov = px.bar(
                top_clients.sort_values("AVG_ORDER", ascending=False),
                x=COL_CLIENT, y="AVG_ORDER",
                template=DEFAULT_TEMPLATE,
                title="Panier moyen par client",
                color="AVG_ORDER",
                color_continuous_scale=["#1c2a45", PALETTE["green"]],
            )
            fig_aov.update_coloraxes(showscale=False)
            st.plotly_chart(fig_aov, use_container_width=True)

        # Courbe de Pareto
        section("Pareto — concentration du CA")
        pareto_df = client_data.head(50)
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=pareto_df[COL_CLIENT], y=pareto_df["REVENUE"],
            name="CA", marker_color=PALETTE["accent"], opacity=0.8,
        ))
        fig_pareto.add_trace(go.Scatter(
            x=pareto_df[COL_CLIENT], y=pareto_df["CUMUL_PCT"],
            name="Cumul %", yaxis="y2",
            line=dict(color=PALETTE["amber"], width=2),
        ))
        fig_pareto.add_hline(
            y=80, yref="y2",
            line=dict(color=PALETTE["red"], dash="dot", width=1),
            annotation_text="80%", annotation_position="right",
        )
        fig_pareto.update_layout(
            template=DEFAULT_TEMPLATE,
            title="Pareto — top 50 clients",
            yaxis2=dict(
                overlaying="y", side="right",
                range=[0, 110], ticksuffix="%",
                gridcolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

        # Heatmap client x mois
        if COL_MONTH:
            section("Heatmap client x mois")
            pivot = (
                df.groupby([COL_CLIENT, COL_MONTH])[COL_AMOUNT]
                .sum()
                .unstack(fill_value=0)
            )
            top_c = client_data.head(15)[COL_CLIENT].tolist()
            pivot = pivot.loc[pivot.index.isin(top_c)]

            fig_heat = px.imshow(
                pivot,
                template=DEFAULT_TEMPLATE,
                color_continuous_scale=["#0d0f14", PALETTE["accent"]],
                title=f"Heatmap CA — top {min(15, top_n)} clients",
                aspect="auto",
            )
            fig_heat.update_layout(
                coloraxis_colorbar=dict(thickness=10, tickfont_size=9)
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    else:
        st.info("Les colonnes NOM et TOTAL_AMOUNT sont requises pour cet onglet.")


# ══════════════════════════════════════════════
# TAB 4 — RAW DATA
# ══════════════════════════════════════════════
with tab_data:
    section(f"Raw data — {len(df):,} rows")

    search = st.text_input("Search (all columns)", "")
    if search:
        mask = df.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False)
        ).any(axis=1)
        display_df = df[mask]
    else:
        display_df = df

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
    )

    st.markdown(
        f'<div style="font-size:11px;color:{PALETTE["muted"]};margin-top:8px">'
        f'{len(display_df):,} rows displayed</div>',
        unsafe_allow_html=True
    )

    # Column stats
    section("Column statistics")
    num_cols = df.select_dtypes(include="number").columns.tolist()
    if num_cols:
        st.dataframe(
            df[num_cols].describe().T.round(2),
            use_container_width=True,
        )