"""05_figures.py: draw the four figures.

Plain-language note: turns the result tables into pictures in report/figures/.
Every figure carries a draft stamp until you have checked the numbers; then run
python code/05_figures.py --final to remove the stamp.
"""
import csv
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from common import PROC, REPORT, TAU_ACCESSIBLE

FINAL = "--final" in sys.argv
FIG = REPORT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Reference palette (dataviz skill, light mode), validated: adjacent CVD dE >= 9.1
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {"MP": "#2a78d6", "JARVIS": "#eb6834", "NOMAD-Alexandria": "#1baf7a", "OQMD": "#eda100"}
MARK = {"MP": "o", "JARVIS": "s", "NOMAD-Alexandria": "D", "OQMD": "^"}
STATUS = {"hit": "#0ca30c", "miss": "#d03b3b", "false alarm": "#fab219", "correct reject": "#0ca30c", "no data": "#e1e0d9"}
LABEL = {"NOMAD-Alexandria": "NOMAD (Alexandria)"}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.facecolor": SURF, "figure.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.8, "grid.linestyle": "-"})


def stamp(fig):
    if not FINAL:
        fig.text(0.99, 0.01, "D" + "RAFT - not yet verified", ha="right", va="bottom", fontsize=8, color=MUTED)


def title(ax, t, sub, top=0.86):
    fig = ax.figure
    h = fig.get_figheight()
    fig.text(0.015, 1 - 0.1 / h, t, fontsize=12, color=INK, fontweight="bold", va="top", ha="left")
    fig.text(0.015, 1 - 0.38 / h, sub, fontsize=9, color=INK2, va="top", ha="left")
    fig.tight_layout(rect=(0, 0.02, 1, top))


stats = json.load(open(REPORT / "stats.json"))

# ---------- Figure 1: TbCu7 proxy along Sm-Fe
path = list(csv.DictReader(open(PROC / "tbcu7_binary_path.csv")))
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.axvspan(9.0, 10.0, color="#cde2fb", alpha=0.6, lw=0, zorder=0)
ax.text(9.5, 0.97, "observed TbCu7\n(SmFe9 to SmFe10)", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8, color=INK2)
ax.axhline(TAU_ACCESSIBLE * 1000, color=MUTED, lw=1)
ax.text(5.05, TAU_ACCESSIBLE * 1000 + 3, f"{TAU_ACCESSIBLE*1000:.0f} meV/atom formability window", fontsize=8, color=INK2)
for db, col in SERIES.items():
    pts = [(float(r["x_TM_per_R"]), float(r["dE_proxy_eV_atom"]) * 1000) for r in path if r["database"] == db and r["dE_proxy_eV_atom"]]
    if not pts:
        continue
    xs, ys = zip(*pts)
    ax.plot(xs, ys, "-" + MARK[db], color=col, lw=2, ms=6, mec=SURF, mew=1.5, solid_capstyle="round", zorder=3, label=LABEL.get(db, db))
    if db == "JARVIS":
        ax.annotate(LABEL.get(db, db), (xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=INK2)
ax.annotate("MP, OQMD, NOMAD (Alexandria):\n16-24 meV everywhere; flat line", (12, 22), xytext=(10.3, 75), fontsize=8, color=INK2,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.set_xlim(4.8, 13.6)
ax.set_ylim(-5, 280)
ax.set_xticks([5, 6, 7, 8, 8.5, 9, 10, 11, 12])
ax.set_xticklabels(["5\nSmFe5", "6", "7", "8", "8.5\nSm2Fe17", "9", "10", "11", "12\nSmFe12"])
ax.set_xlabel("Fe atoms per Sm-site atom (x in SmFe_x)")
ax.set_ylabel("TbCu7 proxy: energy above hull (meV/atom)")
title(ax, "TbCu7 stability proxy along the Sm-Fe line",
      "Lower envelope of each database's ordered relatives, minus its convex hull.\nAFLOW and GNoME have no Sm-Fe entries, so they draw no line.", top=0.87)
ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0.0, 0.88))
stamp(fig)
fig.savefig(FIG / "fig1_tbcu7_proxy_path.png", dpi=200)
plt.close(fig)

# ---------- Figure 2: discrimination dot plot
disc = stats["discrimination"]
dbs = [d for d in ["MP", "OQMD", "NOMAD-Alexandria", "JARVIS"] if disc.get(d)]
phase_keys = [("Sm2Fe17_stable_meV", "Sm2Fe17: stable", "#2a78d6", "o", -0.2),
              ("TbCu7_x9_metastable_meV", "TbCu7 SmFe9: forms by quenching", "#eb6834", "D", 0.0),
              ("SmFe12_not_formed_by_RS_meV", "SmFe12: does not form by quenching", "#1baf7a", "s", 0.2)]
fig, ax = plt.subplots(figsize=(8, 4.0))
for i, db in enumerate(dbs):
    vals = [disc[db][k] for k, *_ in phase_keys]
    ax.plot([min(vals), max(vals)], [i, i], color=AXIS, lw=1, zorder=1)
    for (k, lab, col, mk, dy) in phase_keys:
        ax.plot(disc[db][k], i + dy, mk, color=col, ms=8, mec=SURF, mew=2, zorder=3, label=lab if i == 0 else None)
    ax.text(300, i, f"spread {disc[db]['spread_meV']:.0f} meV", va="center", fontsize=8, color=INK2)
ax.set_xscale("log")
ax.set_xlim(8, 450)
ax.set_xticks([10, 20, 50, 100, 200])
ax.set_xticklabels(["10", "20", "50", "100", "200"])
ax.set_yticks(range(len(dbs)))
ax.set_yticklabels([LABEL.get(d, d) for d in dbs], color=INK)
ax.set_ylim(-0.6, len(dbs) - 0.4)
ax.grid(axis="y", visible=False)
ax.set_xlabel("energy above hull (meV/atom, log scale)")
title(ax, "Can the databases tell three Sm-Fe phases apart?",
      "Three lab outcomes in the same composition region. A useful screen separates them\nby more than typical DFT error (about 20-30 meV/atom). Sm2Fe17 should sit at 0.", top=0.84)
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.4, -0.22), ncol=3)
stamp(fig)
fig.savefig(FIG / "fig2_discrimination.png", dpi=200)
plt.close(fig)

# ---------- Figure 3: verdict matrix
vm = list(csv.DictReader(open(PROC / "validation_matrix.csv")))
obs_ids = list(dict.fromkeys(r["obs_id"] for r in vm))
dblist = ["MP", "AFLOW", "JARVIS", "NOMAD-Alexandria", "OQMD", "GNoME"]
info = {r["obs_id"]: f"{r['obs_id']}  {r['system']}  {r['test_family']}{' (not formed)' if r['test_outcome']=='not_formed' else ''}" for r in vm}
code = {"hit": "H", "miss": "M", "false alarm": "FA", "correct reject": "CR", "no data": "-"}
fig, ax = plt.subplots(figsize=(8, 9.5))
for i, o in enumerate(obs_ids):
    for j, db in enumerate(dblist):
        r = next(r for r in vm if r["obs_id"] == o and r["database"] == db)
        v = r["verdict_50meV"]
        ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, color=STATUS[v], lw=0))
        txt = code[v]
        tc = INK if v in ("false alarm", "no data") else "#ffffff"
        ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=8, color=tc, fontweight="bold")
ax.set_xlim(0, len(dblist))
ax.set_ylim(len(obs_ids), 0)
ax.set_xticks([j + 0.5 for j in range(len(dblist))])
ax.set_xticklabels([LABEL.get(d, d).replace(" (", "\n(") for d in dblist], color=INK, fontsize=8)
ax.xaxis.tick_top()
ax.set_yticks([i + 0.5 for i in range(len(obs_ids))])
ax.set_yticklabels([info[o] for o in obs_ids], fontsize=8, color=INK)
ax.grid(False)
for s in ax.spines.values():
    s.set_visible(False)
ax.tick_params(length=0)
fig.text(0.015, 0.99, "Database verdict for each lab observation", fontsize=12, color=INK, fontweight="bold", va="top")
fig.text(0.015, 0.97, "50 meV/atom formability window; '-' means the database has no comparable entry", fontsize=9, color=INK2, va="top")
handles = [Patch(color=STATUS["hit"], label="H hit / CR correct reject"), Patch(color=STATUS["miss"], label="M miss"),
           Patch(color=STATUS["false alarm"], label="FA false alarm"), Patch(color=STATUS["no data"], label="- no comparable entry")]
ax.legend(handles=handles, frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.35, -0.01), ncol=2)
stamp(fig)
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
fig.savefig(FIG / "fig3_verdict_matrix.png", dpi=200)
plt.close(fig)

# ---------- Figure 4: magnetization
mg = stats["magnetization_O01"]
fig, ax = plt.subplots(figsize=(8, 3.3))
lo, hi = mg["measured_m_Fe_0K_range"]
rows = [("Measured, room temperature (Katter 1991)", mg["measured_m_Fe_RT"], INK2, "o"),
        ("Measured, scaled to 0 K (range)", (lo + hi) / 2, INK, "|")]
for db in ["JARVIS", "NOMAD-Alexandria"]:
    v = mg["computed"].get(db)
    if v != "":
        rows.append((f"{LABEL.get(db, db)} (0 K, DFT)", float(v), SERIES[db], MARK[db]))
for i, (lab, v, col, mk) in enumerate(rows):
    if mk == "|":
        ax.plot([lo, hi], [i, i], color=col, lw=4, solid_capstyle="round")
    else:
        ax.plot(v, i, mk, color=col, ms=9, mec=SURF, mew=2)
    ax.text(v if mk != "|" else hi, i, f"  {v:.2f}" if mk != "|" else f"  {lo:.2f}-{hi:.2f}", va="center", fontsize=8, color=INK2)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows], color=INK, fontsize=8)
ax.set_ylim(len(rows) - 0.5, -0.5)
ax.set_xlim(1.3, 2.5)
ax.grid(axis="y", visible=False)
ax.set_xlabel("Fe moment in TbCu7 SmFe9 (Bohr magnetons per Fe)")
title(ax, "Computed vs measured Fe moment, TbCu7 SmFe9",
      "MP and OQMD expose no moments without an account; AFLOW and GNoME have no Sm-Fe entries.", top=0.80)
stamp(fig)
fig.savefig(FIG / "fig4_magnetization.png", dpi=200)
plt.close(fig)
print("figures written to", FIG)
