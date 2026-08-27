from datetime import date, timedelta
from app import create_app
from app.models import db, Obat, SubUnit, BatchObat, TransaksiMasuk, TransaksiMasukItem, TransaksiKeluar, TransaksiKeluarItem, Pegawai
from app.services.lplpo_engine import generate_lplpo_periode

app = create_app()

def seed_database():
    with app.app_context():
        print("Membersihkan dan inisialisasi database...")
        db.drop_all()
        db.create_all()

        print("Menambahkan Data Pegawai Puskesmas (48 Pegawai Resmi DUK)...")
        pegawai_list_data = [
            {"nama": "dr.Durotun Nafisa", "nip": "19750423 200212 2 005", "gol": "IVc", "jenis": "PNS", "tmt": "10/1/2022", "jabatan": "Dokter Ahli Madya", "unit": "Manajemen & Kepala Puskesmas"},
            {"nama": "drg. Putri Emyta Sari", "nip": "19810604 200902 2 004", "gol": "IVb", "jenis": "PNS", "tmt": "4/1/2023", "jabatan": "Dokter Gigi Ahli Madya", "unit": "Poli Gigi & Mulut"},
            {"nama": "Setya Budi, Amd., Kep", "nip": "19700508 199203 1 003", "gol": "IIId", "jenis": "PNS", "tmt": "10/1/2015", "jabatan": "Perawat Ahli pertama", "unit": "UGD & Rawat Inap"},
            {"nama": "Luluk Listyaningsih,AMG", "nip": "19691030 199203 2 008", "gol": "IIId", "jenis": "PNS", "tmt": "10/1/2016", "jabatan": "Nutrisionis Penyelia", "unit": "Pelayanan Gizi"},
            {"nama": "Yuanendah, SST.", "nip": "19710125 199203 2 010", "gol": "IIId", "jenis": "PNS", "tmt": "10/1/2021", "jabatan": "Bidan Ahli Muda", "unit": "KIA / KB"},
            {"nama": "Daril Rahmatullah, S. Farm.", "nip": "19810704 200901 1 004", "gol": "IVa", "jenis": "PNS", "tmt": "12/1/2024", "jabatan": "Apoteker Ahli Madya", "unit": "Gudang Farmasi & Apotek"},
            {"nama": "Fitri Ariani Isnaningtyas, Amd.AK", "nip": "19780908 199903 2 001", "gol": "IIId", "jenis": "PNS", "tmt": "8/1/2025", "jabatan": "Pranata Labkes Pelaksana Penyelia", "unit": "Laboratorium Kesehatan"},
            {"nama": "Rinda Ari Puspita, Amd. KG", "nip": "19871127 201001 2 008", "gol": "IIIb", "jenis": "PNS", "tmt": "4/1/2022", "jabatan": "Terapis Gigi dan Mulut Mahir", "unit": "Poli Gigi & Mulut"},
            {"nama": "dr. Rizky Rachmat Kurniawan", "nip": "19960310 202203 1 005", "gol": "IIIb", "jenis": "PNS", "tmt": "1/3/2023", "jabatan": "Dokter Pertama", "unit": "Poli Umum"},
            {"nama": "Supatemi, Amd.Keb", "nip": "19720306 200604 2 014", "gol": "IIIb", "jenis": "PNS", "tmt": "8/1/2025", "jabatan": "Bidan Mahir", "unit": "KIA / KB"},
            {"nama": "Anik Sri Purwati, Amd. Keb.", "nip": "19740806 200604 2 022", "gol": "IIIb", "jenis": "PNS", "tmt": "8/1/2025", "jabatan": "Bidan Mahir", "unit": "KIA / KB"},
            {"nama": "Enny Nurhayati, Amd.. Keb.", "nip": "19741101 200604 2 014", "gol": "IIIb", "jenis": "PNS", "tmt": "10/1/2025", "jabatan": "Bidan Mahir", "unit": "KIA / KB"},
            {"nama": "Sulisni, Amd. Keb.", "nip": "19750315 200604 2 031", "gol": "IIIb", "jenis": "PNS", "tmt": "8/1/2025", "jabatan": "Bidan Mahir", "unit": "KIA / KB"},
            {"nama": "Estu Rahayuningsih, Amd. Keb.", "nip": "19751117 200701 2 010", "gol": "IIIb", "jenis": "PNS", "tmt": "10/1/2025", "jabatan": "Bidan Mahir", "unit": "KIA / KB"},
            {"nama": "Prihatiningtyas, Amd. Keb.", "nip": "19760521 200701 2 012", "gol": "IIIb", "jenis": "PNS", "tmt": "10/1/2025", "jabatan": "Bidan Mahir", "unit": "KIA / KB"},
            {"nama": "Mey Idayati, Amd.Kep", "nip": "19870507 201402 2 001", "gol": "IIIb", "jenis": "PNS", "tmt": "10/1/2023", "jabatan": "Perawat Mahir", "unit": "UGD & Rawat Inap"},
            {"nama": "Sito Luncono Setio Utomo", "nip": "19790506 201001 1 027", "gol": "IId", "jenis": "PNS", "tmt": "4/1/2022", "jabatan": "Pengadministrasi Kepegawaian", "unit": "Tata Usaha & Kepegawaian"},
            {"nama": "Siti Aminah, Amd Kep.", "nip": "19870803 201903 2 005", "gol": "IId", "jenis": "PNS", "tmt": "10/1/2022", "jabatan": "Perawat Terampil", "unit": "UGD & Rawat Inap"},
            {"nama": "Nuryana Vidya C, Amd.Kep", "nip": "19970326 202012 2 013", "gol": "IId", "jenis": "PNS", "tmt": "6/1/2024", "jabatan": "Perawat Terampil", "unit": "Poli Umum"},
            {"nama": "Novia Anjarwati, Amd. Kes", "nip": "19951125 202012 2 013", "gol": "IId", "jenis": "PNS", "tmt": "6/1/2024", "jabatan": "Sanitarian Pelaksana", "unit": "Kesehatan Lingkungan"},
            {"nama": "Dinung Wahyu Purwanti", "nip": "19930105 202221 2 001", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/1/2022", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Susi Winda Wandari, Amd Keb", "nip": "19940405 202321 2 005", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/4/2023", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Desi Natalia, SST", "nip": "3506216412890001", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Bidan Terampil", "unit": "Tata Usaha & Kepegawaian"},
            {"nama": "Devi Ardianti, SE", "nip": "3506164503950002", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Penata Layanan Operasional", "unit": "Tata Usaha & Kepegawaian"},
            {"nama": "Vivi Juni Mega A, S.Tr.Keb", "nip": "3506214506950001", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Anieta Yuni Purnawati, Amd.Keb", "nip": "3506215706900001", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/3/2024", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Slamet Riadi", "nip": "3506212005790003", "gol": "PPPK-V", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Operator Layanan Operasional", "unit": "Tata Usaha & Kepegawaian"},
            {"nama": "Anita Sumariati", "nip": "3506214101850002", "gol": "KONTRAK", "jenis": "-", "tmt": "-", "jabatan": "KEBERSIHAN", "unit": "Tata Usaha & Kebersihan"},
            {"nama": "Mimin Asmawati", "nip": "3506215707790002", "gol": "KONTRAK", "jenis": "-", "tmt": "-", "jabatan": "KEBERSIHAN", "unit": "Tata Usaha & Kebersihan"},
            {"nama": "Fitria Indriyani", "nip": "3506215502970001", "gol": "PPPK-V", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Operator Layanan Operasional", "unit": "Tata Usaha & Kepegawaian"},
            {"nama": "Cendy Santia KS, Amd AK", "nip": "3506154409920001", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Pranata Labkes Terampil", "unit": "Laboratorium Kesehatan"},
            {"nama": "Mistiani Saputri, Amd Kom", "nip": "3506266204980003", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Pengelola Layanan Operasional", "unit": "Tata Usaha & Kepegawaian"},
            {"nama": "Rani Rosita , Amd Keb", "nip": "3506265409920003", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Rise Nisa' Meiula Naaifah", "nip": "3506164105000001", "gol": "PPPK-VII", "jenis": "PPPK-PW", "tmt": "11/1/2025", "jabatan": "Perekam Medis Terampil", "unit": "Rekam Medis & Pendaftaran"},
            {"nama": "Shalikul Hadi, SKM", "nip": "3506161109000001", "gol": "KONTRAK", "jenis": "-", "tmt": "-", "jabatan": "PROMKES", "unit": "Promkes & Pemberdayaan"},
            {"nama": "MUSTAINUL HABIBI", "nip": "19871201 202421 1 018", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/3/2024", "jabatan": "Perekam Medis Terampil", "unit": "Rekam Medis & Pendaftaran"},
            {"nama": "GALIH CATUR AJI SETIAWAN", "nip": "19930220 202421 1 005", "gol": "PPPK-X", "jenis": "PPPK", "tmt": "1/3/2024", "jabatan": "Dokter Ahli Pertama", "unit": "UGD & Rawat Inap"},
            {"nama": "BINTI KHOTIMATUL MUNAWAROH", "nip": "19970129 202421 2 022", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/3/2024", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "VIRDA NILAYANTI", "nip": "199906292024212023", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/3/2024", "jabatan": "Perawat Terampil", "unit": "UGD & Rawat Inap"},
            {"nama": "DELLA ANANDANI HAREFA", "nip": "19950224 202421 2 013", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/3/2024", "jabatan": "Perawat Terampil", "unit": "UGD & Rawat Inap"},
            {"nama": "FENIA ELDIANA", "nip": "19970225 202521 2 007", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/3/2025", "jabatan": "Pranata Labkes Terampil", "unit": "Laboratorium Kesehatan"},
            {"nama": "Aide Bagus Lutfi Zakaria,A.Md.Kep", "nip": "3518071503890005", "gol": "KONTRAK", "jenis": "KONTRAK", "tmt": "-", "jabatan": "Perawat Terampil", "unit": "UGD & Rawat Inap"},
            {"nama": "Wenly Novi Newanda,A.Md.Keb", "nip": "3506114111970003", "gol": "KONTRAK", "jenis": "KONTRAK", "tmt": "-", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Dwi Lestari,A.Md.Keb", "nip": "3506216909940001", "gol": "KONTRAK", "jenis": "KONTRAK", "tmt": "-", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "ika Bintari, A.Md.Keb", "nip": "19910519 202521 2 033", "gol": "PPPK-VII", "jenis": "PPPK", "tmt": "1/9/2025", "jabatan": "Bidan Terampil", "unit": "KIA / KB"},
            {"nama": "Ronal Ardianto", "nip": "3506210301020001", "gol": "KONTRAK", "jenis": "KONTRAK", "tmt": "-", "jabatan": "CS", "unit": "Tata Usaha & Kebersihan"},
            {"nama": "Rinda Agustina,Amd.Gizi", "nip": "3506216208960001", "gol": "KONTRAK", "jenis": "KONTRAK", "tmt": "-", "jabatan": "Nutrisionis Terampil", "unit": "Pelayanan Gizi"},
            {"nama": "Yogi Satrio Lelono", "nip": "3506210306030002", "gol": "KONTRAK", "jenis": "KONTRAK", "tmt": "-", "jabatan": "Perawat Terampil", "unit": "UGD & Rawat Inap"}
        ]

        pegawais = []
        for item in pegawai_list_data:
            p = Pegawai(
                nip=item["nip"],
                nama_pegawai=item["nama"],
                golongan=item["gol"],
                jenis_asn=item["jenis"],
                tmt_gol=item["tmt"],
                jabatan=item["jabatan"],
                unit_tugas=item.get("unit", "Puskesmas")
            )
            db.session.add(p)
            pegawais.append(p)

        db.session.commit()

        print("Menambahkan Sub-Unit / Poli Puskesmas DUK...")
        subunits = [
            SubUnit(nama_subunit="Gudang Farmasi & Apotek", penanggung_jawab="Daril Rahmatullah, S. Farm.", keterangan="Pelayanan Kefarmasian & Penyerahan Obat (Apoteker Ahli Madya)"),
            SubUnit(nama_subunit="Poli Umum", penanggung_jawab="dr. Rizky Rachmat Kurniawan", keterangan="Pelayanan Kesehatan Dewasa & Lansia (Dokter Pertama)"),
            SubUnit(nama_subunit="Poli Gigi & Mulut", penanggung_jawab="drg. Putri Emyta Sari", keterangan="Pelayanan Kesehatan Gigi & Mulut (Dokter Gigi Ahli Madya)"),
            SubUnit(nama_subunit="KIA / KB", penanggung_jawab="Yuanendah, SST.", keterangan="Pelayanan Ibu Hamil, Bersalin, Nifas, Bayi & KB (Bidan Ahli Muda)"),
            SubUnit(nama_subunit="UGD & Rawat Inap", penanggung_jawab="dr. Galih Catur Aji Setiawan / Setya Budi, Amd., Kep", keterangan="Unit Gawat Darurat 24 Jam & Rawat Inap (Perawat Ahli Pertama)"),
            SubUnit(nama_subunit="Laboratorium Kesehatan", penanggung_jawab="Fitri Ariani Isnaningtyas, Amd.AK", keterangan="Pelayanan Labkesmas & Pemeriksaan Darah (Pranata Labkes Penyelia)"),
            SubUnit(nama_subunit="Pelayanan Gizi", penanggung_jawab="Luluk Listyaningsih, AMG", keterangan="Pelayanan Nutrisi & Konseling Gizi (Nutrisionis Penyelia)"),
            SubUnit(nama_subunit="Kesehatan Lingkungan", penanggung_jawab="Novia Anjarwati, Amd. Kes", keterangan="Sanitarian Pelaksana & Pengawasan Kesling"),
            SubUnit(nama_subunit="Rekam Medis & Pendaftaran", penanggung_jawab="MUSTAINUL HABIBI", keterangan="Loket Pendaftaran & Pengelolaan SIMPUS Digital (Perekam Medis)"),
            SubUnit(nama_subunit="Tata Usaha & Kepegawaian", penanggung_jawab="Sito Luncono Setio Utomo", keterangan="Pengadministrasi Kepegawaian, Sarpras & Aset Puskesmas"),
            SubUnit(nama_subunit="Promkes & Pemberdayaan", penanggung_jawab="Shalikul Hadi, SKM", keterangan="Promosi Kesehatan & Pemberdayaan Masyarakat"),
            SubUnit(nama_subunit="Pustu Melati", penanggung_jawab="Bidan Desa / Jejaring Pustu", keterangan="Puskesmas Pembantu Desa Melati"),
            SubUnit(nama_subunit="Poskesdes Sejahtera", penanggung_jawab="Bidan Poskesdes", keterangan="Pos Kesehatan Desa Jejaring")
        ]
        db.session.add_all(subunits)
        db.session.commit()

        print("Menambahkan Master Obat Formularium Puskesmas (Bulk Data)...")
        obats_data = [
            # OBAT ORAL
            {"kode": "OBT-001", "nama": "Paracetamol Tablet 500 mg", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 150.0, "min": 200},
            {"kode": "OBT-002", "nama": "Amoxicillin Kaplet 500 mg", "sediaan": "Kaplet", "satuan": "Kaplet", "kategori": "Obat Oral", "harga": 450.0, "min": 150},
            {"kode": "OBT-003", "nama": "Chlorpheniramine (CTM) 4 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 80.0, "min": 100},
            {"kode": "OBT-004", "nama": "Dexamethasone 0.5 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 120.0, "min": 100},
            {"kode": "OBT-005", "nama": "Antasida Doen Tablet Kunyah", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 200.0, "min": 150},
            {"kode": "OBT-006", "nama": "Ciprofloxacin 500 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 600.0, "min": 80},
            {"kode": "OBT-007", "nama": "Amlodipine 5 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 250.0, "min": 120},
            {"kode": "OBT-008", "nama": "Salbutamol 2 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 180.0, "min": 80},
            {"kode": "OBT-009", "nama": "Metformin 500 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 300.0, "min": 150},
            {"kode": "OBT-010", "nama": "Vitamin C (Asam Askorbat) 50 mg", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 100.0, "min": 200},
            {"kode": "OBT-011", "nama": "Cetirizine 10 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 350.0, "min": 100},
            {"kode": "OBT-012", "nama": "Ibuprofen 400 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 400.0, "min": 100},
            {"kode": "OBT-013", "nama": "Allopurinol 100 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 350.0, "min": 100},
            {"kode": "OBT-014", "nama": "Asam Mefenamat 500 mg Kaplet", "sediaan": "Kaplet", "satuan": "Kaplet", "kategori": "Obat Oral", "harga": 400.0, "min": 120},
            {"kode": "OBT-015", "nama": "Captopril 25 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 200.0, "min": 100},
            {"kode": "OBT-016", "nama": "Simvastatin 10 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 500.0, "min": 100},
            {"kode": "OBT-017", "nama": "Omeprazole 20 mg Kapsul", "sediaan": "Kapsul", "satuan": "Kapsul", "kategori": "Obat Oral", "harga": 600.0, "min": 100},
            {"kode": "OBT-018", "nama": "Lansoprazole 30 mg Kapsul", "sediaan": "Kapsul", "satuan": "Kapsul", "kategori": "Obat Oral", "harga": 800.0, "min": 80},
            {"kode": "OBT-019", "nama": "Domperidone 10 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 300.0, "min": 80},
            {"kode": "OBT-020", "nama": "Glibenclamide 5 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 150.0, "min": 100},
            {"kode": "OBT-021", "nama": "Loratadine 10 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 350.0, "min": 80},
            {"kode": "OBT-022", "nama": "Vitamin B Complex Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 100.0, "min": 200},
            {"kode": "OBT-023", "nama": "Vitamin B6 (Pyridoxine) 10 mg", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 100.0, "min": 150},
            {"kode": "OBT-024", "nama": "Vitamin B12 (Cyanocobalamin) 50 mcg", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 100.0, "min": 150},
            {"kode": "OBT-025", "nama": "Zinc Dispersible 20 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 450.0, "min": 100},
            {"kode": "OBT-026", "nama": "Calcium Lactate 500 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 200.0, "min": 150},
            {"kode": "OBT-027", "nama": "Kotrimoksazol 480 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 350.0, "min": 100},
            {"kode": "OBT-028", "nama": "Ambroxol 30 mg Tab", "sediaan": "Tablet", "satuan": "Tablet", "kategori": "Obat Oral", "harga": 250.0, "min": 120},
            {"kode": "OBT-029", "nama": "Oralit Garam Hidrasi Sachet", "sediaan": "Serbuk", "satuan": "Sachet", "kategori": "Obat Oral", "harga": 600.0, "min": 150},

            # OBAT SUNTIK / INJEKSI
            {"kode": "OBT-030", "nama": "Lidocain Injeksi 2% Ampul 2 ml", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 2500.0, "min": 50},
            {"kode": "OBT-031", "nama": "Epinefrin (Adrenalin) Inj 0.1% Ampul", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 4500.0, "min": 20},
            {"kode": "OBT-032", "nama": "Atropin Sulfat Inj 0.25 mg Ampul", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 3000.0, "min": 20},
            {"kode": "OBT-033", "nama": "Dexamethasone Inj 5 mg/ml Ampul", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 3500.0, "min": 50},
            {"kode": "OBT-034", "nama": "Ranitidin Inj 25 mg/ml Ampul", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 4000.0, "min": 50},
            {"kode": "OBT-035", "nama": "Oksitosin Inj 10 UI Ampul", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 5000.0, "min": 30},
            {"kode": "OBT-036", "nama": "Phytomenadione (Vit K1) Inj 10 mg", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 6000.0, "min": 30},
            {"kode": "OBT-037", "nama": "Diphenhydramine Inj 10 mg/ml", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 3500.0, "min": 30},
            {"kode": "OBT-038", "nama": "Ondansetron Inj 4 mg/2 ml", "sediaan": "Injeksi", "satuan": "Ampul", "kategori": "Obat Injeksi", "harga": 7000.0, "min": 30},
            {"kode": "OBT-039", "nama": "Ceftriaxone Inj 1 gram Vial", "sediaan": "Injeksi", "satuan": "Vial", "kategori": "Obat Injeksi", "harga": 15000.0, "min": 20},
            {"kode": "OBT-040", "nama": "Aqua Pro Injeksi 25 ml Flakon", "sediaan": "Injeksi", "satuan": "Flakon", "kategori": "Obat Injeksi", "harga": 3000.0, "min": 40},

            # OBAT LUAR / SALEP & TETES
            {"kode": "OBT-041", "nama": "Salep 2-4 Salep Kulit Pot 30g", "sediaan": "Salep", "satuan": "Pot", "kategori": "Obat Luar", "harga": 3500.0, "min": 30},
            {"kode": "OBT-042", "nama": "Salep Hydrocortisone 2.5% Tube 5g", "sediaan": "Salep", "satuan": "Tube", "kategori": "Obat Luar", "harga": 4500.0, "min": 30},
            {"kode": "OBT-043", "nama": "Salep Gentamicin 0.1% Tube 5g", "sediaan": "Salep", "satuan": "Tube", "kategori": "Obat Luar", "harga": 5000.0, "min": 30},
            {"kode": "OBT-044", "nama": "Tetes Mata Chloramphenicol 0.5% 5ml", "sediaan": "Tetes Mata", "satuan": "Botol", "kategori": "Obat Luar", "harga": 6000.0, "min": 25},
            {"kode": "OBT-045", "nama": "Tetes Telinga Chloramphenicol 3% 5ml", "sediaan": "Tetes Telinga", "satuan": "Botol", "kategori": "Obat Luar", "harga": 6500.0, "min": 25},
            {"kode": "OBT-046", "nama": "Salep Mata Oxytetracycline 1% 3.5g", "sediaan": "Salep Mata", "satuan": "Tube", "kategori": "Obat Luar", "harga": 5500.0, "min": 25},
            {"kode": "OBT-047", "nama": "Salep Ketoconazole 2% Tube 10g", "sediaan": "Salep", "satuan": "Tube", "kategori": "Obat Luar", "harga": 7500.0, "min": 25},

            # SIRUP & DROPS
            {"kode": "OBT-048", "nama": "Obat Batuk Hitam (OBH) Sirup 100 ml", "sediaan": "Sirup", "satuan": "Botol", "kategori": "Sirup & Drops", "harga": 4500.0, "min": 30},
            {"kode": "OBT-049", "nama": "Paracetamol Sirup 120 mg/5ml 60 ml", "sediaan": "Sirup", "satuan": "Botol", "kategori": "Sirup & Drops", "harga": 5000.0, "min": 40},
            {"kode": "OBT-050", "nama": "Amoxicillin Sirup Kering 125 mg 60 ml", "sediaan": "Sirup", "satuan": "Botol", "kategori": "Sirup & Drops", "harga": 6500.0, "min": 40},
            {"kode": "OBT-051", "nama": "Antasida Doen Sirup 60 ml", "sediaan": "Sirup", "satuan": "Botol", "kategori": "Sirup & Drops", "harga": 5500.0, "min": 30},
            {"kode": "OBT-052", "nama": "Zinc Sirup 20 mg/5ml 60 ml", "sediaan": "Sirup", "satuan": "Botol", "kategori": "Sirup & Drops", "harga": 7000.0, "min": 30},
            {"kode": "OBT-053", "nama": "Ibuprofen Sirup 100 mg/5ml 60 ml", "sediaan": "Sirup", "satuan": "Botol", "kategori": "Sirup & Drops", "harga": 6000.0, "min": 30},

            # BMHP & ALKES
            {"kode": "OBT-054", "nama": "Spuit Disposable 1 cc Steril", "sediaan": "BMHP", "satuan": "Pcs", "kategori": "BMHP", "harga": 1000.0, "min": 100},
            {"kode": "OBT-055", "nama": "Spuit Disposable 3 cc Steril", "sediaan": "BMHP", "satuan": "Pcs", "kategori": "BMHP", "harga": 1200.0, "min": 150},
            {"kode": "OBT-056", "nama": "Spuit Disposable 5 cc Steril", "sediaan": "BMHP", "satuan": "Pcs", "kategori": "BMHP", "harga": 1500.0, "min": 100},
            {"kode": "OBT-057", "nama": "Spuit Disposable 10 cc Steril", "sediaan": "BMHP", "satuan": "Pcs", "kategori": "BMHP", "harga": 2000.0, "min": 80},
            {"kode": "OBT-058", "nama": "IV Catheter / Abocath No 20G", "sediaan": "BMHP", "satuan": "Pcs", "kategori": "BMHP", "harga": 8000.0, "min": 50},
            {"kode": "OBT-059", "nama": "Infuset Dewasa / Macro Set", "sediaan": "BMHP", "satuan": "Pcs", "kategori": "BMHP", "harga": 9000.0, "min": 50},
            {"kode": "OBT-060", "nama": "Handscoon / Sarung Tangan Steril M Box", "sediaan": "BMHP", "satuan": "Box", "kategori": "BMHP", "harga": 45000.0, "min": 10},
            {"kode": "OBT-061", "nama": "Masker Medis 3-Ply Box", "sediaan": "BMHP", "satuan": "Box", "kategori": "BMHP", "harga": 25000.0, "min": 15},
            {"kode": "OBT-062", "nama": "Kassa Steril 16x16 cm Box", "sediaan": "BMHP", "satuan": "Box", "kategori": "BMHP", "harga": 8500.0, "min": 20},
            {"kode": "OBT-063", "nama": "Alkohol 70% Botol 100 ml", "sediaan": "BMHP", "satuan": "Botol", "kategori": "BMHP", "harga": 6000.0, "min": 30},
            {"kode": "OBT-064", "nama": "Povidone Iodine 10% Botol 60 ml", "sediaan": "BMHP", "satuan": "Botol", "kategori": "BMHP", "harga": 8000.0, "min": 30}
        ]

        obats = []
        for o in obats_data:
            obat = Obat(
                kode_obat=o["kode"],
                nama_obat=o["nama"],
                bentuk_sediaan=o["sediaan"],
                satuan=o["satuan"],
                kategori=o["kategori"],
                harga_satuan=o["harga"],
                stok_minimum=o["min"]
            )
            db.session.add(obat)
            obats.append(obat)
        
        db.session.commit()

        print("Menambahkan Batch Obat & Stok Fisik (FEFO Setup)...")
        today = date.today()
        batches = []

        for idx, o in enumerate(obats):
            # Batch 1 (Near Expired / FEFO Priority)
            b1 = BatchObat(
                obat_id=o.id,
                no_batch=f"BCH-{o.kode_obat}-001",
                expired_date=today + timedelta(days=30 + (idx * 5) % 60),
                stok_awal=300 + (idx * 20) % 400,
                stok_sekarang=100 + (idx * 15) % 200,
                sumber_dana="APBD" if idx % 2 == 0 else "DAK"
            )
            # Batch 2 (Longer Expired)
            b2 = BatchObat(
                obat_id=o.id,
                no_batch=f"BCH-{o.kode_obat}-002",
                expired_date=today + timedelta(days=365 + (idx * 10) % 300),
                stok_awal=800 + (idx * 50) % 1000,
                stok_sekarang=500 + (idx * 30) % 800,
                sumber_dana="APBD"
            )
            batches.extend([b1, b2])

        db.session.add_all(batches)
        db.session.commit()

        print("Menambahkan Transaksi Masuk SBBK dari GFK...")
        tm = TransaksiMasuk(
            no_sbbk="SBBK/GFK/2026/08/001",
            sumber_penerimaan="Gudang Farmasi Kabupaten",
            tanggal_terima=today - timedelta(days=12),
            keterangan="Penerimaan Alokasi Obat Rutin Puskesmas Bulan Agustus"
        )
        db.session.add(tm)
        db.session.flush()

        for idx in range(10):
            tm_item = TransaksiMasukItem(
                transaksi_masuk_id=tm.id,
                obat_id=obats[idx].id,
                batch_id=batches[idx * 2 + 1].id,
                jumlah=500 + idx * 50,
                harga_satuan=obats[idx].harga_satuan
            )
            db.session.add(tm_item)
        db.session.commit()

        print("Menambahkan Transaksi Keluar ke Sub-Unit / Poli...")
        tk1 = TransaksiKeluar(
            no_penyerahan="PENYERAHAN/POLI/2026/08/001",
            subunit_id=subunits[0].id, # Poli Umum
            tanggal_keluar=today - timedelta(days=7),
            keterangan="Distribusi Mingguan Poli Umum"
        )
        tk2 = TransaksiKeluar(
            no_penyerahan="PENYERAHAN/POLI/2026/08/002",
            subunit_id=subunits[2].id, # KIA / KB
            tanggal_keluar=today - timedelta(days=3),
            keterangan="Distribusi Rutin KIA / KB"
        )
        db.session.add_all([tk1, tk2])
        db.session.flush()

        for idx in range(6):
            tk_item1 = TransaksiKeluarItem(
                transaksi_keluar_id=tk1.id,
                obat_id=obats[idx].id,
                batch_id=batches[idx * 2].id,
                jumlah=50 + idx * 10
            )
            tk_item2 = TransaksiKeluarItem(
                transaksi_keluar_id=tk2.id,
                obat_id=obats[idx + 6].id,
                batch_id=batches[(idx + 6) * 2].id,
                jumlah=30 + idx * 5
            )
            db.session.add_all([tk_item1, tk_item2])

        db.session.commit()

        print("Menghasilkan Dokumen LPLPO Otomatis Bulan Ini...")
        generate_lplpo_periode(today.month, today.year, "Puskesmas Sehat Utama")

        print("[OK] Bulk Seeding Berhasil! Database siap dengan 64 item obat Formularium Puskesmas.")

if __name__ == '__main__':
    seed_database()
