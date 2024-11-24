from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

class Data_Encryption:
    def __init__(self) -> None:
        # Retrieve the SECRET_KEY from Django settings and use it to generate a Fernet key
        key = settings.SECRET_KEY.encode()  # Convert SECRET_KEY to bytes
        # Hash the SECRET_KEY to make it 32 bytes, then base64 encode it for Fernet
        self.key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
        self.fernet = Fernet(self.key)

    def str_encrypt(self, data):
        """Encrypts a string using Fernet encryption."""
        if not isinstance(data, str):
            raise TypeError("Data to encrypt must be a string.")
        encrypted_data = self.fernet.encrypt(data.encode())
        return encrypted_data  # Return as string for easier handling

    def str_decrypt(self, encrypted_data):
        """Decrypts a string using Fernet encryption."""
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return decrypted_data.decode()  # Return decrypted data as string
