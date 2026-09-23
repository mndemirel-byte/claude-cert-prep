# Task Statement 4.5: Toplu İşleme (Batch Processing)

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Her Claude çağrısı eşzamanlı (synchronous) olmak zorunda değil. **Message Batches API**, belirli görevler için önemli maliyet tasarrufu sağlar — ama kısıtlamaları vardır ve bu kısıtlamalar sınavın odak noktasıdır.

Temel soru: **"Bu iş akışı beklemeye tahammül edebilir mi?"**

---

## Message Batches API — Temel Özellikler

| Özellik | Değer |
|---------|-------|
| **Maliyet tasarrufu** | %50 (senkron API'ye kıyasla) |
| **İşlem penceresi** | 24 saate kadar |
| **Gecikme garantisi** | Yok (SLA belirsiz) |
| **Multi-turn tool calling** | Desteklenmiyor |
| **İstek-yanıt eşleştirme** | `custom_id` ile |

---

## Senkron vs. Batch — Karar Kuralı

Bu ayrım sınavda her zaman çıkar. Ezberle:

### Senkron API Kullan (Bloklanabilir iş akışları)

```
- Pre-merge kod incelemeleri → Geliştiriciler commit'i bekliyor
- Gerçek zamanlı güvenlik taraması → CI/CD pipeline durumu bekleniyor
- Kullanıcı etkileşimli görevler → İnsan sonucu bekliyor
- SLA gerektiren herhangi bir şey → Gecikme garantisi lazım
```

**Kural:** İnsan veya sistem sonucu bekliyorsa → Senkron.

### Batch API Kullan (Gecikmeye toleranslı iş akışları)

```
- Gece raporları → Sabaha hazır olması yeterli
- Haftalık kod kalite auditleri → Ertesi güne kadar beklenebilir
- Gece test üretimi → Gündüz pipeline'da hazır olur
- Büyük arşiv analizi → Acil değil
- Toplu belge çıkarımı → Saatler içinde tamamlanması yeterli
```

**Kural:** Belirli bir gecikme toleransı varsa ve %50 maliyet tasarrufu cazip geliyorsa → Batch.

---

## Sınavın Q11 Tuzağı

Sınav genellikle şu senaryoyu sunar:

> *"Bir mühendislik müdürü maliyetleri azaltmak için tüm Claude çağrılarını Batch API'ye taşımayı öneriyor."*

**Yanlış cevaplar:**
- "Harika fikir, %50 tasarruf büyük fark yaratır" — Hayır
- "Batch API tüm görevler için uygun" — Hayır

**Doğru cevap:**
> *"Pre-merge kontroller ve CI/CD pipeline bekleyen görevler senkron kalmalı. Sadece gecikmeye toleranslı iş akışları (gece raporları, haftalık auditler) Batch'e taşınabilir."*

**Temel prensip:** Batch, senkronu desteklemez. Sadece tamamlar.

---

## custom_id — İstek/Yanıt Eşleştirme

Batch işlemde hangi yanıtın hangi isteğe ait olduğunu `custom_id` ile takip edersin:

```python
import anthropic

client = anthropic.Anthropic()

# Batch isteği oluştur
requests = []
for doc_id, document in documents.items():
    requests.append({
        "custom_id": f"doc-{doc_id}",  # Takip için benzersiz ID
        "params": {
            "model": "claude-opus-4-5",
            "max_tokens": 1000,
            "messages": [{
                "role": "user",
                "content": f"Bu belgeyi analiz et:\n{document}"
            }]
        }
    })

# Batch gönder
batch = client.beta.messages.batches.create(requests=requests)

# Sonuçları al (24 saate kadar)
for result in client.beta.messages.batches.results(batch.id):
    doc_id = result.custom_id  # Hangi belge?
    
    if result.result.type == "succeeded":
        response = result.result.message.content[0].text
        process_result(doc_id, response)
    else:
        # Başarısız → custom_id ile yeniden gönder
        handle_failure(doc_id, result.result.error)
```

---

## Başarısız İstekleri Yönetme

Batch'te bazı belgeler başarısız olabilir (çok büyük, hatalı format, vs.).

### Doğru Yaklaşım

```
1. Tüm batch sonuçlarını al
2. custom_id üzerinden başarısız olanları filtrele
3. Sadece başarısız belgeleri yeniden gönder:
   - Aşırı büyük belgeler → Parçalara böl, yeniden gönder
   - Prompt hatası → Prompt'u düzelt, yeniden gönder
4. Başarılı olanları tekrar gönderme — maliyet iki katına çıkar
```

```python
failed_requests = []
for result in batch_results:
    if result.result.type != "succeeded":
        original_doc = documents[result.custom_id]
        
        if "too large" in str(result.result.error):
            # Belgeyi parçala
            chunks = chunk_document(original_doc)
            for i, chunk in enumerate(chunks):
                failed_requests.append({
                    "custom_id": f"{result.custom_id}-chunk-{i}",
                    "params": build_params(chunk)
                })
        else:
            failed_requests.append(rebuild_request(result.custom_id))

# Sadece başarısızları yeniden gönder
if failed_requests:
    retry_batch = client.beta.messages.batches.create(requests=failed_requests)
```

---

## Batch Öncesi Optimizasyon

**Büyük batch göndermeden önce küçük örnekle test et.**

```
Neden?
- 1000 belge batch gönderdin, prompt hatalı
- 24 saat sonra tüm sonuçlar kullanılamaz
- Maliyet: yarısı gitti, iş sıfırdan başlıyor

Doğru yaklaşım:
1. 10-20 temsilci belge seç
2. Senkron API ile test et
3. Extraction kalitesini doğrula
4. Sorunları gider
5. Batch'e geç → İlk seferden başarı oranını maksimize et
```

---

## Multi-Turn Tool Calling Kısıtlaması

Sınavın trick sorusu:

> *"Batch API'de çok adımlı araç çağrısı gerektiren bir extraction pipeline çalıştırmak istiyorum."*

**Cevap:** Batch API bunu desteklemez. Multi-turn tool calling senkron API gerektirir — her araç çağrısı sonucu bir sonraki istek için input oluşturur.

```
Desteklenen → Batch:
  Tek istek → Tek yanıt (araç çağrısı olmayan veya tek araç çağrısı)

Desteklenmeyen → Batch:
  İstek → Araç çağrısı → Araç sonucu → Devam → Sonuç
  (multi-turn, iterative tool use)
```

---

## Pratik Karar Ağacı

```
Görev nedir?
│
├─ Geliştiriciler/sistem sonucu bekliyor mu?
│   ├─ EVET → Senkron API
│   └─ HAYIR ↓
│
├─ Belirli bir gecikme SLA var mı?
│   ├─ EVET → Senkron API
│   └─ HAYIR ↓
│
├─ Multi-turn tool calling gerekiyor mu?
│   ├─ EVET → Senkron API
│   └─ HAYIR ↓
│
└─ Maliyet önemli mi ve gecikme toleranslı mı?
    ├─ EVET → Batch API (%50 tasarruf)
    └─ HAYIR → Senkron API
```

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Batch API: %50 maliyet tasarrufu, 24 saate kadar işlem, SLA yok.** |
| 2 | **Bloklanabilir iş akışları (CI/CD, pre-merge) → her zaman senkron.** |
| 3 | **Gecikmeye toleranslı iş akışları (gece raporu, haftalık audit) → batch.** |
| 4 | **`custom_id` ile istek-yanıt eşleştirmesi yapılır.** |
| 5 | **Batch, multi-turn tool calling desteklemez.** |
| 6 | **Başarısızlarda yalnızca başarısız belgeler yeniden gönderilir, tüm batch değil.** |
| 7 | **Büyük batch öncesi küçük örnekle test et** — ilk seferden başarı oranını artır. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Bir takım, %50 maliyet tasarrufu için tüm Claude çağrılarını Batch API'ye taşımayı planlıyor. Buna dahil: (a) gece kod kalite raporları, (b) PR merge öncesi güvenlik taraması. Bu plan doğru mu?

**A)** Evet, her iki kullanım da Batch için uygundur  
**B)** Hayır, her iki kullanım da senkron kalmalıdır  
**C)** Hayır; gece raporları batch'e alınabilir, PR güvenlik taraması senkron kalmalıdır  
**D)** Evet ama Batch API sadece gece 00:00-06:00 arası çalışır  

**✅ Cevap: C**

*Açıklama:* Gece raporları gecikmeye toleranslı — sabah hazır olması yeterli, batch uygun. PR güvenlik taraması bloklanabilir iş akışı — geliştiriciler merge öncesi sonucu bekliyor, senkron gerekli. Tümünü batch'e almak CI/CD'yi kırar.

---

### Soru 2

Batch API ile 500 belge gönderildi. 24 saat sonra 480 başarılı, 20 başarısız. Sonraki adım nedir?

**A)** Tüm 500 belgeyi yeniden gönder  
**B)** Sadece 20 başarısız belgeyi, gerekiyorsa modifiye ederek yeniden gönder  
**C)** Başarısız 20 belgeyi elle incele ve atla  
**D)** Daha küçük bir modelle tüm batch'i yeniden işle  

**✅ Cevap: B**

*Açıklama:* custom_id sayesinde hangi belgeler başarısız olduğu bilinir. Sadece bunları yeniden göndermek maliyeti minimize eder. Tüm batch'i yeniden göndermek 480 başarılı belge için gereksiz harcama demektir.

---

### Soru 3

Batch API hangi senaryoda kullanılamaz?

**A)** 1000 fatura belgesinin haftalık analizi  
**B)** Gece test senaryosu üretimi  
**C)** Çok adımlı araç çağrısı gerektiren extraction (sonuç → yeni araç çağrısı → sonuç)  
**D)** Arşiv belgelerinin toplu sınıflandırması  

**✅ Cevap: C**

*Açıklama:* Batch API multi-turn tool calling'i desteklemez. Her batch isteği bağımsız — önceki araç sonuçlarını bir sonraki isteğe bağlayan iteratif akış senkron API gerektirir.

---

### Soru 4

Büyük bir batch işlemi başlatmadan önce en iyi pratik nedir?

**A)** En güçlü modeli kullan — kalite otomatik artar  
**B)** Tüm belgeleri göndermeden önce 10-20 temsilci belge üzerinde senkron API ile test et  
**C)** Önce tüm batch'i gönder, sonuçlara göre prompt'u düzelt ve yeniden gönder  
**D)** Custom_id olmadan gönder — daha hızlı işlenir  

**✅ Cevap: B**

*Açıklama:* Küçük örnekle test, prompt hataları erken yakalanır. 24 saat bekleyip tüm sonuçların kullanılamaz olduğunu öğrenmek yerine, önce doğrulayıp sonra büyük batch göndermek hem zamandan hem maliyetten tasarruf sağlar.
