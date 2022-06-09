from attrdict import AttrDict
import requests
import datetime
import uuid

class PayPayError(Exception):
    pass

class PayPay(object):
    def __init__(self, access_token=None, device_uuid=None, client_uuid=None, proxy=None):
        self.host = "app4.paypay.ne.jp"
        if device_uuid:
            self.device_uuid = device_uuid
        else:
            self.device_uuid = str(uuid.uuid4()).upper()
        if client_uuid:
            self.client_uuid = device_uuid
        else:
            self.client_uuid = str(uuid.uuid4()).upper()
        self.proxies = proxy
        if self.proxies:
            self.proxies = {
                'http': self.proxies,
                'https': self.proxies,
            }
        response = requests.get("https://api.cokepokes.com/v-api/app/1435783608").json()
        self.headers = {
            'Host': self.host,
            'Client-Version': response[-1]["bundleVersion"],
            'Device-Uuid': self.device_uuid,
            'System-Locale': 'ja',
            'User-Agent': 'PaypayApp/3.43.202205231147 CFNetwork/1126 Darwin/19.5.0',
            'Network-Status': 'WIFI',
            'Device-Name': 'iPhone9,1',
            'Client-Os-Type': 'IOS',
            'Client-Mode': 'NORMAL',
            'Client-Type': 'PAYPAYAPP',
            'Accept-Language': 'ja-jp',
            'Timezone': 'Asia/Tokyo',
            'Accept': '*/*',
            'Client-Uuid': self.client_uuid,
            'Client-Os-Version': '13.5.0',
        }
        if access_token:
            self.headers["Authorization"] = "Bearer " + access_token
        self.params = {
            'payPayLang': 'ja'
        }

    def proxy_check(self):
        response = requests.get("https://api.vxxx.cf/ip", proxies=self.proxies).json()
        return AttrDict(response)

    def login(self, phoneNumber, password):
        json_data = {
            'phoneNumber': phoneNumber,
            'password': password,
            'signInAttemptCount': 1,
        }

        response = requests.post(f'https://{self.host}/bff/v1/signIn', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            self.headers["Authorization"] = "Bearer " + response["payload"]["accessToken"]
            return AttrDict(response)
        elif response['header']['resultCode'] == "S1004":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def login_otp(self, otpReferenceId, otp):
        json_data = {
            'otpReferenceId': otpReferenceId,
            'otp': otp,
        }

        response = requests.post(f'https://{self.host}/bff/v1/signInWithSms', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            self.headers["Authorization"] = "Bearer " + response["payload"]["accessToken"]
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def register(self, phoneNumber, password):
        json_data = {
            'phoneNumber': phoneNumber,
            'password': password,
        }
        
        response = requests.post(f'https://{self.host}/bff/v1/sendRegistrationSms', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def register_otp(self, otpReferenceId, otp):
        json_data = {
            'type': 'PAYPAY',
            'otpReferenceId': otpReferenceId,
            'privacyPolicyVersion': '1.0.2',
            'otp': otp,
        }
        
        response = requests.post(f'https://{self.host}/bff/v1/registerUser', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            self.headers["Authorization"] = "Bearer " + response["payload"]["accessToken"]
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def get_balance(self):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        params = {
            'includeKycInfo': 'true',
            'includePending': 'true',
            'includePendingBonusLite': 'true',
            'includePreAuth': 'true',
            'noCache': 'true',
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v1/getBalanceInfo', params=params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def get_history(self, page_size: int=40):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        params = {
            'pageSize': str(page_size),
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v2/getPay2BalanceHistory', params=params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def get_profile(self):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")

        response = requests.get(f'https://{self.host}/bff/v2/getProfileDisplayInfo', params=self.params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def create_mycode(self):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")

        response = requests.post(f'https://{self.host}/bff/v2/createP2PCode', params=self.params, headers=self.headers, json={}, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def get_payment(self):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")

        response = requests.get(f'https://{self.host}/bff/v2/getPaymentMethodList', params=self.params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def create_paymentcode(self, paymentMethodType="WALLET", paymentMethodId="106177237"):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        json_data = {
            'paymentMethodType': paymentMethodType,
            'paymentMethodId': paymentMethodId,
            'paymentCodeSessionId': str(uuid.uuid4()),
        }

        response = requests.post(f'https://{self.host}/bff/v2/createPaymentOneTimeCodeForHome', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def get_link(self, verificationCode):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        params = {
            'verificationCode': verificationCode,
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v2/getP2PLinkInfo', params=params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def accept_link(self, verificationCode, passcode=None):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        params = {
            'verificationCode': verificationCode,
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v2/getP2PLinkInfo', params=params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            if response["payload"]["orderStatus"] == "PENDING":
                if response["payload"]["pendingP2PInfo"]["isSetPasscode"]:
                    if passcode:
                        json_data = {
                            'verificationCode': verificationCode,
                            'passcode': passcode,
                            'requestId': str(uuid.uuid4()).upper(),
                            'requestAt': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
                            'iosMinimumVersion': '2.55.0',
                            'androidMinimumVersion': '2.55.0',
                            'orderId': response["payload"]["message"]["data"]["orderId"],
                            'senderChannelUrl': response["payload"]["message"]["chatRoomId"],
                            'senderMessageId': response["payload"]["message"]["messageId"],
                        }
                    else:
                        raise PayPayError("REQUIRE_PASSCODE", response["payload"]["orderStatus"])
                else:
                    json_data = {
                        'verificationCode': verificationCode,
                        'requestId': str(uuid.uuid4()).upper(),
                        'requestAt': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
                        'iosMinimumVersion': '2.55.0',
                        'androidMinimumVersion': '2.55.0',
                        'orderId': response["payload"]["message"]["data"]["orderId"],
                        'senderChannelUrl': response["payload"]["message"]["chatRoomId"],
                        'senderMessageId': response["payload"]["message"]["messageId"],
                    }

                response = requests.post('https://app4.paypay.ne.jp/bff/v2/acceptP2PSendMoneyLink', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
                if response['header']['resultCode'] == "S0000":
                    return AttrDict(response)
                else:
                    raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])
            else:
                raise PayPayError("INVALID_STATUS", response["payload"]["orderStatus"])
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def reject_link(self, verificationCode):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        params = {
            'verificationCode': verificationCode,
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v2/getP2PLinkInfo', params=params, headers=self.headers, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            if response["payload"]["orderStatus"] == "PENDING":
                json_data = {
                    'androidMinimumVersion': '2.55.0',
                    'verificationCode': verificationCode,
                    'iosMinimumVersion': '2.55.0',
                    'senderChannelUrl': response["payload"]["message"]["chatRoomId"],
                    'requestAt': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
                    'senderMessageId': response["payload"]["message"]["messageId"],
                    'requestId': str(uuid.uuid4()).upper(),
                    'orderId': response["payload"]["message"]["data"]["orderId"],
                }

                response = requests.post(f'https://{self.host}/bff/v2/rejectP2PSendMoneyLink', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
                if response['header']['resultCode'] == "S0000":
                    return AttrDict(response)
                else:
                    raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])
            else:
                raise PayPayError("INVALID_STATUS", response["payload"]["orderStatus"])
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def execute_link(self, amount:int, passcode=None):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        if passcode:
            json_data = {
                "androidMinimumVersion": "2.55.0",
                "requestId": str(uuid.uuid4()).upper(),
                "requestAt": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
                "theme": "default-sendmoney",
                "amount": int(amount),
                "passcode": passcode,
                "iosMinimumVersion": "2.55.0"
            }
        else:
            json_data = {
                "androidMinimumVersion": "2.55.0",
                "requestId": str(uuid.uuid4()).upper(),
                "requestAt": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
                "theme": "default-sendmoney",
                "amount": int(amount),
                "iosMinimumVersion": "2.55.0"
            }

        response = requests.post(f'https://{self.host}/bff/v2/executeP2PSendMoneyLink', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

    def execute_sendmoney(self, amount, externalReceiverId):
        if not "Authorization" in self.headers:
            raise PayPayError("TOKEN_NOT_SET", "Access token has not been set.")
        json_data = {
            'theme': 'default-sendmoney',
            'androidMinimumVersion': '2.55.0',
            'externalReceiverId': externalReceiverId,
            'amount': int(amount),
            'requestId': str(uuid.uuid4()).upper(),
            'requestAt': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
            'iosMinimumVersion': '2.55.0',
        }

        response = requests.post(f'https://{self.host}/bff/v2/executeP2PSendMoney', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json()
        if response['header']['resultCode'] == "S0000":
            return AttrDict(response)
        else:
            raise PayPayError(response['header']['resultCode'], response['header']['resultMessage'])

