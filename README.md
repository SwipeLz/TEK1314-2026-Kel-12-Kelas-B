# Proyek PBL Keamanan Siber - Kelompok 12

**Mata Kuliah:** TEK1314 - Keamanan Siber  
**Program Studi:** D4 Teknologi Rekayasa Komputer  
**Fase Proyek:** Minggu ke-3 & 4 (Perancangan Arsitektur & Skema IP)  

---

## 1. Deskripsi Skenario Proyek
Proyek ini mengimplementasikan simulasi lingkungan uji penetrasi dan pertahanan siber terisolasi pada segmen jaringan privat **192.168.12.0/24**. 

Skenario mencakup:
* **Penyerangan (Red Team):** Attacker melakukan reconnaissance serta eksploitasi web aplikasi dan service rentan pada server korban menggunakan Kali Linux.
* **Pertahanan & Analisis (Blue Team):** Seluruh lalu lintas serangan dipantau dan dianalisis secara real-time oleh Security Onion (NIDS/Suricata dan Zeek) untuk deteksi intrusi dan log forensik jaringan.

## 2. Struktur Deliverables Desain
* [Dokumen Perencanaan IP (ip_plan.md)](docs/design/ip_plan.md)
* [Diagram Topologi Jaringan (topology.png)](docs/design/topology.jpeg)

## 3. Pembagian Peran Tim
* **Project Lead:** Koordinasi desain, tinjauan arsitektur, dan manajemen repositori.
* **Red Team:** Riset celah eksploitasi (port 80, 21, 22) dan spesifikasi mesin target (Metasploitable 2).
* **Blue Team:** Pemodelan topologi logis, konfigurasi segmentasi IP, dan rancangan penempatan sensor NIDS.
