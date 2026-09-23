from narration import prepare_narration_text


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
