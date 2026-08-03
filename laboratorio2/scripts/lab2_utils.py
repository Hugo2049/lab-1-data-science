# -*- coding: utf-8 -*-
"""
Laboratorio 2 - Deep Learning y catch22 (CC3084)
Utilidades compartidas: rutas, catalogo de series (reutilizado del Laboratorio 1).
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # .../laboratorio2
LAB1_BASE = os.path.join(os.path.dirname(BASE), "laboratorio1")
LAB1_SCRIPTS = os.path.join(LAB1_BASE, "scripts")
LAB1_SERIES = os.path.join(LAB1_BASE, "outputs", "series")
LAB1_TABLAS = os.path.join(LAB1_BASE, "outputs", "tablas")

OUT = os.path.join(BASE, "outputs")

if LAB1_SCRIPTS not in sys.path:
    sys.path.insert(0, LAB1_SCRIPTS)

from lab_utils import SERIES_CATALOG, SERIES_NAMES, SPLIT_DATE, error_metrics  # noqa: E402,F401


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def load_series_completa(name):
    import pandas as pd
    path = os.path.join(LAB1_SERIES, f"{name}_completa.csv")
    s = pd.read_csv(path, index_col=0, parse_dates=True)["viajeros"]
    s = s.asfreq("MS")
    s.name = name
    return s


def load_series_train_test(name):
    import pandas as pd
    train = pd.read_csv(os.path.join(LAB1_SERIES, f"{name}_train.csv"),
                         index_col=0, parse_dates=True)["viajeros"]
    test = pd.read_csv(os.path.join(LAB1_SERIES, f"{name}_test.csv"),
                        index_col=0, parse_dates=True)["viajeros"]
    return train, test
