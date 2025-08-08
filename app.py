import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Souhrn práce", layout="wide")
st.title("📦 Souhrn práce – Streamlit aplikace")

uploaded_file = st.file_uploader("Nahraj Excel soubor (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Filtrování dat
    filtered_df = df[(df['Typ práce'] == 'Vydat') & ((df['ID pracovní třídy'] == 'Prodej') | (df['ID pracovní třídy'].isna()))].copy()
    filtered_df['Datum'] = pd.to_datetime(filtered_df['Uzavřená práce']).dt.date

    # Výpočet metrik
    filtered_df['SKP'] = filtered_df.apply(lambda row: 1 if pd.isna(row['ID pracovní třídy']) else row['Množství práce'], axis=1)
    filtered_df['PALETY'] = filtered_df.apply(lambda row: row['Množství práce'] if row['Jednotka'] == 'PAL' else 0, axis=1)

    # Souhrn podle uživatele a dne
    grouped = filtered_df.groupby(['Datum', 'ID uživatele']).agg(
        POČET_SKU=('Množství práce', 'count'),
        POČET_SKP=('SKP', 'sum'),
        POČET_PALET=('PALETY', 'sum')
    ).reset_index()

    # Celkové součty za den
    daily_totals = grouped.groupby('Datum').agg(
        CELKEM_POČET_SKU=('POČET_SKU', 'sum'),
        CELKEM_POČET_SKP=('POČET_SKP', 'sum'),
        CELKEM_POČET_PALET=('POČET_PALET', 'sum')
    ).reset_index()

    # Spojení souhrnů
    final_df = pd.merge(grouped, daily_totals, on='Datum', how='left')

    st.subheader("📊 Souhrnná tabulka")
    st.dataframe(final_df)

    # Export do Excelu
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Souhrn')
    st.download_button("📥 Stáhnout souhrn jako Excel", data=output.getvalue(), file_name="souhrn_vydat.xlsx")

    # Graf 1: Počet SKU podle uživatelů v rámci dne
    st.subheader("📈 Počet SKU podle uživatelů v rámci dne")
    pivot1 = grouped.pivot(index='Datum', columns='ID uživatele', values='POČET_SKU').fillna(0)
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    pivot1.plot(kind='bar', stacked=True, ax=ax1)
    ax1.set_title("Počet SKU podle uživatelů v rámci dne")
    ax1.set_xlabel("Datum")
    ax1.set_ylabel("Počet SKU")
    st.pyplot(fig1)

    # Graf 2: Celkové počty po dnech
    st.subheader("📈 Celkové počty po dnech")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    daily_totals.set_index('Datum').plot(kind='bar', ax=ax2)
    ax2.set_title("Celkové počty po dnech")
    ax2.set_xlabel("Datum")
    ax2.set_ylabel("Počty")
    st.pyplot(fig2)
else:
    st.info("📤 Nahraj prosím Excel soubor pro zobrazení souhrnu.")
