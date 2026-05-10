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
## 👤 Author

**Alam Yin**      
🌐 Website: [www.dataaksi.id](https://www.dataaksi.id)

## 📄 Lisensi

Karya ini dilisensikan di bawah [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

Creative Commons ©© 2025 [www.dataaksi.id](https://www.dataaksi.id)




graph TD
    %% DEFINISI FASE
    subgraph A_PELAKSANAAN [📋 A. PELAKSANAAN ASESMEN]
        A1[1. FR.APL.01 Permohonan Sertifikasi]
        A2[2. FR.APL.02 Asesmen Mandiri]
        A3[3. Portofolio Asesi]
        A4[4. FR.MAPA.01 Merencanakan Aktivitas & Proses]
        A5[5. Referensi: Skema, Standar Kompetensi, Kelompok Pekerjaan]
        A6[6. FR.MAPA.02 Peta Instrumen & Perencanaan]
        A7[7. FR.AK.07 Ceklis Penyesuaian Wajar]
        A8[9. FR.AK.01 Persetujuan Asesmen & Kerahasiaan]
    end

    subgraph INSTRUMEN [🔍 INSTRUMEN ASESMEN]
        I1[10. FR.IA.01 Observasi / Simulasi]
        I2[11. FR.IA.02 TPD Demonstrasi]
        I3[12-20. Instrumen Pendukung\n(PMO, DIT, DPT PG/Essay,\nCVP, VPK, CRP, dll)]
    end

    subgraph B_KEPUTUSAN [⚖️ B. KEPUTUSAN]
        B1[21. FR.AK.02 Rekaman Asesmen Kompetensi]
        B2[22. FR.AK.03 Umpan Balik & Catatan Asesmen]
    end

    subgraph C_LAPORAN [📊 C. LAPORAN ASESMEN]
        C1[23. FR.AK.05 Laporan Asesmen]
        C2[24. FR.AK.06 Meninjau Proses Asesmen]
    end

    subgraph D_VALIDASI [✅ D. VALIDASI]
        D1[25. FR.VA Kontribusi dalam Validasi Asesmen]
    end

    %% ALUR LOGIS
    A1 --> A2 --> A3 --> A4
    A4 --> A5
    A4 --> A6
    A6 --> A7
    A8 --> A4
    A6 --> INSTRUMEN
    INSTRUMEN --> B1 --> B2 --> C1
    C1 --> C2
    C2 --> D1
    
    %% ALUR BANDING (Opsional)
    C1 -.->|Jika Asesi Tidak Setuju| AK4[8. FR.AK.04 Formulir Banding]
    AK4 -.->|Review Ulang| C1

    %% STYLING
    classDef phase fill:#f8f9fa,stroke:#495057,stroke-width:2px,rx:8px;
    class A_PELAKSANA,INSTRUMEN,B_KEPUTUSAN,C_LAPORAN,D_VALIDASI phase;
    classDef critical fill:#e3f2fd,stroke:#1976d2,stroke-width:2px;
    class A4,A6,B1,C1 critical;
