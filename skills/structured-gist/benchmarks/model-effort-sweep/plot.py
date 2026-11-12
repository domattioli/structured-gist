#!/usr/bin/env python3
"""
Plots for the model-effort sweep. Standard library only; writes SVG text.

Reads results/sweep.json (from score.py) and writes

    results/plots/<metric>.svg   one chart per metric
    results/plots/overview.svg   2 x 3 small multiples of the first six

x axis: effort (in config order). One line per generator, each with its own
color and marker shape, plus a legend. y: mean over cases, with min-max
whiskers. Colors are CSS custom properties with a prefers-color-scheme: dark
override, so the files read on GitHub's light and dark themes.

Output is deterministic: the same sweep.json gives byte-identical SVGs
(no timestamps, fixed number formatting, config-ordered iteration).

Usage:
    python3 plot.py [--source resolved|<judge name>]
"""
import argparse
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent

METRICS = [
    ("task_weighted_fact_retention", "Task-weighted fact retention", "retention (0-1)"),
    ("relation_retention", "Relation retention", "retention (0-1)"),
    ("recoverability", "Recoverability", "questions answered (0-1)"),
    ("reduction_pct", "Reduction", "reduction vs source (%)"),
    ("lint_violations", "Lint violations", "violations per outline"),
    ("unsupported_claim_count", "Unsupported claims", "confirmed unsupported claims"),
    ("output_tokens", "Output tokens", "output tokens per call"),
    ("total_tokens", "Total tokens", "input + output tokens per call"),
]
UNIT_RANGE = {"task_weighted_fact_retention", "relation_retention", "recoverability"}

LIGHT = ["#0072b2", "#d55e00", "#009e73", "#cc79a7", "#b8860b", "#56b4e9"]
DARK = ["#5cb3ff", "#ff8c42", "#3ddc97", "#e39ad0", "#f5c242", "#9fd8ff"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def fmt(v: float) -> str:
    """Fixed formatting so output is byte-stable across runs."""
    r = round(v, 2)
    if r == int(r):
        return str(int(r))
    return f"{r:.2f}".rstrip("0").rstrip(".")


def nice_ticks(lo: float, hi: float, n: int = 5) -> list:
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start = math.floor(lo / step) * step
    ticks, t = [], start
    while t <= hi + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    if ticks[-1] < hi:
        ticks.append(round(ticks[-1] + step, 10))
    return ticks


def style_block() -> str:
    light = ";".join(f"--c{i}:{c}" for i, c in enumerate(LIGHT))
    dark = ";".join(f"--c{i}:{c}" for i, c in enumerate(DARK))
    # Series rules set stroke only. Fill applies to filled markers (.mk) alone,
    # so .line, .whisker and .open paths can never be filled by a series rule.
    series = "".join(f".s{i}{{stroke:var(--c{i})}}.mk.s{i}{{fill:var(--c{i})}}" for i in range(len(LIGHT)))
    return (
        "<style>"
        f"svg{{--bg:#ffffff;--fg:#1f2328;--muted:#59636e;--grid:#d1d9e0;{light}}}"
        "@media (prefers-color-scheme: dark){"
        f"svg{{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--grid:#3d444d;{dark}}}}}"
        ".bg{fill:var(--bg)}"
        f"text{{fill:var(--fg);font-family:{FONT}}}"
        ".muted{fill:var(--muted)}"
        ".axis{stroke:var(--fg);stroke-width:1;fill:none}"
        ".grid{stroke:var(--grid);stroke-width:1;fill:none}"
        ".line{fill:none;stroke-width:2}"
        ".whisker{fill:none;stroke-width:1.5;opacity:0.45}"
        ".open{fill:none;stroke-width:2}"
        + series
        + "</style>"
    )


def marker(i: int, x: float, y: float, r: float = 4.5) -> str:
    cls = f"mk s{i}"
    shape = i % 6
    if shape == 0:
        return f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>'
    if shape == 1:
        return f'<rect class="{cls}" x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}"/>'
    if shape == 2:
        pts = [(x, y - r * 1.2), (x + r * 1.1, y + r * 0.8), (x - r * 1.1, y + r * 0.8)]
    elif shape == 3:
        pts = [(x, y - r * 1.3), (x + r * 1.3, y), (x, y + r * 1.3), (x - r * 1.3, y)]
    elif shape == 5:
        pts = [(x, y + r * 1.2), (x + r * 1.1, y - r * 0.8), (x - r * 1.1, y - r * 0.8)]
    else:  # 4: cross
        d = r * 1.1
        return (f'<path class="s{i} open" fill="none" d="M{x - d:.1f},{y - d:.1f}L{x + d:.1f},{y + d:.1f}'
                f'M{x - d:.1f},{y + d:.1f}L{x + d:.1f},{y - d:.1f}"/>')
    return f'<polygon class="{cls}" points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}"/>'


def series_for(sweep: dict, source: str, metric: str) -> dict:
    agg = sweep.get("aggregate", {}).get(source, {})
    out = {}
    for g in sweep["generators"]:
        out[g] = [agg.get(g, {}).get(e, {}).get(metric) or {} for e in sweep["efforts"]]
    return out


def panel(sweep: dict, source: str, metric: str, title: str, ylabel: str,
          x0: float, y0: float, w: float, h: float, small: bool) -> list:
    """SVG elements for one chart panel whose outer box is (x0, y0, w, h)."""
    ml, mr, mt, mb = (52, 12, 26, 40) if small else (64, 16, 36, 48)
    px0, py0 = x0 + ml, y0 + mt
    pw, ph = w - ml - mr, h - mt - mb
    data = series_for(sweep, source, metric)
    vals = [v for pts in data.values() for p in pts for v in (p.get("min"), p.get("max"), p.get("mean"))
            if isinstance(v, (int, float))]
    if metric in UNIT_RANGE:
        lo, hi = 0.0, 1.0
    elif vals:
        lo, hi = min(0.0, min(vals)), max(vals)
    else:
        lo, hi = 0.0, 1.0
    ticks = nice_ticks(lo, hi, 4 if small else 5)
    lo, hi = ticks[0], ticks[-1]

    def ys(v):
        return py0 + ph - (v - lo) / (hi - lo) * ph

    efforts = sweep["efforts"]
    n = len(efforts)

    def xs(k):
        return px0 + pw * (k + 0.5) / n

    fs = 11 if small else 12
    el = [f'<text x="{x0 + w / 2:.1f}" y="{y0 + (16 if small else 22):.1f}" text-anchor="middle" '
          f'font-size="{13 if small else 16}" font-weight="600">{escape(title)}</text>']
    for t in ticks:
        y = ys(t)
        el.append(f'<line class="grid" x1="{px0:.1f}" y1="{y:.1f}" x2="{px0 + pw:.1f}" y2="{y:.1f}"/>')
        el.append(f'<text class="muted" x="{px0 - 6:.1f}" y="{y + 4:.1f}" text-anchor="end" font-size="{fs}">{fmt(t)}</text>')
    el.append(f'<path class="axis" d="M{px0:.1f},{py0:.1f}V{py0 + ph:.1f}H{px0 + pw:.1f}"/>')
    for k, e in enumerate(efforts):
        el.append(f'<text x="{xs(k):.1f}" y="{py0 + ph + 16:.1f}" text-anchor="middle" font-size="{fs}">{escape(e)}</text>')
    el.append(f'<text class="muted" x="{px0 + pw / 2:.1f}" y="{py0 + ph + 32:.1f}" text-anchor="middle" '
              f'font-size="{fs}">effort</text>')
    cy = py0 + ph / 2
    el.append(f'<text class="muted" x="{x0 + 14:.1f}" y="{cy:.1f}" text-anchor="middle" font-size="{fs}" '
              f'transform="rotate(-90 {x0 + 14:.1f} {cy:.1f})">{escape(ylabel)}</text>')

    ng = len(sweep["generators"])
    dodge = (pw / n) * 0.06
    for i, g in enumerate(sweep["generators"]):
        off = (i - (ng - 1) / 2) * dodge
        pts = []
        for k, p in enumerate(data[g]):
            if not isinstance(p.get("mean"), (int, float)):
                pts.append(None)
                continue
            x = xs(k) + off
            if isinstance(p.get("min"), (int, float)) and isinstance(p.get("max"), (int, float)) and p["min"] != p["max"]:
                el.append(f'<line class="whisker s{i}" fill="none" x1="{x:.1f}" y1="{ys(p["min"]):.1f}" '
                          f'x2="{x:.1f}" y2="{ys(p["max"]):.1f}"/>')
            pts.append((x, ys(p["mean"])))
        runs, cur = [], []
        for pt in pts + [None]:
            if pt is None:
                if len(cur) > 1:
                    runs.append(cur)
                cur = []
            else:
                cur.append(pt)
        for r in runs:
            d = "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in r)
            el.append(f'<path class="line s{i}" fill="none" d="{d}"/>')
        for pt in pts:
            if pt:
                el.append(marker(i, pt[0], pt[1], 3.5 if small else 4.5))
    if not vals:
        el.append(f'<text class="muted" x="{px0 + pw / 2:.1f}" y="{cy:.1f}" text-anchor="middle" '
                  f'font-size="{fs}">no scored data yet</text>')
    return el


def legend(sweep: dict, x: float, y: float, horizontal: bool) -> list:
    el = []
    models = sweep.get("generator_models", {})
    for i, g in enumerate(sweep["generators"]):
        lx, ly = (x + i * 150, y) if horizontal else (x, y + i * 34)
        el.append(f'<path class="line s{i}" fill="none" d="M{lx:.1f},{ly:.1f}H{lx + 24:.1f}"/>')
        el.append(marker(i, lx + 12, ly))
        el.append(f'<text x="{lx + 30:.1f}" y="{ly + 4:.1f}" font-size="12">{escape(g)}</text>')
        if not horizontal and models.get(g) and models[g] != g:
            el.append(f'<text class="muted" x="{lx + 30:.1f}" y="{ly + 16:.1f}" font-size="9">{escape(models[g])}</text>')
    return el


def n_range(sweep: dict, source: str, metrics: list) -> str:
    """Real number of cases behind the plotted points, e.g. '7-9' or '9'."""
    ns = []
    for metric in metrics:
        for pts in series_for(sweep, source, metric).values():
            ns += [p.get("n") for p in pts if isinstance(p.get("mean"), (int, float))
                   and isinstance(p.get("n"), int)]
    if not ns:
        return ""
    lo, hi = min(ns), max(ns)
    return str(lo) if lo == hi else f"{lo}-{hi}"


def caption(sweep: dict, source: str, metrics: list) -> list:
    """Two caption lines: the statistic shown, then the judge resolution status."""
    unresolved = sweep.get("unresolved", {})
    if source == "resolved":
        status = (f"{' + '.join(sweep.get('judges', []))}, per item agreed or operator tiebreak; "
                  f"{unresolved.get('total', 0)} unresolved item(s) use the two-judge mean")
    else:
        status = f"single judge {source}, unresolved by a second judge"
    n = n_range(sweep, source, metrics)
    if n:
        stat = (f"Points: mean over n = {n} cases per point "
                f"(of {sweep.get('n_cases', 0)} in the suite); whiskers: min-max.")
    else:
        stat = "No scored points yet."
    return [stat,
            f"Judge resolution: {status}."]


def caption_el(sweep: dict, source: str, y: float, metrics: list) -> list:
    return [f'<text class="muted" x="16" y="{y + 15 * k:.0f}" font-size="11">{escape(line)}</text>'
            for k, line in enumerate(caption(sweep, source, metrics))]


def svg_doc(w: float, h: float, title: str, body: list) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{escape(title, {chr(34): "&quot;"})}">\n'
        f"<title>{escape(title)}</title>\n"
        + style_block() + "\n"
        + f'<rect class="bg" x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>\n'
        + "\n".join(body) + "\n</svg>\n"
    )


def metric_svg(sweep: dict, source: str, metric: str, title: str, ylabel: str) -> str:
    w, h = 760, 440
    body = panel(sweep, source, metric, title, ylabel, 0, 0, 590, 390, small=False)
    body += legend(sweep, 600, 60, horizontal=False)
    body += caption_el(sweep, source, h - 30, [metric])
    return svg_doc(w, h, f"{title} by effort and generator", body)


def overview_svg(sweep: dict, source: str) -> str:
    pw, ph, cols = 330, 240, 3
    w, h = pw * cols, 2 * ph + 80
    body = []
    for k, (metric, title, ylabel) in enumerate(METRICS[:6]):
        r, c = divmod(k, cols)
        body += panel(sweep, source, metric, title, ylabel, c * pw, r * ph, pw, ph, small=True)
    body += legend(sweep, 40, 2 * ph + 22, horizontal=True)
    body += caption_el(sweep, source, h - 30, [m for m, _, _ in METRICS[:6]])
    return svg_doc(w, h, "Model-effort sweep overview", body)


def write_plots(sweep: dict, out_dir: Path, source: str = "resolved") -> list:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for metric, title, ylabel in METRICS:
        p = out_dir / f"{metric}.svg"
        p.write_text(metric_svg(sweep, source, metric, title, ylabel), encoding="utf-8")
        written.append(p)
    p = out_dir / "overview.svg"
    p.write_text(overview_svg(sweep, source), encoding="utf-8")
    written.append(p)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=HERE)
    ap.add_argument("--source", default="resolved", help="'resolved' or a judge name")
    args = ap.parse_args(argv)
    sweep_path = Path(args.root) / "results" / "sweep.json"
    if not sweep_path.exists():
        print(f"error: {sweep_path} not found; run score.py first", file=sys.stderr)
        return 2
    sweep = json.loads(sweep_path.read_text(encoding="utf-8"))
    if args.source not in sweep.get("aggregate", {}):
        print(f"error: source {args.source!r} not in sweep.json aggregate "
              f"({sorted(sweep.get('aggregate', {}))})", file=sys.stderr)
        return 2
    for p in write_plots(sweep, Path(args.root) / "results" / "plots", args.source):
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
