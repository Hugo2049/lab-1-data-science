# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Paso 2 y 3: split train/test (70/30, cronologico) y construccion de series
mensuales: Total (obligatoria), Vias de ingreso (Aerea/Terrestre/Maritima)
y Paises de residencia Top 3 (El Salvador, Guatemala, Estados Unidos).
"""
import pandas as pd
import numpy as np
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "outputs", "series")
os.makedirs(OUT, exist_ok=True)

df = pd.read_excel(os.path.join(BASE, "Base_Migracion_2009-2026jun.xlsx"), sheet_name="Datos")
df.columns = ['Anio','Mes_cod','Mes','Via','Frontera','Pais','Region',
              'Region_dos','Region_OMT','MCEO','Agrup_Residencia','Tipo_Viajero','Viajero']
df['Fecha'] = pd.to_datetime(df['Anio'].astype(str) + '-' + df['Mes_cod'].astype(str) + '-01')

# ---------------------------------------------------------------
# Split cronologico 70/30 a nivel de fila (segun instrucciones del lab)
# ---------------------------------------------------------------
SPLIT_DATE = pd.Timestamp('2021-04-01')   # primer mes de test
df['set'] = np.where(df['Fecha'] < SPLIT_DATE, 'train', 'test')

n_train_meses = df.loc[df.set=='train', 'Fecha'].nunique()
n_test_meses = df.loc[df.set=='test', 'Fecha'].nunique()
print(f"Train: {df.Fecha.min().strftime('%Y-%m')} a "
      f"{df.loc[df.set=='train','Fecha'].max().strftime('%Y-%m')} "
      f"({n_train_meses} meses, {(df.set=='train').sum():,} filas)")
print(f"Test:  {df.loc[df.set=='test','Fecha'].min().strftime('%Y-%m')} a "
      f"{df.Fecha.max().strftime('%Y-%m')} "
      f"({n_test_meses} meses, {(df.set=='test').sum():,} filas)")
print(f"Proporcion train: {n_train_meses/(n_train_meses+n_test_meses)*100:.1f}%")

df.to_csv(os.path.join(BASE, "outputs", "datos_con_split.csv"), index=False, encoding="utf-8")

# ---------------------------------------------------------------
# Construccion de series mensuales
# Nota: las series completas (train+test) se guardan para graficar/evaluar;
# el analisis de estacionariedad/ACF/ADF de la seccion 4 se hace SOLO
# sobre el tramo de entrenamiento, como corresponde a un flujo de modelado.
# ---------------------------------------------------------------
FULL_RANGE = pd.date_range('2009-01-01', '2026-06-01', freq='MS')

def serie_mensual(mask, nombre):
    """Agrega a mensual y rellena con 0 los meses sin filas (=0 viajeros
    reales, confirmado: coinciden con el cierre de fronteras abr-ago 2020
    y con la perdida de detalle de registro maritimo desde 2017)."""
    sub = df[mask]
    s = sub.groupby('Fecha')['Viajero'].sum().sort_index()
    s = s.reindex(FULL_RANGE, fill_value=0.0)
    s.index.freq = 'MS'
    s.name = nombre
    return s

series = {}
series['Total'] = serie_mensual(df.Viajero.notna(), 'Total')

for via in ['Aérea', 'Terrestre', 'Marítima']:
    series[f'Via_{via}'] = serie_mensual(df.Via == via, f'Via_{via}')

# Nota: 'Guatemala' es el pais #2 por acumulado historico en la columna Pais,
# pero esa categoria DESAPARECE del catalogo desde 2023 (el nuevo catalogo de
# 'agrupacion de mercado' ya no incluye residentes guatemaltecos reingresando).
# Su serie mensual no puede extenderse mas alla de 2022-12, lo que rompe el
# conjunto de prueba (test llega hasta 2026-06). Para el modelado de series de
# tiempo se sustituye por Honduras (#4 en el ranking, serie completa 2009-2026).
# El hallazgo sobre Guatemala se documenta igual en el EDA (seccion de paises).
for pais in ['El Salvador', 'Honduras', 'Estados Unidos de América']:
    key = {'El Salvador': 'ElSalvador', 'Honduras': 'Honduras',
           'Estados Unidos de América': 'EstadosUnidos'}[pais]
    series[f'Pais_{key}'] = serie_mensual(df.Pais == pais, f'Pais_{key}')

resumen = []
for nombre, s in series.items():
    train_s = s[s.index < SPLIT_DATE]
    test_s = s[s.index >= SPLIT_DATE]
    resumen.append({
        'serie': nombre,
        'inicio': s.index.min().strftime('%Y-%m'),
        'fin': s.index.max().strftime('%Y-%m'),
        'n_obs': len(s),
        'n_train': len(train_s),
        'n_test': len(test_s),
        'n_nulos': s.isna().sum(),
        'freq': s.index.freqstr,
    })
    # guardar CSVs
    s.to_frame('viajeros').to_csv(os.path.join(OUT, f"{nombre}_completa.csv"))
    train_s.to_frame('viajeros').to_csv(os.path.join(OUT, f"{nombre}_train.csv"))
    test_s.to_frame('viajeros').to_csv(os.path.join(OUT, f"{nombre}_test.csv"))

resumen_df = pd.DataFrame(resumen)
print()
print(resumen_df.to_string(index=False))
resumen_df.to_csv(os.path.join(OUT, "_resumen_series.csv"), index=False)
print("\nSeries guardadas en:", OUT)
