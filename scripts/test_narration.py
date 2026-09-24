import os

from narration import (
    prepare_narration_text,
    discover_lessons,
    LessonSource,
    plan_narration_jobs,
    NarrationJob,
    narration_filename,
    split_into_chunks,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_strips_heading_markdown_syntax_but_keeps_text():
    markdown = "## The Core Idea"

    result = prepare_narration_text(markdown)

    assert result == "The Core Idea"


def test_replaces_fenced_code_block_with_spoken_placeholder():
    markdown = "Some text.\n\n```python\nprint('hi')\n```\n\nMore text."

    result = prepare_narration_text(markdown)

    assert result == "Some text.\n\nHere's a code example.\n\nMore text."


def test_strips_inline_formatting_but_keeps_text():
    markdown = "This is **bold**, *italic*, and a [link](https://example.com)."

    result = prepare_narration_text(markdown)

    assert result == "This is bold, italic, and a link."


def test_flattens_table_rows_into_spoken_sentences():
    markdown = "| Feature | Support |\n|---|---|\n| Hooks | Yes |"

    result = prepare_narration_text(markdown)

    assert result == "Feature, Support. Hooks, Yes."


def test_combines_all_transformations_on_realistic_lesson_markdown():
    markdown = (
        "## The Core Idea\n\n"
        "An **agentic loop** turns Claude into something that can *act*. "
        "See the [Anthropic docs](https://docs.anthropic.com) for details.\n\n"
        "```python\nwhile not done:\n    step()\n```\n\n"
        "It keeps going until the job is finished."
    )

    result = prepare_narration_text(markdown)

    assert result == (
        "The Core Idea\n\n"
        "An agentic loop turns Claude into something that can act. "
        "See the Anthropic docs for details.\n\n"
        "Here's a code example.\n\n"
        "It keeps going until the job is finished."
    )


def test_pairs_en_and_tr_lesson_files_by_task_statement_id(tmp_path):
    en_dir = tmp_path / "en_lessons"
    tr_dir = tmp_path / "tr"
    en_dir.mkdir()
    tr_dir.mkdir()
    en_file = en_dir / "2.1.md"
    tr_file = tr_dir / "task_statement_2_1_tool_interface_design_TR.md"
    en_file.write_text("# Tool Interface Design\n")
    tr_file.write_text("# Arac Arayuzu Tasarimi\n")

    lessons = discover_lessons(str(en_dir), str(tr_dir))

    assert lessons == [
        LessonSource(id="2.1", domain=2, en_path=str(en_file), tr_path=str(tr_file)),
    ]


def test_treats_unsuffixed_tr_dir_file_as_en_source_for_domain_1_quirk(tmp_path):
    en_dir = tmp_path / "en_lessons"
    tr_dir = tmp_path / "tr"
    en_dir.mkdir()
    tr_dir.mkdir()
    en_only_file = tr_dir / "task_statement_1_3_subagent_invocation.md"
    en_only_file.write_text("# Subagent Invocation\n")

    lessons = discover_lessons(str(en_dir), str(tr_dir))

    assert lessons == [
        LessonSource(id="1.3", domain=1, en_path=str(en_only_file), tr_path=None),
    ]


def test_excludes_practice_exam_and_yeterlilik_testi_files_from_lessons(tmp_path):
    en_dir = tmp_path / "en_lessons"
    tr_dir = tmp_path / "tr"
    en_dir.mkdir()
    tr_dir.mkdir()
    (tr_dir / "domain_1_practice_exam.md").write_text("quiz content")
    (tr_dir / "domain_4_yeterlilik_testi_TR.md").write_text("quiz content")

    lessons = discover_lessons(str(en_dir), str(tr_dir))

    assert lessons == []


def test_discovers_all_current_repo_lessons_with_correct_domain_1_language_coverage():
    lessons = discover_lessons(
        os.path.join(REPO_ROOT, "content", "en_lessons"),
        os.path.join(REPO_ROOT, "content", "tr"),
    )

    coverage = {l.id: (l.en_path is not None, l.tr_path is not None) for l in lessons}

    assert len(lessons) == 30
    assert coverage["1.1"] == (True, True)
    assert coverage["1.2"] == (True, True)
    assert coverage["1.3"] == (True, True)
    assert coverage["1.7"] == (True, True)
    assert coverage["2.1"] == (True, True)
    assert coverage["5.6"] == (True, True)
    assert all(en and tr for en, tr in coverage.values())


def test_plans_generation_for_every_lesson_when_manifest_is_empty():
    lesson_texts = {("2.1", "en"): "Tool Interface Design. Some content."}

    jobs = plan_narration_jobs(lesson_texts, manifest={})

    assert jobs == [
        NarrationJob(id="2.1", language="en", text="Tool Interface Design. Some content."),
    ]


def test_skips_lesson_whose_manifest_hash_matches_current_text():
    lesson_texts = {("2.1", "en"): "Tool Interface Design. Some content."}
    manifest = {
        "2.1:en": "71eb66882e8fb7e81cfbd436aa08e49f6b99de391665c4e4ed2c534118126358",
    }

    jobs = plan_narration_jobs(lesson_texts, manifest)

    assert jobs == []


def test_regenerates_only_the_lesson_whose_text_changed():
    lesson_texts = {
        ("2.1", "en"): "Tool Interface Design. Some content.",
        ("2.2", "en"): "Structured Error Responses. Updated content.",
    }
    manifest = {
        "2.1:en": "71eb66882e8fb7e81cfbd436aa08e49f6b99de391665c4e4ed2c534118126358",
        "2.2:en": "0000000000000000000000000000000000000000000000000000000000000000",
    }

    jobs = plan_narration_jobs(lesson_texts, manifest)

    assert jobs == [
        NarrationJob(id="2.2", language="en", text="Structured Error Responses. Updated content."),
    ]


def test_narration_filename_encodes_domain_and_lesson_number():
    assert narration_filename("1.1") == "D1-1.mp3"
    assert narration_filename("2.10") == "D2-10.mp3"


def test_returns_single_chunk_when_text_fits_within_limit():
    text = "Paragraph one.\n\nParagraph two."

    chunks = split_into_chunks(text, max_chars=1000)

    assert chunks == ["Paragraph one.\n\nParagraph two."]


def test_splits_on_paragraph_boundaries_when_over_limit():
    text = "Paragraph one is here.\n\nParagraph two is here."

    chunks = split_into_chunks(text, max_chars=30)

    assert chunks == ["Paragraph one is here.", "Paragraph two is here."]
