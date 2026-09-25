# Domain 1 — Teknik Doğruluk ve Derinlik İnceleme Raporu

**Tarih:** 25 Eylül 2026
**Kapsam:** `task_statement_1_1` … `task_statement_1_7`, `domain_1_practice_exam.md` ve mevcut TR çevirileri (1.1, 1.2)
**Karşılaştırma tabanı:**
- Skilljar prep sayfası (`/page/claude-certified-architect-foundations-prep-courses`) — bu sayfa yalnızca 7 hazırlık kursunun listesini içeriyor (AI Fluency, Building with the Claude API, Claude on Google Cloud, Claude Code in Action, Claude 101, Claude with Amazon Bedrock, Introduction to MCP). Domain 1 için ders içeriği taşımıyor; bu yüzden asıl karşılaştırma **resmi Exam Guide'ın Domain 1 bölümü** (task statement + knowledge/skills maddeleri) ve güncel Anthropic dokümantasyonu (Messages API, Agent SDK, Claude Code hooks/subagents/sessions) ile yapıldı.
- Domain 1 için ilgili prep kursları: *Building with the Claude API* (agentic loop, tool use) ve *Claude Code in Action* (Hooks, Steering Long Sessions, Permission Modes, Headless modülleri).

---

## Genel Değerlendirme

Yedi dokümanın tamamı exam guide'daki task statement'larla **birebir hizalı** ve sınav mantığını (olasılıksal vs deterministik, hatayı kaynağına izleme, isolation principle) doğru öğretiyor. Sınav geçmeye yönelik "hangi şıkkı reddet" yaklaşımı güçlü.

Zayıf taraf: Dokümanlar exam guide'ın *özeti* seviyesinde kalıyor; API/SDK katmanında **mekanizma detayı** (tool_result yapısı, hook event adları, `fork_session`'ın `resume` ile ilişkisi vb.) eksik. Sınav "Architect" sınavı olduğu için senaryolar bu mekanizma bilgisini distractor olarak kullanabiliyor. Ayrıca bazı ifadeler mutlak ("tek güvenilir sinyal", "%100 garanti") — teknik olarak nüans gerektiriyor.

**Bulgu özeti:** 3 teknik yanlış/eksik-yanıltıcı ifade, 12 derinlik eksiği, 6 geliştirme önerisi.

---

## Task Statement 1.1 — Agentic Loops

### ✅ Doğru olanlar
- `stop_reason` kontrolü, tool sonuçlarını geçmişe ekleme, üç anti-pattern, model-driven vs pre-configured ayrımı — hepsi exam guide ile uyumlu.
- "Iteration cap safety net olabilir ama birincil mekanizma olamaz" nüansı doğru ve önemli.

### ❌ Yanlış / yanıltıcı
1. **"`stop_reason` için sadece `tool_use` ve `end_turn` var" izlenimi.** Doküman "`end_turn` → bitti, `tool_use` → devam" dışında bir değer tanımıyor. Gerçekte `stop_reason` değerleri: `end_turn`, `tool_use`, `max_tokens`, `stop_sequence`, `pause_turn`, `refusal`, `model_context_window_exceeded`. Verilen örnek kod (`if end_turn … elif tool_use`) `max_tokens` durumunda sessizce yarım kalmış yanıt döndürür — bu bir bug. Sınavda "agent bazen yarım cümleyle duruyor" senaryosu gelirse öğrenci `max_tokens`'ı tanımaz.

### ⚠️ Eksik derinlik
2. **`tool_result` bloğunun yapısı yok.** "Sonucu geçmişe ekle" deniyor ama *nasıl* eklendiği yok: `role: "user"` mesajı içinde `type: "tool_result"` bloğu, `tool_use_id` eşleşmesi, `is_error: true` ile hata bildirimi. Bu, "Building with the Claude API" kursunun çekirdek içeriği.
3. **Paralel tool çağrıları.** Claude tek yanıtta birden fazla `tool_use` bloğu döndürebilir; **hepsinin** `tool_result`'ı hemen sonraki tek bir user mesajında gönderilmelidir. Örnek kod `content[0]` üzerinden düşündürüyor — sınav bu tuzağı kullanabilir. `disable_parallel_tool_use` seçeneğinden bahsedilmeli.
4. **`pause_turn`** (server-side tool'lar, ör. web search) — yanıt geri gönderilerek devam edilir; "iteration cap" tartışmasıyla doğrudan ilişkili.
5. Loop'ta **hata yönetimi** (tool exception → `is_error` tool_result olarak Claude'a döndür, loop'u kırma) exam guide "recommended preparation" bölümünde açıkça geçiyor; dokümanda yok.

### 💡 Geliştirme
- Örnek kodu tam bir loop iskeletine dönüştür: `while True` + `stop_reason` switch (7 değer) + `tool_result` bloklarının tek user mesajında toplanması + safety-net iteration cap.
- "Tek güvenilir sinyal" ifadesini "**birincil** sinyal" yap.

---

## Task Statement 1.2 — Multi-Agent Orchestration

### ✅ Doğru olanlar
- Hub-and-spoke, isolation principle, koordinatör sorumlulukları, narrow decomposition failure — exam guide ile uyumlu. Practice scenario iyi kurgulanmış.

### ⚠️ Eksik derinlik
6. **Scope partitioning / duplication.** Exam guide Skills: "Partitioning research scope to minimize duplication across subagents." Dokümanda hiç yok. Sınav "iki subagent aynı kaynakları araştırıp maliyet ikiye katlanıyor" senaryosu sorabilir → cevap: koordinatörün kapsamı ayrık (non-overlapping) bölmesi.
7. **Iterative refinement loop** yalnızca bir madde olarak geçiyor. Exam guide bunu ayrı bir skill olarak vurguluyor: koordinatör synthesis çıktısını değerlendirir, boşluk bulursa yeniden delege eder (evaluator-optimizer pattern). Kısa bir alt bölüm + "ne zaman durur" kriteri eklenmeli.
8. **Dynamic selection vs routing through all.** Exam guide: "dynamically select subagents rather than routing through all." Dokümanda parantez içi bir not. "Her isteği tüm subagent'lardan geçirmek" anti-pattern olarak açıkça yazılmalı (maliyet + latency + gürültü).
9. **Isolation principle'ın nüansı.** "Subagent'lar hiçbir şeyi miras almaz" ifadesi Claude Code/Agent SDK bağlamında tam doğru değil: subagent kendi system prompt'unu, tool tanımlarını ve proje CLAUDE.md'sini alır; **konuşma geçmişini** almaz. Fork edilmiş subagent ise geçmişi fork noktasına kadar alır. Sınav için "konuşma geçmişi miras alınmaz" vurgusu yeterli ama TR ders notunda "hiçbir şey" yerine "koordinatörün konuşma geçmişini ve ara bulgularını" demek daha doğru.

### 💡 Geliştirme
- Hub-and-spoke'un alternatifleriyle (sequential pipeline, peer-to-peer) kısa karşılaştırma tablosu: hangi durumda hangisi, neden sınav hub-and-spoke'u tercih ediyor.

---

## Task Statement 1.3 — Subagent Invocation & Context Passing

### ✅ Doğru olanlar
- Task tool, AgentDefinition (description / system prompt / tool restrictions), üç context passing kuralı, structured metadata örneği, parallel spawning, `fork_session` — exam guide'daki her madde karşılanmış. Practice scenario güçlü.

### ❌ Yanlış / yanıltıcı
10. **`allowedTools` içinde `"Task"`.** Exam guide bunu böyle yazıyor, dolayısıyla **sınav için "Task" doğru cevaptır** — dokümanı değiştirme. Ancak güncel Agent SDK'da araç `"Agent"` olarak yeniden adlandırıldı (`tool_use` bloklarında `Agent`, `system:init` tools listesinde hâlâ `Task`). Dokümana bir dipnot eklenmeli: "Sınavda Task; güncel SDK'da Agent — ikisini de tanı."

### ⚠️ Eksik derinlik
11. **AgentDefinition alanları eksik.** Gerçek alanlar: `description` (zorunlu), `prompt` (zorunlu), `tools`, `disallowedTools`, `model`, `maxTurns`, `background`, `skills`, `mcpServers`, `permissionMode`. En azından `model` (subagent'a daha ucuz model verme — maliyet senaryoları) ve `maxTurns` eklenmeli. Ayrıca `.claude/agents/*.md` dosya tabanlı tanım ile programatik `agents` seçeneği arasındaki ilişki bir cümleyle verilmeli.
12. **`fork_session` tek başına çalışmaz** — yalnızca `resume` ile birlikte anlamlı (`resume=<id>, fork_session=True`). Doküman bunu bağımsız bir mekanizma gibi anlatıyor. 1.7 ile birleştirilip tek yerde net anlatılmalı (şu an iki dokümanda birebir aynı paragraf tekrar ediyor).
13. **Parallel spawning'in sınırları.** "Her zaman tercih edilen yaklaşım" ifadesi fazla mutlak: subagent'lar birbirinin çıktısına bağımlıysa (search → synthesis) paralel başlatılamaz. "Bağımsız alt görevler için" kaydı eklenmeli. Ayrıca nesting depth (varsayılan 3, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`) ve concurrency/maliyet kontrolü bir cümleyle geçmeli.
14. **Structured metadata örneği** iyi ama koordinatörün bunu subagent'lardan nasıl *talep ettiği* yok: subagent system prompt'una JSON output şeması vermek (Domain 4'teki structured output ile bağ).

---

## Task Statement 1.4 — Workflow Enforcement & Handoff

### ✅ Doğru olanlar
- Prompt-based (olasılıksal) vs programmatic (deterministik), karar kuralı, multi-concern decomposition, handoff özeti — exam guide ile uyumlu. Practice scenario, exam guide'daki resmi örnek soruyla (get_customer → lookup_order → process_refund, %12) neredeyse birebir; çok iyi.

### ⚠️ Eksik derinlik
15. **"Programmatic prerequisite" nasıl uygulanır?** Doküman "gate/hook yazarsın" diyor ama iki farklı uygulama yolu var: (a) kendi loop'unda tool dispatcher'a state kontrolü (`if not verified: return tool_result(is_error=True, "call verify_identity first")`), (b) Agent SDK/Claude Code'da `PreToolUse` hook ile `permissionDecision: "deny"` + `permissionDecisionReason`. Her iki kalıp da kısa kodla gösterilmeli; "deny sebebini Claude'a geri bildir ki doğru sıraya geçsin" nüansı önemli.
16. **"%100 garanti"** ifadesi: gate, tool'un *çağrılmasını* garanti eder; Claude'un görevi doğru tamamlamasını değil. Sınav bu ayrımı test edebilir ("hook ekledik ama agent şimdi hiç iade yapmıyor" → deny reason eksik). Bir uyarı cümlesi eklenmeli.
17. **Multi-concern request** bölümü 3 satır. Exam guide'ın "distinct parallel items" vurgusu için kısa bir örnek (müşteri: "kargom gelmedi + yanlış fatura kesildi + hesabımı kapatmak istiyorum" → 3 ayrı iş, paralel araştırma, tek yanıt) ve "hangi durumda paralel *olmaz*" (biri diğerine bağlıysa) notu.
18. **Handoff özeti** — exam guide "customer details, root cause, actions taken" diyor. Dokümanda "önerilen aksiyon" var ama **"şimdiye kadar yapılan aksiyonlar / denenen çözümler"** yok; insan agent'ın aynı şeyi tekrar denememesi için kritik. Ayrıca "conversation transcript'e erişemez" ifadesi bir tasarım varsayımı — "erişemeyeceğini varsay, özet self-contained olsun" şeklinde yazılmalı.

---

## Task Statement 1.5 — Agent SDK Hooks

### ❌ Yanlış / yanıltıcı
19. **Hook event adı.** Doküman "Tool Call Interception Hooks" diye jenerik bir isim kullanıyor; gerçek event adı **`PreToolUse`**. Exam guide de adı vermiyor ama sınav şıklarında `PreToolUse`/`PostToolUse` geçmesi çok olası. Başlık `PreToolUse Hooks (Tool Çağrılmadan Önce)` olmalı.

### ⚠️ Eksik derinlik
20. **Diğer hook event'leri hiç yok.** En azından şunlar bir tabloda listelenmeli: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStart`/`SubagentStop`, `PreCompact`, `SessionStart`/`SessionEnd`, `Notification`, `PermissionRequest`. Sınav "subagent bittiğinde loglamak için hangi hook?" gibi sorabilir.
21. **Hook çıktıları / karar mekanizması yok.** `PreToolUse` → `permissionDecision: allow | deny | ask`, `permissionDecisionReason`, `updatedInput` (girdiyi değiştirme). `PostToolUse` → `updatedToolOutput` (sonucu değiştirme — normalizasyon tam olarak burada yapılır), `additionalContext`. `PostToolUse`'un **engelleyemeyeceği** (tool zaten çalıştı) belirtilmeli — sınavda "PostToolUse ile iade işlemini engelle" şıkkı distractor olur.
22. **Hook tanımlama biçimleri.** Claude Code'da `settings.json` (shell komutu, exit code 2 = block, JSON stdout), Agent SDK'da programatik callback (`hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[fn])]}`). Matcher kavramı (hangi tool'lara uygulanacağı) hiç yok.
23. **Hook vs prompt tablosuna üçüncü sütun**: "Permission modes / allowedTools" — bazı kuralları hook yazmadan da deterministik uygulayabilirsin (tool'u hiç vermemek). Sınav "en basit deterministik çözüm" sorabilir.

### 💡 Geliştirme
- Practice scenario tek açık uçlu soru; 1.4'teki gibi 4 şıklı formata çevrilmeli ve şıklardan biri "PostToolUse ile engelle" olmalı.

---

## Task Statement 1.6 — Task Decomposition

### ✅ Doğru olanlar
- Fixed sequential (prompt chaining) vs dynamic adaptive, attention dilution, multi-pass mimari — exam guide ile uyumlu; practice scenario iyi.

### ⚠️ Eksik derinlik
24. **Anthropic'in "Building Effective Agents" pattern seti** ile bağ kurulmamış: prompt chaining, routing, parallelization (sectioning + voting), orchestrator-workers, evaluator-optimizer. Sınavın terminolojisi bu; 1.2'deki hub-and-spoke = orchestrator-workers, 1.2'deki refinement = evaluator-optimizer olduğu söylenmeli. Bir eşleme tablosu yeterli.
25. **Prompt chaining'de ara doğrulama (gate)**: her adım arasında programatik kontrol (ör. "analiz çıktısı boşsa devam etme") — exam guide'da "sequential steps" vurgusu bununla birlikte anlamlı.
26. **"Daha büyük model / daha büyük context window çözmez"** iddiası doğru yönde ama gerekçesi zayıf. Attention dilution'ın context window kapasitesiyle değil, tek geçişte tutarlı kriter uygulamayla ilgili olduğu bir cümleyle açıklanmalı; ayrıca multi-pass'in maliyeti (daha fazla çağrı) ve bunun kabul edilebilir trade-off olduğu belirtilmeli.
27. Dynamic decomposition'ın **durma kriteri** yok: keşif ne zaman biter, alt görev sayısı nasıl sınırlanır (bütçe/depth). Sınav "agent sonsuz keşif yapıyor" senaryosu sorabilir.

---

## Task Statement 1.7 — Session State & Resumption

### ✅ Doğru olanlar
- Resume / fork_session / fresh start with summary injection üçlüsü, stale context, spesifik dosya bildirimi — exam guide'daki tüm knowledge/skill maddeleri karşılanmış. Karar tablosu çok iyi.

### ⚠️ Eksik derinlik
28. **Mekanizma detayı.** `--resume <name>` var ama session'ın nasıl adlandırıldığı yok (`claude --name <ad>` / `/rename <ad>`), `--continue` (son oturum) ile farkı yok, Agent SDK karşılıkları yok (`resume`, `continue_conversation`, `fork_session`, `session_id`). Bir tablo yeterli.
29. **`fork_session` = `resume` + `fork_session: true`** (bkz. madde 12). Fork'un orijinal oturumu değiştirmediği, yeni session ID ürettiği belirtilmeli.
30. **Context compaction** (`/compact`, `PreCompact` hook) — "uzun oturumda context kalitesi düştü" senaryosunun fresh-start dışındaki alternatifi. Skilljar "Claude Code in Action → Steering Long Sessions" modülü tam bunu işliyor; dokümanda yok.
31. **"Summary injection" nasıl yapılır?** Yapılandırılmış özetin hangi kanaldan verildiği (ilk prompt, CLAUDE.md, `--append-system-prompt`, bir dosya) ve özetin içeriği (bulgular, kararlar, kalan işler, değişen dosyalar) örneklenmeli.

---

## Practice Exam (domain_1_practice_exam.md)

- **Kapsam dengesi:** 10 sorunun 4'ü "prompt vs deterministik" mantığına dayanıyor (Q5, Q6, Q8, Q10 aynı reddetme kalıbı). Sınav dağılımına göre 1.2 (scope partitioning, dynamic selection) ve 1.5 (hook event'leri) alt konularından soru yok.
- **Q1:** Kod `response.content[0].text` kullanıyor; içerik `tool_use` ile başlarsa `.text` AttributeError verir — bu üçüncü bir bug ve şık açıklamasında kullanılabilir.
- **Q3:** Doğru cevap B iyi, ancak "C yanlış" açıklaması zayıf: text bloğunu kullanıcıya göstermek aslında yanlış değil (streaming UI'larda yapılır). C'nin yanlışlığı "yeni döngü başlat" belirsizliği ise şık daha net yazılmalı.
- **Q6:** B şıkkı ("API'leri ISO 8601 döndürecek şekilde değiştir") — kendi MCP server'ınsa bu meşru bir çözüm. Sorunun "tool'lar üçüncü parti" olduğunu belirtmesi gerekir.
- **Eksik soru tipleri:** `max_tokens`/`pause_turn` handling; paralel `tool_use` bloklarına tek user mesajında yanıt; `PostToolUse` ile engelleme denemesi (distractor); scope overlap; `fork_session` için `resume` gerekliliği; nesting depth.

---

## TR Çevirileri (1.1, 1.2)

- İçerik İngilizce ile birebir; ekstra hata yok. Ancak yukarıdaki düzeltmeler EN dosyasına yapıldığında TR dosyalarının da senkronize edilmesi gerekiyor. 1.3–1.7 zaten Türkçe yazılmış; 1.1–1.2 için EN/TR çift kopya tutmak bakım yükü — tek dil önerilir.

---

## Öncelik Sırası (yapılacaklar)

**Yüksek (sınavda puan kaybettirebilir):**
1. 1.1'e tüm `stop_reason` değerleri + `max_tokens`/`pause_turn` davranışı (madde 1, 4)
2. 1.1'e `tool_result` bloğu, `tool_use_id`, paralel tool çağrıları tek user mesajı kuralı (madde 2, 3)
3. 1.5'te `PreToolUse` adı + hook event tablosu + `PostToolUse` engelleyemez (madde 19, 20, 21)
4. 1.3/1.7'de `fork_session`'ın `resume` gerektirdiği (madde 12, 29)
5. 1.2'ye scope partitioning + dynamic selection anti-pattern'ı (madde 6, 8)

**Orta (derinlik):**
6. 1.3'e `Task`/`Agent` dipnotu, AgentDefinition alanları (`model`, `maxTurns`), nesting depth (madde 10, 11, 13)
7. 1.4'e iki uygulama kalıbı kod örneği + deny reason nüansı (madde 15, 16)
8. 1.6'ya Building Effective Agents pattern eşlemesi (madde 24)
9. 1.7'ye CLI/SDK seçenek tablosu + compaction (madde 28, 30)

**Düşük (kalite):**
10. Practice exam'e eksik soru tipleri, Q1/Q3/Q6 düzeltmeleri
11. 1.5 practice scenario'yu 4 şıklı formata çevirme
12. Mutlak ifadeleri yumuşatma ("tek güvenilir", "%100", "her zaman")

---

## Kaynaklar

- [Claude Certified Architect – Foundations Exam Guide (PDF)](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor/34hhd92iyp94a0gtbr15cy5jk/public/1782870727/Claude+Certified+Architect+-+Foundations+-+Exam+Guide.pdf)
- [Skilljar prep courses sayfası](https://anthropic-partners.skilljar.com/page/claude-certified-architect-foundations-prep-courses)
- [Claude Code in Action kursu](https://anthropic.skilljar.com/claude-code-in-action)
- [Handle stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons)
- [Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use)
- [Agent SDK — Subagents](https://code.claude.com/docs/en/agent-sdk/subagents)
- [Agent SDK — Hooks](https://code.claude.com/docs/en/agent-sdk/hooks)
- [Claude Code — Sessions](https://code.claude.com/docs/en/sessions)
- [Building Effective AI Agents](https://resources.anthropic.com/building-effective-ai-agents)
