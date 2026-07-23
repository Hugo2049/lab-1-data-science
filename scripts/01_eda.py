# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Analisis Exploratorio de Datos (EDA) general
Dataset: Base_Migracion_2009-2026jun.xlsx
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "outputs")
os.makedirs(OUT, exist_ok=True)

MESES_ORD = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

# ---------------------------------------------------------------
# 1. Carga y limpieza de nombres de columnas
# ---------------------------------------------------------------
df = pd.read_excel(os.path.join(BASE, "Base_Migracion_2009-2026jun.xlsx"), sheet_name="Datos")
df.columns = ['Anio','Mes_cod','Mes','Via','Frontera','Pais','Region',
              'Region_dos','Region_OMT','MCEO','Agrup_Residencia','Tipo_Viajero','Viajero']

df['Mes'] = df['Mes'].astype(str).str.strip()
for c in ['Via','Frontera','Pais','Region','Region_dos','Region_OMT','MCEO','Agrup_Residencia','Tipo_Viajero']:
    df[c] = df[c].astype(str).str.strip()

df['Fecha'] = pd.to_datetime(df['Anio'].astype(str) + '-' + df['Mes_cod'].astype(str) + '-01')

report = []
def log(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    report.append(s)

log("="*70)
log("1. DESCRIPCION GENERAL DEL DATASET")
log("="*70)
log(f"Filas: {df.shape[0]:,}  Columnas: {df.shape[1]}")
log(f"Periodo cubierto: {df['Fecha'].min().strftime('%Y-%m')} a {df['Fecha'].max().strftime('%Y-%m')}")
log(f"Meses distintos (Anio-Mes): {df.groupby(['Anio','Mes_cod']).ngroups} "
    f"(esperado sin huecos = {(2026-2009)*12+6})")
log("")
log("Tipos de dato:")
log(df.dtypes.to_string())

# ---------------------------------------------------------------
# 2. Valores faltantes, duplicados y atipicos
# ---------------------------------------------------------------
log("")
log("="*70)
log("2. VALORES FALTANTES, DUPLICADOS Y ATIPICOS")
log("="*70)
nulls = df.isnull().sum()
log("Valores nulos por columna:")
log(nulls.to_string())

dups = df.duplicated().sum()
log(f"\nFilas totalmente duplicadas: {dups}")

log(f"\nViajero == 0 (registros con conteo cero): {(df.Viajero==0).sum()}")
log(f"Viajero < 0 (imposible): {(df.Viajero<0).sum()}")
log(f"Viajero con decimales (estimaciones expandidas de encuesta, no error): "
    f"{(df.Viajero % 1 != 0).sum()} filas ({(df.Viajero % 1 != 0).mean()*100:.1f}%)")

# outliers via IQR sobre Viajero (a nivel de fila desagregada)
q1, q3 = df.Viajero.quantile([0.25, 0.75])
iqr = q3 - q1
upper = q3 + 1.5*iqr
n_out = (df.Viajero > upper).sum()
log(f"\nOutliers (IQR, fila desagregada) por encima de {upper:,.1f}: {n_out:,} "
    f"({n_out/len(df)*100:.1f}%) -> esperado: filas desagregadas por pais/frontera/tipo "
    f"tienen muchas colas largas (paises grandes como El Salvador, Honduras, EEUU dominan).")

# categorias inconsistentes detectadas
log("\nCategorias inconsistentes detectadas en 'Region_dos':")
log(df.Region_dos.value_counts().to_string())
log(" -> '0' y 'Cruceros' aparecen solo en 2022 (13 y 8 filas); 'Cruceristas' cubre 2009-2021.")
log("    Es un quiebre de codificacion, no un error aleatorio (ver hoja 'Notas' del archivo).")

# ---------------------------------------------------------------
# 3. Comportamiento temporal (serie total)
# ---------------------------------------------------------------
log("")
log("="*70)
log("3. COMPORTAMIENTO TEMPORAL DEL NUMERO DE VIAJEROS")
log("="*70)
total_mensual = df.groupby('Fecha')['Viajero'].sum().sort_index()
log(f"Min mensual: {total_mensual.min():,.0f} en {total_mensual.idxmin().strftime('%Y-%m')}")
log(f"Max mensual: {total_mensual.max():,.0f} en {total_mensual.idxmax().strftime('%Y-%m')}")
log(f"Promedio mensual: {total_mensual.mean():,.0f}  Desv.Est: {total_mensual.std():,.0f}")

fig, ax = plt.subplots(figsize=(12,5))
ax.plot(total_mensual.index, total_mensual.values, color="#1f77b4", lw=1.2)
ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2021-12-31'), color='red', alpha=0.08, label='Pandemia COVID-19')
ax.axvline(pd.Timestamp('2023-01-01'), color='orange', ls='--', lw=1, label='Quiebre metodologico 2023')
ax.set_title("Total mensual de viajeros internacionales a Guatemala (2009-2026)")
ax.set_xlabel("Fecha"); ax.set_ylabel("Viajeros")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "01_total_mensual.png"))
plt.close(fig)

# Turista+Excursionista (comparable en todo el periodo, segun instrucciones del lab)
te = df[df.Tipo_Viajero.isin(['Turista','Excursionista'])].groupby('Fecha')['Viajero'].sum().sort_index()
fig, ax = plt.subplots(figsize=(12,5))
ax.plot(te.index, te.values, color="#2ca02c", lw=1.2)
ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2021-12-31'), color='red', alpha=0.08, label='Pandemia COVID-19')
ax.set_title("Turista + Excursionista (comparable en todo el periodo 2009-2026)")
ax.set_xlabel("Fecha"); ax.set_ylabel("Viajeros")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "02_turista_excursionista.png"))
plt.close(fig)

# Estacionalidad promedio por mes
prom_mes = df.groupby('Mes_cod')['Viajero'].sum().reindex(range(1,13))
fig, ax = plt.subplots(figsize=(9,4.5))
ax.bar(MESES_ORD, prom_mes.values, color="#1f77b4")
ax.set_title("Total acumulado de viajeros por mes del anio (2009-2026, todos los anios)")
ax.set_ylabel("Viajeros (suma historica)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
fig.tight_layout()
fig.savefig(os.path.join(OUT, "03_estacionalidad_mensual.png"))
plt.close(fig)

# ---------------------------------------------------------------
# 4. Paises con mayor cantidad de viajeros
# ---------------------------------------------------------------
log("")
log("="*70)
log("4. PAISES CON MAYOR CANTIDAD DE VIAJEROS (acumulado 2009-2026)")
log("="*70)
top_paises = df.groupby('Pais')['Viajero'].sum().sort_values(ascending=False)
log(top_paises.head(15).to_string())
log(f"\nNota: desde 2023 'Pais' cambia a agrupacion de mercado (27 grupos) en vez de pais individual (226).")
log(f"Los 3 paises/agrupaciones con mayor acumulado historico (criterio del lab) son:")
log(top_paises.head(3).to_string())

fig, ax = plt.subplots(figsize=(9,6))
top15 = top_paises.head(15).sort_values()
ax.barh(top15.index, top15.values, color="#ff7f0e")
ax.set_title("Top 15 paises/agrupaciones por viajeros acumulados (2009-2026)")
ax.set_xlabel("Viajeros acumulados")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
fig.tight_layout()
fig.savefig(os.path.join(OUT, "04_top_paises.png"))
plt.close(fig)

# ---------------------------------------------------------------
# 5. Regiones con mayor cantidad de viajeros
# ---------------------------------------------------------------
log("")
log("="*70)
log("5. REGIONES CON MAYOR CANTIDAD DE VIAJEROS (Region dos, acumulado)")
log("="*70)
top_reg = df.groupby('Region_dos')['Viajero'].sum().sort_values(ascending=False)
log(top_reg.to_string())
log(f"\nLas 3 regiones (Region dos) con mayor acumulado (criterio del lab):")
log(top_reg.head(3).to_string())

fig, ax = plt.subplots(figsize=(9,5))
tr = top_reg.sort_values()
ax.barh(tr.index, tr.values, color="#9467bd")
ax.set_title("Viajeros acumulados por Region dos (2009-2026)")
ax.set_xlabel("Viajeros acumulados")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
fig.tight_layout()
fig.savefig(os.path.join(OUT, "05_top_regiones.png"))
plt.close(fig)

# ---------------------------------------------------------------
# 6. Vias de ingreso y fronteras mas utilizadas
# ---------------------------------------------------------------
log("")
log("="*70)
log("6. VIAS DE INGRESO Y FRONTERAS MAS UTILIZADAS")
log("="*70)
top_via = df.groupby('Via')['Viajero'].sum().sort_values(ascending=False)
log("Por Via:")
log(top_via.to_string())
log(f"\n% del total por via:")
log((top_via/top_via.sum()*100).round(2).to_string())

top_front = df.groupby('Frontera')['Viajero'].sum().sort_values(ascending=False)
log("\nTop 10 Fronteras (acumulado):")
log(top_front.head(10).to_string())
log(f"\nLas 3 fronteras con mayor acumulado (criterio del lab):")
log(top_front.head(3).to_string())

fig, axes = plt.subplots(1, 2, figsize=(13,5))
axes[0].pie(top_via.values, labels=top_via.index, autopct='%1.1f%%', colors=["#1f77b4","#2ca02c","#d62728"])
axes[0].set_title("Distribucion de viajeros por Via de ingreso")
tf = top_front.head(10).sort_values()
axes[1].barh(tf.index, tf.values, color="#17becf")
axes[1].set_title("Top 10 Fronteras por viajeros acumulados")
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
fig.tight_layout()
fig.savefig(os.path.join(OUT, "06_via_frontera.png"))
plt.close(fig)

# ---------------------------------------------------------------
# 7. Tipo de viajero
# ---------------------------------------------------------------
log("")
log("="*70)
log("7. TIPO DE VIAJERO")
log("="*70)
top_tipo = df.groupby('Tipo_Viajero')['Viajero'].sum().sort_values(ascending=False)
log(top_tipo.to_string())

# comportamiento anual por tipo (para ver el quiebre 2022->2023 mencionado en Notas)
anual_tipo = df.groupby(['Anio','Tipo_Viajero'])['Viajero'].sum().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12,5))
for col in anual_tipo.columns:
    ax.plot(anual_tipo.index, anual_tipo[col], marker='o', ms=3, label=col)
ax.axvline(2022.5, color='orange', ls='--', lw=1, label='Quiebre metodologico 2023')
ax.set_title("Viajeros por anio segun Tipo de Viajero (muestra el quiebre metodologico 2022->2023)")
ax.set_xlabel("Anio"); ax.set_ylabel("Viajeros")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "07_tipo_viajero_anual.png"))
plt.close(fig)

# ---------------------------------------------------------------
# 8. Estadisticas descriptivas (a nivel de fila y de serie mensual total)
# ---------------------------------------------------------------
log("")
log("="*70)
log("8. ESTADISTICAS DESCRIPTIVAS")
log("="*70)
log("Variable 'Viajero' a nivel de fila desagregada (161,036 registros):")
log(df.Viajero.describe().to_string())
log("\nVariable 'Total mensual' (serie agregada, 210 meses):")
log(total_mensual.describe().to_string())

fig, axes = plt.subplots(1, 2, figsize=(12,4.5))
axes[0].boxplot(np.log1p(df.Viajero), vert=True)
axes[0].set_title("Boxplot de Viajero (escala log1p)\nfila desagregada")
axes[0].set_xticklabels(["Viajero"])
axes[1].boxplot(total_mensual.values, vert=True)
axes[1].set_title("Boxplot Total mensual\n(serie agregada, 2009-2026)")
axes[1].set_xticklabels(["Total mensual"])
fig.tight_layout()
fig.savefig(os.path.join(OUT, "08_boxplots.png"))
plt.close(fig)

with open(os.path.join(OUT, "reporte_eda.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))

log("\n\nListo. Graficos guardados en:", OUT)
