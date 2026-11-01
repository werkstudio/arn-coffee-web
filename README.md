# ARN Coffee — Bold Artisan Brews & Real Aren

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](#)
[![Stack: Vanilla HTML5 / CSS3 / JS](https://img.shields.io/badge/Stack-Vanilla_HTML5_|_CSS3_|_JS-crimson.svg)](#)
[![3D: Google Model Viewer](https://img.shields.io/badge/3D-Model_Viewer-orange.svg)](#)
[![Animation: GSAP 3](https://img.shields.io/badge/Animation-GSAP_3-green.svg)](#)

Website resmi interaktif untuk **ARN Coffee**, brand kopi artisan *Ready-To-Drink* (RTD) berbasis di Bandung yang menghadirkan paduan espresso bold dari biji kopi organik, 100% sari buah berry asli, dan 100% sari nira aren murni.

Dibangun dengan pendekatan desain **Hallmark (Atmospheric Genre)**: single-screen 3D interactive showcase, specular glare physics, force-field particle repulsion, dan sistem pemesanan langsung WhatsApp yang terintegrasi.

---

## ☕ Varian Produk

Semua varian disajikan dalam kemasan botol higienis **200ml** dengan harga seragam **Rp 18.000**:

| Varian | Karakter Rasa | Komposisi Utama | Kemasan & Harga |
| :--- | :--- | :--- | :--- |
| **Berry Americano** | *Crisp, fruity, electric* | Signature Houseblend 100% Organic Espresso + 100% Pure Berry Juice | 200ml · Rp 18.000 |
| **Aren Latte Classic** | *Smooth, velvety, comforting* | Signature Houseblend Espresso + Fresh Creamy Milk + 100% Gula Aren Murni | 200ml · Rp 18.000 |
| **Aren Latte Strong** | *Fierce, double shot, bold* | Double Shot Dark-Roast Organic Arabica + Raw Palm Sugar + Fresh Milk | 200ml · Rp 18.000 |
| **Matcha Latte** | *Earthy, silky, umami* | 100% Real Artisan Matcha Murni + Velvety Fresh Milk | 200ml · Rp 18.000 |

> **Penyimpanan:** Wajib disimpan dalam kulkas bersuhu 4°C. Kocok perlahan sebelum dinikmati. Masa simpan optimal 7 hari dalam kondisi dingin.

---

## ⚡ Fitur Utama

1. **2.5D / 3D Interactive Bottle Stage**
   - Efek rotasi dinamis 3D yang merespons pergerakan kursor mouse dan gestur drag/touch pada layar sentuh.
   - Dynamic specular glare yang mengikuti sudut pencahayaan kursor.
   - Drop shadow prosedural yang bergerak proporsional terhadap elevasi botol.

2. **Thematic 3D Floating Elements & Force-Field Repulsion**
   - Aset 3D GLB tematik mengambang di sekitar botol menggunakan `<model-viewer>`:
     - **Berry Americano**: Floating cherries & leaves.
     - **Aren Classic**: Biji kopi 3D & balok es batu (*ice cubes*).
     - **Aren Strong**: Biji kopi 3D & lempengan gula aren (*palm sugar*).
     - **Matcha Latte**: Daun teh 3D (*leaves*) & balok es batu (*ice cubes*).
   - Efek gravitasi/repulsi 400px: Elemen menjauh secara organik saat didekati kursor pengguna.

3. **Sinkronisasi Multi-Komponen (Unified State)**
   - Perubahan varian rasa (via desktop navbar, mobile drawer, kartu carousel, atau chip modal) secara otomatis menyinkronkan:
     - Rotasi dan pergantian botol aktif.
     - Transisi warna gradien background (`--bg-inner`, `--bg-mid`, `--bg-outer`, `--accent-color`).
     - Headline tipografi (judul varian & deskripsi).
     - Model 3D tematik yang meledak keluar (*implosion-explosion transition*).
     - Data pratinjau dan kalkulasi harga pada modal pemesanan.

4. **Direct WhatsApp Ordering System**
   - Modal glassmorphic pemesanan instan tanpa perlu akun/registrasi.
   - Stepper jumlah botol (1–30 botol) dengan kalkulasi subtotal dan total harga real-time.
   - Generator pesan WhatsApp otomatis ke **`+62 858-6300-2824`** lengkap dengan rincian pesanan dan alamat pengiriman.

5. **Panel Edukasi "The Craft & Real Aren"**
   - Menjelaskan 4 pilar kualitas ARN Coffee:
     1. Signature Houseblend 100% Organic (tanpa pestisida/residu kimia).
     2. 100% Sari Buah Berry Murni & Gula Aren Organik Asli (tanpa perisa buatan & tanpa sirup fruktosa sintetis).
     3. Standar Cold Storage Sealed Bottle 200ml.
     4. Transparansi lokasi Roastery & jam operasional Bandung.

6. **Optimasi Performa & Aksesibilitas (Hallmark Compliant)**
   - **Zero Layout Thrashing**: Posisi elemen di-cache, tidak ada pemanggilan `getBoundingClientRect()` di dalam loop 60 FPS `requestAnimationFrame`.
   - **Page Visibility API**: Loop animasi dan pembuatan partikel dihentikan otomatis saat tab browser tidak aktif untuk menghemat baterai & CPU.
   - **Idle Prefetch**: Botol sekunder dan model 3D di-preload saat browser dalam kondisi idle via `requestIdleCallback`.
   - **Keyboard Navigable & A11y**: Dukungan penuh `:focus-visible`, penutupan dialog via tombol `Escape`, dan label ARIA semantik.

---

## 🛠️ Tech Stack & Dependensi

* **HTML5 & CSS3 Modern**: CSS Variables, radial gradients, glassmorphism backdrop-filter, `overflow-x: clip`.
* **Google Model Viewer (`@google/model-viewer` v3)**: Render WebGL GLB interaktif tanpa overhead engine berat.
* **GSAP 3 (`gsap.min.js`)**: Animasi koreografi kompleks, elastisitas impuls botol, dan interpolasi warna.
* **Google Fonts**: `Galada` (heading dekoratif), `Outfit`, `Inter`, dan `Manrope` (body & navigasi).
* **Zero Build Step**: Berjalan langsung di browser tanpa bundler (No Webpack/Vite/Node required to serve).

---

## 📂 Struktur Direktori

```text
arn-coffee-web/
├── index.html                 # Entry point aplikasi (HTML, CSS tokens, JS logic)
├── assets/
│   ├── bottles/               # Aset foto botol WebP transparan (200ml)
│   │   ├── bottle-berry-americano.webp
│   │   ├── bottle-latte-classic.webp
│   │   ├── bottle-latte-strong.webp
│   │   └── bottle-matcha-latte.webp
│   ├── cards/                 # Thumbnail kartu carousel rasa
│   │   ├── card-berry-americano.webp
│   │   ├── card-latte-classic.webp
│   │   ├── card-latte-strong.webp
│   │   └── card-matcha-latte.webp
│   ├── models/                # Aset 3D GLB (biji kopi, es batu, aren, daun)
│   │   ├── coffee-bean.glb
│   │   ├── ice-cube.glb
│   │   ├── palm-sugar.glb
│   │   └── leaves.glb
│   ├── textures/              # Peta tekstur untuk model 3D
│   ├── logo-tiger-transparent.webp
│   └── logo-tiger-badge.webp
├── scripts/                   # Script utilitas pembuatan aset 3D & tekstur
│   ├── build_thematic_models.py
│   ├── build_textures.py
│   └── build_bottle_assets.py
├── references/                # Foto mentah & referensi visual
├── .hallmark/                 # Snapshot & konfigurasi audit desain Hallmark
├── README.md                  # Dokumentasi proyek
└── AGENTS.md                  # Panduan & pedoman teknis untuk Coding Agent
```

---

## 🚀 Cara Menjalankan Secara Lokal

Karena proyek ini menggunakan Vanilla Web Stack murni, Anda cukup menyajikan folder proyek menggunakan HTTP server lokal apa saja:

### Opsi 1: Menggunakan Python
```bash
python3 -m http.server 8000
```
Buka browser di: `http://localhost:8000`

### Opsi 2: Menggunakan Node `npx serve`
```bash
npx serve .
```

### Opsi 3: VS Code / Live Server
Klik kanan pada file `index.html` dan pilih **"Open with Live Server"**.

---

## ☁️ Deployment ke Cloudflare Workers

Proyek ini telah dikonfigurasi menggunakan **Cloudflare Workers Static Assets** (`wrangler.toml` & `_headers`) untuk performa CDN edge global, kompresi otomatis (Brotli/Gzip), dan caching statis instan.

### 1. Prasyarat
Pastikan Anda memiliki akun Cloudflare dan telah menginstal dependensi:
```bash
npm install
```

### 2. Uji Coba Lokal (Workers Dev Server)
Untuk menjalankan web di lingkungan simulasi Cloudflare Workers:
```bash
npx wrangler dev
# atau
npm run dev
```

### 3. Deploy ke Cloudflare Workers
Pastikan Anda sudah login ke akun Cloudflare di terminal Anda:
```bash
npx wrangler login
```
Lalu jalankan perintah deployment:
```bash
npx wrangler deploy
# atau
npm run deploy
```

> **Detail Konfigurasi:**
> * `wrangler.toml`: Menggunakan fitur modern `[assets]` dengan `not_found_handling = "single-page-application"`.
> * `.assetsignore`: Memastikan hanya file produksi (`index.html`, `assets/`, `_headers`) yang diunggah ke edge CDN Cloudflare.
> * `_headers`: Menetapkan header keamanan (`nosniff`, `DENY`) dan cache immutable 1 tahun untuk `/assets/*`.

---

## 📍 Informasi Bisnis & Operasional

* **Nama Brand**: ARN Coffee
* **Tagline**: *Bold Artisan Brews & Real Aren*
* **Alamat Roastery & Lab**:
  > Mega Regency No.Kav.42, Karang Pamulang, Kec. Mandalajati, Kota Bandung, Jawa Barat 40195
* **Jam Operasional**:
  > Senin – Sabtu, 08:00 – 17:00 WIB *(Minggu Libur)*
* **Layanan Pengiriman**: Instant & Same-day delivery (Cold storage packing) area Bandung & sekitarnya.
* **Kontak Pemesanan WhatsApp**: [`+62 858-6300-2824`](https://wa.me/6285863002824)

---

## 📄 Lisensi

Hak Cipta © 2025–2026 ARN Coffee & Werkstudio. Seluruh hak cipta dilindungi undang-undang.
