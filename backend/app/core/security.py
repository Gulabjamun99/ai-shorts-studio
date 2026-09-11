import base64
import os
import re
from pathlib import Path
from cryptography.fernet import Fernet
from PIL import Image
from backend.app.core.config import settings

# Derive a consistent 32-byte Fernet key from settings
def _get_fernet() -> Fernet:
    key_bytes = settings.SECRET_ENCRYPTION_KEY.encode()
    if len(key_bytes) == 44:  # Already valid Fernet key
        try:
            return Fernet(key_bytes)
        except Exception:
            pass
    # Fallback to base64-padded 32-byte key
    padded = (key_bytes + b"0" * 32)[:32]
    fernet_key = base64.urlsafe_b64encode(padded)
    return Fernet(fernet_key)

_fernet = _get_fernet()

def encrypt_secret(secret: str) -> str:
    """Encrypts an API key or OAuth token before database storage."""
    if not secret:
        return ""
    return _fernet.encrypt(secret.encode()).decode()

def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypts an encrypted API key or OAuth token."""
    if not encrypted_secret:
        return ""
    try:
        return _fernet.decrypt(encrypted_secret.encode()).decode()
    except Exception:
        return ""

def sanitize_input_text(text: str) -> str:
    """Sanitizes user concept, title, and prompt inputs."""
    if not text:
        return ""
    # Strip dangerous control characters but preserve unicode and punctuation
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return cleaned.strip()

def validate_image_file(file_path: Path) -> tuple[bool, str]:
    """Validates an uploaded asset file for format, size, and corruption."""
    if not file_path.exists():
        return False, "File does not exist."
    
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
    
    if file_path.suffix.lower() not in settings.ALLOWED_IMAGE_EXTENSIONS:
        return False, f"Unsupported file extension {file_path.suffix}. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
    
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True, "Valid image"
    except Exception as e:
        return False, f"Corrupted or invalid image file: {str(e)}"
