from flask import Blueprint, render_template
from app.models import db, Pegawai

organisasi_bp = Blueprint('organisasi', __name__, url_prefix='/organisasi')

@organisasi_bp.route('/')
def index():
    # Mengambil pegawai berdasarkan posisi di Bagan Organisasi
    kepala = Pegawai.query.filter(Pegawai.nama_pegawai.ilike('%Durotun Nafisa%')).first()
    
    # Structure Klaster 1 s/d 5
    klasters = [
        {
            "id": 1,
            "nama": "Klaster 1 Manajemen",
            "pj": "Daril Rahmatullah, S.Farm.Apt",
            "koordinators": [
                {"tugas": "Manajemen Inti Puskesmas", "nama": "Desi Natalia, SST"},
                {"tugas": "Manajemen Arsip", "nama": "Mistiani Saputri"},
                {"tugas": "Manajemen Sumber Daya Manusia", "nama": "Sito Luncono Setio Utomo"},
                {"tugas": "Manajemen Sarpras & Perbekalan Kesehatan", "nama": "Novia Anjarwati, A.Md.Kes"},
                {"tugas": "Manajemen Mutu Pelayanan", "nama": "drg. Putri Emyta L"},
                {"tugas": "Manajemen Keuangan dan Aset/EMD", "nama": "Fitri Ariani I, A.Md.AK"},
                {"tugas": "Manajemen Sistem Informasi Digital", "nama": "Musta'inul Habibi, A.Md.RMIK"},
                {"tugas": "Manajemen Jejaring", "nama": "Yuanendah, SST"},
                {"tugas": "Manajemen Pemberdayaan Masyarakat", "nama": "Shalikul Hadi, SKM"}
            ]
        },
        {
            "id": 2,
            "nama": "Klaster 2 Ibu dan Anak",
            "pj": "Yuanendah, SST",
            "koordinators": [
                {"tugas": "Pelayanan Kesehatan Ibu Hamil, Bersalin, dan Nifas", "nama": "Enny Nur Hayati, A.Md.Keb"},
                {"tugas": "Pelayanan Kesehatan Bayi, Balita dan Anak Prasekolah", "nama": "Estu Rahayuningtyas, A.Md.Keb"},
                {"tugas": "Pelayanan Kesehatan Anak Usia Sekolah dan Remaja", "nama": "Rinda Ari P, A.Md.KG"}
            ]
        },
        {
            "id": 3,
            "nama": "Klaster 3 Dewasa dan Lansia",
            "pj": "drg. Putri Emyta L",
            "koordinators": [
                {"tugas": "Pelayanan Kesehatan Usia Produktif", "nama": "Nuryana Vidya C, A.Md.Kep"},
                {"tugas": "Pelayanan Kesehatan Lanjut Usia", "nama": "Supatemi, A.Md.Keb"}
            ]
        },
        {
            "id": 4,
            "nama": "Klaster 4 Penanggulangan Penyakit",
            "pj": "Setya Budi, S.Kep.Ners",
            "koordinators": [
                {"tugas": "Survailans dan Respon Penyakit Menular", "nama": "Mey Idayati, A.Md.Kep"},
                {"tugas": "Survailans Kesehatan Lingkungan", "nama": "Novia Anjarwati, A.Md.Kes"}
            ]
        },
        {
            "id": 5,
            "nama": "Klaster 5 Lintas Klaster",
            "pj": "Luluk Listyaningsih, A.Md.Gz",
            "koordinators": [
                {"tugas": "Pelayanan Kesehatan Gigi dan Mulut", "nama": "drg. Putri Emyta L"},
                {"tugas": "Pelayanan Kegawatdaruratan", "nama": "dr. Rizky Rachmat K"},
                {"tugas": "Pelayanan Labkesmas", "nama": "Fitri Ariani I, A.Md.AK"},
                {"tugas": "Pelayanan Kefarmasian", "nama": "Daril Rahmatullah, S.Farm.Apt"},
                {"tugas": "Pelayanan Penanggulangan Krisis Kesehatan", "nama": "Virda Nilayanti, A.Md.Kep"},
                {"tugas": "Pelayanan Rawat Inap", "nama": "dr. Galih Catur Aji Setiawan"},
                {"tugas": "Pelayanan Gizi", "nama": "Luluk Listyaningsih, A.Md.Gz"}
            ]
        }
    ]

    return render_template('organisasi/index.html', kepala=kepala, klasters=klasters)
