"""
MedDose UZ — Farmakokinetik hisoblash matematik dvigatel

Quyidagi modellar amalga oshirilgan:
  1. Bir kamerali model (One-compartment): dC/dt = -k * C
  2. Ikki kamerali model (Two-compartment):
       dC_depo/dt = -ka * C_depo
       dC_qon/dt  =  ka * C_depo - ke * C_qon
  3. Eyler usuli (Euler method)
  4. 4-tartibli Runge-Kutta usuli (RK4)
"""

import math


# ─────────────────────────────────────────────────────────────────────────────
# YORDAMCHI FUNKSIYALAR
# ─────────────────────────────────────────────────────────────────────────────

def linspace(start, stop, n):
    """np.linspace analog — n ta teng oraliqli nuqtalar."""
    if n <= 1:
        return [start]
    step = (stop - start) / (n - 1)
    return [start + i * step for i in range(n)]


def arange(start, stop, step):
    """np.arange analog."""
    result = []
    t = start
    while t <= stop + 1e-12:
        result.append(round(t, 10))
        t += step
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 1. BIR KAMERALI MODEL — analitik yechim
# ─────────────────────────────────────────────────────────────────────────────

def one_compartment_model(C0, k, t_list):
    """
    Bir kamerali farmakokinetik model — analitik yechim.
    
    dC/dt = -k * C  =>  C(t) = C0 * exp(-k * t)

    Parametrlar:
        C0      — boshlang'ich konsentratsiya (mg/L)
        k       — eliminatsiya tezligi konstantasi (1/soat)
        t_list  — vaqt ro'yxati (soat)

    Qaytaradi:
        (t_list, C_list) — vaqt va konsentratsiya ro'yxatlari
    """
    C_list = [C0 * math.exp(-k * t) for t in t_list]
    return t_list, C_list


# ─────────────────────────────────────────────────────────────────────────────
# 2. IKKi KAMERALI MODEL — analitik yechim
# ─────────────────────────────────────────────────────────────────────────────

def two_compartment_model(dose, ka, ke, t_list):
    """
    Ikki kamerali farmakokinetik model — analitik yechim.

    Depo (qabul) kamera:  dC_depo/dt = -ka * C_depo
    Markaziy (qon) kamera: dC_qon/dt  =  ka * C_depo - ke * C_qon

    Parametrlar:
        dose   — doza (mg); C_depo(0) = dose, C_qon(0) = 0
        ka     — absorbsiya tezligi (1/soat)
        ke     — eliminatsiya tezligi (1/soat)
        t_list — vaqt ro'yxati (soat)

    Qaytaradi:
        (t_list, C_depo_list, C_qon_list)
    """
    C_depo_list = []
    C_qon_list = []

    for t in t_list:
        C_depo = dose * math.exp(-ka * t)
        if abs(ka - ke) < 1e-9:
            # Maxsus holat: ka ≈ ke
            C_qon = ka * dose * t * math.exp(-ka * t)
        else:
            C_qon = (ka * dose / (ka - ke)) * (math.exp(-ke * t) - math.exp(-ka * t))
        C_depo_list.append(max(C_depo, 0))
        C_qon_list.append(max(C_qon, 0))

    return t_list, C_depo_list, C_qon_list


# ─────────────────────────────────────────────────────────────────────────────
# 3. EYLER USULI — sonli yechim
# ─────────────────────────────────────────────────────────────────────────────

def euler_method(C0, k, t_start, t_end, h):
    """
    Eyler usuli yordamida bir kamerali model uchun sonli yechim.

    y_{n+1} = y_n + h * f(t_n, y_n)
    bu yerda: f(t, C) = -k * C

    Parametrlar:
        C0      — boshlang'ich konsentratsiya (mg/L)
        k       — eliminatsiya konstantasi (1/soat)
        t_start — boshlang'ich vaqt (soat)
        t_end   — tugash vaqti (soat)
        h       — vaqt qadami (soat)

    Qaytaradi:
        (t_list, C_list)
    """
    t_list = []
    C_list = []

    t = t_start
    C = C0

    while t <= t_end + 1e-12:
        t_list.append(round(t, 6))
        C_list.append(max(C, 0))
        # f(t, C) = -k * C
        C = C + h * (-k * C)
        t += h

    return t_list, C_list


# ─────────────────────────────────────────────────────────────────────────────
# 4. RUNGE-KUTTA 4-tartibli usuli — sonli yechim
# ─────────────────────────────────────────────────────────────────────────────

def rk4_method(C0, k, t_start, t_end, h):
    """
    4-tartibli Runge-Kutta usuli yordamida bir kamerali model uchun sonli yechim.

    k1 = f(t_n, y_n)
    k2 = f(t_n + h/2, y_n + h*k1/2)
    k3 = f(t_n + h/2, y_n + h*k2/2)
    k4 = f(t_n + h,   y_n + h*k3)
    y_{n+1} = y_n + (h/6) * (k1 + 2*k2 + 2*k3 + k4)

    bu yerda: f(t, C) = -k * C

    Parametrlar:
        C0      — boshlang'ich konsentratsiya (mg/L)
        k       — eliminatsiya konstantasi (1/soat)
        t_start — boshlang'ich vaqt (soat)
        t_end   — tugash vaqti (soat)
        h       — vaqt qadami (soat)

    Qaytaradi:
        (t_list, C_list)
    """

    def f(t, C):
        return -k * C

    t_list = []
    C_list = []

    t = t_start
    C = C0

    while t <= t_end + 1e-12:
        t_list.append(round(t, 6))
        C_list.append(max(C, 0))

        k1 = f(t, C)
        k2 = f(t + h / 2, C + h * k1 / 2)
        k3 = f(t + h / 2, C + h * k2 / 2)
        k4 = f(t + h, C + h * k3)

        C = C + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        t += h

    return t_list, C_list


# ─────────────────────────────────────────────────────────────────────────────
# 5. KONSENTRATSIYANI HISOBLASH (asosiy funksiya)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_concentration(
    dose, weight, age, route,
    model_type, k, ka, ke,
    t_end, h
):
    """
    Bemor parametrlarini hisobga olgan holda farmakokinetik hisoblash.

    Parametrlar:
        dose       — doza (mg)
        weight     — bemor vazni (kg)
        age        — bemor yoshi (yil)
        route      — yuborish usuli: 'oral', 'injection', 'infusion'
        model_type — 'one' yoki 'two'
        k          — eliminatsiya konstantasi (bir kamerali uchun)
        ka         — absorbsiya konstantasi (ikki kamerali uchun)
        ke         — eliminatsiya konstantasi (ikki kamerali uchun)
        t_end      — hisoblash tugash vaqti (soat)
        h          — vaqt qadami (soat)

    Qaytaradi:
        dict — barcha hisoblash natijalari
    """
    t_start = 0.0

    # Doza kg ga nisbatan sozlash
    dose_per_kg = dose / weight if weight > 0 else dose

    # Yoshga ko'ra tuzatish koeffitsiyenti
    if age < 12:
        age_factor = 0.7
    elif age > 65:
        age_factor = 0.8
    else:
        age_factor = 1.0

    # Boshlang'ich konsentratsiya (soddalashtirilgan model)
    # Agar IV (ukol/kapelnitsa) bo'lsa — darhol qonga, aks holda absorbsiya
    if route in ('injection', 'infusion'):
        C0 = dose_per_kg * age_factor  # mg/kg
    else:
        C0 = dose_per_kg * age_factor * 0.85  # 85% bioavailability (og'iz orqali)

    t_list_fine = arange(t_start, t_end, h / 10)  # Analitik uchun mayda qadamlar

    results = {}

    if model_type == 'one':
        # Analitik yechim
        t_anal, C_anal = one_compartment_model(C0, k, t_list_fine)
        results['analytic'] = {
            'label': 'Analitik (Bir kamerali)',
            't': t_anal,
            'C': C_anal
        }

        # Eyler usuli
        t_euler, C_euler = euler_method(C0, k, t_start, t_end, h)
        results['euler'] = {
            'label': 'Eyler usuli',
            't': t_euler,
            'C': C_euler
        }

        # RK4 usuli
        t_rk4, C_rk4 = rk4_method(C0, k, t_start, t_end, h)
        results['rk4'] = {
            'label': 'Runge-Kutta 4 (RK4)',
            't': t_rk4,
            'C': C_rk4
        }

    elif model_type == 'two':
        # Ikki kamerali model
        t_two, C_depo, C_qon = two_compartment_model(C0, ka, ke, t_list_fine)
        results['two_depo'] = {
            'label': 'Depo konsentratsiyasi',
            't': t_two,
            'C': C_depo
        }
        results['two_blood'] = {
            'label': 'Qon konsentratsiyasi (Analitik)',
            't': t_two,
            'C': C_qon
        }

        # Eyler usuli (qon uchun)
        t_euler, C_euler = euler_method(C0, ke, t_start, t_end, h)
        results['euler'] = {
            'label': 'Eyler usuli (qon)',
            't': t_euler,
            'C': C_euler
        }

        # RK4 usuli (qon uchun)
        t_rk4, C_rk4 = rk4_method(C0, ke, t_start, t_end, h)
        results['rk4'] = {
            'label': 'Runge-Kutta 4 (RK4, qon)',
            't': t_rk4,
            'C': C_rk4
        }

    results['C0'] = C0
    results['model_type'] = model_type
    results['t_end'] = t_end
    results['h'] = h

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 6. XAVF ZONASINI ANIQLASH
# ─────────────────────────────────────────────────────────────────────────────

def detect_risk_zone(C_values, mic, mtc):
    """
    Konsentratsiya qiymatlarini xavf zonalari bo'yicha baholash.

    Parametrlar:
        C_values — konsentratsiya ro'yxati
        mic      — Minimal Inhibitory Concentration / minimal terapevtik chegara
        mtc      — Maximum Toxic Concentration / maksimal toksik chegara

    Qaytaradi:
        dict — xavf holati haqida ma'lumot
    """
    if not C_values:
        return {'status': 'unknown', 'message': 'Ma\'lumot yo\'q', 'color': 'secondary'}

    max_C = max(C_values)
    min_C = min(v for v in C_values if v > 0) if any(v > 0 for v in C_values) else 0

    if max_C > mtc:
        status = 'toxic'
        message = (
            f'⚠️ DIQQAT! Dori dozasi TOKSIK zonaga chiqdi! '
            f'Maksimal konsentratsiya: {max_C:.2f} mg/L '
            f'(Toksik chegara: {mtc:.2f} mg/L)'
        )
        color = 'danger'
    elif max_C < mic:
        status = 'subtherapeutic'
        message = (
            f'📉 Dori konsentratsiyasi TERAPEVTIK darajadan PAST! '
            f'Maksimal konsentratsiya: {max_C:.2f} mg/L '
            f'(Minimal terapevtik: {mic:.2f} mg/L). '
            f'Doza samaradorligi past bo\'lishi mumkin.'
        )
        color = 'warning'
    else:
        status = 'safe'
        message = (
            f'✅ Doza XAVFSIZ intervalda. '
            f'Konsentratsiya: {max_C:.2f} mg/L '
            f'(Terapevtik oraliq: {mic:.2f} – {mtc:.2f} mg/L)'
        )
        color = 'success'

    return {
        'status': status,
        'message': message,
        'color': color,
        'max_C': round(max_C, 4),
        'min_C': round(min_C, 4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. KEYINGI DOZA VAQTINI TAVSIYA QILISH
# ─────────────────────────────────────────────────────────────────────────────

def recommend_next_dose(t_list, C_list, mic):
    """
    Konsentratsiya MIC darajasiga tushgan vaqtni hisoblash va
    keyingi doza vaqtini tavsiya qilish.

    Parametrlar:
        t_list — vaqt ro'yxati (soat)
        C_list — konsentratsiya ro'yxati (mg/L)
        mic    — minimal terapevtik chegara (mg/L)

    Qaytaradi:
        dict — keyingi doza tavsiyasi
    """
    next_dose_time = None

    for i in range(1, len(C_list)):
        if C_list[i] < mic and C_list[i - 1] >= mic:
            # Interpolatsiya
            dt = t_list[i] - t_list[i - 1]
            dc = C_list[i] - C_list[i - 1]
            if abs(dc) > 1e-12:
                frac = (mic - C_list[i - 1]) / dc
                next_dose_time = t_list[i - 1] + frac * dt
            else:
                next_dose_time = t_list[i]
            break

    if next_dose_time is not None:
        hours = int(next_dose_time)
        minutes = int((next_dose_time - hours) * 60)
        return {
            'time': round(next_dose_time, 2),
            'formatted': f'{hours} soat {minutes} daqiqa',
            'recommendation': f'Keyingi dozani {hours} soat {minutes} daqiqadan so\'ng qabul qiling.'
        }
    else:
        return {
            'time': None,
            'formatted': 'Terapevtik oraliqdan tushishi kuzatilmadi',
            'recommendation': 'Konsentratsiya ko\'rsatilgan vaqt davomida terapevtik oraliqda qoladi.'
        }


# ─────────────────────────────────────────────────────────────────────────────
# 8. EULER VA RK4 XATONI SOLISHTIRISH
# ─────────────────────────────────────────────────────────────────────────────

def compare_methods(C0, k, t_end, h):
    """
    Eyler va RK4 usullarini analitik yechim bilan solishtiradi.

    Qaytaradi:
        dict — t_list, euler_errors, rk4_errors, max_euler_err, max_rk4_err
    """
    t_euler, C_euler = euler_method(C0, k, 0, t_end, h)
    t_rk4, C_rk4 = rk4_method(C0, k, 0, t_end, h)

    euler_errors = []
    rk4_errors = []

    for i, t in enumerate(t_euler):
        C_exact = C0 * math.exp(-k * t)
        if i < len(C_euler):
            euler_errors.append(abs(C_euler[i] - C_exact))
        if i < len(C_rk4):
            rk4_errors.append(abs(C_rk4[i] - C_exact))

    return {
        't': t_euler,
        'euler_errors': [round(e, 8) for e in euler_errors],
        'rk4_errors': [round(e, 8) for e in rk4_errors],
        'max_euler_err': round(max(euler_errors), 8) if euler_errors else 0,
        'max_rk4_err': round(max(rk4_errors), 8) if rk4_errors else 0,
    }
