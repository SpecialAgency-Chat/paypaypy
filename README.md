# PayPayPy

PayPayをPythonから操作します。

[![PyPI Version](https://img.shields.io/pypi/v/PayPayPy?label=PyPI)](https://pypi.org/project/PayPayPy/)
[![Python Versions](https://img.shields.io/pypi/pyversions/PayPayPy?label=Python)](https://pypi.org/project/PayPayPy/)

## 特徴

- 次のようなことを行うことが出来ます: 
    * PayPayへの、電話番号とパスワードを使用したログイン
    * 残高の参照
    * 取引履歴の指定個数分の参照
    * 送金リンクの受け取り 
    * 送金リンクの作成
    * 指定したユーザーへの送金
    * アカウント情報の確認

## インストール

pipを使用したインストール:

``pip install PayPayPy``

アップデートの際:

``pip install PayPayPy --upgrade``

Python 3.9.10 上で作成されテストされました

## 使い方

### ログイン
```python

from PayPayPy import PayPay

paypay = PayPay()
login_result = paypay.login("PHONENUMBER", "PASSWORD")
if login_result.header.resultCode == "S0000":
    print("ログイン成功！")
    print("貴方のアクセストークン: " + login_result.payload.accessToken)
elif login_result.header.resultCode == "S1004":
    otp = input("OTP: ")
    otp_result = paypay.login_otp(otp, login_result.error.otpReferenceId)
    print("ログイン成功！")
    print("貴方のアクセストークン: " + otp_result.payload.accessToken)
```

### その他のメソッド
```python

from PayPayPy import PayPay

paypay = PayPay("YOUR_ACCESS_TOKEN")

print(paypay.get_balance()) #残高照会
print(paypay.get_history(40)) #引数に数値を設定することで指定した個数の履歴を確認
print(paypay.get_profile()) #PayPayのプロフィール(メールアドレスなど) を取得
print(paypay.create_mycode()) #受け取りQRコードを生成
print(paypay.get_payment()) #登録されている支払い方法(クレジットカードなら下4桁など) を取得
print(paypay.create_paymentcode()) #支払いQRコードを生成
print(paypay.get_link("WYmwBH4b")) #受け取りリンク(リンクの後ろから8文字) の詳細を確認し、受け取られているかなどを確認
print(paypay.accept_link("WYmwBH4b", "パスコードがある場合")) #受け取りリンク(リンクの後ろから8文字) の詳細を確認し、受け取られていない場合に受け取り
print(paypay.execute_link(100, "パスコード")) #指定した額とパスワード(オプション) を使用して送金リンクを作成
print(paypay.execute_sendmoney(100, "0000000000000000")) #指定した額とユーザーを使用して直接送金
```
## 支援

Bitcoin
bc1qad5yr8x8edvuxfaumqdplrs0ed93phfrxng7ur

## 法的
これは、PayPayによって影響を受けたり、推奨されたり、認定されたりするものではありません。これは独立した非公式のAPIです。自己責任でご使用ください。
