# Laboratorio 1 - Series de Tiempo

Analisis de series de tiempo sobre el ingreso de viajeros internacionales a Guatemala
(enero 2009 - junio 2026), para el curso CC3084 Data Science de la Universidad del Valle
de Guatemala, Semestre II 2026.

## Integrantes

- Hugo Barillas
- Jose Pablo Lopez
- Luis Palacios

## Entregable

El informe final esta en [`informe/Laboratorio1_SeriesDeTiempo.pdf`](informe/Laboratorio1_SeriesDeTiempo.pdf).
No contiene codigo: todos los analisis, tablas y graficos se generan con los scripts de
`scripts/` y el informe los incorpora ya renderizados.

## Datos

`Base_Migracion_2009-2026jun.xlsx`, hoja `Datos` (161,036 filas) y hoja `Notas` con las
consideraciones metodologicas de la fuente. Los datos son de uso exclusivamente academico
y no corresponden a cifras oficiales del INGUAT ni del Instituto Guatemalteco de Migracion.

## Series analizadas

Ademas de la serie obligatoria se eligieron dos categorias de analisis, para un total de
siete series mensuales de 210 observaciones:

| Categoria | Series |
|---|---|
| Total | Total mensual de viajeros |
| Vias de ingreso | Aerea, Terrestre, Maritima |
| Paises de residencia | El Salvador, Honduras, Estados Unidos |

La particion es cronologica: entrenamiento de 2009-01 a 2021-03 (147 meses, 70%) y prueba
de 2021-04 a 2026-06 (63 meses, 30%).

## Estructura

```
scripts/
  lab_utils.py                  Rutas, catalogo de series, carga y metricas de error
  01_eda.py                     Analisis exploratorio (punto 1)
  02_series_construccion.py     Particion 70/30 y construccion de las series (puntos 2 y 3)
  03_analisis_series.py         Estacionariedad, descomposicion, ACF/PACF y ADF (punto 4 a-e)
  04_modelos_arima.py           Modelos ARIMA/SARIMA, residuos, AIC y BIC (punto 4 f-g)
  05_modelos_alternativos.py    Prophet, Holt-Winters, suavizamiento simple y seasonal naive (punto 4 h)
  06_comparacion_modelos.py     Predicciones y comparacion por MAE, RMSE y MAPE (punto 4 i-k)
  07_analisis_comparativo.py    Comparacion entre series (punto 5)
  08_build_report.py            Genera el informe HTML y lo exporta a PDF
outputs/                        Figuras, tablas y predicciones generadas
informe/                        Informe final en HTML y PDF
```

## Reproducir

```bash
pip install -r requirements.txt
python scripts/01_eda.py
python scripts/02_series_construccion.py
python scripts/03_analisis_series.py
python scripts/04_modelos_arima.py
python scripts/05_modelos_alternativos.py
python scripts/06_comparacion_modelos.py
python scripts/07_analisis_comparativo.py
python scripts/08_build_report.py
```

Los scripts deben correrse en ese orden: cada uno consume las salidas del anterior. El
ultimo paso requiere Chrome o Edge instalado para exportar el PDF; si no los encuentra,
deja el HTML listo para imprimirlo a PDF manualmente.
