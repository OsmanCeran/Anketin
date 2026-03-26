from django.contrib import admin

from .models import Secenek, Soru, KullaniciProfili

class SecenekInline(admin.TabularInline):
    model = Secenek
    extra = 3

class SoruAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["soru_metni"]}),
        ("Tarih bilgisi", {"fields": ["yayinlanma_tarihi"], "classes": ["collapse"]}),
    ]
    inlines = [SecenekInline]
    list_display = ["soru_metni", "yayinlanma_tarihi", "was_published_recently"]
    list_filter = ["yayinlanma_tarihi"]
    search_fields = ["soru_metni"]

admin.site.register(Soru, SoruAdmin)

@admin.register(KullaniciProfili)
class KullaniciProfiliAdmin(admin.ModelAdmin):
    list_display = ("user", "dogum_tarihi")
    search_fields = ("user__username", "bio")
