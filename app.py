import numpy as np
import streamlit as st
import plotly.graph_objs as go

# Sidebar untuk parameter model
st.sidebar.title("Parameter DSGE Model")
beta   = st.sidebar.slider("β (Diskonto Waktu)", 0.8, 1.0, 0.99, 0.01)
kappa  = st.sidebar.slider("κ (Sensitivitas Inflasi)", 0.01, 0.5, 0.1, 0.01)
phi_pi = st.sidebar.slider("ϕπ (Respon Inflasi)", 0.5, 3.0, 1.5, 0.1)
phi_x  = st.sidebar.slider("ϕx (Respon Output Gap)", 0.0, 2.0, 0.5, 0.1)
rho    = st.sidebar.slider("ρ (Smoothing Suku Bunga)", 0.0, 1.0, 0.7, 0.05)
sigma  = st.sidebar.slider("σ (Elastisitas Permintaan)", 0.5, 3.0, 1.0, 0.1)
rn     = st.sidebar.slider("rⁿ (Suku Bunga Natural)", 0.0, 3.0, 1.0, 0.1)

T = 40
u = np.zeros(T)
u[5] = 0.5  # shock pasokan di t=5

x, pi, i = np.zeros(T), np.zeros(T), np.zeros(T)
exp_x, exp_pi = np.zeros(T), np.zeros(T)

for t in range(1, T):
    exp_x[t]  = x[t-1]
    exp_pi[t] = pi[t-1]
    x[t] = exp_x[t] - (1/sigma)*(i[t-1] - exp_pi[t] - rn)
    pi[t] = beta*exp_pi[t] + kappa*x[t] + u[t]
    i[t]  = rho*i[t-1] + (1 - rho)*(phi_pi*pi[t] + phi_x*x[t])

# Visualisasi dengan Plotly
time = np.arange(T)
fig = go.Figure()
fig.add_trace(go.Scatter(x=time, y=x,  mode='lines+markers', name='Output Gap (xₜ)', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=time, y=pi, mode='lines+markers', name='Inflasi (πₜ)'))
fig.add_trace(go.Scatter(x=time, y=i,  mode='lines+markers', name='Suku Bunga (iₜ)', line=dict(dash='dot')))
fig.update_layout(title="Simulasi Dinamis DSGE", xaxis_title="Periode", yaxis_title="Level", height=500)

st.plotly_chart(fig)

st.markdown("### Deskripsi Dinamis:")
st.write("""
- **Output Gap (xₜ)**: Mencerminkan selisih antara output aktual dan potensial. Jika output gap negatif, berarti ekonomi sedang lesu.
- **Inflasi (πₜ)**: Dipengaruhi oleh output gap dan ekspektasi inflasi masa lalu. Meningkat saat output gap positif.
- **Suku Bunga (iₜ)**: Dikendalikan melalui Aturan Taylor, merespons perubahan inflasi dan output gap. Di-'haluskan' oleh parameter ρ.
""")
