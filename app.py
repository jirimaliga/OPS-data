import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.title("Souhrnná analýza práce - Prodej & Vydat + Prázdné")

uploaded_file = st.file_uploader("Nahraj Excel soubor (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df["Uzavřená práce"] = pd.to_datetime(df["Uzavřená práce"], errors="coerce")

    # Filtrování: Typ práce = Vydat, ID pracovní třídy = Prodej nebo prázdné
    filtered_df = df[
        (df["Typ práce"] == "Vydat") &
        (df["ID pracovní třídy"].isin(["Prodej", None, ""]))
    ]

    # Výpočet POČET SKU, SKP, PALET
    def compute_summary(group):
        pocet_sku = len(group)
        skp_values = group.apply(
            lambda row: 1 if pd.isna(row["ID pracovní třídy"]) or row["ID pracovní třídy"] == "" else row["Množství práce"],
            axis=1
        )
        pocet_skp = skp_values.sum()
        pocet_palet = group[group["Jednotka"] == "PAL"]["Množství práce"].sum()
        return pd.Series({
            "POČET SKU": pocet_sku,
            "POČET SKP": pocet_skp,
            "POČET PALET": pocet_palet
        })

    # Souhrn podle dne a ID uživatele
    summary = filtered_df.groupby([filtered_df["Uzavřená práce"].dt.date, "ID uživatele"]).apply(compute_summary).reset_index()

    # Souhrn CELKEM za každý den
    daily_total = filtered_df.groupby(filtered_df["Uzavřená práce"].dt.date).apply(compute_summary).reset_index()
    daily_total["ID uživatele"] = "CELKEM"

    # Spojení obou tabulek
    final_summary = pd.concat([summary, daily_total], ignore_index=True)

    st.subheader("Souhrnná tabulka")
    st.dataframe(final_summary)

    # Export do Excelu
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        final_summary.to_excel(writer, index=False, sheet_name='Souhrn')
    st.download_button(
        label="📥 Stáhnout souhrn jako Excel",
        data=output.getvalue(),
        file_name="souhrn_prodej_vydat.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Grafy po dnech (jen CELKEM)
    st.subheader("📊 Grafy souhrnných hodnot po dnech")

    daily_plot_data = daily_total.set_index("Uzavřená práce")[["POČET SKU", "POČET SKP", "POČET PALET"]]

    fig, ax = plt.subplots(figsize=(10, 5))
    daily_plot_data.plot(kind='bar', ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Datum")
    plt.ylabel("Hodnota")
    plt.title("Souhrnné hodnoty po dnech (CELKEM)")
    st.pyplot(fig)
