# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Punto 4, incisos a-e, para las siete series construidas:
  a. Inicio, fin y frecuencia.
  b. Grafico de la serie.
  c. Descomposicion y discusion de estacionariedad en media y varianza.
  d. Necesidad de transformar la serie.
  e. ACF/PACF y prueba de Dickey-Fuller aumentada (complementada con KPSS).

El diagnostico de estacionariedad se hace sobre el tramo de ENTRENAMIENTO
(2009-01 a 2021-03); el grafico general se muestra sobre la serie completa
para dar contexto.
"""
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
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_utils import (BASE, OUT, SEASONAL_PERIOD, SERIES_CATALOG, SPLIT_DATE,
                       Reporter, ensure_dir, load_series, split_series,
                       transform, uses_log1p)

warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

FIG = ensure_dir(os.path.join(OUT, "series_analisis"))
TAB = ensure_dir(os.path.join(OUT, "tablas"))

log = Reporter()


def adf_test(series, label):
    """Dickey-Fuller aumentada; devuelve un dict con el resultado."""
    stat, pvalue, lags, nobs, crit, _ = adfuller(series.dropna(), autolag="AIC")
    return {
        "prueba": label,
        "estadistico": round(float(stat), 3),
        "p_valor": round(float(pvalue), 4),
        "lags": int(lags),
        "n": int(nobs),
        "critico_5pct": round(float(crit["5%"]), 3),
        "conclusion": "Estacionaria" if pvalue < 0.05 else "No estacionaria",
    }


def kpss_test(series):
    """KPSS con hipotesis nula de estacionariedad (complemento de ADF)."""
    stat, pvalue, _, _ = kpss(series.dropna(), regression="c", nlags="auto")
    return {
        "estadistico": round(float(stat), 3),
        "p_valor": round(float(pvalue), 4),
        "conclusion": "No estacionaria" if pvalue < 0.05 else "Estacionaria",
    }


def strengths(series):
    """Fuerza de tendencia y de estacionalidad a partir de una descomposicion STL."""
    stl = STL(series, period=SEASONAL_PERIOD, robust=True).fit()
    resid_var = np.var(stl.resid)
    trend_strength = max(0.0, 1 - resid_var / np.var(stl.trend + stl.resid))
    seasonal_strength = max(0.0, 1 - resid_var / np.var(stl.seasonal + stl.resid))
    return float(trend_strength), float(seasonal_strength)


def choose_d(series, max_d=2):
    """Numero minimo de diferenciaciones regulares para que ADF rechace la raiz unitaria."""
    current = series.copy()
    for d in range(max_d + 1):
        if adfuller(current.dropna(), autolag="AIC")[1] < 0.05:
            return d
        current = current.diff()
    return max_d


def choose_orders(series):
    """Determina D y luego d, en ese orden.

    La fuerza estacional se mide sobre la ventana previa a marzo de 2020: el
    desplome de la pandemia domina la varianza del tramo final y enmascara el
    patron anual, subestimando la estacionalidad real de la serie.
    """
    pre_covid = series[series.index < "2020-03-01"]
    _, seasonal_pre = strengths(pre_covid)
    D = 1 if seasonal_pre > 0.4 else 0
    base = series.diff(SEASONAL_PERIOD) if D else series
    # Se limita a una diferencia regular: una segunda diferencia rara vez se
    # justifica y vuelve inestable el pronostico a horizontes largos.
    d = choose_d(base.dropna(), max_d=1)
    return d, D, float(seasonal_pre)


def analizar_serie(nombre, titulo, categoria, color):
    log("=" * 78)
    log(f"SERIE: {titulo}  [categoria: {categoria}]")
    log("=" * 78)

    s_full = load_series(nombre)
    s_train, s_test = split_series(s_full)

    # ---- a. Inicio, fin y frecuencia -----------------------------------
    log(f"a) Inicio: {s_full.index.min():%Y-%m}   Fin: {s_full.index.max():%Y-%m}   "
        f"Frecuencia: mensual (MS)   Observaciones: {len(s_full)} "
        f"(entrenamiento {len(s_train)}, prueba {len(s_test)})")

    # ---- b. Grafico de la serie ----------------------------------------
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(s_full.index, s_full.values, color=color, lw=1.1)
    ax.axvspan(s_full.index.min(), SPLIT_DATE, color=color, alpha=0.06,
               label="Entrenamiento (70%)")
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-31"),
               color="red", alpha=0.07, label="Pandemia COVID-19")
    ax.axvline(SPLIT_DATE, color="black", ls="--", lw=1)
    ax.set_title(f"{titulo} - serie mensual completa (2009-2026)")
    ax.set_ylabel("Viajeros")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_01_serie.png"))
    plt.close(fig)

    pre_covid = s_full[s_full.index < "2020-03-01"]
    crecimiento = (pre_covid[-24:].mean() / pre_covid[:24].mean() - 1) * 100
    piso_covid = s_full["2020-03-01":"2021-12-31"].min()
    log(f"b) Crecimiento del nivel medio entre los primeros y los ultimos 24 meses previos "
        f"a la pandemia: {crecimiento:+.1f}%. Piso durante la pandemia: {piso_covid:,.0f} viajeros.")

    # ---- c. Descomposicion ---------------------------------------------
    dec_add = seasonal_decompose(s_train, model="additive", period=SEASONAL_PERIOD)
    fig, axes = plt.subplots(4, 1, figsize=(10, 8.5), sharex=True)
    for ax_i, (serie_i, etiqueta) in zip(axes, [
            (dec_add.observed, "Observada"), (dec_add.trend, "Tendencia"),
            (dec_add.seasonal, "Estacional"), (dec_add.resid, "Residuo")]):
        ax_i.plot(serie_i.index, serie_i.values, color=color, lw=1)
        ax_i.set_ylabel(etiqueta)
    axes[0].set_title(f"{titulo} - descomposicion aditiva (entrenamiento, periodo = 12)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_02_descomposicion.png"))
    plt.close(fig)

    trend_strength, seasonal_strength = strengths(s_train)
    std_anual = s_train.groupby(s_train.index.year).std()
    ratio_dispersion = std_anual.max() / max(std_anual.min(), 1e-9)
    log(f"c) Fuerza de tendencia (STL): {trend_strength:.3f}   "
        f"Fuerza estacional (STL, todo el entrenamiento): {seasonal_strength:.3f}")
    log(f"   Desviacion estandar anual: minimo {std_anual.min():,.0f}, "
        f"maximo {std_anual.max():,.0f} (razon {ratio_dispersion:.1f}x) "
        f"-> la dispersion cambia con el nivel de la serie.")

    # ---- d. Transformacion ---------------------------------------------
    log1p = uses_log1p(s_train)
    cv_niveles = s_train.std() / s_train.mean()
    s_log = transform(s_train, True, log1p)
    cv_log = s_log.std() / s_log.mean()
    usar_log = ratio_dispersion > 2.0
    log(f"d) Coeficiente de variacion en niveles: {cv_niveles:.3f}; en escala logaritmica: {cv_log:.3f}. "
        f"Transformacion elegida: {'logaritmica' if usar_log else 'ninguna'}"
        f"{' (log1p por la presencia de meses en cero)' if usar_log and log1p else ''}.")

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    axes[0].plot(s_train.index, s_train.values, color=color, lw=1)
    axes[0].set_title("Niveles (sin transformar)")
    axes[1].plot(s_log.index, s_log.values, color=color, lw=1)
    axes[1].set_title("Escala logaritmica")
    fig.suptitle(f"{titulo} - niveles frente a logaritmo (entrenamiento)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_03_transformacion.png"))
    plt.close(fig)

    # ---- e. ACF, PACF y pruebas de raiz unitaria ------------------------
    base = s_log if usar_log else s_train

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    plot_acf(base, ax=axes[0][0], lags=36, color=color)
    axes[0][0].set_title("ACF - serie sin diferenciar")
    plot_pacf(base, ax=axes[0][1], lags=36, color=color, method="ywm")
    axes[0][1].set_title("PACF - serie sin diferenciar")
    plot_acf(base.diff().dropna(), ax=axes[1][0], lags=36, color=color)
    axes[1][0].set_title("ACF - primera diferencia")
    plot_pacf(base.diff().dropna(), ax=axes[1][1], lags=36, color=color, method="ywm")
    axes[1][1].set_title("PACF - primera diferencia")
    fig.suptitle(f"{titulo} - funciones de autocorrelacion (entrenamiento)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"{nombre}_04_acf_pacf.png"))
    plt.close(fig)

    pruebas = [
        adf_test(base, "Serie sin diferenciar"),
        adf_test(base.diff(), "Primera diferencia (d=1)"),
        adf_test(base.diff().diff(SEASONAL_PERIOD), "Primera diferencia + diferencia estacional (d=1, D=1)"),
    ]
    log("e) Prueba de Dickey-Fuller aumentada sobre el tramo de entrenamiento:")
    for p in pruebas:
        log(f"   {p['prueba']:<52s} estadistico={p['estadistico']:>8.3f}  "
            f"p={p['p_valor']:.4f}  -> {p['conclusion']}")

    kp = kpss_test(base)
    log(f"   KPSS sobre la serie sin diferenciar: estadistico={kp['estadistico']:.3f}  "
        f"p={kp['p_valor']:.4f} -> {kp['conclusion']}")

    d, D, seasonal_pre = choose_orders(base)
    log(f"   Fuerza estacional medida antes de la pandemia: {seasonal_pre:.3f} "
        f"(la ventana completa la subestima por el desplome de 2020).")
    log(f"   Diferenciaciones sugeridas: D={D} (estacional, periodo 12) y d={d} (regular), "
        f"determinadas en ese orden.")
    log("")

    return {
        "serie": nombre,
        "titulo": titulo,
        "categoria": categoria,
        "inicio": f"{s_full.index.min():%Y-%m}",
        "fin": f"{s_full.index.max():%Y-%m}",
        "frecuencia": "Mensual (MS)",
        "n_obs": len(s_full),
        "n_train": len(s_train),
        "n_test": len(s_test),
        "media_train": float(s_train.mean()),
        "cv_niveles": float(cv_niveles),
        "ratio_dispersion": float(ratio_dispersion),
        "fuerza_tendencia": round(trend_strength, 3),
        "fuerza_estacional": round(seasonal_strength, 3),
        "fuerza_estacional_prepandemia": round(seasonal_pre, 3),
        "crecimiento_prepandemia_pct": float(crecimiento),
        "usar_log": bool(usar_log),
        "log1p": bool(log1p),
        "d": int(d),
        "D": int(D),
        "adf": pruebas,
        "kpss": kp,
    }


resultados = [analizar_serie(nombre, titulo, categoria, color)
              for nombre, (titulo, categoria, color) in SERIES_CATALOG.items()]

resumen = pd.DataFrame([{k: v for k, v in r.items() if k not in ("adf", "kpss")}
                        for r in resultados])
resumen.to_csv(os.path.join(TAB, "diagnostico_series.csv"), index=False, encoding="utf-8")

adf_rows = [dict(serie=r["serie"], **p) for r in resultados for p in r["adf"]]
pd.DataFrame(adf_rows).to_csv(os.path.join(TAB, "pruebas_adf.csv"), index=False, encoding="utf-8")

with open(os.path.join(TAB, "diagnostico_series.json"), "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

log("=" * 78)
log("RESUMEN DEL DIAGNOSTICO")
log("=" * 78)
log(resumen[["serie", "fuerza_tendencia", "fuerza_estacional",
             "fuerza_estacional_prepandemia", "cv_niveles", "usar_log", "d", "D"]]
    .to_string(index=False))

log.save(os.path.join(OUT, "reporte_analisis_series.txt"))
print("\nFiguras en:", FIG)
print("Tablas en:", TAB)
