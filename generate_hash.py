import bcrypt

# Dictionary of usernames and their plain-text passwords
passwords = {
    "jeevan": "stack123",
    "admin": "admin123"
}

# Generate and print bcrypt hashes
for user, pwd in passwords.items():
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    print(f"{user}: {hashed.decode()}")