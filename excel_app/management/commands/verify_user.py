from excel_app.models import Fields
from django.core.management.base import BaseCommand, CommandError
import requests
from utils.config import loadenv
from dotenv import load_dotenv
from os import getenv

load_dotenv(loadenv())


headers = {
    "Content-Type": "application/json;charset=UTF-8"
}

class Command(BaseCommand):
    help = "Create a user with username/password"

    def handle(self, *args, **options):
        uid_api_url = getenv("UID_API_URL")
        if not uid_api_url:
            raise CommandError("UID_API_URL is not configured in environment.")
      

        for field in Fields.objects.all():
            national_code = field.national_code
            birth_date = field.birth_date
            if not field.is_verified and national_code and birth_date:
                birth_date_value = birth_date.isoformat() if hasattr(birth_date, "isoformat") else str(birth_date)
                payload = {
                "requestContext": {
                    "apiInfo": {
                        "businessId": getenv("BUSINESS_ID"),   
                        "businessToken": getenv("BUSINESS_TOKEN") 
                    }
                },
                "nationalId": national_code,
                "birthDate": birth_date_value
                }
                

                response = requests.post(uid_api_url, headers=headers, json=payload, timeout=30)

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                    except ValueError:
                        self.stdout.write(self.style.ERROR("پاسخ API معتبر نیست (JSON نامعتبر)."))
                        self.stdout.write(response.text)
                        continue

                    status_code = (
                        response_data.get("responseContext", {})
                        .get("status", {})
                        .get("code")
                    )
                    if status_code != 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f"استعلام ناموفق برای کدملی {national_code}: {response_data}"
                            )
                        )
                        continue

                    basic_info = response_data.get("basicInformation", {})
                    first_name = basic_info.get("firstName")
                    last_name = basic_info.get("lastName")
                    father_name = basic_info.get("fatherName")
                    api_gender = basic_info.get("gender")
                    gender_map = {
                        "GENDER_MALE": Fields.GenderType.MAN,
                        "GENDER_FEMALE": Fields.GenderType.WOMAN,
                    }
                    gender = gender_map.get(api_gender)

                    if first_name:
                        field.first_name = first_name
                    if last_name:
                        field.last_name = last_name
                    if father_name:
                        field.father_name = father_name
                    if gender:
                        field.gender = gender
                    field.is_verified = True
                    field.save(update_fields=["first_name", "last_name", "father_name", "gender", "is_verified"])
                    self.stdout.write(
                        self.style.SUCCESS(f"تایید شد: کدملی {national_code}")
                    )
                else:
                    print(f"خطا (کد {response.status_code}):")
                    print(response.text)
    
