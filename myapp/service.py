import requests
from django.conf import settings
import logging
import json
import random

logger = logging.getLogger(__name__)
class PayVesselService:
    @staticmethod
    def generate_virtual_account(user, first_name, last_name, phone_number):
        headers = {
          'api-key': settings.PAYVESSEL_API_KEY,
          'api-secret': f'Bearer {settings.PAYVESSEL_SECRET_KEY}',
         'Content-Type': 'application/json'
}
        number = random.randint(10**10, 10**11 - 1)
        data = {
        "account_type": "STATIC",
        "email": user.email,
        "name": f"{first_name} {last_name}",
        "phoneNumber": "08080891605",
        "bankcode": [999991],
        "nin":number,
        "businessid": settings.BUSINESS_ID
       }
        response = requests.post(settings.PAYVESSEL_BASE_URL, headers=headers, data=json.dumps(data))
        response_data = response.json()
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response data: {response_data}")

        if response.status_code == 201 or response.status_code == 200:
            return response_data
        else:
            error_message = response_data.get('message', 'Unknown error')
            logger.error(f"PayVessel API error: {error_message}")
            raise Exception(f"PayVessel API error: {error_message}")
            
            
            
  

