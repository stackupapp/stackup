import streamlit_authenticator as stauth

# List of plain-text passwords to hash
passwords = ['stack123', 'admin123']
# Generate secure bcrypt hashes for each password
hasher = stauth.Hasher()
hashed_passwords = [hasher.hash(password) for password in passwords]
# Print them out so you can paste into your config
for i, h in enumerate(hashed_passwords):
    print(f"Password {i+1}: {h}")