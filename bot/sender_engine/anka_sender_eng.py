import requests
import os
from dotenv import load_dotenv
import re


load_dotenv()

class AnkarexSender:

    def __init__(self, sms_informations) -> None:
        self.api_key = os.getenv('API_KEY')
        self.api = os.getenv('API')
        self.sms_informations = sms_informations
        self.post_header = {
            'method': 'POST',
            "Content-Type": "application/json",
            "User-Agent": "Ankarex-Rest-0.22"
        }
        self.sender_response = None
        self.valid_numbers = ''

    def __filter_blacklisted_number(self) -> list:
        filter_data = {
            'token': self.api_key,
            'status': 'blacklist'
        }
        response = requests.post(self.api, json=filter_data, headers=self.post_header)
        return response

    def __check_blacklisted_nums(self) -> bool:
        filtered_response = self.__filter_blacklisted_number()
        xms = filtered_response.json()['blacklist']
        filter_numbers = [ blacklisted_number_pack['url'] for blacklisted_number_pack in xms]

        numbers = re.findall(r"\d+", self.sms_informations['phone_number'])
        for number in numbers:
            if re.sub(r"\D", "", self.sms_informations['phone_number']) in filter_numbers:
                return True
            else:
                self.valid_numbers += number +','


    def send_sms(self) -> None:

        phone_number_validator = self.__check_blacklisted_nums()
        if not phone_number_validator:
            sending_data = {
                'token': self.api_key,
                'send': 'bulk',
                'to': self.valid_numbers,
                'sender_id': self.sms_informations['sid'],
                "message_content": self.sms_informations['message'],
                'unicode': False
            }
            response = requests.post(self.api, json=sending_data, headers=self.post_header)
            self.sender_response = response.json()
        else:
            self.sender_response = 'blacklisted'

        return self.sender_response





