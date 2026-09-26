# Task Statement 4.5: Toplu İşleme (Batch Processing)

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Her Claude çağrısı eşzamanlı (synchronous) olmak zorunda değil. **Message Batches API**, belirli görevler için önemli maliyet tasarrufu sağlar — ama kısıtlamaları vardır ve bu kısıtlamalar sınavın odak noktasıdır.

Temel soru: **"Bu iş akışı beklemeye tahammül edebilir mi?"**

> **Karıştırma uyarısı:** Exam guide'da Q10 (`claude -p`, Claude Code headless/CI) ile Q11 (Message Batches API) art arda gelir ve Q10'un distractor'larından biri `--batch` bayrağıdır. **Böyle bir bayrak yok.** Message Batches API, *Messages API*'nin bir özelliğidir (`/v1/messages/batches`); Claude Code'un pipeline'da çalışması ise `-p` bayrağıdır (Domain 3.6). "Batch" kelimesini görünce hangisinin sorulduğuna bak.

---

## Message Batches API — Temel Özellikler

| Özellik | Değer |
|---------|-------|
| **Maliyet tasarrufu** | %50 (senkron API'ye kıyasla); prompt caching indirimiyle **üst üste biner** |
| **İşlem penceresi** | Çoğu batch **1 saat içinde** biter; üst sınır **24 saat** |
| **Gecikme garantisi** | Yok (SLA yok) — ama 24 saatlik **üst sınır** var; hesaplar buna dayanır |
| **24 saat dolarsa** | Kalan istekler `expired` olur, **faturalanmaz**, yeniden gönderilir |
| **Batch başına limit** | 100.000 istek veya 256 MB (hangisi önce) |
| **Sonuçların saklanması** | Batch oluşturulduktan sonra 29 gün indirilebilir |
| **İstek-yanıt eşleştirme** | `custom_id` ile — çünkü **sonuçlar istek sırasında dönmez** |
| **Desteklenen** | Tool use, çok turlu konuşma geçmişi, extended thinking, vision, PDF, prompt caching, structured outputs |
| **Desteklenmeyen** | `stream: true`; **tek istek içinde araç çalıştırıp devam etme** (aşağıya bak) |

---

## Senkron vs. Batch — Karar Kuralı

Bu ayrım sınavda her zaman çıkar. Ezberle:

### Senkron API Kullan (Bloklanabilir iş akışları)

```
- Pre-merge kod incelemeleri → Geliştiriciler commit'i bekliyor
- Gerçek zamanlı güvenlik taraması → CI/CD pipeline durumu bekleniyor
- Kullanıcı etkileşimli görevler → İnsan sonucu bekliyor
- 24 saatten kısa gecikme sınırı olan her şey → Batch üst sınırı sığmaz
```

**Kural:** İnsan veya sistem sonucu *şimdi* bekliyorsa → Senkron.

### Batch API Kullan (Gecikmeye toleranslı iş akışları)

```
- Gece raporları → Sabaha hazır olması yeterli
- Haftalık kod kalite auditleri → Ertesi güne kadar beklenebilir
- Gece test üretimi → Gündüz pipeline'da hazır olur
- Büyük arşiv analizi → Acil değil
- Toplu belge çıkarımı → Saatler içinde tamamlanması yeterli
```

**Kural:** Gecikme toleransı 24 saatten büyükse (ya da SLA hesabı tutuyorsa — aşağı bak) ve %50 maliyet tasarrufu cazip geliyorsa → Batch.

---

## Sınavın Q11 Tuzağı

Sınav genellikle şu senaryoyu sunar:

> *"Bir mühendislik müdürü maliyetleri azaltmak için tüm Claude çağrılarını Batch API'ye taşımayı öneriyor: gece raporları ve pre-merge güvenlik kontrolleri."*

**Yanlış cevaplar (Q11'in gerçek şıkları):**
- "Her ikisini de batch'e taşı" — Pre-merge kontrol her PR'da 24 saate kadar bekler
- "Her ikisini de senkron tut" — Gece raporlarındaki %50 tasarruf boşa gider
- "Her ikisini de batch'e taşı, **timeout olursa senkrona düş (fallback)**" — En çekici tuzak: "en kötü durumu yönetiyorum" gibi görünür, ama pre-merge kontrol için *her* PR önce bekler sonra timeout'a düşer; gecikme de maliyet de artar

**Doğru cevap:**
> *"Yalnızca gece raporları / haftalık auditler gibi gecikmeye toleranslı iş akışları Batch'e taşınır. Pre-merge kontroller ve CI/CD pipeline'ın beklediği görevler senkron kalır."*

**Temel prensip:** Batch, senkronun **yerine geçmez**; onu **tamamlar**.

---

## SLA'ya Göre Gönderim Sıklığı Hesabı — Domain 4'ün Tek Hesap Sorusu

Exam guide'ın Skills maddesi: "*Calculating batch submission frequency based on SLA constraints (e.g., **4-hour windows to guarantee 30-hour SLA with 24-hour batch processing**)*". Hazırlık Egzersizi 3 adım 14 de "*calculate total processing time relative to SLA constraints*" der.

"Batch'in SLA'sı yok" cümlesi seni "batch ile SLA verilemez" sonucuna götürmesin. Batch'in **24 saatlik üst sınırı** var; SLA 24 saatten büyükse batch ile SLA verilebilir — yeter ki gönderim sıklığı doğru seçilsin.

### Formül

Bir belgenin en kötü durum gecikmesi iki parçadan oluşur:

```
en kötü gecikme = (bir sonraki gönderimi bekleme) + (batch işlem üst sınırı)
                = P + 24 saat

Şart: P + 24 ≤ SLA   →   P ≤ SLA − 24
```

- **P** = gönderim penceresi (batch'leri kaç saatte bir gönderiyorsun). Bir belge pencerenin *başında* gelirse bir sonraki gönderime kadar P saat bekler.
- Belge pencere sonunda gelirse bekleme ~0; ama SLA en kötü durum için verilir.

### Örnekler

| SLA | Hesap | Sonuç |
|-----|-------|-------|
| 30 saat | P ≤ 30 − 24 = 6 | En geç **6 saatte bir** gönder; guide'ın **4 saatlik** penceresi 2 saat pay bırakır (4 + 24 = 28 < 30) |
| 36 saat | P ≤ 12 | 12 saatte bir (ör. 08:00 ve 20:00) |
| 26 saat | P ≤ 2 | 2 saatte bir — sık; hâlâ %50 tasarruf |
| 24 saat veya altı | P ≤ 0 | **Batch ile SLA verilemez** → senkron |
| P = 6 saat sabit | SLA ≥ 6 + 24 | Verebileceğin en iyi SLA **30 saat** |

### Sınav soru kalıpları
- "30 saatlik SLA, 24 saatlik batch işleme; batch'ler kaç saatte bir gönderilmeli?" → **≤ 6 saat** (4 saat güvenli)
- "6 saatte bir gönderiyoruz; müşteriye hangi SLA'yı taahhüt edebiliriz?" → **30 saat**
- "SLA 20 saat, batch kullanabilir miyiz?" → **Hayır** (20 < 24)
- Toplam işlem süresi sorusu (Egzersiz 3): 100 belge tek batch → süre ≤ 24 saat; günlük hacim tek batch limitini (100.000 / 256 MB) aşmıyorsa parçalamaya gerek yok

---

## custom_id — İstek/Yanıt Eşleştirme

Batch sonuçları **istek sırasında dönmez**; hangi yanıtın hangi isteğe ait olduğunu yalnızca `custom_id` ile bilirsin.

**Kurallar:** 1–64 karakter, yalnızca `a-z A-Z 0-9 _ -` (regex `^[a-zA-Z0-9_-]{1,64}$`), batch içinde benzersiz. Anlamlı ID kullan (`doc-{id}`, `doc-{id}-chunk-{n}`), rastgele değil.

```python
import anthropic

client = anthropic.Anthropic()

# Batch isteği oluştur
requests = []
for doc_id, document in documents.items():
    requests.append({
        "custom_id": f"doc-{doc_id}",  # Takip için benzersiz ID
        "params": {
            "model": "claude-sonnet-5",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": f"Bu belgeyi analiz et:\n{document}"
            }]
        }
    })

# Batch gönder (GA endpoint — beta değil)
batch = client.messages.batches.create(requests=requests)

# Durumu izle: processing_status "in_progress" → "ended"
import time
while True:
    batch = client.messages.batches.retrieve(batch.id)
    if batch.processing_status == "ended":
        break
    time.sleep(60)
print(batch.request_counts)  # {processing, succeeded, errored, canceled, expired}

# Sonuçları al (.jsonl akışı; sıra garantili değil)
for result in client.messages.batches.results(batch.id):
    doc_id = result.custom_id  # Hangi belge?
    outcome = result.result

    if outcome.type == "succeeded":
        response = outcome.message.content[0].text
        process_result(doc_id, response)
    elif outcome.type == "expired":
        resubmit_as_is(doc_id)                      # 24 saat doldu, faturalanmadı → aynen tekrar gönder
    elif outcome.type == "errored":
        handle_failure(doc_id, outcome.error)       # isteğin kendisi hatalı → düzelt, sonra gönder
    elif outcome.type == "canceled":
        pass                                        # sen iptal ettin
```

---

## Başarısız İstekleri Yönetme

Bir batch'te dört sonuç tipi vardır ve her biri farklı bir eylem ister:

| `result.type` | Ne oldu? | Faturalandı mı? | Eylem |
|---------------|----------|-----------------|-------|
| `succeeded` | Yanıt üretildi | ✅ | İşle. **Tekrar gönderme** — maliyet iki katına çıkar |
| `errored` | İstek geçersiz (çok büyük, hatalı parametre) veya sunucu hatası | ❌ | İsteği **düzelt** (chunk'la, parametreyi onar), sonra gönder |
| `expired` | 24 saat doldu, sıra gelmedi | ❌ | **Aynen** yeniden gönder (istekte sorun yok) |
| `canceled` | Sen iptal ettin | ❌ | Kasıtlı; gerekiyorsa gönder |

### Doğru Yaklaşım

```
1. Tüm batch sonuçlarını al
2. custom_id üzerinden succeeded olmayanları filtrele
3. Sadece bunları yeniden gönder:
   - expired → değiştirmeden
   - errored "too large" / bağlam limiti → belgeyi parçalara böl (chunk), yeniden gönder
   - errored prompt/parametre hatası → düzelt, yeniden gönder
4. Başarılı olanları tekrar gönderme
```

```python
retry_requests = []
for result in client.messages.batches.results(batch.id):
    outcome = result.result
    if outcome.type == "succeeded":
        continue
    original_doc = documents[result.custom_id.removeprefix("doc-")]

    if outcome.type == "expired":
        retry_requests.append(rebuild_request(result.custom_id))          # aynen
    elif outcome.type == "errored" and "too large" in str(outcome.error):
        for i, chunk in enumerate(chunk_document(original_doc)):          # parçala
            retry_requests.append({
                "custom_id": f"{result.custom_id}-chunk-{i}",
                "params": build_params(chunk)
            })
    elif outcome.type == "errored":
        retry_requests.append(fix_and_rebuild(result.custom_id, outcome.error))

# Sadece başarısızları yeniden gönder
if retry_requests:
    retry_batch = client.messages.batches.create(requests=retry_requests)
```

---

## Batch Öncesi Optimizasyon

**Büyük batch göndermeden önce küçük örnekle test et.** Resmi tavsiye: "*Test with the Messages API first — validate request shape synchronously before batching.*" Exam guide: "*prompt refinement on a sample set before batch-processing large volumes to maximize first-pass success rates*".

```
Neden?
- 1000 belge batch gönderdin, prompt hatalı
- 24 saat sonra tüm sonuçlar kullanılamaz
- Maliyet: yarısı gitti, iş sıfırdan başlıyor

Doğru yaklaşım:
1. 10-20 temsilci belge seç (Task 4.1'deki etiketli eval setinin aynısı)
2. Senkron API ile test et
3. Extraction kalitesini doğrula
4. Sorunları gider
5. Batch'e geç → İlk seferden başarı oranını maksimize et
```

**Ek tasarruf — prompt caching:** system prompt + few-shot örnekleri + araç şeması tüm isteklerde aynıysa `cache_control` ile önbelleklenir; batch'in %50'si caching indiriminin üstüne biner. Batch içinde de yüksek cache isabet oranı elde edilir (istekler benzer sırayla işlenir).

**Büyük kümeler:** 100.000 istek / 256 MB limiti aşılıyorsa birden fazla batch. Batch'teki kuyruk istekleri de rate limit'e sayılır; çok yüksek hacim workspace harcama limitini aşabilir.

---

## "Multi-Turn Tool Calling" Kısıtlaması — Doğru Okunuşu

Sınavın trick sorusu:

> *"Batch API'de çok adımlı araç çağrısı gerektiren bir extraction pipeline çalıştırmak istiyorum."*

**Sınav cevabı:** Batch API bunu **tek istek içinde** desteklemez. Exam guide'ın tam cümlesi: "*does not support multi-turn tool calling **within a single request** (cannot execute tools mid-request and return results)*".

**Ne demek, ne demek değil:**

```
Bir batch isteği = TEK bir Messages çağrısı.
  ✅ Araç tanımlayabilirsin (tools=[...]); Claude tool_use bloğu döndürebilir
  ✅ Çok turlu konuşma GEÇMİŞİ gönderebilirsin (önceki tool_use/tool_result dahil)
  ✅ Extended thinking, vision, caching, structured outputs çalışır
  ❌ Claude SENİN aracını çağırırsa yanıt stop_reason="tool_use" ile biter;
     aracı batch içinde çalıştırıp sonucu verip DEVAM ETTİREMEZSİN.
     Devam = aracı kendin çalıştır → tool_result'lı yeni istek (yeni batch veya senkron).

Desteklenen → Batch:
  İstek → Yanıt (metin veya tek turluk tool_use çıktısı — ör. extraction aracı)

Desteklenmeyen (tek istekte) → Senkron veya zincirlenmiş batch'ler:
  İstek → Araç çağrısı → (sen çalıştır) → Araç sonucu → Devam → Sonuç
```

Pratik sonuç: **extraction** (tek çağrı, `tool_choice` ile araç zorlanır, `input` alınır) batch için idealdir; **agentic döngü** (araç sonucuna göre bir sonraki adım) batch için uygun değildir — ya senkron, ya her turu ayrı batch olarak zincirle (gecikme her turda 24 saate kadar büyür).

> **Güncel not (sınav cevabını değiştirmez):** *sunucu* araçları (web search, code execution, web fetch gibi Anthropic'in çalıştırdığı araçlar) batch içinde agentic döngüyle çalışır, çünkü onları sen değil API çalıştırır. Kısıt yalnızca **istemci (senin) araçların** içindir.

---

## Pratik Karar Ağacı

```
Görev nedir?
│
├─ Geliştiriciler/sistem sonucu ŞİMDİ bekliyor mu? (pre-merge, etkileşimli)
│   ├─ EVET → Senkron API
│   └─ HAYIR ↓
│
├─ Gecikme sınırı (SLA) 24 saatten KISA mı?
│   ├─ EVET → Senkron API
│   └─ HAYIR (SLA yok veya > 24 saat) ↓
│       └─ SLA varsa gönderim penceresi P ≤ SLA − 24 saat olarak planla
│
├─ İstemci aracı çalıştırıp aynı istekte devam etmek gerekiyor mu? (agentic döngü)
│   ├─ EVET → Senkron API (veya turları ayrı batch'ler olarak zincirle)
│   └─ HAYIR ↓
│
└─ Hacim büyük ve maliyet önemli mi?
    ├─ EVET → Batch API (%50 tasarruf; küçük örnekle önce test et)
    └─ HAYIR → Senkron API
```

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Batch API: %50 maliyet tasarrufu, çoğu 1 saat / üst sınır 24 saat, gecikme SLA'sı yok** — ama 24 saatlik üst sınır hesap yapmaya yeter. |
| 2 | **Bloklanabilir iş akışları (CI/CD, pre-merge) → her zaman senkron.** "Timeout fallback" tuzağına düşme. |
| 3 | **Gecikmeye toleranslı iş akışları (gece raporu, haftalık audit) → batch.** Batch senkronun yerine geçmez, onu tamamlar. |
| 4 | **SLA hesabı: P ≤ SLA − 24 saat.** 30 saat SLA → ≤ 6 saatte bir gönder (4 saat güvenli). SLA ≤ 24 saat → batch olmaz. |
| 5 | **`custom_id` ile eşleştir** — sonuçlar sırayla dönmez; 1–64 karakter, `[A-Za-z0-9_-]`, benzersiz. |
| 6 | **Batch tek istek içinde istemci aracını çalıştırıp devam edemez;** tool use, geçmiş, thinking, caching desteklenir. Extraction ✅, agentic döngü ❌. |
| 7 | **Dört sonuç tipi:** `succeeded` işle · `expired` aynen gönder · `errored` düzelt/chunk'la gönder · `canceled`. Başarılıları tekrar gönderme. |
| 8 | **Büyük batch öncesi küçük örnekle senkron test et;** prompt caching ile ek tasarruf. `client.messages.batches.*` (GA, beta değil). |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Bir takım, %50 maliyet tasarrufu için tüm Claude çağrılarını Batch API'ye taşımayı planlıyor. Buna dahil: (a) gece kod kalite raporları, (b) PR merge öncesi güvenlik taraması. Bu plan doğru mu?

**A)** Evet, her iki kullanım da Batch için uygundur  
**B)** Hayır, her iki kullanım da senkron kalmalıdır  
**C)** Hayır; gece raporları batch'e alınabilir, PR güvenlik taraması senkron kalmalıdır  
**D)** Evet; her ikisi batch'e alınır, 15 dakikada sonuç gelmezse senkron API'ye düşülür  

**✅ Cevap: C**

*Açıklama:* Gece raporları gecikmeye toleranslı — sabah hazır olması yeterli, batch uygun. PR güvenlik taraması bloklanabilir iş akışı — geliştiriciler merge öncesi sonucu bekliyor, senkron gerekli. (D) exam guide Q11'in gerçek tuzağıdır: pre-merge tarama için *her* PR önce 15 dakika bekler, sonra senkron çağrı yapılır — hem gecikme hem maliyet artar, tasarruf yok. (B) gece raporlarındaki tasarrufu boşa harcar.

---

### Soru 2

Batch API ile 500 belge gönderildi. 24 saat sonra 480 başarılı, 12 `expired`, 8 `errored` ("request too large"). Sonraki adım nedir?

**A)** Tüm 500 belgeyi yeniden gönder  
**B)** 12 expired belgeyi aynen, 8 errored belgeyi parçalara bölerek (chunk) yeni bir batch'te gönder; 480 başarılıyı gönderme  
**C)** 20 başarısız belgeyi elle incele ve atla  
**D)** 20 belgenin hepsini parçalara bölerek yeniden gönder  

**✅ Cevap: B**

*Açıklama:* custom_id sayesinde hangi belgelerin hangi nedenle başarısız olduğu bilinir. `expired` isteklerde sorun yoktur (sıra gelmedi, faturalanmadı) → değiştirmeden gönder. `errored` "too large" → belge bağlam limitini aşmış → chunk'la. Tüm batch'i yeniden göndermek (A) 480 belge için gereksiz harcama. (D) expired belgeleri gereksiz yere parçalar.

---

### Soru 3

Batch API hangi senaryoda kullanılamaz?

**A)** 1000 fatura belgesinin haftalık analizi  
**B)** Gece test senaryosu üretimi  
**C)** Her belge için önce bir arama aracını (senin sunucundaki) çağırıp sonucuna göre ikinci bir aracı çağıran, tek istekte tamamlanması gereken extraction  
**D)** Arşiv belgelerinin toplu sınıflandırması  

**✅ Cevap: C**

*Açıklama:* Batch API tek istek içinde istemci aracını çalıştırıp devam edemez — Claude `tool_use` döndürür ve istek biter; sonucu verip devam etmek yeni bir istek gerektirir. Bu iteratif akış senkron API (veya zincirlenmiş batch'ler) gerektirir. Diğer üçü tek istek → tek yanıt işleridir.

---

### Soru 4

Büyük bir batch işlemi başlatmadan önce en iyi pratik nedir?

**A)** En güçlü modeli kullan — kalite otomatik artar  
**B)** Tüm belgeleri göndermeden önce 10-20 temsilci belge üzerinde senkron API ile test et  
**C)** Önce tüm batch'i gönder, sonuçlara göre prompt'u düzelt ve yeniden gönder  
**D)** Custom_id olmadan gönder — daha hızlı işlenir  

**✅ Cevap: B**

*Açıklama:* Küçük örnekle test, prompt hataları erken yakalanır. 24 saat bekleyip tüm sonuçların kullanılamaz olduğunu öğrenmek yerine, önce doğrulayıp sonra büyük batch göndermek hem zamandan hem maliyetten tasarruf sağlar.

---

### Soru 5

Bir müşteriye "belgeniz en geç 30 saat içinde işlenir" SLA'sı veriliyor. Belgeler gün boyu düzensiz geliyor; maliyet için Batch API kullanılacak (işlem üst sınırı 24 saat). Batch'ler en seyrek kaç saatte bir gönderilmeli?

**A)** Günde bir kez — 24 saat + 24 saat = 48 < 30 × 2  
**B)** 6 saatte bir (4 saat daha güvenli): en kötü gecikme = bekleme (6) + işlem (24) = 30 ≤ 30  
**C)** Batch kullanılamaz; SLA olan her iş senkron olmalı  
**D)** 12 saatte bir — çoğu batch 1 saatte bittiği için yeterli  

**✅ Cevap: B**

*Açıklama:* P ≤ SLA − 24 = 6 saat. Exam guide'ın örneği 4 saatlik pencere (28 saat, 2 saat pay). (A) günde bir gönderimde pencere başında gelen belge 24 + 24 = 48 saat bekleyebilir. (C) "SLA yok" ile "SLA verilemez"i karıştırır; 24 saatlik üst sınır hesap yapmaya yeter. (D) SLA en kötü durum içindir; "çoğu 1 saatte biter" ortalamadır, garanti değil — 12 + 24 = 36 > 30.
