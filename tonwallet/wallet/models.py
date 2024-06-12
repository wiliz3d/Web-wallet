# wallet/models.py
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import base64
import uuid

# Generate a key for encryption
# Save this key securely; it should not be hardcoded in production
KEY = base64.urlsafe_b64encode(Fernet.generate_key())

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    encrypted_seed_phrase = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    receive_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def encrypt_seed_phrase(self, seed_phrase):
        cipher_suite = Fernet(KEY)
        self.encrypted_seed_phrase = cipher_suite.encrypt(seed_phrase.encode()).decode()

    def decrypt_seed_phrase(self):
        cipher_suite = Fernet(KEY)
        return cipher_suite.decrypt(self.encrypted_seed_phrase.encode()).decode()

    def __str__(self):
        return f"{self.user.username}'s Wallet: {self.address}"
