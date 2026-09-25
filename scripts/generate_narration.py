"""Generate Narration MP3s for every Lesson (build-time, not unit tested — see CONTEXT.md
and issue #1's Testing Decisions: the OpenAI call and manifest-driven skip logic are
verified by actually running this script, not by mocking a paid external API)."""
import argparse
import json
import os
import subprocess

from openai import OpenAI

from narration import (
    content_hash,
    discover_lessons,
    narration_filename,
    plan_narration_jobs,
    prepare_narration_text,
    split_into_chunks,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_dotenv() -> None:
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv()

EN_DIR = os.path.join(ROOT, "content", "en_lessons")
TR_DIR = os.path.join(ROOT, "content", "tr")
AUDIO_DIR = os.path.join(ROOT, "dist", "audio")
MANIFEST_PATH = os.path.join(AUDIO_DIR, "manifest.json")

MODEL = "gpt-4o-mini-tts"
VOICE = "cedar"
INSTRUCTIONS = "warm, friendly, clear educator tone"
MAX_CHARS_PER_TTS_CALL = 3000


def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        return json.load(open(MANIFEST_PATH, encoding="utf-8"))
    return {}


def save_manifest(manifest: dict) -> None:
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    json.dump(manifest, open(MANIFEST_PATH, "w", encoding="utf-8"), indent=2, sort_keys=True)


def output_path(lesson_id: str, language: str) -> str:
    return os.path.join(AUDIO_DIR, language, narration_filename(lesson_id))


def reencode_to_64kbps_mono(path: str) -> None:
    """Re-encode in place via ffmpeg to keep narration file sizes reasonable."""
    tmp = path + ".tmp.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", path, "-ac", "1", "-b:a", "64k", tmp],
        check=True,
    )
    os.replace(tmp, path)


def collect_lesson_texts() -> dict:
    lesson_texts = {}
    for lesson in discover_lessons(EN_DIR, TR_DIR):
        if lesson.en_path:
            lesson_texts[(lesson.id, "en")] = prepare_narration_text(
                open(lesson.en_path, encoding="utf-8").read()
            )
        if lesson.tr_path:
            lesson_texts[(lesson.id, "tr")] = prepare_narration_text(
                open(lesson.tr_path, encoding="utf-8").read()
            )
    return lesson_texts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Limit generation to a single lesson id, e.g. 1.1")
    args = parser.parse_args()

    lesson_texts = collect_lesson_texts()
    if args.only:
        lesson_texts = {k: v for k, v in lesson_texts.items() if k[0] == args.only}
        if not lesson_texts:
            print(f"no lesson found with id {args.only!r}")
            return

    manifest = load_manifest()
    jobs = plan_narration_jobs(lesson_texts, manifest)

    print(f"{len(jobs)} narration(s) to generate out of {len(lesson_texts)} total")
    if not jobs:
        return

    client = OpenAI()
    for job in jobs:
        out = output_path(job.id, job.language)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        chunks = split_into_chunks(job.text, MAX_CHARS_PER_TTS_CALL)
        print(f"generating {job.id} ({job.language}, {len(chunks)} chunk(s)) -> {out}")
        with open(out, "wb") as f:
            for chunk in chunks:
                with client.audio.speech.with_streaming_response.create(
                    model=MODEL,
                    voice=VOICE,
                    input=chunk,
                    instructions=INSTRUCTIONS,
                ) as response:
                    for data in response.iter_bytes():
                        f.write(data)
        reencode_to_64kbps_mono(out)
        manifest[f"{job.id}:{job.language}"] = content_hash(job.text)
        save_manifest(manifest)


if __name__ == "__main__":
    main()
