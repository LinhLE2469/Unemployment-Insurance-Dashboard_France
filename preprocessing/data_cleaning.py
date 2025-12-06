import pandas as pd
import numpy as np
from pathlib import Path



def cleaning_data(df,save_path=None):
    # Due to the name of col is too long, so we change it.
    col_mapping = {
            "region": "region",
            "departement": "departement",
            "Mois": "mois",
            "Nombre d'allocataires pris en charge": "allocataires_total",
            "Nombre d'ouvertures de droit": "ouvertures_droit",
            "Nombre d'ouvertures de droit initiales": "ouvertures_initiales",
            "Nombre de reprises": "reprises",
            "Nombre de fins de droit": "fins_droit",
            "Montant d'allocation journalier": "allocation_jour",
            "Durée moyenne potentielle": "duree_moy",
            "Nombre d'allocataires indemnisés": "allocataires_indemnises",
            "Nombre d'allocataires indemnisés au titre de l'AREF": "allocataires_aref",
            "Nombre d'allocataires indemnisés au titre de l'ASP": "allocataires_asp",
            "Montant moyen d'indemnisation mensuel net": "indemnisation_moy_net",
            "Montant moyen d'indemnisation mensuel net des allocataires ayant travaillé": "indemnisation_moy_trav",
            "Montant moyen d'indemnisation mensuel net des allocataires n'ayant pas travaillé": "indemnisation_moy_non_trav",
            "Part des allocataires ayant travaillé dans le mois": "part_trav_mois",
            "Part des allocataires ayant travaillé dans le mois ét ayant été indemnisé": "part_trav_mois_indemnise",
            "Dépense mensuelle": "depense_mensuelle",
            "code_departement": "code_dep",
            "geo_departement": "geo_dep",
            "geo_centre": "geo_centre" }

    # Change column_name
    df.rename(columns=col_mapping, inplace=True)
    # remove duplicate values
    df = df.drop_duplicates()
    # convert the object to datatime for the col "mois"
    df['mois'] = pd.to_datetime(df['mois'], errors='coerce') 
    # remove the cold unnecessary
    df.drop(columns=['geo_dep', 'geo_centre'], inplace=True, errors='ignore') 
    # switch to category (helps reduce memory and speed up groupby)
    df[['region', 'departement']] = df[['region', 'departement']].astype('category')
    df['code_dep'] = df['code_dep'].astype(str).str.zfill(2)
    # Handle missing data
    missing_counts = df.isna().sum().sort_values(ascending=False)
    # Delete rows with NaN in columns with few missing values
    cols_to_dropna = missing_counts[missing_counts < 20].index
    df = df.dropna(subset=cols_to_dropna)
    # Hanlde rows with NaN in columns with many missing values
    cols = missing_counts[missing_counts >= 20].index.tolist()
    # Sort and interpolate by region+department, then close with median
    df = df.sort_values(["region", "departement", "mois"]).reset_index(drop=True)
    for c in cols:
        df[c] = (df.groupby(["region","departement"])[c]
               .transform(lambda s: s.interpolate(limit_direction="both")))
        df[c] = df[c].fillna(df[c].median())
    # Saving data_cleaned
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path, index=False)

    return df 

def clean_dataset_filelike(file, sep=";", save_path=None):
    # Read CSV from streamlit and run cleaning_data
    df = pd.read_csv(file, sep=sep, engine="python")
    return cleaning_data(df, save_path=save_path)
