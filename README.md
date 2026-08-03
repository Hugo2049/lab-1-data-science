# Laboratorios CC3084 - Data Science

Repositorio del curso CC3084 Data Science, Universidad del Valle de Guatemala, Semestre II 2026.

## Integrantes

- Hugo Barillas
- Jose Pablo Lopez
- Luis Palacios

---

## Laboratorio 1 - Series de Tiempo

Analisis de series de tiempo sobre el ingreso de viajeros internacionales a Guatemala
(enero 2009 - junio 2026).

**Entregable:** [`laboratorio1/informe/Laboratorio1_SeriesDeTiempo.pdf`](laboratorio1/informe/Laboratorio1_SeriesDeTiempo.pdf)

```
laboratorio1/
  scripts/          Scripts Python (EDA, ARIMA, Prophet, comparacion)
  outputs/          Figuras, tablas y predicciones generadas
  informe/          Informe final en HTML y PDF
```

```bash
pip install -r requirements.txt
python laboratorio1/scripts/01_eda.py
# ... scripts 02 a 08 en orden
```

---

## Laboratorio 2 - Deep Learning

Modelos LSTM y analisis de similitud con catch22 sobre las mismas series del Lab 1.

**Entregables:** notebooks en [`laboratorio2/scripts/`](laboratorio2/scripts/) con analisis y resultados.

```
laboratorio2/
  scripts/
    01_lstm_avance.ipynb       Ejercicio 1: LSTM + comparacion vs Lab 1
    02_catch22_analisis.ipynb  Ejercicio 2: catch22, PCA, clustering, LSTM con features
  outputs/                     Tablas y figuras generadas
```

Requiere Python 3.10 y las dependencias de [`laboratorio2/requirements.txt`](laboratorio2/requirements.txt).
Ver instrucciones de entorno en [`laboratorio2/README.md`](laboratorio2/README.md).

