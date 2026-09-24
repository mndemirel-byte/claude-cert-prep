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

## Practice

**Question Pool**:
The flat bank of exam-style questions (280 as of this writing), each tagged with a Domain, a Scenario, correct answer, and explanation, used exclusively to build Quick Mock and Full-Length Mock attempts. Distinct from the per-Domain quiz questions embedded in a Lesson's own practice-exam content, which stay tied to that Domain's "Yeterlilik testi" page and are never drawn into a Mock attempt.
_Avoid_: Mock bank, Exam bank

**Scenario Combo**:
The 4 of 6 official exam Scenarios drawn for one Mock attempt. Chosen only from combos that can actually supply every Domain's required question count for that attempt's mode (some Domains' questions cluster in just one or two Scenarios, so not every combo of 4 is viable); the combo is then picked at random among the viable ones.
_Avoid_: Scenario selection, Scenario draw

**Quick Mock** / **Full-Length Mock**:
The two Mock attempt modes, both built from a Scenario Combo and a fixed per-Domain question count matching the exam's weighting (Quick: 24 questions / 2 min each; Full-Length: 60 questions / 2 min each, mirroring real exam conditions). Question and answer-option order are randomized per attempt. Replaces the old ~48-question single Mock Exam mode.
_Avoid_: Mock Exam (the old single-mode name), Practice Test

**Flashcard** / **Flashcard Deck**:
A front/back flip card testing a single concept, term, principle, or anti-pattern from a Lesson's "Key Exam Takeaways" table (front: the Concept; back: the Remember text). A Flashcard Deck is one Domain's full set of Flashcards, pooled from every Lesson in that Domain and shown in randomized order each time the deck is opened.
_Avoid_: Study card, Quiz card

**Exam Guide**:
The site's own page reproducing four sections of Anthropic's official Exam Guide PDF (About This Certification, Intended Audience, Exam Details at a Glance, Exam Content Outline) as collapsible entries, replacing the home page's direct "Register for Exam" link — a learner reads the guide here first, then registers from a button at the end of this page.
_Avoid_: Certification guide, About page
