import re
import random

class SMSDetails:

    def __init__(self, text: str) -> None:
        self.text = text
    
        self.sid = ''
        self.sms_details_response = ''

    def crop_out_content(self) -> str:
        sid_match = re.search(r"\*{0,2}SID:\*{0,2}\s*`?([^`\n]*)`?", self.text, re.I)
        phone_match = re.search(r"\*{0,2}PHONE:\*{0,2}\s*`?([^`\n]*)`?", self.text, re.I)
        message_match = re.search(r"\*{0,2}Message:\*{0,2}\s*`?([^`\n]*)`?", self.text, re.I)
        route_match = re.search(r"\*{0,2}ROUTE_ID:\*{0,2}\s*`?([^`\n]*)`?", self.text, re.I)

        extracted_content = {
            "phone_number": phone_match.group(1).strip() if phone_match else "",
            "message": message_match.group(1).strip() if message_match else "",
            "sid": sid_match.group(1).strip() if sid_match else "",
            "route_id": route_match.group(1).strip() if route_match else "none"
        }

        print(extracted_content)
        return extracted_content
            
    def sms_details_composer(self) -> str:
        sms_details = self.crop_out_content()

    
        if sms_details['phone_number']:  
            
            try:
                fixed_number = sms_details['phone_number'].replace(' ', ',')

                phone_number_list = list(map(str, fixed_number.split(',')))

                digits = list(phone_number_list[0])
                positions = [i for i, c in enumerate(phone_number_list[0]) if c.isdigit()]
                for i in positions[-5:]:
                    digits[i] = str(random.randint(0, 9))

                sid =  ''.join(digits)

                if sms_details['sid'] == '' or sms_details['sid'] == 'None':
                    self.sid = sid
                else:
                    self.sid = sms_details['sid']


                return {
                    'phone_number': fixed_number,
                    "message" : sms_details['message'],
                    "sid": self.sid,
                    'route_id': sms_details['route_id']
                }
                
            except ValueError:
                return "Error: Caption contains non-numeric values."

        else:
            return 'Not Found'
        
        
        
            
           