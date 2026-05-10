import numpy as np
import streamlit as st
import plotly.graph_objs as go

# ==========================================
# 1. SIDEBAR: INPUT PARAMETER
# ==========================================
st.sidebar.title("⚙️ Parameter Model DSGE (New Keynesian)")
beta   = st.sidebar.slider("β (Faktor Diskonto)", 0.8, 1.0, 0.99, 0.01)
kappa  = st.sidebar.slider("κ (Sensitivitas NKPC)", 0.01, 0.5, 0.1, 0.01)
phi_pi = st.sidebar.slider("ϕπ (Respon Inflasi)", 0.5, 3.0, 1.5, 0.1)
phi_x  = st.sidebar.slider("ϕx (Respon Output Gap)", 0.0, 2.0, 0.5, 0.1)
rho    = st.sidebar.slider("ρ (Smoothing Suku Bunga)", 0.0, 1.0, 0.7, 0.05)
sigma  = st.sidebar.slider("σ (Elastisitas Intertemporal)", 0.5, 3.0, 1.0, 0.1)
rn     = st.sidebar.slider("rⁿ (Suku Bunga Natural)", 0.0, 3.0, 1.0, 0.1)

# ==========================================
# 2. SIMULASI DINAMIS
# ==========================================
T = 40
u = np.zeros(T)
u[5] = 0.5  # Cost-push / supply shock di t=5

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
- **Inflasi (πₜ)**: Dipengaruhi ekspektasi forward-looking, output gap, dan shock pasokan.
- **Suku Bunga (iₜ)**: Mengikuti Aturan Taylor, dihaluskan oleh parameter `ρ`.
""")

# ==========================================
# 4. METRIK KUANTITATIF
# ==========================================
st.divider()
st.markdown("### 📊 Metrik Dinamis Pasca-Shock (t ≥ 5)")

t_shock = 5
x_post, pi_post, i_post = x[t_shock:], pi[t_shock:], i[t_shock:]

idx_x = t_shock + np.argmax(np.abs(x_post))
idx_pi = t_shock + np.argmax(np.abs(pi_post))
idx_i = t_shock + np.argmax(np.abs(i_post))
peak_x, peak_pi, peak_i = x[idx_x], pi[idx_pi], i[idx_i]

def recovery_time(series, start_t=t_shock, threshold=0.05):
    for t in range(start_t, T):
        if abs(series[t]) < threshold:
            return t - start_t
    return T - start_t

rec_x = recovery_time(x)
rec_pi = recovery_time(pi)
rec_i = recovery_time(i)

def fmt_recovery(val):
    max_p = T - t_shock
    return str(val) if val < max_p else f"> {max_p}"

vol_x, vol_pi, vol_i = np.std(x_post), np.std(pi_post), np.std(i_post)
corr_pi_x = np.corrcoef(pi_post, x_post)[0, 1]

c1, c2, c3 = st.columns(3)
c1.metric("📉 Deviasi Output Gap Max", f"{peak_x:.3f}", f"Pada t={idx_x} | Vol: {vol_x:.3f}")
c2.metric("🔥 Puncak Inflasi", f"{peak_pi:.3f}", f"Pada t={idx_pi} | Vol: {vol_pi:.3f}")
c3.metric("🏦 Puncak Suku Bunga", f"{peak_i:.3f}", f"Pada t={idx_i} | Vol: {vol_i:.3f}")

st.markdown(f"""
⏱️ **Estimasi Waktu Pemulihan (ke ±{0.05:.0%} steady state):**
- Output Gap: `{fmt_recovery(rec_x)}` periode | Inflasi: `{fmt_recovery(rec_pi)}` periode | Suku Bunga: `{fmt_recovery(rec_i)}` periode
🔗 **Korelasi Inflasi-Output Gap (pasca shock):** `{corr_pi_x:.2f}`
""")

# ==========================================
# 5. INTERPRETASI TEORITIS LENGKAP
# ==========================================
st.divider()
st.markdown("🧠 **Interpretasi Teoritis & Dinamika Kebijakan (New Keynesian Framework)**")

# 1. NKPC & Trade-off
kappa_text = "Harga relatif fleksibel (κ tinggi) → shock langsung diterjemahkan menjadi tekanan inflasi. Kurva Phillips curam." if kappa > 0.15 else "Harga kaku (κ rendah) → dampak shock tertahan di output gap sebelum perlahan meresap ke inflasi. Kurva Phillips landai."
beta_text = f"Faktor diskonto β={beta:.2f} menunjukkan ekonomi sangat *forward-looking*. Ekspektasi inflasi masa depan ({'kuat' if beta > 0.95 else 'sedang'}) mempercepat transmisi kebijakan ke variabel nominal saat ini melalui mekanisme intertemporal optimization."

if corr_pi_x < -0.4:
    tradeoff_text = "Korelasi negatif kuat mengkonfirmasi *Taylor Principle in action*: bank sentral berhasil menciptakan trade-off stabilisasi dengan menaikkan suku bunga riil, mengorbankan output gap sementara untuk menekan ekspektasi inflasi."
elif corr_pi_x > 0.3:
    tradeoff_text = "Korelasi positif mencerminkan dominasi *cost-push shock* pada fase awal (stagflasi parsial). Transmisi kebijakan belum sepenuhnya membalik dinamika nominal-riil, atau respons kebijakan terlalu gradual untuk memutus lingkaran harga-upah."
else:
    tradeoff_text = "Korelasi lemah menunjukkan proses dis-inflasi dan penyesuaian output berjalan relatif independen, konsisten dengan mekanisme *expectations anchoring* yang efektif melalui forward guidance implisit."

# 2. Monetary Policy Rule & Determinacy
taylor_ok = phi_pi > 1.0  # Dipisahkan agar tidak terjadi error sintaks
taylor_text = "✅ **Prinsip Taylor Terpenuhi (φπ > 1)**: Respons suku bunga terhadap inflasi lebih dari satu-ke-satu. Suku bunga riil naik saat inflasi meningkat, menjamin determinasi keseimbangan (kondisi Blanchard-Kahn) dan mencegah ekspektasi inflasi *self-fulfilling*." if taylor_ok else "⚠️ **Prinsip Taylor Dilanggar (φπ ≤ 1)**: Respons kebijakan terlalu lemah. Suku bunga riil tidak cukup naik saat inflasi melonjak, berisiko menimbulkan indeterminasi, volatilitas ekspektasi, dan potensi spiral inflasi-harga yang tidak terkendali."

rho_text = "🔹 **Gradualism (ρ tinggi)**: Bank sentral mengutamakan stabilitas pasar keuangan dan menghindari kejutan kebijakan (*policy surprises*). Cocok untuk *anchoring* jangka panjang, namun dapat memperpanjang durasi dis-inflasi dan meningkatkan *output cost* penyesuaian." if rho > 0.6 else "🔹 **Aggressive Adjustment (ρ rendah)**: Respons langsung tanpa smoothing. Efektif untuk meredam shock cepat dan mengunci ekspektasi, namun berpotensi meningkatkan volatilitas suku bunga jangka pendek dan mengacaukan perencanaan intertemporal pelaku ekonomi."

# 3. IS Curve & Real Transmission
sigma_text = "🔹 **Elastisitas Permintaan Tinggi (σ besar)**: Konsumen sangat sensitif terhadap perubahan suku bunga riil. Transmisi kebijakan moneter ke sektor riil kuat, sehingga output gap cepat merespons, namun juga lebih rentan terhadap *volatility* akibat fluktuasi kebijakan." if sigma > 1.5 else "🔹 **Elastisitas Permintaan Rendah (σ kecil)**: Konsumsi cenderung di-*smooth* secara intertemporal. Transmisi kebijakan moneter ke output gap lebih lemah dan gradual, membuat penyesuaian sektor riil berjalan lambat namun stabil, mengurangi risiko overshooting output."

# 4. Synthesis & Policy Implications
if peak_i > peak_pi and taylor_ok:
    synth_text = "📊 **Sintesis Kebijakan**: Puncak suku bunga yang melebihi puncak inflasi mengindikasikan stance moneter yang *credibly tight*. Bank sentral berhasil menaikkan suku bunga riil sesuai kerangka New Keynesian, menekan permintaan agregat melalui kurva IS, dan meng-*anchoring* ekspektasi inflasi melalui forward guidance implisit."
elif rec_x > rec_pi and rho > 0.5:
    synth_text = "📊 **Sintesis Kebijakan**: Pemulihan output gap yang lebih lambat dibanding inflasi, dipadu dengan smoothing suku bunga tinggi, mencerminkan *policy trade-off klasik*: stabilitas nominal dicapai lebih cepat, sementara penyesuaian riil memakan waktu akibat rigiditas harga/wage dan transmisi IS yang gradual."
else:
    synth_text = "📊 **Sintesis Kebijakan**: Dinamika sistem menunjukkan keseimbangan stabil antara penyesuaian nominal dan riil. Respons kebijakan terkalibrasi baik untuk meredam shock pasokan tanpa mengorbankan stabilitas makroekonomi jangka menengah, sesuai dengan prediksi *optimal policy* di bawah komitmen sederhana."

st.markdown(f"""
**1️⃣ Transmisi Shock & Kurva Phillips (NKPC)**
• {kappa_text}
• {beta_text}
• {tradeoff_text}

**2️⃣ Aturan Kebijakan Moneter & Stabilitas**
• {taylor_text}
• {rho_text}

**3️⃣ Kurva IS & Transmisi ke Sektor Riil**
• {sigma_text}

**4️⃣ Implikasi Kebijakan & Sintesis Dinamis**
• {synth_text}
""")

st.caption("📚 *Referensi Teoritis: Kerangka New Keynesian DSGE standar (Woodford, 2003; Gali, 2015). Determinasi keseimbangan dijamin oleh Prinsip Taylor (φπ>1), sedangkan trade-off inflasi-output muncul akibat nominal rigidities (κ) dan intertemporal substitution (σ).*)")
