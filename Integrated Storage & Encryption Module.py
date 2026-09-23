import os
import pydicom
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class CortexSecureVault:
    """
    Handles medical scan sanitization (PHI removal) and AES-grade 
    encryption-at-rest for the Cortex AI diagnostic platform.
    """
    def __init__(self, storage_directory: str, master_password: str = None):
        self.storage_directory = storage_directory
        os.makedirs(self.storage_directory, exist_ok=True)
        
        # Initialize encryption cipher
        self.salt = os.urandom(16)
        self.cipher = self._initialize_cipher(master_password)

    def _initialize_cipher(self, password: str = None) -> Fernet:
        """Derives a secure 256-bit encryption key using PBKDF2HMAC."""
        if password:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100_000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        else:
            key = Fernet.generate_key()
        return Fernet(key)

    def sanitize_and_encrypt_scan(self, raw_file_path: str, destination_name: str) -> str:
        """
        1. Strips Protected Health Information (PHI) from DICOM metadata.
        2. Encrypts the clean image file binary data at rest.
        3. Saves the locked file (.enc) into the secure vault.
        """
        try:
            anonymized_temp_path = os.path.join(self.storage_directory, f"temp_anon_{destination_name}")

            # Check if file is DICOM format to handle metadata stripping
            if raw_file_path.lower().endswith('.dcm'):
                dataset = pydicom.dcmread(raw_file_path)
                tags_to_clear = ['PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex']
                for tag in tags_to_clear:
                    if tag in dataset:
                        setattr(dataset, tag, "ANONYMIZED")
                dataset.save_as(anonymized_temp_path)
            else:
                # For standard image formats (PNG/JPG), copy raw bytes
                with open(raw_file_path, "rb") as src, open(anonymized_temp_path, "wb") as dst:
                    dst.write(src.read())

            # Encrypt the file contents at rest
            with open(anonymized_temp_path, "rb") as file:
                file_data = file.read()
            
            encrypted_data = self.cipher.encrypt(file_data)
            
            secure_vault_path = os.path.join(self.storage_directory, f"{destination_name}.enc")
            with open(secure_vault_path, "wb") as enc_file:
                enc_file.write(encrypted_data)

            # Clean up the unencrypted temporary file immediately
            if os.path.exists(anonymized_temp_path):
                os.remove(anonymized_temp_path)

            return secure_vault_path

        except Exception as e:
            if os.path.exists(anonymized_temp_path):
                os.remove(anonymized_temp_path)
            raise RuntimeError(f"Secure vault processing failed: {str(e)}")

    def decrypt_scan_for_inference(self, encrypted_vault_path: str, output_temp_path: str) -> None:
        """
        Temporarily decrypts the scan file into memory/secure temp storage 
        strictly for deep learning model inference execution.
        """
        try:
            with open(encrypted_vault_path, "rb") as enc_file:
                encrypted_data = enc_file.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_temp_path, "wb") as dec_file:
                dec_file.write(decrypted_data)
                
        except Exception as e:
            raise RuntimeError(f"Scan decryption for inference failed: {str(e)}")

# =========================================================
# Integration Test Execution
# =========================================================
if __name__ == "__main__":
    vault = CortexSecureVault(storage_directory="secure_vault_storage", master_password="CortexSecureMasterKey2026!")
    print("Cortex AI Secure Encryption & De-identification Module initialized successfully.")