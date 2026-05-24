from django.db import models


class Drug(models.Model):
    """Dori vositalari uchun ma'lumotlar bazasi modeli."""

    name = models.CharField(max_length=200, verbose_name="Dori nomi")
    generic_name = models.CharField(max_length=200, blank=True, verbose_name="Umumiy nomi")

    # Farmakokinetik parametrlar (standart qiymatlar)
    k_default = models.FloatField(
        default=0.1,
        verbose_name="Eliminatsiya konstantasi k (1/soat)"
    )
    ka_default = models.FloatField(
        default=1.2,
        verbose_name="Absorbsiya konstantasi ka (1/soat)"
    )
    ke_default = models.FloatField(
        default=0.1,
        verbose_name="Eliminatsiya konstantasi ke (1/soat)"
    )

    # Terapevtik oraliq
    mic = models.FloatField(
        default=2.0,
        verbose_name="Minimal terapevtik chegara (mg/L)"
    )
    mtc = models.FloatField(
        default=10.0,
        verbose_name="Maksimal toksik chegara (mg/L)"
    )

    description = models.TextField(blank=True, verbose_name="Tavsif")
    category = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Kategoriya",
        choices=[
            ('antibiotic', 'Antibiotik'),
            ('analgesic', 'Og\'riq qoldiruvchi'),
            ('antihypertensive', 'Gipertoniyaga qarshi'),
            ('antidiabetic', 'Diabetga qarshi'),
            ('cardiac', 'Yurak dori'),
            ('other', 'Boshqa'),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dori"
        verbose_name_plural = "Dorilar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Calculation(models.Model):
    """Hisoblash tarixi modeli."""

    # Bemor ma'lumotlari
    patient_weight = models.FloatField(verbose_name="Bemor vazni (kg)")
    patient_age = models.IntegerField(verbose_name="Bemor yoshi (yil)")

    # Dori ma'lumotlari
    drug_name = models.CharField(max_length=200, verbose_name="Dori nomi")
    route = models.CharField(
        max_length=20,
        verbose_name="Yuborish usuli",
        choices=[
            ('oral', 'Og\'iz orqali (Tabletka)'),
            ('injection', 'Ukol (Injection)'),
            ('infusion', 'Kapelnitsa (Infusion)'),
        ]
    )
    dose = models.FloatField(verbose_name="Doza (mg)")

    # Model turi
    model_type = models.CharField(
        max_length=10,
        verbose_name="Model turi",
        choices=[
            ('one', 'Bir kamerali model'),
            ('two', 'Ikki kamerali model'),
        ]
    )

    # Koeffitsiyentlar
    k = models.FloatField(default=0.1, verbose_name="k — eliminatsiya (1/soat)")
    ka = models.FloatField(default=1.2, verbose_name="ka — absorbsiya (1/soat)")
    ke = models.FloatField(default=0.1, verbose_name="ke — eliminatsiya (1/soat)")

    # Terapevtik chegara
    mic = models.FloatField(default=2.0, verbose_name="MIC (mg/L)")
    mtc = models.FloatField(default=10.0, verbose_name="MTC (mg/L)")

    # Vaqt parametrlari
    t_end = models.FloatField(default=24.0, verbose_name="Vaqt oralig'i (soat)")
    h = models.FloatField(default=1.0, verbose_name="Vaqt qadami (soat)")

    # Natijalar
    risk_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Xavf holati",
        choices=[
            ('toxic', 'Toksik'),
            ('subtherapeutic', 'Terapevtik darajadan past'),
            ('safe', 'Xavfsiz'),
        ]
    )
    max_concentration = models.FloatField(null=True, blank=True, verbose_name="Maksimal konsentratsiya")
    next_dose_time = models.FloatField(null=True, blank=True, verbose_name="Keyingi doza vaqti (soat)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hisoblash"
        verbose_name_plural = "Hisoblashlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.drug_name} — {self.patient_weight}kg — {self.created_at.strftime('%d.%m.%Y %H:%M')}"
