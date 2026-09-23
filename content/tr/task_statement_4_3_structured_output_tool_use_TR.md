# Task Statement 4.3: Tool_Use ile Yapılandırılmış Çıktı

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Yapılandırılmış veri çıkarmanın iki yolu var:

1. **Prompt tabanlı JSON:** "JSON formatında yanıt ver" diye talimat vermek
2. **Tool_use ile JSON şeması:** Claude'a resmi bir araç tanımlamak ve onu kullanmasını zorlamak

Bu ikisi arasındaki fark **güvenilirlik** meselesidir. Sınav sana bu farkın sınırlarını — ne işe yarar, ne yaramaz — doğru anlamanı bekler.

---

## Güvenilirlik Hiyerarşisi

### Sözdizimi Güvenilirliği

```
Tool_use + JSON şeması  →  Sözdizimi hatalarını TAMAMEN ortadan kaldırır
Prompt tabanlı JSON     →  Model geçersiz JSON üretebilir
```

**Tool_use kullandığında Claude geçersiz JSON üretemez** — şema buna izin vermez. Bu, downstream sisteminizin parse hatasıyla çökmeyeceği anlamına gelir.

### Tool_use'un Engelleyemediği Hatalar

Burası sınavın tuzak kurduğu yer. Tool_use her şeyi çözmez.

```
❌ Anlamsal hatalar: Kalemler 500 + 300 = 900 diyor, ama satır toplamı 750.
   → JSON geçerli, şema doğrulandı, ama sayılar yanlış.

❌ Alan yerleştirme hataları: "Birim fiyat" değeri "toplam fiyat" alanına girmiş.
   → JSON geçerli, tüm alanlar dolu, ama değerler yanlış yerde.

❌ Uydurma (Fabrication): Kaynak belgede fiyat yok, ama model makul bir değer uyduruyor.
   → Özellikle "required" alanlar için risk yüksek.
```

**Özet:** Tool_use **sözdizimi** güvencesi verir. **Anlam** güvencesi vermez.

---

## Tool_choice Modları — Kritik Ayrımlar

```json
"tool_choice": "auto"
// Varsayılan. Model araç çağırabilir veya düz metin dönebilir.
// Belge tipi bilinmiyorsa ve metin yanıtı kabul edilebilirse kullan.

"tool_choice": "any"
// Model MUTLAKA bir araç çağırmak zorunda. Hangisini seçeceğine o karar verir.
// Garantili yapılandırılmış çıktı istiyorsun ama belge tipi değişken → bunu kullan.

"tool_choice": {"type": "tool", "name": "extract_invoice"}
// Model MUTLAKA bu spesifik aracı çağırmak zorunda.
// Zorunlu ilk adım veya belirli şema gerektiren durumlarda kullan.
```

### Sınavın Favori Sorusu

> *"Bilinmeyen formatlarda belgeler geliyor. Garantili yapılandırılmış çıktı lazım. Hangi tool_choice?"*

**Cevap: `"any"`** — Model hangi aracı kullanacağını seçer ama MUTLAKA bir araç çağırır.

---

## Şema Tasarımı — Uydurma Önleme

Bu, sınavın en detaylı beklentisi. İyi bir şema üç şeyi içerir:

### 1. Optional/Nullable Alanlar

```json
{
  "name": "extract_invoice",
  "input_schema": {
    "type": "object",
    "properties": {
      "invoice_number": {
        "type": "string",
        "description": "Fatura numarası"
      },
      "payment_due_date": {
        "type": ["string", "null"],
        "description": "Ödeme vadesi. Belgede yoksa null döndür."
      },
      "discount_rate": {
        "type": ["number", "null"],
        "description": "İndirim oranı. Belirtilmemişse null döndür."
      }
    },
    "required": ["invoice_number"]
  }
}
```

**Neden önemli:** `payment_due_date` required olsaydı, belgede olmadığında model uydururdu. Nullable yaparak "null döndür" seçeneği sunulur.

### 2. Belirsiz Durumlar için "unclear" Enum Değeri

```json
{
  "severity": {
    "type": "string",
    "enum": ["critical", "major", "minor", "unclear"],
    "description": "Mevcut bilgilerle belirlenemiyor ise 'unclear' kullan."
  }
}
```

Bu olmadan model her zaman bir değer seçer — belirsiz durumlarda bile. `"unclear"` seçeneği modele "bilmiyorum" deme izni verir.

### 3. "other" + Serbest Metin — Genişletilebilir Sınıflandırma

```json
{
  "document_type": {
    "type": "string",
    "enum": ["invoice", "receipt", "contract", "other"]
  },
  "document_type_detail": {
    "type": ["string", "null"],
    "description": "document_type 'other' ise açıkla. Aksi halde null."
  }
}
```

**Neden önemli:** Enum'u kapalı tutarsan bilinmeyen belgeler yanlış sınıflandırılır. "other" + freeform field her iki dünyayı da kapsar: yapılandırılmış sınıflandırma + esneklik.

### 4. Format Normalisation Kuralları

Şemaya ek olarak prompt'ta format kuralları belirle:

```
"Tüm tarihler YYYY-MM-DD formatında döndür.
Para birimleri ondalık olmadan tam sayı olarak: '1.250,50 TL' → 125050 (kuruş)
Telefon numaraları +90XXXXXXXXXX formatında."
```

Bu kurallar şemaya yazılamaz — ama tutarlılık için zorunlu.

---

## Tam Şema Örneği: Fatura Çıkarımı

```json
{
  "name": "extract_invoice_data",
  "description": "Fatura belgesinden yapılandırılmış veri çıkar",
  "input_schema": {
    "type": "object",
    "properties": {
      "invoice_number": {
        "type": "string",
        "description": "Fatura numarası veya referans kodu"
      },
      "invoice_date": {
        "type": ["string", "null"],
        "description": "Fatura tarihi, YYYY-MM-DD formatında. Yoksa null."
      },
      "vendor_name": {
        "type": "string",
        "description": "Satıcı/tedarikçi adı"
      },
      "total_amount": {
        "type": ["number", "null"],
        "description": "Toplam tutar kuruş cinsinden. Çıkarılamazsa null."
      },
      "line_items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "description": {"type": "string"},
            "unit_price": {"type": ["number", "null"]},
            "quantity": {"type": ["number", "null"]},
            "total": {"type": ["number", "null"]}
          },
          "required": ["description"]
        }
      },
      "currency": {
        "type": "string",
        "enum": ["TRY", "USD", "EUR", "other"],
        "description": "Para birimi. Bilinmiyorsa 'other'."
      },
      "extraction_confidence": {
        "type": "string",
        "enum": ["high", "medium", "low"],
        "description": "Çıkarım kalitesine dair model değerlendirmesi"
      }
    },
    "required": ["invoice_number", "vendor_name"]
  }
}
```

---

## Sınav Tuzakları

### Tuzak 1: "Tool_use her şeyi çözer"

*"Validation sorunlarını çözmek için tool_use ekledik."*

Hayır. Tool_use **sözdizimi** sorunlarını çözer. Anlamsal sorunlar (yanlış toplam, yanlış alan) için validation-retry loop gerekir.

### Tuzak 2: "Required alanlar halüsinasyonu önler"

*"Hiçbir alanı null yapmamalıyız, böylece eksik veri olmaz."*

Tam tersi. Tüm alanları required yaparsanız, model eksik bilgi için değer uydurmak zorunda kalır. Optional/nullable alanlar fabrication'ı önler.

### Tuzak 3: "`auto` ile garantili çıktı alınır"

Hayır. `auto` ile model metin yanıtı da döndürebilir. Garantili yapılandırılmış çıktı için `any` veya spesifik araç zorunluluğu.

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Tool_use sözdizimi hatalarını ortadan kaldırır** — JSON her zaman geçerli olur. |
| 2 | **Tool_use anlamsal hataları, alan yanlışlarını, uydurmaları engellemez.** |
| 3 | **`auto`:** model metin veya araç seçer. **`any`:** mutlaka araç. **Spesifik:** mutlaka o araç. |
| 4 | **Optional/nullable alanlar uydurmaları önler** — required değil. |
| 5 | **`"unclear"` enum değeri** modele "bilmiyorum" deme izni verir. |
| 6 | **`"other"` + freeform field** bilinmeyen kategoriler için şemayı genişletir. |
| 7 | **Format normalisation kuralları** şemaya değil, prompt'a yazılır. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Tool_use ile JSON şeması kullanmak hangi sorunu kesinlikle çözer?

**A)** Model değer uydurmaz  
**B)** JSON her zaman sözdizimsel olarak geçerli olur  
**C)** Alanlar her zaman doğru değeri taşır  
**D)** Extraction kalitesi garanti altına alınır  

**✅ Cevap: B**

*Açıklama:* Tool_use yalnızca sözdizimi güvencesi sağlar. Model JSON'ı bozuk üretemez. Ama uydurma (A), yanlış alan değeri (C) ve genel kalite (D) hâlâ sorun olabilir.

---

### Soru 2

Farklı yapılarda belgeler geliyor (fatura, sözleşme, makbuz). Belge tipine göre farklı araçlar tanımlandı. Hangi tool_choice doğru?

**A)** `"auto"` — model en uygun aracı seçer, yapılandırılmış çıktı garantisi yok  
**B)** `"any"` — model mutlaka bir araç çağırır, hangisini seçeceğine o karar verir  
**C)** `{"type": "tool", "name": "extract_invoice"}` — her belge için fatura aracını zorla  
**D)** Her belge tipi için ayrı API çağrısı yap  

**✅ Cevap: B**

*Açıklama:* `"any"` garantili yapılandırılmış çıktı sağlar ve model belge tipine göre en uygun aracı seçer. `"auto"` (A) metin yanıtı dönebilir. Spesifik araç (C) tüm belgeleri fatura olarak ele alır.

---

### Soru 3

Fatura çıkarım şemasında `payment_due_date` alanı zorunlu (`required`) yapıldı. Tarih içermeyen faturalar işlendiğinde ne olur?

**A)** Model "null" döndürür, bu güvenlidir  
**B)** Model schema hatasıyla başarısız olur  
**C)** Model makul bir tarih uydurabilir  
**D)** Model boş string döndürür  

**✅ Cevap: C**

*Açıklama:* Required alan olduğunda ve kaynak belgede bilgi yoksa model "zorunlu alana bir şey koymalıyım" düşüncesiyle değer uydurur. Bu yanlış veri üretimi — downstream sistemleri etkiler. Çözüm: `"type": ["string", "null"]` ile nullable yapmak.

---

### Soru 4

Bir şemada belge türü için `"enum": ["invoice", "receipt", "contract"]` tanımlandı. Yeni bir belge türüyle (lease agreement) karşılaşıldığında ne olur?

**A)** Model hata döndürür ve işlemi durdurur  
**B)** Model en yakın mevcut kategoriye ("contract") atar — potansiyel yanlış sınıflandırma  
**C)** Model schema dışı bir değer döndürür  
**D)** Model belgeyi işlemeyi reddeder  

**✅ Cevap: B**

*Açıklama:* Model şemaya uymak zorunda olduğu için bilinmeyen türü mevcut kategorilere zorla eşler. Çözüm: `"other"` enum değeri + `document_type_detail` nullable field eklemek.
