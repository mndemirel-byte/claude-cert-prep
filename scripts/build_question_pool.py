"""One-off: converts docs/question-pool-merged-338.json (the authored Question Pool,
our source of truth for questions) into content/question_pool.json, the build's
consumable schema (#12). Not part of the regular build — re-run only if the
authored pool changes."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE = os.path.join(ROOT, "docs", "question-pool-merged-338.json")

merged = json.load(open(SOURCE, encoding="utf-8"))

out = []
for q in merged:
    out.append({
        "d": q["domain"],
        "sc": q["scenario"],
        "ts": q["task_statement"],
        "body_tr": q["question_tr"],
        "opts_tr": q["options_tr"],
        "ans": q["correct_answer"],
        "expl_tr": q["explanation_tr"],
        "body_en": q["question_en"],
        "opts_en": q["options_en"],
        "expl_en": q["explanation_en"],
    })

out_path = os.path.join(ROOT, "content", "question_pool.json")
json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(out)} questions written to {out_path}")
