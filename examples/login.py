from PayPayPy import PayPay

paypay = PayPay()
login_result = paypay.login("PHONENUMBER", "PASSWORD")
if login_result.header.resultCode == "S0000":
    otp = input("Enter OTP: ")
    otp_result = paypay.login_otp(otp)
    if otp_result.header.resultCode == "S0000":
        print("Login successful")
