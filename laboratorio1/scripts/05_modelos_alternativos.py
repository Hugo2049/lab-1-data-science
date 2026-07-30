# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Punto 4, inciso h: modelos alternativos al ARIMA para cada serie.
  - Prophet (Meta)
  - Holt-Winters (suavizamiento exponencial triple, con estacionalidad)
  - Suavizamiento exponencial simple
  - Seasonal naive

Todos se ajustan sobre el mismo conjunto de entrenamiento y pronostican los
63 meses del conjunto de prueba, de modo que las metricas sean comparables
con las del ARIMA del script 04.
"""
import json
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_utils import (OUT, SEASONAL_PERIOD, SERIES_CATALOG, Reporter, ensure_dir,
                       error_metrics, inverse_transform, load_series,
                       seasonal_naive_forecast, split_series, transform)

warnings.filterwarnings("ignore")
logging.getLogger("prophet").setLevel(logging.CRITICAL)
logging.getLogger("cmdstanpy").setLevel(logging.CRITICAL)
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

FIG = ensure_dir(os.path.join(OUT, "alternativos"))
TAB = ensure_dir(os.path.join(OUT, "tablas"))
PRED = ensure_dir(os.path.join(OUT, "predicciones"))

log = Reporter()

with open(os.path.join(TAB, "diagnostico_series.json"), encoding="utf-8") as f:
    DIAGNOSTICO = {d["serie"]: d for d in json.load(f)}


def ajustar_prophet(s_train, horizonte, index_test):
    """Prophet con estacionalidad anual sobre la serie en niveles."""
    from prophet import Prophet
    df = pd.DataFrame({"ds": s_train.index, "y": s_train.values})
    modelo = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                     daily_seasonality=False, seasonality_mode="multiplicative",
                     interval_width=0.95)
    modelo.fit(df)
    futuro = pd.DataFrame({"ds": index_test})
    pronostico = modelo.predict(futuro)
    return np.clip(pronostico["yhat"].values, 0, None)


def modelar_serie(nombre, titulo, categoria, color):
    log("=" * 78)
    log(f"SERIE: {titulo}")
    log("=" * 78)

    diag = DIAGNOSTICO[nombre]
    usar_log, log1p = diag["usar_log"], diag["log1p"]

    s_full = load_series(nombre)
    s_train, s_test = split_series(s_full)
    y_train = transform(s_train, usar_log, log1p)
    horizonte = len(s_test)

    pronosticos, filas = {}, []

    # --- Holt-Winters (tendencia y estacionalidad aditivas sobre el log) --
    hw = ExponentialSmoothing(y_train, trend="add", seasonal="add",
                              seasonal_periods=SEASONAL_PERIOD,
                              initialization_method="estimated").fit()
    pronosticos["Holt-Winters"] = inverse_transform(
        hw.forecast(horizonte).values, usar_log, log1p)
    filas.append({"modelo": "Holt-Winters", "AIC": round(float(hw.aic), 2),
                  "BIC": round(float(hw.bic), 2)})

    # --- Suavizamiento exponencial simple ---------------------------------
    ses = SimpleExpSmoothing(y_train, initialization_method="estimated").fit()
    pronosticos["Suavizamiento exponencial simple"] = inverse_transform(
        ses.forecast(horizonte).values, usar_log, log1p)
    filas.append({"modelo": "Suavizamiento exponencial simple",
                  "AIC": round(float(ses.aic), 2), "BIC": round(float(ses.bic), 2)})

    # --- Seasonal naive ----------------------------------------------------
    pronosticos["Seasonal naive"] = seasonal_naive_forecast(
        s_train.values, horizonte, SEASONAL_PERIOD)
    filas.append({"modelo": "Seasonal naive", "AIC": np.nan, "BIC": np.nan})

    # --- Prophet -----------------------------------------------------------
    pronosticos["Prophet"] = ajustar_prophet(s_train, horizonte, s_test.index)
    filas.append({"modelo": "Prophet", "AIC": np.nan, "BIC": np.nan})

    registros = []
    for fila in filas:
        metricas = error_metrics(s_test.values, pronosticos[fila["modelo"]])
        registros.append({"serie": nombre, "titulo": titulo, "categoria": categoria,
                          **fila, **metricas})

    tabla = pd.DataFrame(registros).sort_values("RMSE")
    log(tabla[["modelo", "AIC", "BIC", "MAE", "RMSE", "MAPE"]].to_string(index=False))
    log(f"   Mejor de los cuatro por RMSE: {tabla.iloc[0]['modelo']}")
    log("")

    # --- Grafico comparativo -----------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.plot(s_train.index[-36:], s_train.values[-36:], color="#666666", lw=1,
            label="Entrenamiento (ultimos 36 meses)")
    ax.plot(s_test.index, s_test.values, color="black", lw=1.6, label="Prueba (real)")
    estilos = {"Prophet": "-", "Holt-Winters": "--",
               "Suavizamiento exponencial simple": ":", "Seasonal naive": "-."}
    for etiqueta, valores in pronosticos.items():
        ax.plot(s_test.index, valores, ls=estilos[etiqueta], lw=1.3, label=etiqueta)
    ax.set_title(f"{titulo} - modelos alternativos sobre el conjunto de prueba")
    ax.set_ylabel("Viajeros")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_alternativos.png"))
    plt.close(fig)

    salida = pd.DataFrame({"fecha": s_test.index, "real": s_test.values})
    for etiqueta, valores in pronosticos.items():
        salida[etiqueta] = valores
    salida.to_csv(os.path.join(PRED, f"{nombre}_alternativos.csv"),
                  index=False, encoding="utf-8")

    return tabla


tablas = [modelar_serie(nombre, titulo, categoria, color)
          for nombre, (titulo, categoria, color) in SERIES_CATALOG.items()]

completa = pd.concat(tablas)
completa.to_csv(os.path.join(TAB, "modelos_alternativos.csv"), index=False, encoding="utf-8")

log("=" * 78)
log("RESUMEN: MEJOR MODELO ALTERNATIVO POR SERIE (menor RMSE)")
log("=" * 78)
mejores = completa.loc[completa.groupby("serie")["RMSE"].idxmin()]
log(mejores[["serie", "modelo", "MAE", "RMSE", "MAPE"]].to_string(index=False))

log.save(os.path.join(OUT, "reporte_alternativos.txt"))
print("\nFiguras en:", FIG)
