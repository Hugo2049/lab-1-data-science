# -*- coding: utf-8 -*-
import base64, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "outputs")
PRE = os.path.join(BASE, "outputs", "preliminar")
DEST = r"C:\Users\Jose\AppData\Local\Temp\claude\C--Users-Jose-Downloads-DATA\3ad7f542-2eb2-471b-b0b3-53610576f020\scratchpad\eda_report.html"

def b64(folder, name):
    with open(os.path.join(folder, name), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

IMG = {name: b64(OUT, name) for name in [
    "01_total_mensual.png","02_turista_excursionista.png","03_estacionalidad_mensual.png",
    "04_top_paises.png","05_top_regiones.png","06_via_frontera.png",
    "07_tipo_viajero_anual.png","08_boxplots.png"
]}

PRE_IMG = {name: b64(PRE, name) for name in [
    "Total_01_serie.png","Total_02_descomposicion_aditiva.png","Total_03_transformacion.png",
    "Total_04_acf.png","Total_05_pacf.png",
    "Via_Aérea_01_serie.png","Via_Aérea_02_descomposicion_aditiva.png","Via_Aérea_03_transformacion.png",
    "Via_Aérea_04_acf.png","Via_Aérea_05_pacf.png",
]}

HTML = f"""<!doctype html>
<title>EDA — Migración Internacional Guatemala 2009-2026</title>
<style>
:root {{
  --bg: #f7f5f0;
  --panel: #ffffff;
  --ink: #1e2a28;
  --ink-soft: #4b5a57;
  --line: #dcd6c8;
  --accent: #1d6b63;
  --accent-soft: #e4efec;
  --warn: #b5622a;
  --warn-soft: #f5e6da;
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'IBM Plex Sans', Arial, sans-serif;
  --font-mono: 'IBM Plex Mono', Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #14201d;
    --panel: #1b2b27;
    --ink: #eef2ee;
    --ink-soft: #a9bdb7;
    --line: #2c3d38;
    --accent: #5fbfae;
    --accent-soft: #233a35;
    --warn: #e0966a;
    --warn-soft: #3a2a20;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #14201d; --panel: #1b2b27; --ink: #eef2ee; --ink-soft: #a9bdb7;
  --line: #2c3d38; --accent: #5fbfae; --accent-soft: #233a35; --warn: #e0966a; --warn-soft: #3a2a20;
}}
:root[data-theme="light"] {{
  --bg: #f7f5f0; --panel: #ffffff; --ink: #1e2a28; --ink-soft: #4b5a57;
  --line: #dcd6c8; --accent: #1d6b63; --accent-soft: #e4efec; --warn: #b5622a; --warn-soft: #f5e6da;
}}
* {{ box-sizing: border-box; }}
body {{
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-body);
  line-height: 1.55;
  max-width: 920px;
  margin: 0 auto;
  padding: 3.5rem 1.5rem 6rem;
}}
h1, h2, h3 {{
  font-family: var(--font-display);
  font-weight: 600;
  text-wrap: balance;
  color: var(--ink);
}}
header.masthead {{
  border-bottom: 2px solid var(--ink);
  padding-bottom: 1.5rem;
  margin-bottom: 2.5rem;
}}
.eyebrow {{
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.6rem;
}}
h1 {{ font-size: 2.1rem; margin: 0 0 0.4rem; letter-spacing: -0.01em; }}
.subtitle {{ color: var(--ink-soft); font-size: 1.02rem; max-width: 60ch; }}
.meta-row {{
  display: flex; flex-wrap: wrap; gap: 1.5rem;
  margin-top: 1.2rem; font-family: var(--font-mono); font-size: 0.78rem; color: var(--ink-soft);
}}
.meta-row b {{ color: var(--ink); font-variant-numeric: tabular-nums; }}

section {{ margin: 3rem 0; }}
h2 {{
  font-size: 1.35rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.5rem;
  margin-bottom: 1.1rem;
  display: flex; align-items: baseline; gap: 0.6rem;
}}
h2 .tag {{
  font-family: var(--font-mono); font-size: 0.68rem; color: var(--accent);
  background: var(--accent-soft); padding: 0.2rem 0.5rem; border-radius: 3px;
  letter-spacing: 0.06em;
}}
h3 {{ font-size: 1.05rem; margin: 1.6rem 0 0.6rem; color: var(--ink); }}
p {{ max-width: 72ch; color: var(--ink); }}
p.soft {{ color: var(--ink-soft); }}

figure {{ margin: 1.4rem 0; }}
figure img {{
  width: 100%; border: 1px solid var(--line); border-radius: 6px;
  background: var(--panel);
}}
figcaption {{
  font-size: 0.82rem; color: var(--ink-soft); margin-top: 0.5rem; max-width: 72ch;
}}
.grid-2 {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem;
}}
@media (max-width: 720px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

.callout {{
  background: var(--panel); border: 1px solid var(--line); border-left: 3px solid var(--accent);
  border-radius: 4px; padding: 1rem 1.2rem; margin: 1.2rem 0;
}}
.callout.warn {{ border-left-color: var(--warn); }}
.callout h4 {{
  font-family: var(--font-mono); text-transform: uppercase; font-size: 0.72rem;
  letter-spacing: 0.08em; color: var(--accent); margin: 0 0 0.5rem;
}}
.callout.warn h4 {{ color: var(--warn); }}
.callout p {{ margin: 0.3rem 0; font-size: 0.93rem; }}

table {{
  width: 100%; border-collapse: collapse; font-size: 0.88rem; margin: 1rem 0;
  font-variant-numeric: tabular-nums;
}}
th, td {{ text-align: left; padding: 0.45rem 0.7rem; border-bottom: 1px solid var(--line); }}
th {{ font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-soft); }}
td.num, th.num {{ text-align: right; }}
.wrap-table {{ overflow-x: auto; }}

.stat-row {{ display: flex; gap: 1.2rem; flex-wrap: wrap; margin: 1.2rem 0; }}
.stat {{
  background: var(--panel); border: 1px solid var(--line); border-radius: 6px;
  padding: 0.9rem 1.1rem; min-width: 150px; flex: 1;
}}
.stat .label {{ font-family: var(--font-mono); font-size: 0.68rem; text-transform: uppercase; color: var(--ink-soft); letter-spacing: 0.05em; }}
.stat .value {{ font-family: var(--font-display); font-size: 1.5rem; margin-top: 0.2rem; font-variant-numeric: tabular-nums; }}
.stat .sub {{ font-size: 0.78rem; color: var(--ink-soft); margin-top: 0.2rem; }}

footer {{
  margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--line);
  font-size: 0.8rem; color: var(--ink-soft);
}}
</style>

<header class="masthead">
  <div class="eyebrow">CC3084 — Data Science · Laboratorio 1, Series de Tiempo</div>
  <h1>Ingreso de viajeros internacionales a Guatemala</h1>
  <p class="subtitle">Análisis exploratorio de datos (EDA) — base mensual desagregada por país, vía, frontera, región y tipo de viajero, enero 2009 a junio 2026.</p>
  <div class="meta-row">
    <span>Registros: <b>161,036</b></span>
    <span>Periodo: <b>2009-01 → 2026-06</b> (210 meses, sin huecos)</span>
    <span>Fuente: <b>Base_Migracion_2009-2026jun.xlsx</b></span>
  </div>
</header>

<section id="resumen">
  <h2><span class="tag">0</span> Resumen del dataset</h2>
  <p>El archivo trae 161,036 filas en formato largo: una fila por combinación de mes, vía, frontera, país/agrupación y tipo de viajero, con la cantidad de personas en la columna <em>Viajero</em>. No hay filas de total ni doble conteo. La hoja «Notas» del propio archivo documenta tres tramos de fuente con metodologías distintas, que son clave para interpretar la serie:</p>
  <div class="callout warn">
    <h4>Quiebres metodológicos a tener en cuenta</h4>
    <p><b>2009–2020</b> respaldos históricos · <b>2021–2022</b> entrega del IGM con caracterización · <b>2023–2026</b> sistema depurado de conteos del INGUAT.</p>
    <p>Desde 2023 la categoría <em>Viajero</em> excluye comercio fronterizo y tránsito de alta frecuencia, por lo que el total anual "cae" en 2023 sin que sea una caída real de turismo. Para comparar en todo el rango se debe usar <b>Turista + Excursionista</b>.</p>
    <p>Desde 2023 la columna <em>País</em> pasa de país individual (226 posibles) a agrupación de mercado (27 grupos). Los mercados principales siguen siendo comparables como serie.</p>
    <p>La vía Marítima pierde detalle de registro desde 2017.</p>
  </div>
</section>

<section id="temporal">
  <h2><span class="tag">a</span> Comportamiento temporal del número de viajeros</h2>
  <div class="stat-row">
    <div class="stat"><div class="label">Promedio mensual</div><div class="value">248,990</div><div class="sub">± 100,744 desv. est.</div></div>
    <div class="stat"><div class="label">Mínimo mensual</div><div class="value">9,779</div><div class="sub">mayo 2020 (pandemia)</div></div>
    <div class="stat"><div class="label">Máximo mensual</div><div class="value">526,190</div><div class="sub">diciembre 2022</div></div>
    <div class="stat"><div class="label">Caída pandemia</div><div class="value">−73%</div><div class="sub">total 2020 vs. 2019</div></div>
  </div>
  <figure>
    <img src="data:image/png;base64,{IMG['01_total_mensual.png']}" alt="Total mensual de viajeros 2009-2026">
    <figcaption>Fig. 1 — Total mensual de viajeros (todas las categorías). Se observa tendencia creciente 2009-2019, colapso abrupto en marzo-2020, y el quiebre metodológico de 2023 (línea naranja) que reduce el nivel de la serie sin ser una caída real de demanda turística.</figcaption>
  </figure>
  <p>A primera vista la serie muestra: (1) crecimiento sostenido y estacionalidad clara antes de 2020; (2) un colapso muy pronunciado en 2020-2021 por COVID-19, con piso alrededor del 27% del nivel de 2019; (3) una recuperación fuerte en 2022 (~92% del nivel de 2019, aún bajo la metodología antigua); y (4) desde 2023 un cambio de nivel por el ajuste metodológico, no por un cambio real en el volumen de visitantes.</p>

  <figure>
    <img src="data:image/png;base64,{IMG['02_turista_excursionista.png']}" alt="Serie Turista + Excursionista comparable en todo el periodo">
    <figcaption>Fig. 2 — Turista + Excursionista, la métrica recomendada por el propio dataset para comparar todo el periodo sin el sesgo del quiebre 2023. La recuperación real es más lenta de lo que sugiere el total bruto.</figcaption>
  </figure>
  <div class="callout">
    <h4>Hallazgo</h4>
    <p>Usando Turista + Excursionista (comparable en todo el rango), el 2025 cerró en apenas el <b>81%</b> del volumen de 2019, y el primer semestre de 2026 está en <b>78%</b> del primer semestre de 2019. La recuperación pospandemia del turismo genuino todavía no se completa, aunque el total bruto de "viajeros" ya luce recuperado.</p>
  </div>

  <figure>
    <img src="data:image/png;base64,{IMG['03_estacionalidad_mensual.png']}" alt="Estacionalidad mensual acumulada">
    <figcaption>Fig. 3 — Suma histórica de viajeros por mes calendario (2009-2026). Diciembre y julio-agosto destacan como los meses de mayor ingreso, patrón consistente con temporada vacacional y fin de año.</figcaption>
  </figure>
</section>

<section id="paises">
  <h2><span class="tag">b</span> Países con mayor cantidad de viajeros</h2>
  <figure>
    <img src="data:image/png;base64,{IMG['04_top_paises.png']}" alt="Top 15 países por viajeros acumulados">
    <figcaption>Fig. 4 — Top 15 países/agrupaciones por viajeros acumulados 2009-2026.</figcaption>
  </figure>
  <div class="wrap-table">
  <table>
    <thead><tr><th>#</th><th>País</th><th class="num">Viajeros acumulados</th><th class="num">% del total</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>El Salvador</td><td class="num">16,213,980</td><td class="num">23.4%</td></tr>
      <tr><td>2</td><td>Guatemala <span style="color:var(--ink-soft)">(residentes)</span></td><td class="num">14,792,330</td><td class="num">21.3%</td></tr>
      <tr><td>3</td><td>Estados Unidos de América</td><td class="num">7,047,843</td><td class="num">10.2%</td></tr>
      <tr><td>4</td><td>Honduras</td><td class="num">2,788,233</td><td class="num">4.0%</td></tr>
      <tr><td>5</td><td>México</td><td class="num">1,808,946</td><td class="num">2.6%</td></tr>
    </tbody>
  </table>
  </div>
  <div class="callout">
    <h4>Top 3 (criterio del laboratorio: acumulado histórico)</h4>
    <p><b>El Salvador → Guatemala → Estados Unidos</b>. El Salvador y Guatemala dominan por tráfico terrestre fronterizo recurrente (trabajo, comercio, visitas familiares), no solo turismo vacacional: al cruzar por país de residencia, "Guatemala" agrupa a guatemaltecos que reingresan al país y quedan registrados como viajero/turista/excursionista en el sistema.</p>
  </div>
</section>

<section id="regiones">
  <h2><span class="tag">c</span> Regiones con mayor cantidad de viajeros</h2>
  <figure>
    <img src="data:image/png;base64,{IMG['05_top_regiones.png']}" alt="Viajeros acumulados por Región dos">
    <figcaption>Fig. 5 — Viajeros acumulados por "Región dos" (agrupación continental), 2009-2026.</figcaption>
  </figure>
  <p><b>América del Centro</b> concentra el 61% del total acumulado, seguida de <b>América del Norte</b> (15%) y <b>Europa</b> (3.6%) — el Top 3 por el criterio del laboratorio. El mercado guatemalteco de viajeros es, ante todo, un mercado regional/fronterizo.</p>
</section>

<section id="via-frontera">
  <h2><span class="tag">d</span> Vías de ingreso y fronteras más utilizadas</h2>
  <figure>
    <img src="data:image/png;base64,{IMG['06_via_frontera.png']}" alt="Distribución por vía y top fronteras">
    <figcaption>Fig. 6 — Izquierda: distribución de viajeros por vía de ingreso. Derecha: top 10 fronteras por viajeros acumulados.</figcaption>
  </figure>
  <div class="grid-2">
    <div>
      <h3>Vía</h3>
      <p class="soft">Terrestre 61.2% · Aérea 36.5% · Marítima 2.4% (y esta última pierde detalle de registro desde 2017, ver nota metodológica).</p>
    </div>
    <div>
      <h3>Fronteras (Top 3, criterio acumulado)</h3>
      <p class="soft"><b>01 La Aurora</b> (aeropuerto, 27.5%) → <b>07 Valle Nuevo</b> (frontera con El Salvador, 15.5%) → <b>09 San Cristóbal</b> (frontera con El Salvador, 7.7%).</p>
    </div>
  </div>
</section>

<section id="tipo-viajero">
  <h2>Tipo de viajero</h2>
  <figure>
    <img src="data:image/png;base64,{IMG['07_tipo_viajero_anual.png']}" alt="Viajeros por año según tipo de viajero">
    <figcaption>Fig. 7 — Evolución anual por tipo de viajero. La caída abrupta de "Viajero" en 2023 es el efecto de la reclasificación metodológica descrita en la hoja Notas, no una caída real.</figcaption>
  </figure>
  <p>Turista domina con 65.5% del acumulado histórico, seguido de Excursionista (15.8%), Viajero (7.8%) y Cruceristas (1.9% — categoría descontinuada desde 2023, cuando los cruceros pasan a medirse por fuente portuaria externa).</p>
</section>

<section id="calidad">
  <h2><span class="tag">e</span> Valores faltantes, duplicados y atípicos</h2>
  <div class="stat-row">
    <div class="stat"><div class="label">Valores nulos</div><div class="value">0</div><div class="sub">en las 14 columnas</div></div>
    <div class="stat"><div class="label">Filas duplicadas</div><div class="value">0</div><div class="sub">duplicado exacto</div></div>
    <div class="stat"><div class="label">Viajero = 0</div><div class="value">54</div><div class="sub">de 161,036 filas (0.03%)</div></div>
    <div class="stat"><div class="label">Viajero &lt; 0</div><div class="value">0</div><div class="sub">sin valores imposibles</div></div>
  </div>
  <div class="callout">
    <h4>No hay huecos, pero sí quiebres</h4>
    <p>Los 210 meses de enero-2009 a junio-2026 están completos, sin meses faltantes. El "problema de calidad" real de este dataset no son NAs sino <b>quiebres metodológicos</b> (2022→2023 en Tipo de Viajero, cambio de granularidad de País, y pérdida de detalle marítimo desde 2017) documentados en la hoja «Notas» del propio archivo.</p>
  </div>
  <div class="callout warn">
    <h4>Categorías inconsistentes en "Región dos"</h4>
    <p>Aparecen 3 valores espurios: <code>"0"</code> (13 filas, 821 viajeros) y <code>"Cruceros"</code> (8 filas, 26,030 viajeros) — ambos exclusivos de 2022 — junto con <code>"Cruceristas"</code> (196 filas, 1,078,372 viajeros) que cubre 2009-2021. Es un artefacto de la unión de catálogos entre tramos de fuente, no un error aleatorio; para agregaciones por región conviene homologar estas tres etiquetas o excluirlas si se analiza turismo terrestre/aéreo regular.</p>
  </div>
  <div class="callout">
    <h4>Decimales en "Viajero"</h4>
    <p>31.8% de las filas (51,272) tienen valores no enteros (ej. 6,518.97). Según la documentación del dataset son <b>estimaciones expandidas de encuesta</b>, no errores de captura — corresponden sobre todo a los tramos 2009-2022. No requieren corrección, pero si se necesitan conteos enteros para algún modelo, deben redondearse de forma explícita y documentada.</p>
  </div>
  <div class="callout">
    <h4>Valores atípicos</h4>
    <p>A nivel de fila desagregada (país × vía × frontera × tipo), 16.4% de los registros exceden el umbral IQR (&gt;94.2 viajeros). Esto es esperable, no un error: la distribución es de cola larga porque unos pocos países/fronteras (El Salvador, Guatemala, La Aurora) concentran volúmenes enormes frente a la mayoría de combinaciones con pocos viajeros. A nivel de serie mensual agregada (la que se usará para el modelado) no se observan atípicos evidentes fuera del quiebre pandémico de 2020, que es un evento real, no un error de datos.</p>
  </div>
</section>

<section id="descriptivas">
  <h2><span class="tag">f</span> Estadísticas descriptivas</h2>
  <figure>
    <img src="data:image/png;base64,{IMG['08_boxplots.png']}" alt="Boxplots de Viajero">
    <figcaption>Fig. 8 — Izquierda: boxplot de Viajero a nivel de fila desagregada (escala log1p, por la cola larga). Derecha: boxplot del total mensual agregado (210 meses), donde los "outliers" bajos corresponden a los meses de pandemia.</figcaption>
  </figure>
  <div class="wrap-table">
  <table>
    <thead><tr><th></th><th class="num">Fila desagregada (n=161,036)</th><th class="num">Total mensual (n=210)</th></tr></thead>
    <tbody>
      <tr><td>Media</td><td class="num">324.7</td><td class="num">248,990</td></tr>
      <tr><td>Desv. estándar</td><td class="num">2,387.7</td><td class="num">100,744</td></tr>
      <tr><td>Mínimo</td><td class="num">0</td><td class="num">9,779</td></tr>
      <tr><td>P25</td><td class="num">2.0</td><td class="num">184,593</td></tr>
      <tr><td>Mediana</td><td class="num">7.0</td><td class="num">250,394</td></tr>
      <tr><td>P75</td><td class="num">38.9</td><td class="num">315,373</td></tr>
      <tr><td>Máximo</td><td class="num">92,336</td><td class="num">526,190</td></tr>
    </tbody>
  </table>
  </div>
  <p class="soft">La enorme diferencia entre media (324.7) y mediana (7.0) a nivel de fila confirma la distribución de cola muy larga propia de un dataset desagregado por 235 países × 22 fronteras × 3 vías × 4 tipos de viajero. Al agregar a serie mensual (lo relevante para el análisis de series de tiempo) la dispersión relativa baja mucho: CV de fila ≈ 7.4 vs. CV mensual ≈ 0.40.</p>
</section>

<section id="split">
  <h2>Construcción de series y partición entrenamiento / prueba</h2>
  <p>Se seleccionaron las categorías <b>Vías de ingreso</b> y <b>Países de residencia</b> como las dos categorías de análisis adicionales a la serie obligatoria. El dataset se dividió cronológicamente 70/30 (no aleatorio, por tratarse de series de tiempo):</p>
  <div class="stat-row">
    <div class="stat"><div class="label">Entrenamiento</div><div class="value">2009-01 → 2021-03</div><div class="sub">147 meses (70.0%)</div></div>
    <div class="stat"><div class="label">Prueba</div><div class="value">2021-04 → 2026-06</div><div class="sub">63 meses (30.0%)</div></div>
  </div>
  <p>A partir del entrenamiento se construyeron 7 series mensuales: <b>Total</b> (obligatoria), <b>Vía Aérea / Terrestre / Marítima</b>, y <b>Países</b> Top 3 acumulado. Los meses sin filas en la base (borde cerrado abr–ago 2020, y huecos de registro marítimo desde 2017) se rellenaron con 0, confirmando caso por caso que representan actividad genuinamente nula y no datos perdidos.</p>
  <div class="callout warn">
    <h4>Ajuste al criterio de Top-3 países</h4>
    <p>Por acumulado histórico el Top 3 es El Salvador → <b>Guatemala</b> → Estados Unidos. Sin embargo la categoría <em>"Guatemala"</em> en la columna País <b>desaparece del catálogo desde 2023</b> (el nuevo catálogo de "agrupación de mercado" ya no clasifica a residentes guatemaltecos reingresando); su serie mensual no puede extenderse más allá de dic-2022, lo que deja sin datos casi todo el conjunto de prueba. Se sustituye por <b>Honduras</b> (#4 en el ranking, serie completa 2009–2026) para la construcción y el modelado de series, dejando documentado el hallazgo sobre Guatemala como parte del EDA.</p>
  </div>
  <p class="soft">Series construidas: Total · Vía_Aérea · Vía_Terrestre · Vía_Marítima · País_ElSalvador · País_Honduras · País_EstadosUnidos.</p>
</section>

<section id="preliminar">
  <h2>Análisis preliminar de series (avance)</h2>
  <p>Primer análisis (incisos a–e del punto 4 del laboratorio) para dos de las siete series: la serie obligatoria <b>Total mensual</b> y <b>Vía Aérea</b>. El resto de las series se completará en el entregable final. El diagnóstico de estacionariedad se hace sobre el tramo de <b>entrenamiento</b> (2009-01 a 2021-03), como corresponde antes de ajustar modelos.</p>

  <h3>Serie 1 — Total mensual de viajeros internacionales</h3>
  <p class="soft"><b>a) Inicio/fin/frecuencia:</b> 2009-01 a 2026-06, mensual (MS), 210 observaciones (147 train / 63 test).</p>

  <figure>
    <img src="data:image/png;base64,{PRE_IMG['Total_01_serie.png']}" alt="Serie Total mensual con particion train/test">
    <figcaption>Fig. 9 — Serie completa con la partición entrenamiento (sombreado) / prueba y la ventana de pandemia resaltada.</figcaption>
  </figure>
  <p><b>b)</b> A primera vista: tendencia creciente y estacionalidad anual clara hasta 2020, quiebre abrupto por la pandemia, y recuperación posterior — consistente con lo visto en la sección de EDA general.</p>

  <figure>
    <img src="data:image/png;base64,{PRE_IMG['Total_02_descomposicion_aditiva.png']}" alt="Descomposicion aditiva Total">
    <figcaption>Fig. 10 — Descomposición aditiva (train, periodo=12): tendencia, componente estacional y residuo.</figcaption>
  </figure>
  <div class="callout">
    <h4>c) Estacionariedad</h4>
    <p>La tendencia no es constante (crece 2009-2019, colapsa en 2020) → <b>no estacionaria en media</b>. La desviación estándar por año pasa de ~28,000–60,000 (2009-2019) a 158,000 en 2020 → también hay indicio de <b>no estacionariedad en varianza</b>, con la dispersión escalando con el nivel de la serie.</p>
  </div>

  <figure>
    <img src="data:image/png;base64,{PRE_IMG['Total_03_transformacion.png']}" alt="Niveles vs log Total">
    <figcaption>Fig. 11 — Niveles vs. logaritmo (train). El log comprime la escala pero la tendencia y el quiebre de 2020 siguen presentes.</figcaption>
  </figure>
  <p><b>d)</b> Se recomienda transformación logarítmica para estabilizar varianza antes de diferenciar en media (CV en niveles ≈ 0.43).</p>

  <div class="grid-2">
    <figure>
      <img src="data:image/png;base64,{PRE_IMG['Total_04_acf.png']}" alt="ACF Total">
      <figcaption>Fig. 12 — ACF en niveles (decaimiento lento → no estacionaria) vs. primera diferencia.</figcaption>
    </figure>
    <figure>
      <img src="data:image/png;base64,{PRE_IMG['Total_05_pacf.png']}" alt="PACF Total">
      <figcaption>Fig. 13 — PACF en niveles vs. primera diferencia (referencia para p en el modelado posterior).</figcaption>
    </figure>
  </div>
  <div class="wrap-table">
  <table>
    <thead><tr><th>Prueba ADF (train)</th><th class="num">Estadístico</th><th class="num">p-valor</th><th>Conclusión (α=0.05)</th></tr></thead>
    <tbody>
      <tr><td>Niveles</td><td class="num">−1.970</td><td class="num">0.300</td><td>No estacionaria</td></tr>
      <tr><td>Log(niveles)</td><td class="num">−2.236</td><td class="num">0.194</td><td>No estacionaria</td></tr>
      <tr><td>1ª diferencia</td><td class="num">−3.206</td><td class="num">0.020</td><td>Estacionaria</td></tr>
      <tr><td>1ª diferencia de log</td><td class="num">−3.100</td><td class="num">0.027</td><td>Estacionaria</td></tr>
      <tr><td>1ª dif. + dif. estacional(12)</td><td class="num">−5.795</td><td class="num">&lt;0.001</td><td>Estacionaria</td></tr>
    </tbody>
  </table>
  </div>
  <p><b>e)</b> El ACF en niveles decae muy lentamente (autocorrelación significativa en lags altos) y el ADF no rechaza H0 en niveles ni en log → confirma no estacionariedad en media. Tras una diferenciación regular (d=1) el ADF sí rechaza H0 → <b>se necesita al menos d=1</b> (y valorar una diferenciación estacional adicional dado el patrón anual) para lograr estacionariedad en media.</p>

  <h3>Serie 2 — Vía Aérea</h3>
  <p class="soft"><b>a) Inicio/fin/frecuencia:</b> 2009-01 a 2026-06, mensual (MS), 210 observaciones (147 train / 63 test).</p>

  <figure>
    <img src="data:image/png;base64,{PRE_IMG['Via_Aérea_01_serie.png']}" alt="Serie Via Aerea con particion train/test">
    <figcaption>Fig. 14 — Serie completa de la vía Aérea, con partición train/test y ventana de pandemia.</figcaption>
  </figure>
  <p><b>b)</b> Mismo patrón general que el total (tendencia + estacionalidad + colapso 2020), pero con una caída relativa aún más pronunciada durante la pandemia por el cierre casi total del Aeropuerto La Aurora a vuelos comerciales.</p>

  <figure>
    <img src="data:image/png;base64,{PRE_IMG['Via_Aérea_02_descomposicion_aditiva.png']}" alt="Descomposicion aditiva Via Aerea">
    <figcaption>Fig. 15 — Descomposición aditiva (train, periodo=12).</figcaption>
  </figure>
  <div class="callout">
    <h4>c) Estacionariedad</h4>
    <p>Tendencia creciente 2009-2019 con quiebre marcado en 2020 → <b>no estacionaria en media</b>. La desv. estándar anual pasa de ~11,000–18,000 a 46,000 en 2020 → <b>no estacionaria en varianza</b>.</p>
  </div>

  <figure>
    <img src="data:image/png;base64,{PRE_IMG['Via_Aérea_03_transformacion.png']}" alt="Niveles vs log Via Aerea">
    <figcaption>Fig. 16 — Niveles vs. logaritmo (train).</figcaption>
  </figure>
  <p><b>d)</b> También se recomienda transformación logarítmica (CV en niveles ≈ 0.33, algo menor que el total pero con el mismo patrón de heterocedasticidad ligada al nivel).</p>

  <div class="grid-2">
    <figure>
      <img src="data:image/png;base64,{PRE_IMG['Via_Aérea_04_acf.png']}" alt="ACF Via Aerea">
      <figcaption>Fig. 17 — ACF en niveles vs. primera diferencia.</figcaption>
    </figure>
    <figure>
      <img src="data:image/png;base64,{PRE_IMG['Via_Aérea_05_pacf.png']}" alt="PACF Via Aerea">
      <figcaption>Fig. 18 — PACF en niveles vs. primera diferencia.</figcaption>
    </figure>
  </div>
  <div class="wrap-table">
  <table>
    <thead><tr><th>Prueba ADF (train)</th><th class="num">Estadístico</th><th class="num">p-valor</th><th>Conclusión (α=0.05)</th></tr></thead>
    <tbody>
      <tr><td>Niveles</td><td class="num">−2.364</td><td class="num">0.152</td><td>No estacionaria</td></tr>
      <tr><td>Log(niveles)</td><td class="num">−4.018</td><td class="num">0.001</td><td>Estacionaria*</td></tr>
      <tr><td>1ª diferencia</td><td class="num">−4.068</td><td class="num">0.001</td><td>Estacionaria</td></tr>
      <tr><td>1ª diferencia de log</td><td class="num">−3.214</td><td class="num">0.019</td><td>Estacionaria</td></tr>
      <tr><td>1ª dif. + dif. estacional(12)</td><td class="num">−6.360</td><td class="num">&lt;0.001</td><td>Estacionaria</td></tr>
    </tbody>
  </table>
  </div>
  <p><b>e)</b> El ADF en niveles no rechaza H0 y el ACF decae lentamente → no estacionaria en media. El ADF sobre el log en niveles ya resulta significativo (*), pero la tendencia sigue siendo visible en la descomposición, así que no se toma como estacionariedad real: se prioriza la evidencia conjunta (gráfico + ACF + ADF) y se concluye que <b>se necesita al menos d=1</b> para estabilizar la media, igual que en la serie Total.</p>

  <div class="callout warn">
    <h4>Pendiente para el entregable final (26 de julio)</h4>
    <p>Repetir este mismo análisis (a–e) para las 5 series restantes (Vía Terrestre, Vía Marítima, País El Salvador, País Honduras, País Estados Unidos), y continuar con los incisos f–k del punto 4 (selección de p/d/q, modelos ARIMA, Prophet/Holt-Winters/suavizamiento/seasonal naive, predicción sobre el conjunto de prueba, métricas MAE/RMSE/AIC/BIC) y el punto 5 (análisis comparativo entre series).</p>
  </div>
</section>

<footer>
  Laboratorio 1 — Series de Tiempo · CC3084 Data Science · Universidad del Valle de Guatemala.
  Datos con fines exclusivamente académicos; no corresponden a cifras oficiales de INGUAT ni del Instituto Guatemalteco de Migración.
</footer>
"""

with open(DEST, "w", encoding="utf-8") as f:
    f.write(HTML)
print("Escrito:", DEST, len(HTML), "bytes de HTML (antes de imagenes ya incluidas)")
