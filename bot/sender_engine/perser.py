import requests
import json


class MessageParser:

    def __init__(self) -> list:
        self.route_found = False

    def get_routes(self) -> str:
        request = requests.get(
            f'{self.api}/v2/routes',
            headers={
                "Authorization": f"bearer {self.api_key}"
            }
        )
        routes =  request.json()["data"]
        active_route = {}
        for elements in routes:
            if self.recipient_numbers[0].startswith(elements["prefix"].replace("+", "")):
                active_route = elements
                self.route_found = True
                return active_route["id"]
            else:
                self.route_found = False

    def fetch_available_routes(self) -> list:
        routes_id = self.get_routes()
        request = requests.get(
            f'{self.api}/v2/routes/{routes_id}/options',
            headers={
                "Authorization": f"bearer {self.api_key}"
            }
        )
        response = request.json()
        print(response)
        return response["data"]

    def number_validator(self) -> list:
        request = requests.post(
            f"{self.api}/v2/number-lists/validate",
            headers={
                "Authorization": f"bearer {self.api_key}",
                "context-type": "application/json"
            },
            data = json.dumps({ "numbers": self.recipient_numbers }).encode('utf-8')
        )

        response = request.json()
        print("response: ", response)
        return response["data"]["valid"]



