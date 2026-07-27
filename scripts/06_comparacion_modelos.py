# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Punto 4, incisos i, j y k: reune las predicciones de todos los algoritmos
sobre el conjunto de prueba, compara MAE, RMSE, MAPE, AIC y BIC, y selecciona
el mejor modelo de cada serie.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_utils import (OUT, SERIES_CATALOG, Reporter, ensure_dir, error_metrics,
                       load_series, split_series)

warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

FIG = ensure_dir(os.path.join(OUT, "comparacion"))
TAB = os.path.join(OUT, "tablas")
PRED = os.path.join(OUT, "predicciones")

log = Reporter()

arima = pd.read_csv(os.path.join(TAB, "arima_mejor_por_serie.csv"))
alternativos = pd.read_csv(os.path.join(TAB, "modelos_alternativos.csv"))

filas = []
for _, r in arima.iterrows():
    filas.append({"serie": r["serie"], "titulo": r["titulo"], "categoria": r["categoria"],
                  "modelo": r["modelo"], "familia": "ARIMA", "AIC": r["AIC"], "BIC": r["BIC"],
                  "MAE": r["MAE"], "RMSE": r["RMSE"], "MAPE": r["MAPE"]})
for _, r in alternativos.iterrows():
    filas.append({"serie": r["serie"], "titulo": r["titulo"], "categoria": r["categoria"],
                  "modelo": r["modelo"], "familia": r["modelo"], "AIC": r["AIC"], "BIC": r["BIC"],
                  "MAE": r["MAE"], "RMSE": r["RMSE"], "MAPE": r["MAPE"]})

comparacion = pd.DataFrame(filas)
comparacion.to_csv(os.path.join(TAB, "comparacion_modelos.csv"), index=False, encoding="utf-8")

log("=" * 78)
log("COMPARACION DE MODELOS POR SERIE (conjunto de prueba: 2021-04 a 2026-06)")
log("=" * 78)
log("Nota: AIC y BIC solo son comparables dentro de una misma familia y sobre la")
log("misma transformacion de la serie; el seasonal naive y Prophet no los reportan.")
log("")

resumen_mejores = []
for nombre, (titulo, categoria, color) in SERIES_CATALOG.items():
    sub = comparacion[comparacion.serie == nombre].sort_values("RMSE")
    log(f"--- {titulo} ---")
    log(sub[["modelo", "AIC", "BIC", "MAE", "RMSE", "MAPE"]].to_string(index=False))
    mejor = sub.iloc[0]
    log(f"    Mejor modelo por RMSE: {mejor['modelo']} "
        f"(MAE={mejor['MAE']:,.0f}, RMSE={mejor['RMSE']:,.0f}, MAPE={mejor['MAPE']:.1f}%)")
    log("")
    resumen_mejores.append({"serie": nombre, "titulo": titulo, "categoria": categoria,
                            "mejor_modelo": mejor["modelo"], "MAE": mejor["MAE"],
                            "RMSE": mejor["RMSE"], "MAPE": mejor["MAPE"]})

    # --- Grafico: todos los pronosticos frente al valor real ---------------
    s_full = load_series(nombre)
    s_train, s_test = split_series(s_full)
    pred_arima = pd.read_csv(os.path.join(PRED, f"{nombre}_arima.csv"), parse_dates=["fecha"])
    pred_alt = pd.read_csv(os.path.join(PRED, f"{nombre}_alternativos.csv"), parse_dates=["fecha"])

    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.plot(s_train.index[-24:], s_train.values[-24:], color="#888888", lw=1,
            label="Entrenamiento (ultimos 24 meses)")
    ax.plot(s_test.index, s_test.values, color="black", lw=1.8, label="Prueba (real)")
    ax.plot(pred_arima["fecha"], pred_arima["prediccion"], lw=1.3, label="ARIMA")
    for columna in ["Prophet", "Holt-Winters", "Suavizamiento exponencial simple", "Seasonal naive"]:
        ax.plot(pred_alt["fecha"], pred_alt[columna], lw=1.2, ls="--", label=columna)
    ax.set_title(f"{titulo} - comparacion de todos los modelos")
    ax.set_ylabel("Viajeros")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_comparacion.png"))
    plt.close(fig)

df_mejores = pd.DataFrame(resumen_mejores)
df_mejores.to_csv(os.path.join(TAB, "mejor_modelo_por_serie.csv"), index=False, encoding="utf-8")

# --- Grafico resumen: RMSE relativo por modelo y serie ---------------------
pivote = comparacion.pivot_table(index="serie", columns="familia", values="RMSE")
pivote_rel = pivote.div(pivote.min(axis=1), axis=0)   # 1.0 = mejor modelo de esa serie

fig, ax = plt.subplots(figsize=(11, 5))
pivote_rel.plot(kind="bar", ax=ax, width=0.8)
ax.set_yscale("log")
ax.set_ylabel("RMSE relativo al mejor modelo de cada serie (escala log)")
ax.set_xlabel("")
ax.axhline(1, color="black", lw=1)
ax.set_title("Desempeno relativo de cada algoritmo sobre el conjunto de prueba")
ax.legend(fontsize=8, ncol=2)
plt.xticks(rotation=25, ha="right")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "resumen_rmse_relativo.png"))
plt.close(fig)

log("=" * 78)
log("MEJOR MODELO POR SERIE")
log("=" * 78)
log(df_mejores[["serie", "mejor_modelo", "MAE", "RMSE", "MAPE"]].to_string(index=False))
log("")
conteo = df_mejores["mejor_modelo"].apply(
    lambda m: "ARIMA" if m.startswith("SARIMA") else m).value_counts()
log("Veces que cada algoritmo resulta el mejor:")
log(conteo.to_string())

log.save(os.path.join(OUT, "reporte_comparacion.txt"))
print("\nFiguras en:", FIG)
