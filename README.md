# Anketin 📊

Anketin, kullanıcıların anket oluşturup oylayabildikleri, sonuçları grafiklerle anlık olarak takip edebildikleri modern, şık ve premium görünüme sahip bir Django web uygulamasıdır. Başta standart bir anket uygulaması olarak geliştirilmiş, daha sonra "Glassmorphism" tasarım kurallarıyla zenginleştirilmiştir.

## 🌟 Özellikler
- **Anket Oluşturma ve Oylama:** Kolayca çoktan seçmeli dinamik anketler oluşturabilir ve anında oy verebilirsiniz.
- **Canlı Grafikler:** Oylamaların sonuçları *Chart.js* destekli interaktif grafiklerle şık bir şekilde raporlanır.
- **Premium Arayüz:** Modern "cam efekti" (Glassmorphism) tasarımı, gece-koyu karma teması (Dark Teal/Midnight Theme) ve göz yormayan yüksek kaliteli geçişleriyle harika bir kullanıcı deneyimi sunar.
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
