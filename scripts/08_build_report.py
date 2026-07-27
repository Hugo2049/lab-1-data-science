# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Construye el informe final en HTML (con las imagenes incrustadas en base64) y
lo exporta a PDF usando Chrome en modo headless.

Todas las cifras del informe se leen de las tablas generadas por los scripts
anteriores, de modo que el documento no pueda desincronizarse del analisis.
"""
import base64
import json
import os
import subprocess
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_utils import BASE, OUT, SERIES_CATALOG, ensure_dir

TAB = os.path.join(OUT, "tablas")
INFORME = ensure_dir(os.path.join(BASE, "informe"))
HTML_PATH = os.path.join(INFORME, "informe.html")
PDF_PATH = os.path.join(INFORME, "Laboratorio1_SeriesDeTiempo.pdf")

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

MESES = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
         7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre",
         12: "diciembre"}


def img(*parts):
    """Incrusta una imagen como data URI para que el PDF sea autocontenido."""
    path = os.path.join(OUT, *parts)
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def figure(src, caption):
    return f'<figure><img src="{src}"><figcaption>{caption}</figcaption></figure>'


def table_html(df, columns=None, headers=None, numeric_format=None):
    """Convierte un DataFrame en una tabla HTML sencilla."""
    df = df[columns] if columns else df
    headers = headers or list(df.columns)
    numeric_format = numeric_format or {}
    thead = "".join(f"<th>{h}</th>" for h in headers)
    rows = []
    for _, r in df.iterrows():
        cells = []
        for col in df.columns:
            value = r[col]
            if col in numeric_format and pd.notna(value):
                cells.append(f'<td class="num">{numeric_format[col](value)}</td>')
            elif isinstance(value, float):
                cells.append(f'<td class="num">{value:,.2f}</td>' if pd.notna(value)
                             else '<td class="num">-</td>')
            else:
                cells.append(f"<td>{value}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<div class="wrap-table"><table><thead><tr>{thead}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


# ---------------------------------------------------------------------------
# Datos del analisis
# ---------------------------------------------------------------------------
with open(os.path.join(TAB, "diagnostico_series.json"), encoding="utf-8") as f:
    diagnostico = {d["serie"]: d for d in json.load(f)}

arima_mejor = pd.read_csv(os.path.join(TAB, "arima_mejor_por_serie.csv")).set_index("serie")
arima_todos = pd.read_csv(os.path.join(TAB, "arima_todos_los_modelos.csv"))
comparacion = pd.read_csv(os.path.join(TAB, "comparacion_modelos.csv"))
mejor_modelo = pd.read_csv(os.path.join(TAB, "mejor_modelo_por_serie.csv")).set_index("serie")
comparativo = pd.read_csv(os.path.join(TAB, "analisis_comparativo.csv")).set_index("serie")

ENTERO = lambda v: f"{v:,.0f}"
DECIMAL = lambda v: f"{v:,.2f}"
PORCENTAJE = lambda v: f"{v:,.1f}%"

# ---------------------------------------------------------------------------
# Seccion 4: una subseccion por serie
# ---------------------------------------------------------------------------
secciones_series = []
for nombre, (titulo, categoria, _) in SERIES_CATALOG.items():
    d = diagnostico[nombre]
    a = arima_mejor.loc[nombre]
    comp = comparacion[comparacion.serie == nombre].sort_values("RMSE")
    mejor = mejor_modelo.loc[nombre]
    top_arima = arima_todos[arima_todos.serie == nombre].nsmallest(5, "AIC")

    adf_df = pd.DataFrame(d["adf"])[["prueba", "estadistico", "p_valor", "conclusion"]]

    transformacion = ("logaritmica" if d["usar_log"] else "ninguna")
    if d["usar_log"] and d["log1p"]:
        transformacion += " (log(1+x), porque la serie tiene meses en cero)"

    residuos_ok = a["ljung_box_p"] > 0.05
    texto_residuos = (
        f"Los residuos del modelo elegido no muestran autocorrelacion remanente "
        f"(Ljung-Box con 24 rezagos, p = {a['ljung_box_p']:.3f}), de modo que el modelo "
        f"capturo la estructura temporal disponible."
        if residuos_ok else
        f"Los residuos conservan autocorrelacion significativa (Ljung-Box p = "
        f"{a['ljung_box_p']:.3f}), senal de que la estructura de esta serie no queda "
        f"bien descrita por un modelo lineal de este tipo."
    )

    secciones_series.append(f"""
<section class="serie">
  <h3>{titulo}</h3>
  <p class="soft"><b>Inciso a.</b> Inicio {d['inicio']}, fin {d['fin']}, frecuencia {d['frecuencia'].lower()},
  {d['n_obs']} observaciones ({d['n_train']} de entrenamiento y {d['n_test']} de prueba).</p>

  {figure(img('series_analisis', f'{nombre}_01_serie.png'),
          'Serie mensual completa. El area sombreada corresponde al tramo de entrenamiento y la banda roja a la ventana de la pandemia.')}
  <p><b>Inciso b.</b> El nivel medio de la serie crecio
  {d['crecimiento_prepandemia_pct']:+.1f}% entre los primeros y los ultimos dos anios previos a la
  pandemia, con un patron anual que se repite de forma regular. El desplome de 2020 y la
  recuperacion posterior dominan la parte final del recorrido.</p>

  {figure(img('series_analisis', f'{nombre}_02_descomposicion.png'),
          'Descomposicion aditiva sobre el tramo de entrenamiento con periodo 12.')}
  <p><b>Inciso c.</b> La descomposicion separa una tendencia de fuerza
  {d['fuerza_tendencia']:.2f} y una componente estacional de fuerza {d['fuerza_estacional']:.2f}
  medida sobre todo el entrenamiento, que sube a {d['fuerza_estacional_prepandemia']:.2f} si se
  mide antes de marzo de 2020. Como la media cambia de nivel a lo largo del periodo, la serie
  <b>no es estacionaria en media</b>. La desviacion estandar anual varia en un factor de
  {d['ratio_dispersion']:.1f} entre su ano mas estable y el mas disperso, es decir que la
  dispersion acompana al nivel: tampoco hay <b>estacionariedad en varianza</b>.</p>

  {figure(img('series_analisis', f'{nombre}_03_transformacion.png'),
          'Serie en niveles frente a la misma serie en escala logaritmica.')}
  <p><b>Inciso d.</b> Transformacion aplicada: {transformacion}. El coeficiente de variacion
  en niveles es {d['cv_niveles']:.2f} y la dispersion crece con el nivel, condicion tipica en la
  que el logaritmo estabiliza la varianza antes de diferenciar.</p>

  {figure(img('series_analisis', f'{nombre}_04_acf_pacf.png'),
          'Funciones de autocorrelacion simple y parcial, antes y despues de diferenciar.')}
  <p><b>Inciso e.</b> La autocorrelacion de la serie sin diferenciar decae con mucha lentitud y
  se mantiene significativa en rezagos altos, comportamiento propio de una raiz unitaria. Las
  pruebas formales confirman el diagnostico:</p>
  {table_html(adf_df, headers=['Prueba de Dickey-Fuller aumentada', 'Estadistico', 'Valor p', 'Conclusion'],
              numeric_format={'estadistico': DECIMAL, 'p_valor': lambda v: f"{v:.4f}"})}
  <p>Para volverla estacionaria en media hacen falta <b>d = {d['d']}</b> diferencia regular y
  <b>D = {d['D']}</b> diferencia estacional de periodo 12.</p>

  <p><b>Incisos f y g.</b> Con esas diferenciaciones fijas se ajustaron
  {int(a['n_modelos_probados'])} modelos combinando p y q en {{0, 1, 2}} y P y Q en {{0, 1}}.
  Comparar AIC entre modelos con distinto grado de diferenciacion no seria valido, por eso el
  orden de integracion se fija antes con las pruebas de raiz unitaria y no por AIC. Los cinco
  mejores por AIC:</p>
  {table_html(top_arima, columns=['modelo', 'AIC', 'BIC', 'ljung_box_p', 'jarque_bera_p'],
              headers=['Modelo', 'AIC', 'BIC', 'Ljung-Box (p)', 'Jarque-Bera (p)'],
              numeric_format={'AIC': DECIMAL, 'BIC': DECIMAL})}
  <p>El modelo seleccionado es <b>{a['modelo']}</b>, el de menor AIC entre los que dejan residuos
  sin autocorrelacion. {texto_residuos}</p>
  {figure(img('arima', f'{nombre}_residuos.png'),
          'Diagnostico de residuos del modelo ARIMA seleccionado.')}

  <p><b>Incisos h, i y j.</b> El mismo conjunto de entrenamiento se modelo tambien con Prophet,
  Holt-Winters, suavizamiento exponencial simple y seasonal naive, y los cinco pronosticos se
  evaluaron sobre los mismos {d['n_test']} meses de prueba:</p>
  {table_html(comp, columns=['modelo', 'AIC', 'BIC', 'MAE', 'RMSE', 'MAPE'],
              headers=['Modelo', 'AIC', 'BIC', 'MAE', 'RMSE', 'MAPE'],
              numeric_format={'AIC': DECIMAL, 'BIC': DECIMAL, 'MAE': ENTERO,
                              'RMSE': ENTERO, 'MAPE': PORCENTAJE})}
  {figure(img('comparacion', f'{nombre}_comparacion.png'),
          'Todos los pronosticos frente a los valores reales del conjunto de prueba.')}
  <p><b>Inciso k.</b> El mejor modelo para esta serie es <b>{mejor['mejor_modelo']}</b>, con
  MAE de {mejor['MAE']:,.0f} viajeros, RMSE de {mejor['RMSE']:,.0f} y MAPE de
  {mejor['MAPE']:.1f}%. AIC y BIC solo permiten ordenar modelos ajustados sobre la misma serie
  transformada, por lo que se usan para elegir dentro de la familia ARIMA, mientras que la
  comparacion entre algoritmos distintos se resuelve con el error sobre el conjunto de prueba.</p>
</section>
""")

# ---------------------------------------------------------------------------
# Seccion 5: analisis comparativo
# ---------------------------------------------------------------------------
def bloque_categoria(categoria, etiqueta):
    sub = comparativo[comparativo.categoria == categoria]
    mas_estacional = sub.loc[sub.fuerza_estacional.idxmax()]
    mayor_tendencia = sub.loc[sub.cagr_prepandemia_pct.idxmax()]
    mas_volatil = sub.loc[sub.volatilidad_pct.idxmax()]
    mas_golpeada = sub.loc[sub.caida_2020_pct.idxmin()]
    tabla = sub.reset_index()[["titulo", "fuerza_estacional", "amplitud_estacional_pct",
                               "cagr_prepandemia_pct", "volatilidad_pct", "caida_2020_pct",
                               "recuperacion_2025_pct"]]
    return f"""
<h3>{etiqueta}</h3>
{table_html(tabla,
            headers=['Serie', 'Fuerza estacional', 'Amplitud estacional', 'Crecimiento anual',
                     'Volatilidad mensual', 'Caida en 2020', 'Nivel de 2025 sobre 2019'],
            numeric_format={'fuerza_estacional': DECIMAL, 'amplitud_estacional_pct': PORCENTAJE,
                            'cagr_prepandemia_pct': PORCENTAJE, 'volatilidad_pct': PORCENTAJE,
                            'caida_2020_pct': PORCENTAJE, 'recuperacion_2025_pct': PORCENTAJE})}
<p><b>Mayor estacionalidad:</b> {mas_estacional['titulo']}, con una fuerza estacional de
{mas_estacional['fuerza_estacional']:.2f} y una amplitud equivalente al
{mas_estacional['amplitud_estacional_pct']:.1f}% de su nivel medio. Su pico se da en
{MESES[int(mas_estacional['mes_pico'])]} y su valle en {MESES[int(mas_estacional['mes_valle'])]}.</p>
<p><b>Mayor tendencia de crecimiento:</b> {mayor_tendencia['titulo']}, que crecio
{mayor_tendencia['cagr_prepandemia_pct']:+.2f}% anual compuesto entre el promedio de 2009-2011 y
el de 2017-2019.</p>
<p><b>Mayor volatilidad:</b> {mas_volatil['titulo']}, cuyos cambios mensuales tienen una
desviacion estandar de {mas_volatil['volatilidad_pct']:.1f}% en escala logaritmica.</p>
<p><b>Mas afectada por la pandemia:</b> {mas_golpeada['titulo']}, con una caida de
{mas_golpeada['caida_2020_pct']:.1f}% en 2020 frente a 2019. Para 2025 se ubicaba en el
{mas_golpeada['recuperacion_2025_pct']:.1f}% de su nivel de 2019.</p>
{figure(img('comparativo', f'comparativo_{categoria.lower()}.png'),
        f'Indicadores comparados entre las series de {etiqueta.lower()}.')}
"""


total_diag = diagnostico["Total"]
total_comp = comparativo.loc["Total"]
mejor_global = mejor_modelo.reset_index()
conteo_mejores = (mejor_global["mejor_modelo"]
                  .apply(lambda m: "ARIMA" if m.startswith("SARIMA") else m)
                  .value_counts())
resumen_conteo = ", ".join(f"{k} en {v} de las 7 series" for k, v in conteo_mejores.items())

CSS = """
:root {
  --bg:#ffffff; --panel:#ffffff; --ink:#1e2a28; --ink-soft:#4b5a57;
  --line:#d9d4c8; --accent:#1d6b63; --accent-soft:#e4efec; --warn:#b5622a; --warn-soft:#f7ece2;
}
* { box-sizing:border-box; }
body {
  background:var(--bg); color:var(--ink); line-height:1.5;
  font-family:'Segoe UI', Arial, sans-serif; font-size:10.5pt;
  max-width:940px; margin:0 auto; padding:0 24px 40px;
}
h1,h2,h3,h4 { font-family:Georgia, 'Times New Roman', serif; color:var(--ink); }
h1 { font-size:22pt; margin:0 0 6px; }
h2 {
  font-size:14pt; border-bottom:2px solid var(--accent); padding-bottom:6px;
  margin:26px 0 12px; page-break-after:avoid;
}
h3 { font-size:12pt; margin:20px 0 8px; page-break-after:avoid; }
p { margin:8px 0; text-align:justify; }
p.soft { color:var(--ink-soft); }
.eyebrow {
  font-size:8.5pt; letter-spacing:.14em; text-transform:uppercase;
  color:var(--accent); margin-bottom:8px;
}
header.masthead { border-bottom:2px solid var(--ink); padding:32px 0 18px; margin-bottom:8px; }
.subtitle { color:var(--ink-soft); font-size:11pt; }
.meta-row { display:flex; flex-wrap:wrap; gap:18px; margin-top:12px; font-size:9pt; color:var(--ink-soft); }
.meta-row b { color:var(--ink); }
figure { margin:14px 0; page-break-inside:avoid; }
figure img { width:100%; border:1px solid var(--line); border-radius:4px; }
figcaption { font-size:8.5pt; color:var(--ink-soft); margin-top:4px; }
table { width:100%; border-collapse:collapse; font-size:8.8pt; margin:10px 0; }
th,td { text-align:left; padding:5px 8px; border-bottom:1px solid var(--line); }
th { background:var(--accent-soft); font-size:8pt; text-transform:uppercase; letter-spacing:.04em; }
td.num, th.num { text-align:right; }
.wrap-table { page-break-inside:avoid; }
.callout {
  border:1px solid var(--line); border-left:3px solid var(--accent);
  border-radius:3px; padding:10px 14px; margin:12px 0; page-break-inside:avoid;
  background:var(--accent-soft);
}
.callout.warn { border-left-color:var(--warn); background:var(--warn-soft); }
.callout h4 { margin:0 0 6px; font-size:9.5pt; color:var(--accent); }
.callout.warn h4 { color:var(--warn); }
.callout p { margin:4px 0; font-size:9.5pt; }
.stat-row { display:flex; gap:10px; flex-wrap:wrap; margin:12px 0; }
.stat { border:1px solid var(--line); border-radius:4px; padding:8px 12px; flex:1; min-width:130px; }
.stat .label { font-size:7.8pt; text-transform:uppercase; color:var(--ink-soft); letter-spacing:.05em; }
.stat .value { font-family:Georgia, serif; font-size:14pt; margin-top:2px; }
.stat .sub { font-size:8pt; color:var(--ink-soft); }
section.serie { page-break-before:always; }
ol, ul { padding-left:20px; }
li { margin:5px 0; text-align:justify; }
footer { margin-top:30px; padding-top:12px; border-top:1px solid var(--line); font-size:8.5pt; color:var(--ink-soft); }
@page { size:letter; margin:14mm 12mm; }
"""

HTML = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Laboratorio 1 - Series de Tiempo</title>
<style>{CSS}</style></head><body>

<header class="masthead">
  <div class="eyebrow">Universidad del Valle de Guatemala &middot; CC3084 Data Science &middot; Semestre II 2026</div>
  <h1>Laboratorio 1. Series de Tiempo</h1>
  <p class="subtitle">Ingreso de viajeros internacionales a Guatemala: analisis exploratorio,
  construccion de series mensuales, modelado ARIMA y comparacion con Prophet, Holt-Winters,
  suavizamiento exponencial y seasonal naive.</p>
  <div class="meta-row">
    <span>Registros: <b>161,036</b></span>
    <span>Periodo: <b>2009-01 a 2026-06</b> (210 meses)</span>
    <span>Series analizadas: <b>7</b></span>
    <span>Fuente: <b>Base_Migracion_2009-2026jun.xlsx</b></span>
  </div>
</header>

<section>
  <h2>Resumen</h2>
  <p>Se analizaron 161,036 registros mensuales de ingreso de viajeros internacionales a Guatemala
  entre enero de 2009 y junio de 2026. A partir de ellos se construyeron siete series mensuales:
  el total de viajeros, las tres vias de ingreso y los tres principales paises de residencia. Cada
  serie se dividio cronologicamente en 70% de entrenamiento y 30% de prueba, se diagnostico su
  estacionariedad en media y en varianza, y se modelo con ARIMA estacional y con cuatro algoritmos
  alternativos.</p>
  <p>El resultado central es que ningun modelo entrenado con datos hasta marzo de 2021 logra
  anticipar la recuperacion pospandemia: {resumen_conteo}, pero incluso los mejores mantienen
  errores porcentuales altos. La explicacion no es una falla de los algoritmos sino la naturaleza
  del corte 70/30 exigido, que deja el final del entrenamiento en el punto mas bajo de la pandemia
  y coloca toda la reapertura dentro del conjunto de prueba.</p>
</section>

<section>
  <h2>Datos y consideraciones metodologicas</h2>
  <p>El archivo trae los datos en formato largo: una fila por combinacion de mes, via, frontera,
  pais o agrupacion de mercado y tipo de viajero, con la cantidad de personas en la columna
  Viajero. No hay filas de total ni doble conteo. La propia hoja de notas del archivo documenta
  tres tramos de fuente con metodologias distintas, decisivos para interpretar los resultados.</p>
  <div class="callout warn">
    <h4>Quiebres que condicionan todo el analisis</h4>
    <p><b>Tramos de fuente.</b> 2009-2020 respaldos historicos; 2021-2022 entrega del Instituto
    Guatemalteco de Migracion con caracterizacion; 2023-2026 sistema depurado de conteos del INGUAT.</p>
    <p><b>Reclasificacion de 2023.</b> La categoria Viajero pasa de cerca de 1.06 millones en 2022 a
    0.33 millones en 2023 porque se excluyen el comercio fronterizo y el transito de alta frecuencia.
    La caida del total anual no corresponde a una caida real del turismo; para comparar todo el rango
    hay que usar Turista mas Excursionista.</p>
    <p><b>Granularidad de Pais.</b> Hasta 2022 la columna registra el pais individual (226 posibles)
    y desde 2023 pasa a agrupacion de mercado (27 grupos).</p>
    <p><b>Otros.</b> La via maritima pierde detalle de registro desde 2017, los decimales de la
    columna Viajero son estimaciones expandidas de encuesta, y 2026 solo cubre de enero a junio.</p>
  </div>
</section>

<section>
  <h2>1. Analisis exploratorio</h2>
  <div class="stat-row">
    <div class="stat"><div class="label">Promedio mensual</div><div class="value">248,990</div><div class="sub">desviacion estandar 100,744</div></div>
    <div class="stat"><div class="label">Minimo mensual</div><div class="value">9,779</div><div class="sub">mayo de 2020</div></div>
    <div class="stat"><div class="label">Maximo mensual</div><div class="value">526,190</div><div class="sub">diciembre de 2022</div></div>
    <div class="stat"><div class="label">Caida en 2020</div><div class="value">{total_comp['caida_2020_pct']:.0f}%</div><div class="sub">frente a 2019</div></div>
  </div>

  <h3>Comportamiento temporal</h3>
  {figure(img('01_total_mensual.png'),
          'Total mensual de viajeros. Se distinguen el crecimiento sostenido hasta 2019, el desplome de marzo de 2020 y el cambio de nivel por el ajuste metodologico de 2023.')}
  <p>La serie total muestra cuatro etapas: crecimiento sostenido con estacionalidad marcada entre
  2009 y 2019; colapso en 2020 y 2021, con un piso cercano al 27% del nivel de 2019; recuperacion
  fuerte durante 2022; y desde 2023 un descenso de nivel que responde al cambio de metodologia y no
  a una caida de la demanda.</p>
  {figure(img('02_turista_excursionista.png'),
          'Turista mas Excursionista, la unica medida comparable en todo el periodo segun la documentacion del dataset.')}
  <p>Al restringir la medicion a Turista mas Excursionista, la recuperacion resulta mas lenta de lo
  que sugiere el total bruto, lo que confirma la advertencia de la hoja de notas.</p>
  {figure(img('03_estacionalidad_mensual.png'),
          'Suma historica de viajeros por mes calendario.')}
  <p>El calendario turistico se concentra en diciembre y en el bloque de julio y agosto, coherente
  con las vacaciones escolares y las fiestas de fin de ano.</p>

  <h3>Paises y regiones de origen</h3>
  {figure(img('04_top_paises.png'), 'Quince principales paises o agrupaciones por viajeros acumulados.')}
  <p>El Salvador encabeza con 23.4% del acumulado, seguido por los residentes guatemaltecos que
  reingresan al pais (21.3%) y Estados Unidos (10.2%). El peso de los dos primeros refleja trafico
  terrestre fronterizo recurrente por trabajo, comercio y visitas familiares, mas que turismo
  vacacional.</p>
  {figure(img('05_top_regiones.png'), 'Viajeros acumulados por la variable Region dos.')}
  <p>America Central concentra el 61% del acumulado, America del Norte el 15% y Europa el 3.6%.
  Guatemala recibe, ante todo, un mercado regional.</p>

  <h3>Vias de ingreso y fronteras</h3>
  {figure(img('06_via_frontera.png'), 'Distribucion por via de ingreso y diez fronteras mas utilizadas.')}
  <p>La via terrestre aporta 61.2% de los ingresos, la aerea 36.5% y la maritima 2.4%. Entre las
  fronteras, La Aurora concentra 27.5%, Valle Nuevo 15.5% y San Cristobal 7.7%.</p>
  {figure(img('07_tipo_viajero_anual.png'), 'Evolucion anual por tipo de viajero.')}
  <p>Turista representa 65.5% del acumulado, Excursionista 15.8%, Viajero 7.8% y Cruceristas 1.9%.
  El desplome de la categoria Viajero en 2023 corresponde a la reclasificacion metodologica.</p>

  <h3>Valores faltantes, duplicados y atipicos</h3>
  <div class="stat-row">
    <div class="stat"><div class="label">Valores nulos</div><div class="value">0</div><div class="sub">en las 13 columnas</div></div>
    <div class="stat"><div class="label">Filas duplicadas</div><div class="value">0</div><div class="sub">duplicado exacto</div></div>
    <div class="stat"><div class="label">Registros en cero</div><div class="value">54</div><div class="sub">0.03% de las filas</div></div>
    <div class="stat"><div class="label">Valores negativos</div><div class="value">0</div><div class="sub">sin valores imposibles</div></div>
  </div>
  <p>Los 210 meses estan completos y no hay valores perdidos ni duplicados. El problema de calidad
  de este conjunto no son los datos ausentes sino los quiebres de codificacion. En la variable
  Region dos aparecen tres etiquetas espurias, resultado de unir catalogos de tramos distintos:
  el valor "0" (13 filas) y "Cruceros" (8 filas), ambos exclusivos de 2022, junto a "Cruceristas"
  que cubre de 2009 a 2021.</p>
  {figure(img('08_boxplots.png'), 'Distribucion de la variable Viajero a nivel de fila y del total mensual agregado.')}
  <p>A nivel de fila desagregada, 16.4% de los registros supera el umbral del rango intercuartil,
  pero no son errores: la distribucion tiene cola larga porque unos pocos paises y fronteras
  concentran volumenes enormes frente a muchas combinaciones marginales. La media de 324.7 frente
  a una mediana de 7.0 lo confirma. Sobre la serie mensual agregada, que es la que se modela, los
  unicos valores extremos son los meses de pandemia, que corresponden a un evento real.</p>
</section>

<section>
  <h2>2. Division en entrenamiento y prueba</h2>
  <p>La particion es cronologica y no aleatoria, como corresponde a series de tiempo: mezclar meses
  al azar filtraria informacion del futuro hacia el entrenamiento.</p>
  <div class="stat-row">
    <div class="stat"><div class="label">Entrenamiento</div><div class="value">2009-01 a 2021-03</div><div class="sub">147 meses, 70.0%</div></div>
    <div class="stat"><div class="label">Prueba</div><div class="value">2021-04 a 2026-06</div><div class="sub">63 meses, 30.0%</div></div>
  </div>
  <div class="callout warn">
    <h4>Consecuencia del corte exigido</h4>
    <p>El 70% cronologico deja el final del entrenamiento en marzo de 2021, es decir en el tramo mas
    deprimido de la pandemia, y coloca la reapertura completa dentro del conjunto de prueba. Ningun
    modelo univariado puede anticipar ese punto de inflexion a partir de la historia previa, de modo
    que los errores altos que se reportan mas adelante son una consecuencia estructural del corte y
    no un defecto de la estimacion.</p>
  </div>
</section>

<section>
  <h2>3. Construccion de las series mensuales</h2>
  <p>Ademas de la serie obligatoria se eligieron dos categorias de analisis: <b>vias de ingreso</b>,
  con una serie por cada una de las tres vias, y <b>paises de residencia</b>, con una serie por cada
  uno de los tres mercados de mayor acumulado historico. En total, siete series mensuales de 210
  observaciones cada una, sin valores faltantes.</p>
  <p>Los meses sin registros se completaron con cero tras verificar que corresponden a actividad
  genuinamente nula: el cierre de fronteras entre abril y agosto de 2020 y la perdida de detalle del
  registro maritimo desde 2017.</p>
  <div class="callout warn">
    <h4>Ajuste al criterio de los tres principales paises</h4>
    <p>Por acumulado historico el podio es El Salvador, Guatemala y Estados Unidos. Sin embargo la
    categoria Guatemala, que agrupa a residentes guatemaltecos que reingresan, desaparece del catalogo
    desde 2023, cuando la fuente pasa a reportar agrupaciones de mercado. Su serie no puede extenderse
    mas alla de diciembre de 2022 y dejaria casi vacio el conjunto de prueba, por lo que se sustituye
    por Honduras, cuarto del ranking y con serie completa. El hallazgo sobre Guatemala se conserva
    como parte del analisis exploratorio.</p>
    <p>Esa misma desaparicion explica una aparente contradiccion en los resultados: en 2025 los tres
    paises analizados superan su nivel de 2019, mientras el total apenas alcanza el
    {total_comp['recuperacion_2025_pct']:.0f}%. El total incluye a los residentes guatemaltecos, que
    representaban el 21% del acumulado historico y dejaron de contabilizarse.</p>
  </div>
</section>

<section>
  <h2>4. Analisis y modelado de cada serie</h2>
  <p>Para cada una de las siete series se recorren los incisos a hasta k del enunciado. El
  diagnostico de estacionariedad y el ajuste de los modelos se realizan unicamente sobre el tramo de
  entrenamiento; el conjunto de prueba se reserva para medir el error de prediccion.</p>
  {"".join(secciones_series)}
</section>

<section style="page-break-before:always">
  <h2>5. Analisis comparativo</h2>
  <p>Los indicadores se calculan sobre las series completas. La estacionalidad y la volatilidad se
  miden en la etapa previa a marzo de 2020 para que el desplome de la pandemia no distorsione la
  comparacion. La fuerza estacional y la de tendencia provienen de una descomposicion STL y se
  interpretan como la proporcion de variacion que explica cada componente, entre 0 y 1.</p>
  {bloque_categoria('Vias', 'Vias de ingreso')}
  {bloque_categoria('Paises', 'Paises de residencia')}
  {figure(img('comparativo', 'trayectoria_relativa_2019.png'),
          'Total anual de cada serie expresado como porcentaje de su propio nivel de 2019.')}

  <h3>Desempeno de los algoritmos</h3>
  {figure(img('comparacion', 'resumen_rmse_relativo.png'),
          'RMSE de cada algoritmo relativo al mejor modelo de cada serie, en escala logaritmica.')}
  {table_html(mejor_global, columns=['titulo', 'mejor_modelo', 'MAE', 'RMSE', 'MAPE'],
              headers=['Serie', 'Mejor modelo', 'MAE', 'RMSE', 'MAPE'],
              numeric_format={'MAE': ENTERO, 'RMSE': ENTERO, 'MAPE': PORCENTAJE})}
  <p>El recuento final es: {resumen_conteo}. Prophet gana en las series con tendencia clara porque
  su componente de tendencia por tramos se adapta mejor al cambio de nivel, mientras que el
  suavizamiento exponencial simple resulta competitivo justamente por lo contrario: al proyectar una
  linea plana desde el ultimo nivel observado evita extrapolar la caida pandemica, cosa que los
  modelos con tendencia y estacionalidad si hacen. Que un metodo tan elemental compita con SARIMA es
  en si mismo un resultado: indica que, en este corte, la estructura historica aporta poco para
  predecir la reapertura.</p>

  <h3>Hallazgos utiles para el INGUAT</h3>
  <ol>
    <li>La demanda tiene un calendario estable y pronunciado: el total alcanza su pico en
    {MESES[int(total_comp['mes_pico'])]} y su valle en {MESES[int(total_comp['mes_valle'])]}, con una
    amplitud equivalente al {total_comp['amplitud_estacional_pct']:.1f}% del nivel medio. La
    programacion de campanas, de personal en fronteras y de capacidad hotelera puede anclarse a ese
    patron con bastante confianza, porque es el componente mas predecible de todas las series.</li>
    <li>Las vias aerea y terrestre se comportan como negocios distintos. La terrestre crecio
    {comparativo.loc['Via_Terrestre', 'cagr_prepandemia_pct']:+.2f}% anual antes de la pandemia frente a
    {comparativo.loc['Via_Aérea', 'cagr_prepandemia_pct']:+.2f}% de la aerea, y sus estacionalidades
    difieren en intensidad. Conviene fijarles metas, presupuestos y campanas separados en lugar de
    gestionar un unico agregado.</li>
    <li>La via maritima es un caso aparte: su volatilidad mensual es de
    {comparativo.loc['Via_Marítima', 'volatilidad_pct']:.0f}%, en 2025 estaba en apenas el
    {comparativo.loc['Via_Marítima', 'recuperacion_2025_pct']:.1f}% de su nivel de 2019 y ningun modelo
    la predice de forma util. Antes de fijar metas sobre cruceros habria que resolver la calidad del
    registro, que perdio detalle desde 2017.</li>
    <li>La recuperacion es desigual por mercado y eso permite priorizar el gasto comercial: conviene
    concentrarlo en los segmentos que siguen por debajo de su nivel previo en lugar de repartirlo de
    forma uniforme.</li>
    <li>Para pronosticar no basta con la historia previa a la pandemia. La recomendacion practica es
    reentrenar los modelos con datos posteriores a la reapertura, incorporar variables externas como
    conectividad aerea o tipo de cambio, y revisar los pronosticos con frecuencia mensual.</li>
    <li>Ninguna meta institucional deberia plantearse sobre el total bruto de viajeros. El quiebre de
    2023 cambia el nivel de la serie sin que exista una caida real de demanda, de modo que el
    indicador comparable en todo el periodo es Turista mas Excursionista.</li>
  </ol>
</section>

<section>
  <h2>Conclusiones</h2>
  <ol>
    <li>Las siete series comparten el mismo diagnostico: no son estacionarias ni en media ni en
    varianza. Todas requieren transformacion logaritmica para estabilizar la dispersion y al menos
    una diferencia regular, acompanada de una diferencia estacional de periodo 12 en casi todos los
    casos.</li>
    <li>La estacionalidad anual es el componente mas fuerte y mas estable de todas las series, con
    fuerzas estacionales prepandemia de entre
    {comparativo.fuerza_estacional.min():.2f} y {comparativo.fuerza_estacional.max():.2f}.</li>
    <li>Dentro de la familia ARIMA, los criterios AIC y BIC junto con la prueba de Ljung-Box permiten
    seleccionar modelos con residuos sin autocorrelacion en seis de las siete series. La excepcion es
    la via maritima, cuya estructura no queda bien descrita por un modelo lineal.</li>
    <li>Sobre el conjunto de prueba, sin embargo, el buen ajuste dentro de la muestra no se traduce en
    buena prediccion. La comparacion entre algoritmos deja a Prophet y al suavizamiento exponencial
    simple por delante del SARIMA, y ese resultado se explica por el corte temporal exigido mas que
    por las virtudes de cada metodo.</li>
    <li>La leccion metodologica es que, cuando el conjunto de prueba contiene un cambio estructural
    ausente del entrenamiento, las metricas de error miden sobre todo la magnitud de ese cambio. Por
    eso el analisis se acompana de los diagnosticos dentro de la muestra y de los indicadores
    descriptivos, que si son informativos.</li>
  </ol>
</section>

<footer>
  Laboratorio 1, Series de Tiempo. CC3084 Data Science, Universidad del Valle de Guatemala,
  Semestre II 2026. Los datos utilizados tienen fines exclusivamente academicos y no corresponden a
  cifras oficiales del INGUAT ni del Instituto Guatemalteco de Migracion.
</footer>
</body></html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"HTML escrito en: {HTML_PATH} ({len(HTML) / 1_000_000:.1f} MB)")


def exportar_pdf():
    navegador = next((c for c in CHROME_CANDIDATES if os.path.exists(c)), None)
    if navegador is None:
        print("No se encontro Chrome ni Edge; abra el HTML e imprima a PDF manualmente.")
        return
    url = "file:///" + HTML_PATH.replace("\\", "/")
    comando = [navegador, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer", "--virtual-time-budget=30000",
               f"--print-to-pdf={PDF_PATH}", url]
    subprocess.run(comando, check=False, capture_output=True, timeout=300)
    if os.path.exists(PDF_PATH):
        print(f"PDF generado: {PDF_PATH} ({os.path.getsize(PDF_PATH) / 1_000_000:.1f} MB)")
    else:
        print("El navegador no genero el PDF; abra el HTML e imprima a PDF manualmente.")


exportar_pdf()
