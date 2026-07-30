# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Punto 4, incisos f y g: seleccion de los parametros p, d, q (y su contraparte
estacional), ajuste de varios modelos ARIMA/SARIMA sobre el conjunto de
entrenamiento, diagnostico de residuos y comparacion por AIC y BIC.

La estrategia sigue el orden estandar: las diferenciaciones d y D vienen del
analisis de raices unitarias del script 03 (comparar AIC entre modelos con
distinto grado de diferenciacion no es valido), y sobre esas diferenciaciones
fijas se explora una malla de ordenes p, q, P y Q.
"""
import itertools
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_utils import (OUT, SEASONAL_PERIOD, SERIES_CATALOG, Reporter, ensure_dir,
                       error_metrics, inverse_transform, load_series, split_series,
                       transform)

warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

FIG = ensure_dir(os.path.join(OUT, "arima"))
TAB = ensure_dir(os.path.join(OUT, "tablas"))
PRED = ensure_dir(os.path.join(OUT, "predicciones"))

log = Reporter()

with open(os.path.join(TAB, "diagnostico_series.json"), encoding="utf-8") as f:
    DIAGNOSTICO = {d["serie"]: d for d in json.load(f)}


def fit_sarimax(y, order, seasonal_order):
    """Ajusta un SARIMAX; devuelve None si el ajuste no converge."""
    try:
        # Se imponen estacionariedad e invertibilidad: sin esa restriccion algunos
        # ajustes quedan con raices explosivas y, al deshacer el logaritmo en un
        # horizonte de 63 meses, el pronostico diverge a valores absurdos.
        model = SARIMAX(y, order=order, seasonal_order=seasonal_order,
                        enforce_stationarity=True, enforce_invertibility=True)
        return model.fit(disp=False, maxiter=200)
    except Exception:
        return None


def burn_in(d, D):
    """Observaciones iniciales a descartar por la inicializacion difusa del filtro.

    Con d diferencias regulares y D estacionales, los primeros d + D*12 residuos
    son enormes y, si se incluyen, inflan la varianza y vuelven inservible la
    prueba de Ljung-Box.
    """
    return d + D * SEASONAL_PERIOD + 1


def residual_diagnostics(res, d, D):
    """Ljung-Box (autocorrelacion) y Jarque-Bera (normalidad) sobre los residuos."""
    resid = pd.Series(res.resid).iloc[burn_in(d, D):].dropna()
    lb = acorr_ljungbox(resid, lags=[24], return_df=True)
    jb_p = float(res.test_normality("jarquebera")[0][1])
    return float(lb["lb_pvalue"].iloc[0]), jb_p


def evaluar_serie(nombre, titulo, categoria, color):
    log("=" * 78)
    log(f"SERIE: {titulo}")
    log("=" * 78)

    diag = DIAGNOSTICO[nombre]
    usar_log, log1p = diag["usar_log"], diag["log1p"]
    d, D = diag["d"], diag["D"]

    s_full = load_series(nombre)
    s_train, s_test = split_series(s_full)
    y_train = transform(s_train, usar_log, log1p)

    log(f"f) Transformacion: {'logaritmica' if usar_log else 'ninguna'}. "
        f"Diferenciacion fijada por las pruebas de raiz unitaria: d={d}, D={D} (periodo 12).")
    log(f"   Sobre esa base se exploran ordenes p,q en {{0,1,2}} y P,Q en {{0,1}}, "
        f"comparables entre si por tener el mismo grado de diferenciacion.")

    # --- Malla de modelos candidatos ------------------------------------
    resultados = []
    for p, q, P, Q in itertools.product(range(3), range(3), range(2), range(2)):
        res = fit_sarimax(y_train, (p, d, q), (P, D, Q, SEASONAL_PERIOD))
        if res is None or not np.isfinite(res.aic):
            continue
        lb_p, jb_p = residual_diagnostics(res, d, D)
        resultados.append({
            "serie": nombre,
            "modelo": f"SARIMA({p},{d},{q})({P},{D},{Q})[12]",
            "p": p, "d": d, "q": q, "P": P, "D": D, "Q": Q,
            "AIC": round(float(res.aic), 2),
            "BIC": round(float(res.bic), 2),
            "ljung_box_p": round(lb_p, 4),
            "jarque_bera_p": round(jb_p, 4),
            "_res": res,
        })

    resultados.sort(key=lambda r: r["AIC"])
    tabla = pd.DataFrame([{k: v for k, v in r.items() if k != "_res"} for r in resultados])

    log(f"g) Se ajustaron {len(resultados)} modelos. Los cinco mejores por AIC:")
    log(tabla.head(5)[["modelo", "AIC", "BIC", "ljung_box_p", "jarque_bera_p"]]
        .to_string(index=False))

    # El mejor modelo debe combinar buen AIC con residuos sin autocorrelacion
    con_residuos_limpios = [r for r in resultados if r["ljung_box_p"] > 0.05]
    mejor = con_residuos_limpios[0] if con_residuos_limpios else resultados[0]
    if con_residuos_limpios:
        log(f"   Modelo elegido: {mejor['modelo']} - el de menor AIC entre los que dejan "
            f"residuos sin autocorrelacion (Ljung-Box p={mejor['ljung_box_p']:.3f} > 0.05).")
    else:
        log(f"   Modelo elegido: {mejor['modelo']} - ningun candidato supera Ljung-Box, "
            f"se toma el de menor AIC y se advierte autocorrelacion residual.")

    res_mejor = mejor["_res"]

    # --- Diagnostico de residuos del modelo elegido ----------------------
    resid = pd.Series(res_mejor.resid, index=y_train.index).iloc[burn_in(d, D):]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes[0][0].plot(resid.index, resid.values, color=color, lw=0.9)
    axes[0][0].axhline(0, color="black", lw=0.8)
    axes[0][0].set_title("Residuos en el tiempo")
    axes[0][1].hist(resid.values, bins=25, color=color, alpha=0.8)
    axes[0][1].set_title("Histograma de residuos")
    plot_acf(resid, ax=axes[1][0], lags=36, color=color)
    axes[1][0].set_title("ACF de los residuos")
    from scipy import stats
    stats.probplot(resid.values, dist="norm", plot=axes[1][1])
    axes[1][1].set_title("Grafico cuantil-cuantil")
    fig.suptitle(f"{titulo} - diagnostico de residuos de {mejor['modelo']}")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_residuos.png"))
    plt.close(fig)

    # --- Prediccion sobre el conjunto de prueba --------------------------
    horizonte = len(s_test)
    pred = res_mejor.get_forecast(steps=horizonte)
    media = inverse_transform(pred.predicted_mean.values, usar_log, log1p)
    intervalo = pred.conf_int(alpha=0.05).values
    low = inverse_transform(intervalo[:, 0], usar_log, log1p)
    high = inverse_transform(intervalo[:, 1], usar_log, log1p)

    metricas = error_metrics(s_test.values, media)
    log(f"   Prediccion a {horizonte} meses sobre el conjunto de prueba: "
        f"MAE={metricas['MAE']:,.0f}  RMSE={metricas['RMSE']:,.0f}  MAPE={metricas['MAPE']:.1f}%")
    log("")

    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(s_train.index, s_train.values, color="#666666", lw=1, label="Entrenamiento")
    ax.plot(s_test.index, s_test.values, color="black", lw=1.3, label="Prueba (real)")
    ax.plot(s_test.index, media, color=color, lw=1.6, label=f"Pronostico {mejor['modelo']}")
    ax.fill_between(s_test.index, low, high, color=color, alpha=0.15, label="Intervalo 95%")
    ax.set_title(f"{titulo} - pronostico ARIMA sobre el conjunto de prueba")
    ax.set_ylabel("Viajeros")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_pronostico.png"))
    plt.close(fig)

    pd.DataFrame({"fecha": s_test.index, "real": s_test.values, "prediccion": media,
                  "inferior": low, "superior": high}).to_csv(
        os.path.join(PRED, f"{nombre}_arima.csv"), index=False, encoding="utf-8")

    return tabla, {
        "serie": nombre,
        "titulo": titulo,
        "categoria": categoria,
        "modelo": mejor["modelo"],
        "AIC": mejor["AIC"],
        "BIC": mejor["BIC"],
        "ljung_box_p": mejor["ljung_box_p"],
        "jarque_bera_p": mejor["jarque_bera_p"],
        "n_modelos_probados": len(resultados),
        **metricas,
    }


tablas, mejores = [], []
for nombre, (titulo, categoria, color) in SERIES_CATALOG.items():
    tabla, mejor = evaluar_serie(nombre, titulo, categoria, color)
    tablas.append(tabla)
    mejores.append(mejor)

pd.concat(tablas).to_csv(os.path.join(TAB, "arima_todos_los_modelos.csv"),
                         index=False, encoding="utf-8")
df_mejores = pd.DataFrame(mejores)
df_mejores.to_csv(os.path.join(TAB, "arima_mejor_por_serie.csv"), index=False, encoding="utf-8")

log("=" * 78)
log("MEJOR MODELO ARIMA POR SERIE")
log("=" * 78)
log(df_mejores[["serie", "modelo", "AIC", "BIC", "ljung_box_p", "MAE", "RMSE", "MAPE"]]
    .to_string(index=False))

log.save(os.path.join(OUT, "reporte_arima.txt"))
print("\nFiguras en:", FIG)
