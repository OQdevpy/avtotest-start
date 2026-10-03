import base64
import os
import time
import uuid


import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import Student
from binproto.crypto import CONTENT_TYPE, HKDF_INFO, open_, seal


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()


@pytest.fixture
def seeded(db):
    from django.core.management import call_command
    call_command("seed_demo", per_category=6, verbosity=0)


@pytest.fixture
def student(db):
    s = Student(full_name="Test O'quvchi")
    s.set_code("ABCD-EFGH-JKLM")
    s.save()
    return s


class BinClient:
    """Brauzerdagi frontend bilan bir xil protokolni bajaruvchi test mijozi."""

    def __init__(self, device_id=None):
        self.api = APIClient()
        self.device_id = device_id or uuid.uuid4().hex
        self.key = None
        self.token = None

    def login(self, code="ABCDEFGHJKLM"):
        priv = ec.generate_private_key(ec.SECP256R1())
        pub = priv.public_key().public_bytes(serialization.Encoding.X962,
                                             serialization.PublicFormat.UncompressedPoint)
        r = self.api.post("/api/auth/login/", {"code": code, "device_id": self.device_id,
                                               "client_pub": base64.b64encode(pub).decode()}, format="json")
        if r.status_code != 200:
            return r
        d = r.json()
        server_pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), base64.b64decode(d["server_pub"]))
        shared = priv.exchange(ec.ECDH(), server_pub)
        self.key = HKDF(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(d["salt"]),
                        info=HKDF_INFO + d["sid"].encode()).derive(shared)
        self.token = d["token"]
        return r

    def _headers(self):
        return {"HTTP_AUTHORIZATION": f"Bin {self.token}", "HTTP_X_DEVICE_ID": self.device_id}

    def body(self, path, payload, *, nonce=None, ts=None):
        payload = {**payload, "_ts": ts or int(time.time() * 1000), "_n": nonce or uuid.uuid4().hex}
        return seal(self.key, payload, path=path, direction="req")

    def get(self, path):
        return self.api.get(path, **self._headers())

    def post(self, path, payload=None, raw=None, **kw):
        data = raw if raw is not None else self.body(path, payload or {}, **kw)
        return self.api.generic("POST", path, data, content_type=CONTENT_TYPE, **self._headers())

    def decode(self, response):
        assert response["Content-Type"] == CONTENT_TYPE, response.content[:200]
        return open_(self.key, response.content, path=response.wsgi_request.path, direction="res")[1]


@pytest.fixture
def client_bin(student):
    c = BinClient()
    assert c.login().status_code == 200
    return c
