# -*- coding: utf-8 -*-
"""
Laboratorio 1 - Series de Tiempo (CC3084)
Utilidades compartidas: rutas, catalogo de series, carga y metricas de error.
"""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "outputs")
SER = os.path.join(OUT, "series")

SPLIT_DATE = pd.Timestamp("2021-04-01")   # primer mes del conjunto de prueba
SEASONAL_PERIOD = 12

# Catalogo de las 7 series: nombre de archivo -> (titulo legible, categoria, color)
SERIES_CATALOG = {
    "Total":               ("Total mensual de viajeros internacionales", "Total",  "#1f77b4"),
    "Via_Aérea":           ("Via de ingreso: Aerea",                     "Vias",   "#d62728"),
    "Via_Terrestre":       ("Via de ingreso: Terrestre",                 "Vias",   "#2ca02c"),
    "Via_Marítima":        ("Via de ingreso: Maritima",                  "Vias",   "#17becf"),
    "Pais_ElSalvador":     ("Pais de residencia: El Salvador",           "Paises", "#ff7f0e"),
    "Pais_Honduras":       ("Pais de residencia: Honduras",              "Paises", "#9467bd"),
    "Pais_EstadosUnidos":  ("Pais de residencia: Estados Unidos",        "Paises", "#8c564b"),
}

SERIES_NAMES = list(SERIES_CATALOG.keys())


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def load_series(name):
    """Carga la serie mensual completa (train + test) con frecuencia MS."""
    path = os.path.join(SER, f"{name}_completa.csv")
    s = pd.read_csv(path, index_col=0, parse_dates=True)["viajeros"]
    s = s.asfreq("MS")
    s.name = name
    return s


def split_series(s):
    """Divide la serie en entrenamiento y prueba segun SPLIT_DATE."""
    return s[s.index < SPLIT_DATE], s[s.index >= SPLIT_DATE]


def uses_log1p(s):
    """Las series con ceros (Maritima) requieren log1p en lugar de log."""
    return bool((s <= 0).any())


def transform(s, use_log, log1p):
    """Aplica la transformacion elegida para estabilizar varianza."""
    if not use_log:
        return s.copy()
    return np.log1p(s) if log1p else np.log(s)


def inverse_transform(values, use_log, log1p):
    """Devuelve los valores a la escala original de viajeros."""
    values = np.asarray(values, dtype=float)
    if not use_log:
        return values
    out = np.expm1(values) if log1p else np.exp(values)
    return np.clip(out, 0, None)


def error_metrics(actual, predicted):
    """MAE, RMSE y MAPE (esta ultima solo sobre meses con valor real positivo)."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mask = np.isfinite(actual) & np.isfinite(predicted)
    actual, predicted = actual[mask], predicted[mask]
    if len(actual) == 0:
        return {"MAE": np.nan, "RMSE": np.nan, "MAPE": np.nan}
    err = actual - predicted
    nonzero = actual > 0
    mape = (np.abs(err[nonzero] / actual[nonzero]).mean() * 100) if nonzero.any() else np.nan
    return {
        "MAE": float(np.abs(err).mean()),
        "RMSE": float(np.sqrt((err ** 2).mean())),
        "MAPE": float(mape),
    }


def seasonal_naive_forecast(train, horizon, period=SEASONAL_PERIOD):
    """Pronostico seasonal naive: repite el ultimo ciclo estacional observado."""
    last_cycle = np.asarray(train[-period:], dtype=float)
    reps = int(np.ceil(horizon / period))
    return np.tile(last_cycle, reps)[:horizon]


class Reporter:
    """Acumula texto de consola y lo guarda en un archivo de reporte."""

    def __init__(self):
        self.lines = []

    def __call__(self, *args):
        text = " ".join(str(a) for a in args)
        print(text)
        self.lines.append(text)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))
