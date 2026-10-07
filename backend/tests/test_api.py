import time

import pytest
from django.test import override_settings
from django.utils import timezone

from apps.accounts.models import DeviceSession
from apps.exams.models import Attempt
from binproto.crypto import FLAG_JSON, BinError, open_, seal

from .conftest import BinClient

pytestmark = pytest.mark.django_db


def test_envelope_roundtrip_and_tamper():
    key = b"k" * 32
    blob = seal(key, {"a": 1}, path="/api/x.bin", direction="res")
    assert open_(key, blob, path="/api/x.bin", direction="res") == (FLAG_JSON, {"a": 1})
    with pytest.raises(BinError):  # boshqa endpoint
        open_(key, blob, path="/api/y.bin", direction="res")
    with pytest.raises(BinError):  # javobni so'rov sifatida qayta ishlatish
        open_(key, blob, path="/api/x.bin", direction="req")
    tampered = blob[:-1] + bytes([blob[-1] ^ 1])
    with pytest.raises(BinError):
        open_(key, tampered, path="/api/x.bin", direction="res")


def test_login_wrong_code_is_generic(student):
    r = BinClient().login("WRONGCODE123")
    assert r.status_code == 401 and r.json() == {"error": "invalid_code"}


def test_login_response_has_no_key(student):
    c = BinClient()
    r = c.login()
    assert set(r.json()) == {"token", "sid", "server_pub", "salt", "expires_at", "student"}
    assert c.key not in r.content


def test_login_code_normalized(student):
    assert BinClient().login("abcd efgh-jklm").status_code == 200


def test_ip_lockout(student):
    with override_settings(LOGIN_MAX_FAILS=3, REST_FRAMEWORK={
        "DEFAULT_THROTTLE_RATES": {"login": "100/min", "anon": "100/min", "user": "100/min"}}):
        for _ in range(3):
            BinClient().login("XXXXXXXXXXXX")
        assert BinClient().login().status_code == 429


def test_device_limit(student):
    assert BinClient().login().status_code == 200
    r = BinClient().login()
    assert r.status_code == 403 and r.json()["error"] == "device_limit"


def test_same_device_relogin_replaces_session(student):
    c = BinClient()
    c.login()
    old = c.token
    c.login()
    assert DeviceSession.objects.filter(revoked=False).count() == 1
    c.token = old
    assert c.get("/api/catalog.bin").status_code == 401


def test_catalog_is_encrypted(client_bin, seeded):
    r = client_bin.get("/api/catalog.bin")
    assert r.status_code == 200
    assert b"bosqich" not in r.content  # ochiq matn yo'q
    data = client_bin.decode(r)
    assert len(data["stages"]) == 4 and len(data["variants"]) == 60


def test_requires_auth(seeded):
    assert BinClient().get("/api/catalog.bin").status_code == 401


def test_device_id_mismatch(client_bin, seeded):
    client_bin.device_id = "x" * 32
    r = client_bin.get("/api/catalog.bin")
    assert r.status_code == 401 and r.json()["error"] == "device_mismatch"


def test_stolen_token_with_wrong_key_rejected(client_bin, seeded):
    client_bin.key = b"z" * 32
    r = client_bin.post("/api/attempts/start.bin", {"kind": "final"})
    assert r.status_code == 400


def test_replay_and_stale_rejected(client_bin, seeded):
    path = "/api/attempts/start.bin"
    blob = client_bin.body(path, {"kind": "final"})
    assert client_bin.post(path, raw=blob).status_code == 201
    assert client_bin.post(path, raw=blob).status_code == 400  # replay
    old = int((time.time() - 3600) * 1000)
    assert client_bin.post(path, {"kind": "final"}, ts=old).status_code == 400


def test_exam_flow_hides_answers_until_answered(client_bin, seeded):
    r = client_bin.post("/api/attempts/start.bin", {"kind": "final", "count": 20})
    data = client_bin.decode(r)
    assert len(data["questions"]) == 20 and 0 < data["remaining"] <= 25 * 60
    assert all(q["correct"] is None for q in data["questions"])

    q = data["questions"][0]
    path = f"/api/attempts/{data['id']}/answer.bin"
    res = client_bin.decode(client_bin.post(path, {"question": q["id"], "answer": q["answers"][0]["id"]}))
    assert res["correct_answer"] is not None
    # Javobni o'zgartirib bo'lmaydi
    r2 = client_bin.post(path, {"question": q["id"], "answer": q["answers"][-1]["id"]})
    assert r2.status_code == 409

    state = client_bin.decode(client_bin.get(f"/api/attempts/{data['id']}.bin"))
    assert state["questions"][0]["correct"] is not None
    assert state["questions"][1]["correct"] is None


def test_answer_from_other_question_rejected(client_bin, seeded):
    data = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "final"}))
    q1, q2 = data["questions"][:2]
    r = client_bin.post(f"/api/attempts/{data['id']}/answer.bin",
                        {"question": q1["id"], "answer": q2["answers"][0]["id"]})
    assert r.status_code == 404


def test_deadline_enforced(client_bin, seeded):
    data = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "final"}))
    Attempt.objects.filter(pk=data["id"]).update(deadline=timezone.now())
    q = data["questions"][0]
    r = client_bin.post(f"/api/attempts/{data['id']}/answer.bin", {"question": q["id"], "answer": q["answers"][0]["id"]})
    assert r.status_code == 409


def test_score_computed_on_server(client_bin, seeded):
    data = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "final"}))
    for q in data["questions"]:
        res = client_bin.decode(client_bin.post(f"/api/attempts/{data['id']}/answer.bin",
                                                {"question": q["id"], "answer": q["answers"][0]["id"]}))
    assert res["finished"] and res["result"]["total"] == 20


def test_other_students_attempt_hidden(client_bin, seeded):
    from apps.accounts.models import Student
    other = Student(full_name="Boshqa")
    other.set_code("ZZZZZZZZZZZZ")
    other.save()
    c2 = BinClient()
    c2.login("ZZZZZZZZZZZZ")
    data = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "final"}))
    assert c2.get(f"/api/attempts/{data['id']}.bin").status_code == 404


def test_study_reveals_answers(client_bin, seeded):
    cat = client_bin.decode(client_bin.get("/api/catalog.bin"))["stages"][0]["categories"][0]
    data = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "study", "ref": cat["id"]}))
    assert data["remaining"] is None and all(q["correct"] for q in data["questions"])
    q = data["questions"][0]
    r = client_bin.post(f"/api/attempts/{data['id']}/answer.bin", {"question": q["id"], "answer": q["answers"][0]["id"]})
    assert r.status_code == 409 and client_bin.decode(r)["error"] == "read_only"


def test_logout_revokes(client_bin, seeded):
    assert client_bin.post("/api/auth/logout/", {}).status_code == 200
    assert client_bin.get("/api/catalog.bin").status_code == 401


def test_security_headers(client_bin, seeded):
    r = client_bin.get("/api/catalog.bin")
    assert r["Cache-Control"] == "no-store"
    assert "default-src 'none'" in r["Content-Security-Policy"]
    assert r["X-Content-Type-Options"] == "nosniff"


def test_media_served_only_encrypted(client_bin, seeded, settings, tmp_path):
    from django.core.files.base import ContentFile

    from apps.content.models import Question
    from binproto.crypto import FLAG_RAW

    settings.MEDIA_ROOT = tmp_path
    q = Question.objects.first()
    png = b"\x89PNG\r\n\x1a\n" + b"x" * 100
    q.image.save("sign.png", ContentFile(png))
    path = f"/api/media/question/{q.pk}/image.bin"
    r = client_bin.get(path)
    assert r.status_code == 200 and png not in r.content
    flags, body = open_(client_bin.key, r.content, path=path, direction="res")
    assert flags == FLAG_RAW and body == bytes([9]) + b"image/png" + png
    # Ruxsat etilmagan maydon / model
    assert client_bin.get(f"/api/media/question/{q.pk}/text_uz.bin").status_code == 404
    assert client_bin.get("/api/media/student/1/code_hash.bin").status_code == 404
    # Nashr etilmagan savol rasmi berilmaydi
    Question.objects.filter(pk=q.pk).update(is_published=False)
    assert client_bin.get(path).status_code == 404


def test_unpublished_not_in_attempts(client_bin, seeded):
    from apps.content.models import Question
    Question.objects.update(is_published=False)
    r = client_bin.post("/api/attempts/start.bin", {"kind": "final"})
    assert r.status_code == 404


def test_long_exam_gets_45_minutes(client_bin, seeded):
    # 20 ta -> 25 daqiqa
    short = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "final", "count": 20}))
    assert 20 * 60 < short["remaining"] <= 25 * 60
    # 50 ta -> 45 daqiqa
    long = client_bin.decode(client_bin.post("/api/attempts/start.bin", {"kind": "final", "count": 50}))
    assert 25 * 60 < long["remaining"] <= 45 * 60
