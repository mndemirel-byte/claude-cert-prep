# Claude Cert Prep

A single-file, bilingual (EN/TR) study guide and mock-exam trainer for the Claude Certified Architect (Foundations) exam, built as a static site (`content/*.md` → `dist/index.html`) with no runtime backend.

## Language

**Lesson**:
The prose teaching content for a single Task Statement (its narrative explanation, core ideas, examples). Distinct from that Task Statement's practice-exam questions, which are separate assessment content and out of scope for narration.
_Avoid_: Content, Page, Article

**Narration**:
A pre-generated MP3 audio rendition of a Lesson's spoken-ready text (code blocks stripped, headings kept), produced via OpenAI's TTS API (model `gpt-4o-mini-tts`, voice `cedar`, instructions "warm, friendly, clear educator tone") by a local script and committed to the repo alongside `dist/`. Generated once per language a Lesson exists in — some Lessons only have a Narration in one language, mirroring the site's existing asymmetric EN/TR content coverage.
_Avoid_: Audio, TTS, Voiceover, Podcast

**Domain Playlist**:
The ordered sequence of Narrations for all Lessons within a single Domain. Pressing play on any Lesson starts the Domain Playlist from that Lesson and auto-advances through the rest of the Domain's Lessons; it stops at the end of the Domain and does not continue into the next Domain.
_Avoid_: Course playlist, Continuous playlist, Queue

**Listening Position**:
The (Lesson, timestamp) pointer persisted in the browser's `localStorage` so Narration playback can resume where the listener left off after closing or backgrounding the app.
_Avoid_: Progress, Bookmark, Resume point
