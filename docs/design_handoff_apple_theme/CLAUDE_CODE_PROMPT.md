# Prompt for Claude Code

Paste this as the first message in a Claude Code session opened at the root of the claude-cert-prep repository (the app deployed at https://claude-cert-prep-mocha.vercel.app/), with this handoff folder copied into the repo (e.g. `./design_handoff_apple_theme/`).

---

Read `design_handoff_apple_theme/README.md` fully before touching code. It documents a hi-fi redesign of this app. The HTML files next to it are design references (open them in a browser to inspect); do not import them — recreate the design in this codebase's existing framework, routing, i18n (TR/EN) and data.

Goal: implement the **Apple direction, light + dark, Palette A (Blue)** as the app's new UI, built on a CSS-variable token system so the other directions/palettes in the README can be added later by adding token sets only.

Work in this order and stop for my review after each step:
1. Explore the codebase: framework, routing, how domains/lessons/quiz/scenarios/practice data and audio are loaded, existing theme or CSS setup. Summarize before changing anything.
2. Add the token layer (`data-style` / `data-theme` / `data-palette` on <html>, CSS variables per README "Theme architecture"), a theme toggle in the nav (persist to localStorage, respect prefers-color-scheme). Domain colors D1–D5 come from the palette hues via OKLCH.
3. Home page (web + responsive mobile): nav, hero + stat cells, weight bar, action cards in the order Exam Guide → Exam scenarios → Practice (stacked full-width on mobile, never horizontally scrolling), domain accordion, footer. Mobile gets the translucent bottom tab bar.
4. Domain page: header, segmented Lessons/Quiz control, lesson accordion with the per-lesson audio button and inline player (wire to the real audio, ⏮/⏭ ±15s, speed cycle), quiz card (sticky on web, inline on mobile with fixed bottom actions).
5. Scenarios page and Practice page (Quick Mock / Full-Length Mock / Flashcards), including the in-progress mock question layout and the flip flashcard. Use the app's real scenario titles — the ones in the prototype are placeholders.
6. Verify light and dark at 1180px and 390px against the reference HTML; check contrast (4.5:1 body text) and 44px minimum tap targets on mobile.

Constraints: keep all existing copy and data verbatim; no new dependencies unless already used by the project; inline glyphs in the mock should map to the project's icon set (or SF Symbols-like SVGs). Match spacing, radii, weights and colors exactly as listed in the README.
