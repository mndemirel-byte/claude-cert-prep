# Task Statement 2.3: Araç Dağılımı ve tool_choice (Tool Distribution & tool_choice)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Bir agent'a kaç araç verirsin? Hepsini mi, yoksa sadece ihtiyacı olanları mı? Ve model araç çağırıp çağırmayacağına kendisi mi karar vermeli, yoksa sen mi dayatmalısın? Bu task statement tam olarak bu iki soruyu cevaplıyor.

---

## Araç Aşırı Yüklemesi Problemi (Tool Overload)

Bir agent'a 18 araç verirsen, seçim güvenilirliği düşer. Her ek araç karar karmaşıklığını artırır; Claude hangi aracı ne zaman kullanacağına karar vermekte zorlanır. Anthropic'in kendi ölçümü: 30–50 aracın üzerinde seçim doğruluğu belirgin düşer; tipik çok-sunuculu bir MCP kurulumu (GitHub + Slack + Sentry + Grafana + Splunk) daha iş başlamadan ~55k token araç tanımı yükler.

**Optimal:** Agent başına **4–5 araç**, rolüne göre kapsamlandırılmış.

Temel kural: **Her agent sadece kendi rolü için gereken araçlara sahip olmalı.**

- Sentez agent'ının web arama araçları olmamalı — rol dışı araçlar **kötüye kullanılır** (sentez agent'ı sentez yapmak yerine arama yapmaya başlar)
- Web arama agent'ının doküman analiz araçları olmamalı
- Her agent kendi işine odaklı araç setine sahip olmalı

Resmi terim: **principle of least privilege** (en az yetki ilkesi) — her agent'a işini yapmaya yetecek en dar araç seti.

### Claude Code / Agent SDK'da nasıl uygulanır?

Araç dağılımı soyut bir ilke değil; subagent tanımının bir alanıdır:

```markdown
---
name: synthesis-agent
description: Bulguları tek bir rapora dönüştürür
tools: Read, Write, verify_fact
---
```

- `.claude/agents/*.md` frontmatter'ında `tools` (izin listesi) veya `disallowedTools` (kara liste)
- Agent SDK'da `AgentDefinition.tools` / `disallowedTools`
- MCP araçları `mcp__<server>__<tool>` adıyla listelenir (`mcp__github__create_issue`)
- `tools` verilmezse subagent koordinatörün tüm araçlarını miras alır — **varsayılan "hepsi", bilinçli olarak daralt**

(Bkz. Domain 1.3 — Subagent Invocation.)

### Güncel not (sınav cevabını değiştirmez)

Anthropic, çok araç problemine API seviyesinde bir çözüm de sundu: **Tool Search Tool**. Araçlar `defer_loading: true` ile işaretlenir, Claude `tool_search_tool_regex` / `tool_search_tool_bm25` ile ihtiyaç duyduğu 3–5 aracı arayıp yükler; context'teki araç tanımı yükü %85+ düşer. Öneri eşiği: 10+ araç veya 10k+ token araç tanımı. Exam guide'da yok; **sınav cevabı hâlâ "rol bazlı dağıt, agent başına 4–5"** — bu not, "18 → 4–5" sayısının nereden geldiğini anlamlandırmak için.

---

## tool_choice Konfigürasyonu

**Dört** değer var — sınav bunları birbirinden ayırt etmeni bekliyor:

### 1. `"auto"` (tools verildiğinde varsayılan)
Model araç çağırıp çağırmamaya **kendisi** karar verir. Araç çağırmak yerine doğrudan metin yanıt da verebilir.

**Ne zaman kullanılır:** Genel operasyon. Çoğu durumda bu mod yeterli.

### 2. `"any"`
Model **mutlaka** bir araç çağırmalı ama hangisini çağıracağına kendisi karar verir. Konuşma metni döndüremez.

**Ne zaman kullanılır:** Birden fazla şemadan birinden **garantili yapılandırılmış çıktı** istediğinde — "model bana metin değil, şu üç JSON şemasından biriyle cevap versin."

### 3. `{"type": "tool", "name": "extract_metadata"}`
Model **mutlaka** bu belirli aracı çağırmalı. Seçim şansı yok.

**Ne zaman kullanılır:** Zorunlu ilk adımları dayatmak için. Örneğin, zenginleştirme (enrichment) adımlarından önce metadata çıkarımını zorunlu kılmak.

### 4. `"none"` (tools verilmediğinde varsayılan)
Model **hiçbir** araç çağıramaz; yalnızca metin üretir. Araçlar tanımlı kalır ama bu turda kapalıdır.

**Ne zaman kullanılır:** Araç tanımlarını her istekte göndermeye devam ederken (prompt cache'i bozmamak için) belirli bir turda yalnızca metin istediğinde — örn. son özet turu, "kullanıcıya açıklama yaz" adımı.

### Özet Tablo

| Değer | Davranış | Kullanım alanı | Sınav ipucu |
|---|---|---|---|
| `"auto"` | Model karar verir — araç veya metin | Genel operasyon | Varsayılan; "modelin karar vermesi sorun değil" |
| `"any"` | Mutlaka araç çağırır, hangisini seçer | Garantili yapılandırılmış çıktı | "Metin yanıt istemiyorum, şemalardan biri olsun" |
| `{"type":"tool","name":"X"}` | Mutlaka belirtilen aracı çağırır | Zorunlu ilk adım | "İlk turda forced, **sonraki turlarda `auto`**" |
| `"none"` | Hiç araç çağırmaz | Yalnızca metin turu | "Araçlar tanımlı ama bu turda kapalı" |

### Forced seçimden sonra `auto`'ya dönmek — SINAV TUZAĞI

Exam guide'ın Skills maddesi tam olarak şöyle: *"Using tool_choice forced selection to ensure a specific tool is called **first, then processing subsequent steps in follow-up turns**."*

`tool_choice` **istek bazında** çalışır. `{"type":"tool","name":"extract_metadata"}` ile ilk isteği gönderirsin, model `extract_metadata`'yı çağırır, sonucu `tool_result` olarak eklersin. **İkinci istekte `tool_choice`'u `auto`'ya çevirmezsen**, model yine `extract_metadata`'yı çağırmaya zorlanır — enrichment adımlarına hiç geçemez, sonsuz metadata döngüsüne girer.

```python
# Tur 1: zorunlu ilk adım
r1 = client.messages.create(..., tools=tools,
        tool_choice={"type": "tool", "name": "extract_metadata"})
messages += [assistant(r1.content), user(tool_results(r1))]

# Tur 2+: modele serbestlik ver
r2 = client.messages.create(..., tools=tools, tool_choice={"type": "auto"})
```

Sınav senaryosu: "Zorunlu metadata adımı eklendi, ama agent artık analize hiç geçmiyor, sürekli metadata çıkarıyor." → Cevap: forced `tool_choice` sonraki turlarda `auto`'ya döndürülmemiş.

### Ek nüanslar

- **`disable_parallel_tool_use: true`** — `auto` altında Claude tek yanıtta birden fazla `tool_use` bloğu döndürebilir. Bu bayrak yanıtı en fazla bir araç çağrısıyla sınırlar; `any`/`tool` ile birlikte kullanıldığında **tam olarak bir** araç çağrısı garanti eder. "Zorunlu ilk adım" kalıbının doğal parçası. (Bkz. Domain 1.1 — paralel tool çağrıları.)
- **`any`/`tool` ile düşünme:** Zorunlu araç seçiminde assistant mesajı prefill edilir; model tool_use öncesinde düşünme/metin bloğu üretmez. Manuel extended thinking (`thinking: {"type": "enabled"}`) ile `any`/`tool` **birlikte kullanılamaz** — API hata döndürür. Thinking gerekiyorsa `auto` kullan.
- **Güncel not (sınav cevabını değiştirmez):** En yeni modellerde (Opus 5.5, Fable 5.1, Mythos 5.1) `any` ve `tool` desteklenmiyor (400 hatası); alternatif `auto` + strict tool use ya da structured outputs. **Sınav guide'ı `auto` / `any` / forced'ı geçerli sayıyor; sınavda bunlar doğru cevaptır.**

---

## Kapsamlı Çapraz Rol Araçları (Scoped Cross-Role Tools) — SINAV SORUSU

Bu kalıp exam guide'ın resmi örnek sorusudur (Q9). Senaryoyu, çözümü **ve tüm distractor'ları** iyi öğren.

### Problem

Bir sentez agent'ı sık sık basit doğrulama (fact verification) için koordinatöre kontrolü geri veriyor; koordinatör web search agent'ı çağırıyor, sonuç geri dönüyor, sentez yeniden başlıyor. Her seferinde 2–3 ek tur-dönüş (round-trip) oluyor ve toplam gecikme **%40** artıyor. Doğrulamaların **%85'i** basit arama (tarih, isim, istatistik); **%15'i** derin araştırma gerektiriyor.

### Çözüm: Kapsamlandırılmış verify_fact Aracı

Sentez agent'a **kapsamlandırılmış bir `verify_fact` aracı** ver — sadece basit aramalar yapabilir. Karmaşık doğrulamalar hâlâ koordinatör üzerinden web search agent'a gider.

**Sonuç:**
- Vakaların %85'inde koordinatör tur-dönüş gecikmesi ortadan kalkar
- Kalan %15 karmaşık doğrulama hâlâ koordinatör üzerinden akar — mimari bütünlük korunur
- Resmi gerekçe: **principle of least privilege** — sentez agent'a %85'lik yaygın vaka için *gereken kadar* yetki, fazlası değil

### Neden Diğer Çözümler Yanlış? (Q9'un gerçek distractor'ları dahil)

| Çözüm | Neden Yanlış |
|---|---|
| **Doğrulamaları biriktir, sentez sonunda toplu olarak koordinatöre gönder** (Q9 şık B) | Gecikmeyi *toplar* ama ortadan kaldırmaz — en az bir ek tur-dönüş kalır. Daha kötüsü: sentez agent doğrulanmamış iddialarla yazmaya devam eder, sonra geri dönüp düzeltmek zorunda kalır; hatalı iddia üzerine kurulu paragraflar yeniden yazılır. |
| **Sentez agent'a tüm web search araçlarını ver** (Q9 şık C) | Çok geniş yetki — rol dışı araç kötüye kullanılır; sentez agent araştırma yapmaya başlar, rolü bulanıklaşır. %15'lik derin vakalar için web search agent'ın uzmanlığı kaybolur. Least privilege ihlali. |
| **Web search agent proaktif olarak her kaynak için ekstra bağlam cache'lesin** (Q9 şık D) | Spekülatif — neyin doğrulanacağı önceden bilinemez; context şişer, maliyet artar, %15'lik derin vakaları yine çözmez. |
| Koordinatörü daha hızlı modelle çalıştır | Yapısal gecikmeyi çözmez — tur-dönüş hâlâ var. |
| Doğrulama adımını kaldır | Fonksiyonalite kaybı — doğrulama kalite adımı. |
| Sentez agent'a tam `fetch_url` ver | Çok geniş kapsamlı — güvenlik riski, odak kaybı. |

---

## Genel Araçları Kısıtlanmış Alternatiflerle Değiştirme

Subagent'lara genel amaçlı araçlar vermek yerine, kısıtlanmış alternatifler ver:

- ❌ `fetch_url` — her URL'yi çekebilir, güvenlik riski (prompt injection yüzeyi, veri sızıntısı)
- ✅ `load_document` — sadece onaylı doküman URL'lerini doğrulayıp çeker

- ❌ `run_sql` — her sorguyu çalıştırır
- ✅ `get_order_by_id` — tek bir parametreli, salt okunur sorgu

Daha güvenli, daha odaklı, daha az hata riski. Bu, least privilege'ın araç *kapsamı* boyutudur (yukarıdaki dağıtım, araç *sayısı* boyutuydu).

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Araç aşırı yüklemesi | 18 araç = seçim güvenilirliği düşer. Optimal: agent başına 4–5 araç, rol bazlı |
| Rol dışı araç | Kötüye kullanılır (sentez agent arama yapar) → verme |
| Least privilege | Her agent'a işine yetecek en dar set — sayı **ve** kapsam olarak |
| Nasıl uygulanır | Subagent `tools` / `disallowedTools`; MCP araçları `mcp__server__tool` |
| `"auto"` | Varsayılan — model araç veya metin seçer |
| `"any"` | Mutlaka araç çağırır, hangisini seçer — garantili yapılandırılmış çıktı |
| `{"type":"tool","name":"X"}` | Belirli aracı zorlar — zorunlu ilk adım; **sonraki turda `auto`'ya dön** |
| `"none"` | Bu turda araç yok, yalnızca metin |
| `disable_parallel_tool_use` | Tek yanıtta tek araç çağrısı; `any`/`tool` ile "tam olarak bir" |
| Thinking + forced | Manuel extended thinking ile `any`/`tool` birlikte olmaz |
| Scoped cross-role tools | Yüksek frekanslı basit işler için dar kapsamlı araç ver, karmaşık olanlar koordinatörden aksın |
| Kısıtlanmış alternatifler | `fetch_url` yerine `load_document` — güvenlik ve odak |

---

## Pratik Senaryo

> Bir sentez agent'ı nihai rapor yazarken sık sık iddiaları doğrulaması gerekiyor. Her doğrulama için koordinatöre kontrol veriyor, koordinatör web search subagent'ı çağırıyor, sonuç geri dönüyor. Bu süreç görev başına 2–3 ek tur-dönüş ekliyor ve toplam gecikmeyi %40 artırıyor. Doğrulamaların %85'i "X doğru mu?" şeklinde basit arama; %15'i derin araştırma gerektiriyor.
>
> **Gecikmeyi azaltırken sistem güvenilirliğini korumanın en etkili yolu hangisidir?**
>
> **A)** Sentez agent'a kapsamlandırılmış bir `verify_fact` aracı ver — basit aramalar doğrudan agent'ta çözülsün, karmaşık doğrulamalar koordinatör üzerinden web search agent'a aksın.
>
> **B)** Sentez agent tüm doğrulama ihtiyaçlarını biriktirsin ve geçişinin sonunda toplu olarak koordinatöre göndersin; koordinatör hepsini tek seferde web search agent'a iletsin.
>
> **C)** Sentez agent'a tüm web search araçlarına erişim ver — her doğrulamayı koordinatöre gitmeden kendisi yapsın.
>
> **D)** Web search agent ilk araştırma sırasında her kaynağın çevresinde proaktif olarak ekstra bağlam cache'lesin — sentez agent'ın doğrulamak isteyebileceği şeyleri önceden tahmin etsin.

### Doğru Cevap: A

**Neden A doğru:** Vakaların %85'i basit arama — bunlar için koordinatöre gitmek gereksiz gecikme yaratıyor. Kapsamlandırılmış `verify_fact` aracı basit doğrulamaları agent'ta çözer; %15'lik karmaşık olanlar hâlâ koordinatör → web search agent yolundan akar. Least privilege: sentez agent'a yaygın vaka için *gereken kadar* yetki. Gecikme azalır, mimari bütünlük korunur.

**Neden B yanlış:** Toplu gönderim gecikmeyi *biriktirir*, kaldırmaz — en az bir ek tur-dönüş kalır. Ayrıca sentez agent doğrulanmamış iddialarla yazmaya devam eder; sonuçlar gelince hatalı iddialara dayanan bölümleri yeniden yazmak zorunda kalır. Kalite ve gecikme birlikte kötüleşebilir.

**Neden C yanlış:** Tüm web search araçları çok geniş yetki. Rol dışı araçlar kötüye kullanılır — sentez agent araştırma yapmaya başlar, rolü bulanıklaşır. %15'lik derin vakalar web search agent'ın uzmanlığını kaybeder. Least privilege ihlali.

**Neden D yanlış:** Spekülatif — hangi iddiaların doğrulanacağı önceden bilinemez. Context şişer, maliyet artar; %15'lik derin vakalar yine koordinatöre gider. Sorunu çözmeden yeni maliyet ekler.
