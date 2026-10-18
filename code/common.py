"""Shared helpers for the TbCu7 stability screen.

Plain-language note: this file holds small tools the other scripts share
(reading chemical formulas, sorting crystal structures into families,
and the settings used everywhere). You do not need to open it.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CUR = ROOT / "data" / "curated"
PROC = ROOT / "data" / "processed"
REPORT = ROOT / "report"

CORE_M = ["Co", "Ti", "V", "Zr", "Nb", "Cu", "Si", "Ga", "Al", "Mo", "Cr", "Mn", "Hf"]
DATABASES = ["MP", "AFLOW", "JARVIS", "NOMAD-Alexandria", "OQMD", "GNoME"]

# Settings (every threshold used in the analysis lives here)
TAU_ACCESSIBLE = 0.050   # eV/atom: "formable as a metastable phase" window (primary)
TAU_SENSITIVITY = [0.025, 0.050, 0.100]
TOL_ON_HULL = 0.010      # eV/atom: numerical tolerance for "on the hull"
COMP_WINDOW = 0.10       # max |difference| in any atomic fraction for an entry to count as comparable
T_QUENCH = 1273.0        # K, temperature for the configurational-entropy term
KB = 8.617333262e-5      # eV/K
MU_B = 9.2740100783e-24  # A m^2
MU_0 = 1.25663706212e-6  # T m/A


def parse_formula(f):
    """'Fe17Sm2' -> {'Fe': 17, 'Sm': 2}. Handles fractional counts."""
    out = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", f):
        out[el] = out.get(el, 0) + (float(n) if n else 1.0)
    return out


def fractions(counts):
    tot = sum(counts.values())
    return {k: v / tot for k, v in counts.items()}


def family_of(counts, sg_number=None, nsites=None):
    """Assign a structure family from composition (and symmetry when known).

    Families relevant to the TbCu7 question:
      CaCu5  (1:5)     TM/R = 5        parent of TbCu7 (delta = 0)
      TbCu7  (1:7-ish) 5 < TM/R < 12   disordered; no ordered DB entry exists
      Th2Zn17/Th2Ni17 (2:17) TM/R = 8.5  ordered dumbbell variant (delta = 1/3)
      ThMn12 (1:12)    TM/R = 12        ordered dumbbell variant (delta = 1/2)
    R = Sm, plus Zr/Hf when the entry is an R-site-substituted 1:5 (Pmmm, 12 sites).
    Cubic Heusler / Laves-derived cells are excluded from the TbCu7 family set.
    """
    x, r_site = tm_per_r(counts)
    if x is None:
        return "no-Sm"
    cubic = sg_number is not None and sg_number >= 195
    if cubic and not (abs(x - 2) < 0.05 and sg_number == 227):
        return f"other(x={x:.2f})"
    fe_rich = (counts.get("Fe", 0) + counts.get("Co", 0)) / sum(counts.values()) >= 0.6
    for name, target, tol in STANDARD_RATIOS:
        if abs(x - target) < tol:
            if name == "MgCu2" and sg_number not in (227, None):
                break
            if name in ("CaCu5", "2:17", "3:29", "ThMn12") and not fe_rich:
                break
            return name
    if 5.3 < x < 12.3 and fe_rich:
        return "TbCu7-approximant"
    return f"other(x={x:.2f})"


STANDARD_RATIOS = [("CaCu5", 5.0, 0.3), ("2:17", 8.5, 0.3), ("3:29", 29 / 3, 0.1),
                   ("ThMn12", 12.0, 0.3), ("Sm5Fe17", 3.4, 0.05), ("PuNi3", 3.0, 0.05),
                   ("Ce2Ni7", 3.5, 0.05), ("MgCu2", 2.0, 0.05)]
R_SITE_CAPABLE = ("Zr", "Hf", "Ti", "Nb")


def _std(x):
    return any(abs(x - t) < tol for _, t, tol in STANDARD_RATIOS)


def tm_per_r(counts):
    """Transition-metal-site atoms per rare-earth-site atom.

    Sm always sits on the R site. Zr and Hf are placed on the R site whenever
    that gives a standard ratio (they are known to replace Sm in TbCu7/1:5
    phases). Ti and Nb are placed on the R site only if the transition-metal
    assignment gives no standard ratio. Returns (x, r_site_elements)."""
    sm = counts.get("Sm", 0)
    if sm == 0:
        return None, []
    tm_all = sum(v for k, v in counts.items() if k != "Sm")
    x_tm = tm_all / sm
    for el in R_SITE_CAPABLE:
        if el in counts:
            x_r = (tm_all - counts[el]) / (sm + counts[el])
            if el in ("Zr", "Hf") and _std(x_r):
                return x_r, ["Sm", el]
            if el in ("Ti", "Nb") and _std(x_r) and not _std(x_tm):
                return x_r, ["Sm", el]
    return x_tm, ["Sm"]


def delta_from_x(x):
    """TbCu7 R(1-d)T(5+2d): dumbbell fraction d from TM/R ratio x."""
    return (x - 5.0) / (x + 2.0)


def s_conf_per_atom(x):
    """Ideal configurational entropy (units of k_B per atom) of the random
    Sm / Fe-dumbbell occupation of the 1a site in TbCu7 at ratio x."""
    import math
    d = delta_from_x(x)
    if d <= 0 or d >= 1:
        return 0.0
    s = -(d * math.log(d) + (1 - d) * math.log(1 - d))
    return s / (6.0 + d)
