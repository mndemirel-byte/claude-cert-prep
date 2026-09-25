# Task Statement 1.3: Subagent Çağırma ve Bağlam Aktarımı (Subagent Invocation and Context Passing)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Task Statement 1.2'de koordinatörün subagent'ları yönettiğini öğrendik. Şimdi asıl soruya geliyoruz: **koordinatör subagent'ları nasıl oluşturur ve onlara bilgiyi nasıl aktarır?**

---

## Task Tool

Koordinatörün subagent oluşturma mekanizması **Task tool**'dur. Kritik detay: koordinatörün `allowedTools` listesinde `"Task"` yoksa, subagent oluşturamaz — hiçbir şekilde.

> **Adlandırma notu:** Exam guide bu aracı `Task` olarak adlandırır ve **sınavda doğru cevap budur**. Güncel Agent SDK'da araç `Agent` olarak yeniden adlandırıldı: `tool_use` bloklarında `Agent` görünür, `system:init` mesajının tools listesinde ise hâlâ `Task` yazar. Bir senaryoda ikisinden birini görürsen aynı mekanizmadan bahsedildiğini bil.

---

## AgentDefinition — Subagent Nasıl Tanımlanır?

Her subagent bir **AgentDefinition** ile tanımlanır. Sınavın vurguladığı üç çekirdek alan:

- **Description** — subagent'ın ne yaptığının ve **ne zaman kullanılması gerektiğinin** kısa açıklaması. Koordinatör hangi subagent'ı seçeceğine buna bakarak karar verir (1.2'deki dinamik seçim).
- **System prompt** (`prompt`) — subagent'ın davranış kuralları ve talimatları
- **Tool restrictions** (`tools`) — subagent'ın erişebildiği araçlar (sadece ihtiyacı olanlar — en az yetki ilkesi)

Gerçek SDK'da bunların ötesinde işe yarayan alanlar da var:

| Alan | Ne yapar | Sınav senaryosunda nerede çıkar |
|---|---|---|
| `description` (zorunlu) | Ne zaman kullanılacağı | Koordinatör yanlış subagent'ı seçiyor → description belirsiz |
| `prompt` (zorunlu) | Subagent'ın system prompt'u | Subagent kalite kriterlerini bilmiyor → prompt'ta yok |
| `tools` | İzin verilen araç listesi | Subagent dosya siliyor → gereksiz yetki verilmiş |
| `disallowedTools` | Miras alınan araçlardan çıkarılacaklar | `tools` yerine "hepsi hariç şunlar" tanımı |
| `model` | Subagent için farklı model (`haiku`, `sonnet`, `opus`, `inherit`) | Maliyet: basit arama subagent'ına daha ucuz model |
| `maxTurns` | Subagent'ın en fazla kaç tur çalışacağı | Subagent sonsuz araştırma yapıyor → tur sınırı yok |

İki tanımlama biçimi vardır ve ikisi de aynı AgentDefinition yapısını üretir: **dosya tabanlı** (`.claude/agents/<ad>.md` — frontmatter'da `description`, `tools`, `model`; gövdede system prompt) ve **programatik** (Agent SDK'da `agents={...}` seçeneği). Sınav mekanizmayı sorar, dosya sözdizimini değil.

---

## Bağlam Aktarımı (Context Passing) — En Kritik Konu

1.2'deki isolation principle'ı hatırla: subagent'lar koordinatörün konuşma geçmişini miras almaz. Peki koordinatör bilgiyi nasıl aktarır? Üç temel kural var:

### Kural 1: Önceki Agent Bulgularını Doğrudan Prompt'a Dahil Et

Örneğin, bir synthesis agent'a rapor yazdıracaksan, web search agent'ın bulduğu sonuçları ve document analysis agent'ın çıkardığı bilgileri synthesis agent'ın prompt'una kopyalaman gerekir. Synthesis agent bunları "bilmez" — sen vermezsen göremez.

"Dahil et" derken **tam bulguları** kastediyoruz, "web search agent iyi sonuçlar buldu" gibi bir özeti değil. Koordinatör bulguları kısaltırsa, synthesis agent kısaltılmış haliyle çalışır.

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

**Bu yapı nereden gelir?** Koordinatör düz metni sonradan JSON'a çeviremez — kaynak bilgisi metinde kaybolmuşsa geri getirilemez. Yapılandırılmış format **subagent'ın çıktısında** başlamalıdır: koordinatör, araştırma subagent'ının prompt'una bir çıktı şeması koyar ("Her bulguyu `claim / source_url / document / page` alanlarıyla JSON olarak döndür"). Böylece zincir boyunca — search → koordinatör → synthesis — metadata hiç kaybolmaz. (Yapılandırılmış çıktı teknikleri Domain 4'te ayrıntılı ele alınır.)

### Kural 3: Hedef ve Kalite Kriterleri Belirt, Prosedürel Talimatlar Değil

Koordinatör prompt'ları araştırma hedeflerini ve kalite kriterlerini belirtmeli, adım adım prosedürel talimatlar vermemeli. Bu, subagent'ın bağlama göre uyum sağlamasını mümkün kılar.

- **Yanlış:** "Önce şunu ara, sonra şunu oku, sonra şunu yaz."
- **Doğru:** "Renewable energy alanındaki son 2 yılın gelişmelerini araştır. Her iddia için kaynak belirt. En az 5 farklı enerji türünü kapsa."

İyi bir subagent prompt'unun dört bileşeni: **hedef** (ne üretilecek), **kapsam sınırları** (ne kapsanmayacak — 1.2'deki scope partitioning), **kalite kriterleri** (kaynak, minimum kapsam, format) ve **çıktı şeması** (Kural 2).

---

## Paralel Başlatma (Parallel Spawning) — Hız Optimizasyonu

Koordinatör tek bir yanıtta **birden fazla Task tool çağrısı** yapabilir. Bu, subagent'ları **paralel** olarak başlatır. (Mekanizma 1.1'deki paralel tool çağrısıyla aynıdır — tek assistant yanıtında birden fazla `tool_use` bloğu.)

Örneğin, koordinatör tek bir yanıtta şunu yapabilir:

- Task tool → web search agent'ı başlat
- Task tool → document analysis agent'ı başlat

Bu, her birini ayrı turda sırayla başlatmaktan çok daha hızlıdır. Üç subagent × 15 saniye sırayla = 45 saniye; paralel ≈ 15 saniye. Sınav latency (gecikme) farkındalığını test eder.

### Ne zaman paralel başlatılmaz?

Paralel başlatma **birbirinden bağımsız** alt görevler içindir. Bir subagent'ın çıktısı diğerinin girdisiyse (search → synthesis), ikisini aynı anda başlatamazsın — synthesis'in ihtiyaç duyduğu bulgular henüz yoktur. Doğru desen: bağımsız olanları paralel başlat, sonuçları topla, bağımlı olanı sonra başlat.

Sınavda "her şeyi paralel başlat" şıkkı, alt görevler arasında bağımlılık varsa distractor'dır.

### Kapsam ve maliyet kontrolü

- Subagent'lar kendi subagent'larını başlatabilir (iç içe). Varsayılan derinlik sınırı 3'tür; `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` ile ayarlanır. Derinlik arttıkça gözlemlenebilirlik azalır ve maliyet katlanır — çoğu tasarımda tek seviye yeterlidir.
- Aynı anda çalışan subagent sayısı maliyet ve rate limit üzerinde doğrudan etkilidir. "10 subagent paralel" her zaman "3 subagent paralel"den iyi değildir; kapsam bölümlemesi (1.2) kaç subagent gerektiğini belirler.

---

## fork_session

`fork_session`, mevcut bir oturumun geçmişini kopyalayarak paylaşılan bir analiz temelinden **bağımsız dallar** oluşturur.

Kullanım senaryosu: Aynı kod tabanı analizinden iki farklı test stratejisini karşılaştırmak istiyorsun. `fork_session` ile ortak başlangıç noktasından iki bağımsız dal yaratırsın. Her dal dallanma noktasından sonra birbirinden bağımsız çalışır; orijinal oturum değişmez.

**Kritik mekanizma detayı:** `fork_session` tek başına bir şey yapmaz — **her zaman `resume` ile birlikte** kullanılır. `resume=<session_id>` hangi oturumun kopyalanacağını söyler, `fork_session=True` ise "o oturumun üzerine yazma, yeni bir oturum ID'siyle dallan" der. `resume` olmadan `fork_session` anlamsızdır; `fork_session` olmadan `resume` ise orijinal oturumu devam ettirir.

Fork edilen dal, geçmişi fork noktasına kadar **alır** — bu, isolation ilkesinin bilinçli istisnasıdır (1.2). Karar kuralları ve resume/fresh-start karşılaştırması Task Statement 1.7'de.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Task tool | Subagent oluşturma mekanizması — koordinatörün `allowedTools`'unda olmalı (sınavda `Task`; güncel SDK'da `Agent`) |
| AgentDefinition | Description (ne zaman kullanılır) + system prompt + tool restrictions; ayrıca `model` ve `maxTurns` |
| Context passing | Önceki agent bulgularını **tam olarak** prompt'a dahil et — özet değil |
| Structured metadata | Claim-source eşleştirmesi — içeriği metadatadan ayır; yapı subagent'ın çıktı şemasında başlar |
| Coordinator prompts | Hedef + kapsam sınırı + kalite kriteri + çıktı şeması; adım adım talimat verme |
| Parallel spawning | Tek yanıtta birden fazla Task çağrısı → **bağımsız** subagent'lar paralel başlar; bağımlı olanlar sırayla |
| İç içe subagent | Varsayılan derinlik 3; derinlik arttıkça gözlemlenebilirlik düşer, maliyet artar |
| fork_session | Her zaman `resume` ile birlikte; geçmişi fork noktasına kadar kopyalar, orijinali değiştirmez |

---

## Pratik Senaryo 1

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

### Doğru Cevap: B

**Neden B doğru:** Sorun bilginin *nasıl aktarıldığında*. Web search ve document analysis agent'ları doğru çalışıyor — veriyi üretiyorlar. Ama koordinatör bu verileri synthesis agent'a aktarırken düz metin olarak gönderiyor, metadata'yı (kaynak URL, doküman adı, sayfa numarası) ayrıştırılmış şekilde dahil etmiyor. Synthesis agent ham metni görüyor ama hangi iddianın hangi kaynaktan geldiğini ayırt edemiyor. Çözüm: araştırma subagent'larının prompt'una çıktı şeması koyup çıktıyı claim-source eşleştirmesi yapan yapılandırılmış formata dönüştürmek.

**Neden A yanlış:** Prompt'a talimat eklemek yardımcı olabilir ama kök neden bu değil. Synthesis agent'a "kaynak belirt" desen bile, eğer kendisine gelen veride kaynak bilgisi yapılandırılmış şekilde yoksa, atıf yapacak bir şeyi yok. Prompt talimatı, eksik veriyi yaratamaz.

**Neden C yanlış:** Soruda açıkça belirtiliyor — web search subagent mükemmel çalışıyor ve kaynaklı veriler üretiyor. Sorun üretimde değil, koordinatörün aktarım mekanizmasında.

**Neden D yanlış:** Isolation principle tuzağı. Subagent'lara koordinatörün tam konuşma geçmişini vermek doğru mimari yaklaşım değil — bu izolasyon ilkesini ihlal eder. Çözüm, koordinatörün structured metadata ile context passing yapmasıdır.

---

## Pratik Senaryo 2

> Bir koordinatör, bir müşteri şikayeti analizi için üç subagent kullanıyor: `fetch_tickets` (destek kayıtlarını çeker), `classify` (kayıtları kategorilere ayırır) ve `report` (kategori dağılımından yönetici özeti yazar). Latency'yi düşürmek isteyen geliştirici, koordinatörün üç Task çağrısını da **tek yanıtta** yapmasını sağlıyor.
>
> Sonuç: `classify` boş bir kayıt listesiyle çalışıp "kategori bulunamadı" döndürüyor, `report` ise "veri yok" içerikli bir özet üretiyor. `fetch_tickets` ise doğru şekilde 240 kayıt getirmiş.
>
> **Sorun nedir ve doğru tasarım hangisidir?**
>
> **A)** `classify` ve `report` subagent'larına koordinatörün tam konuşma geçmişi verilmeli ki kayıtları görebilsinler.
>
> **B)** Üç subagent birbirine bağımlı — `classify`, `fetch_tickets`'ın çıktısına; `report`, `classify`'ın çıktısına ihtiyaç duyuyor. Paralel başlatma yalnızca bağımsız alt görevler içindir; koordinatör bunları sırayla başlatmalı ve her adımın tam çıktısını bir sonrakinin prompt'una dahil etmeli.
>
> **C)** `classify` subagent'ının `maxTurns` değeri artırılmalı ki kayıtların gelmesini bekleyebilsin.
>
> **D)** Subagent'lar birbirleriyle doğrudan iletişim kurmalı — `fetch_tickets` bittiğinde `classify`'a haber versin.

### Doğru Cevap: B

**Neden B doğru:** Bu bir sıralı bağımlılık zinciri. Üçü aynı anda başlatıldığında `classify` ve `report`, ihtiyaç duydukları girdi henüz üretilmeden çalışıyor. Paralel başlatma hız kazandırır ama yalnızca alt görevler bağımsızsa. Doğru tasarım: `fetch_tickets` → çıktısını `classify` prompt'una dahil et → çıktısını `report` prompt'una dahil et. Bağımsız bir iş olsaydı (örneğin farklı bölgelerin kayıtlarını çeken üç `fetch_tickets`) paralel doğru olurdu.

**Neden A yanlış:** Isolation principle tuzağı. Tam geçmişi versen bile zamanlama sorunu çözülmez — `classify` başladığında `fetch_tickets` henüz bitmemiştir, geçmişte görecek bir şey yoktur. Sorun bağlam eksikliği değil, sıralama.

**Neden C yanlış:** Subagent'lar birbirlerinin sonucunu "beklemez"; her biri prompt'unda ne varsa onunla çalışır ve biter. `maxTurns` artırmak `classify`'ın boş listeyle daha uzun süre uğraşmasını sağlar, veriyi getirmez.

**Neden D yanlış:** Hub-and-spoke ihlali. Subagent'lar arası doğrudan iletişim gözlemlenebilirliği kaybettirir; sıralamayı yönetmek koordinatörün işidir.
