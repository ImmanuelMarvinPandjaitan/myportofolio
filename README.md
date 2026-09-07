# My Portofolio

Nama : Immanuel Marvin Pandjaitan

NPM : 2506623881

Kelas : PBP D

## Deskripsi Proyek

Website portofolio pribadi yang dibangun pakai Django, tapi untuk saat ini
(Tutorial 01 & Individual Assignment 1) baru murni HTML5 + CSS3 lewat
template Django (belum pakai database / arsitektur MVT). Halaman berisi
section "About Me" dengan data diri, dan section "Skills" yang baru
ditambahkan di Tugas 1.

## Cara Menjalankan

1. Aktifkan virtual environment (`env`).
2. Install dependencies: `pip install -r requirements.txt`
3. Jalankan server: `python manage.py runserver`
4. Buka `http://127.0.0.1:8000/` di browser.

## Individual Assignment 1 - Static Web with HTML5 and CSS3

### Perubahan yang ditambahkan
- Section baru **Skills** di `templates/index.html` (3 item: Python, Django,
  HTML5 & CSS3), pakai elemen `<article>` untuk tiap card.
- Styling khusus di `static/css/style.css`: layout CSS Grid 3 kolom
  (`.skills-grid`), efek hover naik di kartu (`.skill-card:hover`), dan
  media query supaya jadi 1 kolom di layar mobile.

### Pertanyaan Reflektif

1. **Elemen semantik HTML5** — Ya, saya pakai beberapa elemen semantik: <header> dan <nav> untuk navigasi, <main> untuk konten inti, <section> untuk tiga blok utama (Profile, Skills, Pendidikan), <article> untuk tiap item di dalam Skills dan Pendidikan, serta <dl>/<dt>/<dd> untuk pasangan data NPM-Program. Saya sengaja bedakan <section> dan <article>: <section> saya pakai untuk pengelompokan tematik (semua yang berhubungan dengan "Skills" jadi satu section), sedangkan <article> saya pakai untuk tiap card di dalamnya karena satu skill card atau satu baris riwayat pendidikan tetap punya makna walau berdiri sendiri, dipisah dari section-nya — beda dengan <div> yang sifatnya cuma pembungkus tanpa makna semantik.

Saya sengaja tidak memakai <aside> di halaman ini, karena semua konten yang saya tampilkan sifatnya inti (bukan pelengkap seperti sidebar iklan atau widget tambahan) — kalau saya paksakan pakai <aside> hanya supaya "terlihat lengkap elemen semantiknya", itu justru salah kaprah karena <aside> seharusnya menandai konten yang tidak esensial terhadap alur utama. Keputusan untuk tidak memakai suatu elemen semantik itu sendiri saya anggap bagian dari desain semantik yang benar, bukan kekurangan.


2. **Tantangan responsive** — Tantangan utamanya adalah saya punya tiga pola grid berbeda di satu halaman: .hero-grid pakai grid-template-areas 2 kolom untuk foto-identitas-detail, .skills-grid pakai repeat(2, 1fr) untuk kartu skill, dan .education-item pakai grid 2 kolom (tahun | detail) per baris. Ketiganya harus saya evaluasi satu per satu di breakpoint yang sama (600px), karena kalau saya samakan treatment-nya, hasilnya nggak konsisten — misalnya .education-item yang cuma 2 kolom sempit (tahun vs detail) sebenarnya sudah cukup pas di layar kecil kalau cuma di-stack, tapi .hero-grid yang isinya foto besar harus diprioritaskan urutan tampilnya (identity dulu, baru foto, baru detail) supaya foto nggak "mendorong" konten teks terlalu jauh ke bawah.

Satu keterbatasan yang saya sadari tapi belum saya perbaiki: .site-header nav saya isi 3 link (Profile, Skills, Pendidikan) tanpa flex-wrap, jadi di layar yang sangat sempit (di bawah ~360px) kemungkinan nav ini bisa mepet atau overflow. Untuk iterasi berikutnya saya perlu tambahkan flex-wrap: wrap atau ubah jadi hamburger menu di breakpoint mobile, tapi saat ini saya belum sempat uji di ukuran seextreme itu.


3. **Batasan static web** — Batasan paling terasa: semua konten Skills dan Pendidikan itu hardcoded langsung di index.html. Kalau saya mau nambah satu skill baru atau ganti riwayat pendidikan, saya harus edit HTML, commit, push, dan redeploy ulang ke PWS — dan dari pengalaman saya deploy Tutorial 01 kemarin, proses redeploy ini sempat menyebabkan halaman 502 sebentar karena migrasi database jalan duluan sebelum server aplikasi siap, meskipun untuk kasus static content sebenarnya nggak ada perubahan skema database sama sekali. Ini nunjukin salah satu inefisiensi nyata dari static web: perubahan konten sekecil apapun tetap butuh siklus deploy penuh.

Untuk iterasi selanjutnya, saya ingin memindahkan data Skills dan Pendidikan ini jadi model Django (Skill, Education) yang disimpan di database, supaya bisa ditambah/diubah lewat Django admin tanpa perlu sentuh kode maupun redeploy — sesuai arsitektur MVT yang akan dibahas di tutorial berikutnya.

### AI Disclosure

Saya menggunakan Claude untuk brainstorming struktur section Skills dan Riwayat Pendidikan, penulisan CSS Grid (`.skills-grid`, `.education-item`) beserta efek hover, penyesuaian responsive di media query, dan bantuan menyusun draft jawaban pertanyaan reflektif di atas — yang saya baca ulang dan sesuaikan dengan proses dan pengalaman saya sendiri sebelum submit. Untuk warna hover pada .skill-card dan breakpoint media query, saya tidak langsung pakai saran awal dari Claude — warna hover awal saya rasa kurang kontras dengan warna kartu, jadi saya sesuaikan sendiri, dan breakpoint yang awalnya disarankan di 768px saya ubah jadi 600px karena di HP saya sendiri layout-nya masih terlihat kepotong/terlalu sempit di lebar itu. Bagian konten (data skill, riwayat pendidikan, teks bio) saya isi sendiri sesuai data asli saya. Saya pahami tiap baris kode HTML/CSS yang dihasilkan sebelum di-commit.