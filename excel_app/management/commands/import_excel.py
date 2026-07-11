import os
import re
from decimal import Decimal, InvalidOperation

import pandas as pd
import jdatetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from excel_app.models import Area, BoardOfTrustee, CertificateType, Neighborhood, SubArea, Fields

class Command(BaseCommand):
    help = 'Import data from Excel file into database'

    @staticmethod
    def _normalize_text(value):
        if value is None:
            return ''
        text = str(value).replace('\u200c', ' ').strip()
        return re.sub(r'\s+', ' ', text)

    @staticmethod
    def _to_english_digits(value):
        if value is None:
            return None
        text = str(value)
        persian = '۰۱۲۳۴۵۶۷۸۹'
        arabic = '٠١٢٣٤٥٦٧٨٩'
        english = '0123456789'
        trans = str.maketrans(persian + arabic, english + english)
        return text.translate(trans)

    def _parse_jalali_date(self, value):
        text = self._normalize_text(value)
        if not text:
            return None
        text = self._to_english_digits(text).replace('-', '/')
        try:
            parts = text.split('/')
            if len(parts) != 3:
                return None
            j_date = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            return j_date.togregorian()
        except Exception:
            return None

    def _parse_jalali_datetime(self, value):
        text = self._normalize_text(value)
        if not text:
            return None
        text = self._to_english_digits(text)
        # Keep only digits and separators, then split date/time parts.
        cleaned = re.sub(r"[^0-9/:\\-\\s]", " ", text)
        cleaned = re.sub(r"\\s+", " ", cleaned).strip()
        if not cleaned:
            return None

        parts = cleaned.split(" ", 1)
        date_part = parts[0].replace("-", "/")
        time_part = parts[1] if len(parts) > 1 else "00:00:00"

        date_tokens = [p for p in date_part.split("/") if p]
        if len(date_tokens) != 3:
            return None

        time_tokens = [p for p in time_part.split(":") if p]
        while len(time_tokens) < 3:
            time_tokens.append("0")
        try:
            j_dt = jdatetime.datetime(
                int(date_tokens[0]),
                int(date_tokens[1]),
                int(date_tokens[2]),
                int(time_tokens[0]),
                int(time_tokens[1]),
                int(time_tokens[2]),
            )
            gregorian_dt = j_dt.togregorian()
            if timezone.is_naive(gregorian_dt):
                return timezone.make_aware(gregorian_dt, timezone=timezone.utc)
            return gregorian_dt
        except Exception:
            return None

    def _parse_decimal(self, value):
        text = self._normalize_text(value)
        if not text:
            return None
        text = self._to_english_digits(text).replace(',', '')
        try:
            return Decimal(text)
        except (InvalidOperation, ValueError):
            return None

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')
        parser.add_argument(
            '--truncate',
            action='store_true',
            help='Delete existing Area/SubArea/Fields data before import',
        )

    def _get_or_create_board_member(self, board_name):
        member = BoardOfTrustee.objects.filter(name=board_name).first()
        if member:
            return member

        if BoardOfTrustee.objects.count() >= 24:
            raise ValueError("BoardOfTrustee catalog exceeds 24 unique records.")
        return BoardOfTrustee.objects.create(name=board_name)

    def handle(self, *args, **options):
        file_path = options['excel_file']
        if not os.path.exists(file_path):
            self.stderr.write(f"File not found: {file_path}")
            return

        if options['truncate']:
            self.stdout.write("Truncating existing data...")
            Fields.objects.all().delete()
            CertificateType.objects.all().delete()
            BoardOfTrustee.objects.all().delete()
            Neighborhood.objects.all().delete()
            SubArea.objects.all().delete()
            Area.objects.all().delete()

        self.stdout.write("Reading Excel file...")
        df = pd.read_excel(file_path, header=0, dtype=str)  
        df.columns = [self._normalize_text(col) for col in df.columns]

        
        if 'منطقه' not in df.columns:
            self.stderr.write('Required column "منطقه" not found in Excel.')
            return
        if 'ناحیه' not in df.columns:
            self.stderr.write('Required column "ناحیه" not found in Excel.')
            return
        if 'محله' not in df.columns:
            self.stderr.write('Required column "محله" not found in Excel.')
            return
        df['منطقه'] = df['منطقه'].ffill()
        df['ناحیه'] = df['ناحیه'].ffill()
        df['محله'] = df['محله'].ffill()

        
        column_mapping = {
            'ناحیه': 'subarea_name',          
            'محله': 'neighborhood_name',     
            'هیات امناء': 'board_of_trustees_name',
            'تاریخ ویرایش': 'edit_time',
            'نام(1)': 'first_name',
            'نام خانوادگي(2)': 'last_name',
            'نام پدر(3)': 'father_name',
            'کد ملی(4)': 'national_code',
            'شماره شناسنامه(5)': 'birth_certificate_number',
            'تاریخ تولد(6)': 'birth_date',
            'شماره تلفن همراه(7)': 'phone_number',
            'شماره تلفن همراه مجازی(8)': 'social_phone_number',
            'شماره تلفن ثابت(9)': 'landline_number',
            'مدرک تحصیلی(10)': 'certificate_type_name',
            'رشته تحصیلی(11)': 'major',
            'آدرس محل سکونت(12)': 'address',
            'کد پستی(13)': 'postal_code',
            'نوع سکونت در محله(14)': 'neighborhood_type',
            'بکارگیری مدیر محله(15)': 'manager_engagement',
            'رئیس - نایب رئیس(16)': 'president_or_vice',
            'تاریخ انتخابات(17)': 'election_date',
            'شماره نامه -انتخابات(18)': 'election_letter_number',
            'شماره حکم(19)': 'decree_number',
            'تاریخ حکم(20)': 'decree_date',
            'تحویل حکم به  منطقه(21)': 'decree_delivery_to_region', 
            'تاریخ تحویل حکم به منطقه(22)': 'decree_delivery_date',
            'توضیحات حکم(23)': 'decree_notes',
            'آدرس سرای محله(24)': 'neighborhood_address',
            'کدپستی سرای محله(25)': 'postal_code_neighborhood',
            'تلفن 1 سرای محله(26)': 'phone_1',
            'تلفن 2 سرای محله(27)': 'phone_2',
            'تلفن 3  سرای محله(28)': 'phone_3',    
            'نمابر(29)': 'fax',
            'شماره نامه معرفی معتمدین از طرف عضو ستاد(30)': 'member_letter_number',
            'تاریخ نامه معرفی معتمدین از طرف عضو ستاد': 'member_letter_date',
            'شماره نامه معرفی معتمدین به شهردارتهران': 'mayor_letter_number',
            'تاریخ نامه معرفی به شهردار تهران': 'mayor_letter_date',
            'شماره نامه صدور حکم معتمدین به زاکانی': 'zakani_letter_number',
            'تاریخ نامه صدورحکم معتمدین به زاکانی': 'zakani_letter_date',
            'شماره استعلام از دستگاه نظارتی': 'supervision_request_number',
            'تاریخ استعلام از دستگاه نظارتی': 'supervision_request_date',
            'شماره نامه جوابیه دستگاه نظارتی': 'supervision_reply_number',
            'تاریخ نامه جوابیه دستگاه نظارتی': 'supervision_reply_date',
            'وضعیت نظارتی': 'supervision_status',
            'صدورحکم': 'decree_issued',
            'پرداخت عیدی1403': 'bonus_1403',
            'تاریخ پرداخت1403': 'bonus_1403_date',
            'حساب بانک شهر': 'bank_account',
            'عیدی 1404': 'bonus_1404',
            'توضیحات': 'bonus_notes',
        }

        normalized_mapping = {
            self._normalize_text(excel_col): model_field
            for excel_col, model_field in column_mapping.items()
        }
        existing_mapped_columns = [
            col for col in normalized_mapping.keys() if col in df.columns
        ]
        missing_cols = sorted(
            [col for col in normalized_mapping.keys() if col not in df.columns]
        )
        if missing_cols:
            self.stdout.write(
                f"Warning: {len(missing_cols)} optional columns not found and will be skipped."
            )

        success_count = 0
        error_count = 0

        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # دریافت یا ایجاد منطقه
                    area_name = row.get('منطقه')
                    if pd.isna(area_name):
                        self.stderr.write(f"Skipping row {index+2}: no region")
                        continue
                    area, _ = Area.objects.get_or_create(
                        name=self._normalize_text(area_name)
                    )

                    subarea_name = row.get('ناحیه')
                    if pd.isna(subarea_name):
                        self.stderr.write(f"Skipping row {index+2}: no subarea")
                        continue
                    subarea_name = self._normalize_text(subarea_name)
                    subarea, _ = SubArea.objects.get_or_create(
                        name=subarea_name,
                        area=area,
                    )

                    neighborhood_name = self._normalize_text(row.get('محله'))
                    if not neighborhood_name:
                        self.stderr.write(f"Skipping row {index+2}: no neighborhood")
                        continue
                    neighborhood, _ = Neighborhood.objects.get_or_create(
                        name=neighborhood_name,
                        sub_area=subarea,
                    )

                    board_name_raw = row.get('هیات امناء')
                    board_name = self._normalize_text(board_name_raw)
                    board_member = None
                    if board_name:
                        board_member = self._get_or_create_board_member(board_name)

                    cert_name_raw = row.get('مدرک تحصیلی(10)')
                    cert_name = self._normalize_text(cert_name_raw)
                    certificate = None
                    if cert_name:
                        certificate, _ = CertificateType.objects.get_or_create(name=cert_name)

                    data = {
                        'sub_area': subarea,
                        'neighborhood': neighborhood,
                        'board_of_trustees': board_member,
                        'certificate_type': certificate,
                    }
                    for excel_col in existing_mapped_columns:
                        model_field = normalized_mapping[excel_col]
                        if model_field in ['subarea_name', 'neighborhood_name', 'board_of_trustees_name', 'certificate_type_name']:
                            continue
                        value = row.get(excel_col)
                        if pd.isna(value):
                            value = None
                        else:
                            value = self._normalize_text(value) if isinstance(value, str) else value
                            if value == '':
                                value = None

                        # تبدیل تاریخ‌های شمسی به میلادی
                        if model_field == 'edit_time' and value:
                            data[model_field] = self._parse_jalali_datetime(value)
                        elif model_field.endswith('_date') and value:
                            data[model_field] = self._parse_jalali_date(value)
                        elif model_field in ['bonus_1403', 'bonus_1404'] and value:
                            data[model_field] = self._parse_decimal(value)
                        else:
                            data[model_field] = value

                    Fields.objects.create(**data)
                    success_count += 1

                    if success_count % 100 == 0:
                        self.stdout.write(f"{success_count} records imported...")

            except Exception as e:
                error_count += 1
                self.stderr.write(f"Error at row {index+2}: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Import completed. Success: {success_count}, Errors: {error_count}"
        ))
