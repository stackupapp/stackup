import bcrypt

passwords = {
    "jeevan": "stack123",
    "admin": "admin123"
}

for user, pwd in passwords.items():
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    print(f'"{user}": "{hashed.decode()}"')