import os
import pydicom
from cryptography.fernet import Fernet

class SecureDICOMVault:
    def __init__(self, storage_directory: str):
        self.storage_directory = storage_directory
        os.makedirs(self.storage_directory, exist_ok=True)
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

    def sanitize_and_store(self, raw_file_path: str, destination_name: str) -> str:
        """Strips PHI (Protected Health Information) tags and encrypts data at rest."""
        try:
            dataset = pydicom.dcmread(raw_file_path)
            
            # Nullify sensitive DICOM tags (Patient Name, ID, DOB)
            tags_to_clear = ['PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex']
            for tag in tags_to_clear:
                if tag in dataset:
                    setattr(dataset, tag, "ANONYMIZED")

            anonymized_path = os.path.join(self.storage_directory, f"anon_{destination_name}")
            dataset.save_as(anonymized_path)

            # Encrypt file contents for database secure storage compliance
            with open(anonymized_path, "rb") as file:
                encrypted_data = self.cipher.encrypt(file.read())
            
            secure_vault_path = anonymized_path + ".enc"
            with open(secure_vault_path, "wb") as enc_file:
                enc_file.write(encrypted_data)

            os.remove(anonymized_path) # Clean intermediate unencrypted temporary file
            return secure_vault_path
        except Exception as e:
            raise IOError(f"DICOM processing failed: {str(e)}")