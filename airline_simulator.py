import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from scipy.stats import binom

st.set_page_config(
    page_title="Airline Overbooking Optimizer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --blue:       #1e88e5;
    --blue-dark:  #1565c0;
    --blue-light: #e3f2fd;
    --navy:       #1e3a8a;
    --text:       #1e293b;
    --subtext:    #475569;
    --muted:      #94a3b8;
    --border:     #e2e8f0;
    --bg:         #f0f2f6;
    --card:       #ffffff;
    --red:        #ef4444;
    --green:      #22c55e;
    --amber:      #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* ── Header (teammate style) ── */
.header-container {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 28px;
    background: linear-gradient(90deg, #1e3a8a 0%, #1e88e5 100%);
    padding: 30px 36px;
    border-radius: 15px;
    color: white;
}
.header-text h1 {
    font-size: 30px; font-weight: 800;
    color: white !important; margin: 0 0 6px 0;
    letter-spacing: -0.02em;
}
.header-text p {
    font-size: 14px; opacity: 0.88; margin: 0; line-height: 1.5;
}

/* ── Metric blocks (teammate style — blue left border) ── */
/* Override Streamlit metric to match teammate's stMetric look */
[data-testid="stMetric"] {
    background: white !important;
    padding: 20px 18px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    border-left: 5px solid var(--blue) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important; font-weight: 600 !important;
    color: var(--subtext) !important; text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
    font-size: 28px !important; font-weight: 800 !important;
    color: var(--navy) !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stMetricDelta"] {
    font-size: 13px !important; font-weight: 600 !important;
}

/* ── Input panel card ── */
.panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.panel-title {
    font-size: 13px; font-weight: 700; color: var(--navy);
    margin-bottom: 16px;
    text-transform: uppercase; letter-spacing: 0.07em;
    border-bottom: 2px solid var(--blue-light);
    padding-bottom: 10px;
}

/* ── Recommendation banner ── */
.rec-banner {
    background: #eff6ff;
    border: 1.5px solid var(--blue);
    border-left: 5px solid var(--blue);
    border-radius: 10px; padding: 16px 20px; margin-bottom: 20px;
}
.rec-banner.amber {
    background: #fffbeb; border-color: var(--amber); border-left-color: var(--amber);
}
.rec-banner.green {
    background: #f0fdf4; border-color: var(--green); border-left-color: var(--green);
}
.rec-title { font-size: 15px; font-weight: 700; color: var(--navy); margin-bottom: 5px; }
.rec-body  { font-size: 13px; color: var(--subtext); line-height: 1.6; }

/* ── Section label ── */
.sec-lbl {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--muted); margin: 0 0 8px 0;
}

/* ── Alert boxes ── */
.alert-info { background:var(--blue-light); border:1px solid #90caf9; border-radius:8px; padding:10px 14px; font-size:12px; color:#1565c0; font-weight:600; margin-top:8px; }
.alert-warn { background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:10px 14px; font-size:12px; color:#92400e; font-weight:600; margin-top:8px; }

/* ── Bump breakdown rows ── */
.bump-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px; border-radius: 8px; margin: 4px 0;
    background: #f8fafc; font-size: 13px; font-weight: 500;
    border: 1px solid var(--border);
}

hr { border: none; border-top: 1px solid var(--border); margin: 18px 0; }

/* ── Run button ── */
div.stButton > button {
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important; font-size: 14px !important;
    padding: 10px 0 !important; transition: all 0.15s !important;
}
div.stButton > button[kind="primary"] {
    background: var(--blue) !important;
    border-color: var(--blue) !important; color: white !important;
}
div.stButton > button[kind="primary"]:hover {
    background: var(--blue-dark) !important;
    border-color: var(--blue-dark) !important;
}

/* ── Number inputs ── */
div[data-testid="stNumberInput"] input {
    background: white !important; border: 1.5px solid var(--border) !important;
    border-radius: 8px !important; color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important; font-weight: 500 !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(30,136,229,0.12) !important;
}
label {
    font-size: 12px !important; font-weight: 700 !important;
    color: var(--subtext) !important; letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
.stSlider > div > div > div { background: var(--blue) !important; }
.stProgress > div > div { background: var(--blue) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #f0f2f6;
    border-radius: 10px; padding: 4px; border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important; font-size: 13px !important;
    color: var(--subtext) !important; padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] { background: var(--blue) !important; color: white !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px !important; }
</style>
"""

# ── Simulation engine ─────────────────────────────────────────────────────────
def simulate(capacity, tickets_sold, ticket_price, voucher_cost, no_show_prob, n_sim, seed=None):
    if seed is not None:
        np.random.seed(seed)
    showed   = np.random.binomial(tickets_sold, 1 - no_show_prob, n_sim)
    bumped   = np.maximum(0, showed - capacity)
    revenues = tickets_sold * ticket_price - bumped * voucher_cost
    return {
        "revenues": revenues, "bumped": bumped, "showed": showed,
        "mean":     float(revenues.mean()),
        "std":      float(revenues.std()),
        "p5":       float(np.percentile(revenues, 5)),
        "p95":      float(np.percentile(revenues, 95)),
        "prob_bump":float((bumped > 0).mean()),
        "avg_bump": float(bumped.mean()),
        "max_bump": int(bumped.max()),
    }

def scan(capacity, ticket_price, voucher_cost, no_show_prob, n_sim, max_extra, seed=None):
    """Scan overbooking levels 0→max_extra using exact binomial math + MC."""
    p_show   = 1 - no_show_prob
    baseline = capacity * ticket_price
    rows = []
    for extra in range(0, max_extra + 1):
        sold     = capacity + extra
        # Exact expected profit via binomial
        k_range  = np.arange(capacity + 1, sold + 1)
        exp_bump = float(np.sum((k_range - capacity) * binom.pmf(k_range, sold, p_show)))
        exp_cost = exp_bump * voucher_cost
        exp_prof = sold * ticket_price - exp_cost
        prob_b   = float(1 - binom.cdf(capacity, sold, p_show))
        # MC for P5/P95
        r        = simulate(capacity, sold, ticket_price, voucher_cost, no_show_prob, n_sim, seed)
        rows.append({
            "Overbook By":      extra,
            "Tickets Sold":     sold,
            "Exact Exp. Profit":round(exp_prof, 2),
            "MC Mean Revenue":  round(r["mean"], 2),
            "Std Dev":          round(r["std"], 2),
            "P5 Revenue":       round(r["p5"], 2),
            "P95 Revenue":      round(r["p95"], 2),
            "Bump Prob (%)":    round(prob_b * 100, 1),
            "Avg Bumped":       round(exp_bump, 2),
            "vs Baseline ($)":  round(exp_prof - baseline, 2),
        })
    return pd.DataFrame(rows)


# ── App ───────────────────────────────────────────────────────────────────────
st.markdown(CSS, unsafe_allow_html=True)

# ── Header (teammate's gradient style) ───────────────────────────────────────
st.markdown("""
<div class="header-container">
    <div style="font-size:52px;line-height:1">✈️</div>
    <div class="header-text">
        <h1>Airline Overbooking Optimizer</h1>
        <p>A strategic tool for maximising yield through Monte Carlo simulation
        and Binomial probability modelling. Configure your flight parameters and
        find the revenue-optimal number of tickets to sell.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">✈️ Aircraft & Pricing</div>', unsafe_allow_html=True)
    capacity     = st.number_input("Seat Capacity",    min_value=1,   max_value=1000, value=100,  step=1)
    ticket_price = st.number_input("Ticket Price ($)", min_value=0.0, value=300.0,    step=10.0)
    voucher_cost = st.number_input("Voucher / Compensation Cost ($)", min_value=0.0, value=500.0, step=50.0,
                                   help="Amount given to each bumped passenger.")
    no_show_pct  = st.slider("No-Show Rate (%)", min_value=0, max_value=50, value=10, step=1)
    no_show_prob = no_show_pct / 100
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🎫 Tickets to Sell</div>', unsafe_allow_html=True)
    tickets_sold = st.number_input("Tickets Sold",
                                   min_value=int(capacity), max_value=int(capacity) + 100,
                                   value=int(capacity) + 10, step=1)
    overbook_by  = tickets_sold - capacity
    if overbook_by > 0:
        st.markdown(f'<div class="alert-info">Overbooking by <strong>{overbook_by}</strong> seats ({round(overbook_by/capacity*100,1)}% above capacity)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-info">Selling exactly at capacity — no overbooking.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">⚙️ Simulation Settings</div>', unsafe_allow_html=True)
    n_sim    = st.select_slider("Monte Carlo Iterations", options=[1000, 5000, 10000, 50000], value=10000)
    max_scan = st.slider("Optimizer Scan Range (0 → N extra seats)", min_value=5, max_value=50, value=20)
    use_seed = st.checkbox("Fix random seed (reproducible results)")
    seed_val = st.number_input("Seed", min_value=0, value=42, step=1, disabled=not use_seed)
    st.markdown('</div>', unsafe_allow_html=True)

    run = st.button("▶  Run Simulation", type="primary", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
with right:
    if not run and "res" not in st.session_state:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:420px;background:white;border:2px dashed #e2e8f0;border-radius:15px;">
            <div style="font-size:64px;margin-bottom:16px">✈️</div>
            <div style="font-size:20px;font-weight:800;color:#1e3a8a;margin-bottom:8px;
                        font-family:'Outfit',sans-serif">Ready for Analysis</div>
            <div style="font-size:14px;color:#64748b;text-align:center;
                        max-width:300px;line-height:1.6">
                Set your flight parameters on the left and click
                <strong>Run Simulation</strong>.</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        if run:
            seed = int(seed_val) if use_seed else None
            with st.spinner("Running simulation..."):
                res     = simulate(int(capacity), int(tickets_sold), float(ticket_price),
                                   float(voucher_cost), no_show_prob, int(n_sim), seed)
                scan_df = scan(int(capacity), float(ticket_price), float(voucher_cost),
                               no_show_prob, int(n_sim), int(max_scan), seed)
            st.session_state.res     = res
            st.session_state.scan_df = scan_df
            st.session_state.params  = dict(
                capacity=capacity, tickets_sold=tickets_sold, overbook_by=overbook_by,
                ticket_price=ticket_price, voucher_cost=voucher_cost,
                no_show_pct=no_show_pct, n_sim=n_sim,
            )

        res     = st.session_state.res
        scan_df = st.session_state.scan_df
        params  = st.session_state.params
        ob      = params["overbook_by"]

        best_row   = scan_df.loc[scan_df["Exact Exp. Profit"].idxmax()]
        best_extra = int(best_row["Overbook By"])
        best_profit = float(best_row["Exact Exp. Profit"])
        baseline    = params["capacity"] * params["ticket_price"]
        gain_vs_base = best_profit - baseline
        current_exact_profit = float(
            scan_df.loc[scan_df["Overbook By"] == ob, "Exact Exp. Profit"].values[0]
            if ob <= int(max_scan) else res["mean"]
        )
        gain_vs_current = best_profit - current_exact_profit

        # ── Recommendation banner ──
        if best_extra == ob:
            st.markdown(f"""
            <div class="rec-banner green">
                <div class="rec-title">✅ Your current setting is optimal</div>
                <div class="rec-body">Selling <strong>{int(params['tickets_sold'])}</strong> tickets
                (overbooking by <strong>{ob}</strong>) maximises expected profit at
                <strong>${current_exact_profit:,.0f}</strong> per flight.</div>
            </div>""", unsafe_allow_html=True)
        elif gain_vs_current > 0:
            st.markdown(f"""
            <div class="rec-banner">
                <div class="rec-title">💡 Recommended: Sell {int(best_row['Tickets Sold'])} tickets — overbook by {best_extra}</div>
                <div class="rec-body">Expected profit <strong>${best_profit:,.0f}</strong> per flight
                (<strong>+${gain_vs_current:,.0f}</strong> vs your current setting ·
                <strong>+${gain_vs_base:,.0f}</strong> vs no overbooking).
                Estimated bump probability: <strong>{float(best_row['Bump Prob (%)']):.1f}%</strong>,
                average <strong>{float(best_row['Avg Bumped']):.1f}</strong> bumped passengers.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="rec-banner amber">
                <div class="rec-title">⚠️ You may be over-overbooking</div>
                <div class="rec-body">The optimal level is <strong>{best_extra}</strong> extra tickets.
                At your current level, compensation costs are reducing profit below the optimum.</div>
            </div>""", unsafe_allow_html=True)

        # ── Key metrics — native st.metric with blue-border CSS ──
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Optimal Overbook",
            f"+{best_extra} seats",
            help="This many extra tickets maximises expected profit.",
        )
        c2.metric(
            "Expected Profit",
            f"${best_profit:,.0f}",
            delta=f"+${gain_vs_base:,.0f} vs base",
        )
        c3.metric(
            "Bump Probability",
            f"{float(best_row['Bump Prob (%)']):.1f}%",
            delta=f"at optimal level",
            delta_color="off",
        )
        c4.metric(
            "Avg Bumped Pax",
            f"{float(best_row['Avg Bumped']):.2f}",
            help="Expected number of bumped passengers at the optimal level.",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabs ──
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Revenue Distribution",
            "🔍 Optimizer",
            "👥 Bump Analysis",
            "📋 Full Table",
            "📖 Executive Summary",
        ])

        PLOT = dict(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Outfit", color="#475569", size=12),
            margin=dict(l=10, r=10, t=24, b=40),
        )
        GRID  = dict(showgrid=True, gridcolor="#f1f5f9")
        TICK  = dict(tickfont=dict(family="JetBrains Mono", size=11, color="#475569"))

        # ── Tab 1: Revenue Distribution ──────────────────────────────────────
        with tab1:
            ft = res["revenues"]
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=ft, nbinsx=55,
                marker=dict(color="#1e88e5", opacity=0.8, line=dict(color="white", width=0.5)),
                hovertemplate="Revenue: $%{x:,.0f}<br>Count: %{y}<extra></extra>",
            ))
            for v, lb, c in [
                (res["mean"], "Mean",  "#1e3a8a"),
                (res["p5"],   "P5",    "#ef4444"),
                (res["p95"],  "P95",   "#22c55e"),
            ]:
                fig.add_vline(x=v, line=dict(color=c, width=2, dash="dash"),
                              annotation_text=f" {lb} = ${v:,.0f}",
                              annotation_font=dict(color=c, size=12, family="Outfit"))
            fig.update_layout(**PLOT, height=320,
                xaxis=dict(title="Revenue per Flight ($)", tickprefix="$",
                           showgrid=False, **TICK),
                yaxis=dict(title="Number of Flights", **GRID, **TICK),
                showlegend=False, bargap=0.03)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"{int(n_sim):,} simulated flights · Std deviation: ${res['std']:,.0f} · "
                       f"Current overbook level: +{ob}")

        # ── Tab 2: Optimizer ──────────────────────────────────────────────────
        with tab2:
            # Profit curve (exact binomial)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=scan_df["Overbook By"], y=scan_df["P95 Revenue"],
                mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
            ))
            fig2.add_trace(go.Scatter(
                x=scan_df["Overbook By"], y=scan_df["P5 Revenue"],
                mode="lines", line=dict(width=0),
                fill="tonexty", fillcolor="rgba(30,136,229,0.08)",
                name="P5–P95 range", hoverinfo="skip",
            ))
            fig2.add_trace(go.Scatter(
                x=scan_df["Overbook By"], y=scan_df["Exact Exp. Profit"],
                mode="lines+markers",
                line=dict(color="#1e88e5", width=3),
                marker=dict(size=6, color="#1e88e5"),
                name="Expected Profit (exact)",
                hovertemplate="Overbook by %{x}<br>Profit: $%{y:,.0f}<extra></extra>",
            ))
            fig2.add_vline(x=ob, line=dict(color="#f59e0b", width=2, dash="dash"),
                           annotation_text=f" Current ({ob})",
                           annotation_font=dict(color="#f59e0b", size=12, family="Outfit"))
            fig2.add_vline(x=best_extra, line=dict(color="#22c55e", width=2.5),
                           annotation_text=f" Optimal ({best_extra})",
                           annotation_font=dict(color="#22c55e", size=12, family="Outfit"))
            fig2.update_layout(**PLOT, height=300,
                title=dict(text="Profit Sensitivity Optimization", font=dict(size=14, color="#1e3a8a")),
                xaxis=dict(title="Additional Seats Sold (Overbooking)",
                           showgrid=False, **TICK),
                yaxis=dict(title="Expected Profit ($)", tickprefix="$", **GRID, **TICK),
                legend=dict(font=dict(size=12)))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

            # Gain vs baseline bars
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=scan_df["Overbook By"],
                y=scan_df["vs Baseline ($)"],
                marker_color=["#22c55e" if v >= 0 else "#ef4444" for v in scan_df["vs Baseline ($)"]],
                marker_opacity=0.85,
                hovertemplate="Overbook by %{x}: %{y:+,.0f} vs no overbook<extra></extra>",
            ))
            fig3.add_hline(y=0, line=dict(color="#94a3b8", width=1))
            fig3.update_layout(**PLOT, height=200,
                title=dict(text="Revenue Gain vs No-Overbooking Baseline",
                           font=dict(size=13, color="#1e3a8a")),
                xaxis=dict(title="Seats Overbooked", showgrid=False, **TICK),
                yaxis=dict(title="Gain ($)", tickprefix="$", **GRID, **TICK),
                showlegend=False)
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
            st.caption("Green = revenue above the no-overbooking baseline · Red = voucher costs exceed gains.")

        # ── Tab 3: Bump Analysis ──────────────────────────────────────────────
        with tab3:
            bump = res["bumped"]
            c1, c2 = st.columns(2)

            with c1:
                unique, counts = np.unique(bump, return_counts=True)
                fig4 = go.Figure()
                fig4.add_trace(go.Bar(
                    x=unique, y=counts / len(bump) * 100,
                    marker_color="#1e88e5", marker_opacity=0.82,
                    hovertemplate="%{x} pax bumped: %{y:.1f}% of flights<extra></extra>",
                ))
                fig4.update_layout(**PLOT, height=290,
                    title=dict(text="Operational Risk Exposure",
                               font=dict(size=13, color="#1e3a8a")),
                    xaxis=dict(title="Bumped Passengers", showgrid=False, **TICK),
                    yaxis=dict(title="% of Flights", **GRID, **TICK),
                    showlegend=False)
                st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                for lbl, val, fg in [
                    ("No passengers bumped",  f"{(bump==0).mean()*100:.1f}%",              "#16a34a"),
                    ("1–2 bumped",            f"{((bump>=1)&(bump<=2)).mean()*100:.1f}%",  "#d97706"),
                    ("3–5 bumped",            f"{((bump>=3)&(bump<=5)).mean()*100:.1f}%",  "#ea580c"),
                    ("6 or more bumped",      f"{(bump>=6).mean()*100:.1f}%",              "#dc2626"),
                ]:
                    st.markdown(f"""
                    <div class="bump-row">
                        <span style="color:#475569">{lbl}</span>
                        <span style="color:{fg};font-family:'JetBrains Mono',monospace;
                                     font-weight:700;font-size:15px">{val}</span>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                worst = int(bump.max()) * float(voucher_cost)
                st.markdown(f"""
                <div style="background:#fef2f2;border:1.5px solid #fca5a5;border-left:5px solid #ef4444;
                            border-radius:10px;padding:16px 18px;">
                    <div style="font-size:11px;font-weight:700;color:#991b1b;text-transform:uppercase;
                                letter-spacing:0.08em;margin-bottom:6px">Worst-Case Exposure</div>
                    <div style="font-size:28px;font-weight:800;color:#dc2626;
                                font-family:'Outfit',sans-serif">${worst:,.0f}</div>
                    <div style="font-size:12px;color:#ef4444;margin-top:4px">
                        {int(bump.max())} passengers × ${float(voucher_cost):,.0f} voucher</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="sec-lbl">Passenger Show-Up Distribution</div>', unsafe_allow_html=True)
            fig5 = go.Figure()
            fig5.add_trace(go.Histogram(
                x=res["showed"], nbinsx=40,
                marker_color="#6366f1", opacity=0.75,
                hovertemplate="Show-ups: %{x}<br>Count: %{y}<extra></extra>",
            ))
            fig5.add_vline(x=int(capacity), line=dict(color="#ef4444", width=2, dash="dash"),
                           annotation_text=f" Capacity ({int(capacity)} seats)",
                           annotation_font=dict(color="#ef4444", size=12, family="Outfit"))
            fig5.update_layout(**PLOT, height=220,
                xaxis=dict(title="Passengers Who Showed Up", showgrid=False, **TICK),
                yaxis=dict(title="Frequency", **GRID, **TICK),
                showlegend=False)
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"Flights where show-ups exceed capacity ({int(capacity)} seats) result in bumping.")

        # ── Tab 4: Full Table ─────────────────────────────────────────────────
        with tab4:
            st.markdown('<div class="sec-lbl">Complete Overbooking Scan — Exact Binomial + Monte Carlo</div>', unsafe_allow_html=True)
            st.dataframe(scan_df, use_container_width=True, hide_index=True)
            st.download_button("⬇ Download as CSV", data=scan_df.to_csv(index=False),
                               file_name="overbooking_scan.csv", mime="text/csv",
                               use_container_width=True)

        # ── Tab 5: Executive Summary ──────────────────────────────────────────
        with tab5:
            st.info(f"**Optimization Result:** To maximize yield, sell **{int(params['capacity'] + best_extra)}** "
                    f"tickets for this **{int(params['capacity'])}**-seat flight "
                    f"(overbook by **{best_extra}**).")

            st.markdown(f"""
#### The Economics of Overbooking

1. **Revenue Capture:** Each overbooked ticket sold generates a certain **${float(params['ticket_price']):,.0f}**
   in revenue — passengers who don't show up are not refunded.

2. **Expected Cost:** Bumping only occurs when actual show-ups exceed capacity.
   At current settings, each bumped passenger costs **${float(params['voucher_cost']):,.0f}** in compensation.

3. **The Equilibrium:** The optimal level of **+{best_extra}** extra seats is where the
   *Marginal Revenue* of the next ticket sold equals the *Marginal Expected Bumping Cost*.

#### Risk Metrics at the Optimal Level

- **Bump Probability:** **{float(best_row['Bump Prob (%)']):.1f}%** chance at least one passenger will be denied boarding.
- **Average Bumped:** **{float(best_row['Avg Bumped']):.2f}** passengers per flight on average.
- **Financial Impact:** Overbooking at this level generates an additional
  **${gain_vs_base:,.0f}** in expected profit vs selling only {int(params['capacity'])} seats.

#### Model Notes
- *Exact method* uses the Binomial distribution `X ~ Binomial(n, 1 − p_no_show)` for precise expected profit.
- *Monte Carlo* adds empirical P5/P95 ranges to quantify downside risk.
- No refund is assumed for no-show passengers.
            """)

        st.markdown("---")
        st.caption(
            f"Model: Binomial Distribution  X ~ Binomial(n, {1-no_show_prob:.2f})  ·  "
            f"{int(n_sim):,} Monte Carlo iterations  ·  Built for airline revenue management"
        )