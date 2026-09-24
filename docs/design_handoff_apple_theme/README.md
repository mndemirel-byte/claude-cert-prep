# Handoff: Claude Cert Prep — Apple-style theme system (web + mobile, light/dark)

## Overview
A visual redesign of the existing single-page study app at https://claude-cert-prep-mocha.vercel.app/ (hash routes: #home, #domain-N, #scenarios, practice, exam guide). The design keeps the app's content and structure and re-skins it with an **Apple / iOS-grouped-list aesthetic** (default), plus three alternative directions (SaaS, Futuristic, Developer) that share the same token contract. Every direction ships in **light and dark**, with **2 palettes** each. Default target: **Apple · Light · Palette A (Blue)**.

## About the Design Files
The files in this bundle are **design references created in HTML** (`Cert Prep Themes.dc.html`, `Mobile Study Guide.dc.html`, plus `support.js` runtime). They are prototypes showing intended look and behavior — **not production code to copy**. Recreate them in the target codebase's existing environment (the Vercel-hosted SPA and whatever framework it already uses; keep its routing, i18n TR/EN switch, and lesson/quiz data). If no framework constraints exist, React + CSS variables is the most natural fit for the token system below.

## Fidelity
**High-fidelity.** Colors, type, radii, spacing and copy are final. Recreate pixel-accurately, but express all values as CSS custom properties so the theme/palette switch is a single root attribute change.

## Theme architecture (implement first)
One token set drives everything. Suggested: `<html data-style="apple" data-theme="light" data-palette="A">` and CSS variables per combination.

Token contract (names used throughout this doc):
- `--bg` page background · `--surface` cards · `--surface2` inset/segmented track · `--text` · `--muted` secondary text · `--border`
- `--accent` primary action · `--on-accent` text on accent · `--accent-text` accent used as text on bg
- `--d1…--d5` domain colors · `--on-domain` text on domain color
- `--code-bg` `--code-fg` code blocks · `--chip-bg` `--chip-fg` "EXAM TRAP" chips and selected quiz option background
- `--tabbar-bg` translucent bottom bar (with `backdrop-filter: blur(12px)`)
- Shape: `--r` card radius · `--rs` small radius (buttons, inputs) · `--rs-in` inner radius of segmented control · `--btn-r` round buttons · `--dot-r` badges/dots
- Type: `--font` UI · `--mono` code/labels · `--hw` heading weight · `--ls` body letter-spacing · `--ls-h` heading letter-spacing · label transform + tracking

### Apple (default)
- font: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif`; mono: `ui-monospace, "SF Mono", Menlo, monospace`
- r 20px · rs 12px · rs-in 9px · btn-r 50% · dot-r 50% · hw 700 · ls -0.02em · ls-h -0.035em · labels UPPERCASE, tracking 0.04em · domain bar gap 4px · list gap 10px · cards: yes (white insets)
- Light: bg #F2F2F7 · surface #FFFFFF · surface2 #E5E5EA · text #000000 · muted #6C6C70 · border #E0E0E5 · code-bg #1C1C1E · code-fg #F2F2F7 · shadow none
- Dark: bg #000000 · surface #1C1C1E · surface2 #2C2C2E · text #FFFFFF · muted #98989F · border #2C2C2E · code-bg #0A0A0B · code-fg #F2F2F7
- Domain/accent colors are OKLCH: light `oklch(0.58 0.19 H)`, dark `oklch(0.72 0.17 H)`
  - Palette A "Blue": accent H=255; domains D1–D5 hues 255, 150, 30, 300, 70
  - Palette B "Graphite": monochrome; domain i (0-based) = light `oklch(0.32+0.09i 0.06 275)`, dark `oklch(0.82−0.09i 0.06 275)`; accent `oklch(L 0.19 275)`
- accent-text: light `oklch(0.45 0.14 H)`, dark `oklch(0.80 0.12 H)`
- chip-bg: light `oklch(0.93 0.05 H)` / dark `oklch(0.30 0.08 H)`; chip-fg: light `oklch(0.35 0.12 H)` / dark `oklch(0.90 0.10 H)`
- on-accent / on-domain: light #FFFFFF, dark #0B0D15
- tabbar-bg: light rgba(255,255,255,.85), dark rgba(20,22,30,.85)
- Segmented control (Lessons | Quiz): track surface2, 4px padding, 1px border; active segment = surface with shadow `0 1px 3px rgba(0,0,0,.12)`, text color text.

### Alternative directions (same contract)
- **SaaS**: Plus Jakarta Sans / JetBrains Mono · r 16 · rs 10 · btn-r 12 · hw 800 · ls-h -0.03em · light bg #F5F6FA surface #FFF surface2 #EDEFF5 text #12142B muted #646A85 border #E3E6EF shadow `0 1px 2px rgba(18,20,43,.05), 0 10px 30px -14px rgba(18,20,43,.12)` code-bg #12142B · dark bg #0B0D15 surface #141726 surface2 #1C2033 text #F2F3F9 muted #8C92AD border #252A40 · colors oklch(0.55 0.15 H) light / (0.74 0.14 H) dark · A Indigo 275 [275,200,330,150,50] · B Teal 175 [175,250,25,300,95] · active segment = text on bg
- **Futuristic**: Space Grotesk / JetBrains Mono · r 4 · rs 2 · btn-r 2 · dot-r 0 · hw 700 · mono UPPERCASE labels tracking 0.14em · no cards (hairline rows, list gap 0) · glow on accent/domain elements `0 0 0 1px C, 0 0 18px -2px C` · light bg #E9EDF0 surface #F6F8F9 surface2 #DDE3E8 text #0B1014 muted #5A6672 border #B9C3CC code-bg #0B1014 code-fg #C8F2FF · dark bg #04060A surface #0A0E14 surface2 #10161E text #E8F1F7 muted #7A8A99 border #1C2632 code-fg #9BE8FF · colors oklch(0.50 0.18 H)/(0.78 0.20 H) · A Cyan 200 [200,320,130,280,70] · B Acid 120 [120,200,30,300,60] · active segment = accent
- **Developer**: IBM Plex Mono everywhere · r 6 · rs 4 · hw 600 · ls -0.02em · lowercase labels · no cards, list gap 0 · domain numbers "01…05" · light bg #FFF surface #F6F8FA surface2 #EAEEF2 text #1F2328 muted #656D76 border #D0D7DE code-bg #F6F8FA · dark bg #0D1117 surface #161B22 surface2 #21262D text #E6EDF3 muted #8B949E border #30363D code-bg #010409 · colors oklch(0.50 0.13 H)/(0.74 0.13 H) · A Green 150 [150,250,40,300,200] · B Amber 70 [70,210,330,150,260]

## Screens / Views
Web frames are 1180px wide (content padding 48px); mobile frames 390×844 (content padding 20px, bottom tab bar). All copy below is verbatim from the live app.

### 1. Home (web)
- Top nav: 28px accent square (radius rs) + "CCA Foundations" 15/700; links "Domains · Scenarios · Practice · Exam guide" 14/500 muted (active = text); TR|EN pill (1px border, 12px mono 700, active segment text-on-bg); theme toggle 32px circle.
- Hero grid `1.2fr 1fr`, gap 56px, align end. Left: label "Study guide" 12/600 accent-text (Apple: uppercase); H1 "Claude Certified Architect" + line break + "Foundations" (muted, 500) — 56px, weight hw, line-height 1, ls-h; paragraph 16/1.6 muted, max-width 560px: "The exam has five domains. The bar below shows each domain's weight in the exam; every domain page has the lessons first, followed by a practice quiz with answer key."
- Right: 3 stat cells in a 1px-gap grid on border color, radius r: 5 domains · 30 lessons · 45 questions (32px number, 12px label).
- Domain weight bar: flex row height 64px, gap 4px; each segment flex = weight (27/18/20/20/15), background --dN, radius rs, padding 12×16, shows "27%" 20/700 and "D1" 11px at 85% opacity.
- Action cards grid 3×1fr gap 16, min-height 140, padding 22, radius r, in this order:
  1. **Claude Certified Architect – Foundations Exam Guide** — "Official exam guide from Anthropic." — surface card, 1px border.
  2. **Exam scenarios** — "4 of 6 are drawn at random; which domain is asked in which context?" — tinted: bg light `oklch(0.94 0.04 H)` / dark `oklch(0.24 0.04 H)`, border `oklch(0.88 0.05 H)` / `oklch(0.32 0.05 H)`.
  3. **Practice** — "Study with Quick Mock, Full-Length Mock, or Flashcards" — inverted: bg text, fg bg (Futuristic: transparent with accent border/text).
  Title 18/700 with "→" right-aligned; desc 13/1.5 at 80% opacity.
- Domain list (accordion), gap list-gap: row grid `72px 1fr 56px`, gap 24, padding 24, surface, 1px border, radius r. Left: number 40px weight hw in --dN. Middle: title 20/700, desc 14/1.55 muted, meta 12px "Weight 27% · 7 lessons · 10 questions" (label style). Right: 44px round button in --dN with "+" / "−" 22px.
- Footer: 12px muted centered "Claude Certified Architect (Foundations) study notes · 5 domains · 45 questions".

### 2. Domain page (web)
- "← All domains" 13/600 muted. Header: dot (10px, --d1) + "Domain 1 · 27% of the exam" label in --d1; H1 44px "Agentic Architecture & Orchestration"; summary 16/1.6 muted.
- Segmented control "Lessons · 7 | Practice quiz · 10", 8×18 padding, 14/600.
- Two columns `1fr 440px` gap 32. Left: lesson accordion rows (padding 18×22, gap 14). Row: "1.1" mono 13/600 --d1 width 32 · title 17/600 · **audio button** 32px circle, 1.5px border, "▶" 11px in --d1 (background chip-bg while playing) · "+/−" 18px muted.
  - Clicking ▶ (stopPropagation) opens an inline **audio player** under the row header: top border 1px, padding 12px 0 0, mono 12px muted: ⏮ · "0:04" · progress track 6px surface2 with --d1 fill and 14px round thumb · "5:43" · ⏭ · "1x" pill (1px border, radius rs, --d1 text).
  - Expanded body (padding-left 48): "The Core Idea" 16/700; paragraph 14/1.65 muted with bold/italic; code block (code-bg/fg, 1px border, radius rs, mono 12.5/1.6, pre); chip "EXAM TRAP" (11/700, chip colors, pill) + note.
- Right: sticky quiz card (top 24) padding 24, gap 16: header "Practice quiz · Question 1 / 10" + "TS 1.1" mono --d1; progress 4px (10%); question 14/1.55; 4 options (padding 12×14, radius rs, 1px border; badge 24px A–D mono; selected: border accent, bg chip-bg, badge accent/on-accent); buttons "Check answer" (accent, 14/700) + "Skip" (outline).

### 3. Exam scenarios (web)
- "← Home"; label "Exam scenarios"; H1 44px "6 scenarios, 4 on your exam"; paragraph "4 of 6 are drawn at random; questions are grouped under the scenario they belong to. Each scenario below lists which domains it tends to test."
- 2-column grid gap 16 of scenario cards (padding 24, gap 12): "Scenario N" mono 12/600 muted + domain pills (11/700, bg --dN, on-domain) right; title 20/700; desc 14/1.55 muted; "Read scenario →" 13/600 accent-text.
- **Scenario titles/descriptions in the prototype are placeholders** — use the app's real six scenarios.

### 4. Practice (web)
- "← Home"; label "Practice"; H1 44px "Study with Quick Mock, Full-Length Mock, or Flashcards".
- 3 mode cards (padding 24, min-height 170): title 20/700 + "→"; meta 12/600 label-style; desc 14/1.5. Middle card (Full-Length Mock) is primary: bg accent, all text on-accent. Meta copy: "10 questions · 2 scenarios · ~20 min" / "45 questions · 4 of 6 scenarios · 90 min · 720/1000 to pass" / "30 cards · one per task statement".
- Below, grid `1fr 420px` gap 24: **in-progress mock question** card (padding 28): header "Full-Length Mock · 12 / 45" + pill "Scenario 1" (--d1) + timer "01:34:12" mono 13/600 accent-text; 4px progress (27%); question 15/1.6; options as in quiz card (A selected); footer "← Previous" outline / "Next →" accent.
- **Flashcard**: bg text, fg bg, radius r, padding 28, min-height 300; header "Flashcard 1 / 30 · TS 1.1" at 70% opacity; front 24/700 question, back 20/500 answer; "Tap to flip"; click toggles.

### 5. Mobile Home (390×844)
- Status bar 48px. Header row: 24px accent square + "CCA Foundations" 14/700; TR|EN pill.
- Label 11px; H1 32px (hw, ls-h) "Claude Certified Architect Foundations" (Foundations muted 500); paragraph 14/1.55 muted.
- Weight bar 14px tall gap 4 + 5-col grid of "27% / D1" (15/700 in --dN, 10px muted); line "5 domains · 30 task statement lessons · 45 practice questions" 12px muted.
- Action cards **stacked vertically** (full width, gap 10, padding 16) in the same order as web: Exam Guide, Exam scenarios, Practice. No horizontal scrolling.
- Domain accordion cards (padding 16): 40px round number badge in --dN, title 15/700, meta 11px, "+/−" 20px; expanded desc 13/1.5 muted indented 52px.
- Bottom tab bar (fixed, 10px 20px 28px, tabbar-bg + blur, top border): Home · Domains · Scenarios · Practice; 22px ring icon + 10/600 label; active = accent filled.

### 6. Mobile Domain page
- "← All domains"; header dot + label; H1 28px; summary 13px; full-width segmented "Lessons · 7 | Quiz · 10".
- Lesson rows (padding 14×16): "1.1" mono 12 width 26 · title 14/600 · **28px audio button** ("▶" 10px) · "+/−" 16px. Player row as web but mono 11px, padding 10px 0 0. Expanded body 13/1.6 with code block mono 11px (overflow-x auto).
- Quiz card inline (padding 18) with header, question 13px, options 12px (badge 22px).
- Fixed bottom action bar: "Check answer" (accent, flex 1, padding 14) + "Skip" outline.

### 7. Mobile Scenarios
- "← Home"; label; H1 30px "6 scenarios, 4 on your exam"; short paragraph. Scenario cards (padding 16, gap list-gap): "Scenario N" + pills (10/700), title 15/700 + "›" chevron, desc 12/1.5. Tab bar active = Scenarios.

### 8. Mobile Practice
- "← Home"; label; H1 30px "Quick Mock, Full-Length Mock, or Flashcards"; 3 stacked mode cards (padding 16; title 16/700 + "→"; meta 11/600) — Full-Length Mock primary (accent). Flashcard (padding 20, min-height 200, front 19/700, back 15/500). Tab bar active = Practice.

## Interactions & Behavior
- Domain rows and lesson rows: single-open accordion (opening one closes the other); icon "+"→"−". 150–200ms ease-out height/opacity.
- Audio ▶: toggles an inline player row per lesson; multiple lessons may not play simultaneously (playing a new one stops the previous). Hook to the real audio files; show live current time / duration; ⏮/⏭ seek ±15s; "1x" cycles 1x → 1.25x → 1.5x → 2x.
- Quiz options: tap selects (border accent, bg chip-bg); "Check answer" reveals correct answer + rationale (app already has this content).
- Flashcard: tap flips (front/back); consider a 300ms 3D flip.
- Theme toggle in nav: switches data-theme and persists to localStorage; respect `prefers-color-scheme` on first load.
- Mobile tab bar: translucent with blur; safe-area bottom padding (28px in mock ≈ env(safe-area-inset-bottom)).
- Responsive: web layout collapses to the mobile layout below ~720px (hero stacks, quiz card moves below lessons, action cards stack, weight bar shows compact 14px variant).

## State Management
- `style` ('saas'|'futur'|'dev'|'apple'), `theme` ('light'|'dark'), `palette` ('A'|'B') — global, persisted.
- `openDomain: number|null`, `openLesson: number|null`, `playingLesson: number|null`, `selectedOption`, `flashcardFlipped`, mock-exam progress (index, answers, timer) — existing app data model for domains/lessons/questions is reused as-is.

## Design Tokens (summary)
- Spacing: 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32, 40, 48, 56.
- Type (web): 56/44 H1, 32 stat, 20 titles, 18 card titles, 17 lesson, 16 body, 15 nav/brand, 14 secondary, 13 links, 12 labels, 11 pills. Mobile: 32/30/28 H1, 15–16 titles, 13–14 body, 11–12 labels, 10 tab labels.
- Radii (Apple): 20 card, 12 small, 9 segmented inner, 50% round buttons, 99px pills.
- Domain weights: 27, 18, 20, 20, 15.

## Assets
No raster assets. Icons are glyphs in the mock (▶ ⏮ ⏭ + − → ‹ › ☀ ☾); replace with SF Symbols / the app's icon set (play.fill, gobackward.15, goforward.15, plus, minus, chevron.right, sun.max, moon).

## Screenshots
`screenshots/apple-light/` and `screenshots/apple-dark/` — 1x captures of every reference frame at design size: `web-home`, `web-domain`, `web-scenarios`, `web-practice` (1180px wide) and `mobile-home`, `mobile-domain`, `mobile-scenarios`, `mobile-practice` (390×844). Mobile frames show the initial viewport; scroll the HTML reference for content below the fold.

## Files
- `Cert Prep Themes.dc.html` — main reference: web Home, Domain, Scenarios, Practice + mobile Home, Domain, Scenarios, Practice; top switcher for Style / Theme / Palette (16 combinations).
- `Mobile Study Guide.dc.html` — earlier mobile-only exploration (Sand / Night / Ink); reference only.
- `support.js` — runtime needed to open the .dc.html files in a browser; not part of the implementation.
- `CLAUDE_CODE_PROMPT.md` — the prompt to start the implementation session.
