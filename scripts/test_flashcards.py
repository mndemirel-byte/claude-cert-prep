import os

from flashcards import extract_flashcards

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_extracts_a_single_card_from_the_takeaways_table():
    markdown = (
        "## Key Exam Takeaways\n\n"
        "| Concept | Remember |\n"
        "|---|---|\n"
        "| Tool description | THE mechanism for Claude's tool selection |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [
        {"concept": "Tool description", "remember": "THE mechanism for Claude's tool selection"},
    ]


def test_extracts_multiple_cards_in_table_order():
    markdown = (
        "## Key Exam Takeaways\n\n"
        "| Concept | Remember |\n"
        "|---|---|\n"
        "| Hooks | Deterministic — runs 100% of the time |\n"
        "| Prompts | Probabilistic — works most of the time |\n"
        "| Decision rule | If a failure costs money → use a hook |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [
        {"concept": "Hooks", "remember": "Deterministic — runs 100% of the time"},
        {"concept": "Prompts", "remember": "Probabilistic — works most of the time"},
        {"concept": "Decision rule", "remember": "If a failure costs money → use a hook"},
    ]


def test_preserves_inline_formatting_and_code_in_cells():
    markdown = (
        "## Key Exam Takeaways\n\n"
        "| Concept | Remember |\n"
        "|---|---|\n"
        "| `stop_reason` | Check `response.stop_reason` — **never** parse free text |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [
        {"concept": "`stop_reason`", "remember": "Check `response.stop_reason` — **never** parse free text"},
    ]


def test_returns_empty_list_when_no_takeaways_section_exists():
    markdown = "## The Core Idea\n\nSome lesson prose with no takeaways table at all.\n"

    assert extract_flashcards(markdown) == []


def test_recognizes_the_turkish_takeaways_heading():
    markdown = (
        "## Sınav İçin Temel Çıkarımlar\n\n"
        "| Kavram | Hatırla |\n"
        "|---|---|\n"
        "| Hook | Deterministik — %100 çalışır |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [
        {"concept": "Hook", "remember": "Deterministik — %100 çalışır"},
    ]


def test_stops_at_the_next_section_and_ignores_later_tables():
    markdown = (
        "## Key Exam Takeaways\n\n"
        "| Concept | Remember |\n"
        "|---|---|\n"
        "| Hooks | Deterministic |\n"
        "\n---\n\n"
        "## Practice Scenario\n\n"
        "| Unrelated | Table |\n"
        "|---|---|\n"
        "| Should not | Appear in cards |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [{"concept": "Hooks", "remember": "Deterministic"}]


def test_recognizes_the_key_takeaways_heading_variant_used_by_domain_4():
    markdown = (
        "## Key Takeaways\n\n"
        "| Concept | Remember |\n"
        "|---|---|\n"
        "| Explicit criteria | State the bar explicitly, don't imply it |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [
        {"concept": "Explicit criteria", "remember": "State the bar explicitly, don't imply it"},
    ]


def test_recognizes_the_key_takeaway_listesi_heading_variant():
    markdown = (
        "## Key Takeaway Listesi\n\n"
        "| Kavram | Hatırla |\n"
        "|---|---|\n"
        "| Açık kriter | Eşiği ima etme, açıkça belirt |\n"
    )

    cards = extract_flashcards(markdown)

    assert cards == [
        {"concept": "Açık kriter", "remember": "Eşiği ima etme, açıkça belirt"},
    ]


def test_extracts_cards_from_every_current_en_lesson_with_no_empty_decks():
    en_dir = os.path.join(REPO_ROOT, "content", "en_lessons")
    empty = []
    total = 0
    for fname in sorted(os.listdir(en_dir)):
        text = open(os.path.join(en_dir, fname), encoding="utf-8").read()
        cards = extract_flashcards(text)
        total += len(cards)
        if not cards:
            empty.append(fname)

    assert empty == []
    assert total > 0
