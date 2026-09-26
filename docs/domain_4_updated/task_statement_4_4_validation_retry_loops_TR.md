# Task Statement 4.4: Validation-Retry Döngüleri

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

İlk çıkarım her zaman mükemmel olmaz. Validation-retry, şu soruyu sorar: **"Hata geri gönderilebilir ve model kendini düzeltebilir mi?"**

Cevap duruma göre değişir. Ve sınav tam olarak bu ayrımı bilip bilmediğini test eder.

**Retry'ın alanı:** Task 4.3'te gördüğün gibi tool_use (özellikle `strict: true`) şema-sözdizimi hatalarını sıfırlar. Geriye kalan hatalar **anlamsal**dır — toplam tutmuyor, değer yanlış alanda, format beklenen gibi değil. Exam guide'ın ayrımı: "*semantic validation errors (values don't sum, wrong field placement) vs schema syntax errors (eliminated by tool use)*". Retry döngüsü yalnızca birinci grup için vardır.

---

## Retry-with-Error-Feedback Mimarisi

### Temel Akış

```
1. Belge gönderilir → İlk çıkarım alınır (tool_use)
2. Çıkarım validate edilir (şema/tip + anlamsal kurallar)
3. Hata varsa → Hata mesajıyla birlikte modele geri gönderilir
4. Model orijinal belgeyi + başarısız çıkarımı + hatayı görür
5. Model kendini düzeltir → Yeni çıkarım
6. Tekrar validate
```

### Retry İsteğinin İçeriği

Exam guide'ın Skills maddesi: "*follow-up requests that include **the original document, the failed extraction, and specific validation errors***". Üçü de gerekir:

```
Orijinal belge:        {original_document}
İlk çıkarım girişiniz: {failed_extraction}
Doğrulama hatası:      {validation_error}   ← alan adı + beklenen + bulunan
Lütfen hatayı dikkate alarak çıkarımı düzeltin.
```

**Kritik:** Modele sadece "yeniden dene" demek yetmez. **Spesifik, model tarafından okunabilir hata mesajı** gerekir — hangi alan, ne bekleniyordu, ne geldi. Model ne yanlış yaptığını bilmeden düzeltemez.

**Doğal biçim:** tool_use kullandığında retry, ayrı bir prompt değil **çok turlu bir konuşma**dır: asistanın `tool_use` bloğu geçmişte kalır, sen `tool_result` içinde hata mesajını gönderirsin, model aynı aracı düzeltilmiş `input` ile yeniden çağırır (kursun *Sending tool results* dersi).

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

### ❌ Etkin Değil (ama farklı çözüm): Bilgi Harici Bir Belgede

Exam guide'ın kendi örneği: "*information exists only in an **external document not provided***" — ödeme koşulları çerçeve sözleşmede, indirim oranı önceki faturada, birim fiyat fiyat listesinde.

```
Hata: "payment_terms null"
Gerçek: Faturada "ödeme koşulları: bkz. sözleşme No. 2024-17" yazıyor.

Model ne yapar: Retry → yine null (sözleşme elinde değil).

Doğru çözüm: nullable DEĞİL — eksik belgeyi bağlama ekle
(sözleşmeyi de gönder), SONRA retry. Retry ancak bilgi bağlamda
olduğunda işe yarar.
```

Teşhis ipucu: model null döndürüyor **ve** belgede başka bir belgeye referans var → "belge yok" değil, "belge eksik". İlkinin cevabı nullable, ikincisinin cevabı bağlam.

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

### Teşhis tablosu

| Belirti | Bilgi nerede? | Retry? | Doğru araç |
|---------|---------------|--------|------------|
| Yanlış format / yanlış alan / sayım hatası | Belgede | ✅ | Hata mesajlı retry |
| Null, belgede hiç yok | Hiçbir yerde | ❌ | Nullable alan (4.3) |
| Null, belge başka belgeye atıf yapıyor | Harici belgede | ❌ (önce) | Belgeyi ekle → sonra retry |
| Null, bilgi belgede var ama farklı formatta | Belgede | ⚠️ kısmen | Few-shot (4.2) — retry her seferinde aynı hatayı yapar |
| İki değer çelişiyor | Belge tutarsız | ❌ | `conflict_detected` → insan |

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

`calculated_total` alanını şemaya ekle — model her satırı toplayarak doldurur. Sonra backend'de `stated_total == calculated_total` kontrol edersin. Uyuşmazlık → retry veya flag. (Backend'de toplamı *kendin de* hesapla — modelin `calculated_total`'ı da yanlış olabilir; iki bağımsız hesap birbirini denetler.)

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

Bu flag ile sistem otomatik olarak insan incelemesine yönlendirebilir. `conflict_detected` (kapalı değer) + `conflict_details` (açıklama) — Task 4.3'teki `"other"` + detay alanıyla aynı **"kapalı değer + açıklama" deseni**.

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

**Sistematik veri → Sistematik iyileştirme.** Döngü şöyle kapanır:

```
detected_pattern verisi: "f-string SQL" kalıbı %70 reddediliyor
   → İncele: reddedilenlerin çoğu test dosyalarındaki sabit sorgular
   → Task 4.1: kriteri netleştir ("test dizinindeki sabit sorgular → atla")
   → Task 4.2: o kalıbı "kabul edilebilir" gösteren bir few-shot örneği ekle
   → Task 4.1 eval seti: yanlış pozitif oranını yeniden ölç
```

`detected_pattern` (4.4) ve `confidence_reason` (4.6) Domain 4'ün *geri besleme* alanlarıdır; ikisi de 4.1/4.2'ye geri döner.

---

## Self-Correction Flow — Tam Örnek

Tool_use'lu, Pydantic doğrulamalı, hata mesajlı, 2 retry'lı ve "harici belge" dalı olan tek akış (Hazırlık Egzersizi 3, adım 11–12'nin çözümü):

```python
import anthropic
from datetime import datetime
from pydantic import BaseModel, ValidationError, model_validator

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5"

# --- 1. Araç şeması (Task 4.3) ---
EXTRACT_TOOL = {
    "name": "extract_invoice_data",
    "description": "Fatura belgesinden yapılandırılmış veri çıkar",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "invoice_date": {"type": ["string", "null"], "description": "YYYY-MM-DD; yoksa null"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "line_total": {"type": ["number", "null"]},
                    },
                    "required": ["description", "line_total"],
                    "additionalProperties": False,
                },
            },
            "stated_total": {"type": ["number", "null"]},
            "calculated_total": {"type": ["number", "null"]},
            "conflict_detected": {"type": "boolean"},
            "conflict_details": {"type": ["string", "null"]},
            "references_external_document": {"type": ["string", "null"],
                "description": "Belge başka bir belgeye atıf yapıyorsa (sözleşme no vb.) onu yaz"},
        },
        "required": ["invoice_number", "invoice_date", "line_items", "stated_total",
                     "calculated_total", "conflict_detected", "conflict_details",
                     "references_external_document"],
        "additionalProperties": False,
    },
}

# --- 2. Doğrulama: şema/tip + anlamsal kurallar tek yerde (Pydantic) ---
class LineItem(BaseModel):
    description: str
    line_total: float | None

class Invoice(BaseModel):
    invoice_number: str
    invoice_date: str | None
    line_items: list[LineItem]
    stated_total: float | None
    calculated_total: float | None
    conflict_detected: bool
    conflict_details: str | None
    references_external_document: str | None

    @model_validator(mode="after")
    def semantic_checks(self):
        if self.invoice_date:
            try:
                datetime.strptime(self.invoice_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"invoice_date '{self.invoice_date}' YYYY-MM-DD formatında değil")
        totals = [i.line_total for i in self.line_items if i.line_total is not None]
        if totals and self.stated_total is not None:
            backend_sum = sum(totals)               # bağımsız hesap
            if abs(backend_sum - self.stated_total) > 0.01 and not self.conflict_detected:
                raise ValueError(
                    f"Toplam uyuşmazlığı: satırlar {backend_sum}, stated_total {self.stated_total}. "
                    "Ya bir satır/toplam yanlış okundu (düzelt) ya da belge çelişkili "
                    "(conflict_detected=true ve conflict_details doldur)."
                )
        return self

# --- 3. Çağrı + retry döngüsü ---
def extract_with_retry(document: str, max_retries: int = 2) -> dict:
    messages = [{"role": "user", "content": f"Aşağıdaki faturadan veri çıkar.\n\n<document>\n{document}\n</document>"}]

    for attempt in range(max_retries + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            tools=[EXTRACT_TOOL],
            tool_choice={"type": "tool", "name": "extract_invoice_data"},  # sınav: zorunlu araç
            messages=messages,
        )
        tool_block = next(b for b in response.content if b.type == "tool_use")
        extraction = tool_block.input

        try:
            invoice = Invoice.model_validate(extraction)
        except ValidationError as e:
            errors = "\n".join(f"- {err['loc']}: {err['msg']}" for err in e.errors())
        else:
            # Geçerli — ama retry'ın çözemeyeceği durumları ayır
            if invoice.conflict_detected:
                return {"status": "human_review", "reason": invoice.conflict_details, "data": extraction}
            if invoice.references_external_document and invoice.stated_total is None:
                return {"status": "needs_document", "document": invoice.references_external_document,
                        "data": extraction}          # retry değil: eksik belgeyi ekle, sonra tekrar çağır
            return {"status": "ok", "data": extraction}

        if attempt == max_retries:
            break

        # Retry: aynı konuşmada tool_use bloğu + hata içeren tool_result
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_block.id,
            "is_error": True,
            "content": (
                "Çıkarım doğrulamadan geçmedi. Orijinal belgeye yeniden bak ve "
                f"yalnızca aşağıdaki hataları düzelterek aracı tekrar çağır:\n{errors}"
            ),
        }]})

    return {"status": "human_review", "reason": f"{max_retries} retry sonrası hâlâ geçersiz:\n{errors}",
            "data": extraction}
```

Akışın üç çıkışı var ve sınav üçünü de ayırt etmeni ister: **`ok`** (retry çözdü ya da ilk seferde doğru), **`needs_document`** (retry değil, bağlam), **`human_review`** (belge çelişkili ya da retry bütçesi bitti).

---

## Retry Sayısı Sınırı

```
Önerilen: maksimum 2-3 retry

Asıl neden — TEŞHİS:
- Retry yalnızca "bilgi belgede var" hatalarını çözer (format, alan, sayım)
- 2-3 retry sonrası hâlâ başarısızsa hata bu sınıfta değildir:
  bilgi yok / harici belgede / belge çelişkili → daha fazla retry çözmez
- Sınır, "bu belge retry'ın işi değil" kararının verildiği noktadır

İkincil neden — MALİYET:
- Her retry = ek çağrı + gecikme
- Sonsuz döngü kaynak tüketir

Başarısız son deneme sonrası: 
- İnsan inceleme kuyruğuna ekle
- conflict_detected: true ile işaretle
- Downstream sistemi uyar
```

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Retry'da spesifik hata mesajı şart** — "yeniden dene" yeterli değil. Belge + başarısız çıkarım + hata, üçü birlikte (tool_use'ta `tool_result` ile). |
| 2 | **Format hatası, yapısal hata, alan yanlışı → retry etkin.** Şema-sözdizimi hataları zaten tool_use ile sıfırlanır; retry anlamsal hatalar içindir. |
| 3 | **Kaynakta bilgi yoksa retry etkin değil** — nullable alan gerekir. **Bilgi harici belgedeyse** → belgeyi ekle, sonra retry. |
| 4 | **Çelişkili kaynak belgesi → conflict_detected flag**, insan incelemesi. |
| 5 | **calculated_total** anlamsal doğrulama için şemaya eklenir; backend kendi hesabıyla çapraz kontrol eder. |
| 6 | **detected_pattern** bulgu kaydı tutar → reddedilen kalıplar 4.1 kriterine / 4.2 örneğine geri döner. |
| 7 | **Maks 2-3 retry** — sınır teşhis içindir ("bu hata retry'ın sınıfında değil"); sonra insan kuyruğu. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Fatura çıkarım sistemi `payment_terms` alanı için null dönüyor. Retry mesajı gönderildi: "payment_terms zorunlu alan, null olamaz." Hâlâ null. Faturanın altında *"Ödeme koşulları için bkz. Çerçeve Sözleşme 2024-17"* yazıyor. Doğru sonuç nedir?

**A)** Daha güçlü model kullan  
**B)** `payment_terms` alanını nullable yap — bilgi belgede yok  
**C)** Çerçeve sözleşmeyi bağlama ekleyip çıkarımı yeniden çalıştır; retry ancak bilgi bağlamda olunca işe yarar  
**D)** Modele ödeme koşulları hakkında few-shot örneği ver  

**✅ Cevap: C**

*Açıklama:* Bilgi *var* ama **harici bir belgede** — exam guide'ın "information exists only in an external document not provided" senaryosu. Retry aynı belgeye bakar, yine null. (B) belge hiç atıf yapmasaydı doğru olurdu; burada bilgi ulaşılabilir, atlamak veri kaybıdır. (A) ve (D) modelin elinde olmayan bilgiyi bulmasını bekler.

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

*Açıklama:* `detected_pattern` sistematik veri toplar. Geliştiricilerin sık reddeddiği kalıplar analiz edilince hangi kategorilerin kötü kalibre olduğu görülür. Bu veriyle prompt kriterleri (4.1) ve few-shot örnekleri (4.2) iyileştirilir.

---

### Soru 4

Validation-retry döngüsü için kaç retry önerilir? Ve son başarısız denemeden sonra ne yapılmalı?

**A)** 1 retry — herhangi bir hata insan incelemesine gider  
**B)** 2-3 retry; başarısız olursa insan inceleme kuyruğuna ekle  
**C)** 10+ retry — model zamanla doğru cevabı üretir  
**D)** Retry sayısı sınırsız olmalı — sistem başarıya ulaşana kadar dener  

**✅ Cevap: B**

*Açıklama:* 2-3 retry, retry'ın çözebileceği hata sınıfı (format/alan/sayım) için yeterlidir; sonrasında hâlâ başarısızsa sorun bu sınıfta değildir (bilgi yok, harici belge, çelişkili belge) — insan incelemesi gerekir. Sonsuz döngü hem bunu maskeler hem kaynak tüketir.

---

### Soru 5

Bir çıkarım sistemi `strict: true` tool_use'a geçti; şema hataları sıfırlandı. Ekip "artık validation-retry döngüsüne gerek kalmadı" diyor. Doğru mu?

**A)** Evet — strict şema uyumunu garanti eder, doğrulama gereksizdir  
**B)** Hayır — strict yalnızca şema/sözdizimi hatalarını kaldırır; toplam uyuşmazlığı, yanlış alana yerleştirme gibi anlamsal hatalar için doğrulama ve retry hâlâ gerekir  
**C)** Hayır — strict modda retry daha da önemlidir çünkü model daha çok hata yapar  
**D)** Evet — anlamsal hatalar için few-shot yeterlidir  

**✅ Cevap: B**

*Açıklama:* Exam guide'ın ayrımı: schema syntax errors (tool use ile giderilir) vs semantic validation errors (giderilmez). Strict, retry'ın *kapsamını daraltır* — artık yalnızca anlamsal hatalar kalır — ama kaldırmaz. (C) strict hata oranını artırmaz. (D) few-shot tutarlılık sağlar, hesaplama doğruluğu garanti etmez.
