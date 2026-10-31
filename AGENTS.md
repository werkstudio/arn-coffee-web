# AGENTS.md — Coding Agent Guidelines for ARN Coffee Web

Dokumen ini adalah pedoman teknis dan panduan operasional bagi **AI Coding Agent** (seperti Antigravity, Claude Code, Cursor, Copilot, dll.) yang bekerja pada repositori `arn-coffee-web`.

BACA DOKUMEN INI SEBELUM MEMODIFIKASI KODE.

---

## 1. Ringkasan Arsitektur & Filosofi Proyek

* **Single-File App Architecture**: Seluruh antarmuka, token CSS, dan logika interaksi berpusat di [index.html](file:///Users/arry/Documents/Projects/arn-coffee-web/index.html). Tidak ada framework runtime berat (React/Vue/Angular) dan tidak ada bundler (Vite/Webpack).
* **Genre Desain**: **Atmospheric / Luxury Craft** (mengikuti standar **Hallmark v2.0**).
* **Layout Posture**: **100dvh Single-Screen Interactive Showcase** (`body { overflow: hidden; height: 100dvh; }`). Konten tambahan (detail bahan, order channel, jam buka) disajikan melalui **Glass Modals** dan **Slide Drawers**, bukan melalui scroll halaman vertikal biasa.

---

## 2. Parameter Bisnis & Data Autentik (Ground Truth)

Jangan pernah mengarang (*hallucinate*) data bisnis atau penghargaan fiktif. Selalu gunakan parameter nyata berikut:

* **Brand**: ARN Coffee (*Bold Artisan Brews & Real Aren*)
* **Harga & Ukuran**: **Semua Varian Rp 18.000 (Ukuran 200ml)**.
* **Bahan Baku**:
  * **Biji Kopi**: Signature Houseblend, 100% Organik (Profil sangrai artisan).
  * **Berry Americano**: 100% Sari Buah Berry Murni (bukan perisa sintetis).
  * **Aren**: 100% Sari Nira Aren Murni Organik (tanpa sirup jagung/pemanis buatan).
* **Alamat Roastery**:
  `Mega Regency No.Kav.42, Karang Pamulang, Mandalajati, Bandung City, West Java 40195`
* **Jam Operasional**:
  `Senin – Sabtu, 08:00 – 17:00 WIB` *(Minggu Libur)*
* **Nomor WhatsApp Order**:
  `+62 858-6300-2824` (Format URL: `https://wa.me/6285863002824?text=...`)

---

## 3. Protokol Sinkronisasi State (The Multi-Component Sync Rule)

State utama aplikasi dikendalikan oleh:
```javascript
let activeFlavorIndex = 0; // 0: berry, 1: classic, 2: strong
const flavors = ['berry', 'classic', 'strong'];
const flavorConfigs = { ... };
```

### ⚠️ ATURAN SINKRONISASI WAJIB:
Saat menambahkan varian, mengubah harga, atau memicu pergantian rasa, Agent **WAJIB** menyinkronkan 5 elemen antarmuka sekaligus melalui fungsi `syncActiveElements()`:

1. **Desktop Navbar Buttons**: `.nav .nav-item[data-flavor]`
2. **Mobile Drawer Items**: `.mobile-nav-item[data-flavor]`
3. **Product Carousel Cards**: `.carousel-cards .card[data-flavor]`
4. **Order Modal Chips**: `.flavor-chips .flavor-chip[data-flavor]`
5. **3D Stage & Background Gradient**: `switchFlavor(flavorKey)` yang menganimasikan botol 2.5D, partikel 3D, dan variabel `--bg-inner`, `--bg-mid`, `--bg-outer`, `--accent-color`.

---

## 4. Standar Desain & Batasan Hallmark (Floor Rules)

Setiap modifikasi CSS dan layout **WAJIB** mematuhi aturan baku Hallmark berikut:

1. **DILARANG `transition: all`**:
   Selalu deklarasikan properti transisi secara eksplisit.
   *Contoh Benar:* `transition: transform 0.25s ease, opacity 0.25s ease, background 0.3s ease;`
2. **DILARANG Menganimasikan Dimensi Geometris**:
   Jangan menganimasikan `width`, `height`, `top`, atau `left` dalam transisi interaktif. Gunakan `transform: translate()` dan `scale()`.
3. **DILARANG Mengarang Metrik / Penghargaan Palsu**:
   Tidak boleh ada *"Best Coffee Award 2025"* atau *"5.0 Rating dari 10.000 Pelanggan"*. Gunakan fakta nyata produk (organik, 200ml, alamat Bandung, nomor WA).
4. **Viewport & Overflow Control**:
   * `html, body { overflow-x: clip; }`
   * Dilarang menggunakan `overflow-x: hidden` atau `100vw` (mencegah horizontal scrollbar jump).
5. **Aksesibilitas & Focus States**:
   * Setiap elemen interaktif (`<button>`, `<a>`, dialog trigger) wajib memiliki gaya `:focus-visible` instan:
     `:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }`
   * Elemen 3D dekoratif `<model-viewer>` wajib menyertakan `tabindex="-1"` dan `aria-hidden="true"`.
6. **Dukungan Tombol Keyboard**:
   Tombol `Escape` harus menutup modal yang sedang terbuka, atau menutup mobile drawer jika sedang terbuka.

---

## 5. Pedoman Kritis Performa (60 FPS & Memory Management)

Aplikasi ini menjalankan render loop terus-menerus (`requestAnimationFrame`) untuk fisika botol dan partikel 3D. Ikuti aturan performa berikut:

### A. Larangan Layout Thrashing di Loop Animasi
* **JANGAN PERNAH** memanggil `getBoundingClientRect()`, `offsetWidth`, `offsetHeight`, atau `offsetTop` di dalam fungsi `animate()`.
* Posisi pusat partikel **wajib di-cache** di luar loop menggunakan array `berryCenters[]` melalui fungsi `cacheBerryPositions()`.
* Fungsi `cacheBerryPositions()` hanya dipanggil saat *resize* window atau setelah selesai transisi pergantian rasa.

### B. Page Visibility API
Pastikan loop animasi dan generator gelembung dihentikan ketika tab browser berada di latar belakang (*backgrounded*):
```javascript
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAnimation();
    } else {
        startAnimation();
    }
});
```

### C. Idle-Time Prefetching
Aset sekunder (botol rasa lain dan model 3D) di-preload saat waktu luang browser melalui `requestIdleCallback(prefetchIdle, { timeout: 2000 })`. Jangan memicu unduhan aset sekunder saat render pertama (*first contentful paint*).

---

## 6. Prosedur Verifikasi Sebelum Menyelesaikan Tugas

Sebelum melaporkan tugas selesai atau melakukan commit:

1. **Uji Validitas Sintaks JavaScript**:
   ```bash
   node -e '
   const fs = require("fs");
   const html = fs.readFileSync("index.html", "utf8");
   const scripts = html.match(/<script>([\s\S]*?)<\/script>/g);
   scripts.forEach((s) => new Function(s.replace(/<\/?script>/g, "")));
   console.log("Syntax OK");
   '
   ```
2. **Uji Integritas ID Elemen HTML**:
   Pastikan tidak ada ID duplikat yang tidak disengaja.
3. **Cek Pelanggaran Floor Rules**:
   Pastikan tidak ada kemunculan `transition: all` atau `overflow-x: hidden`.
4. **Verifikasi Jalur Pemesanan WhatsApp**:
   Pastikan format pesan WhatsApp menghasilkan encoded URL yang valid dan nomor tujuan adalah `6285863002824`.

---

## 7. Referensi File & Skrip Utilitas

* `scripts/build_thematic_models.py`: Pembuat model 3D GLB prosedural lokal.
* `scripts/build_textures.py`: Generator tekstur prosedural botol.
* `scripts/build_bottle_assets.py`: Utilitas pengolah gambar botol WebP.
* `references/`: Folder aset referensi dan mockup mentah.

---

## 8. Panduan Deployment Cloudflare Workers

Proyek ini dikonfigurasi menggunakan **Cloudflare Workers Static Assets** (bukan Workers Sites lawas):
* **Konfigurasi Utama**: [wrangler.toml](file:///Users/arry/Documents/Projects/arn-coffee-web/wrangler.toml) (`[assets]` block).
* **Asset Whitelist / Ignore**: [.assetsignore](file:///Users/arry/Documents/Projects/arn-coffee-web/.assetsignore) menyaring file dokumentasi, skrip build python, dan folder `.git` agar tidak ikut terunggah ke Cloudflare edge.
* **Header Keamanan & Caching**: [_headers](file:///Users/arry/Documents/Projects/arn-coffee-web/_headers) menyetel `Cache-Control: public, max-age=31536000, immutable` pada folder `/assets/*`.
* **Perintah Deploy**: `npx wrangler deploy` (atau `npm run deploy`).

