#!/usr/bin/env python3
"""Qo'lda qo'shilgan savollarni (extra_questions.json) content.json ga qo'shadi.

    python3 tools/merge_extra.py frontend/public/content.json tools/extra_questions.json

Har bir savolning barqaror "key" i bor: qayta ishga tushirilsa savol takrorlanmaydi,
balki yangilanadi. Bo'lim bosqich raqami + o'zbekcha nomi bo'yicha topiladi, shuning
uchun Firebase'dan qayta eksportdan keyin ham to'g'ri joyga tushadi.
"""
import json
import sys
from pathlib import Path

content_path, extra_path = Path(sys.argv[1]), Path(sys.argv[2])
content = json.loads(content_path.read_text(encoding="utf-8"))
extras = json.loads(extra_path.read_text(encoding="utf-8"))

stage_ids = {s["number"]: s["id"] for s in content["stages"]}
next_q = max(q["id"] for q in content["questions"]) + 1
next_a = max(a["id"] for q in content["questions"] for a in q["answers"]) + 1

for ex in extras:
    stage_id = stage_ids[ex["stage"]]
    cat = next(c for c in content["categories"]
               if c["stage"] == stage_id and c["title"]["uz"].strip().lower() == ex["category_uz"].strip().lower())
    old = next((q for q in content["questions"] if q.get("key") == ex["key"]), None)
    qid = old["id"] if old else next_q
    if old:
        content["questions"].remove(old)
    else:
        next_q += 1
    answers = []
    for i, a in enumerate(ex["answers"]):
        answers.append({"id": next_a, "text": {k: a[k] for k in ("uz", "kr", "ru")},
                        "correct": a["correct"], "order": i})
        next_a += 1
    assert sum(a["correct"] for a in answers) == 1, f"{ex['key']}: aniq bitta to'g'ri javob kerak"
    content["questions"].append({
        "id": qid, "key": ex["key"], "category": cat["id"], "stage": stage_id,
        "text": ex["text"], "image": ex.get("image"), "explanation": ex["explanation"],
        "order": max((q.get("order", 0) for q in content["questions"] if q["category"] == cat["id"]), default=0) + 1,
        "answers": answers,
    })
    print(f"+ {ex['key']} -> {ex['stage']}-bosqich / {cat['title']['uz']} (savol id {qid})")

content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
print("jami savol:", len(content["questions"]))
