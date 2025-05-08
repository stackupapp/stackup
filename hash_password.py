import streamlit_authenticator as stauth

# Plain-text passwords
passwords = ['stack123', 'admin123']

# Hash passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Print the output
for pwd, hashed in zip(passwords, hashed_passwords):
    print(f"{pwd} → {hashed}")