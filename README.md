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

### Tugas 2

1. **Alur request sampai data tampil di browser**

Semuanya dimulai ketika browser mengirim request ke `/education/`. Request itu pertama kali ditangkap oleh `urls.py` di level proyek (`portofolio/urls.py`), tapi file ini sendiri nggak tahu cara nanganinnya — dia cuma nge-forward semua path ke `main/urls.py` lewat `include('main.urls')`, karena logika routing yang sesungguhnya sengaja dipisah ke level aplikasi (`main`), bukan ditumpuk di proyek. Di `main/urls.py`, barulah path `education/` dicocokkan dengan salah satu `urlpatterns`, dan Django memetakannya ke fungsi `show_education` di `main/views.py`. Di titik inilah "jembatan" MVT bekerja: view memanggil `Education.objects.all()` untuk query semua baris dari tabel `main_education` di database, lalu membungkusnya ke dalam dictionary `context` bersama data lain seperti `name`.

View lalu memanggil `render(request, "education.html", context)`.  Django Template Engine membaca `education.html`, mencari setiap penanda `{{ }}` dan `{% %}`, lalu menggantinya dengan nilai dari `context` — dalam kasus ini, perulangan `{% for education in education_list %}` dijalankan sebanyak jumlah objek yang ada, menghasilkan satu blok `<article class="education-item">` untuk tiap baris data. Hasil akhirnya berupa dokumen HTML utuh yang dikirim balik sebagai HTTP response ke browser, dan barulah pengguna melihat halaman Pendidikan yang sudah terisi.

2. **Kenapa data tidak ditulis langsung di template**

Alasan utamanya adalah pemeliharaan jangka panjang. Kalau data pendidikan saya tulis langsung sebagai teks statis di `education.html` (seperti yang saya lakukan sebelumnya di Tugas 1), setiap kali ada perubahan — katakanlah saya lulus dan mau nambahin baris "S1 selesai 2029" — saya harus buka kode HTML, cari baris yang tepat, edit manual, lalu deploy ulang seluruh aplikasi cuma buat satu perubahan teks.

Dengan model, data dan tampilan jadi dua hal yang terpisah total. Saya bisa menambah, mengedit, atau menghapus entri pendidikan lewat Django admin atau shell — tanpa menyentuh satu baris pun kode HTML atau Python di luar itu. Ini juga berarti template `education.html` bisa dipakai ulang untuk berapa pun jumlah data yang ada, entah 4 atau 40 entri, tanpa perlu saya tulis ulang. Kalau nanti proyek ini berkembang jadi butuh fitur tambah data lewat form di halaman web(bukan cuma admin/shell), struktur ini juga sudah siap — tinggal bikin view baru buat proses form-nya, model dan template yang sudah ada nggak perlu diubah sama sekali.

3. **`makemigrations` vs `migrate`**

Dua perintah ini sering ketuker karena selalu dijalankan berurutan, tapi fungsinya beda. `makemigrations` itu semacam "mencatat rencana perubahan" — Django membandingkan definisi model di `models.py` dengan riwayat migrasi yang sudah ada, lalu menghasilkan file baru di folder `migrations/` yang isinya instruksi perubahan struktur tabel (bahasa Python, bukan SQL langsung). Di tahap ini, database yang sesungguhnya belum tersentuh sama sekali.

`migrate` itu yang benar-benar mengeksekusi instruksi dari file migrasi tadi ke database (`db.sqlite3` di lokal saya). Tanpa `migrate`, file migrasi cuma jadi dokumen rencana yang nggak pernah dijalankan, dan tabelnya nggak akan pernah kebentuk.

Contoh konkret dari proyek ini: waktu saya menambahkan model `Education` di Tugas 2, `makemigrations` mendeteksi model baru itu dan membuatkan file `0002_education.py` yang isinya instruksi "buat tabel baru dengan kolom institution, level, major, started_at ended_at". Setelah itu saya jalankan `migrate`, dan barulah tabel `main_education` benar-benar muncul di `db.sqlite3`, siap diisi data.

### AI Disclosure (Tugas 2)

Untuk tugas ini saya berdiskusi dengan Claude cukup lama, terutama di tahap perencanaan: memutuskan apakah bikin section portofolio baru dari nol atau memindahkan section Pendidikan yang sudah ada di Tugas 1 jadi model + halaman sendiri — saya pilih opsi kedua. Dari situ, saya dibantu menyusun struktur field model `Education` (termasuk kenapa `major` dibuat `blank=True`, karena SD/SMP nggak punya jurusan), logika view `show_education`, kode template dengan `{% for %}` dan `{% empty %}`, serta empat unit test di `EducationTest`.

Saya juga sempat ketemu beberapa error di luar dugaan yang nggak langsung berhubungan sama kode Tugas 2 ini sendiri, seperti salah menjalankan file (`asgi.py` dan `tests.py` dijalankan langsung sebagai script Python alih-alih lewat `manage.py`) dan masalah cache browser yang bikin CSS/HTML terlihat belum ter-update — semuanya saya diskusikan dan pahami penyebabnya satu per satu sebelum lanjut.

Lalu ada Bagian yang saya periksa ulang pemilihan bagian mana dari portofolio yang dijadikan model (Pendidikan), data pendidikan yang diinput, serta pengecekan akhir bahwa `python manage.py test` dan `python manage.py runserver` berjalan tanpa error sebelum commit dan push. 

### Tugas 3

1. **Kenapa ModelForm, bukan form HTML manual — dan kenapa wajib `{% csrf_token %}`**

Kalau saya bikin form HTML manual (`<input>` satu-satu ditulis tangan), saya harus mendefinisikan ulang tipe input, validasi, dan aturan panjang karakter yang sebenarnya **sudah didefinisikan** di `models.py` nama field, `max_length`, apakah boleh kosong (`blank=True`), semuanya jadi dobel ditulis di dua tempat berbeda. Kalau suatu saat saya ubah field di model (misalnya `major` jadi wajib diisi), saya juga harus inget buat ubah manual di HTML-nya. `ModelForm` menghilangkan duplikasi itu: form-nya otomatis "membaca" struktur dari `Education` lewat `class Meta`, jadi validasi dan tipe input cukup didefinisikan sekali di model, lalu form dan database otomatis konsisten. 
   
Soal `{% csrf_token %}`, itu bukan sekadar formalitas Django, tanpa token itu, aplikasi saya rentan kena **Cross-Site Request Forgery**: situs lain yang nggak berhubungan bisa diam-diam nyuruh browser pengunjung saya buat ngirim request POST ke `/education/add/` atau endpoint lain di portofolio saya, tanpa pengunjung itu sadar. Django nge-generate token unik tiap sesi, nempelinnya di form lewat `{% csrf_token %}`, dan nge-cek waktu form di-submit apakah tokennya cocok dengan yang di server. Kalau nggak cocok (atau nggak ada sama sekali), requestnya ditolak duluan sebelum sempat masuk ke logika view saya.

2. **Kenapa JSON lebih disukai dibanding XML buat aplikasi web modern**

Alasan paling kerasa buat saya pribadi waktu ngerjain `get_education_json` adalah soal **ukuran dan kesederhanaan**. Satu objek Education di XML butuh tag pembuka-penutup buat tiap field (`<institution>...</institution>`, dst), sedangkan di JSON cukup pasangan `"institution": "..."` — lebih ringkas, dan itu ngaruh langsung ke ukuran response yang dikirim lewat jaringan.

Alasan kedua, JSON hampir selalu bisa langsung di-*parse* jadi
struktur data native tanpa proses tambahan yang ribet — di
JavaScript malah `JSON.parse()` doang, karena sintaksnya memang asalnya dari notasi objek JavaScript. XML butuh parser tersendiri (DOM parser atau semacamnya) yang secara komputasi lebih berat. Buat arsitektur RESTful API yang saya pelajari di tutorial ini di mana endpoint kayak `/api/education/` bakal sering dipanggil berulang-ulang, misalnya nanti kalau saya pasang fitur pencarian real-time pakai fetch() — ukuran yang kecil dan parsing yang cepat itu jadi keunggulan yang langsung kerasa dibanding XML.

3. **Alur view mengembalikan data JSON, dan kenapa perlu serialization**

Waktu browser (atau Postman, seperti di tutorial) mengakses `/api/education/`, Django memetakan URL itu ke fungsi `get_education_json` di `main/views.py`. Di dalam fungsi ini, `Education.objects.all()` mengambil data dari database dalam bentuk QuerySet — tapi QuerySet ini isinya objek Python (instance model Django), bukan teks yang bisa langsung dikirim lewat HTTP. Disinilah `serializers.serialize("json", education_qs)` berperan: dia mengubah tiap objek model jadi representasi teks berformat JSON yang strukturnya baku (ada `model`, `pk`, dan `fields`).

Proses serialization ini **wajib** dilakukan karena protokol HTTP cuma bisa mengangkut data dalam bentuk teks/byte, sedangkan objek Python (apalagi yang menyimpan referensi ke koneksi database, method, dsb) nggak bisa langsung "dikirim" begitu saja —ObjectQuerySet nggak punya arti apa-apa buat client di luar proses Python yang sedang jalan. Setelah diserialize jadi teks JSON, hasilnya dibungkus `HttpResponse(..., content_type="application/json")` supaya client tahu cara membaca isi response-nya, baru dikirim balik lewat jaringan.

Alur ini saya pakai dua kali di proyek saya: pertama buat endpoint API murni (`/api/education/`), kedua di dalam `show_education` sendiri — yang sengaja memanggil `get_education_json`, lalu melakukan **deserialization** (`serializers.deserialize`) buat mengubah teks JSON itu balik jadi objek Python yang bisa dibaca propertinya (`.institution`, `.is_ongoing`, dst) sebelum dikirim ke template `education.html`. Sekilas muter-muter, tapi ini mensimulasikan skenario di mana data sebenarnya datang dari sumber luar berbentuk JSON (API pihak ketiga, atau frontend yang terpisah dari backend), bukan langsung dari database.

### AI Disclosure (Tugas 3)

Tugas ini saya kerjakan dengan bantuan Claude di beberapa bagian.
Untuk refactoring `base.html`, saya awalnya salah gabungin dua potongan kode dari tutorial (ada duplikat `<head>` dan `<body>`/`<html>` yang nggak ketutup), dan itu ketahuan serta diperbaiki lewat diskusi dengan Claude. Saya juga dibantu mengadaptasi seluruh contoh kode tutorial yang aslinya pakai entity "Project" supaya sesuai dengan pilihan saya sendiri di Tugas 2, yaitu "Education" — termasuk `EducationForm`, view `create_education`/`update_education`/`delete_education`/`get_ed cation_json`, template `education_form.html` yang dipakai bareng buat tambah dan edit data, serta komponen modal konfirmasi hapus.

Fitur update/edit (yang jadi syarat baru di Tugas 3 ini, belum ada di Tutorial 03) saya rancang dengan pola yang sama seperti create, cumaform-nya di-passing `instance=education` supaya terprefill data lama ini saya pahami betul alurnya karena mempraktikkan langsung, bukan cuma nyalin. Saya juga menambahkan endpoint `/api/experience/` sebagai fitur ekstra (bonus, sesuai catatan di soal), dengan pola yang identik ke `/api/education/`.

Keputusan desain (memilih Pendidikan sebagai section, struktur field model, kapan pakai tombol vs link, dsb) tetap saya yang tentukan. Claude membantu di sisi implementasi teknis dan penjelasan konsep, yang saya baca ulang dan pastikan saya pahami sebelum commit.