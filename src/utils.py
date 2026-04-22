"""
utils.py
--------
Utilitaires.
"""

import matplotlib.pyplot as plt
import seaborn as sns


def set_style():
    """Style cohérent pour toutes les visualisations."""
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "figure.dpi": 110,
        "savefig.dpi": 140,
        "savefig.bbox": "tight",
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    })


def print_section(title: str):
    line = "=" * 60
    print(f"\n{line}\n{title}\n{line}")