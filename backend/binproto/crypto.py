""".bin konvert formati va kalit kelishuvi.

Konvert (barcha so'rov va javoblar uchun bir xil):

    +-------+-------+----------+-----------------------------+
    | AVS1  | flags | nonce    | AES-256-GCM(ciphertext+tag) |
    | 4 B   | 1 B   | 12 B     | N + 16 B                    |
    +-------+-------+----------+-----------------------------+

flags: 0x01 — ichida zlib bilan siqilgan JSON;
       0x02 — ichida xom bayt (rasm/audio): [mime uzunligi 1 B][mime][bayt].

AAD (autentifikatsiyalangan, lekin shifrlanmaydigan qism) = magic + flags +
yo'nalish + so'rov yo'li. Shu sababli bir endpointning .bin javobini boshqa
endpointga yoki so'rov sifatida qayta yuborib bo'lmaydi.

Kalit: brauzer ECDH P-256 juftini yaratadi (maxfiy qismi eksport qilinmaydi),
login paytida ochiq kalitini yuboradi. Server o'zining bir martalik juftini
yaratadi, umumiy sirni hisoblab, HKDF-SHA256 bilan 256-bitli AES kalitini
chiqaradi. AES kaliti tarmoqdan hech qachon o'tmaydi.
"""
import base64
import json
import os
import zlib

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

MAGIC = b"AVS1"
FLAG_JSON = 0x01
FLAG_RAW = 0x02
NONCE_LEN = 12
HEADER_LEN = len(MAGIC) + 1 + NONCE_LEN
HKDF_INFO = b"avtostart-bin-v1:"
MAX_PLAINTEXT = 8 * 1024 * 1024
CONTENT_TYPE = "application/octet-stream"


class BinError(Exception):
    """Konvert buzilgan, kalit noto'g'ri yoki ma'lumot o'zgartirilgan."""


def _aad(flags, direction, path):
    return MAGIC + bytes([flags]) + direction.encode() + b"|" + path.encode()


def seal(key, payload, *, path, direction, flags=FLAG_JSON):
    """payload: FLAG_JSON uchun JSON-ga aylanadigan obyekt, FLAG_RAW uchun bytes."""
    if flags == FLAG_JSON:
        body = zlib.compress(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode())
    else:
        body = payload
    nonce = os.urandom(NONCE_LEN)
    ct = AESGCM(key).encrypt(nonce, body, _aad(flags, direction, path))
    return MAGIC + bytes([flags]) + nonce + ct


def open_(key, blob, *, path, direction):
    """Konvertni ochadi. (flags, payload) qaytaradi."""
    if len(blob) < HEADER_LEN + 16 or blob[:4] != MAGIC:
        raise BinError("bad envelope")
    flags = blob[4]
    if flags not in (FLAG_JSON, FLAG_RAW):
        raise BinError("bad flags")
    nonce = blob[5:HEADER_LEN]
    try:
        body = AESGCM(key).decrypt(nonce, blob[HEADER_LEN:], _aad(flags, direction, path))
    except InvalidTag as exc:
        raise BinError("auth failed") from exc
    if flags == FLAG_JSON:
        try:
            d = zlib.decompressobj()
            raw = d.decompress(body, MAX_PLAINTEXT)
            if d.unconsumed_tail:
                raise BinError("too large")
            return flags, json.loads(raw)
        except (zlib.error, ValueError) as exc:
            raise BinError("bad payload") from exc
    return flags, body


def pack_media(mime, data):
    m = mime.encode()[:255]
    return bytes([len(m)]) + m + data


def b64e(b):
    return base64.b64encode(b).decode()


def b64d(s):
    return base64.b64decode(s, validate=True)


def handshake(client_pub_raw, session_id):
    """Server tomoni ECDH. (aes_key, server_pub_raw, salt) qaytaradi.

    client_pub_raw — siqilmagan P-256 nuqtasi (65 bayt, 0x04 bilan boshlanadi),
    WebCrypto `exportKey('raw', publicKey)` aynan shuni beradi.
    """
    try:
        client_pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), client_pub_raw)
    except ValueError as exc:
        raise BinError("bad public key") from exc
    server_priv = ec.generate_private_key(ec.SECP256R1())
    shared = server_priv.exchange(ec.ECDH(), client_pub)
    salt = os.urandom(16)
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt,
               info=HKDF_INFO + session_id.encode()).derive(shared)
    server_pub_raw = server_priv.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return key, server_pub_raw, salt


# --- DB'da saqlash uchun kalitni o'rash ---

def _storage_key():
    from django.conf import settings
    k = b64d(settings.BIN_STORAGE_KEY)
    if len(k) != 32:
        raise ValueError("BIN_STORAGE_KEY 32 bayt (base64) bo'lishi kerak")
    return k


def wrap_key(key, session_id):
    nonce = os.urandom(NONCE_LEN)
    return nonce + AESGCM(_storage_key()).encrypt(nonce, key, b"wrap:" + session_id.encode())


def unwrap_key(blob, session_id):
    return AESGCM(_storage_key()).decrypt(blob[:NONCE_LEN], blob[NONCE_LEN:], b"wrap:" + session_id.encode())
