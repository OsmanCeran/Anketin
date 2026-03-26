import json
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib import messages

from .models import Secenek, Soru, KullaniciProfili, Oy
from .forms import ProfilGuncellemeForm, UserUpdateForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        soru = self.get_object()
        
        # Grafik için verileri JSON formatında seri hale getir
        labels = [secenek.secenek_metni for secenek in soru.secenek_set.all()]
        data = [secenek.oylar for secenek in soru.secenek_set.all()]
        
        context['chart_labels_json'] = json.dumps(labels)
        context['chart_data_json'] = json.dumps(data)
        
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            profil, _ = KullaniciProfili.objects.get_or_create(user=self.request.user)
            context['is_favorited'] = profil.favori_anketler.filter(id=self.object.id).exists()
        else:
            context['is_favorited'] = False
        return context

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
        # Prevent duplicate voting
        user = request.user if request.user.is_authenticated else None
        
        if not user:
            if not request.session.session_key:
                request.session.save()
            session_id = request.session.session_key
        else:
            session_id = None
            
        if user:
            already_voted = Oy.objects.filter(user=user, soru=soru).exists()
        else:
            already_voted = Oy.objects.filter(session_id=session_id, soru=soru).exists()
            
        if already_voted:
            return render(request, 'anketin/detail.html', {
                'soru': soru,
                'error_message': 'Bu ankete zaten oy verdiniz. İlginize teşekkürler!'
            }, status=400)

        # Record the vote
        Oy.objects.create(soru=soru, secenek=secilen_secenek, user=user, session_id=session_id)

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
            yayinlanma_tarihi=timezone.now(),
            olusturan=request.user if request.user.is_authenticated else None
        )

        # Seçenekleri oluştur
        for secenek_metni in gecerli_secenekler:
            yeni_soru.secenek_set.create(secenek_metni=secenek_metni)

        return HttpResponseRedirect(reverse("anketin:index"))

    # GET Request
    return render(request, "anketin/anket_ekle.html", {"kategoriler": kategoriler})

@login_required
def dashboard(request):
    profil, created = KullaniciProfili.objects.get_or_create(user=request.user)
    favori_anketler = profil.favori_anketler.all()
    olusturdugu_anketler = Soru.objects.filter(olusturan=request.user).order_by("-yayinlanma_tarihi")

    if request.method == 'POST':
        if 'remove_photo' in request.POST:
            profil.profil_fotografi = 'default_avatar.png'
            profil.save()
            messages.success(request, 'Profil fotoğrafınız başarıyla kaldırıldı.')
            return redirect('anketin:dashboard')

        user_form = UserUpdateForm(request.POST, instance=request.user)
        form = ProfilGuncellemeForm(request.POST, request.FILES, instance=profil)
        
        if form.is_valid() and user_form.is_valid():
            user_form.save()
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('anketin:dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        form = ProfilGuncellemeForm(instance=profil)

    context = {
        'profil': profil,
        'form': form,
        'user_form': user_form,
        'favoriler': favori_anketler,
        'olusturulanlar': olusturdugu_anketler
    }
    return render(request, 'anketin/dashboard.html', context)

def kayit_ol(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("anketin:dashboard"))
    else:
        form = UserCreationForm()
    return render(request, 'anketin/auth/kayit.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    # Security: Set session to expire in 30 minutes (1800 seconds) for admin dashboard activity
    request.session.set_expiry(1800)
    
    if request.method == "POST":
        action = request.POST.get("action")
        poll_ids = request.POST.getlist("poll_ids")
        if action == "bulk_delete" and poll_ids:
            Soru.objects.filter(id__in=poll_ids).delete()
        elif action == "bulk_deactivate" and poll_ids:
            fut_date = timezone.now() + datetime.timedelta(days=36500)
            Soru.objects.filter(id__in=poll_ids).update(yayinlanma_tarihi=fut_date)
        return HttpResponseRedirect(reverse("anketin:admin_dashboard"))

    all_polls = Soru.objects.all().order_by("-yayinlanma_tarihi")
    total_polls = all_polls.count()
    active_users = User.objects.count()
    recent_votes_agg = Secenek.objects.aggregate(oy_toplami=Sum('oylar'))
    recent_votes = recent_votes_agg['oy_toplami'] if recent_votes_agg['oy_toplami'] else 0

    context = {
        'all_polls': all_polls,
        'total_polls': total_polls,
        'active_users': active_users,
        'recent_votes': recent_votes
    }
    return render(request, 'anketin/admin_dashboard.html', context)

def custom_logout(request):
    username = request.user.username if request.user.is_authenticated else "Ziyaretçi"
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'anketin/auth/logout_confirmation.html', {'username': username})

@login_required
def toggle_favori(request, soru_id):
    if request.method == 'POST':
        soru = get_object_or_404(Soru, pk=soru_id)
        profil, _ = KullaniciProfili.objects.get_or_create(user=request.user)
        if profil.favori_anketler.filter(id=soru_id).exists():
            profil.favori_anketler.remove(soru)
            messages.success(request, 'Anket favorilerinizden çıkarıldı.')
        else:
            profil.favori_anketler.add(soru)
            messages.success(request, 'Anket favorilerinize eklendi.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('anketin:detail', args=[soru_id])))
