# Kişisel Finans Yönetimi

Bu proje, bireylerin gelir ve giderlerini takip etmelerine, bütçe planlamalarına olanak tanıyan ve finansal durumlarını görselleştiren bir Python tabanlı masaüstü uygulamasıdır. Kullanıcı dostu bir arayüzle finansal işlemleri kaydetmeyi, kategorize etmeyi, bütçe belirlemeyi ve gelir-gider dağılımlarını pasta grafikleriyle görselleştirmeyi sağlar.

## 🔍 Özellikler

İşlem Yönetimi: Gelir ve gider işlemlerini ekleme, silme ve filtreleme.
Bütçe Planlama: Aylık bütçe belirleme ve bütçe aşımı uyarıları.
Veri Görselleştirme: Kategorilere göre gelir ve gider dağılımını gösteren pasta grafikleri.
Kullanıcı Dostu Arayüz: Modern ve sezgisel bir arayüz (customtkinter ile).
Veritabanı Desteği: SQLite ile kalıcı veri saklama.
Raporlama: Finansal özetler ve bütçe raporları.

## 🛠 Gereksinimler

Projenin çalışması için aşağıdaki bağımlılıklar gereklidir:
Python 3.13.3 
Gerekli Python kütüphaneleri (requirements.txt'de listelenmiştir):
customtkinter==5.2.2
pandas==2.2.2
tkcalendar==1.6.1
Web tarayıcı (grafiklerin görüntülenmesi için)


## 🧱 Modüller

- main.py – Uygulama giriş noktası
- gui.py – Arayüz elemanlarını yönetir
- database.py – SQLite bağlantı ve sorgular
- finance_manager.py – Gelir/gider iş mantığı
- chart.html, chart_data.json – Grafik arayüz dosyaları
- summary.html – Finansal özet çıktısı

## 🖥️ Kurulum ve Çalıştırma

```bash
git clone https://github.com/polenkadife/personal-finance-manager.git
cd personal-finance-manager
pip install -r requirements.txt
python main.py
```

## 📊 Kullanım

Uygulamayı Başlatma: python main.py komutunu çalıştırın.
İşlem Ekleme: Ana arayüzdeki formu kullanarak gelir veya gider ekleyin. Tür, miktar, kategori, tarih ve açıklama girin.
Bütçe Belirleme: Yıl, ay ve bütçe miktarını girerek aylık bütçe tanımlayın.
Filtreleme: Kategori, yıl ve ay filtrelerini kullanarak işlemleri görüntüleyin.
Rapor ve Grafik: "Özeti Görüntüle" veya "Grafik Görüntüle" butonlarıyla finansal özetleri ve pasta grafiklerini görün.
Bütçe Kontrolü: Bütçe aşımlarında otomatik uyarılar alın.

## ✍️ Geliştirici

**Polen Kadife**  
212503071 - Mühendislikte Bilgisayar Uygulamaları II

## 📌 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
