from PayPayPy import PayPay

paypay = PayPay()
login_result = paypay.login("PHONENUMBER", "PASSWORD")
if login_result.header.resultCode == "S0000":
    print("ログイン成功！")
    print("貴方のアクセストークン: " + login_result.payload.accessToken)
elif login_result.header.resultCode == "S1004":
    otp = input("OTP: ")
    otp_result = paypay.login_otp(login_result.error.otpReferenceId, otp)
    print("ログイン成功！")
    print("貴方のアクセストークン: " + otp_result.payload.accessToken)
