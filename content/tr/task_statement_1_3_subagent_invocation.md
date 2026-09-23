# Task Statement 1.3: Subagent Invocation and Context Passing

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

Task Statement 1.2'de koordinatörün subagent'ları yönettiğini öğrendik. Şimdi asıl soruya geliyoruz: **koordinatör subagent'ları nasıl oluşturur ve onlara bilgiyi nasıl aktarır?**

---

## The Task Tool

Koordinatörün subagent oluşturma mekanizması **Task tool**'dur. Kritik detay: koordinatörün `allowedTools` listesinde `"Task"` yoksa, subagent oluşturamaz — hiçbir şekilde.

Her subagent bir **AgentDefinition** ile tanımlanır. Bu tanım üç şey içerir:

- **Description** — subagent'ın ne yaptığının kısa açıklaması
- **System prompt** — subagent'ın davranış kuralları ve talimatları
- **Tool restrictions** — subagent'ın erişebildiği araçlar (sadece ihtiyacı olanlar)

---

## Context Passing — En Kritik Konu

1.2'deki isolation principle'ı hatırla: subagent'lar hiçbir şeyi otomatik olarak miras almaz. Peki koordinatör bilgiyi nasıl aktarır? Üç temel kural var:

### Kural 1: Önceki Agent Bulgularını Doğrudan Prompt'a Dahil Et

Örneğin, bir synthesis agent'a rapor yazdıracaksan, web search agent'ın bulduğu sonuçları ve document analysis agent'ın çıkardığı bilgileri synthesis agent'ın prompt'una kopyalaman gerekir. Synthesis agent bunları "bilmez" — sen vermezsen göremez.

### Kural 2: Yapılandırılmış Veri Formatları Kullan — İçeriği Metadatadan Ayır

Bu çok önemli ve sınavda sıkça test ediliyor. Subagent'lara bilgi aktarırken sadece ham metin göndermek yetmez. Kaynak URL'lerini, doküman adlarını, sayfa numaralarını içerikten ayrı olarak yapılandırılmış formatta göndermelisin. Böylece attribution (kaynak atıfı) agent'lar arasında korunur.

Kötü örnek:
```
"The global solar market grew 25% in 2024 according to some reports."
```

İyi örnek:
```json
{
  "claim": "The global solar market grew 25% in 2024",
  "source_url": "https://iea.org/reports/solar-2024",
  "document": "IEA Solar Market Report 2024",
  "page": 12
}
```

### Kural 3: Hedef ve Kalite Kriterleri Belirt, Prosedürel Talimatlar Değil

Koordinatör prompt'ları araştırma hedeflerini ve kalite kriterlerini belirtmeli, adım adım prosedürel talimatlar vermemeli. Bu, subagent'ın bağlama göre uyum sağlamasını mümkün kılar.

- **Yanlış:** "Önce şunu ara, sonra şunu oku, sonra şunu yaz."
- **Doğru:** "Renewable energy alanındaki son 2 yılın gelişmelerini araştır. Her iddia için kaynak belirt. En az 5 farklı enerji türünü kapsa."

---

## Parallel Spawning — Hız Optimizasyonu

Koordinatör tek bir yanıtta **birden fazla Task tool çağrısı** yapabilir. Bu, subagent'ları **paralel** olarak başlatır.

Örneğin, koordinatör tek bir yanıtta şunu yapabilir:

- Task tool → web search agent'ı başlat
- Task tool → document analysis agent'ı başlat

Bu, her birini ayrı turda sırayla başlatmaktan çok daha hızlıdır. Sınav latency (gecikme) farkındalığını test eder — paralel başlatma her zaman tercih edilen yaklaşımdır.

---

## fork_session

`fork_session` paylaşılan bir analiz temelinden **bağımsız dallar** oluşturur.

Kullanım senaryosu: Aynı kod tabanı analizinden iki farklı test stratejisini karşılaştırmak istiyorsun. `fork_session` ile ortak başlangıç noktasından iki bağımsız dal yaratırsın. Her dal dallanma noktasından sonra birbirinden bağımsız çalışır.

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Task tool | Subagent oluşturma mekanizması — koordinatörün `allowedTools`'unda olmalı |
| AgentDefinition | Description + system prompt + tool restrictions |
| Context passing | Önceki agent bulgularını doğrudan prompt'a dahil et, structured metadata ile |
| Structured metadata | Claim-source eşleştirmesi — içeriği metadatadan ayır (URL, doküman adı, sayfa no) |
| Coordinator prompts | Hedef ve kalite kriterleri belirt, adım adım talimat verme |
| Parallel spawning | Tek yanıtta birden fazla Task tool çağrısı → subagent'lar paralel başlar → daha hızlı |
| fork_session | Paylaşılan analiz temelinden bağımsız dallar oluşturur |

---

## Practice Scenario

> Bir multi-agent research sistemi var. Web search subagent ve document analysis subagent mükemmel çalışıyor — her ikisi de zengin, kaynaklı veriler üretiyor. Ancak synthesis subagent'ın ürettiği nihai raporda birçok iddia **kaynak atıfsız** — hangi bilginin nereden geldiği belli değil.
>
> **Kök neden nedir ve nasıl düzeltilir?**
>
> **A)** Synthesis subagent'ın system prompt'u kaynak atıfı istemiyor — prompt'a "her iddia için kaynak belirt" talimatı eklenmeli.
>
> **B)** Koordinatörün context passing mekanizması yapılandırılmış metadata içermiyor — subagent'ların çıktısı claim-source eşleştirmesi yapan structured format'a dönüştürülmeli.
>
> **C)** Web search subagent kaynak URL'lerini döndürmüyor — arama sonuçlarına URL eklenmeli.
>
> **D)** Synthesis subagent'a koordinatörün tam konuşma geçmişi verilmeli ki kaynakları görebilsin.

### Correct Answer: B

**Why B is correct:** Sorun bilginin *nasıl aktarıldığında*. Web search ve document analysis agent'ları doğru çalışıyor — veriyi üretiyorlar. Ama koordinatör bu verileri synthesis agent'a aktarırken düz metin olarak gönderiyor, metadata'yı (kaynak URL, doküman adı, sayfa numarası) ayrıştırılmış şekilde dahil etmiyor. Synthesis agent ham metni görüyor ama hangi iddianın hangi kaynaktan geldiğini ayırt edemiyor. Çözüm: subagent'ların çıktısını claim-source eşleştirmesi yapan yapılandırılmış formata dönüştürmek.

**Why A is wrong:** Prompt'a talimat eklemek yardımcı olabilir ama kök neden bu değil. Synthesis agent'a "kaynak belirt" desen bile, eğer kendisine gelen veride kaynak bilgisi yapılandırılmış şekilde yoksa, atıf yapacak bir şeyi yok. Prompt talimatı, eksik veriyi yaratamaz.

**Why C is wrong:** Soruda açıkça belirtiliyor — web search subagent mükemmel çalışıyor ve zengin veriler üretiyor. Sorun üretimde değil, koordinatörün aktarım mekanizmasında.

**Why D is wrong:** Isolation principle tuzağı. Subagent'lara koordinatörün tam konuşma geçmişini vermek doğru mimari yaklaşım değil — bu izolasyon ilkesini ihlal eder. Çözüm, koordinatörün structured metadata ile context passing yapmasıdır.
