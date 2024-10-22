import pyotp

totp = pyotp.TOTP("TNOAM3UVSORCWVZQXPXNA7SEEZVMZBPZ")
print(f"2FA: {totp.now()}")

