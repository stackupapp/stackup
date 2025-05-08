import streamlit_authenticator as stauth

# List of plain-text passwords to hash
passwords = ['stack123', 'admin123']

# Create bcrypt hashes
hashed_passwords = [stauth.Hasher().hash(pw) for pw in passwords]

# Print each one
for i, hash in enumerate(hashed_passwords):
    print(f"Password {i+1} Hash: {hash}")