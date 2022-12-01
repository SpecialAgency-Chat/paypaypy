from bs4 import BeautifulSoup
import requests
import urllib.parse
import datetime
import pkce
import uuid
import json

def get_application():
    response = requests.get('https://apps.apple.com/jp/app/paypay-%E3%83%9A%E3%82%A4%E3%83%9A%E3%82%A4/id1435783608')
    soup = BeautifulSoup(response.text, 'html.parser')
    application = json.loads(list(json.loads(soup.find('script', attrs={'id': 'shoebox-media-api-cache-apps'}).text).values())[0])
    return application

class AttributeDict(object):
    def __init__(self, obj):
        self.obj = obj

    def __getstate__(self):
        return self.obj.items()

    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    def __getattr__(self, name):
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    def fields(self):
        return self.obj

    def keys(self):
        return self.obj.keys()

class PayPayError(Exception):
    pass

class PayPay(object):
    def __init__(self, access_token: str = None, device_uuid: str = str(uuid.uuid4()), client_uuid: str = str(uuid.uuid4()), proxy: str = None) -> None:
        self.host = "app4.paypay.ne.jp"
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.version = get_application()['d'][0]['attributes']['platformAttributes']['ios']['versionHistory'][0]['versionDisplay']
        self.params = {
            'payPayLang': 'ja'
        }
        self.headers = {
            'Host': self.host,
            'Timezone': 'Asia/Tokyo',
            'Client-OS-Type': 'ANDROID',
            'Device-Name': 'Pixel 3 XL',
            'Is-Emulator': 'false',
            'Client-OS-Version': '32.0.0',
            'User-Agent': f'PaypayApp/{self.version} Android12',
            'Client-Version': self.version,
            'System-Locale': 'ja',
            'Device-UUID': device_uuid,
            'Client-Mode': 'NORMAL',
            'Client-Type': 'PAYPAYAPP',
            'Network-Status': 'WIFI',
            'Client-UUID': client_uuid,
            'Connection': 'Keep-Alive',
        }
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
        self.session = requests.Session()

    def login(self, phoneNumber: str, password: str) -> AttributeDict:
        self.verifier, self.challenge = pkce.generate_pkce_pair(code_verifier_length=43)
        data = {
            'clientId': 'pay2-mobile-app-client',
            'clientAppVersion': self.version,
            'clientOsVersion': '32.0.0',
            'clientOsType': 'ANDROID',
            'responseType': 'code',
            'redirectUri': 'paypay://oauth2/callback',
            'state': pkce.generate_code_verifier(length=43),
            'codeChallenge': self.challenge,
            'codeChallengeMethod': 'S256',
            'scope': 'REGULAR',
            'tokenVersion': 'v1',
            'prompt': 'create',
            'uiLocales': 'ja',
        }

        response = requests.post(f'https://{self.host}/bff/v2/oauth2/par', params=self.params, headers=self.headers, data=data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != 'S0000':
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        params = {
            'client_id': 'pay2-mobile-app-client',
            'request_uri': response.payload.requestUri,
        }

        self.session.get('https://www.paypay.ne.jp/portal/api/v2/oauth2/authorize', params=params, proxies=self.proxies)

        headers = {
            'Host': 'www.paypay.ne.jp',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Client-Os-Version': '32.0.0',
            'Client-Version': self.version,
            'User-Agent': f'Mozilla/5.0 (Linux; Android 12; Pixel 3 XL Build/SQ3A.220705.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/106.0.5249.126 Mobile Safari/537.36 jp.pay2.app.android/{self.version}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Client-Os-Type': 'ANDROID',
            'Client-Id': 'pay2-mobile-app-client',
            'Client-Type': 'PAYPAYAPP',
            'Origin': 'https://www.paypay.ne.jp',
            'X-Requested-With': 'jp.ne.paypay.android.app',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.paypay.ne.jp/portal/oauth2/sign-in?mode=landing',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        json_data = {
            'username': phoneNumber,
            'password': password,
            'signInAttemptCount': 1,
        }

        response = self.session.post('https://www.paypay.ne.jp/portal/api/v2/oauth2/sign-in/password', headers=headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != 'S0000':
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def login_otp(self, otp: str) -> AttributeDict:
        if not all(key in self.session.cookies for key in ['Lang', '__Secure-request_uri', '__Secure-otpReferenceId']):
            raise PayPayError('S9999', '先にログインを行ってください')

        headers = {
            'Host': 'www.paypay.ne.jp',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Client-Os-Version': '32.0.0',
            'Client-Version': self.version,
            'User-Agent': f'Mozilla/5.0 (Linux; Android 12; Pixel 3 XL Build/SQ3A.220705.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/106.0.5249.126 Mobile Safari/537.36 jp.pay2.app.android/{self.version}',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Client-Os-Type': 'ANDROID',
            'Client-Id': 'pay2-mobile-app-client',
            'Client-Type': 'PAYPAYAPP',
            'Origin': 'https://www.paypay.ne.jp',
            'X-Requested-With': 'jp.ne.paypay.android.app',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.paypay.ne.jp/portal/oauth2/otp?mode=navigation',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        json_data = {
            'otp': otp
        }

        response = self.session.post('https://www.paypay.ne.jp/portal/api/v2/oauth2/sign-in/2fa/validate-otp', headers=headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != 'S0000':
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(response.payload.redirectUrl).query))

        data = {
            'clientId': 'pay2-mobile-app-client',
            'redirectUri': 'paypay://oauth2/callback',
            'code': params['code'],
            'codeVerifier': self.verifier,
        }

        response = requests.post(f'https://{self.host}/bff/v2/oauth2/token', params=self.params, headers=self.headers, data=data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != 'S0000':
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        self.headers['Authorization'] = f'Bearer {response.payload.accessToken}'
        return response

    def register(self, phoneNumber, password):
        json_data = {
            'phoneNumber': phoneNumber,
            'password': password,
        }
        
        response = requests.post(f'https://{self.host}/bff/v1/sendRegistrationSms', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def register_otp(self, otpReferenceId, otp):
        json_data = {
            'type': 'PAYPAY',
            'otpReferenceId': otpReferenceId,
            'privacyPolicyVersion': '1.0.2',
            'otp': otp,
        }
        
        response = requests.post(f'https://{self.host}/bff/v1/registerUser', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response['header']['resultCode'] == "S0000":
            self.headers["Authorization"] = "Bearer " + response["payload"]["accessToken"]
            return response
        else:
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

    def get_balance(self):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        params = {
            'includeKycInfo': 'true',
            'includePending': 'true',
            'includePendingBonusLite': 'true',
            'includePreAuth': 'true',
            'noCache': 'true',
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v1/getBalanceInfo', params=params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def get_history(self, page_size: int=40):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        params = {
            'pageSize': str(page_size),
            'payPayLang': 'ja',
        }

        response = requests.get(f'https://{self.host}/bff/v2/getPay2BalanceHistory', params=params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def get_profile(self):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')

        response = requests.get(f'https://{self.host}/bff/v2/getProfileDisplayInfo', params=self.params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def create_mycode(self):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')

        response = requests.post(f'https://{self.host}/bff/v2/createP2PCode', params=self.params, headers=self.headers, json={}, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def get_payment(self):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')

        response = requests.get(f'https://{self.host}/bff/v2/getPaymentMethodList', params=self.params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def create_paymentcode(self, paymentMethodType="WALLET", paymentMethodId="106177237"):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        json_data = {
            'paymentMethodType': paymentMethodType,
            'paymentMethodId': paymentMethodId,
            'paymentCodeSessionId': str(uuid.uuid4()),
        }

        response = requests.post(f'https://{self.host}/bff/v2/createPaymentOneTimeCodeForHome', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def get_link(self, verificationCode):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        params = {**self.params, 'verificationCode': verificationCode}

        response = requests.get(f'https://{self.host}/bff/v2/getP2PLinkInfo', params=params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def accept_link(self, verificationCode, passcode=None):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        params = {**self.params, 'verificationCode': verificationCode}

        response = requests.get(f'https://{self.host}/bff/v2/getP2PLinkInfo', params=params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)
        if response.payload.orderStatus != 'PENDING':
            raise PayPayError('S9999', 'このリンクは既に処理されています。')
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
        if response.payload.pendingP2PInfo.isSetPasscode:
            if not passcode:
                raise PayPayError('S9999', 'パスコードが必要です。')
            json_data['passcode'] = passcode
        response = requests.post(f'https://{self.host}/bff/v2/acceptP2PSendMoneyLink', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)
        return response

    def reject_link(self, verificationCode):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        params = {**self.params, 'verificationCode': verificationCode}

        response = requests.get(f'https://{self.host}/bff/v2/getP2PLinkInfo', params=params, headers=self.headers, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)
        if response.payload.orderStatus != 'PENDING':
            raise PayPayError('S9999', 'このリンクは既に処理されています。')
        json_data = {
            'androidMinimumVersion': '2.55.0',
            'verificationCode': verificationCode,
            'iosMinimumVersion': '2.55.0',
            'senderChannelUrl': response.payload.message.chatRoomId,
            'requestAt': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
            'senderMessageId': response.payload.message.messageId,
            'requestId': str(uuid.uuid4()).upper(),
            'orderId': response.payload.message.data.orderId,
        }

        response = requests.post(f'https://{self.host}/bff/v2/rejectP2PSendMoneyLink', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)
        return response

    def execute_link(self, amount:int, passcode=None):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        json_data = {
            "androidMinimumVersion": "2.55.0",
            "requestId": str(uuid.uuid4()).upper(),
            "requestAt": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
            "theme": "default-sendmoney",
            "amount": int(amount),
            "iosMinimumVersion": "2.55.0"
        }
        if passcode:
            json_data['passcode'] = passcode

        response = requests.post(f'https://{self.host}/bff/v2/executeP2PSendMoneyLink', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

    def execute_sendmoney(self, amount, externalReceiverId):
        if not "Authorization" in self.headers:
            raise PayPayError('S9999', 'ログインしてください。')
        json_data = {
            'theme': 'default-sendmoney',
            'androidMinimumVersion': '2.55.0',
            'externalReceiverId': externalReceiverId,
            'amount': int(amount),
            'requestId': str(uuid.uuid4()).upper(),
            'requestAt': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0900'),
            'iosMinimumVersion': '2.55.0',
        }

        response = requests.post(f'https://{self.host}/bff/v2/executeP2PSendMoney', params=self.params, headers=self.headers, json=json_data, proxies=self.proxies).json(object_hook=AttributeDict)
        if response.header.resultCode != "S0000":
            raise PayPayError(response.header.resultCode, response.error.displayErrorResponse.title if response.error.displayErrorResponse.title else response.header.resultMessage)

        return response

if __name__ == '__main__':
    paypay = PayPay()
    response = paypay.login('09057462967', 'KohnoseLami')
    print(response)