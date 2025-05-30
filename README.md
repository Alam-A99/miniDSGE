# 📊 Simulasi Model DSGE: IS Curve, Phillips Curve & Taylor Rule

Aplikasi interaktif menggunakan Streamlit yang memvisualisasikan dinamika makroekonomi dalam model DSGE sederhana. Simulasi melibatkan:

- **IS Curve** (Permintaan Agregat Dinamis)
- **Phillips Curve Baru** (Penawaran Agregat Dinamis)
- **Aturan Taylor** (Kebijakan Suku Bunga Responsif)

![preview](https://user-images.githubusercontent.com/your-screenshot.png)

---

## ⚙️ Fitur

- Interaktif dengan slider parameter: β, κ, φπ, φx, ρ, σ, dan rⁿ
- Visualisasi waktu nyata untuk:
  - Output Gap (xₜ)
  - Inflasi (πₜ)
  - Suku Bunga Nominal (iₜ)
- Simulasi shock penawaran (cost-push shock)
- Bisa di-deploy ke Railway

---

## 📌 Struktur Model

### IS Curve:

\[
x_t = E_t x_{t+1} - \frac{1}{\sigma}(i_t - E_t \pi_{t+1} - r^n)
\]

### Phillips Curve Baru:

\[
\pi_t = \beta E_t \pi_{t+1} + \kappa x_t + u_t
\]

### Aturan Taylor:

\[
i_t = \rho i_{t-1} + (1 - \rho)(\phi_\pi \pi_t + \phi_x x_t)
\]

---

## 🚀 Cara Menjalankan Secara Lokal

1. Clone repositori:
   ```bash
   git clone https://github.com/username/dsge-streamlit.git
   cd dsge-streamlit
