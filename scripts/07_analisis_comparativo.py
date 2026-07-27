# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Punto 5: analisis comparativo entre series con evidencia estadistica.
Para cada categoria se determina que serie presenta mayor estacionalidad,
mayor tendencia de crecimiento, mayor volatilidad y cual fue la mas afectada
por la pandemia. Se cierra con los hallazgos utiles para el INGUAT.

A diferencia del resto de los scripts, aqui se usan las series completas
(2009-2026): la comparacion describe el comportamiento historico observado,
no el desempeno de un modelo, por lo que no corresponde limitarse al tramo
de entrenamiento.
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
from statsmodels.tsa.seasonal import STL

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_utils import (OUT, SEASONAL_PERIOD, SERIES_CATALOG, Reporter, ensure_dir,
                       load_series)

warnings.filterwarnings("ignore")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3

FIG = ensure_dir(os.path.join(OUT, "comparativo"))
TAB = os.path.join(OUT, "tablas")

log = Reporter()

PRE_COVID_FIN = "2020-02-01"


def indicadores(nombre, titulo, categoria):
    s = load_series(nombre)
    pre = s[s.index <= PRE_COVID_FIN]

    # --- Estacionalidad: fuerza estacional STL sobre la etapa prepandemia ---
    stl = STL(pre, period=SEASONAL_PERIOD, robust=True).fit()
    var_resid = np.var(stl.resid)
    fuerza_estacional = max(0.0, 1 - var_resid / np.var(stl.seasonal + stl.resid))
    fuerza_tendencia = max(0.0, 1 - var_resid / np.var(stl.trend + stl.resid))

    # Amplitud estacional relativa: cuanto se separan el mejor y el peor mes
    perfil = stl.seasonal.groupby(stl.seasonal.index.month).mean()
    amplitud_relativa = (perfil.max() - perfil.min()) / pre.mean() * 100
    mes_alto, mes_bajo = int(perfil.idxmax()), int(perfil.idxmin())

    # --- Tendencia: crecimiento anual compuesto entre 2009-2011 y 2017-2019 ---
    base_inicial = s["2009":"2011"].sum() / 3
    base_final = s["2017":"2019"].sum() / 3
    cagr = ((base_final / base_inicial) ** (1 / 8) - 1) * 100 if base_inicial > 0 else np.nan

    # --- Volatilidad: dispersion de los cambios mensuales relativos ----------
    retornos = np.log(pre.replace(0, np.nan)).diff().dropna()
    volatilidad = float(retornos.std() * 100)

    # --- Impacto de la pandemia ---------------------------------------------
    total_2019 = s["2019"].sum()
    total_2020 = s["2020"].sum()
    caida_2020 = (total_2020 / total_2019 - 1) * 100 if total_2019 > 0 else np.nan
    piso = s["2020-03-01":"2021-06-30"].min()
    piso_relativo = piso / (total_2019 / 12) * 100 if total_2019 > 0 else np.nan
    total_2025 = s["2025"].sum()
    recuperacion = total_2025 / total_2019 * 100 if total_2019 > 0 else np.nan

    return {
        "serie": nombre, "titulo": titulo, "categoria": categoria,
        "fuerza_estacional": round(float(fuerza_estacional), 3),
        "amplitud_estacional_pct": round(float(amplitud_relativa), 1),
        "mes_pico": mes_alto, "mes_valle": mes_bajo,
        "fuerza_tendencia": round(float(fuerza_tendencia), 3),
        "cagr_prepandemia_pct": round(float(cagr), 2),
        "volatilidad_pct": round(volatilidad, 2),
        "caida_2020_pct": round(float(caida_2020), 1),
        "piso_relativo_pct": round(float(piso_relativo), 1),
        "recuperacion_2025_pct": round(float(recuperacion), 1),
    }


datos = pd.DataFrame([indicadores(n, t, c) for n, (t, c, _) in SERIES_CATALOG.items()])
datos.to_csv(os.path.join(TAB, "analisis_comparativo.csv"), index=False, encoding="utf-8")

MESES = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
         7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre",
         12: "diciembre"}

log("=" * 78)
log("PUNTO 5 - ANALISIS COMPARATIVO")
log("=" * 78)
log("")
log("Indicadores calculados sobre las series completas (2009-2026). La")
log("estacionalidad y la volatilidad se miden en la etapa previa a marzo de 2020")
log("para que el desplome de la pandemia no contamine la comparacion.")
log("")
log(datos[["serie", "fuerza_estacional", "amplitud_estacional_pct", "cagr_prepandemia_pct",
           "volatilidad_pct", "caida_2020_pct", "recuperacion_2025_pct"]].to_string(index=False))
log("")

for categoria in ["Vias", "Paises"]:
    sub = datos[datos.categoria == categoria]
    etiqueta = "Vias de ingreso" if categoria == "Vias" else "Paises de residencia"
    log("=" * 78)
    log(f"CATEGORIA: {etiqueta}")
    log("=" * 78)

    mas_estacional = sub.loc[sub.fuerza_estacional.idxmax()]
    log(f"i)   Mayor estacionalidad: {mas_estacional['titulo']} "
        f"(fuerza estacional {mas_estacional['fuerza_estacional']:.3f}, amplitud equivalente al "
        f"{mas_estacional['amplitud_estacional_pct']:.1f}% del nivel medio; pico en "
        f"{MESES[mas_estacional['mes_pico']]}, valle en {MESES[mas_estacional['mes_valle']]}).")

    mayor_tendencia = sub.loc[sub.cagr_prepandemia_pct.idxmax()]
    log(f"ii)  Mayor tendencia de crecimiento: {mayor_tendencia['titulo']} "
        f"(crecimiento anual compuesto de {mayor_tendencia['cagr_prepandemia_pct']:+.2f}% "
        f"entre 2009-2011 y 2017-2019).")

    mas_volatil = sub.loc[sub.volatilidad_pct.idxmax()]
    log(f"iii) Mayor volatilidad: {mas_volatil['titulo']} "
        f"(desviacion estandar de los cambios mensuales de {mas_volatil['volatilidad_pct']:.1f}%).")

    mas_golpeada = sub.loc[sub.caida_2020_pct.idxmin()]
    log(f"iv)  Mas afectada por la pandemia: {mas_golpeada['titulo']} "
        f"(caida de {mas_golpeada['caida_2020_pct']:.1f}% en 2020 frente a 2019; "
        f"en 2025 recupero el {mas_golpeada['recuperacion_2025_pct']:.1f}% del nivel de 2019).")
    log("")

# --- Graficos comparativos --------------------------------------------------
for categoria, etiqueta in [("Vias", "Vias de ingreso"), ("Paises", "Paises de residencia")]:
    sub = datos[datos.categoria == categoria]
    nombres_cortos = [t.split(": ")[-1] for t in sub.titulo]

    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
    for ax, columna, titulo_eje in zip(
            axes,
            ["fuerza_estacional", "cagr_prepandemia_pct", "volatilidad_pct", "caida_2020_pct"],
            ["Fuerza estacional (STL)", "Crecimiento anual compuesto (%)",
             "Volatilidad mensual (%)", "Caida en 2020 frente a 2019 (%)"]):
        ax.bar(nombres_cortos, sub[columna], color="#1d6b63")
        ax.set_title(titulo_eje, fontsize=9)
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.axhline(0, color="black", lw=0.8)
    fig.suptitle(f"Comparacion entre series - {etiqueta}")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"comparativo_{categoria.lower()}.png"))
    plt.close(fig)

# --- Series normalizadas: trayectoria relativa a 2019 -----------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))
for ax, categoria, etiqueta in [(axes[0], "Vias", "Vias de ingreso"),
                                (axes[1], "Paises", "Paises de residencia")]:
    for nombre, (titulo, cat, color) in SERIES_CATALOG.items():
        if cat != categoria:
            continue
        s = load_series(nombre)
        anual = s.groupby(s.index.year).sum()
        anual = anual[anual.index <= 2025]
        base = anual.loc[2019]
        ax.plot(anual.index, anual / base * 100, marker="o", ms=3,
                color=color, label=titulo.split(": ")[-1])
    ax.axhline(100, color="black", lw=0.9, ls="--")
    ax.set_title(f"{etiqueta} - total anual como % del nivel de 2019")
    ax.set_ylabel("% de 2019")
    ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "trayectoria_relativa_2019.png"))
plt.close(fig)

log("=" * 78)
log("HALLAZGOS PARA LA TOMA DE DECISIONES DEL INGUAT")
log("=" * 78)
total = datos[datos.serie == "Total"].iloc[0]
vias = datos[datos.categoria == "Vias"]
paises = datos[datos.categoria == "Paises"]
aerea = datos[datos.serie == "Via_Aérea"].iloc[0]
terrestre = datos[datos.serie == "Via_Terrestre"].iloc[0]

log(f"1. La demanda es marcadamente estacional: la serie total concentra su pico en "
    f"{MESES[total['mes_pico']]} y su valle en {MESES[total['mes_valle']]}, con una amplitud "
    f"equivalente al {total['amplitud_estacional_pct']:.1f}% del nivel medio. La planificacion "
    f"de campanas y de capacidad hotelera deberia anclarse a ese calendario.")
log(f"2. La via aerea y la terrestre son negocios distintos: la aerea crece al "
    f"{aerea['cagr_prepandemia_pct']:+.2f}% anual y la terrestre al "
    f"{terrestre['cagr_prepandemia_pct']:+.2f}%, con estacionalidades de distinta intensidad "
    f"({aerea['fuerza_estacional']:.2f} frente a {terrestre['fuerza_estacional']:.2f}). "
    f"Conviene fijar metas y presupuestos separados por via.")
log(f"3. La recuperacion pospandemia es desigual: en 2025 las vias alcanzaron entre "
    f"{vias.recuperacion_2025_pct.min():.0f}% y {vias.recuperacion_2025_pct.max():.0f}% del nivel "
    f"de 2019, y los mercados de origen entre {paises.recuperacion_2025_pct.min():.0f}% y "
    f"{paises.recuperacion_2025_pct.max():.0f}%. El esfuerzo comercial deberia concentrarse en "
    f"los segmentos que siguen por debajo de su nivel previo.")
log(f"4. Los modelos entrenados hasta marzo de 2021 no logran anticipar la recuperacion: "
    f"todos los algoritmos subestiman fuertemente el conjunto de prueba. Para pronosticar el "
    f"turismo pospandemia no basta con la historia previa, hay que reentrenar con datos "
    f"posteriores a la reapertura o incorporar variables externas.")
log(f"5. El quiebre metodologico de 2023 cambia el nivel de la serie sin que exista una caida "
    f"real de demanda. Cualquier meta institucional planteada sobre el total de viajeros debe "
    f"usar Turista mas Excursionista, que si es comparable en todo el periodo.")

log.save(os.path.join(OUT, "reporte_comparativo.txt"))
print("\nFiguras en:", FIG)
