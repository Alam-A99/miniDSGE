# Simulasi Model DSGE: IS Curve, Phillips Curve & Taylor Rule

Aplikasi interaktif menggunakan Streamlit yang memvisualisasikan dinamika makroekonomi dalam model DSGE sederhana. Simulasi melibatkan:

* **IS Curve** (Permintaan Agregat Dinamis)
* **Phillips Curve Baru** (Penawaran Agregat Dinamis)
* **Aturan Taylor** (Kebijakan Suku Bunga Responsif)

---

## ⚙️ Fitur

* Interaktif dengan slider parameter: `β`, `κ`, `φπ`, `φx`, `ρ`, `σ`, dan `rⁿ`
* Visualisasi waktu nyata untuk:

  * Output Gap (`xₜ`)
  * Inflasi (`πₜ`)
  * Suku Bunga Nominal (`iₜ`)
* Simulasi shock pasokan (cost-push shock)
* Siap dideploy ke Railway

---

## Struktur Model

### 1. IS Curve (Permintaan Agregat Dinamis):

$$
x_t = E_t x_{t+1} - \frac{1}{\sigma} \left( i_t - E_t \pi_{t+1} - r^n \right)
$$

### 2. New Keynesian Phillips Curve (Penawaran Agregat Dinamis):

$$
\pi_t = \beta E_t \pi_{t+1} + \kappa x_t + u_t
$$

### 3. Aturan Taylor (Respon Kebijakan Moneter):

$$
i_t = \rho i_{t-1} + (1 - \rho)(\phi_\pi \pi_t + \phi_x x_t)
$$

---

## Cara Menjalankan Secara Lokal

1. Clone repositori:

   ```bash
    git clone https://github.com/Alam-A99/miniDSGE.git
   cd miniDSGE
   ```
