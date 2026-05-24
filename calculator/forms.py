from django import forms


# Dori ro'yxati — standart farmakokinetik koeffitsiyentlar bilan
DRUG_CHOICES = [
    ('', '— Dori turini tanlang —'),
    ('Amoksitsillin', 'Amoksitsillin (Antibiotik)'),
    ('Paratsetamol', 'Paratsetamol (Analgetik)'),
    ('Ibuprofen', 'Ibuprofen (NSAID)'),
    ('Metformin', 'Metformin (Antidiabetik)'),
    ('Enalapril', 'Enalapril (Gipertoniya)'),
    ('Digoksin', 'Digoksin (Yurak glikozidi)'),
    ('Vankomitsin', 'Vankomitsin (Antibiotik)'),
    ('Morfin', 'Morfin (Opioid analgetik)'),
    ('Boshqa', 'Boshqa (qo\'lda kiriting)'),
]

ROUTE_CHOICES = [
    ('oral', '💊 Og\'iz orqali (Tabletka/Kapsul)'),
    ('injection', '💉 Ukol (In\'ektsiya)'),
    ('infusion', '🩸 Kapelnitsa (Infuziya)'),
]

MODEL_CHOICES = [
    ('one', '1️⃣ Bir kamerali model'),
    ('two', '2️⃣ Ikki kamerali model'),
]


class DosageForm(forms.Form):
    """Bemor ma'lumotlari va dori dozasi uchun asosiy forma."""

    # ── Bemor ma'lumotlari ──────────────────────────────────────────────────
    patient_weight = forms.FloatField(
        label='Bemor vazni (kg)',
        min_value=1, max_value=300,
        initial=70,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masalan: 70',
            'id': 'id_patient_weight',
            'step': '0.1',
        })
    )

    patient_age = forms.IntegerField(
        label='Bemor yoshi (yil)',
        min_value=1, max_value=120,
        initial=30,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masalan: 30',
            'id': 'id_patient_age',
        })
    )

    # ── Dori ma'lumotlari ───────────────────────────────────────────────────
    drug_name = forms.ChoiceField(
        label='Dori nomi',
        choices=DRUG_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_drug_name',
        })
    )

    drug_name_custom = forms.CharField(
        label='Dori nomi (qo\'lda)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dori nomini kiriting...',
            'id': 'id_drug_name_custom',
        })
    )

    route = forms.ChoiceField(
        label='Yuborish usuli',
        choices=ROUTE_CHOICES,
        initial='oral',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_route',
        })
    )

    dose = forms.FloatField(
        label='Doza (mg)',
        min_value=0.01,
        initial=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masalan: 500',
            'id': 'id_dose',
            'step': '0.01',
        })
    )

    # ── Model tanlash ────────────────────────────────────────────────────────
    model_type = forms.ChoiceField(
        label='Farmakokinetik model',
        choices=MODEL_CHOICES,
        initial='one',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_model_type',
        })
    )

    # ── Koeffitsiyentlar ────────────────────────────────────────────────────
    k = forms.FloatField(
        label='k — Eliminatsiya konstantasi (1/soat)',
        min_value=0.001,
        initial=0.1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.1',
            'id': 'id_k',
            'step': '0.001',
        })
    )

    ka = forms.FloatField(
        label='ka — Absorbsiya konstantasi (1/soat)',
        min_value=0.001,
        initial=1.2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1.2',
            'id': 'id_ka',
            'step': '0.001',
        })
    )

    ke = forms.FloatField(
        label='ke — Eliminatsiya konstantasi (1/soat)',
        min_value=0.001,
        initial=0.1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.1',
            'id': 'id_ke',
            'step': '0.001',
        })
    )

    # ── Terapevtik chegara ──────────────────────────────────────────────────
    mic = forms.FloatField(
        label='MIC — Minimal terapevtik chegara (mg/L)',
        min_value=0.01,
        initial=2.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2.0',
            'id': 'id_mic',
            'step': '0.01',
        })
    )

    mtc = forms.FloatField(
        label='MTC — Maksimal toksik chegara (mg/L)',
        min_value=0.01,
        initial=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '10.0',
            'id': 'id_mtc',
            'step': '0.01',
        })
    )

    # ── Vaqt parametrlari ───────────────────────────────────────────────────
    t_end = forms.FloatField(
        label='Vaqt oralig\'i (soat)',
        min_value=1,
        max_value=168,
        initial=24,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '24',
            'id': 'id_t_end',
            'step': '1',
        })
    )

    h = forms.FloatField(
        label='Vaqt qadami — h (soat)',
        min_value=0.01,
        max_value=6.0,
        initial=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1.0',
            'id': 'id_h',
            'step': '0.01',
        })
    )

    def clean(self):
        cleaned = super().clean()
        mic = cleaned.get('mic')
        mtc = cleaned.get('mtc')
        h = cleaned.get('h')
        t_end = cleaned.get('t_end')

        if mic and mtc and mic >= mtc:
            raise forms.ValidationError(
                'MIC (minimal terapevtik chegara) MTC dan kichik bo\'lishi kerak!'
            )

        if h and t_end and h >= t_end:
            raise forms.ValidationError(
                'Vaqt qadami (h) vaqt oralig\'idan (T) kichik bo\'lishi kerak!'
            )

        # Dori nomi
        drug_name = cleaned.get('drug_name')
        drug_name_custom = cleaned.get('drug_name_custom')
        if drug_name == 'Boshqa' and not drug_name_custom:
            raise forms.ValidationError(
                'Iltimos, dori nomini qo\'lda kiriting!'
            )

        return cleaned
