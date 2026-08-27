from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

class Obat(BaseModel):
    __tablename__ = 'obat'
    
    id = db.Column(db.Integer, primary_key=True)
    kode_obat = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nama_obat = db.Column(db.String(150), nullable=False)
    bentuk_sediaan = db.Column(db.String(50), default='Tablet')
    satuan = db.Column(db.String(30), default='Tablet')
    kategori = db.Column(db.String(50), default='Generik')
    harga_satuan = db.Column(db.Float, default=0.0)
    stok_minimum = db.Column(db.Integer, default=10)
    buffer_percent = db.Column(db.Float, default=0.20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    batches = db.relationship('BatchObat', backref='obat', lazy=True, cascade="all, delete-orphan")

    @property
    def total_stok(self):
        return sum(batch.stok_sekarang for batch in self.batches if batch.stok_sekarang > 0)

    @property
    def batch_terdekat_ed(self):
        active_batches = [b for b in self.batches if b.stok_sekarang > 0]
        if not active_batches:
            return None
        return min(active_batches, key=lambda b: b.expired_date)

    def to_dict(self):
        return {
            'id': self.id,
            'kode_obat': self.kode_obat,
            'nama_obat': self.nama_obat,
            'bentuk_sediaan': self.bentuk_sediaan,
            'satuan': self.satuan,
            'kategori': self.kategori,
            'harga_satuan': self.harga_satuan,
            'total_stok': self.total_stok,
            'stok_minimum': self.stok_minimum
        }

class SubUnit(BaseModel):
    __tablename__ = 'sub_unit'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_subunit = db.Column(db.String(100), nullable=False, unique=True)
    penanggung_jawab = db.Column(db.String(100))
    keterangan = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transaksi_keluar = db.relationship('TransaksiKeluar', backref='subunit', lazy=True)

class BatchObat(BaseModel):
    __tablename__ = 'batch_obat'
    
    id = db.Column(db.Integer, primary_key=True)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    no_batch = db.Column(db.String(50), nullable=False)
    expired_date = db.Column(db.Date, nullable=False)
    stok_awal = db.Column(db.Integer, default=0)
    stok_sekarang = db.Column(db.Integer, default=0)
    sumber_dana = db.Column(db.String(50), default='APBD')
    harga_batch = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def days_until_expired(self):
        if not self.expired_date:
            return 9999
        return (self.expired_date - date.today()).days

    @property
    def is_expired(self):
        return self.days_until_expired <= 0

    @property
    def is_near_expired(self):
        return 0 < self.days_until_expired <= 90

class TransaksiMasuk(BaseModel):
    __tablename__ = 'transaksi_masuk'
    
    id = db.Column(db.Integer, primary_key=True)
    no_sbbk = db.Column(db.String(50), nullable=False)
    sumber_penerimaan = db.Column(db.String(100), default='Gudang Farmasi Kabupaten')
    tanggal_terima = db.Column(db.Date, nullable=False, default=date.today)
    keterangan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('TransaksiMasukItem', backref='transaksi', lazy=True, cascade="all, delete-orphan")

class TransaksiMasukItem(BaseModel):
    __tablename__ = 'transaksi_masuk_item'
    
    id = db.Column(db.Integer, primary_key=True)
    transaksi_masuk_id = db.Column(db.Integer, db.ForeignKey('transaksi_masuk.id'), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_obat.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Float, default=0.0)

    obat = db.relationship('Obat')
    batch = db.relationship('BatchObat')

class TransaksiKeluar(BaseModel):
    __tablename__ = 'transaksi_keluar'
    
    id = db.Column(db.Integer, primary_key=True)
    no_penyerahan = db.Column(db.String(50), nullable=False)
    subunit_id = db.Column(db.Integer, db.ForeignKey('sub_unit.id'), nullable=False)
    tanggal_keluar = db.Column(db.Date, nullable=False, default=date.today)
    keterangan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('TransaksiKeluarItem', backref='transaksi', lazy=True, cascade="all, delete-orphan")

class TransaksiKeluarItem(BaseModel):
    __tablename__ = 'transaksi_keluar_item'
    
    id = db.Column(db.Integer, primary_key=True)
    transaksi_keluar_id = db.Column(db.Integer, db.ForeignKey('transaksi_keluar.id'), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_obat.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)

    obat = db.relationship('Obat')
    batch = db.relationship('BatchObat')

class LPLPO(BaseModel):
    __tablename__ = 'lplpo'
    
    id = db.Column(db.Integer, primary_key=True)
    bulan = db.Column(db.Integer, nullable=False)  # 1 - 12
    tahun = db.Column(db.Integer, nullable=False)  # e.g. 2026
    nama_puskesmas = db.Column(db.String(100), default='Puskesmas Kunjang')
    tanggal_laporan = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='Draft')  # Draft, Final
    keterangan = db.Column(db.Text)
    kepala_puskesmas = db.Column(db.String(100), default='dr. Durotun Nafisa, M.H')
    nip_kepala = db.Column(db.String(30), default='19750423 200212 2 005')
    pengelola_obat = db.Column(db.String(100), default='Daril Rahmatullah, S.Farm.Apt')
    nip_pengelola = db.Column(db.String(30), default='19810704 200901 1 004')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('LPLPOItem', backref='lplpo', lazy=True, cascade="all, delete-orphan")

    @property
    def nama_bulan(self):
        nama_bulan_list = [
            '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        if 1 <= self.bulan <= 12:
            return nama_bulan_list[self.bulan]
        return str(self.bulan)

class LPLPOItem(BaseModel):
    __tablename__ = 'lplpo_item'
    
    id = db.Column(db.Integer, primary_key=True)
    lplpo_id = db.Column(db.Integer, db.ForeignKey('lplpo.id'), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    
    stok_awal = db.Column(db.Integer, default=0)
    penerimaan = db.Column(db.Integer, default=0)
    persediaan = db.Column(db.Integer, default=0)  # stok_awal + penerimaan
    pemakaian = db.Column(db.Integer, default=0)
    sisa_stok = db.Column(db.Integer, default=0)   # persediaan - pemakaian
    stok_optimum = db.Column(db.Integer, default=0)
    permintaan = db.Column(db.Integer, default=0)
    pemberian = db.Column(db.Integer, default=0)

    obat = db.relationship('Obat')

class Pegawai(BaseModel):
    __tablename__ = 'pegawai'

    id = db.Column(db.Integer, primary_key=True)
    nip = db.Column(db.String(50), unique=True, nullable=False)
    nama_pegawai = db.Column(db.String(150), nullable=False)
    golongan = db.Column(db.String(30))
    jenis_asn = db.Column(db.String(30))
    tmt_gol = db.Column(db.String(30))
    jabatan = db.Column(db.String(150), default='Staf Puskesmas')
    unit_tugas = db.Column(db.String(100), default='Puskesmas')
    klaster = db.Column(db.String(100))
    jabatan_organisasi = db.Column(db.String(150))
    no_hp = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PenyesuaianStok(BaseModel):
    __tablename__ = 'penyesuaian_stok'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_obat.id'), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    jenis_penyesuaian = db.Column(db.String(20), nullable=False)  # 'Pengurangan' atau 'Penambahan'
    kategori_alasan = db.Column(db.String(50), nullable=False)   # 'Rusak', 'Hilang', 'Expired (ED)', 'Koreksi Fisik', 'Lain-lain'
    stok_sebelum = db.Column(db.Integer, nullable=False)
    jumlah_penyesuaian = db.Column(db.Integer, nullable=False)
    stok_setelah = db.Column(db.Integer, nullable=False)
    tanggal_penyesuaian = db.Column(db.Date, default=date.today)
    keterangan = db.Column(db.Text)
    petugas = db.Column(db.String(100), default='Daril Rahmatullah, S. Farm.')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    batch = db.relationship('BatchObat')
    obat = db.relationship('Obat')

class StokOpname(BaseModel):
    __tablename__ = 'stok_opname'

    id = db.Column(db.Integer, primary_key=True)
    no_opname = db.Column(db.String(50), unique=True, nullable=False)
    tanggal_opname = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='Draft')  # Draft, Final
    petugas_opname = db.Column(db.String(100), default='Daril Rahmatullah, S. Farm.')
    penanggung_jawab = db.Column(db.String(100), default='dr. Durotun Nafisa, M.H')
    keterangan = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('StokOpnameItem', backref='stok_opname', lazy=True, cascade="all, delete-orphan")

class StokOpnameItem(BaseModel):
    __tablename__ = 'stok_opname_item'

    id = db.Column(db.Integer, primary_key=True)
    stok_opname_id = db.Column(db.Integer, db.ForeignKey('stok_opname.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch_obat.id'), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    stok_sistem = db.Column(db.Integer, default=0)
    stok_fisik = db.Column(db.Integer, default=0)
    selisih = db.Column(db.Integer, default=0) # stok_fisik - stok_sistem
    keterangan = db.Column(db.String(200))

    batch = db.relationship('BatchObat')
    obat = db.relationship('Obat')




