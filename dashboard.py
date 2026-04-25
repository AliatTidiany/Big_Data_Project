import streamlit as st
import pandas as pd
import snowflake.connector
import os
import plotly.express as px

# ==========================
# CONFIG PAGE
# ==========================
st.set_page_config(
    page_title="📚 Bookshop Analytics",
    layout="wide"
)

# ==========================
# HEADER
# ==========================
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>
    📚 Bookshop Analytics Dashboard
    </h1>
    <p style='text-align: center;'>
    Analyse des ventes - Data Warehouse (OBT)
    </p>
""", unsafe_allow_html=True)

# ==========================
# CONNEXION SNOWFLAKE
# ==========================
conn = snowflake.connector.connect(
    user="ATTIDIANY",
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account="iwledsd-ow30473",
    warehouse="COMPUTE_WH",
    database="BOOKSHOP",
    schema="MARTS"
)

df = pd.read_sql("SELECT * FROM OBT_SALES", conn)

if df.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

# ==========================
# NORMALISATION
# ==========================
df.columns = df.columns.str.upper()

# ==========================
# SIDEBAR FILTRES
# ==========================
st.sidebar.header("🎛 Filtres")

# Mois
if "MOIS" in df.columns:
    mois_options = sorted(df["MOIS"].dropna().unique())
    selected_mois = st.sidebar.multiselect(
        "📅 Mois",
        mois_options,
        default=mois_options
    )
    df = df[df["MOIS"].isin(selected_mois)]

# ==========================
# KPI CARDS (DESIGN)
# ==========================
st.subheader("📌 Indicateurs clés")

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
    <div style="background-color:#e8f5e9;padding:20px;border-radius:10px">
    <h3>💰 Revenue</h3>
    <h2>{int(df["TOTAL_AMOUNT"].sum()):,}</h2>
    </div>
""", unsafe_allow_html=True)

col2.markdown(f"""
    <div style="background-color:#e3f2fd;padding:20px;border-radius:10px">
    <h3>📦 Quantité</h3>
    <h2>{int(df["QTE"].sum()):,}</h2>
    </div>
""", unsafe_allow_html=True)

col3.markdown(f"""
    <div style="background-color:#fff3e0;padding:20px;border-radius:10px">
    <h3>👥 Clients</h3>
    <h2>{df["NOM"].nunique()}</h2>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================
# VENTES PAR MOIS
# ==========================
st.subheader("📈 Évolution des ventes")

if "MOIS" in df.columns:
    sales = df.groupby("MOIS")["TOTAL_AMOUNT"].sum().reset_index()

    fig = px.line(
        sales,
        x="MOIS",
        y="TOTAL_AMOUNT",
        markers=True,
        title="Chiffre d'affaires par mois"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================
# TOP LIVRES
# ==========================
st.subheader("📚 Top livres")

book_col = None
if "INTITULE_BOOK" in df.columns:
    book_col = "INTITULE_BOOK"
elif "INTITULE" in df.columns:
    book_col = "INTITULE"

if book_col:
    top_books = (
        df.groupby(book_col)["QTE"]
        .sum()
        .reset_index()
        .sort_values(by="QTE", ascending=False)
        .head(10)
    )

    fig_books = px.bar(
        top_books,
        x=book_col,
        y="QTE",
        color="QTE",
        title="Top 10 livres vendus"
    )

    st.plotly_chart(fig_books, use_container_width=True)

# ==========================
# TOP CLIENTS
# ==========================
st.subheader("👤 Top clients")

if "NOM" in df.columns:
    top_clients = (
        df.groupby("NOM")["TOTAL_AMOUNT"]
        .sum()
        .reset_index()
        .sort_values(by="TOTAL_AMOUNT", ascending=False)
        .head(10)
    )

    fig_clients = px.bar(
        top_clients,
        x="NOM",
        y="TOTAL_AMOUNT",
        color="TOTAL_AMOUNT",
        title="Top 10 clients"
    )

    st.plotly_chart(fig_clients, use_container_width=True)

# ==========================
# TABLE FINALE
# ==========================
st.subheader("🧾 Données détaillées")

st.dataframe(df, use_container_width=True)