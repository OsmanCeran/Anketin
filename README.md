# Anketin 📊

Anketin, kullanıcıların anket oluşturup oylayabildikleri, sonuçları grafiklerle anlık olarak takip edebildikleri modern, şık ve premium görünüme sahip bir Django web uygulamasıdır. Başta standart bir anket uygulaması olarak geliştirilmiş, daha sonra "Glassmorphism" tasarım kurallarıyla zenginleştirilmiştir.

## 🌟 Özellikler
- **Kategorize Edilmiş Anketler:** Spor, Teknoloji, Finans, Oyun, Gündem gibi alanlarda ilgilinizi çeken anketlere anında ulaşabilmeniz için kategorize edilmiş akıllı yapı.
- **Trend Anketler Altyapısı:** En çok oy alan, etkileşimi en yüksek olan oylamaları akıllı bir şekilde süzüp ana sayfada "Öne Çıkanlar (🔥)" olarak listeler.
- **Detaylı Analiz & Yeni Nesil Grafikler:** Her anketin sonucu sadece ona özel oluşturulmuş ayrı bir grafikte gösterilir! Chart.js destekli interaktif *"Doughnut"* (Simit) grafik stili ile çok daha berrak veri okuma.
- **Modern Anket Oluşturma:** Sisteme dilediğiniz kategoriyi belirterek en az iki seçenekten oluşan kendi sorularınızı ekleyebilir ve insanların fikrini alabilirsiniz.
- **Premium Arayüz (Glassmorphism):** "Cam efekti", gece-koyu (Midnight/Teal) renk uyumu ve yüksek performanslı animasyonlu geçişleriyle benzersiz bir görsel deneyim.
- **Yönetim Paneli:** Django'nun güçlü entegre Admin paneli ile tüm soru ve seçimlerin idaresini kolayca yapabilirsiniz.

## 🚀 Kurulum Adımları (Yerel Ortam)

Projeyi kendi bilgisayarınızda (localhost) denemek için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

1. **Projeyi Bilgisayarınıza İndirin:**
   ```bash
   git clone https://github.com/OsmanCeran/Anketin.git
   cd Anketin
   ```

2. **Gereksinimleri Yükleyin:**
   Bilgisayarınızda öncelikle Python yüklü olmalıdır. Projenin bağımlılıklarını kurmak için terminalinizde:
   ```bash
   pip install django pillow
   ```

3. **Veritabanı Uyumlamasını Yapın:**
   ```bash
   python manage.py migrate
   ```

4. **Sunucuyu Başlatın:**
   ```bash
   python manage.py runserver
   ```
   Kurulum tamamlandı! Tarayıcınızdan `http://localhost:8000/anketin/` adresine girerek uygulamayı test edebilirsiniz.

## 🛠️ Kullanılan Teknolojiler
- **Backend:** Python, Django
- **Frontend:** HTML5, Vanilla CSS3 (Custom Design System), JavaScript, Chart.js
- **Veritabanı:** SQLite
