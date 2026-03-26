import datetime
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User

class Soru(models.Model):
    KATEGORI_SECIMLERI = [
        ('Spor', 'Spor'),
        ('Teknoloji', 'Teknoloji'),
        ('Finans', 'Finans'),
        ('Oyun', 'Oyun'),
        ('Gündem', 'Gündem'),
        ('Sinema', 'Sinema'),
        ('Diğer', 'Diğer'),
    ]
    # Anketin kim tarafından oluşturulduğunu bilmemiz gerekiyor
    olusturan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kendi_anketleri', null=True, blank=True)
    soru_metni = models.CharField(max_length=200)
    kategori = models.CharField(max_length=20, choices=KATEGORI_SECIMLERI, default='Diğer')
    yayinlanma_tarihi = models.DateTimeField("Yayımlanma Tarihi")

    def __str__(self):
        return self.soru_metni

    @admin.display(
        boolean=True,
        ordering="yayinlanma_tarihi",
        description="Yakın zamanda yayımlandı mı?",
    )
    def was_published_recently(self):
        simdi = timezone.now()
        return simdi - datetime.timedelta(days=1) <= self.yayinlanma_tarihi <= simdi


class Secenek(models.Model):
    soru = models.ForeignKey(Soru, on_delete=models.CASCADE)
    secenek_metni = models.CharField(max_length=200)
    oylar = models.IntegerField(default=0)

    def __str__(self):
        return self.secenek_metni


class KullaniciProfili(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil', verbose_name="Kullanıcı")
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Hakkında (Bio)")
    dogum_tarihi = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    profil_fotografi = models.ImageField(upload_to='profil_fotograflari/', null=True, blank=True, default='default_avatar.png')
    puan = models.IntegerField(default=0, verbose_name="Kazanılan Puan")
    cozulen_anket_sayisi = models.IntegerField(default=0, verbose_name="Toplam Çözülen Anket")
    favori_anketler = models.ManyToManyField(Soru, blank=True, related_name='favorileyen_kullanicilar')

    def save(self, *args, **kwargs):
        # Eğer profil mevcutsa ve yeni resim yükleniyorsa eski resmi sil
        if self.pk:
            try:
                eski_profil = KullaniciProfili.objects.get(pk=self.pk)
                if eski_profil.profil_fotografi and self.profil_fotografi and eski_profil.profil_fotografi != self.profil_fotografi:
                    import os
                    if eski_profil.profil_fotografi.name != 'default_avatar.png' and os.path.isfile(eski_profil.profil_fotografi.path):
                        os.remove(eski_profil.profil_fotografi.path)
            except KullaniciProfili.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Yeni yüklenen resmi kontrol et ve gerekirse boyutlandır
        if self.profil_fotografi and self.profil_fotografi.name != 'default_avatar.png':
            from PIL import Image
            img = Image.open(self.profil_fotografi.path)
            
            if img.height > 250 or img.width > 250:
                output_size = (250, 250)
                # Aspect ratio'yu koruyarak küçült
                img.thumbnail(output_size)
                img.save(self.profil_fotografi.path)

    def __str__(self):
        return f"{self.user.username} Profili"

class Oy(models.Model):
    soru = models.ForeignKey(Soru, on_delete=models.CASCADE)
    secenek = models.ForeignKey(Secenek, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'soru'],
                condition=Q(user__isnull=False),
                name='unique_user_vote'
            ),
            models.UniqueConstraint(
                fields=['session_id', 'soru'],
                condition=Q(session_id__isnull=False),
                name='unique_session_vote'
            )
        ]

    def __str__(self):
        voter = self.user.username if self.user else "Anonim: " + self.session_id
        return f"{voter} - {self.soru.soru_metni}"
