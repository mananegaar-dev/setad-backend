from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.conf import settings
import django_jalali.db.models as jmodels


class Area(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="منطقه")

    def __str__(self):
        return self.name
    
class SubArea(models.Model):
    name = models.CharField(max_length=50, verbose_name="ناحیه")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="sub_areas")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["area", "name"],
                name="unique_subarea_per_area",
            )
        ]

    def __str__(self):
        return f"{self.area.name} - {self.name}"



class Neighborhood(models.Model):
    name = models.CharField(max_length=100)
    sub_area = models.ForeignKey(SubArea, on_delete=models.CASCADE, related_name="neighborhoods")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sub_area", "name"],
                name="unique_neighborhood_per_subarea",
            )
        ]

    def __str__(self):
        return f"{self.sub_area.area.name} - {self.sub_area.name} - {self.name}"


class BoardOfTrusteeCategory(models.Model):
    name = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return self.name

class BoardOfTrustee(models.Model):
    name = models.CharField(max_length=100)
    board_of_Trustee_category = models.ForeignKey(BoardOfTrusteeCategory, on_delete=models.SET_NULL, related_name="board_of_Trustee_category", null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_board_member_name",
            )
        ]

    def clean(self):
        if not self.pk:
            current_count = BoardOfTrustee.objects.count()
            if current_count >= 24:
                raise ValidationError("Board of trustees catalog can have at most 24 records.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CertificateType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Fields(models.Model):
    class GenderType(models.TextChoices):
        MAN = 'مرد', 'مرد'
        WOMAN = 'زن', 'زن'


    class StatusType(models.TextChoices):
        ACTIVE = 'فعال', 'فعال'
        INACTIVE = 'غیرفعال', 'غیرفعال'
        PENDING = 'درحال بررسی', 'درحال بررسی'
        RESERVATION = 'رزرو', 'رزرو'


    sub_area = models.ForeignKey(SubArea, on_delete=models.CASCADE, related_name="fields", verbose_name="ناحیه")
    gender = models.CharField(
        max_length=10,
        choices=GenderType.choices,
        default=None,
        blank=True,
        null=True,
        verbose_name="جنسیت"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusType.choices,
        default=StatusType.PENDING,
        blank=True,
        null=True,
        verbose_name="وضعیت"
    )
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.SET_NULL,
        related_name="fields",
        blank=True,
        null=True,
        verbose_name="محله",
    )
    board_of_trustees = models.ForeignKey(
        BoardOfTrustee,
        on_delete=models.SET_NULL,
        related_name="fields",
        blank=True,
        null=True,
        verbose_name="هیئت امناء",
    )
    edit_time = jmodels.jDateTimeField(blank=True, null=True, verbose_name="زمان آخرین ویرایش", auto_now=True)
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="edited_fields",
        blank=True,
        null=True,
        verbose_name="آخرین ویرایش‌کننده",
    )
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام")
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام خانوادگی")
    father_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام پدر")
    national_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="کد ملی")
    is_verified = models.BooleanField(default=False,verbose_name="احرازهویت شده")

    birth_certificate_number = models.CharField(blank=True, null=True, verbose_name="شماره شناسنامه")
    birth_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تولد")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="شماره موبایل")
    social_phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="شماره موبایل اجتماعی")
    landline_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="تلفن ثابت")

    certificate_type = models.ForeignKey(
        CertificateType,
        on_delete=models.SET_NULL,
        related_name="fields",
        blank=True,
        null=True,
        verbose_name="نوع مدرک تحصیلی",
    )

    major = models.CharField(max_length=100, blank=True, null=True, verbose_name="رشته تحصیلی")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="کد پستی")


    neighborhood_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="نوع سکونت در محله")
    manager_engagement = models.CharField(max_length=100, blank=True, null=True, verbose_name="بکارگیری مدیر محله")
    president_or_vice = models.CharField(max_length=100, blank=True, null=True, verbose_name="رئیس - نایب رئیس")
    election_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ انتخابات")
    election_letter_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره نامه انتخابات")
    decree_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره حکم")
    decree_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ حکم")
    decree_delivery_to_region = models.CharField(max_length=100, blank=True, null=True, verbose_name="تحویل حکم به منطقه")
    decree_delivery_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تحویل حکم به منطقه")
    decree_notes = models.TextField(blank=True, null=True, verbose_name="توضیحات حکم")


    neighborhood_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="آدرس سرای محله")
    postal_code_neighborhood = models.CharField(max_length=20, blank=True, null=True, verbose_name="کدپستی سرای محله")
    phone_1 = models.CharField(max_length=20, blank=True, null=True, verbose_name="تلفن 1 سرای محله")
    phone_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="تلفن 2 سرای محله")
    phone_3 = models.CharField(max_length=20, blank=True, null=True, verbose_name="تلفن 3 سرای محله")
    fax = models.CharField(max_length=20, blank=True, null=True, verbose_name="نمابر")

    member_letter_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره نامه معرفی معتمدین از طرف عضو ستاد")
    member_letter_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ نامه معرفی معتمدین از طرف عضو ستاد")
    mayor_letter_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره نامه معرفی معتمدین به شهردار تهران")
    mayor_letter_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ نامه معرفی به شهردار تهران")
    zakani_letter_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره نامه صدور حکم معتمدین به زاکانی")
    zakani_letter_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ نامه صدور حکم معتمدین به زاکانی")

    supervision_request_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره استعلام از دستگاه نظارتی")
    supervision_request_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ استعلام از دستگاه نظارتی")
    supervision_reply_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="شماره نامه جوابیه دستگاه نظارتی")
    supervision_reply_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ نامه جوابیه دستگاه نظارتی")
    supervision_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="وضعیت نظارتی")
    decree_issued = models.CharField(max_length=100, blank=True, null=True, verbose_name="صدور حکم")

    bonus_1403 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="پرداخت عیدی 1403")
    bonus_1403_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ پرداخت 1403")
    bank_account = models.CharField(max_length=50, blank=True, null=True, verbose_name="حساب بانک شهر")
    bonus_1404 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="عیدی 1404")
    bonus_notes = models.TextField(blank=True, null=True, verbose_name="توضیحات پرداخت")

    class Meta:
        indexes = [
            GinIndex(
                fields=["first_name"],
                name="fields_first_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["last_name"],
                name="fields_last_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def save(self, *args, **kwargs):
        if self.neighborhood_id:
            self.sub_area = self.neighborhood.sub_area
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.neighborhood_address or 'بدون آدرس'} - {self.neighborhood_type or 'بدون نوع محله'}"
