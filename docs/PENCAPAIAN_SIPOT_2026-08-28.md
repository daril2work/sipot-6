# 🏥 DOKUMENTASI PENCAPAIAN & PENGEMBANGAN SIPOT PUSKESMAS KUNJANG
**Sistem Informasi Pengelolaan & Pelayanan Obat Terpadu**  
*Kabupaten Kediri - Jawa Timur*

---

## 📌 1. RINGKASAN EKSEKUTIF
Sistem Informasi Pengelolaan & Pelayanan Obat Terpadu (**SIPOT**) Puskesmas Kunjang telah berhasil dikembangkan dengan arsitektur berbasis Python Flask, SQLAlchemy, Tailwind CSS, dan Alpine.js. 

Aplikasi ini mengintegrasikan dua sudut pandang utama pengelolaan farmasi tingkat Puskesmas:
1. **Sudut Pandang Operasional Harian (POS & Inventory Management):** Pengelolaan stok fisik berbasis FEFO (*First Expired, First Out*), penerimaan SBBK dari GFK, penyerahan resep/distribusi ke sub-unit/poli, audit penyesuaian stok rusak/ED, dan stok opname berkala.
2. **Sudut Pandang Pelaporan Resmi Kemenkes RI (Format LPLPO 10-Kolom):** Penyiapan otomatis Laporan Pemakaian dan Lembar Permintaan Obat (LPLPO) bulanan dengan ekspor resmi format Excel (.xlsx) dan pencetakan Berita Acara.

---

## 🚀 2. RINCIAN MODUL & FITUR UTAMA

### A. Autentikasi Multi-Role & Restriksi Hak Akses (RBAC)
- **Role Admin (Apoteker / Pengelola Gudang Farmasi Utama):**
  - Mengelola seluruh modul master data, transaksi masuk/keluar, audit stok, stok opname, dan laporan LPLPO bulanan.
- **Role Sub-Unit (Petugas Poli Pelayanan / Unit Aksi):**
  - Memiliki portal khusus (*Unit Dashboard*) yang hanya menampilkan riwayat penyerahan dan penerimaan obat ke unit yang bersangkutan (misal: Poli Umum hanya dapat melihat transaksi Poli Umum).
- **⚡ Toggle Alih Peran 1-Klik (Development Mode):**
  - Menu dropdown instan pada topbar header aplikasi untuk beralih antar akun (Admin vs Poli Umum vs KIA/KB vs UGD, dll.) secara cepat tanpa perlu logout.

### B. Master Data SDM Pegawai (DUK Resmi)
- Menyimpan 48 data pegawai resmi DUK Puskesmas Kunjang lengkap dengan NIP, Golongan, Jenis ASN (PNS/PPPK/Kontrak), TMT Golongan, dan Jabatan Kedinasan.
- Mendukung pencarian, penambahan, pengeditan, serta fitur **Hapus Semua / Impor Masal** (CSV/JSON).

### C. Master Sub-Unit / Poli & Integrasi SDM
- Mendaftarkan 13 Sub-Unit/Poli Pelayanan resmi (Gudang Farmasi, Poli Umum, Poli Gigi, KIA/KB, UGD & Rawat Inap, Labkesmas, Pelayanan Gizi, Kesling, Rekam Medis, TU, Promkes, Pustu Melati, Poskesdes Sejahtera).
- **Dropdown SDM Otomatis:** Pemilihan Penanggung Jawab (PJ) Sub-Unit mengambil data pegawai secara otomatis dari daftar Master Pegawai yang telah diupload.

### D. Master Obat Formularium (64 Item) & Bulk Import
- 64 sediaan obat Formularium Puskesmas yang dikelompokkan ke dalam kategori *Obat Oral*, *Obat Injeksi*, *Obat Luar*, *Sirup & Drops*, serta *BMHP*.
- Fitur Impor Masal Data Obat via drag-and-drop file atau paste format CSV/JSON.

### E. Transaksi Stok (Masuk SBBK & Pengeluaran FEFO)
- **Penerimaan SBBK:** Pencatatan obat masuk dari Gudang Farmasi Kabupaten (GFK) lengkap dengan nomor batch, tanggal kadaluarsa (ED), dan sumber dana (APBD/DAK).
- **Pengeluaran FEFO & POS Pelayanan:** Penyerahan obat ke sub-unit/poli secara otomatis memprioritaskan batch yang paling mendekati tanggal kadaluarsa (*First Expired, First Out*) untuk mencegah pemborosan obat ED.
- **Struk Penyerahan Obat:** Pencetakan struk bukti penyerahan obat internal.

### F. Audit Penyesuaian Stok (Rusak, ED, Kehilangan)
- Modul pencatatan penyesuaian stok fisik secara langsung jika terdapat barang rusak, kadaluarsa (ED), selisih hilang, atau koreksi fisik.
- Audit log tersimpan lengkap dengan informasi petugas audit, jenis penyesuaian (*Pengurangan/Penambahan*), stok sebelum dan sesudah.

### G. Stok Opname Berkala & Berita Acara Resmi
- **Sesi Opname Interaktif:** Memuat seluruh batch obat aktif ke dalam lembar kerja opname secara otomatis.
- **Kalkulasi Selisih Live:** Pengisian jumlah fisik langsung menghitung selisih (*stok_fisik - stok_sistem*).
- **Finalisasi & Lock Dokumen:** Memfinalkan dokumen opname langsung meng-update stok batch sistem agar sesuai 100% dengan fisik gudang.
- **Cetak Berita Acara:** Cetak dokumen fisik resmi Berita Acara Stok Opname lengkap dengan blok tanda tangan Petugas Audit dan Kepala Puskesmas Kunjang.

### H. Modul LPLPO Bulanan Kemenkes RI
- Generasi otomatis lembar LPLPO 10-Kolom Baku (*Stok Awal, Penerimaan, Persediaan, Pemakaian, Sisa Stok, Stok Optimum, Permintaan, Pemberian*).
- Fitur **Ekspor Excel (.xlsx)** dengan *styling* profesional dan rumus otomatis.

### I. Paginasi Global
- Seluruh 8 tabel data utama (*Obat, Pegawai, SubUnit, Transaksi Masuk, Transaksi Keluar, Penyesuaian Stok, Stok Opname, LPLPO*) dilengkapi dengan pagination berbasis `Flask-SQLAlchemy` yang mempertahankan query filter saat berpindah halaman.

---

## 🗝️ 3. DAFTAR AKUN DEFAULT (CREDENTIALS)

| Peran (Role) | Username | Password | Unit / Deskripsi |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Apoteker & Pengelola Gudang Farmasi Utama |
| **SubUnit** | `apotek` | `123456` | Gudang Farmasi & Apotek |
| **SubUnit** | `poli.umum` | `123456` | Poli Umum |
| **SubUnit** | `kia.kb` | `123456` | KIA / KB |
| **SubUnit** | `poli.gigi` | `123456` | Poli Gigi & Mulut |
| **SubUnit** | `ugd.rawat` | `123456` | UGD & Rawat Inap |
| **SubUnit** | `labkes` | `123456` | Laboratorium Kesehatan |
| **SubUnit** | `gizi` | `123456` | Pelayanan Gizi |
| **SubUnit** | `kesling` | `123456` | Kesehatan Lingkungan |
| **SubUnit** | `simpus` | `123456` | Rekam Medis & Pendaftaran |
| **SubUnit** | `tu` | `123456` | Tata Usaha & Kepegawaian |
| **SubUnit** | `promkes` | `123456` | Promkes & Pemberdayaan |
| **SubUnit** | `pustu` | `123456` | Pustu Melati |
| **SubUnit** | `poskesdes` | `123456` | Poskesdes Sejahtera |

---

## 📂 4. STRUKTUR FOLDER APLIKASI
```
sipot-6-flask/
├── app/
│   ├── routes/
│   │   ├── auth.py          # Route Login, Logout, Switch Account, SubUnit Dashboard
│   │   ├── dashboard.py     # Route Admin Dashboard Utama
│   │   ├── lplpo.py         # Route LPLPO Bulanan & Ekspor Excel
│   │   ├── obat.py          # Route Master Obat & Bulk Import
│   │   ├── pegawai.py       # Route Master SDM Pegawai DUK
│   │   ├── penyesuaian.py   # Route Audit Penyesuaian Stok (ED/Rusak)
│   │   ├── pos.py           # Route POS Pelayanan & Distribusi
│   │   ├── stok_opname.py   # Route Stok Opname & Berita Acara Cetak
│   │   ├── subunit.py       # Route Master Sub-Unit / Poli
│   │   └── transaksi.py     # Route Transaksi Masuk & Keluar FEFO
│   ├── services/
│   │   ├── inventory.py     # Logika FEFO & Pengelolaan Stok
│   │   └── lplpo_engine.py  # Engine Perhitungan Matriks LPLPO
│   ├── templates/
│   │   ├── auth/            # Template Login & SubUnit Dashboard
│   │   ├── lplpo/           # Template LPLPO (List, Detail, Print, Generate)
│   │   ├── obat/            # Template Master Obat
│   │   ├── pegawai/         # Template Master Pegawai
│   │   ├── penyesuaian/     # Template Penyesuaian Stok
│   │   ├── stok_opname/     # Template Stok Opname & Berita Acara
│   │   ├── subunit/         # Template Master Sub-Unit
│   │   ├── transaksi/       # Template Transaksi Masuk & Keluar
│   │   ├── base.html        # Layout Utama & Sidebar Responsive
│   │   ├── dashboard.html   # Template Dashboard Utama
│   │   ├── pagination.html  # Komponen Reusable Pagination Bar
│   │   └── pos.html         # Template POS Pelayanan
│   ├── utils/
│   │   └── excel_exporter.py# Engine Ekspor XLSX LPLPO Format Kemenkes
│   ├── __init__.py          # App Factory, Blueprint Registry & Context Processors
│   └── models.py            # Skema Database SQLAlchemy
├── docs/
│   └── PENCAPAIAN_SIPOT_2026-08-28.md # Dokumentasi Resmi Pengembangan
├── farmasi_lplpo.db         # Database SQLite Local Development
├── Procfile                 # Konfigurasi Cloud Deployment (Gunicorn)
├── requirements.txt         # Daftar Dependensi Python
├── run.py                   # Script Entry Point Server Flask
├── seed.py                  # Script Seeding Data Master & User Default
└── wsgi.py                  # Adapter WSGI Server
```

---

## 🌐 5. PANDUAN REPOSITORY & CLOUD DEPLOYMENT

### A. Repository GitHub
- **URL Repository:** [`https://github.com/daril2work/sipot-6.git`](https://github.com/daril2work/sipot-6.git)
- **Branch Utama:** `main`

### B. Langkah Update Server PythonAnywhere
Untuk memperbarui aplikasi pada server live PythonAnywhere, buka **Bash Console** pada PythonAnywhere lalu jalankan perintah berikut:

```bash
cd ~/sipot-6 && git reset --hard HEAD && git pull && python seed.py
```

Setelah eksekusi perintah selesai dengan keterangan `[OK] Bulk Seeding Berhasil!`, buka tab **Web** pada PythonAnywhere lalu klik **Reload**.

---

*Dokumentasi ini disusun secara otomatis sebagai catatan resmi pengembangan proyek SIPOT Puskesmas Kunjang tanggal 28 Agustus 2026.*
