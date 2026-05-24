"""
MedDose UZ — Django Unit Testlar

Quyidagi modullar testlanadi:
  1. math_engine.py — matematik funksiyalar
  2. views.py       — HTTP so'rovlar
  3. forms.py       — forma validatsiyasi
  4. models.py      — model metodlari
"""

from django.test import TestCase, Client
from django.urls import reverse

from .math_engine import (
    one_compartment_model,
    two_compartment_model,
    euler_method,
    rk4_method,
    calculate_concentration,
    detect_risk_zone,
    recommend_next_dose,
    compare_methods,
    arange,
)
from .models import Calculation, Drug
from .forms import DosageForm


# ─────────────────────────────────────────────────────────────────────────────
# MATH ENGINE TESTLARI
# ─────────────────────────────────────────────────────────────────────────────

class OneCompartmentModelTest(TestCase):
    """Bir kamerali model testlari."""

    def test_initial_concentration(self):
        """t=0 da konsentratsiya C0 ga teng bo'lishi kerak."""
        t_list = [0, 1, 2, 5, 10]
        C0 = 10.0
        k = 0.1
        t_out, C_out = one_compartment_model(C0, k, t_list)
        self.assertAlmostEqual(C_out[0], C0, places=6)

    def test_exponential_decay(self):
        """Konsentratsiya eksponensial kamayishi kerak."""
        import math
        t_list = [0, 1, 2, 5, 10]
        C0 = 10.0
        k = 0.1
        t_out, C_out = one_compartment_model(C0, k, t_list)
        for i, t in enumerate(t_list):
            expected = C0 * math.exp(-k * t)
            self.assertAlmostEqual(C_out[i], expected, places=8)

    def test_zero_elimination(self):
        """k=0 bo'lsa konsentratsiya o'zgarmasligi kerak."""
        t_list = [0, 1, 5, 10]
        C0 = 5.0
        t_out, C_out = one_compartment_model(C0, 0.0, t_list)
        for c in C_out:
            self.assertAlmostEqual(c, C0, places=6)

    def test_half_life(self):
        """Yarim hayot (half-life) = ln(2)/k da C = C0/2."""
        import math
        C0 = 100.0
        k = 0.2
        t_half = math.log(2) / k
        t_list = [t_half]
        _, C_out = one_compartment_model(C0, k, t_list)
        self.assertAlmostEqual(C_out[0], C0 / 2, places=4)


class TwoCompartmentModelTest(TestCase):
    """Ikki kamerali model testlari."""

    def test_blood_zero_at_start(self):
        """t=0 da qon konsentratsiyasi 0 bo'lishi kerak."""
        t_list = [0, 1, 2, 5, 10]
        _, _, C_qon = two_compartment_model(100, ka=1.2, ke=0.1, t_list=t_list)
        self.assertAlmostEqual(C_qon[0], 0.0, places=6)

    def test_depo_decreases(self):
        """Depo konsentratsiyasi vaqt o'tishi bilan kamayishi kerak."""
        t_list = [0, 1, 2, 5, 10, 24]
        _, C_depo, _ = two_compartment_model(100, ka=1.2, ke=0.1, t_list=t_list)
        self.assertGreater(C_depo[0], C_depo[-1])

    def test_blood_peaks_then_decreases(self):
        """Qon konsentratsiyasi oldin o'sishi, keyin kamayishi kerak."""
        import math
        t_list = list(range(0, 25))
        _, _, C_qon = two_compartment_model(100, ka=1.2, ke=0.1, t_list=t_list)
        max_idx = C_qon.index(max(C_qon))
        # Maksimum 0-chi yoki oxirgi bo'lmasligi kerak
        self.assertGreater(max_idx, 0)
        self.assertLess(max_idx, len(C_qon) - 1)

    def test_ka_equals_ke_special_case(self):
        """ka == ke bo'lganda maxsus holat ishlashi kerak."""
        t_list = [0, 1, 2, 5]
        # Bu ValueError chiqarmasligi kerak
        try:
            _, C_depo, C_qon = two_compartment_model(100, ka=0.1, ke=0.1, t_list=t_list)
            self.assertEqual(len(C_qon), 4)
        except Exception as e:
            self.fail(f"ka==ke holatida xato: {e}")


class EulerMethodTest(TestCase):
    """Eyler usuli testlari."""

    def test_output_length(self):
        """Chiqish uzunligi to'g'ri bo'lishi kerak."""
        t_list, C_list = euler_method(C0=10, k=0.1, t_start=0, t_end=5, h=1)
        self.assertEqual(len(t_list), 6)  # 0,1,2,3,4,5
        self.assertEqual(len(C_list), 6)

    def test_initial_value(self):
        """Birinchi nuqta C0 ga teng bo'lishi kerak."""
        t_list, C_list = euler_method(C0=10, k=0.1, t_start=0, t_end=5, h=1)
        self.assertAlmostEqual(C_list[0], 10.0, places=6)

    def test_no_negative_values(self):
        """Konsentratsiya manfiy bo'lmasligi kerak."""
        t_list, C_list = euler_method(C0=5, k=0.5, t_start=0, t_end=20, h=0.5)
        for c in C_list:
            self.assertGreaterEqual(c, 0)

    def test_decreasing_concentration(self):
        """Konsentratsiya monoton kamayishi kerak."""
        t_list, C_list = euler_method(C0=10, k=0.1, t_start=0, t_end=10, h=1)
        for i in range(1, len(C_list)):
            self.assertLessEqual(C_list[i], C_list[i - 1] + 1e-10)


class RK4MethodTest(TestCase):
    """Runge-Kutta 4 usuli testlari."""

    def test_output_length(self):
        """Chiqish uzunligi to'g'ri bo'lishi kerak."""
        t_list, C_list = rk4_method(C0=10, k=0.1, t_start=0, t_end=5, h=1)
        self.assertEqual(len(t_list), 6)

    def test_rk4_more_accurate_than_euler(self):
        """RK4 Eylerga qaraganda aniqroq bo'lishi kerak."""
        import math
        C0, k, t_end, h = 10.0, 0.1, 10.0, 1.0
        _, C_euler = euler_method(C0, k, 0, t_end, h)
        _, C_rk4 = rk4_method(C0, k, 0, t_end, h)

        # t=10 da analitik qiymat
        C_exact = C0 * math.exp(-k * t_end)
        euler_err = abs(C_euler[-1] - C_exact)
        rk4_err = abs(C_rk4[-1] - C_exact)

        self.assertLess(rk4_err, euler_err)

    def test_rk4_initial_value(self):
        """Birinchi nuqta C0 ga teng bo'lishi kerak."""
        t_list, C_list = rk4_method(C0=8.5, k=0.2, t_start=0, t_end=5, h=0.5)
        self.assertAlmostEqual(C_list[0], 8.5, places=6)


class DetectRiskZoneTest(TestCase):
    """Xavf zonasini aniqlash testlari."""

    def test_toxic_zone(self):
        """Toksik zona to'g'ri aniqlanishi kerak."""
        C_values = [1, 5, 15, 10, 5]  # max=15 > mtc=10
        result = detect_risk_zone(C_values, mic=2.0, mtc=10.0)
        self.assertEqual(result['status'], 'toxic')
        self.assertEqual(result['color'], 'danger')

    def test_subtherapeutic_zone(self):
        """Terapevtik darajadan past zona aniqlanishi kerak."""
        C_values = [0.5, 1.0, 0.8, 0.3]  # max=1.0 < mic=2.0
        result = detect_risk_zone(C_values, mic=2.0, mtc=10.0)
        self.assertEqual(result['status'], 'subtherapeutic')
        self.assertEqual(result['color'], 'warning')

    def test_safe_zone(self):
        """Xavfsiz zona aniqlanishi kerak."""
        C_values = [2.5, 5.0, 8.0, 6.0, 3.0]  # mic=2 < max=8 < mtc=10
        result = detect_risk_zone(C_values, mic=2.0, mtc=10.0)
        self.assertEqual(result['status'], 'safe')
        self.assertEqual(result['color'], 'success')

    def test_empty_list(self):
        """Bo'sh ro'yxat xavfsiz qaytarishi kerak."""
        result = detect_risk_zone([], mic=2.0, mtc=10.0)
        self.assertEqual(result['status'], 'unknown')


class RecommendNextDoseTest(TestCase):
    """Keyingi doza tavsiyasi testlari."""

    def test_returns_time_when_drops_below_mic(self):
        """MIC dan pastga tushganda vaqt qaytarilishi kerak."""
        t_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        C_list = [10, 8, 6, 4, 3, 2.5, 2.0, 1.5, 1.0, 0.5, 0.2]
        result = recommend_next_dose(t_list, C_list, mic=2.0)
        self.assertIsNotNone(result['time'])
        self.assertGreater(result['time'], 0)

    def test_no_time_when_always_above_mic(self):
        """MIC dan pastga tushmasa None qaytarilishi kerak."""
        t_list = [0, 1, 2, 3]
        C_list = [10, 8, 6, 5]  # Hammasi > mic=2
        result = recommend_next_dose(t_list, C_list, mic=2.0)
        self.assertIsNone(result['time'])


class CompareMethodsTest(TestCase):
    """Usullarni solishtirish testlari."""

    def test_rk4_always_less_error(self):
        """RK4 xatosi Eyler xatosidan kichik bo'lishi kerak."""
        result = compare_methods(C0=10.0, k=0.1, t_end=10.0, h=1.0)
        self.assertLess(result['max_rk4_err'], result['max_euler_err'])

    def test_errors_nonnegative(self):
        """Barcha xatolar manfiy bo'lmasligi kerak."""
        result = compare_methods(C0=5.0, k=0.2, t_end=5.0, h=0.5)
        for e in result['euler_errors']:
            self.assertGreaterEqual(e, 0)
        for e in result['rk4_errors']:
            self.assertGreaterEqual(e, 0)


# ─────────────────────────────────────────────────────────────────────────────
# VIEW TESTLARI
# ─────────────────────────────────────────────────────────────────────────────

class IndexViewTest(TestCase):
    """Bosh sahifa view testi."""

    def setUp(self):
        self.client = Client()

    def test_index_get(self):
        """GET / 200 qaytarishi kerak."""
        response = self.client.get(reverse('calculator:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_contains_form(self):
        """Bosh sahifada forma mavjud bo'lishi kerak."""
        response = self.client.get(reverse('calculator:index'))
        self.assertContains(response, 'dosageForm')

    def test_index_contains_mathjax(self):
        """Bosh sahifada MathJax bo'lishi kerak."""
        response = self.client.get(reverse('calculator:index'))
        self.assertContains(response, 'MathJax')


class CalculateViewTest(TestCase):
    """Hisoblash view testi."""

    def setUp(self):
        self.client = Client()
        self.valid_data = {
            'patient_weight': 70,
            'patient_age': 30,
            'drug_name': 'Amoksitsillin',
            'drug_name_custom': '',
            'route': 'oral',
            'dose': 500,
            'model_type': 'one',
            'k': 0.1,
            'ka': 1.2,
            'ke': 0.1,
            'mic': 2.0,
            'mtc': 10.0,
            't_end': 24,
            'h': 1.0,
        }

    def test_calculate_post_valid(self):
        """To'g'ri ma'lumot bilan POST 200 qaytarishi kerak."""
        response = self.client.post(
            reverse('calculator:calculate'),
            self.valid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Natijalar')

    def test_calculate_saves_to_db(self):
        """Hisoblash ma'lumotlar bazasiga saqlanishi kerak."""
        self.client.post(reverse('calculator:calculate'), self.valid_data)
        self.assertEqual(Calculation.objects.count(), 1)

    def test_calculate_two_compartment(self):
        """Ikki kamerali model ham to'g'ri ishlashi kerak."""
        data = self.valid_data.copy()
        data['model_type'] = 'two'
        response = self.client.post(reverse('calculator:calculate'), data)
        self.assertEqual(response.status_code, 200)

    def test_calculate_invalid_mic_mtc(self):
        """MIC >= MTC bo'lganda xato qaytarilishi kerak."""
        data = self.valid_data.copy()
        data['mic'] = 15.0
        data['mtc'] = 10.0
        response = self.client.post(reverse('calculator:calculate'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Xatolik')

    def test_calculate_all_routes(self):
        """Barcha yuborish usullari ishlashi kerak."""
        for route in ('oral', 'injection', 'infusion'):
            data = self.valid_data.copy()
            data['route'] = route
            response = self.client.post(reverse('calculator:calculate'), data)
            self.assertEqual(response.status_code, 200)

    def test_result_contains_chart(self):
        """Natija sahifasida grafik bo'lishi kerak."""
        response = self.client.post(reverse('calculator:calculate'), self.valid_data)
        self.assertContains(response, 'mainChart')

    def test_result_chart_has_datasets(self):
        """Grafik datasetslarida to'g'ri ma'lumot bo'lishi kerak."""
        response = self.client.post(reverse('calculator:calculate'), self.valid_data)
        self.assertContains(response, 'allDatasets')
        self.assertContains(response, 'scatter')

    def test_result_chart_has_mic_mtc_lines(self):
        """Natijada MIC va MTC chiziqlar bo'lishi kerak."""
        response = self.client.post(reverse('calculator:calculate'), self.valid_data)
        self.assertContains(response, 'MIC')
        self.assertContains(response, 'MTC')



class HistoryViewTest(TestCase):
    """Tarix view testi."""

    def setUp(self):
        self.client = Client()

    def test_history_get(self):
        """GET /history/ 200 qaytarishi kerak."""
        response = self.client.get(reverse('calculator:history'))
        self.assertEqual(response.status_code, 200)

    def test_history_shows_calculations(self):
        """Hisoblashlar tarixda ko'rinishi kerak."""
        Calculation.objects.create(
            patient_weight=70,
            patient_age=30,
            drug_name='Test Dori',
            route='oral',
            dose=500,
            model_type='one',
            k=0.1, ka=1.2, ke=0.1,
            mic=2.0, mtc=10.0,
            t_end=24, h=1.0,
            risk_status='safe',
        )
        response = self.client.get(reverse('calculator:history'))
        self.assertContains(response, 'Test Dori')


class AboutViewTest(TestCase):
    """About sahifa testi."""

    def test_about_get(self):
        """GET /about/ 200 qaytarishi kerak."""
        response = self.client.get(reverse('calculator:about'))
        self.assertEqual(response.status_code, 200)

    def test_about_contains_formulas(self):
        """Formulalar sahifada bo'lishi kerak."""
        response = self.client.get(reverse('calculator:about'))
        self.assertContains(response, 'MathJax')


# ─────────────────────────────────────────────────────────────────────────────
# FORMA TESTLARI
# ─────────────────────────────────────────────────────────────────────────────

class DosageFormTest(TestCase):
    """DosageForm validatsiya testlari."""

    def get_valid_data(self):
        return {
            'patient_weight': 70,
            'patient_age': 30,
            'drug_name': 'Paratsetamol',
            'drug_name_custom': '',
            'route': 'oral',
            'dose': 500,
            'model_type': 'one',
            'k': 0.1,
            'ka': 1.2,
            'ke': 0.1,
            'mic': 2.0,
            'mtc': 10.0,
            't_end': 24,
            'h': 1.0,
        }

    def test_valid_form(self):
        """To'g'ri ma'lumot bilan forma valid bo'lishi kerak."""
        form = DosageForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_mic_greater_than_mtc_invalid(self):
        """MIC >= MTC bo'lganda forma invalid bo'lishi kerak."""
        data = self.get_valid_data()
        data['mic'] = 15.0
        data['mtc'] = 10.0
        form = DosageForm(data=data)
        self.assertFalse(form.is_valid())

    def test_h_greater_than_t_end_invalid(self):
        """h >= t_end bo'lganda forma invalid bo'lishi kerak."""
        data = self.get_valid_data()
        data['h'] = 25.0
        data['t_end'] = 24.0
        form = DosageForm(data=data)
        self.assertFalse(form.is_valid())

    def test_custom_drug_required_when_other_selected(self):
        """'Boshqa' tanlanganda qo'lda nom kiritish shart."""
        data = self.get_valid_data()
        data['drug_name'] = 'Boshqa'
        data['drug_name_custom'] = ''
        form = DosageForm(data=data)
        self.assertFalse(form.is_valid())

    def test_negative_weight_invalid(self):
        """Manfiy vazn invalid bo'lishi kerak."""
        data = self.get_valid_data()
        data['patient_weight'] = -5
        form = DosageForm(data=data)
        self.assertFalse(form.is_valid())


# ─────────────────────────────────────────────────────────────────────────────
# MODEL TESTLARI
# ─────────────────────────────────────────────────────────────────────────────

class CalculationModelTest(TestCase):
    """Calculation model testlari."""

    def test_str_representation(self):
        """__str__ metodi to'g'ri ishlashi kerak."""
        calc = Calculation.objects.create(
            patient_weight=70,
            patient_age=30,
            drug_name='Ibuprofen',
            route='oral',
            dose=400,
            model_type='one',
            k=0.1, ka=1.2, ke=0.1,
            mic=2.0, mtc=10.0,
            t_end=24, h=1.0,
        )
        self.assertIn('Ibuprofen', str(calc))

    def test_ordering(self):
        """Hisoblashlar yangi-dan-eskiga tartibda bo'lishi kerak."""
        for name in ['Dori1', 'Dori2', 'Dori3']:
            Calculation.objects.create(
                patient_weight=70, patient_age=30,
                drug_name=name, route='oral', dose=100,
                model_type='one', k=0.1, ka=1.2, ke=0.1,
                mic=2.0, mtc=10.0, t_end=24, h=1.0,
            )
        calcs = list(Calculation.objects.all())
        self.assertEqual(calcs[0].drug_name, 'Dori3')


class DrugModelTest(TestCase):
    """Drug model testlari."""

    def test_drug_creation(self):
        """Drug yaratish ishlashi kerak."""
        drug = Drug.objects.create(
            name='Vankomitsin',
            generic_name='Vancomycin',
            k_default=0.12,
            ka_default=2.0,
            ke_default=0.12,
            mic=10.0,
            mtc=40.0,
            category='antibiotic',
        )
        self.assertEqual(str(drug), 'Vankomitsin')
        self.assertEqual(drug.category, 'antibiotic')
