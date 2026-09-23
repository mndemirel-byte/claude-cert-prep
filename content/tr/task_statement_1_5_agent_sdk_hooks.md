# Task Statement 1.5: Agent SDK Hooks

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

Task Statement 1.4'te programmatic enforcement'ın neden gerekli olduğunu öğrendik. Şimdi **nasıl** uygulandığını öğreniyoruz. Cevap: **hooks**.

Hook'lar, tool çağrılarının **önüne** veya **sonrasına** yerleştirdiğin kod parçaları. İki ana türü var:

---

## PostToolUse Hooks (Tool Çalıştıktan Sonra)

Tool çalıştıktan **sonra**, sonuç Claude'a gitmeden **önce** araya girer.

**Kullanım amacı: Veri normalizasyonu.**

Farklı MCP tool'ları farklı formatlarla veri döndürür — biri Unix timestamp verir, diğeri ISO 8601. Biri sayısal status code döndürür, diğeri string. PostToolUse hook tüm bu farklı formatları standart bir formata dönüştürür.

Sonuç: Claude her zaman temiz, tutarlı veri görür — hangi tool'un ürettiği farketmez.

---

## Tool Call Interception Hooks (Tool Çağrılmadan Önce)

Tool çağrılmadan **önce** araya girer.

**Kullanım amacı: İş kurallarını zorlamak.**

Örnekler:

- $500 üzerindeki iadeleri engelle ve insan escalation workflow'una yönlendir
- Uluslararası transferlerde compliance kontrolü olmadan işlem yapılmasını engelle
- Belirli operasyonlar için yönetici onayı gerektir

---

## Karar Çerçevesi

| Yaklaşım | Garanti | Kullanım Alanı |
|---|---|---|
| **Hooks** | Deterministik — %100 çalışır | İş kuralları, compliance, finansal kontroller |
| **Prompts** | Olasılıksal — çoğu zaman çalışır | Tercihler, stil kuralları, yumuşak rehberlik |

> **Tek bir başarısızlık para kaybı veya yasal risk yaratıyorsa → hook kullan.**

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| PostToolUse hooks | Tool sonuçlarını Claude'a göndermeden önce yakalar — veri normalizasyonu için |
| Tool call interception | Tool çağrılmadan önce yakalar — iş kurallarını zorlamak için |
| Hook = deterministik | %100 garanti — business rules, compliance, finansal kontroller |
| Prompt = olasılıksal | Çoğu zaman çalışır — tercihler ve yumuşak kurallar için yeterli |
| Decision rule | Tek bir hata para kaybı veya yasal risk yaratıyorsa → her zaman hook |

---

## Practice Scenario

> Bir agent zaman zaman uluslararası transferleri gerekli compliance kontrolleri yapmadan işliyor. Bu düzenleyici (regulatory) risk yaratıyor.
>
> **Çözüm: hook mu, yoksa geliştirilmiş prompt talimatları mı? Neden?**

### Correct Answer: Hook

**Açıklama:** Regulatory risk = tek bir başarısızlık yasal sonuç doğurur. Prompt talimatları başarı oranını artırabilir (örneğin %92'den %97'ye) ama %100 garanti edemez. Tool call interception hook, compliance kontrolü tamamlanmadan transfer tool'unun çalışmasını fiziksel olarak engeller. Sıfır hata oranı.

**Neden prompt yetmez:** Uluslararası transferler finansal düzenlemeye tabidir. Tek bir kontrolsüz transfer bile ceza veya yasal soruşturma riskini taşır. Olasılıksal bir çözüm bu risk seviyesi için kabul edilemez. Deterministik garanti şarttır.
