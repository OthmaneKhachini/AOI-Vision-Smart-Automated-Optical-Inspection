# ==========================================
# MEMBER 4: DATA, STATISTICS & REPORTS
# Name: Othmane
# Concept: Session State, Statistics, Charts, and Exports
# ==========================================

# ==========================================
# 1. SESSION STATE (Section 3 in web.py)
# ==========================================
S = st.session_state
_defaults = {
    "total": 0, "ok": 0, "defect": 0,
    "history": [], "yield_data": [], "recent": [], "times": [], "fails": [],
    "conf": 100, "last_snap": None,
    "started": datetime.now().strftime("%H:%M:%S"),
    "started_ts": time.time(),
}
for _k, _v in _defaults.items():
    if _k not in S:
        S[_k] = _v


# ==========================================
# 2. RESET DATA BUTTON (in Section 4 - Sidebar)
# ==========================================
if st.button(f"🗑️ {T['reset']}", **FIT):
    for k in ("history", "yield_data", "recent", "times", "fails"):
        S[k] = []
    S.total = S.ok = S.defect = 0
    S.conf = 100
    S.last_snap = None
    st.rerun()


# ==========================================
# 3. STATISTICS FUNCTIONS (Section 7)
# ==========================================
def stats():
    tot, ok, de = S.total, S.ok, S.defect
    y = (ok / tot * 100) if tot > 0 else 100.0
    dr = (de / tot * 100) if tot > 0 else 0.0
    avg = (sum(h["Defects"] for h in S.history) / de) if de > 0 else 0.0
    return tot, ok, de, y, dr, avg


def per_minute():
    d = {}
    for h in S.history:
        m = h["Time"][:5]
        d.setdefault(m, [0, 0])[0 if "PASS" in h["Status"] else 1] += 1
    keys = sorted(d)[-30:]
    return keys, [d[k][0] for k in keys], [d[k][1] for k in keys]


# ==========================================
# 4. CHART FUNCTIONS (Section 7)
# ==========================================
def dark_layout(fig, h=215):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#9aa7bb", size=11), height=h,
                      margin=dict(t=4, b=4, l=4, r=4))


def pie_fig(h=215):
    if S.total <= 0:
        return None
    fig = go.Figure(go.Pie(
        labels=[T["pass"], T["def"]], values=[S.ok, S.defect], hole=0.7, sort=False, textinfo="none",
        marker=dict(colors=["#3ddc84", "#ff5c5c"], line=dict(color="#0d131c", width=3)),
        domain=dict(x=[0, 1], y=[0.16, 1])))
    dark_layout(fig, h)
    fig.update_layout(
        legend=dict(orientation="h", x=0.5, xanchor="center", y=0, yanchor="bottom", font=dict(color="#c9d1d9", size=12)),
        annotations=[
            dict(text=f"<b>{S.total}</b>", x=0.5, y=0.63, showarrow=False, font=dict(size=28, color="#e6edf3")),
            dict(text=T["tot"], x=0.5, y=0.52, showarrow=False, font=dict(size=11, color="#7d8ba1")),
        ])
    return fig


def line_fig(h=215):
    if len(S.yield_data) < 2:
        return None
    y = S.yield_data
    fig = go.Figure(go.Scatter(
        x=list(range(1, len(y) + 1)), y=y, mode="lines",
        line=dict(color="#6366f1", width=2.6, shape="spline"),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.13)"))
    fig.add_hline(y=target, line=dict(color="#ffab2e", width=1.5, dash="dot"))
    dark_layout(fig, h)
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, color="#7d8ba1"),
        yaxis=dict(gridcolor="#1b2636", zeroline=False, color="#7d8ba1",
                   range=[max(0, min(min(y), target) - 10), 101], ticksuffix="%"))
    return fig


def bar_fig(h=215):
    keys, p, f = per_minute()
    if not keys:
        return None
    fig = go.Figure([
        go.Bar(x=keys, y=p, name=T["pass"], marker_color="#3ddc84"),
        go.Bar(x=keys, y=f, name=T["def"], marker_color="#ff5c5c"),
    ])
    dark_layout(fig, h)
    fig.update_layout(
        barmode="stack", bargap=0.35, margin=dict(t=28, b=4, l=4, r=4),
        legend=dict(orientation="h", x=1, xanchor="right", y=1.18, font=dict(color="#c9d1d9", size=12)),
        xaxis=dict(showgrid=False, color="#7d8ba1"),
        yaxis=dict(gridcolor="#1b2636", color="#7d8ba1"))
    return fig


def gauge_fig(h=175):
    _, _, _, y, _, _ = stats()
    good = y >= target
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=y,
        number=dict(suffix="%", valueformat=".1f", font=dict(size=34, color="#e6edf3")),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#7d8ba1", tickfont=dict(size=10, color="#7d8ba1")),
            bar=dict(color="#3ddc84" if good else "#ff5c5c", thickness=0.28),
            bgcolor="#111a26", borderwidth=0,
            steps=[dict(range=[0, target], color="rgba(255,92,92,.14)"),
                   dict(range=[target, 100], color="rgba(61,220,132,.12)")],
            threshold=dict(line=dict(color="#ffab2e", width=3), thickness=0.85, value=target))))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#9aa7bb"), height=h,
                      margin=dict(t=18, b=0, l=18, r=18))
    return fig


# ==========================================
# 5. UPDATE CHARTS FUNCTION (Section 8)
# ==========================================
def update_charts():
    cfg = {"displayModeBar": False}
    k = S.total

    fig = pie_fig()
    if fig is not None:
        pie_ui.plotly_chart(fig, config=cfg, **FIT, key=f"pie_{k}")
    else:
        pie_ui.markdown(f'<div class="empty">{T["no_data"]}</div>', unsafe_allow_html=True)

    fig = line_fig()
    if fig is not None:
        chart_ui.plotly_chart(fig, config=cfg, **FIT, key=f"line_{k}")
    else:
        chart_ui.markdown(f'<div class="empty">{T["no_chart"]}</div>', unsafe_allow_html=True)

    fig = bar_fig()
    if fig is not None:
        bar_ui.plotly_chart(fig, config=cfg, **FIT, key=f"bar_{k}")
    else:
        bar_ui.markdown(f'<div class="empty">{T["no_chart"]}</div>', unsafe_allow_html=True)

    gauge_ui.plotly_chart(gauge_fig(), config=cfg, **FIT, key=f"gauge_{k}")


# ==========================================
# 6. REPORT CSS AND EXPORT FUNCTIONS (Section 7)
# ==========================================
REPORT_CSS = (
    "*{box-sizing:border-box}body{margin:0;background:#070b12;color:#e6edf3;font-family:Inter,'Segoe UI',Arial,sans-serif}"
    ".wrap{max-width:1100px;margin:0 auto;padding:32px 24px}"
    "header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid #1b2636;padding-bottom:16px;margin-bottom:22px}"
    "h1{margin:0;font-size:26px}.sub{color:#7d8ba1;font-size:13px;margin-top:6px}"
    ".kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:22px}"
    ".k{background:#0d131c;border:1px solid #1b2636;border-radius:12px;padding:16px}"
    ".kv{font-size:30px;font-weight:700}.kl{color:#7d8ba1;font-size:12px;margin-top:4px}"
    ".grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}"
    ".card{background:#0d131c;border:1px solid #1b2636;border-radius:12px;padding:16px;margin-bottom:14px}"
    ".card h2{font-size:14px;margin:0 0 10px}"
    "table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #1b2636}"
    "th{color:#7d8ba1;font-weight:600}td.p{color:#3ddc84}td.f{color:#ff5c5c}"
    ".gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}"
    "figure{margin:0;background:#111a26;border:1px solid rgba(255,92,92,.5);border-radius:10px;overflow:hidden}"
    "figure img{width:100%;display:block}figcaption{padding:8px 10px;font-size:12px;display:flex;flex-direction:column;gap:2px}"
    "figcaption span{color:#7d8ba1}"
    ".empty{color:#7d8ba1;padding:20px;text-align:center;border:1px dashed #1b2636;border-radius:10px}"
    "@media print{body{-webkit-print-color-adjust:exact;print-color-adjust:exact}.card,figure{break-inside:avoid}}"
    "@media(max-width:700px){.grid{grid-template-columns:1fr}}"
)


def build_report_html(full=True):
    tot, ok, de, y, dr, avg = stats()

    def fh(fig):
        if fig is None:
            return f'<div class="empty">{T["no_chart"]}</div>'
        return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})

    kp = "".join(
        f'<div class="k"><div class="kv" style="color:{c}">{v}</div><div class="kl">{lbl}</div></div>'
        for v, lbl, c in [
            (tot, T["tot"], "#e6edf3"), (ok, T["pass"], "#3ddc84"), (de, T["def"], "#ff5c5c"),
            (f"{y:.1f}%", T["yield"], "#8b8cf8"), (f"{dr:.1f}%", T["def_rate"], "#ffab2e"),
        ])

    body = (
        f'<header><div><h1>🏭 {T["title"]}</h1><div class="sub">AOI Vision · {T["reports"]}</div></div>'
        f'<div class="sub">{T["generated"]}: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div></header>'
        f'<div class="kpis">{kp}</div>'
        f'<div class="grid"><div class="card"><h2>🥧 {T["pie"]}</h2>{fh(pie_fig(240))}</div>'
        f'<div class="card"><h2>📈 {T["chart"]}</h2>{fh(line_fig(240))}</div></div>'
        f'<div class="card"><h2>📊 {T["per_min"]}</h2>{fh(bar_fig(260))}</div>'
    )

    if full:
        rows = "".join(
            f'<tr><td>{h["Time"]}</td><td>{h.get("Part", "-")}</td>'
            f'<td class="{"p" if "PASS" in h["Status"] else "f"}">{h["Status"]}</td><td>{h["Defects"]}</td></tr>'
            for h in S.history)
        body += (f'<div class="card"><h2>📋 {T["log"]}</h2><table><thead><tr><th>{T["col_time"]}</th><th>{T["col_part"]}</th>'
                 f'<th>{T["col_status"]}</th><th>{T["col_def"]}</th></tr></thead><tbody>{rows}</tbody></table></div>')
        if S.fails:
            cards = "".join(
                f'<figure><img src="data:image/jpeg;base64,{base64.b64encode(fr["jpg"]).decode()}"/>'
                f'<figcaption><b>{fr["part"]}</b><span>{fr["time"]} · {fr["defects"]} {T["def"]}</span></figcaption></figure>'
                for fr in S.fails[:30])
            body += f'<div class="card"><h2>❌ {T["gallery"]}</h2><div class="gal">{cards}</div></div>'

    return ('<!doctype html><html><head><meta charset="utf-8"><title>AOI Report</title>'
            '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'
            f'<style>{REPORT_CSS}</style></head><body><div class="wrap">{body}</div></body></html>')


def fails_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fr in S.fails:
            z.writestr(f'{fr["part"]}_{fr["time"].replace(":", "-")}_{fr["defects"]}defects.jpg', fr["jpg"])
    return buf.getvalue()


def dl(label, data, name, mime, key, disabled=False):
    kw = dict(file_name=name, mime=mime, key=key, disabled=disabled, **FIT)
    try:
        st.download_button(label, data, on_click="ignore", **kw)
    except TypeError:
        st.download_button(label, data, **kw)


def render_reports():
    cols = ["Time", "Part", "Status", "Defects"]
    has = len(S.history) > 0
    has_fail = len(S.fails) > 0
    df = pd.DataFrame(S.history, columns=cols)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    k = S.total

    csv_all = df.to_csv(index=False).encode("utf-8-sig")
    csv_pass = df[df["Status"].str.contains("PASS")].to_csv(index=False).encode("utf-8-sig")
    csv_fail = df[df["Status"].str.contains("FAIL")].to_csv(index=False).encode("utf-8-sig")
    html_charts = build_report_html(full=False).encode("utf-8") if has else b""
    html_full = build_report_html(full=True).encode("utf-8") if has else b""
    zip_bytes = fails_zip() if has_fail else b""

    with reports_ui.container():
        a = st.columns(3)
        with a[0]:
            dl(f"📄 {T['r_all']}", csv_all, f"aoi_all_{stamp}.csv", "text/csv", f"dl_all_{k}", not has)
        with a[1]:
            dl(f"✅ {T['r_pass']}", csv_pass, f"aoi_passed_{stamp}.csv", "text/csv", f"dl_pass_{k}", S.ok == 0)
        with a[2]:
            dl(f"❌ {T['r_fail']}", csv_fail, f"aoi_failed_{stamp}.csv", "text/csv", f"dl_fail_{k}", S.defect == 0)
        b = st.columns(3)
        with b[0]:
            dl(f"📈 {T['r_charts']}", html_charts, f"aoi_charts_{stamp}.html", "text/html", f"dl_charts_{k}", not has)
        with b[1]:
            dl(f"📑 {T['r_full']}", html_full, f"aoi_report_{stamp}.html", "text/html", f"dl_full_{k}", not has)
        with b[2]:
            dl(f"🖼️ {T['r_zip']}", zip_bytes, f"aoi_failed_frames_{stamp}.zip", "application/zip", f"dl_zip_{k}", not has_fail)


# ==========================================
# 7. MAIN LOOP RECORDING BLOCK (Section 10)
# ==========================================
# This code goes inside the main loop when "DETECTED" is received from Arduino:

if "DETECTED" in line.upper():
    res, img, d_count, conf = inspect_image(frame, conf_th)
    S.total += 1
    now_time = datetime.now().strftime("%H:%M:%S")
    part = f"PRT-{S.total:05d}"
    passed = (res == "OK")

    if passed:
        S.ok += 1
        S.conf = conf
        S.history.insert(0, {"Time": now_time, "Part": part, "Status": "✅ PASS", "Defects": 0})
        set_status("ok", f"✅ {T['pass_msg']}")
    else:
        S.defect += 1
        S.conf = conf
        S.history.insert(0, {"Time": now_time, "Part": part, "Status": "❌ FAIL", "Defects": d_count})
        S.fails.insert(0, {"part": part, "time": now_time, "defects": d_count, "jpg": to_jpg(img, 800, 85)})
        S.fails = S.fails[:100]
        set_status("bad", f"❌ {T['fail_msg']} ({d_count})")

    S.recent.insert(0, {"part": part, "time": now_time, "ok": passed,
                        "defects": d_count, "img": to_b64(img, 200)})
    S.recent = S.recent[:12]
    S.last_snap = to_b64(img, 640)
    S.times.append(time.time())
    S.yield_data.append(S.ok / S.total * 100)

    update_dashboard()
    update_charts()
    render_thumbs()
    render_snap()
    render_recent()
    render_reports()

    if passed:
        toast(f"{part} · {T['pass_msg']}", "✅")
        beep(2000, 150)
    else:
        toast(f"{part} · {T['fail_msg']} ({d_count})", "❌")
        beep(400, 400)

    arduino.reset_input_buffer()
    time.sleep(1.5)

    S.conf = 100
    set_status("wait", f"⏳ {T['wait']}")
    update_dashboard()