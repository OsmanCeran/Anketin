from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Secenek, Soru

class IndexView(generic.ListView):
    template_name = "anketin/index.html"
    context_object_name = "son_sorular"

    def get_queryset(self):
        """
        Gelecekte yayımlanacak olanları (yayinlanma_tarihi>şimdi) hariç tutarak
        son yayımlanan 5 soruyu döndürür.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now()).order_by(
            "-yayinlanma_tarihi"
        )[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trend_sorular"] = Soru.objects.filter(
            yayinlanma_tarihi__lte=timezone.now()
        ).annotate(
            toplam_oy=Sum("secenek__oylar")
        ).order_by("-toplam_oy")[:4]
        return context

class AnketlerView(generic.ListView):
    template_name = "anketin/anketler.html"
    context_object_name = "kategoriler_sozlugu"

    def get_queryset(self):
        """
        Soruları kategorilerine göre gruplayarak döndürür.
        """
        tum_sorular = Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now()).order_by("-yayinlanma_tarihi")
        kategoriler = {}
        # Etiketlerin Django Model tarafındaki seçimlerine göre:
        tanimli_kategoriler = [k[0] for k in Soru.KATEGORI_SECIMLERI]
        for k in tanimli_kategoriler:
            kategoriler[k] = []
            
        for soru in tum_sorular:
            cat = soru.kategori
            if cat not in kategoriler:
                kategoriler[cat] = []
            kategoriler[cat].append(soru)
            
        # Boş olanları filtrele
        dolu_kategoriler = {k: v for k, v in kategoriler.items() if v}
        return dolu_kategoriler

class GrafiklerView(generic.ListView):
    template_name = "anketin/grafikler.html"
    context_object_name = "sorular"

    def get_queryset(self):
        """
        Tüm yayımlanmış soruları döndür.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now()).order_by("-yayinlanma_tarihi")

class GrafikDetayView(generic.DetailView):
    model = Soru
    template_name = "anketin/grafik_detay.html"
    context_object_name = "soru"

    def get_queryset(self):
        """
        Soruya özel sadece grafik barındıran görünüm.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now())

class DetailView(generic.DetailView):
    model = Soru
    template_name = "anketin/detail.html"

    def get_queryset(self):
        """
        Henüz yayımlanmamış soruları hariç tutar.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Soru
    template_name = "anketin/results.html"

def vote(request, soru_id):
    soru = get_object_or_404(Soru, pk=soru_id)
    try:
        secilen_secenek = soru.secenek_set.get(pk=request.POST["choice"])
    except (KeyError, Secenek.DoesNotExist):
        return render(
            request,
            "anketin/detail.html",
            {
                "soru": soru,
                "error_message": "Bir seçim yapmadınız.",
            },
        )
    else:
        secilen_secenek.oylar = F("oylar") + 1
        secilen_secenek.save()
        return HttpResponseRedirect(reverse("anketin:results", args=(soru.id,)))

def anket_ekle(request):
    kategoriler = [k[0] for k in Soru.KATEGORI_SECIMLERI]
    
    if request.method == "POST":
        soru_metni = request.POST.get("soru_metni", "").strip()
        secenekler = request.POST.getlist("secenek")
        kategori_secimi = request.POST.get("kategori", "Diğer")

        # Boş olan seçenekleri filtrele
        gecerli_secenekler = [s.strip() for s in secenekler if s.strip()]

        if not soru_metni:
            return render(request, "anketin/anket_ekle.html", {
                "error_message": "Lütfen bir soru girin.",
                "kategoriler": kategoriler
            })
            
        if len(gecerli_secenekler) < 2:
            return render(request, "anketin/anket_ekle.html", {
                "error_message": "En az 2 geçerli seçenek girmelisiniz.",
                "soru_metni": soru_metni,
                "kategoriler": kategoriler
            })

        # Soruyu oluştur
        yeni_soru = Soru.objects.create(
            soru_metni=soru_metni,
            kategori=kategori_secimi,
            yayinlanma_tarihi=timezone.now()
        )

        # Seçenekleri oluştur
        for secenek_metni in gecerli_secenekler:
            yeni_soru.secenek_set.create(secenek_metni=secenek_metni)

        return HttpResponseRedirect(reverse("anketin:index"))

    # GET Request
    return render(request, "anketin/anket_ekle.html", {"kategoriler": kategoriler})
