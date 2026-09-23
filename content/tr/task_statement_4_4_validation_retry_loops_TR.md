# Task Statement 4.4: Validation-Retry Döngüleri

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

İlk çıkarım her zaman mükemmel olmaz. Validation-retry, şu soruyu sorar: **"Hata geri gönderilebilir ve model kendini düzeltebilir mi?"**

Cevap duruma göre değişir. Ve sınav tam olarak bu ayrımı bilip bilmediğini test eder.

---

## Retry-with-Error-Feedback Mimarisi

### Temel Akış

```
1. Belge gönderilir → İlk çıkarım alınır
2. Çıkarım validate edilir
3. Hata varsa → Hata mesajıyla birlikte modele geri gönderilir
4. Model orijinal belgeyi + başarısız çıkarımı + hatayı görür
5. Model kendini düzeltir → Yeni çıkarım
6. Tekrar validate
```

### Retry İsteğinin İçeriği

```python
retry_prompt = f"""
Orijinal belge:
{original_document}

İlk çıkarım girişiminiz:
{failed_extraction}

Doğrulama hatası:
{validation_error}

Lütfen hatayı dikkate alarak çıkarımı düzeltin.
"""
```

**Kritik:** Modele sadece "yeniden dene" demek yetmez. **Spesifik hata mesajı** gerekir — model ne yanlış yaptığını bilmeden düzeltemez.

---

## Retry'ın Etkin Olduğu Durumlar

Bunları ezberle — sınav "bu senaryo için retry işe yarar mı?" diye sorar.

### ✅ Etkin: Format Uyuşmazlıkları

```
Hata: "invoice_date alanı '15/01/2024' formatında, beklenen: 'YYYY-MM-DD'"
Düzeltme: Model "2024-01-15" olarak yeniden döndürür.

Neden işe yarar: Bilgi belgede VAR, sadece yanlış formatlanmış.
```

### ✅ Etkin: Yapısal Çıktı Hataları

```
Hata: "line_items dizisinde 3 kalem var ama toplam satır sayısı 2 girilmiş"
Düzeltme: Model satır sayısını 3 olarak düzeltir.

Neden işe yarar: Çelişki tespit edilebilir, model yeniden bakarak düzeltebilir.
```

### ✅ Etkin: Yanlış Alana Yerleştirme

```
Hata: "unit_price alanında toplam değer görünüyor (450 TL, 3 adet × 150 TL)"
Düzeltme: Model unit_price'ı 150, total'ı 450 olarak düzeltir.

Neden işe yarar: Kaynak belgede her iki değer de var, sadece alan karışmış.
```

---

## Retry'ın Etkin OLMADIĞI Durumlar — Sınavın Tuzağı

### ❌ Etkin Değil: Bilgi Kaynakta Gerçekten Yok

```
Hata: "discount_rate null — zorunlu alan"
Gerçek: Belgede indirim oranı hiç yazılmamış.

Model ne yapar: Yeniden denese de aynı belgeye bakacak.
Bilgi yoksa model uydurur veya yine null döndürür.

Doğru çözüm: Schema'da discount_rate'i nullable yapın.
```

### ❌ Etkin Değil: Tutarsız Kaynak Belgesi

```
Belge içeriği:
- Satır kalemleri: 300 + 450 + 200 = 950 TL
- Kapak sayfası toplam: 1.100 TL

Retry hata mesajı: "Satır kalemleri toplamı 950, belirtilen toplam 1.100 TL"

Model ne yapar: Hangisi doğru? Belge kendi içinde çelişiyor.
Retry yardımcı olmaz — model belgeyi seçemez.

Doğru çözüm: conflict_detected flag ekle, insan incelemesine yönlendir.
```

---

## Anlamsal Doğrulama — Hesaplamalı Kontrol

Tool_use sözdizimi sorunlarını çözer. Ama anlamsal sorunlar için **aktif doğrulama mantığı** gerekir.

### calculated_total Alanı

```json
{
  "line_items": [
    {"description": "Ürün A", "unit_price": 100, "quantity": 3, "line_total": 300},
    {"description": "Ürün B", "unit_price": 150, "quantity": 2, "line_total": 300}
  ],
  "stated_total": 650,
  "calculated_total": 600,
  "totals_match": false
}
```

`calculated_total` alanını şemaya ekle — model her satırı toplayarak doldurur. Sonra backend'de `stated_total == calculated_total` kontrol edersin. Uyuşmazlık → retry veya flag.

### conflict_detected Boolean

Kaynak belgede çelişki tespit edildiğinde:

```json
{
  "vendor_name": "ABC Ltd.",
  "invoice_date": "2024-01-15",
  "stated_total": 1100,
  "calculated_total": 950,
  "conflict_detected": true,
  "conflict_details": "Satır toplamı (950 TL) kapak sayfası toplamıyla (1.100 TL) uyuşmuyor"
}
```

Bu flag ile sistem otomatik olarak insan incelemesine yönlendirebilir.

---

## detected_pattern Alanı — Uzun Vadeli İyileştirme

Bu alan sınavda sürpriz çıkabilir.

### Ne İçin Kullanılır?

Kod inceleme agent'ları için: Her bulgunun hangi kod yapısını tetiklediğini kayıt altına almak.

```json
{
  "finding_id": "BUG-001",
  "severity": "critical",
  "description": "SQL enjeksiyonu riski",
  "detected_pattern": "f-string içinde doğrudan SQL sorgusu: f\"SELECT * FROM {table}\"",
  "dismissed_by_developer": false
}
```

### Neden Önemli?

Geliştiriciler bazı bulguları reddeder (dismiss). `detected_pattern` sayesinde:
- Hangi kalıplar sık sık reddedildi?
- Reddedilen kalıplar gerçekten yanlış mı yoksa prompt calibration sorunu mu?
- Prompt'u iyileştirmek için hangi kategoriye odaklanmalı?

**Sistematik veri → Sistematik iyileştirme.**

---

## Self-Correction Flow — Tam Örnek

```python
import anthropic
import json

client = anthropic.Anthropic()

def extract_with_retry(document: str, max_retries: int = 2) -> dict:
    extraction = initial_extract(document)
    
    for attempt in range(max_retries):
        errors = validate(extraction)
        
        if not errors:
            return extraction  # Başarılı
        
        # Hata geri bildirimli retry
        extraction = retry_extract(document, extraction, errors)
    
    # Son kontrol
    final_errors = validate(extraction)
    if final_errors:
        return {"extraction": extraction, "warnings": final_errors}
    
    return extraction

def validate(extraction: dict) -> list[str]:
    errors = []
    
    # Format kontrolü
    if extraction.get("invoice_date"):
        try:
            datetime.strptime(extraction["invoice_date"], "%Y-%m-%d")
        except ValueError:
            errors.append(f"invoice_date formatı yanlış: '{extraction['invoice_date']}'. Beklenen: YYYY-MM-DD")
    
    # Anlamsal kontrol
    if extraction.get("line_items") and extraction.get("stated_total"):
        calculated = sum(item.get("line_total", 0) for item in extraction["line_items"])
        stated = extraction["stated_total"]
        if abs(calculated - stated) > 1:  # 1 kuruş tolerans
            errors.append(
                f"Toplam uyuşmazlığı: hesaplanan {calculated}, belirtilen {stated}"
            )
    
    return errors

def retry_extract(document: str, failed: dict, errors: list[str]) -> dict:
    error_text = "\n".join(f"- {e}" for e in errors)
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Orijinal belge:
{document}

İlk çıkarım:
{json.dumps(failed, ensure_ascii=False, indent=2)}

Doğrulama hataları:
{error_text}

Bu hataları düzelterek çıkarımı yeniden yapın."""
        }]
    )
    return json.loads(response.content[0].text)
```

---

## Retry Sayısı Sınırı

```
Önerilen: maksimum 2-3 retry
Neden: 
- Her retry = ek maliyet + gecikme
- 3 retry'dan sonra hâlâ başarısız ise sorun genellikle kaynakta
- Sonsuz retry döngüsü sistem kaynağı tüketir

Başarısız son deneme sonrası: 
- İnsan inceleme kuyruğuna ekle
- conflict_detected: true ile işaretle
- Downstream sistemi uyar
```

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Retry'da spesifik hata mesajı şart** — "yeniden dene" yeterli değil. |
| 2 | **Format hatası, yapısal hata, alan yanlışı → retry etkin.** |
| 3 | **Kaynakta bilgi yoksa retry etkin değil** — nullable alan gerekir. |
| 4 | **Çelişkili kaynak belgesi → conflict_detected flag**, insan incelemesi. |
| 5 | **calculated_total** anlamsal doğrulama için şemaya eklenir. |
| 6 | **detected_pattern** uzun vadeli prompt iyileştirme için bulgu kaydı tutar. |
| 7 | **Maks 2-3 retry** — sonra insan kuyruğu. Sonsuz döngü değil. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Fatura çıkarım sistemi `payment_terms` alanı için null dönüyor. Retry mesajı gönderildi: "payment_terms zorunlu alan, null olamaz." Hâlâ null. Doğru sonuç nedir?

**A)** Daha güçlü model kullan  
**B)** Retry sayısını artır (5-10 deneme)  
**C)** `payment_terms` alanını nullable/optional yap — bilgi belgede muhtemelen yok  
**D)** Modele ödeme koşulları hakkında örnek ver  

**✅ Cevap: C**

*Açıklama:* Model tekrar tekrar aynı belgeye bakacak. Bilgi orada yoksa retry işe yaramaz. Doğru çözüm: şemada alanı nullable yapmak — böylece model makul bir değer uydurmak yerine null döndürebilir.

---

### Soru 2

Fatura belgesi satır kalemleri toplamı olarak 800 TL gösteriyor, kapak sayfasında toplam 950 TL yazıyor. Sistem bu durumu nasıl ele almalı?

**A)** Satır toplamını doğru kabul et, 800 TL kullan  
**B)** Kapak sayfası toplamını doğru kabul et, 950 TL kullan  
**C)** conflict_detected: true ile işaretle, insan incelemesine yönlendir  
**D)** Ortalama al: 875 TL kullan  

**✅ Cevap: C**

*Açıklama:* Çelişkili kaynak veri — retry yardımcı olmaz, hangi değerin doğru olduğunu model belirleyemez. `conflict_detected: true` ile flag'lemek ve insan incelemesine yönlendirmek tek güvenli seçenek.

---

### Soru 3

`detected_pattern` alanı bir kod inceleme agent'ında ne işe yarar?

**A)** Bulgunun hangi kod yapısını tetiklediğini kaydeder; reddedilen bulgu örüntülerini analiz edip prompt'u iyileştirmeye olanak tanır  
**B)** Model'in hata ayıklama için kullandığı iç durum bilgisidir  
**C)** Retry döngüsünde hangi doğrulama hatasının oluştuğunu gösterir  
**D)** CI/CD sistemine gönderilen uyarı kodudur  

**✅ Cevap: A**

*Açıklama:* `detected_pattern` sistematik veri toplar. Geliştiricilerin sık reddeddiği kalıplar analiz edilince hangi kategorilerin kötü kalibre olduğu görülür. Bu veriyle prompt kriterleri iyileştirilir.

---

### Soru 4

Validation-retry döngüsü için kaç retry önerilir? Ve son başarısız denemeden sonra ne yapılmalı?

**A)** 1 retry — herhangi bir hata insan incelemesine gider  
**B)** 2-3 retry; başarısız olursa insan inceleme kuyruğuna ekle  
**C)** 10+ retry — model zamanla doğru cevabı üretir  
**D)** Retry sayısı sınırsız olmalı — sistem başarıya ulaşana kadar dener  

**✅ Cevap: B**

*Açıklama:* 2-3 retry maliyet-fayda dengesi açısından optimal. 3 retry'dan sonra başarısız olan belgeler genellikle kaynak sorunlu veya format tamamen bilinmiyor — insan incelemesi gerekir. Sonsuz döngü sistem kaynaklarını tüketir.
