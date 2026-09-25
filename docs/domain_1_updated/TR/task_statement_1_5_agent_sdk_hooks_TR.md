# Task Statement 1.5: Agent SDK Hook'ları (Agent SDK Hooks)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Task Statement 1.4'te programatik zorlamanın neden gerekli olduğunu öğrendik. Şimdi Agent SDK ve Claude Code'da bunun **nasıl** uygulandığını öğreniyoruz. Cevap: **hook'lar**.

Hook'lar, agent'ın yaşam döngüsündeki belirli olaylarda (event) otomatik olarak çalışan kod parçalarıdır. Model ne "düşünürse düşünsün" hook çalışır — bu yüzden deterministiktir. Sınavın odaklandığı iki hook, tool çağrısının **öncesine** ve **sonrasına** yerleşenlerdir.

---

## PreToolUse Hook'ları (Tool Çağrılmadan Önce)

Claude bir tool çağırmaya karar verdiğinde, tool **çalışmadan önce** araya girer.

**Kullanım amacı: İş kurallarını zorlamak (policy enforcement).**

Örnekler:

- $500 üzerindeki iadeleri engelle ve insan escalation workflow'una yönlendir
- Uluslararası transferlerde compliance kontrolü olmadan işlem yapılmasını engelle
- Belirli operasyonlar için yönetici onayı gerektir
- Ön koşul gate'i: `verify_identity` tamamlanmadan `process_refund`'u engelle (1.4'teki Kalıp 2)

Hook'un döndürebileceği kararlar:

| Çıktı | Etkisi |
|---|---|
| `permissionDecision: "allow"` | Tool çalışır (izin sistemini atlayarak) |
| `permissionDecision: "deny"` | Tool **çalışmaz**; `permissionDecisionReason` Claude'a iletilir |
| `permissionDecision: "ask"` | Kullanıcıdan onay istenir |
| `updatedInput` | Tool'un girdisi değiştirilerek çalıştırılır (ör. dosya yolunu sandbox'a yönlendirme, PII'yi maskeleme) |

`permissionDecisionReason` süs değildir: 1.4'te gördüğümüz gibi, red nedeni Claude'a ulaşmazsa agent kendini düzeltemez. Her `deny` bir "önce ne yapılmalı" mesajı taşımalıdır.

Exam guide bu hook'u "tool call interception" olarak adlandırır — sınavda her iki ifadeyi de görebilirsin; teknik adı **`PreToolUse`**'dur.

---

## PostToolUse Hook'ları (Tool Çalıştıktan Sonra)

Tool çalıştıktan **sonra**, sonuç Claude'a gitmeden **önce** araya girer.

**Kullanım amacı: Veri normalizasyonu ve zenginleştirme.**

Farklı MCP tool'ları farklı formatlarla veri döndürür — biri Unix timestamp verir, diğeri ISO 8601. Biri sayısal status code döndürür, diğeri string. PostToolUse hook tüm bu farklı formatları standart bir formata dönüştürür. Sonuç: Claude her zaman temiz, tutarlı veri görür — hangi tool'un ürettiği fark etmez.

Hook'un döndürebileceği çıktılar:

| Çıktı | Etkisi |
|---|---|
| `updatedToolOutput` | Claude'un göreceği tool sonucunu **değiştirir** — normalizasyon tam olarak burada yapılır |
| `additionalContext` | Sonucu değiştirmeden Claude'a ek bağlam ekler (ör. "bu tarihler UTC'dir") |

### Sınav tuzağı: PostToolUse engelleyemez

PostToolUse çalıştığında **tool zaten çalışmıştır**. İade zaten yapılmış, transfer zaten gönderilmiştir. Bu hook sonucu dönüştürebilir, loglayabilir, Claude'a not düşebilir — ama işlemi geri alamaz ya da engelleyemez. "PostToolUse ile riskli işlemi engelle" şıkkı her zaman yanlıştır; engelleme **PreToolUse**'un işidir.

---

## Diğer Hook Event'leri

Sınavın çekirdeği Pre/PostToolUse olsa da, "şu iş için hangi hook?" tarzı sorular için tam listeyi tanımalısın:

| Event | Ne zaman çalışır | Tipik kullanım |
|---|---|---|
| `PreToolUse` | Tool çağrısı öncesi | Policy enforcement, ön koşul gate'i, girdi düzeltme |
| `PostToolUse` | Tool başarıyla çalıştıktan sonra | Normalizasyon, zenginleştirme, audit log |
| `PostToolUseFailure` | Tool hata verdiğinde | Hata loglama, alarm |
| `UserPromptSubmit` | Kullanıcı prompt gönderdiğinde, Claude'a ulaşmadan önce | Prompt'a bağlam ekleme, yasaklı içeriği engelleme |
| `Stop` | Ana agent turunu bitirdiğinde | "Testler geçmeden bitirme" kontrolü, çıktı doğrulama |
| `SubagentStart` / `SubagentStop` | Subagent başlarken / biterken | Subagent çıktısını loglama, maliyet takibi |
| `PreCompact` | Context sıkıştırılmadan önce | Kritik bilgiyi sıkıştırma öncesi kaydetme |
| `SessionStart` / `SessionEnd` | Oturum başlarken / biterken | Ortam kurulumu, oturum sonu raporu |
| `PermissionRequest` | Bir tool izin gerektirdiğinde | Programatik izin kararı |
| `Notification` | Sistem bildirimi üretildiğinde | Dış sistemlere bildirim iletme |

---

## Hook'lar Nasıl Tanımlanır?

İki biçim vardır; ikisi de aynı event modelini kullanır.

**Claude Code — `settings.json`:** Hook bir shell komutudur. Event verisi stdin'den JSON olarak gelir. Karar iki yolla verilir: **exit code** (0 = devam, **2 = engelle**; stderr'deki mesaj Claude'a iletilir) ya da stdout'a yazılan JSON (`hookSpecificOutput` ile yukarıdaki alanlar).

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python3 .claude/hooks/guard.py" }]
      }
    ]
  }
}
```

**Agent SDK — programatik callback:** Hook bir fonksiyondur; event verisini alır, yukarıdaki çıktı yapısını döndürür.

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="process_refund", hooks=[refund_gate])],
        "PostToolUse": [HookMatcher(matcher="mcp__crm__.*", hooks=[normalize_dates])],
    }
)
```

**Matcher** kavramı önemli: hook'un hangi tool'lara uygulanacağını belirler (tool adı ya da regex). Matcher yoksa hook her tool çağrısında çalışır — gereksiz latency ve yanlışlıkla engelleme riski. Sınavda "hook tüm tool'ları yavaşlatıyor" senaryosunun cevabı matcher'ı daraltmaktır.

---

## Karar Çerçevesi

| Yaklaşım | Garanti | Kullanım Alanı |
|---|---|---|
| **Tool'u hiç vermemek** (`allowedTools` / `disallowedTools`, permission modes) | Deterministik | Agent'ın o işlemi **hiç** yapmaması gerekiyorsa — en basit çözüm |
| **Hook'lar** | Deterministik | İşlem yapılabilir ama **koşula bağlı** — iş kuralları, compliance, ön koşul, normalizasyon |
| **Prompt'lar** | Olasılıksal | Tercihler, stil kuralları, yumuşak rehberlik |

> **Tek bir başarısızlık para kaybı veya yasal risk yaratıyorsa → hook (ya da tool'u hiç verme).**

Sınav nüansı: hook her zaman en iyi cevap değildir. Agent'ın bir tool'u hiçbir koşulda çağırmaması gerekiyorsa, hook yazmak yerine tool'u `allowedTools`'tan çıkarmak daha basit ve daha güvenlidir. Hook, "bazen evet, bazen hayır" koşullu kurallar içindir.

---

## Sınav İçin Temel Çıkarımlar

| Concept | Remember |
|---|---|
| `PreToolUse` | Tool çalışmadan önce — `allow` / `deny` / `ask` / `updatedInput`; engelleme buradadır |
| `PostToolUse` | Tool çalıştıktan sonra — `updatedToolOutput` ile normalizasyon, `additionalContext` ile zenginleştirme; **engelleyemez** |
| `permissionDecisionReason` | Her `deny` ile birlikte — agent'ın kendini düzeltmesi için |
| Diğer event'ler | `Stop` (bitirme kontrolü), `SubagentStop` (subagent loglama), `PreCompact`, `UserPromptSubmit`, `PostToolUseFailure` |
| Tanımlama | `settings.json` (shell, exit code 2 = engelle) veya SDK callback; **matcher** ile kapsam daralt |
| Hook = deterministik | İş kuralları, compliance, finansal kontroller |
| Prompt = olasılıksal | Tercihler ve yumuşak kurallar için yeterli |
| En basit deterministik çözüm | Tool hiç gerekmiyorsa `allowedTools`'tan çıkar — hook yazma |

---

## Pratik Senaryo 1

> Bir agent zaman zaman uluslararası transferleri gerekli compliance kontrolleri (`compliance_check` tool'u) yapmadan `send_transfer` tool'uyla işliyor. Bu düzenleyici (regulatory) risk yaratıyor.
>
> **Doğru çözüm hangisidir?**
>
> **A)** System prompt'a "uluslararası transferden önce mutlaka compliance_check çağır" talimatını ekle ve 3 örnek konuşmayla pekiştir.
>
> **B)** `send_transfer` için bir `PostToolUse` hook'u ekle; transfer uluslararasıysa ve compliance kontrolü yapılmamışsa işlemi engellesin.
>
> **C)** `send_transfer` için bir `PreToolUse` hook'u ekle; transfer uluslararasıysa ve `compliance_check` başarıyla tamamlanmamışsa `permissionDecision: "deny"` ve "önce compliance_check çağır" nedeniyle çağrıyı engellesin.
>
> **D)** `send_transfer` tool'unu `allowedTools`'tan çıkar; tüm transferleri insan yapsın.

### Doğru Cevap: C

**Neden C doğru:** Regulatory risk = tek bir başarısızlık yasal sonuç doğurur; deterministik garanti şart. `PreToolUse` hook'u transfer **gerçekleşmeden önce** araya girer, koşulu kontrol eder ve sağlanmamışsa çağrıyı engeller. Red nedeni Claude'a iletildiği için agent compliance kontrolünü çağırıp ardından transferi doğru sırayla tamamlar.

**Neden A yanlış:** Prompt talimatları ve few-shot örnekler olasılıksaldır — başarı oranını artırır (örneğin %92'den %97'ye) ama %100 garanti edemez. Tek bir kontrolsüz transfer bile ceza riski taşır.

**Neden B yanlış:** `PostToolUse` tool çalıştıktan **sonra** çalışır — transfer çoktan gönderilmiştir. Bu hook sonucu dönüştürebilir ya da loglayabilir ama işlemi engelleyemez. Klasik sınav tuzağı.

**Neden D yanlış:** Tool'u tamamen kaldırmak deterministiktir ama orantısızdır — uluslararası olmayan ya da compliance kontrolü geçmiş transferler de engellenir. Kural koşulludur ("kontrol yapılmadıysa engelle"), bu da hook'un tam kullanım alanıdır.

---

## Pratik Senaryo 2

> Bir kod inceleme agent'ı, üç MCP server'ından (GitHub, Jira, CI sistemi) veri çekiyor. Her biri zaman damgalarını farklı formatta döndürüyor (Unix epoch, ISO 8601, "2 hours ago"). Agent "en son değişiklik hangisi?" sorularında tutarsız cevaplar veriyor.
>
> Ekip bir `PostToolUse` hook'u ekliyor ama hook yalnızca `additionalContext` ile "tarihler farklı formatlarda olabilir, dikkat et" notu döndürüyor. Tutarsızlık devam ediyor.
>
> **En etkili düzeltme hangisidir?**
>
> **A)** Hook'u `PreToolUse`'a taşı ve tool girdilerine "ISO 8601 döndür" parametresi ekle.
>
> **B)** Hook, `additionalContext` yerine `updatedToolOutput` ile tüm zaman damgalarını ISO 8601'e dönüştürmeli — Claude'a "dikkat et" demek yerine veriyi düzelt.
>
> **C)** Üç MCP server'ının kaynak kodunu değiştirip aynı formatı döndürmelerini sağla.
>
> **D)** System prompt'a tarih formatlarını açıklayan bir referans tablosu ekle.

### Doğru Cevap: B

**Neden B doğru:** `additionalContext` Claude'a bilgi verir ama dönüşümü yine modele bırakır — bu olasılıksal bir çözümdür ve hook'un deterministik gücünü boşa harcar. `updatedToolOutput` tool sonucunu Claude'a ulaşmadan **değiştirir**: her zaman damgası kodla ISO 8601'e çevrilir, Claude yalnızca tutarlı veri görür. Normalizasyon bir kod işidir, model işi değil.

**Neden A yanlış:** `PreToolUse` girdiyi değiştirir, çıktıyı değil. Üçüncü parti MCP tool'larının "ISO 8601 döndür" gibi bir parametresi olduğu varsayılamaz; çıktı formatı senin kontrolünde değil, ama çıktıyı dönüştürmek senin kontrolünde.

**Neden C yanlış:** Üçüncü parti server'ları değiştirmek genellikle mümkün değil; mümkün olsa bile kontrolü dış bağımlılığa bırakır. Normalizasyon senin sınırında olmalı.

**Neden D yanlış:** Prompt tabanlı yönlendirme — olasılıksal. Zaten `additionalContext` ile denenen yaklaşımın bir başka biçimi ve aynı nedenle yetersiz.
