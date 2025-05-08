import streamlit_authenticator as stauth

# List of plain text passwords for your users
passwords = ['stack123', 'admin456']  # jeevan's and admin's passwords

# Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

# Print hashed passwords to paste into config.yaml
for user, pwd in zip(['jeevan', 'admin'], hashed_passwords):
    print(f"{user}: {pwd}")