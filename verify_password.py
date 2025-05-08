import streamlit_authenticator as stauth

hashed = '$2b$12$qXnrU6jNBfjW6VUJYKinNOQkw.nChAqhgkwttmx7kN0OgRQUtk49S'
password = 'stack123'

hasher = stauth.Hasher()
print(hasher.verify(password, hashed))  # Should print True