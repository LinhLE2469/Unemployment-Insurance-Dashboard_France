import json
from datetime import datetime
import os
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st
from preprocessing.data_cleaning import clean_dataset_filelike



st.set_page_config(page_title="Indicateurs Assurance chômage — par département", layout="wide")

# --- Asset helper (placed before sidebar so it can be used there)

# Ensure the main title is shown on app startup (before any sidebar st.stop())
st.title("INDICATEURS DE SUIVI DE L'ASSURANCE CHÔMAGE — PAR DÉPARTEMENT")


#----------------------------- SLIDEBAR--------------------------------
@st.cache_data
def load_and_clean(fileobj, sep=";", save_path=None):
    return clean_dataset_filelike(fileobj, sep=sep, save_path=save_path)

with st.sidebar:
    # show app icon and flag side-by-side at the top of the sidebar (if available)
    
    st.image("assets/flag.jpg", width=120)

    
    st.header("Télécharger les données")
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

    if uploaded_file is not None:
        # User uploaded a file -> pass the file-like object to cleaning helper
        df = load_and_clean(uploaded_file, sep=";", save_path="data/data_cleaned.csv")
    else:
        # No upload: load default raw CSV from disk via helper
        df = load_and_clean("data/raw_data.csv", sep=";", save_path="data/data_cleaned.csv")

    st.header("Filtres")

    # Region filters
    selected_regs = []
    if "region" in df.columns:
        all_regions = sorted(df["region"].dropna().unique().tolist())
        selected_regs = st.multiselect(
            "Région(s)",
            all_regions,
            default=[]  # no default selection: show all France on startup
        )

    # select region
    if selected_regs: 
        df = df[df["region"].isin(selected_regs)]
    
    # select department
    selected_deps = [] 
    if "departement" in df.columns:
        # list department
        all_deps_filtered = sorted(df["departement"].dropna().unique().tolist())

        # If the user has previously selected but is no longer in the region → automatically remove
        selected_deps = st.multiselect(
            "Département(s)",
            all_deps_filtered,
            default=[]  # no default selection: show all departments on startup
        )

    if selected_deps:
        df = df[df["departement"].isin(selected_deps)]

    # Time filter by YEAR
    if "mois" in df.columns and pd.api.types.is_datetime64_any_dtype(df["mois"]):

        # take min/max of year
        min_year = df["mois"].dt.year.min()
        max_year = df["mois"].dt.year.max()

        start_year, end_year = st.slider(
            "Période (année)",
            min_value=int(min_year),
            max_value=int(max_year),
            value=(int(min_year), int(max_year))
        )

        # filter by year
        df = df[df["mois"].dt.year.between(start_year, end_year)]

    # Metric selector inside the sidebar so the user chooses indicator before viewing charts
    numeric_cols_sidebar = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if numeric_cols_sidebar:
        metric = st.selectbox(
            "Choisir un indicateur",
            numeric_cols_sidebar,
            index=numeric_cols_sidebar.index("allocataires_total") if "allocataires_total" in numeric_cols_sidebar else 0,
        )
    else:
        metric = None







#------------------------------- METRICS -----------------------------

# KPI row
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
latest_df = df
if "mois" in df.columns and pd.api.types.is_datetime64_any_dtype(df["mois"]):
    last_date = df["mois"].max()
    latest_df = df[df["mois"]==last_date]

kpi_cols = ["allocataires_total", "ouvertures_droit", "fins_droit", "depense_mensuelle"]
kpi_cols = [c for c in kpi_cols if c in numeric_cols]

st.subheader("Indicateurs clés (dernier mois disponible)")
if not latest_df.empty and kpi_cols:
    cols = st.columns(len(kpi_cols))
    for i, k in enumerate(kpi_cols):
        total = float(latest_df[k].sum())
        delta = None
        if "mois" in df.columns and pd.api.types.is_datetime64_any_dtype(df["mois"]):
            prev_date = df["mois"].sort_values().unique()
            prev_date = prev_date[-2] if len(prev_date)>=2 else None
            if prev_date is not None:
                prev_val = float(df[df["mois"]==prev_date][k].sum())
                delta = total - prev_val
        cols[i].metric(k.replace("_", " ").title(), f"{total:,.0f}".replace(",", " "), (f"{delta:+,.0f}".replace(",", " ")) if delta is not None else None)

with st.expander("Comment interpréter les indicateurs clés"):
    st.markdown("""
- **Bénéficiaires totaux (allocataires_total)** – Nombre de personnes couvertes par l'assurance chômage.  
- **Nouveaux droits ouverts (ouvertures_droit)** – Personnes devenues éligibles ce mois.  
- **Fins de droits (fins_droit)** – Personnes ayant terminé leur période d'indemnisation ce mois.  
- **Dépense mensuelle (depense_mensuelle)** – Montant total versé en indemnités ce mois (€).

**Pourquoi cette section est importante**  
Ces indicateurs donnent un aperçu rapide de la situation récente.  
Ils montrent si le système s'étend ou se contracte, en regardant :
- combien de personnes entrent vs. sortent du dispositif  
- le montant versé par le système  
- la variation par rapport au mois précédent (delta)
""")
# Charts 1

st.markdown("---")

# Charts 1
st.subheader("Série temporelle")
# metric is selected in the sidebar
color_by = st.selectbox("Couleur par", ["departement","region"] if "region" in df.columns else ["departement"])

if "mois" in df.columns and pd.api.types.is_datetime64_any_dtype(df["mois"]):
    # Exclude aggregate 'Total' rows from time series (case-insensitive)
    df_ts = df.copy()
    if "departement" in df_ts.columns:
        df_ts = df_ts[df_ts["departement"].astype(str).str.lower() != "total"]

    ts = alt.Chart(df_ts).mark_line(point=False).encode(
        x=alt.X("yearmonth(mois):T",title="Mois", axis=alt.Axis(format="%b %Y")),
        y=alt.Y(f"{metric}:Q", title=metric.replace("_"," ").title()),
        color=alt.Color(color_by, title=color_by.title()),
        tooltip=[alt.Tooltip("mois:T", title="Mois"), color_by, alt.Tooltip(f"{metric}:Q", format=",.0f")]
    ).properties(height=380)
    st.altair_chart(ts.interactive(), use_container_width=True)
else:
    st.info("Colonne 'mois' manquante ou non datée — série temporelle indisponible.")

with st.expander("Explication des indicateurs"):
    st.markdown("""
**Ce que montre ce graphique**  
Cette série temporelle présente l'évolution mensuelle de l'indicateur sélectionné (2020–2025).

**Pourquoi c'est utile**  
Elle met en évidence les tendances longues, les effets saisonniers ou des ruptures (ex. COVID).

**Questions auxquelles ce graphique répond**
- Le nombre de bénéficiaires augmente-t-il ou diminue-t-il ?
- Certains départements suivent-ils une dynamique différente ?
- Existe-t-il des différences structurelles (urbain/rural) ?

""")

# Charts 2
st.markdown("---")
st.subheader("Classement — Top N (dernier mois)")
topn = st.slider("Top N", 3, 30, 10)

if not latest_df.empty:

    df_rank = latest_df[latest_df["departement"].str.lower() != "total"]

    ranking = (
        df_rank.groupby("departement", as_index=False)[metric]
        .sum()
        .sort_values(metric, ascending=False)
        .head(topn)
    )

    bar = alt.Chart(ranking).mark_bar().encode(
        x=alt.X(f"{metric}:Q", title=metric.replace("_", " ").title()),
        y=alt.Y("departement:N", sort='-x', title="Département"),
        tooltip=["departement", alt.Tooltip(f"{metric}:Q", format=",.0f")]
    ).properties(height=40*len(ranking))

    st.altair_chart(bar, use_container_width=True)

else:
    st.info("Pas de données pour le dernier mois.")

with st.expander("Interprétation du classement"):
    st.markdown("""
**Ce que montre ce graphique**  
Ce classement liste les départements avec les valeurs les plus élevées pour l'indicateur sélectionné (dernier mois disponible).

**Pourquoi c'est utile**  
Il permet d'identifier les départements qui pèsent le plus (en nombre ou en dépense).

**Questions**
- Quels départements représentent la plus grande part des bénéficiaires ?
- La concentration est-elle élevée ?
- Les contributeurs principaux sont-ils stables dans le temps ?
""")
# Charts 3
st.markdown("---")
st.subheader("Carte (dernier mois)")
geojson_url = st.text_input("URL GeoJSON (départements)", value="https://france-geojson.gregoiredavid.fr/repo/departements.geojson")
code_col = "code_dep"
# build data for latest month
map_data = latest_df.copy()
if not map_data.empty:
    # Some sources use codes like '2A','2B'. On our data, we keep as string.
    map_data = map_data.groupby(code_col, as_index=False)[metric].sum()
    # Vega-Lite transform lookup
    try:
        map_chart = alt.Chart(alt.Data(url=geojson_url, format=alt.DataFormat(type="json", property="features"))).mark_geoshape(stroke="white").encode(
            color=alt.Color(f"{metric}:Q", title=metric.replace("_"," ").title(), scale=alt.Scale(scheme="blues")),
            tooltip=[alt.Tooltip("properties.code:O", title="Code dep"),
                     alt.Tooltip("properties.nom:N", title="Département"),
                     alt.Tooltip(f"{metric}:Q", title=metric.replace("_"," ").title(), format=",.0f")]
        ).transform_lookup(
            lookup="properties.code",
            from_=alt.LookupData(map_data, code_col, [metric])
        ).properties(height=500)
        st.altair_chart(map_chart, use_container_width=True)
    except Exception as e:
        st.error(f"Échec du chargement GeoJSON : {e}")
else:
    st.info("Pas de données pour construire la carte.")

with st.expander("Interprétation de la carte"):
    st.markdown("""
**Ce que montre la carte**  
La carte choroplèthe affiche la distribution géographique de l'indicateur sélectionné.

**Pourquoi c'est utile**  
Elle révèle les points chauds et les disparités structurelles sur le territoire.

**Questions**
- Où se concentrent les bénéficiaires ?
- Les zones urbaines/industrielles présentent-elles des niveaux plus élevés ?
- Comment les motifs spatiaux se comparent-ils au classement ?
""")

# Download data
st.markdown("---")
st.subheader("Télécharger les données filtrées")
def to_csv_download(df_in: pd.DataFrame) -> str:
    return df_in.to_csv(index=False).encode("utf-8")
st.download_button("Télécharger CSV", data=to_csv_download(df), file_name="donnees_filtrees.csv", mime="text/csv")

