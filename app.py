import pandas as pd
import matplotlib.pyplot as plt

# Načtení Excel souboru
df = pd.read_excel("Řádky práce_638901695226656392.xlsx", engine="openpyxl")

# Filtrování: Typ práce == 'Vydat' a ID pracovní třídy == 'Prodej' nebo prázdné
filtered_df = df[(df['Typ práce'] == 'Vydat') & ((df['ID pracovní třídy'] == 'Prodej') | (df['ID pracovní třídy'].isna()))].copy()

# Převod datumu
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

# Export do Excelu
final_df.to_excel("souhrn_vydat.xlsx", index=False)

# Graf 1: Počet SKU podle uživatelů v rámci dne
pivot1 = grouped.pivot(index='Datum', columns='ID uživatele', values='POČET_SKU').fillna(0)
pivot1.plot(kind='bar', stacked=True, figsize=(12, 6))
plt.title("Počet SKU podle uživatelů v rámci dne")
plt.xlabel("Datum")
plt.ylabel("Počet SKU")
plt.tight_layout()
plt.savefig("graf_sku_podle_uzivatelu.png")
plt.close()

# Graf 2: Celkové počty po dnech
daily_totals.set_index('Datum').plot(kind='bar', figsize=(12, 6))
plt.title("Celkové počty po dnech")
plt.xlabel("Datum")
plt.ylabel("Počty")
plt.tight_layout()
plt.savefig("graf_celkove_po_dnech.png")
plt.close()

print("Souhrn byl úspěšně vygenerován do souboru 'souhrn_vydat.xlsx' a grafy byly uloženy jako PNG.")
