from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os


def _truncate_utf8_bytes_force71(s, max_bytes=71):
    if not isinstance(s, str):
        raise ValueError(f"Password must be a string, got {type(s)}: {repr(s)}")
    b = s.encode("utf-8")
    for i in range(max_bytes, 0, -1):
        try:
            truncated = b[:i].decode("utf-8")
            if len(truncated.encode("utf-8")) <= max_bytes:
                return truncated
        except UnicodeDecodeError:
            continue

    return ""


SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"], deprecated="auto", bcrypt__variant="pybcrypt"
)


def verify_password(plain_password, hashed_password):
    # Always truncate before verifying
    safe_password = _truncate_utf8_bytes_force71(plain_password, 71)
    return pwd_context.verify(safe_password, hashed_password)


def get_password_hash(password):
    # Debug: log type and value of password
    debug_msg = (
        f"[DEBUG] get_password_hash: type={type(password)}, value={repr(password)}\n"
    )
    print(debug_msg, flush=True)
    try:
        with open("/tmp/password_debug.log", "a") as f:
            f.write(debug_msg)
    except Exception:
        pass
    if not isinstance(password, str):
        raise ValueError(
            f"Password must be a string, got {type(password)}: {repr(password)}"
        )
    if password is None:
        raise ValueError("Password cannot be None")
    # Always truncate before hashing
    safe_password = _truncate_utf8_bytes_force71(password, 71)
    safe_password_bytes = safe_password.encode("utf-8")
    byte_len = len(safe_password_bytes)
    debug_msg2 = (
        f"[DEBUG] About to hash password: {repr(safe_password)}\n"
        f"[DEBUG] Type: {type(safe_password)}\n"
        f"[DEBUG] Encoded bytes: {safe_password_bytes}\n"
        f"[DEBUG] Byte length: {byte_len}\n"
        f"[DEBUG] Char length: {len(safe_password)}\n"
    )
    print(debug_msg2, flush=True)
    try:
        with open("/tmp/password_debug.log", "a") as f:
            f.write(debug_msg2)
    except Exception:
        pass
    try:
        assert byte_len <= 72, (
            f"Password passed to bcrypt is {byte_len} bytes, must be <= 72. "
            f"Value: {repr(safe_password)}"
        )
        return pwd_context.hash(safe_password)
    except ValueError as ve:
        import traceback

        tb = traceback.format_exc()
        error_msg = (
            f"[ERROR] Exception in get_password_hash: {ve}\n{tb}\n"
            f"[DEBUG] Password: {repr(safe_password)} (bytes: {byte_len})\n"
        )
        print(error_msg, flush=True)
        try:
            with open("/tmp/password_debug.log", "a") as f:
                f.write(error_msg)
        except Exception:
            pass
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
