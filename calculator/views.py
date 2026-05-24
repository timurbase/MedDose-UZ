import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import DosageForm
from .models import Calculation
from .math_engine import (
    calculate_concentration,
    detect_risk_zone,
    recommend_next_dose,
    compare_methods,
)

# Dori uchun standart farmakokinetik koeffitsiyentlar
DRUG_DEFAULTS = {
    'Amoksitsillin':  {'k': 0.35, 'ka': 1.50, 'ke': 0.35, 'mic': 2.0,  'mtc': 15.0},
    'Paratsetamol':   {'k': 0.28, 'ka': 1.20, 'ke': 0.28, 'mic': 4.0,  'mtc': 20.0},
    'Ibuprofen':      {'k': 0.20, 'ka': 1.00, 'ke': 0.20, 'mic': 5.0,  'mtc': 25.0},
    'Metformin':      {'k': 0.10, 'ka': 0.60, 'ke': 0.10, 'mic': 1.0,  'mtc': 5.0},
    'Enalapril':      {'k': 0.15, 'ka': 0.80, 'ke': 0.15, 'mic': 0.5,  'mtc': 4.0},
    'Digoksin':       {'k': 0.02, 'ka': 0.40, 'ke': 0.02, 'mic': 0.8,  'mtc': 2.0},
    'Vankomitsin':    {'k': 0.12, 'ka': 2.00, 'ke': 0.12, 'mic': 10.0, 'mtc': 40.0},
    'Morfin':         {'k': 0.25, 'ka': 1.80, 'ke': 0.25, 'mic': 0.01, 'mtc': 0.1},
}


def index(request):
    """Bosh sahifa — hisoblash formasi."""
    form = DosageForm()
    drug_defaults_json = json.dumps(DRUG_DEFAULTS)

    recent_calculations = Calculation.objects.order_by('-created_at')[:5]

    context = {
        'form': form,
        'drug_defaults': drug_defaults_json,
        'recent_calculations': recent_calculations,
        'page_title': 'MedDose UZ — Farmakokinetik Hisoblash',
    }
    return render(request, 'calculator/index.html', context)


@require_http_methods(["POST"])
def calculate(request):
    """Hisoblash so'rovi — POST."""
    form = DosageForm(request.POST)

    if not form.is_valid():
        drug_defaults_json = json.dumps(DRUG_DEFAULTS)
        recent_calculations = Calculation.objects.order_by('-created_at')[:5]
        return render(request, 'calculator/index.html', {
            'form': form,
            'drug_defaults': drug_defaults_json,
            'recent_calculations': recent_calculations,
            'page_title': 'MedDose UZ — Hisoblash',
        })

    data = form.cleaned_data

    # Dori nomi
    drug_name = data['drug_name']
    if drug_name == 'Boshqa':
        drug_name = data.get('drug_name_custom', 'Noma\'lum dori')

    # Asosiy hisoblash
    results = calculate_concentration(
        dose=data['dose'],
        weight=data['patient_weight'],
        age=data['patient_age'],
        route=data['route'],
        model_type=data['model_type'],
        k=data['k'],
        ka=data['ka'],
        ke=data['ke'],
        t_end=data['t_end'],
        h=data['h'],
    )

    mic = data['mic']
    mtc = data['mtc']

    # Asosiy konsentratsiya ma'lumotlari (RK4 yoki qon kamerasi)
    if 'rk4' in results:
        primary_t = results['rk4']['t']
        primary_C = results['rk4']['C']
    elif 'two_blood' in results:
        primary_t = results['two_blood']['t']
        primary_C = results['two_blood']['C']
    else:
        primary_t = []
        primary_C = []

    # Xavf zonasini aniqlash
    risk_info = detect_risk_zone(primary_C, mic, mtc)

    # Keyingi doza vaqti
    next_dose = recommend_next_dose(primary_t, primary_C, mic)

    # Usullarni solishtirish (faqat bir kamerali uchun)
    comparison = None
    if data['model_type'] == 'one':
        comparison = compare_methods(
            C0=results['C0'],
            k=data['k'],
            t_end=data['t_end'],
            h=data['h'],
        )

    # Hisoblashni saqlash
    calc_obj = Calculation.objects.create(
        patient_weight=data['patient_weight'],
        patient_age=data['patient_age'],
        drug_name=drug_name,
        route=data['route'],
        dose=data['dose'],
        model_type=data['model_type'],
        k=data['k'],
        ka=data['ka'],
        ke=data['ke'],
        mic=mic,
        mtc=mtc,
        t_end=data['t_end'],
        h=data['h'],
        risk_status=risk_info.get('status', ''),
        max_concentration=risk_info.get('max_C'),
        next_dose_time=next_dose.get('time'),
    )

    # ── Chart.js uchun ma'lumotlar (scatter + showLine format) ──
    # Har bir dataset o'zining {x, y} nuqtalarini olib yuradi.
    # Chart turi: 'scatter', showLine: true — bu barcha datasetlarni
    # turli uzunliklarda ham to'g'ri ko'rsatadi.

    chart_datasets = []
    colors = {
        'analytic': '#0d6efd',
        'euler': '#fd7e14',
        'rk4': '#198754',
        'two_depo': '#6f42c1',
        'two_blood': '#0dcaf0',
    }

    for key, dataset in results.items():
        if isinstance(dataset, dict) and 't' in dataset:
            chart_datasets.append({
                'label': dataset['label'],
                'data': [{'x': round(t, 4), 'y': round(c, 6)}
                         for t, c in zip(dataset['t'], dataset['C'])],
                'borderColor': colors.get(key, '#333'),
                'backgroundColor': colors.get(key, '#333') + '22',
                'borderWidth': 2.5,
                'pointRadius': 1 if key in ('euler', 'rk4') else 0,
                'tension': 0.4,
                'fill': False,
                'showLine': True,
            })

    # Eyler vs RK4 xato solishtirish datasets
    comparison_datasets = []
    if comparison:
        comparison_datasets = [
            {
                'label': 'Eyler xatosi',
                'data': [{'x': round(t, 4), 'y': round(e, 8)}
                         for t, e in zip(comparison['t'], comparison['euler_errors'])],
                'borderColor': '#fd7e14',
                'backgroundColor': 'rgba(253,126,20,0.15)',
                'borderWidth': 2,
                'pointRadius': 3,
                'tension': 0.3,
                'fill': True,
                'showLine': True,
            },
            {
                'label': 'RK4 xatosi',
                'data': [{'x': round(t, 4), 'y': round(e, 8)}
                         for t, e in zip(comparison['t'], comparison['rk4_errors'])],
                'borderColor': '#198754',
                'backgroundColor': 'rgba(25,135,84,0.15)',
                'borderWidth': 2,
                'pointRadius': 3,
                'tension': 0.3,
                'fill': True,
                'showLine': True,
            },
        ]

    context = {
        'form': form,
        'data': data,
        'drug_name': drug_name,
        'results': results,
        'risk_info': risk_info,
        'next_dose': next_dose,
        'comparison': comparison,
        'calc_id': calc_obj.id,
        'mic': mic,
        'mtc': mtc,

        # JSON for Chart.js — scatter format
        # MUHIM: json.dumps ishlatamiz chunki Django L10N kasr vergulni
        # o'zgartiradi (2.0 -> 2,0), bu JS da xato bo'ladi
        'chart_datasets_json': json.dumps(chart_datasets),
        'comparison_datasets_json': json.dumps(comparison_datasets),
        'mic_json': json.dumps(float(mic)),
        'mtc_json': json.dumps(float(mtc)),
        't_end_json': json.dumps(float(data['t_end'])),

        'page_title': f'Natijalar — {drug_name} | MedDose UZ',
    }

    return render(request, 'calculator/result.html', context)


def history(request):
    """Hisoblashlar tarixi."""
    calculations = Calculation.objects.order_by('-created_at')[:50]
    context = {
        'calculations': calculations,
        'page_title': 'Hisoblashlar tarixi | MedDose UZ',
    }
    return render(request, 'calculator/history.html', context)


def about(request):
    """Loyiha haqida sahifa."""
    features = [
        'Bemor vaznini kiritish',
        'Bemor yoshini kiritish',
        'Dori turini tanlash',
        'Dori yuborish usulini tanlash (tabletka, ukol, kapelnitsa)',
        'Dori dozasini kiritish',
        'Vaqt oralig\'i va vaqt qadamini kiritish',
        'Bir kamerali farmakokinetik modelni hisoblash',
        'Ikki kamerali farmakokinetik modelni hisoblash',
        'Eyler usuli orqali hisoblash',
        '4-tartibli Runge-Kutta usuli orqali hisoblash',
        'Eyler va RK4 natijalarini solishtirish',
        'Qondagi dori konsentratsiyasi grafigini chiqarish',
        'Minimal samarali va maksimal toksik chegarani ko\'rsatish',
        'Toksik zonaga chiqqanda qizil ogohlantirish',
        'Terapevtik zonadan pastga tushganda ogohlantirish',
        'Keyingi doza vaqtini taxminiy tavsiya qilish',
    ]
    context = {
        'page_title': 'Loyiha haqida | MedDose UZ',
        'features': features,
    }
    return render(request, 'calculator/about.html', context)


def clear_history(request):
    """Tarixni tozalash."""
    if request.method == 'POST':
        Calculation.objects.all().delete()
        messages.success(request, 'Hisoblashlar tarixi tozalandi.')
    return redirect('calculator:history')


def handler404(request, exception):
    """404 — Sahifa topilmadi."""
    return render(request, 'calculator/404.html', {
        'page_title': 'Sahifa topilmadi | MedDose UZ',
    }, status=404)


def handler500(request):
    """500 — Server xatosi."""
    return render(request, 'calculator/500.html', {
        'page_title': 'Server xatosi | MedDose UZ',
    }, status=500)
