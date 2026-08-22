"""Generate vector figures for the TriageLoop technical monograph.

The script reads only versioned machine-readable evaluation artifacts. Every
quantitative panel is labelled as synthetic/simulated evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = colors.HexColor("#261F2B")
MUTED = colors.HexColor("#665E6B")
LINE = colors.HexColor("#DDD7E0")
PAPER = colors.HexColor("#FBF9FB")
BRAND = colors.HexColor("#8B2463")
BRAND_SOFT = colors.HexColor("#F5E7F0")
CRITICAL = colors.HexColor("#B63A2B")
CRITICAL_SOFT = colors.HexColor("#F9E8E4")
WARNING = colors.HexColor("#C67A13")
SAFE = colors.HexColor("#287B5B")
INFO = colors.HexColor("#276DA7")
WHITE = colors.white


def load(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / "evaluation" / name).read_text(encoding="utf-8"))


def label(c: Canvas, x: float, y: float, text: str, size: float = 8, color=INK, font="Helvetica") -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def centered(c: Canvas, x: float, y: float, text: str, size: float = 8, color=INK, font="Helvetica") -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x, y, text)


def title(c: Canvas, text: str, subtitle: str, width: float) -> None:
    label(c, 34, 346, text, 15, INK, "Helvetica-Bold")
    label(c, 34, 329, subtitle, 8.2, MUTED)
    c.setStrokeColor(LINE)
    c.line(34, 318, width - 34, 318)


def rounded(c: Canvas, x: float, y: float, w: float, h: float, fill, stroke=LINE, radius: float = 7) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def wrap(c: Canvas, text: str, x: float, y: float, width: float, size: float = 8, leading: float = 10, color=INK, bold_first=False) -> float:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if stringWidth(test, "Helvetica", size) <= width or not current:
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for i, line in enumerate(lines):
        label(c, x, y - i * leading, line, size, color, "Helvetica-Bold" if bold_first and i == 0 else "Helvetica")
    return y - len(lines) * leading


def arrow(c: Canvas, x1: float, y1: float, x2: float, y2: float, color=BRAND, width: float = 1.4) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    d = 6
    c.line(x2, y2, x2 - d * math.cos(a - 0.55), y2 - d * math.sin(a - 0.55))
    c.line(x2, y2, x2 - d * math.cos(a + 0.55), y2 - d * math.sin(a + 0.55))


def architecture() -> None:
    w, h = 820, 380
    c = Canvas(str(OUT / "system_architecture.pdf"), pagesize=(w, h))
    c.setFillColor(WHITE); c.rect(0, 0, w, h, fill=1, stroke=0)
    title(c, "TriageLoop end-to-end safety architecture", "Patient need becomes time; time is tested against capacity; a clinician closes the loop.", w)
    lane_y = [244, 166, 88]
    lane_titles = ["CLINICAL STATE", "DECISION INTELLIGENCE", "OPERATIONS + ACCOUNTABILITY"]
    for y, lt in zip(lane_y, lane_titles):
        label(c, 34, y + 22, lt, 7.2, MUTED, "Helvetica-Bold")
        c.setStrokeColor(LINE); c.line(34, y + 14, w - 34, y + 14)

    boxes = [
        (44, 215, 118, 40, "Repeated observations", "vitals / cues / history", INFO),
        (183, 215, 118, 40, "Quality + provenance", "freshness / reliability", INFO),
        (322, 215, 118, 40, "Age-aware rules", "hard red flags first", CRITICAL),
        (461, 215, 118, 40, "Trajectory risk", "5 / 15 / 30 / 60 min", BRAND),
        (600, 215, 118, 40, "Conformal + OOD", "uncertainty shell", WARNING),
        (92, 137, 136, 40, "Dynamic Action Window", "earliest conservative bound", BRAND),
        (276, 137, 136, 40, "Queue Twin ETA", "site · load · resources", INFO),
        (460, 137, 136, 40, "Clinical Slack", "window minus projected ETA", CRITICAL),
        (644, 137, 126, 40, "Next observation", "first step only", WARNING),
        (122, 59, 150, 40, "Deadline Board", "one consolidated signal", BRAND),
        (335, 59, 150, 40, "Clinician decision", "accept / modify / override", SAFE),
        (548, 59, 150, 40, "Hash-linked audit", "reason / versions / lineage", INK),
    ]
    for x, y, bw, bh, heading, sub, accent in boxes:
        rounded(c, x, y, bw, bh, PAPER)
        c.setFillColor(accent); c.rect(x, y, 4, bh, fill=1, stroke=0)
        label(c, x + 12, y + 24, heading, 8.2, INK, "Helvetica-Bold")
        label(c, x + 12, y + 10, sub, 6.8, MUTED)
    for a, b in [((162,235),(183,235)),((301,235),(322,235)),((440,235),(461,235)),((579,235),(600,235)),((659,215),(160,177)),((228,157),(276,157)),((412,157),(460,157)),((596,157),(644,157)),((160,137),(197,99)),((707,137),(410,99)),((272,79),(335,79)),((485,79),(548,79))]:
        arrow(c, *a, *b)
    rounded(c, 728, 206, 58, 58, CRITICAL_SOFT, CRITICAL)
    centered(c, 757, 242, "FAIL", 8, CRITICAL, "Helvetica-Bold")
    centered(c, 757, 228, "SAFE", 8, CRITICAL, "Helvetica-Bold")
    centered(c, 757, 213, "not open", 6.5, MUTED)
    arrow(c, 718, 235, 728, 235, CRITICAL)
    label(c, 34, 21, "Safety invariants: rules cannot be suppressed / no autonomous downgrade / feasibility never changes need / audit failure blocks state change", 7.5, MUTED)
    c.save()


def runtime_pipeline() -> None:
    """Render the online decision path as a readable portrait flowchart."""
    w, h = 560, 760
    c = Canvas(str(OUT / "runtime_pipeline.pdf"), pagesize=(w, h))
    c.setFillColor(WHITE); c.rect(0, 0, w, h, fill=1, stroke=0)
    label(c, 30, 718, "Runtime clinical-decision pipeline", 16, INK, "Helvetica-Bold")
    label(c, 30, 698, "Every update recomputes need first, then tests queue feasibility; the clinician owns the action.", 8.4, MUTED)
    c.setStrokeColor(LINE); c.line(30, 686, w - 30, 686)

    def box(x: float, y: float, bw: float, bh: float, head: str, body: str, accent=BRAND, fill=PAPER) -> None:
        rounded(c, x, y, bw, bh, fill, LINE, 8)
        c.setFillColor(accent); c.rect(x, y, 5, bh, fill=1, stroke=0)
        label(c, x + 16, y + bh - 19, head, 9.2, INK, "Helvetica-Bold")
        wrap(c, body, x + 16, y + bh - 35, bw - 30, 7.2, 9, MUTED)

    box(130, 620, 300, 48, "1. Event trigger", "arrival / new observation / wait threshold / capacity change", INFO)
    box(130, 548, 300, 48, "2. Contract, provenance and quality", "freshness, completeness, reliability, plausibility and synthetic-only boundary", INFO)
    box(34, 458, 225, 62, "3A. Age-aware safety gate", "deterministic hard red flags and category limits; rules cannot be suppressed", CRITICAL, CRITICAL_SOFT)
    box(301, 458, 225, 62, "3B. Trajectory-risk engine", "calibrated 5 / 15 / 30 / 60-minute hazards from repeated observations", BRAND, BRAND_SOFT)
    box(130, 374, 300, 56, "4. Uncertainty safety shell", "Mondrian conformal set + OOD checks; uncertainty invokes review or Safe Mode", WARNING)
    box(130, 294, 300, 52, "5. Dynamic Action Window", "earliest conservative bound = min(rule, category, model, Safe Mode)", BRAND, BRAND_SOFT)
    box(130, 214, 300, 52, "6. Queue Twin and Clinical Slack", "project action ETA; Slack = Action Window - ETA; negative Slack is a capacity conflict", CRITICAL)
    box(130, 134, 300, 52, "7. Deadline Board + clinician decision", "one consolidated signal; accept / modify / override with a documented reason", SAFE)
    box(130, 54, 300, 52, "8. Hash-linked audit and continuous loop", "recommendation, versions, action, reason and lineage are recomputed and preserved", INK)

    for y1, y2 in [(620, 596), (548, 520), (458, 430), (374, 346), (294, 266), (214, 186), (134, 106)]:
        arrow(c, 280, y1, 280, y2)
    arrow(c, 280, 548, 146, 520)
    arrow(c, 280, 548, 414, 520)
    arrow(c, 146, 458, 225, 430)
    arrow(c, 414, 458, 335, 430)

    rounded(c, 448, 350, 104, 56, CRITICAL_SOFT, CRITICAL)
    centered(c, 500, 383, "SAFE MODE", 8, CRITICAL, "Helvetica-Bold")
    centered(c, 500, 369, "preserve or raise", 6.8, MUTED)
    arrow(c, 430, 402, 448, 382, CRITICAL)
    rounded(c, 448, 214, 104, 52, PAPER, WARNING)
    centered(c, 500, 244, "ETA UNKNOWN", 8, WARNING, "Helvetica-Bold")
    centered(c, 500, 230, "need stays visible", 6.8, MUTED)
    arrow(c, 430, 240, 448, 240, WARNING)
    rounded(c, 448, 54, 104, 52, CRITICAL_SOFT, CRITICAL)
    centered(c, 500, 84, "AUDIT FAIL", 8, CRITICAL, "Helvetica-Bold")
    centered(c, 500, 70, "block state change", 6.8, MUTED)
    arrow(c, 430, 80, 448, 80, CRITICAL)

    c.setStrokeColor(BRAND); c.setLineWidth(1.4)
    c.line(130, 80, 18, 80); c.line(18, 80, 18, 644); c.line(18, 644, 130, 644)
    arrow(c, 18, 644, 130, 644)
    label(c, 25, 325, "continuous", 6.5, BRAND, "Helvetica-Bold")
    label(c, 29, 315, "monitoring", 6.5, BRAND, "Helvetica-Bold")
    label(c, 30, 19, "NON-NEGOTIABLE: no autonomous downgrade, diagnosis, treatment or discharge.", 7.5, CRITICAL, "Helvetica-Bold")
    c.save()


def ml_pipeline() -> None:
    w, h = 820, 380
    c = Canvas(str(OUT / "ml_pipeline.pdf"), pagesize=(w, h))
    c.setFillColor(WHITE); c.rect(0, 0, w, h, fill=1, stroke=0)
    title(c, "Trajectory-risk development and safety pipeline", "All development evidence is synthetic unless explicitly labelled as external input plausibility.", w)
    steps = [
        ("1", "Seeded longitudinal generator", "10,000 encounters / 30,020 snapshots\nage, history and deterioration stressors"),
        ("2", "Patient-level isolation", "60% development / 20% validation\n20% test + separate stress cohort"),
        ("3", "Causal feature cut", "44 features available at prediction time\nworkflow-proxy observation count removed"),
        ("4", "Candidate hazards", "L2 logistic benchmark\ncompact boosted-stump challenger"),
        ("5", "Calibration + operating point", "Platt calibration / 5:1/10:1/20:1 cost\nthresholds chosen on validation only"),
        ("6", "Safety shell", "Mondrian conformal sets / OOD detector\ncritical coverage + review burden"),
        ("7", "Action Window", "min(rule, category, risk horizon)\nSafe Mode when reliability fails"),
    ]
    x0, gap, bw, bh = 34, 10, 99, 146
    for i, (num, head, body) in enumerate(steps):
        x = x0 + i * (bw + gap)
        rounded(c, x, 138, bw, bh, PAPER)
        c.setFillColor(BRAND); c.circle(x + 18, 265, 10, fill=1, stroke=0)
        centered(c, x + 18, 262, num, 8, WHITE, "Helvetica-Bold")
        wrap(c, head, x + 10, 239, bw - 20, 8, 10, INK, True)
        wrap(c, body.replace("\n", " "), x + 10, 191, bw - 20, 7, 9, MUTED)
        if i < len(steps) - 1:
            arrow(c, x + bw + 1, 211, x + bw + gap - 1, 211)
    rounded(c, 49, 57, 722, 46, BRAND_SOFT, BRAND)
    label(c, 64, 85, "Selection rule", 8, BRAND, "Helvetica-Bold")
    label(c, 140, 85, "Boosted model selected because it passed every registered safety gate; logistic retained as transparent fallback.", 8, INK)
    label(c, 64, 68, "Release rule", 8, BRAND, "Helvetica-Bold")
    label(c, 140, 68, "A probability may shorten an Action Window; it cannot lengthen a rule/category bound or independently downgrade a patient.", 8, INK)
    c.save()


def bar_chart(c: Canvas, x: float, y: float, w: float, h: float, labels: list[str], series: list[tuple[str, list[float], object]], ymax: float, suffix="") -> None:
    c.setStrokeColor(LINE); c.setLineWidth(0.7)
    for tick in range(5):
        val = ymax * tick / 4
        yy = y + h * tick / 4
        c.line(x, yy, x + w, yy)
        label(c, x - 27, yy - 3, f"{val:.2f}{suffix}", 6.5, MUTED)
    n, m = len(labels), len(series)
    group = w / n
    bw = min(24, group * 0.65 / m)
    for i, lab in enumerate(labels):
        center_x = x + (i + 0.5) * group
        centered(c, center_x, y - 14, lab, 7, MUTED)
        for j, (_, vals, col) in enumerate(series):
            xx = center_x - (m * bw + (m - 1) * 3) / 2 + j * (bw + 3)
            bh = max(0, vals[i] / ymax * h)
            c.setFillColor(col); c.rect(xx, y, bw, bh, fill=1, stroke=0)
    lx = x
    for name, _, col in series:
        c.setFillColor(col); c.rect(lx, y + h + 14, 9, 9, fill=1, stroke=0)
        label(c, lx + 14, y + h + 15, name, 7, INK)
        lx += 14 + stringWidth(name, "Helvetica", 7) + 18


def model_results() -> None:
    d = load("tl-02-metrics.json")["candidates"]["boosted"]
    horizons = ["5 min", "15 min", "30 min", "60 min"]
    test = d["test"]; stress = d["stress"]
    recall_test = [test[str(h)]["recall"] for h in (5,15,30,60)]
    recall_stress = [stress[str(h)]["recall"] for h in (5,15,30,60)]
    ece_test = [test[str(h)]["ece"] for h in (5,15,30,60)]
    ece_stress = [stress[str(h)]["ece"] for h in (5,15,30,60)]
    w,h=820,380; c=Canvas(str(OUT/"model_results.pdf"),pagesize=(w,h)); c.setFillColor(WHITE);c.rect(0,0,w,h,fill=1,stroke=0)
    title(c,"Selected-model performance across time horizons","Synthetic untouched test and deliberately shifted stress cohorts; recall is prioritised over average discrimination.",w)
    label(c,45,292,"Critical-case recall",9,INK,"Helvetica-Bold")
    bar_chart(c,70,65,300,200,horizons,[("Test",recall_test,BRAND),("Stress",recall_stress,WARNING)],1.0)
    label(c,445,292,"Expected calibration error",9,INK,"Helvetica-Bold")
    bar_chart(c,470,65,300,200,horizons,[("Test",ece_test,INFO),("Stress",ece_stress,CRITICAL)],0.30)
    label(c,45,31,"Gate: test recall ≥0.90; stress recall ≥0.85. Stress calibration degrades materially, motivating OOD + Safe Mode.",7.5,MUTED)
    c.save()


def queue_results() -> None:
    d=load("tl-05-periodic-retriage-metrics.json")
    sites=["Community","Regional","Urban/trauma","Overall"]
    keys=["community","regional","urban_trauma"]
    periodic=[]; triage=[]
    for k in keys:
        comp=d["paired_comparisons"][f"{k}|surge_3x|action_window_miss_rate"]
        periodic.append(comp["static_mean"]); triage.append(comp["triageloop_mean"])
    periodic.append(d["overall_surge"]["action_window_miss_rate"]["static_mean"]); triage.append(d["overall_surge"]["action_window_miss_rate"]["triageloop_mean"])
    w,h=820,380;c=Canvas(str(OUT/"queue_results.pdf"),pagesize=(w,h));c.setFillColor(WHITE);c.rect(0,0,w,h,fill=1,stroke=0)
    title(c,"Action Window misses under simulated 3× surge","Paired comparison against fixed 15-minute periodic re-triage; 1,200 policy shifts across three site profiles.",w)
    bar_chart(c,86,73,650,205,sites,[("Periodic re-triage",periodic,MUTED),("TriageLoop",triage,BRAND)],0.32)
    rounded(c,570,245,164,46,BRAND_SOFT,BRAND);centered(c,652,272,"20.5% fewer misses overall",10,BRAND,"Helvetica-Bold");centered(c,652,256,"95% CI 17.4%-23.8%",7,MUTED)
    label(c,86,36,"Interpretation: positive synthetic operational evidence, not a patient-outcome or staffing claim. Community remains unsafe in absolute terms.",7.5,MUTED)
    c.save()


def sensitivity() -> None:
    d=load("tl-05-periodic-retriage-metrics.json")["deterioration_response_sensitivity"]
    xs=[10,20,30]; vals=[100*d[str(x)]["relative_improvement"] for x in xs]; lows=[100*d[str(x)]["ci95_low"] for x in xs]; highs=[100*d[str(x)]["ci95_high"] for x in xs]
    w,h=820,380;c=Canvas(str(OUT/"response_sensitivity.pdf"),pagesize=(w,h));c.setFillColor(WHITE);c.rect(0,0,w,h,fill=1,stroke=0)
    title(c,"Response-definition sensitivity","Post-verification robustness analysis against periodic re-triage; not a retroactively registered gate.",w)
    x,y,cw,ch=100,70,620,210
    c.setStrokeColor(LINE)
    for t in range(0,31,5):
        yy=y+ch*t/30;c.line(x,yy,x+cw,yy);label(c,x-35,yy-3,f"{t}%",7,MUTED)
    c.setStrokeColor(CRITICAL);c.setDash(4,3);c.line(x,y+ch*20/30,x+cw,y+ch*20/30);c.setDash();label(c,x+cw-87,y+ch*20/30+5,"20% reference",7,CRITICAL)
    for i,(minute,val,lo,hi) in enumerate(zip(xs,vals,lows,highs)):
        xx=x+(i+0.5)*cw/3; yy=y+ch*val/30
        c.setStrokeColor(BRAND);c.setLineWidth(2);c.line(xx,y+ch*lo/30,xx,y+ch*hi/30);c.line(xx-7,y+ch*lo/30,xx+7,y+ch*lo/30);c.line(xx-7,y+ch*hi/30,xx+7,y+ch*hi/30)
        c.setFillColor(BRAND);c.circle(xx,yy,6,fill=1,stroke=0);centered(c,xx,yy+14,f"{val:.1f}%",9,BRAND,"Helvetica-Bold");centered(c,xx,y-16,f"{minute}-minute response",8,MUTED)
    label(c,100,35,"All paired intervals remain positive; only the 30-minute definition exceeds 20%. This dependence is reported, not hidden.",7.5,MUTED)
    c.save()


def nbo_tradeoff() -> None:
    d=load("tl-05-nbo-metrics.json")
    w,h=820,380;c=Canvas(str(OUT/"nbo_tradeoff.pdf"),pagesize=(w,h));c.setFillColor(WHITE);c.rect(0,0,w,h,fill=1,stroke=0)
    title(c,"Next Best Observation: efficiency hypothesis rejected","Counterfactual on 4,317 eligible synthetic snapshots; gate fixed before evaluation.",w)
    panels=[("Measurements requested",8,1,"87.5% fewer",True),("Estimated acquisition time",525,d["next_best_observation"]["mean_typical_seconds"],"91.1% lower",True),("Operational critical recall",100*d["fixed_bundle"]["operational_critical_recall"],100*d["next_best_observation"]["operational_critical_recall"],"-7.1 points",False)]
    for i,(head,a,b,note,lower) in enumerate(panels):
        x=42+i*258;rounded(c,x,98,224,188,PAPER)
        label(c,x+16,261,head,9,INK,"Helvetica-Bold")
        maxv=max(a,b)*1.15
        for j,(name,val,col) in enumerate([("Full bundle",a,MUTED),("One NBO",b,BRAND)]):
            bx=x+34+j*88;bh=112*val/maxv;c.setFillColor(col);c.rect(bx,126,48,bh,fill=1,stroke=0);centered(c,bx+24,112,name,7,MUTED);centered(c,bx+24,132+bh,f"{val:.1f}" if isinstance(val,float) else str(val),8,col,"Helvetica-Bold")
        centered(c,x+112,78,note,10,SAFE if lower else CRITICAL,"Helvetica-Bold")
    rounded(c,104,32,612,30,CRITICAL_SOFT,CRITICAL);centered(c,410,43,"Gate failed: NBO is released only as the first measurement suggestion; full reassessment or escalation remains mandatory.",8,CRITICAL,"Helvetica-Bold")
    c.save()


def review_cycle() -> None:
    w,h=820,380;c=Canvas(str(OUT/"review_cycle.pdf"),pagesize=(w,h));c.setFillColor(WHITE);c.rect(0,0,w,h,fill=1,stroke=0)
    title(c,"Independent review as an engineering control","Reviewer findings were verified against artifacts and code before adoption; critique was not treated as authority.",w)
    nodes=[(56,"Internal evidence lock","Predeclared gates, cards, traceability"),(223,"Claude review 1","14 findings; scientific and UX red team"),(390,"TL-04.5 disposition","Comparator, burden, prior art, failure states"),(557,"Claude review 2","9 release findings across six perspectives"),(680,"TL-06.5 disposition","8 resolved/disproved; Docker gate retained")]
    for i,(x,head,body) in enumerate(nodes):
        bw=125 if i<4 else 105;rounded(c,x,148,bw,94,BRAND_SOFT if i in (1,3) else PAPER,BRAND if i in (1,3) else LINE)
        wrap(c,head,x+10,220,bw-20,8,10,INK,True);wrap(c,body,x+10,181,bw-20,7,9,MUTED)
        if i<len(nodes)-1:
            nx=nodes[i+1][0];arrow(c,x+bw,195,nx-8,195)
    rounded(c,80,70,660,44,PAPER,LINE)
    label(c,96,96,"Material outcomes",8,INK,"Helvetica-Bold")
    label(c,182,96,"Stronger periodic comparator / alert burden / explanation fix / response sensitivity / six UI surfaces",7.5,MUTED)
    label(c,96,80,"Non-negotiable",8,INK,"Helvetica-Bold")
    label(c,182,80,"Negative NBO result and Community limitation remain visible; no clinical-validation or world-first claim.",7.5,MUTED)
    c.save()


if __name__ == "__main__":
    architecture()
    runtime_pipeline()
    ml_pipeline()
    model_results()
    queue_results()
    sensitivity()
    nbo_tradeoff()
    review_cycle()
    print(f"Generated figures in {OUT}")
