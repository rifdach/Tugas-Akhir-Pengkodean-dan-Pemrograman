import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from IPython.display import display, HTML
from google.colab import files

# Install kaleido for PNG export
!pip install kaleido

# Defining pastel color palette
colors = {
    'pastel_pink': '#F8B8C7',
    'rose': '#E75480',
    'pastel_yellow': '#FFF9B1',
    'pastel_blue': '#B3CDE0'
}

# Loading data from CSV content
aset_tetap_data = """aset_id,kategori,nilai_perolehan,umur_ekonomis,metode
A001,Mesin,500000000,10,Garis Lurus
A002,Kendaraan,300000000,5,Saldo Menurun
A003,Bangunan,1000000000,20,Garis Lurus
A004,Peralatan,200000000,8,Saldo Menurun
A005,Mesin,750000000,12,Garis Lurus
A006,Kendaraan,450000000,6,Saldo Menurun
A007,Bangunan,1200000000,25,Garis Lurus
A008,Peralatan,150000000,7,Saldo Menurun
A009,Mesin,600000000,10,Garis Lurus
A010,Komputer,100000000,4,Saldo Menurun"""

transaksi_data = """tahun,pendapatan,beban_operasional,penyusutan,skenario
2023,1000000000,600000000,50000000,Normal
2024,1200000000,700000000,55000000,Normal
2025,1500000000,800000000,60000000,Normal
2026,1800000000,900000000,65000000,Normal
2027,2000000000,1000000000,70000000,Normal"""

kebijakan_fiskal_data = """tahun,tax_rate,tax_holiday_awal,tax_holiday_akhir
2023,0.22,2023-01-01,2023-12-31
2024,0.22,2024-01-01,2024-12-31
2025,0.20,2025-01-01,2025-12-31
2026,0.20,2026-01-01,2026-12-31
2027,0.18,2027-01-01,2027-12-31"""

# Converting string data to DataFrames
from io import StringIO
df_aset = pd.read_csv(StringIO(aset_tetap_data))
df_transaksi = pd.read_csv(StringIO(transaksi_data))
df_fiskal = pd.read_csv(StringIO(kebijakan_fiskal_data))

# Converting tax holiday dates to datetime
df_fiskal['tax_holiday_awal'] = pd.to_datetime(df_fiskal['tax_holiday_awal'])
df_fiskal['tax_holiday_akhir'] = pd.to_datetime(df_fiskal['tax_holiday_akhir'])

# Calculating depreciation for each asset
def calculate_depreciation(row, year):
    if row['metode'] == 'Garis Lurus':
        return row['nilai_perolehan'] / row['umur_ekonomis']
    elif row['metode'] == 'Saldo Menurun':
        rate = 2 / row['umur_ekonomis']
        remaining_value = row['nilai_perolehan']
        for y in range(2023, year + 1):
            remaining_value = remaining_value * (1 - rate)
        return row['nilai_perolehan'] * rate if remaining_value > 0 else 0
    return 0

# Calculating total depreciation per year
depreciation_per_year = {}
for year in range(2023, 2028):
    total_dep = sum(df_aset.apply(lambda row: calculate_depreciation(row, year), axis=1))
    depreciation_per_year[year] = total_dep

# Updating transaction data with calculated depreciation
df_transaksi['penyusutan_calculated'] = df_transaksi['tahun'].map(depreciation_per_year)

# Calculating taxable income and tax expenses
df_transaksi['laba_sebelum_pajak'] = df_transaksi['pendapatan'] - df_transaksi['beban_operasional'] - df_transaksi['penyusutan_calculated']
df_transaksi = df_transaksi.merge(df_fiskal[['tahun', 'tax_rate']], on='tahun', how='left')
df_transaksi['pajak'] = df_transaksi['laba_sebelum_pajak'] * df_transaksi['tax_rate']
df_transaksi['laba_bersih'] = df_transaksi['laba_sebelum_pajak'] - df_transaksi['pajak']

# Creating financial summary table
summary_table = df_transaksi[['tahun', 'pendapatan', 'beban_operasional', 'penyusutan_calculated', 'laba_sebelum_pajak', 'pajak', 'laba_bersih']].copy()
summary_table.columns = ['Tahun', 'Pendapatan', 'Beban Operasional', 'Penyusutan', 'Laba Sebelum Pajak', 'Pajak', 'Laba Bersih']

# Formatting numbers to millions with 2 decimal places
for col in ['Pendapatan', 'Beban Operasional', 'Penyusutan', 'Laba Sebelum Pajak', 'Pajak', 'Laba Bersih']:
    summary_table[col] = (summary_table[col] / 1_000_000).round(2)

# Creating animated bar chart for financial metrics
fig = make_subplots(rows=1, cols=1, subplot_titles=["Tren Keuangan Tahunan"])

fig.add_trace(
    go.Bar(
        x=summary_table['Tahun'], y=summary_table['Pendapatan'],
        name='Pendapatan', marker_color=colors['pastel_pink'],
        text=summary_table['Pendapatan'], textposition='auto'
    )
)
fig.add_trace(
    go.Bar(
        x=summary_table['Tahun'], y=summary_table['Beban Operasional'],
        name='Beban Operasional', marker_color=colors['pastel_yellow'],
        text=summary_table['Beban Operasional'], textposition='auto'
    )
)
fig.add_trace(
    go.Bar(
        x=summary_table['Tahun'], y=summary_table['Laba Bersih'],
        name='Laba Bersih', marker_color=colors['pastel_blue'],
        text=summary_table['Laba Bersih'], textposition='auto'
    )
)

fig.update_layout(
    barmode='group',
    title_text="Tren Keuangan (dalam Juta Rupiah)",
    title_font_color=colors['rose'],
    template='plotly_white',
    yaxis_title="Nilai (Juta Rupiah)",
    xaxis_title="Tahun",
    showlegend=True,
    updatemenus=[{
        'buttons': [
            {
                'args': [{'visible': [True, True, True]}, {'title': 'Tren Keuangan (dalam Juta Rupiah)'}],
                'label': 'Semua',
                'method': 'update'
            },
            {
                'args': [{'visible': [True, False, False]}, {'title': 'Pendapatan (dalam Juta Rupiah)'}],
                'label': 'Pendapatan',
                'method': 'update'
            },
            {
                'args': [{'visible': [False, True, False]}, {'title': 'Beban Operasional (dalam Juta Rupiah)'}],
                'label': 'Beban Operasional',
                'method': 'update'
            },
            {
                'args': [{'visible': [False, False, True]}, {'title': 'Laba Bersih (dalam Juta Rupiah)'}],
                'label': 'Laba Bersih',
                'method': 'update'
            }
        ],
        'direction': 'down',
        'showactive': True,
        'x': 0.1,
        'xanchor': 'left',
        'y': 1.15,
        'yanchor': 'top'
    }]
)

# Creating pie chart for asset distribution
asset_summary = df_aset.groupby('kategori')['nilai_perolehan'].sum().reset_index()
asset_summary['nilai_perolehan'] = asset_summary['nilai_perolehan'] / 1_000_000  # Convert to millions

fig_pie = px.pie(
    asset_summary,
    values='nilai_perolehan',
    names='kategori',
    title='Distribusi Nilai Aset Tetap (dalam Juta Rupiah)',
    color_discrete_sequence=[colors['pastel_pink'], colors['pastel_yellow'], colors['pastel_blue'], colors['rose']]
)

fig_pie.update_traces(textinfo='percent+label', pull=[0.1, 0, 0, 0, 0])
fig_pie.update_layout(
    title_font_color=colors['rose'],
    template='plotly_white'
)

# Save charts as PNG
fig.write_image("financial_trends.png", width=1200, height=600)
fig_pie.write_image("asset_distribution.png", width=800, height=600)

# Building HTML content with escaped curly braces
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Laporan Keuangan</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        table {{ border-collapse: collapse; width: 100%; max-width: 800px; margin: 20px auto; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
        th {{ background-color: #f2f2f2; }}
        h2, h3 {{ color: #E75480; text-align: center; }}
        .container {{ max-width: 1200px; margin: auto; padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Ringkasan Keuangan (dalam Juta Rupiah)</h2>
        {}
        <div id="bar_chart"></div>
        <div id="pie_chart"></div>
        <h3>Fakta Menarik</h3>
        <p>Laba bersih meningkat sebesar {:.2f}% dari 2023 ke 2027, menunjukkan pertumbuhan keuangan yang kuat meskipun adanya fluktuasi beban operasional.</p>
    </div>
"""

# Convert table to HTML and add interesting fact
table_html = summary_table.to_html(index=False, border=1, classes="table")
laba_growth = ((summary_table['Laba Bersih'].iloc[-1] - summary_table['Laba Bersih'].iloc[0]) / summary_table['Laba Bersih'].iloc[0]) * 100
html_content = html_content.format(table_html, laba_growth)

# Add Plotly JavaScript for charts
bar_chart_json = fig.to_json()
pie_chart_json = fig_pie.to_json()
html_content += f"""
    <script>
        var bar_data = {bar_chart_json};
        var pie_data = {pie_chart_json};
        Plotly.newPlot('bar_chart', bar_data.data, bar_data.layout);
        Plotly.newPlot('pie_chart', pie_data.data, pie_data.layout);
    </script>
"""

# Complete HTML
html_content += """
</body>
</html>
"""

# Save report as HTML
with open('laporan_pph_badan_fixed.html', 'w') as f:
    f.write(html_content)

# Display in Colab
display(HTML(html_content))

# Download files in Colab
files.download('laporan_pph_badan_fixed.html')
files.download('financial_trends.png')
files.download('asset_distribution.png')