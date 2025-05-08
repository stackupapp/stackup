import streamlit_authenticator as stauth

# List of plain-text passwords
passwords = ['stack123', 'admin123']

# Correct usage: Hasher expects no arguments in init, and use hash() per password
hashed_passwords = [stauth.Hasher().hash(pwd) for pwd in passwords]

# Print to paste into config.yaml
for pwd, hashed in zip(passwords, hashed_passwords):
    print(f"{pwd}: {hashed}")