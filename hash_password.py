import streamlit_authenticator as stauth

passwords = ['stack123', 'admin123']
hasher = stauth.Hasher()
hashed_passwords = [hasher.hash(pw) for pw in passwords]

for i, h in enumerate(hashed_passwords):
    print(f"Password {i+1}: {h}")