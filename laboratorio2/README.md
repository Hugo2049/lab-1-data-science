# Laboratorio 2 - Deep Learning

Modelos LSTM y analisis de similitud de series con catch22, sobre las mismas series de
tiempo construidas en el Laboratorio 1 (ingreso de viajeros internacionales a Guatemala),
para el curso CC3084 Data Science de la Universidad del Valle de Guatemala, Semestre II 2026.

## Integrantes

- Hugo Barillas
- Jose Pablo Lopez
- Luis Palacios

## Estructura

```
scripts/
  lab2_utils.py                Rutas y catalogo de series (reutiliza scripts/lab_utils.py del Lab 1)
  01_lstm_avance.ipynb         Ejercicio 1: modelos LSTM (Total y Pais_ElSalvador) y comparacion vs Lab 1
  02_catch22_analisis.ipynb    Ejercicio 2: catch22, PCA, clustering, interpretacion y LSTM con features catch22
outputs/
  catch22/                     Matrices, tablas y figuras del analisis catch22
  lstm/                        Predicciones y metricas de los modelos LSTM
```

Las series de tiempo (train/test) se leen de `../outputs/series/`, generadas en el Laboratorio 1.

## Entorno

`pycatch22` y `tensorflow` requieren Python 3.10 o 3.11 en Windows (no hay wheel para 3.13+).

```bash
py -3.10 -m venv .venv310
.venv310\Scripts\python -m pip install -r requirements.txt
.venv310\Scripts\python -m ipykernel install --user --name lab2-py310 --display-name "Laboratorio 2 (Python 3.10)"
```

Al abrir los notebooks, seleccionar el kernel **"Laboratorio 2 (Python 3.10)"**.

## Reproducir

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=lab2-py310 scripts\01_lstm_avance.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=lab2-py310 scripts\02_catch22_analisis.ipynb
```
