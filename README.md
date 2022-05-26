# PayPayPy

PayPayをPythonから操作します。

[![PyPI Version](https://img.shields.io/pypi/v/tweepy?label=PyPI)](https://pypi.org/project/tweepy/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tweepy?label=Python)](https://pypi.org/project/tweepy/)

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

```python

from PayPayPy import PayPay

paypay = PayPay()

```

## 支援

Bitcoin
bc1qad5yr8x8edvuxfaumqdplrs0ed93phfrxng7ur

## 法的
これは、PayPayによって影響を受けたり、推奨されたり、認定されたりするものではありません。これは独立した非公式のAPIです。自己責任でご使用ください。
