# Task Statement 4.3: Tool_Use ile Yapılandırılmış Çıktı

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Yapılandırılmış veri çıkarmanın iki yolu var:

1. **Prompt tabanlı JSON:** "JSON formatında yanıt ver" diye talimat vermek
2. **Tool_use ile JSON şeması:** Claude'a resmi bir araç tanımlamak ve onu kullanmasını zorlamak

Bu ikisi arasındaki fark **güvenilirlik** meselesidir. Sınav sana bu farkın sınırlarını — ne işe yarar, ne yaramaz — doğru anlamanı bekler.

> **Güncel durum kutusu (sınav cevabını değiştirmez):** Exam guide "tool_use ile JSON şeması, şema-uyumlu çıktı için **en güvenilir** yaklaşım" der → sınavda doğru cevap **tool_use**. Güncel API'de yapılandırılmış çıktı için üç araç var: (a) **tool_use** (+ `strict: true` ile tam şema garantisi), (b) **structured outputs** — `output_config.format: {"type": "json_schema", "schema": …}` ile doğrudan JSON yanıt, (c) **prefill / stop-sequence** (kursun *Structured data* dersi: asistan mesajını `{` ile başlatmak) — en az güvenilir, structured outputs ile uyumsuz. Gerçek projede (b) çoğu zaman en temizi; sınavda (a).

---

## Güvenilirlik Hiyerarşisi

### Sözdizimi Güvenilirliği

```
Tool_use + JSON şeması  →  Sözdizimi hatalarını ortadan kaldırır (input her zaman parse edilebilir JSON)
Tool_use + strict: true →  + tam şema uyumu garantisi (zorunlu alanlar, tipler, enum değerleri)
Prompt tabanlı JSON     →  Model geçersiz JSON üretebilir ("İşte sonuç: {…" gibi metin karışabilir)
```

**Tool_use kullandığında `tool_use` bloğunun `input` alanı her zaman geçerli JSON'dur** — downstream sisteminiz parse hatasıyla çökmez. Bu sınavın "eliminates JSON syntax errors" ifadesidir.

**Ama dikkat:** sözdizimi garantisi ≠ şema garantisi. `strict: true` olmadan model nadiren de olsa zorunlu bir alanı atlayabilir veya enum dışı bir değer üretebilir. Resmi doküman: *"Add `strict: true` to your custom tool definitions to ensure Claude's tool calls always match your schema exactly."* Strict ile şema uyumu grammar-constrained sampling ile garanti edilir (istisna: `refusal` ve `max_tokens` ile kesilen yanıtlar).

```json
{
  "name": "extract_invoice",
  "strict": true,
  "input_schema": { "...": "..." }
}
```

### Tool_use'un Engelleyemediği Hatalar

Burası sınavın tuzak kurduğu yer. Tool_use her şeyi çözmez — **strict bile çözmez**, çünkü bunlar şema hatası değil, *anlam* hatasıdır.

```
❌ Anlamsal hatalar: Kalemler 500 + 300 = 900 diyor, ama satır toplamı 750.
   → JSON geçerli, şema doğrulandı, ama sayılar yanlış.

❌ Alan yerleştirme hataları: "Birim fiyat" değeri "toplam fiyat" alanına girmiş.
   → JSON geçerli, tüm alanlar dolu, ama değerler yanlış yerde.

❌ Uydurma (Fabrication): Kaynak belgede fiyat yok, ama model makul bir değer uyduruyor.
   → Özellikle "required" alanlar için risk yüksek.
```

**Özet:** Tool_use **sözdizimi** güvencesi verir (strict ile **şema** güvencesi). **Anlam** güvencesi vermez → Task 4.4.

---

## Tool_choice Modları — Kritik Ayrımlar

```json
"tool_choice": {"type": "auto"}
// Varsayılan (araç tanımlıysa). Model araç çağırabilir veya düz metin dönebilir.
// Belge tipi bilinmiyorsa ve metin yanıtı kabul edilebilirse kullan.

"tool_choice": {"type": "any"}
// Model MUTLAKA bir araç çağırmak zorunda. Hangisini seçeceğine o karar verir.
// Garantili yapılandırılmış çıktı istiyorsun ama belge tipi değişken → bunu kullan.

"tool_choice": {"type": "tool", "name": "extract_metadata"}
// Model MUTLAKA bu spesifik aracı çağırmak zorunda.
// Belirli bir çıkarımın (ör. metadata) zenginleştirme (enrichment) adımlarından
// ÖNCE çalışmasını garanti etmek için. Exam guide'ın örneği tam bu isimle.

"tool_choice": {"type": "none"}
// Araçlar tanımlı kalsın ama bu turda HİÇBİRİ çağrılmasın; yalnızca metin.
// Varsayılan (araç tanımlı değilse). Sınavda dördüncü şık olarak gelebilir.
```

| Mod | Araç çağrısı | Hangi araç | Araçtan önce açıklama metni üretir mi? | Extended thinking (manuel) ile |
|-----|-------------|-----------|----------------------------------------|-------------------------------|
| `auto` | isteğe bağlı | model seçer | evet | ✅ |
| `any` | zorunlu | model seçer | **hayır** | ❌ hata |
| `tool` | zorunlu | belirtilen | **hayır** | ❌ hata |
| `none` | yasak | — | evet (yalnızca metin) | ✅ |

**İki yan etki:**
- `any` ve `tool`, API'nin asistan mesajını *prefill* ederek çalışır; bu yüzden model araç çağrısından **önce doğal dilde açıklama üretmez** (istesen bile). "Hem gerekçe hem araç çağrısı istiyorum" → `auto` + kullanıcı mesajında "X aracını kullan" talimatı.
- Manuel extended thinking (`thinking: {"type": "enabled"}`) açıkken `any` ve `tool` **hata verir**; yalnızca `auto`/`none`. "Thinking + garantili yapılandırılmış çıktı" senaryosunda cevap: thinking'i kapat ya da `auto` + `strict: true`.
- `disable_parallel_tool_use: true` (`auto`/`any` ile): turda **en fazla bir** araç çağrısı. Sıralı pipeline'da (önce metadata, sonra enrichment) paralel çağrıyı kapatmak için.
- `tool_choice` değişikliği prompt cache'ini (mesaj bloklarını) geçersiz kılar.

> **Güncel not:** En yeni modellerde (Opus 5.5, Fable/Mythos 5.1) `any` ve `tool` desteklenmez (400 döner); garantili şema için `auto` + `strict: true` ya da structured outputs kullanılır. Exam guide'ın modeli `any`/`tool` üzerine kurulu; **sınav cevabı `any`**.

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

**Test et:** Hazırlık Egzersizi 3 adım 11'in son cümlesi — "*Process documents where some fields are absent and **verify** the model returns null rather than fabricating values*". Nullable yapmak yetmez; eksik alanlı belgelerden oluşan küçük bir sette null döndüğü doğrulanır (Task 4.1'deki eval seti).

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

Bu olmadan model her zaman bir değer seçer — belirsiz durumlarda bile. `"unclear"` seçeneği modele "bilmiyorum" deme izni verir. **Sonrası:** `"unclear"` gelen bulgular güven tabanlı yönlendirmeyle (Task 4.6) insan kuyruğuna gider — şema tasarımı ile yönlendirme mantığı birbirini tamamlar.

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

**Neden önemli:** Enum'u kapalı tutarsan bilinmeyen belgeler yanlış sınıflandırılır. "other" + freeform field her iki dünyayı da kapsar: yapılandırılmış sınıflandırma + esneklik. Aynı desen Task 4.4'te `conflict_detected` (boolean) + `conflict_details` (metin) olarak tekrar gelir — **"kapalı değer + açıklama alanı"** deseni.

### 4. Format Normalisation Kuralları

Şema **neyi** döndüreceğini tanımlar (tip, enum, nullable). **Nasıl normalize edileceğini** prompt söyler:

```
"Tüm tarihler YYYY-MM-DD formatında döndür.
Para birimleri ondalık olmadan tam sayı olarak: '1.250,50 TL' → 125050 (kuruş)
Telefon numaraları +90XXXXXXXXXX formatında."
```

Neden şemaya değil prompt'a? Şemanın `description` alanına ipucu yazabilirsin (yukarıdaki örnekte yazıyor), ama şema *dönüşüm* kuralını **zorlayamaz**: `pattern` (regex), `minimum`/`maximum`, `minLength` gibi kısıtlar structured outputs'ta desteklenmez ve SDK tarafından description'a taşınır. Exam guide'ın cümlesi: "*format normalization rules in prompts **alongside** strict output schemas*". Kural: **şema neyi, prompt nasıl.**

---

## Tam Şema Örneği: Fatura Çıkarımı

```json
{
  "name": "extract_invoice_data",
  "description": "Fatura belgesinden yapılandırılmış veri çıkar",
  "strict": true,
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
          "required": ["description", "unit_price", "quantity", "total"],
          "additionalProperties": false
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
    "required": ["invoice_number", "vendor_name"],
    "additionalProperties": false
  }
}
```

**Strict ile notlar:** `strict: true` isteğe bağlı (required dışı) alanlara izin verir (istek başına toplam 24 isteğe bağlı parametre, 20 strict araç sınırı); `additionalProperties` otomatik olarak `false` yapılır; `pattern`, `minimum`/`maximum`, `minLength` gibi kısıtlar desteklenmez (SDK bunları description'a taşır). "Alan yok" durumunu **açıkça** görmek istiyorsan alanı required tutup tipini nullable yap (`["string", "null"]`) — böylece model alanı *atlamak* yerine bilinçli olarak `null` yazar; downstream "eksik anahtar" ile "null" arasında ayrım yapmak zorunda kalmaz.

---

## Sınav Tuzakları

### Tuzak 1: "Tool_use her şeyi çözer"

*"Validation sorunlarını çözmek için tool_use ekledik."*

Hayır. Tool_use **sözdizimi** sorunlarını çözer (strict ile şema sorunlarını). Anlamsal sorunlar (yanlış toplam, yanlış alan) için validation-retry loop gerekir.

### Tuzak 2: "Required alanlar halüsinasyonu önler"

*"Hiçbir alanı null yapmamalıyız, böylece eksik veri olmaz."*

Tam tersi. Tüm alanları required yaparsanız, model eksik bilgi için değer uydurmak zorunda kalır. Optional/nullable alanlar fabrication'ı önler.

### Tuzak 3: "`auto` ile garantili çıktı alınır"

Hayır. `auto` ile model metin yanıtı da döndürebilir. Garantili yapılandırılmış çıktı için `any` veya spesifik araç zorunluluğu.

### Tuzak 4: "Thinking'i açarsak çıkarım daha doğru olur — `any` ile birlikte"

Manuel extended thinking + `any`/`tool` → hata. İkisinden birini seç; garantili şema için `auto` + `strict`.

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Tool_use sözdizimi hatalarını ortadan kaldırır** — `input` her zaman geçerli JSON. Tam şema garantisi için **`strict: true`**. |
| 2 | **Tool_use anlamsal hataları, alan yanlışlarını, uydurmaları engellemez** — strict bile. → 4.4. |
| 3 | **`auto`:** metin veya araç. **`any`:** mutlaka araç. **`tool`:** mutlaka o araç (ör. `extract_metadata` → enrichment'tan önce). **`none`:** araç yok. `any`/`tool` açıklama metni üretmez, manuel thinking ile çalışmaz. |
| 4 | **Optional/nullable alanlar uydurmaları önler** — required değil. Strict'te "isteğe bağlı" = nullable. Null döndüğünü **test et**. |
| 5 | **`"unclear"` enum değeri** modele "bilmiyorum" deme izni verir → 4.6 yönlendirmesine gider. |
| 6 | **`"other"` + freeform field** bilinmeyen kategoriler için şemayı genişletir ("kapalı değer + açıklama" deseni). |
| 7 | **Şema neyi, prompt nasıl:** format normalizasyon kuralları prompt'a yazılır; şema dönüşüm kuralı zorlayamaz. |
| 8 | **Güncel:** structured outputs (`output_config.format`) ve `strict` var; sınav cevabı yine tool_use. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Tool_use ile JSON şeması kullanmak hangi sorunu kesinlikle çözer?

**A)** Model değer uydurmaz  
**B)** JSON her zaman sözdizimsel olarak geçerli olur  
**C)** Alanlar her zaman doğru değeri taşır  
**D)** Extraction kalitesi garanti altına alınır  

**✅ Cevap: B**

*Açıklama:* Tool_use yalnızca sözdizimi güvencesi sağlar. Model JSON'ı bozuk üretemez. Ama uydurma (A), yanlış alan değeri (C) ve genel kalite (D) hâlâ sorun olabilir — `strict: true` bile yalnızca *şema* uyumunu ekler, anlamı değil.

---

### Soru 2

Farklı yapılarda belgeler geliyor (fatura, sözleşme, makbuz). Belge tipine göre farklı araçlar tanımlandı. Hangi tool_choice doğru?

**A)** `"auto"` — model en uygun aracı seçer, yapılandırılmış çıktı garantisi yok  
**B)** `"any"` — model mutlaka bir araç çağırır, hangisini seçeceğine o karar verir  
**C)** `{"type": "tool", "name": "extract_invoice"}` — her belge için fatura aracını zorla  
**D)** `"none"` — araçları tanımlı tut, model metinle sınıflandırsın, sonra ikinci çağrıda çıkar  

**✅ Cevap: B**

*Açıklama:* `"any"` garantili yapılandırılmış çıktı sağlar ve model belge tipine göre en uygun aracı seçer. `"auto"` (A) metin yanıtı dönebilir. Spesifik araç (C) tüm belgeleri fatura olarak ele alır. `"none"` (D) bu turda hiç araç çağırtmaz — iki çağrı, gereksiz maliyet ve ilk çağrıda yapılandırılmamış çıktı.

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

*Açıklama:* Model şemaya uymak zorunda olduğu için bilinmeyen türü mevcut kategorilere zorla eşler. Çözüm: `"other"` enum değeri + `document_type_detail` nullable field eklemek. (C) `strict: true` ile imkânsızdır; strict olmadan teorik olarak mümkün ama nadirdir — sınav cevabı yine B, çünkü sorun şemanın *tasarımı*dır.

---

### Soru 5

Bir pipeline önce belgenin metadata'sını (tür, dil, sayfa sayısı) çıkarmalı, sonra bu metadata'ya göre farklı zenginleştirme araçları çalıştırmalı. İlk adımın her zaman `extract_metadata` aracıyla yapılmasını nasıl garanti edersin?

**A)** `tool_choice: {"type": "any"}` — model metadata aracını seçer  
**B)** `tool_choice: {"type": "tool", "name": "extract_metadata"}` — ilk çağrıda bu araç zorlanır; sonraki çağrılarda `auto`  
**C)** System prompt'a "önce metadata çıkar" yaz, `tool_choice: auto`  
**D)** Tüm araçları tek araçta birleştir  

**✅ Cevap: B**

*Açıklama:* Exam guide'ın Skills maddesi: "*Forcing a specific tool with `tool_choice: {"type": "tool", "name": "extract_metadata"}` to ensure a particular extraction runs before enrichment steps*". `any` (A) araç çağrısını garanti eder ama *hangi* aracı değil — model doğrudan bir enrichment aracına atlayabilir. Prompt talimatı (C) olasılıksaldır. (D) şemaları şişirir ve sıralamayı yine garanti etmez. Sıralı akışta `disable_parallel_tool_use: true` de eklenir.
