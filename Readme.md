# MRP Lot Sizing Engine — Koreksi UTS Otomatis

Tool interaktif untuk menyelesaikan soal Material Requirements Planning (MRP)
lot sizing dengan empat metode heuristik — **MCP**, **PPB**, **LTC**, dan **LUC**.
Berbeda dari implementasi MRP pada umumnya, tool ini membangkitkan
**Gross Requirement unik per mahasiswa** berdasarkan 8 digit NPM dan
beberapa parameter tambahan, sehingga setiap mahasiswa mendapat soal
dan jawaban yang berbeda — dirancang untuk membantu proses koreksi UTS
mata kuliah Perencanaan & Pengendalian Produksi.

**[Coba Live Demo →] https://dickyai.github.io/midexam-mrp-tool/**

<!-- Opsional: tambahkan screenshot di sini setelah situs live
![Screenshot](./screenshot.png)
-->

## Fitur

- Input NPM 8 digit → Gross Requirement dibangkitkan otomatis mengikuti aturan pairing digit yang unik per soal
- Perhitungan lot sizing dengan 4 metode: Minimum Cost Period (MCP), Part Period Balancing (PPB), Least Total Cost (LTC), Least Unit Cost (LUC)
- Tabel MRP lengkap (GR, SR, OHI, NR, PORec, PORel) per metode
- Detail iterasi lot sizing — menampilkan angka dasar setiap keputusan LANJUT/STOP (holding cost, part-period, EPP, selisih terhadap setup cost, dst)
- Perbandingan total cost antar metode
- Seluruh komputasi berjalan **di browser**, tanpa server backend

## Tech Stack

- **Python** — seluruh logika bisnis dan algoritma heuristik
- **PyScript / Pyodide (WebAssembly)** — menjalankan Python langsung di browser
- **HTML/CSS** — antarmuka, tanpa framework JS tambahan
- Hosting: GitHub Pages (static, tanpa server)

## Struktur File

```
.
├── index.html   # Struktur halaman & form input NPM
├── style.css    # Styling
└── main.py      # Logika MRP — dijalankan di browser via PyScript
```

## Latar Belakang

Dibuat sebagai bagian dari tugas asisten dosen dalam mengawasi dan
mengoreksi UTS MRP. Parameter pembangkit soal (koefisien biaya, aturan
pairing digit NPM) diganti setiap periode ujian agar soal tetap unik
tiap angkatan.

---

*Proyek pribadi — dibagikan sebagai bagian dari portofolio.*
