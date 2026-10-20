import requests
import os
from dotenv import load_dotenv
import re
import json
from .perser import MessageParser
import uuid
load_dotenv()

def generate_idempotency_key() -> str:
    return str(uuid.uuid4())

class AnkarexSender(MessageParser):

    def __init__(self) -> None:
        self.post_header = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.sender_response = None
        self.response_title = ""
        self.valid_numbers = ''
        self.recipient_numbers = []
        super().__init__()

    def __check_blacklisted_nums(self) -> bool:
        result = self.number_validator()
        return result

    def serve_routes_worker(self) -> None:
        self.recipient_numbers = re.findall(r"\d+", self.sms_detail['phone_number'])
        self.get_routes()
        phone_number = self.number_validator()
        if not self.route_found and phone_number:
            idempotency_key = generate_idempotency_key()
            headers = {
                **self.post_header,
                "Idempotency-Key": idempotency_key,
            }
            sending_data = json.dumps({
                "to": phone_number,
                "text": self.sms_detail['message'],
                "sender_id": self.sms_detail["sid"]
            }).encode('utf-8')
            response = requests.post(f"{self.api}/v2/messages", headers=headers,  data=sending_data)
            self.sender_response = response.json()
            self.response_title = list(self.sender_response.keys())[0]
        else:
            return "blacklist"




    def send_message(self, route_option: str, sms_contents) -> str:
        phone_number_validator = self.__check_blacklisted_nums()
        print(route_option)
        if phone_number_validator:
            idempotency_key = generate_idempotency_key()
            headers = {
                **self.post_header,
                "Idempotency-Key": idempotency_key,
            }
            sending_data = json.dumps({
                "to": phone_number_validator,
                "text": sms_contents['message'],
                "option": route_option,
                "sender_id": sms_contents["sid"]
            }).encode('utf-8')
            response = requests.post(f"{self.api}/v2/messages", headers=headers,  data=sending_data)
            self.sender_response = response.json()
            self.response_title = list(self.sender_response.keys())[0]
        else:
            self.response_title = 'blacklisted'






