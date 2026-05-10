import numpy as np
import streamlit as st
import plotly.graph_objs as go

# ==========================================
# 1. SIDEBAR: INPUT PARAMETER
# ==========================================
st.sidebar.title("⚙️ Parameter DSGE Model")
beta   = st.sidebar.slider("β (Diskonto Waktu)", 0.8, 1.0, 0.99, 0.01)
kappa  = st.sidebar.slider("κ (Sensitivitas Inflasi)", 0.01, 0.5, 0.1, 0.01)
phi_pi = st.sidebar.slider("ϕπ (Respon Inflasi)", 0.5, 3.0, 1.5, 0.1)
phi_x  = st.sidebar.slider("ϕx (Respon Output Gap)", 0.0, 2.0, 0.5, 0.1)
rho    = st.sidebar.slider("ρ (Smoothing Suku Bunga)", 0.0, 1.0, 0.7, 0.05)
sigma  = st.sidebar.slider("σ (Elastisitas Permintaan)", 0.5, 3.0, 1.0, 0.1)
rn     = st.sidebar.slider("rⁿ (Suku Bunga Natural)", 0.0, 3.0, 1.0, 0.1)

# ==========================================
# 2. SIMULASI DINAMIS
# ==========================================
T = 40
u = np.zeros(T)
u[5] = 0.5  # Shock pasokan di t=5

x, pi, i = np.zeros(T), np.zeros(T), np.zeros(T)
exp_x, exp_pi = np.zeros(T), np.zeros(T)

for t in range(1, T):
    exp_x[t]  = x[t-1]
    exp_pi[t] = pi[t-1]
    x[t] = exp_x[t] - (1/sigma)*(i[t-1] - exp_pi[t] - rn)
    pi[t] = beta*exp_pi[t] + kappa*x[t] + u[t]
    i[t]  = rho*i[t-1] + (1 - rho)*(phi_pi*pi[t] + phi_x*x[t])

# ==========================================
# 3. VISUALISASI
# ==========================================
time = np.arange(T)
fig = go.Figure()
fig.add_trace(go.Scatter(x=time, y=x,  mode='lines+markers', name='Output Gap (xₜ)', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=time, y=pi, mode='lines+markers', name='Inflasi (πₜ)'))
fig.add_trace(go.Scatter(x=time, y=i,  mode='lines+markers', name='Suku Bunga (iₜ)', line=dict(dash='dot')))
fig.update_layout(title="📈 Simulasi Dinamis DSGE", xaxis_title="Periode", yaxis_title="Level", height=500)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### 📘 Deskripsi Variabel:
- **Output Gap (xₜ)**: Selisih output aktual vs potensial. Negatif → ekonomi lesu.
- **Inflasi (πₜ)**: Dipengaruhi ekspektasi, output gap, dan shock pasokan.
- **Suku Bunga (iₜ)**: Mengikuti Aturan Taylor, dihaluskan oleh parameter `ρ`.
""")

# ==========================================
# 4. ANALISIS OTOMATIS (Update Real-time)
# ==========================================
st.divider()
st.markdown("### 📊 Analisis Dinamis Berbasis Parameter")

t_shock = 5
x_post = x[t_shock:]
pi_post = pi[t_shock:]
i_post = i[t_shock:]

# 1. Puncak Respons & Waktu Pencapaian
idx_x = t_shock + np.argmax(np.abs(x_post))
idx_pi = t_shock + np.argmax(np.abs(pi_post))
idx_i = t_shock + np.argmax(np.abs(i_post))
peak_x, peak_pi, peak_i = x[idx_x], pi[idx_pi], i[idx_i]

# 2. Waktu Pemulihan (Kembali ke dalam ±5% steady state)
def recovery_time(series, start_t=t_shock, threshold=0.05):
    for t in range(start_t, T):
        if abs(series[t]) < threshold:
            return t - start_t
    return T - start_t  # Selalu kembalikan int agar perbandingan aman

rec_x = recovery_time(x)
rec_pi = recovery_time(pi)
rec_i = recovery_time(i)

# Fungsi formatting untuk tampilan UI
def fmt_recovery(val):
    max_period = T - t_shock
    return str(val) if val < max_period else f"> {max_period}"

# 3. Statistik Lanjutan
vol_x, vol_pi, vol_i = np.std(x_post), np.std(pi_post), np.std(i_post)
corr_pi_x = np.corrcoef(pi_post, x_post)[0, 1]

# 4. Tampilan Metrik
c1, c2, c3 = st.columns(3)
c1.metric("📉 Deviasi Output Gap Max", f"{peak_x:.3f}", f"Pada t={idx_x} | Vol: {vol_x:.3f}")
c2.metric("🔥 Puncak Inflasi", f"{peak_pi:.3f}", f"Pada t={idx_pi} | Vol: {vol_pi:.3f}")
c3.metric("🏦 Puncak Suku Bunga", f"{peak_i:.3f}", f"Pada t={idx_i} | Vol: {vol_i:.3f}")

st.markdown(f"""
⏱️ **Estimasi Waktu Pemulihan (ke ±{0.05:.0%} steady state):**
- Output Gap: `{fmt_recovery(rec_x)}` periode | Inflasi: `{fmt_recovery(rec_pi)}` periode | Suku Bunga: `{fmt_recovery(rec_i)}` periode
🔗 **Korelasi Inflasi-Output Gap (pasca shock):** `{corr_pi_x:.2f}`
""")

# 5. Diagnosis Kebijakan & Struktur
st.markdown("📋 **Diagnosis Kebijakan & Struktur Ekonomi:**")
taylor_ok = phi_pi > 1.0
if taylor_ok:
    st.success("✅ Prinsip Taylor Terpenuhi: `ϕπ > 1` → Ekspektasi inflasi terkendali, ekuilibrium deterministik.")
else:
    st.warning("⚠️ Prinsip Taylor Dilanggar: `ϕπ ≤ 1` → Risiko indeterminasi & ekspektasi inflasi self-fulfilling.")

smoothing_desc = "Tinggi" if rho > 0.7 else "Rendah" if rho < 0.3 else "Sedang"
st.info(f"🔹 **Smoothing Suku Bunga**: {smoothing_desc} (`ρ = {rho:.2f}`) → {'Perubahan bertahap & menghindari volatilitas' if rho > 0.6 else 'Respons kebijakan lebih agresif & cepat'}")

kappa_desc = "Kuat" if kappa > 0.15 else "Lemah" if kappa < 0.05 else "Moderat"
st.info(f"🔹 **Sensitivitas Kurva Phillips**: {kappa_desc} (`κ = {kappa:.2f}`) → {'Inflasi sangat responsif terhadap slack riil' if kappa > 0.1 else 'Inflasi cenderung rigid terhadap perubahan output'}")

# 6. Interpretasi Dinamis Berbasis Hasil Simulasi
st.markdown("🧠 **Interpretasi Hasil Simulasi:**")
if peak_pi > peak_x:
    st.warning("📊 **Inflasi Dominan**: Shock pasokan lebih cepat diteruskan ke harga. Bank Sentral perlu respons kontraktif lebih tegas.")
elif peak_x > peak_pi:
    st.success("📊 **Output Gap Dominan**: Dampak lebih terasa di sisi riil. Kebijakan mungkin menoleransi sedikit overshoot inflasi demi stabilitas pertumbuhan.")
else:
    st.info("📊 **Respons Seimbang**: Transmisi shock ke inflasi dan output relatif proporsional.")

if rec_i > rec_x:
    st.caption("💡 Suku bunga lebih lambat pulih → Kebijakan moneter menjaga stance ketat lebih lama untuk memastikan ekspektasi tertambat.")
else:
    st.caption("💡 Output gap lebih lambat pulih → Ekonomi riil membutuhkan waktu lebih panjang untuk normalisasi penuh.")

if abs(corr_pi_x) > 0.7:
    st.caption(f"📈 Korelasi {'negatif' if corr_pi_x < 0 else 'positif'} kuat antara inflasi & output → Trade-off kebijakan {'klasik (Phillips)' if corr_pi_x < 0 else 'tidak konvensional (supply shock dominan)'}")
