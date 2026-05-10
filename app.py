# app.py
# 🌍 Simulasi Ekonomi Makro Interaktif - Versi Final Robust & Konsisten
# ✅ Suku Bunga Nominal Acuan | ✅ Grafik Inflasi & Nilai Tukar Lengkap
# ✅ Uji Robustness via Slider σ, θπ, λ | ✅ Confidence Band Dinamis

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# ==========================================================
# 🔧 HELPER FUNCTIONS
# ==========================================================
def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    """Convert hex color (#rrggbb) to rgba string for Plotly"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f'rgba({r}, {g}, {b}, {alpha})'

def create_sample_csv() -> str:
    """Generate sample CSV dataset for download"""
    periods = list(range(50))
    G = [1.0]*10 + [1.35]*15 + [1.0]*25
    r_world = [2.0]*30 + [2.8]*11 + [2.0]*9
    df = pd.DataFrame({'periode': periods, 'G': G, 'r_world': r_world})
    return df.to_csv(index=False, sep=';')

# ==========================================================
# 🧠 CORE MODEL ENGINE
# ==========================================================
def run_model(params: dict, shocks=None) -> tuple:
    """
    New Keynesian Open Economy Model.
    Returns (y, pi, r, e, nx) as 2D arrays (T, N)
    
    DEFINISI SUKU BUNGA:
    - r[t] = suku bunga NOMINAL ACUAN (policy rate) dari Taylor Rule
    - r_real = r[t] - pi_e[t] (tidak ditampilkan langsung, tapi digunakan dalam IS curve)
    - Tidak ada "premium" eksplisit — semua sesuai standar NKOE
    """
    T = int(params['T_sim'])
    
    if shocks is not None:
        eps_y, eps_pi, eps_r, eps_e = shocks
        N = eps_y.shape[1]
    else:
        eps_y = eps_pi = eps_r = eps_e = np.zeros((T, 1))
        N = 1
        
    G_path = np.full(T, params.get('G', 1.0))
    r_w_path = np.full(T, params.get('r_world', 2.0))
    
    if params.get('G_data') is not None and len(params['G_data']) > 0:
        G_path[:len(params['G_data'])] = np.asarray(params['G_data']).flatten()
    else:
        G_path[10:25] = 1.35  # Dummy fiscal stimulus
        
    if params.get('rw_data') is not None and len(params['rw_data']) > 0:
        r_w_path[:len(params['rw_data'])] = np.asarray(params['rw_data']).flatten()
    else:
        r_w_path[30:41] = params.get('r_world', 2.0) + 0.8  # Dummy world rate shock
        
    y   = np.zeros((T, N))
    pi  = np.full((T, N), params['pi_target'])
    pi_e = np.full((T, N), params['pi_target'])
    r   = np.full((T, N), params['r_star'])  # ✅ r = nominal policy rate
    e   = np.zeros((T, N))
    nx  = np.zeros((T, N))
    
    for t in range(1, T):
        # Adaptive expectations
        pi_e[t] = params['lam'] * pi[t-1] + (1 - params['lam']) * params['pi_target']
        
        # Taylor Rule → menghasilkan suku bunga NOMINAL ACUAN
        r_star_t = params['r_star'] + params['theta_pi']*(pi[t-1] - params['pi_target']) + params['theta_y']*y[t-1]
        rho_r = params.get('rho_r', 0.0)
        r[t] = (1-rho_r)*r_star_t + rho_r*r[t-1] if rho_r > 0 else r_star_t
        
        # UIP → nilai tukar log-level
        e[t] = e[t-1] - params['mu']*(r[t] - r_w_path[t])
        
        # Net exports
        nx[t] = params['delta']*e[t] - params['sigma_el']*y[t-1]
        
        # IS Curve → menggunakan suku bunga RIIL ekspektasi: r[t] - pi_e[t]
        y[t] = (params['rho']*y[t-1] 
                - params['beta']*(r[t] - pi_e[t] - params['r_star']) 
                + params['gamma']*nx[t] 
                + params['phi']*(G_path[t] - 1.0))
        
        # Phillips Curve
        pi[t] = pi_e[t] + params['kappa']*y[t-1]
        
        # Add shocks
        y[t] += eps_y[t]
        pi[t] += eps_pi[t]
        r[t] += eps_r[t]
        e[t] += eps_e[t]
        
    return y, pi, r, e, nx

def run_monte_carlo(params: dict, N_sim: int = 100) -> dict:
    """Returns DICTIONARY for safe key-based access"""
    sigma = params.get('sigma_shock', 0.4)
    T = int(params['T_sim'])
    seed = params.get('seed')
    if seed is not None:
        np.random.seed(seed)
    
    eps_y  = np.random.normal(0, sigma, (T, N_sim))
    eps_pi = np.random.normal(0, sigma*0.6, (T, N_sim))
    eps_r  = np.random.normal(0, sigma*0.3, (T, N_sim))
    eps_e  = np.random.normal(0, sigma*0.5, (T, N_sim))
    
    y, pi, r, e, nx = run_model(params, (eps_y, eps_pi, eps_r, eps_e))
    return {'y': y, 'pi': pi, 'r': r, 'e': e, 'nx': nx}

# ==========================================================
# 📊 PLOTTING & EXPORT
# ==========================================================
def create_plot(results: dict, params: dict, var_key: str, title: str, color: str) -> go.Figure:
    T = results[var_key].shape[0]
    t_ax = list(range(T))
    mean = np.mean(results[var_key], axis=1)
    p5   = np.percentile(results[var_key], 5, axis=1)
    p95  = np.percentile(results[var_key], 95, axis=1)
    
    fig = go.Figure()
    fill_rgba = hex_to_rgba(color, alpha=0.15)
    
    fig.add_trace(go.Scatter(
        x=t_ax + t_ax[::-1], y=np.concatenate([p95, p5[::-1]]),
        fill='toself', fillcolor=fill_rgba, line=dict(color='rgba(255,255,255,0)'),
        name='90% Confidence Band', hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter(
        x=t_ax, y=mean, line=dict(color=color, width=3),
        name='Mean Path', hovertemplate='Periode: %{x}<br>Nilai: %{y:.3f}<extra></extra>'
    ))
    
    # Reference lines based on variable type
    if var_key == 'pi':
        fig.add_hline(y=params['pi_target'], line_dash='dot', line_color='black', 
                     annotation_text=f"Target: {params['pi_target']}%")
    elif var_key == 'r':
        fig.add_hline(y=params['r_star'], line_dash='dot', line_color='black',
                     annotation_text=f"Neutral Rate: {params['r_star']}%")
    elif var_key in ['y', 'nx']:
        fig.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
        
    fig.update_layout(
        title=title, 
        xaxis_title='Periode', 
        yaxis_title='Nilai',
        hovermode='x unified', 
        template='plotly_white', 
        height=320,
        margin=dict(l=40, r=20, t=40, b=20),
        legend=dict(
            orientation='h', 
            yanchor='bottom', 
            y=1.02, 
            xanchor='right', 
            x=1,
            font=dict(size=9)
        )
    )
    return fig

def prepare_export_df(results: dict, params: dict) -> pd.DataFrame:
    T = results['y'].shape[0]
    df = pd.DataFrame({'Periode': range(T)})
    for key, label in [('y', 'Output_Gap'), ('pi', 'Inflasi'), ('r', 'Suku_Bunga_Nominal'), 
                       ('e', 'Nilai_Tukar_Log'), ('nx', 'Net_Ekspor')]:
        df[f'{label}_Mean'] = results[key].mean(axis=1)
        df[f'{label}_P5'] = np.percentile(results[key], 5, axis=1)
        df[f'{label}_P95'] = np.percentile(results[key], 95, axis=1)
    for k in ['theta_pi', 'theta_y', 'G', 'pi_target', 'r_star', 'sigma_shock', 'lam']:
        df[f'Param_{k}'] = params.get(k)
    return df

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil_Simulasi')
    return output.getvalue()

# ==========================================================
# 🆕 ANALYSIS ENGINE — DENGAN UJI ROBUSTNESS
# ==========================================================
def generate_analysis(params: dict, results: dict) -> dict:
    """Generate automatic policy analysis with robustness check"""
    T = results['y'].shape[0]
    N = results['y'].shape[1]
    
    # Extract final period values
    fin_y = results['y'][-1]
    fin_pi = results['pi'][-1]
    fin_r = results['r'][-1]
    fin_e = results['e'][-1]
    fin_nx = results['nx'][-1]
    
    # Calculate statistics
    y_mean = np.mean(fin_y)
    y_std = np.std(fin_y)
    pi_mean = np.mean(fin_pi)
    r_mean = np.mean(fin_r)
    e_mean = np.mean(fin_e)
    nx_mean = np.mean(fin_nx)
    
    pi_target = params['pi_target']
    r_star = params['r_star']
    sigma = params['sigma_shock']
    theta_pi = params['theta_pi']
    lam = params['lam']
    
    # 1. Output Condition
    if y_mean > 0.5:
        out_cond = "Overheating"
        out_desc = "Output gap tinggi → tekanan inflasi meningkat"
        out_color = "🔴"
    elif y_mean > 0:
        out_cond = "Ekspansi Moderat"
        out_desc = "Pertumbuhan positif, ruang kebijakan masih ada"
        out_color = "🟢"
    elif y_mean > -0.5:
        out_cond = "Melambat"
        out_desc = "Output di bawah potensi, monitor indikator leading"
        out_color = "🟡"
    else:
        out_cond = "Resesi Teknis"
        out_desc = "Output gap negatif dalam → stimulus diperlukan"
        out_color = "🔴"
    
    # 2. Inflation vs Target
    pi_dev = abs(pi_mean - pi_target)
    if pi_dev < 0.3:
        inf_cond = "On-Target"
        inf_desc = f"Inflasi {pi_mean:.2f}% dekat target {pi_target}%"
        inf_color = "🟢"
    elif pi_mean > pi_target:
        inf_cond = "Above Target"
        inf_desc = f"Inflasi {pi_mean:.2f}% di atas target → risiko ekspektasi"
        inf_color = "🟡"
    else:
        inf_cond = "Below Target"
        inf_desc = f"Inflasi {pi_mean:.2f}% di bawah target → risiko deflasi"
        inf_color = "🟡"
    
    # 3. Monetary Stance (Nominal Policy Rate vs Neutral)
    r_diff = r_mean - r_star
    if r_diff > 0.5:
        mon_cond = "Kontraktif"
        mon_desc = f"Suku bunga nominal {r_mean:.2f}% > netral {r_star}% → meredam permintaan"
        mon_color = "🔵"
    elif r_diff < -0.5:
        mon_cond = "Akomodatif"
        mon_desc = f"Suku bunga nominal {r_mean:.2f}% < netral {r_star}% → stimulus moneter"
        mon_color = "🟢"
    else:
        mon_cond = "Netral"
        mon_desc = "Suku bunga nominal sejalan dengan tingkat netral"
        mon_color = "⚪"
    
    # 4. External Pressure (Exchange Rate Log Change)
    if e_mean > 0.3:
        ext_cond = "Depresiasi"
        ext_desc = "Pelemahan nilai tukar → biaya impor meningkat"
        ext_color = "🟡"
    elif e_mean < -0.3:
        ext_cond = "Apresiasi"
        ext_desc = "Penguatan nilai tukar → daya saing ekspor menurun"
        ext_color = "🟡"
    else:
        ext_cond = "Stabil"
        ext_desc = "Nilai tukar relatif stabil"
        ext_color = "🟢"
    
    # Risk Indicators
    risks = []
    if y_std > 0.3:
        risks.append("• Volatilitas output tinggi → ketidakpastian kebijakan")
    if pi_dev > 0.8:
        risks.append("• Deviasi inflasi besar → anchor ekspektasi melemah")
    if sigma > 0.8:
        risks.append(f"• Ketidakpastian tinggi (σ={sigma}) → confidence band lebar")
    if nx_mean < -0.5 and y_mean > 0:
        risks.append("• Defisit neraca dagang saat ekspansi → risiko eksternal")
    
    # Robustness Check: Confidence Band Width
    cb_width = np.mean(np.percentile(results['y'], 95, axis=1) - np.percentile(results['y'], 5, axis=1))
    if cb_width > 1.5:
        risks.append(f"• Pita kepercayaan lebar ({cb_width:.2f}) → kurangi σ atau naikkan N_sim")
    
    # Policy Recommendations
    recs = []
    if y_mean < -0.3 and pi_mean < pi_target:
        recs.append("• Stimulus fiskal terarah + pelonggaran moneter")
    if y_mean > 0.5 and pi_mean > pi_target:
        recs.append("• Konsolidasi fiskal bertahap + pertahankan suku bunga ketat")
    if pi_dev > 0.5:
        recs.append("• Komunikasi kebijakan jelas untuk anchor ekspektasi")
    if e_mean > 0.5:
        recs.append("• Monitor aliran modal + instrumen makroprudensial FX")
    if theta_pi < 1.0:
        recs.append("• Naikkan θπ > 1 untuk stabilitas inflasi (Taylor Principle)")
    if lam < 0.3:
        recs.append("• Ekspektasi sangat forward-looking → pastikan kredibilitas bank sentral")
    if not risks and not recs:
        recs.append("• Kondisi stabil → pertahankan kebijakan")
    
    # Overall Regime Badge
    if y_mean < -0.5 or pi_dev > 1.0 or sigma > 1.0:
        regime = "Tegangan Tinggi"
        regime_color = "red"
    elif y_mean > 0.3 or pi_dev > 0.6 or cb_width > 1.2:
        regime = "Waspada"
        regime_color = "orange"
    else:
        regime = "Stabil"
        regime_color = "green"
    
    return {
        'out_cond': out_cond, 'out_desc': out_desc, 'out_color': out_color,
        'inf_cond': inf_cond, 'inf_desc': inf_desc, 'inf_color': inf_color,
        'mon_cond': mon_cond, 'mon_desc': mon_desc, 'mon_color': mon_color,
        'ext_cond': ext_cond, 'ext_desc': ext_desc, 'ext_color': ext_color,
        'risks': risks, 'recs': recs,
        'regime': regime, 'regime_color': regime_color,
        'cb_width': cb_width  # For display
    }

def display_analysis(analysis: dict):
    """Display analysis in a nice card format"""
    st.subheader("📊 Analisis Otomatis Hasil Simulasi")
    
    # Regime Badge
    col_badge, _ = st.columns([1, 4])
    with col_badge:
        if analysis['regime_color'] == 'red':
            st.error(f"**{analysis['regime']}**")
        elif analysis['regime_color'] == 'orange':
            st.warning(f"**{analysis['regime']}**")
        else:
            st.success(f"**{analysis['regime']}**")
    
    # Analysis Grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {analysis['out_color']} Kondisi Output")
        st.markdown(f"**{analysis['out_cond']}**")
        st.caption(analysis['out_desc'])
        
        st.markdown(f"### {analysis['inf_color']} Inflasi vs Target")
        st.markdown(f"**{analysis['inf_cond']}**")
        st.caption(analysis['inf_desc'])
    
    with col2:
        st.markdown(f"### {analysis['mon_color']} Stance Moneter")
        st.markdown(f"**{analysis['mon_cond']}**")
        st.caption(analysis['mon_desc'])
        
        st.markdown(f"### {analysis['ext_color']} Tekanan Eksternal")
        st.markdown(f"**{analysis['ext_cond']}**")
        st.caption(analysis['ext_desc'])
    
    # Confidence Band Info
    st.info(f"📏 Lebar Pita Kepercayaan (Output Gap): **{analysis['cb_width']:.2f}**")
    st.caption("Semakin kecil σ atau semakin besar N_sim, pita akan menyempit.")
    
    # Risk Box
    if analysis['risks']:
        st.warning("⚠️ **Indikator Risiko & Robustness**")
        for risk in analysis['risks']:
            st.caption(risk)
    
    # Recommendations Box
    if analysis['recs']:
        st.info("💡 **Rekomendasi Kebijakan & Kalibrasi**")
        for rec in analysis['recs']:
            st.caption(rec)
    
    st.divider()

# ==========================================================
# 🎨 STREAMLIT APP
# ==========================================================
st.set_page_config(page_title="🌍 Simulasi Ekonomi Makro", page_icon="📊", layout="wide")

st.title("🌍 Simulasi Kebijakan Moneter & Fiskal")
st.caption("Model: New Keynesian Open Economy • Taylor Rule | Kurva Phillips | Expectations Adaptif | UIP")

with st.sidebar:
    st.header("⚙️ Parameter Kebijakan")
    col1, col2 = st.columns(2)
    with col1:
        theta_pi = st.slider("θπ (Respons Inflasi)", 0.0, 3.0, 1.5, 0.1, help="Naikkan >1 untuk stabilitas inflasi")
        theta_y  = st.slider("θy (Respons Output)", 0.0, 2.0, 1.1, 0.1)
        lam      = st.slider("λ (Adaptive Exp.)", 0.0, 1.0, 0.65, 0.05, help="Turunkan untuk ekspektasi lebih forward-looking")
        kappa    = st.slider("κ (Phillips Slope)", 0.0, 0.5, 0.18, 0.02)
    with col2:
        phi        = st.slider("φ (Fiscal Multiplier)", 0.0, 1.0, 0.35, 0.05)
        sigma_shock= st.slider("σ (Ketidakpastian)", 0.0, 1.5, 0.45, 0.05, help="Turunkan untuk uji robustness → pita menyempit")
        N_sim      = st.slider("Jumlah Simulasi MC", 50, 500, 150, 50, help="Naikkan untuk pita lebih halus")
        G          = st.slider("G (Stimulus Fiskal)", 0.5, 2.0, 1.0, 0.05)
        
    st.divider()
    pi_target = st.slider("Target Inflasi (%)", 0.0, 5.0, 2.25, 0.25)
    r_star    = st.slider("Suku Bunga Netral (%)", 0.0, 6.0, 3.0, 0.5)
    r_world   = st.slider("Suku Bunga Dunia (%)", 0.0, 6.0, 2.0, 0.5)
    
    st.divider()
    st.subheader("📤 Data Eksternal")
    
    sample_csv = create_sample_csv()
    st.download_button(
        label="📥 Download Sample Dataset (CSV)",
        data=sample_csv,
        file_name="sample_data_ekonomi.csv",
        mime="text/csv",
        use_container_width=True,
        help="Dataset contoh dengan stimulus fiskal & shock suku bunga dunia"
    )
    
    uploaded_file = st.file_uploader("📤 Upload CSV Anda (opsional)", type=['csv'],
                                     help="Format: kolom 'periode', 'G', dan/atau 'r_world'")
    
    st.info("""
    💡 **Tips Robustness**:
    - Turunkan σ → lihat pita kepercayaan menyempit
    - Ubah θπ → amati respons inflasi terhadap kebijakan
    - Ubah λ → lihat kecepatan adaptasi ekspektasi
    """)

# Session state init
if 'results' not in st.session_state: st.session_state.results = None
if 'params' not in st.session_state: st.session_state.params = None

# Auto-run on first load
if st.session_state.results is None:
    with st.spinner("🔄 Memuat simulasi dummy default..."):
        default_params = {
            'theta_pi': 1.5, 'theta_y': 1.1, 'lam': 0.65, 'kappa': 0.18,
            'phi': 0.35, 'sigma_shock': 0.45, 'N_sim': 150, 'G': 1.0,
            'pi_target': 2.25, 'r_star': 3.0, 'r_world': 2.0,
            'T_sim': 50, 'rho': 0.55, 'beta': 0.45, 'gamma': 0.12,
            'delta': 0.22, 'sigma_el': 0.15, 'mu': 0.28, 'rho_r': 0.0, 'seed': 42
        }
        st.session_state.results = run_monte_carlo(default_params, int(default_params['N_sim']))
        st.session_state.params = default_params

# Manual run
if st.button("🔄 Jalankan Ulang Simulasi", type="primary", use_container_width=True):
    with st.spinner("⏳ Menjalankan Monte Carlo..."):
        current_params = {
            'theta_pi': theta_pi, 'theta_y': theta_y, 'lam': lam, 'kappa': kappa,
            'phi': phi, 'sigma_shock': sigma_shock, 'N_sim': N_sim, 'G': G,
            'pi_target': pi_target, 'r_star': r_star, 'r_world': r_world,
            'T_sim': 50, 'rho': 0.55, 'beta': 0.45, 'gamma': 0.12,
            'delta': 0.22, 'sigma_el': 0.15, 'mu': 0.28, 'rho_r': 0.0, 'seed': None
        }
        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file, sep=';')
                if 'G' in df_up.columns: current_params['G_data'] = df_up['G'].values
                if 'r_world' in df_up.columns: current_params['rw_data'] = df_up['r_world'].values
                st.sidebar.success(f"✅ Dataset: {len(df_up)} baris")
            except Exception as e:
                st.sidebar.error(f"❌ Error CSV: {e}")
                
        st.session_state.results = run_monte_carlo(current_params, int(N_sim))
        st.session_state.params = current_params
        st.success("✅ Simulasi selesai!")

# ==========================================================
# 📈 DISPLAY DASHBOARD
# ==========================================================
if st.session_state.results is not None:
    res = st.session_state.results
    par = st.session_state.params
    
    # 🆕 DISPLAY AUTOMATIC ANALYSIS WITH ROBUSTNESS CHECK
    analysis = generate_analysis(par, res)
    display_analysis(analysis)
    
    # Key Metrics
    cols = st.columns(5)
    metrics = [
        ("📊 Output Gap Akhir", f"{res['y'][-1].mean():.2f}"),
        ("🌡️ Inflasi Rata-rata", f"{res['pi'].mean():.2f}%"),
        ("🏦 Suku Bunga Nominal Akhir", f"{res['r'][-1].mean():.2f}%"),  # ✅ Explicitly labeled
        ("💱 Nilai Tukar Akhir (log)", f"{res['e'][-1].mean():.2f}"),
        ("🌐 Net Ekspor Akhir", f"{res['nx'][-1].mean():.2f}")
    ]
    for c, (lbl, val) in zip(cols, metrics):
        c.metric(lbl, val)
        
    st.divider()
    
    # Interactive Charts — All 5 variables shown
    st.subheader("📈 Dinamika Variabel Makroekonomi")
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(create_plot(res, par, 'y', '🔹 Output Gap (%)', '#1f77b4'), use_container_width=True)
        st.plotly_chart(create_plot(res, par, 'pi', '🔹 Inflasi (%)', '#d62728'), use_container_width=True)
    with col_b:
        st.plotly_chart(create_plot(res, par, 'r', '🔹 Suku Bunga Nominal Acuan (%)', '#2ca02c'), use_container_width=True)
        st.plotly_chart(create_plot(res, par, 'e', '🔹 Nilai Tukar (log level)', '#9467bd'), use_container_width=True)
        
    st.plotly_chart(create_plot(res, par, 'nx', '🔹 Net Ekspor (% GDP)', '#17becf'), use_container_width=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Statistik", "📥 Data Lengkap", "ℹ️ Dokumentasi"])
    
    with tab1:
        df_stat = pd.DataFrame({
            'Variabel': ['Output Gap', 'Inflasi', 'Suku Bunga Nominal', 'Nilai Tukar (log)', 'Net Ekspor'],
            'Mean Akhir': [res[k][-1].mean() for k in ['y','pi','r','e','nx']],
            'Std Dev': [res[k].std() for k in ['y','pi','r','e','nx']],
            'P5': [np.percentile(res[k], 5) for k in ['y','pi','r','e','nx']],
            'P95': [np.percentile(res[k], 95) for k in ['y','pi','r','e','nx']]
        })
        st.dataframe(
            df_stat.style.format({
                "Mean Akhir": "{:.3f}",
                "Std Dev": "{:.3f}",
                "P5": "{:.3f}",
                "P95": "{:.3f}"
            }), 
            use_container_width=True
        )
        
    with tab2:
        df_exp = prepare_export_df(res, par)
        st.dataframe(df_exp.head(12), use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 Unduh CSV", df_exp.to_csv(index=False, sep=';'), 
                             "hasil_simulasi.csv", "text/csv", use_container_width=True)
        with c2:
            st.download_button("📊 Unduh Excel", to_excel_bytes(df_exp), 
                             "hasil_simulasi.xlsx", 
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             use_container_width=True)
                             
    with tab3:
        st.markdown("""
        ### 📘 Spesifikasi Model Ekonomi
        | Komponen | Persamaan | Interpretasi |
        |----------|-----------|-------------|
        | **Taylor Rule** | `rₜ = r* + θπ(πₜ₋₁-π*) + θy·yₜ₋₁` | Menghasilkan **suku bunga nominal acuan** |
        | **Kurva Phillips** | `πₜ = πᵉ + κ·yₜ₋₁` | Inflasi tergantung ekspektasi & output gap |
        | **Adaptive Expectations** | `πₜ = λ·πₜ₋₁ + (1-λ)·π*` | Pembelajaran dari inflasi masa lalu |
        | **UIP Exchange Rate** | `eₜ = eₜ₋₁ - μ(rₜ-rʷ)` | Nilai tukar log-level, dipengaruhi diferensial suku bunga |
        | **Net Exports** | `nxₜ = δ·eₜ - σ·yₜ₋₁` | Apresiasi → ekspor turun; output tinggi → impor naik |
        | **IS Curve** | `yₜ = ρ·yₜ₋₁ - β(rₜ-πₜᵉ-r*) + γ·nxₜ + φ·(Gₜ-1)` | Menggunakan **suku bunga riil ekspektasi** `(rₜ - πᵉ)` |
        
        ### 🔍 Konsistensi Definisi Suku Bunga
        - **Grafik & Dashboard**: Menampilkan `r[t]` = **suku bunga nominal acuan** (policy rate)
        - **Dalam Model**: Digunakan sebagai input ke UIP dan IS curve (setelah dikurangi ekspektasi inflasi untuk menjadi riil)
        - **Tidak ada "premium"** — semua sesuai standar New Keynesian Open Economy
        
        ### ⚠️ Disclaimer
        Model ini bersifat **edukatif dan stylized**. Parameter default menggunakan nilai ilustratif.
        """)

st.markdown("---")
st.caption("🌍 Simulasi Ekonomi Makro | www.dataaksi.id | ✅ Auto-run + Auto-Analysis + Robustness Check")
st.caption("✅ Developed with Akal sehat, Qwen, Claude 3.5, GPT-4o")
