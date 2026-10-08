#!/usr/bin/env python3
# Ishlatish: python3 tools/convert_firebase.py <avto-test-export papka> frontend/public/content.json
# So'ng:     python3 tools/merge_extra.py frontend/public/content.json tools/extra_questions.json
"""Firebase eksportini (avto-test-export) AvtoStart content.json formatiga o'giradi.

Chiqish: bosqich -> bo'lim -> savol -> javob, rasm fayl nomlari bilan.
Rasmlar public/media/ dan o'qiladi (nom = manifestdagi fayl, "media/" olib tashlangan).
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])          # .../avto-test-export
OUT = Path(sys.argv[2])          # content.json

deps = json.load(open(SRC / "json/departments.json"))
manifest = json.load(open(SRC / "media_manifest.json"))

# URL -> fayl nomi (public/media ichidagi)
url2file = {}
for m in manifest:
    if not m.get("file") or not m.get("url"):
        continue
    name = m["file"].split("/", 1)[-1]
    url2file[m["url"]] = name

def media_name(url):
    if not url:
        return None
    return url2file.get(url)                   # topilmasa None -> placeholder

def tri(obj, base):
    return {
        "uz": (obj.get(f"{base}uz") or "").strip(),
        "kr": (obj.get(f"{base}crl") or "").strip(),
        "ru": (obj.get(f"{base}ru") or "").strip(),
    }

stages, categories, questions = [], [], []
cat_sid = {}   # firebase menu id -> bizning category id
cid = 1
qid = 1
aid = 1
missing_img = 0
used_files = set()

for dep in sorted(deps, key=lambda d: d["sn"]):
    stage = {"id": dep["sn"], "number": dep["sn"], "title": tri(dep, "name")}
    stages.append(stage)

    for menu in sorted(dep["menu"], key=lambda m: m.get("sn", 0)):
        icon = media_name(menu.get("image"))
        if menu.get("image") and not icon:
            missing_img += 1
        if icon:
            used_files.add(icon)
        cat = {
            "id": cid,
            "stage": stage["id"],
            "title": tri(menu, "name"),
            "icon": icon,
            "order": int(menu.get("sn") or 0),
        }
        categories.append(cat)
        cat_sid[menu["id"]] = cid
        cid += 1

    for q in dep["savollar"]:
        cat_id = cat_sid.get(q.get("type"))
        if cat_id is None:
            continue                            # bo'limsiz savol tashlab ketiladi
        img = media_name(q.get("selectedMainPhoto"))
        if q.get("selectedMainPhoto") and not img:
            missing_img += 1
        if img:
            used_files.add(img)

        vs = q.get("variants") or []
        cv = q.get("correctVariant")
        correct_obj = vs[cv] if isinstance(cv, int) and 0 <= cv < len(vs) else None

        def keynum(v):
            m = re.match(r"F(\d+)", str(v.get("key") or ""))
            return int(m.group(1)) if m else 99
        vs_sorted = sorted(vs, key=keynum)

        answers = []
        for order, v in enumerate(vs_sorted):
            answers.append({
                "id": aid,
                "text": {"uz": (v.get("uz") or "").strip(),
                          "kr": (v.get("crl") or "").strip(),
                          "ru": (v.get("ru") or "").strip()},
                "correct": v is correct_obj,
                "order": order,
            })
            aid += 1
        if correct_obj is None and answers:
            answers[0]["correct"] = True        # zaxira: birinchi javob

        questions.append({
            "id": qid,
            "category": cat_id,
            "stage": stage["id"],
            "text": tri(q, "querie"),
            "image": img,
            "explanation": {"uz": "", "kr": "", "ru": ""},
            "order": int(q.get("querieSn") or 0),
            "answers": answers,
        })
        qid += 1

# Variantlar (test biletlari): har bosqich bo'yicha va umumiy
import random
rng = random.Random(42)
variants = []
vid = 1
all_q = [q["id"] for q in questions]
for n in range(1, 61):
    variants.append({"id": vid, "stage": None, "number": n,
                     "questions": rng.sample(all_q, min(20, len(all_q)))}); vid += 1
for st in stages:
    sq = [q["id"] for q in questions if q["stage"] == st["id"]]
    if not sq:
        continue
    for n in range(1, 19):
        variants.append({"id": vid, "stage": st["id"], "number": n,
                         "questions": rng.sample(sq, min(20, len(sq)))}); vid += 1

content = {"stages": stages, "categories": categories,
           "questions": questions, "variants": variants}
OUT.write_text(json.dumps(content, ensure_ascii=False))
Path(str(OUT) + ".used_media.txt").write_text("\n".join(sorted(used_files)))

print(f"bosqich={len(stages)} bo'lim={len(categories)} savol={len(questions)} "
      f"variant={len(variants)} ishlatilgan_rasm={len(used_files)} topilmagan_rasm={missing_img}")
noimg = sum(1 for q in questions if not q["image"])
print(f"rasmsiz savol={noimg}")
