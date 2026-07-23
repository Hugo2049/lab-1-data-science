# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Analisis preliminar (punto 4, incisos a-e) de al menos dos series:
  - Total mensual de viajeros (serie obligatoria)
  - Via Aerea (una de las categorias seleccionadas: Vias de ingreso)

Se trabaja sobre el tramo de ENTRENAMIENTO (2009-01 a 2021-03) para el
diagnostico de estacionariedad, tal como corresponde antes de modelar;
el grafico general se muestra sobre la serie completa para dar contexto.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import os

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SER = os.path.join(BASE, "outputs", "series")
OUT = os.path.join(BASE, "outputs", "preliminar")
os.makedirs(OUT, exist_ok=True)

SPLIT_DATE = pd.Timestamp('2021-04-01')

def cargar(nombre):
    s = pd.read_csv(os.path.join(SER, f"{nombre}_completa.csv"), index_col=0, parse_dates=True)['viajeros']
    s = s.asfreq('MS')
    return s

report = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    report.append(s)

def analizar_serie(nombre, titulo, color):
    log("="*72)
    log(f"SERIE: {titulo}")
    log("="*72)
    s_full = cargar(nombre)
    s_train = s_full[s_full.index < SPLIT_DATE]

    # --- a. Inicio, fin, frecuencia ---
    log(f"a) Inicio: {s_full.index.min().strftime('%Y-%m')}  "
        f"Fin: {s_full.index.max().strftime('%Y-%m')}  "
        f"Frecuencia: Mensual (MS)  N obs totales: {len(s_full)}  "
        f"(train: {len(s_train)}, 2009-01 a 2021-03)")

    # --- b. Grafico de la serie completa (contexto) ---
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(s_full.index, s_full.values, color=color, lw=1.1, label='Serie completa')
    ax.axvspan(s_full.index.min(), SPLIT_DATE, color=color, alpha=0.06, label='Entrenamiento (70%)')
    ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2021-12-31'), color='red', alpha=0.07, label='Pandemia COVID-19')
    ax.axvline(SPLIT_DATE, color='black', ls='--', lw=1)
    ax.set_title(f"{titulo} — serie mensual completa (2009-2026)")
    ax.set_ylabel("Viajeros")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:,.0f}"))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"{nombre}_01_serie.png"))
    plt.close(fig)

    log(f"b) Ver figura {nombre}_01_serie.png. A primera vista: tendencia y estacionalidad "
        f"visibles antes de 2020, quiebre abrupto por la pandemia (2020-2021), y recuperacion posterior.")

    # --- c. Descomposicion (sobre train, periodo 12) ---
    dec_add = seasonal_decompose(s_train, model='additive', period=12)
    dec_mul = seasonal_decompose(s_train, model='multiplicative', period=12)

    fig, axes = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
    dec_add.observed.plot(ax=axes[0], color=color); axes[0].set_ylabel("Observada")
    dec_add.trend.plot(ax=axes[1], color=color); axes[1].set_ylabel("Tendencia")
    dec_add.seasonal.plot(ax=axes[2], color=color); axes[2].set_ylabel("Estacional")
    dec_add.resid.plot(ax=axes[3], color=color, marker='o', ms=2, lw=0.5); axes[3].set_ylabel("Residuo")
    axes[0].set_title(f"{titulo} — descomposicion aditiva (train, periodo=12)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"{nombre}_02_descomposicion_aditiva.png"))
    plt.close(fig)

    # variabilidad de la estacionalidad multiplicativa vs aditiva -> pista de heterocedasticidad
    resid_add_std = dec_add.resid.dropna().std()
    resid_mul_std = dec_mul.resid.dropna().std()
    log(f"c) Descomposicion aditiva: desv.est. del residuo = {resid_add_std:,.1f}")
    log(f"   Descomposicion multiplicativa: desv.est. del residuo = {resid_mul_std:.4f} (escala relativa)")
    # varianza movil por año (proxy simple de heterocedasticidad)
    var_anual = s_train.groupby(s_train.index.year).std()
    log(f"   Desv. estandar por anio (train):\n" + var_anual.to_string())
    log("   Interpretacion: la tendencia muestra crecimiento sostenido 2009-2019 y una caida abrupta "
        "en 2020 -> la serie NO es estacionaria en media (la media cambia claramente con el tiempo). "
        "La desviacion estandar anual tambien crece con el nivel de la serie (mas dispersion en anios "
        "con mas viajeros) -> hay indicios de NO estacionariedad en varianza tambien.")

    # --- d. Transformacion ---
    log_s_train = np.log(s_train.replace(0, np.nan)).dropna()
    log(f"d) Se evalua transformacion logaritmica. CV (coef. variacion) de la serie en niveles: "
        f"{s_train.std()/s_train.mean():.3f}. "
        "Dado que la dispersion escala con el nivel (ver desv.est. por anio), se recomienda aplicar "
        "logaritmo (o Box-Cox) para estabilizar la varianza antes de diferenciar en media.")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(s_train.index, s_train.values, color=color, lw=1)
    axes[0].set_title("Niveles (sin transformar)")
    axes[1].plot(log_s_train.index, log_s_train.values, color=color, lw=1)
    axes[1].set_title("Log(viajeros)")
    fig.suptitle(f"{titulo} — niveles vs. log (train)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"{nombre}_03_transformacion.png"))
    plt.close(fig)

    # --- e. ACF + ADF ---
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    plot_acf(s_train, ax=axes[0], lags=36, color=color)
    axes[0].set_title("ACF - niveles (train)")
    plot_acf(s_train.diff().dropna(), ax=axes[1], lags=36, color=color)
    axes[1].set_title("ACF - primera diferencia (train)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"{nombre}_04_acf.png"))
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    plot_pacf(s_train, ax=axes[0], lags=36, color=color, method='ywm')
    axes[0].set_title("PACF - niveles (train)")
    plot_pacf(s_train.diff().dropna(), ax=axes[1], lags=36, color=color, method='ywm')
    axes[1].set_title("PACF - primera diferencia (train)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"{nombre}_05_pacf.png"))
    plt.close(fig)

    adf_niveles = adfuller(s_train, autolag='AIC')
    adf_log = adfuller(log_s_train, autolag='AIC')
    adf_diff1 = adfuller(s_train.diff().dropna(), autolag='AIC')
    adf_logdiff1 = adfuller(log_s_train.diff().dropna(), autolag='AIC')
    adf_diff1_12 = adfuller(s_train.diff().dropna().diff(12).dropna(), autolag='AIC')
    adf_logdiff1_12 = adfuller(log_s_train.diff().dropna().diff(12).dropna(), autolag='AIC')

    def fmt_adf(res, label):
        stat, p, lags, nobs, crit, _ = res
        sig = "NO estacionaria" if p > 0.05 else "estacionaria"
        return (f"   ADF [{label}]: estadistico={stat:.3f}  p-valor={p:.4f}  "
                f"lags usados={lags}  n={nobs}  -> {sig} (alfa=0.05)  "
                f"valores criticos: 1%={crit['1%']:.3f} 5%={crit['5%']:.3f} 10%={crit['10%']:.3f}")

    log("e) Prueba de Dickey-Fuller Aumentada (ADF) sobre train:")
    log(fmt_adf(adf_niveles, "niveles"))
    log(fmt_adf(adf_log, "log(niveles)"))
    log(fmt_adf(adf_diff1, "1a diferencia de niveles"))
    log(fmt_adf(adf_logdiff1, "1a diferencia de log"))
    log(fmt_adf(adf_diff1_12, "1a diferencia + diferencia estacional(12) de niveles"))
    log(fmt_adf(adf_logdiff1_12, "1a diferencia + diferencia estacional(12) de log"))
    log("   El ACF de niveles decae muy lentamente (lags altos con autocorrelacion significativa) y "
        "el ADF en niveles no rechaza H0 (raiz unitaria) -> confirma NO estacionariedad en media. "
        "Tras una diferenciacion regular (d=1) el ADF SI rechaza H0 -> con d=1 (y d=1 sobre el log si "
        "se quiere estabilizar tambien varianza) se alcanza estacionariedad en media.")
    log("")

    return {
        'serie': nombre, 'inicio': s_full.index.min(), 'fin': s_full.index.max(),
        'p_niveles': adf_niveles[1], 'p_log': adf_log[1],
        'p_diff1': adf_diff1[1], 'p_logdiff1': adf_logdiff1[1],
    }

res1 = analizar_serie('Total', 'Total mensual de viajeros internacionales', '#1f77b4')
res2 = analizar_serie('Via_Aérea', 'Via de ingreso: Aerea', '#d62728')

with open(os.path.join(OUT, "reporte_preliminar.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("\nListo. Resultados en:", OUT)
