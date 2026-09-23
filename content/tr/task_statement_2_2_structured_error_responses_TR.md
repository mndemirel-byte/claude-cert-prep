# Task Statement 2.2: Yapılandırılmış Hata Yanıtları (Structured Error Responses)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Araçlar her zaman başarılı olmaz. Timeout olur, geçersiz girdi gelir, yetki reddedilir. Mesele şu: **araç başarısız olduğunda, bunu Claude'a NASIL bildiriyorsun?**

MCP'de bunun için **`isError` flag'i** var. Araç hata döndürdüğünde bu flag'i `true` olarak işaretlersin ve yanıta yapılandırılmış hata bilgisi eklersin. Böylece Claude hatanın ne olduğunu anlayıp doğru kararı verebilir.

---

## Dört Hata Kategorisi

Bu dördünü ezberle — sınav bunları birbirinden ayırt etmeni bekliyor:

### 1. Geçici Hatalar (Transient)
Timeout, servis geçici olarak kullanılamıyor. **Tekrar denenebilir.** Biraz bekle, tekrar dene.

```json
{
  "isError": true,
  "errorCategory": "transient",
  "isRetryable": true,
  "description": "Veritabanı bağlantı zaman aşımı — 5 saniye sonra tekrar deneyin"
}
```

### 2. Doğrulama Hataları (Validation)
Geçersiz girdi — yanlış format, eksik zorunlu alan. **Girdiyi düzelt, tekrar dene.**

```json
{
  "isError": true,
  "errorCategory": "validation",
  "isRetryable": true,
  "description": "Müşteri ID sayısal olmalı — 'abc123' geçersiz format"
}
```

### 3. İş Kuralı Hataları (Business)
Politika ihlali — iade tutarı limiti aşıyor, hesap askıya alınmış. **Tekrar denenemez.** Farklı bir iş akışı gerekiyor. `retryable: false` olmalı ve müşteriye açıklanabilir bir mesaj içermeli.

```json
{
  "isError": true,
  "errorCategory": "business",
  "isRetryable": false,
  "description": "İade tutarı ($750) maksimum limiti ($500) aşıyor. Yönetici onayı gerekiyor.",
  "customerMessage": "İade talebiniz inceleme için yöneticiye iletilecektir."
}
```

### 4. Yetki Hataları (Permission)
Erişim reddedildi. Yetki yükseltme (escalation) veya farklı kimlik bilgileri gerekiyor.

```json
{
  "isError": true,
  "errorCategory": "permission",
  "isRetryable": false,
  "description": "Bu hesaba erişim yetkisi yok — yönetici seviyesi kimlik bilgileri gerekiyor"
}
```

---

## Yapılandırılmış Hata Metadata'sı

İyi bir hata yanıtı şu bileşenleri içerir:

- **`isError`** — `true` veya `false`
- **`errorCategory`** — transient / validation / business / permission
- **`isRetryable`** — boolean — tekrar denenebilir mi?
- **`description`** — insan tarafından okunabilir açıklama
- **`customerMessage`** (opsiyonel) — müşteriye iletilebilecek mesaj (özellikle business hataları için)

Claude bu yapıyı gördüğünde ne yapacağını bilir: transient ise tekrar dener, validation ise girdiyi düzeltir, business ise alternatif yol arar, permission ise yetki yükseltme başlatır.

---

## Kritik Ayrım: Erişim Hatası vs Geçerli Boş Sonuç (SINAV TUZAĞI)

Bu ayrımı kesinlikle öğren. Sınav bunu test ediyor.

### Erişim Hatası (Access Failure)
Araç veri kaynağına **ulaşamadı** — timeout, kimlik doğrulama hatası. Veri var mı yok mu bilmiyorsun. **Tekrar deneme mantıklı.**

### Geçerli Boş Sonuç (Valid Empty Result)
Araç kaynağa **başarıyla** sorgu yaptı ve eşleşme bulamadı. Veri yok. **Tekrar deneme YANLIŞ.** Cevap "sonuç bulunamadı."

Bu ikisini karıştırırsan kurtarma mantığı bozulur.

### Erişim Hatası Örneği

```json
{
  "isError": true,
  "errorCategory": "transient",
  "isRetryable": true,
  "description": "Veritabanı bağlantı zaman aşımı"
}
```

### Geçerli Boş Sonuç Örneği — BU HATA DEĞİL

```json
{
  "isError": false,
  "results": [],
  "resultCount": 0,
  "description": "Sorgu başarılı, eşleşen kayıt bulunamadı"
}
```

Fark: Boş sonuçta `isError: false` — çünkü araç başarıyla çalıştı. Sadece sonuç boş. Agent tekrar denememeli, müşteriye "kayıt bulunamadı" demeli.

---

## Çoklu Agent Sistemlerinde Hata Yayılımı

Subagent'lar hataları nasıl yönetmeli?

1. **Geçici hataları yerel olarak kurtarmalı** — kendileri tekrar denemeli
2. **Sadece yerel olarak çözemedikleri hataları** koordinatöre yaymalı
3. Yayarken şunları dahil etmeli:
   - **Kısmi sonuçlar** — başarısızlıktan önce ne elde ettiler
   - **Ne denendi** — hangi kurtarma adımları atıldı

Böylece koordinatör bilgilendirilmiş bir karar verebilir — aynı subagent'ı tekrar mı çağırsın, farklı bir subagent mı kullansın, yoksa insana mı yönlendirsin.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `isError` flag'i | MCP'de hata iletişiminin temel mekanizması |
| Dört hata kategorisi | Transient (tekrar dene), Validation (girdiyi düzelt), Business (tekrar deneme, alternatif yol), Permission (yetki yükselt) |
| Yapılandırılmış metadata | errorCategory + isRetryable + description — Claude'un doğru karar vermesi için |
| Business hataları | `isRetryable: false` + müşteri dostu mesaj — politika ihlallerinde tekrar deneme YANLIŞ |
| Erişim hatası vs boş sonuç | Erişim hatası → tekrar dene. Boş sonuç → tekrar deneme, cevap "bulunamadı" |
| Hata yayılımı | Subagent'lar yerel kurtarma yapar, çözemediklerini kısmi sonuçlarla koordinatöre yayar |

---

## Pratik Senaryo

> Bir müşteri destek agent'ı sipariş sorgulama aracını çağırıyor. Araç şu yanıtı döndürüyor:
>
> ```json
> { "results": [], "status": 200 }
> ```
>
> Agent bu yanıtı alıp 3 kez tekrar deniyor, sonra müşteriye "Sistemde bir sorun var, lütfen daha sonra tekrar deneyin" diyor.
>
> Gerçek durum: Müşterinin o numarayla eşleşen siparişi yok.
>
> **Sorun nedir ve nasıl düzeltilir?**
>
> **A)** Agent'ın retry mantığı yetersiz — retry sayısını 5'e çıkar ve bekleme süresini artır.
>
> **B)** Araç yanıtı, erişim hatası ile geçerli boş sonucu ayırt etmiyor. Agent boş diziyi hata sanıyor. Çözüm: araç yanıtına `isError: false` ve `resultCount: 0` ekleyerek başarılı boş sonucu açıkça işaretle.
>
> **C)** Agent'ın system prompt'una "boş sonuç aldığında tekrar deneme" talimatı ekle.
>
> **D)** Sipariş sorgulama aracını daha geniş kapsamlı bir araçla değiştir.

### Doğru Cevap: B

**Neden B doğru:** Sorun, aracın erişim hatası ile geçerli boş sonucu ayırt edememesi. `status: 200` başarılı bir sorguyu gösteriyor ama agent bunu anlayamıyor çünkü yanıtta açık bir `isError` flag'i yok. Çözüm: yapılandırılmış yanıt formatı ile başarılı boş sonucu (`isError: false`, `resultCount: 0`) erişim hatasından (`isError: true`, `errorCategory: transient`) açıkça ayır. Agent `isError: false` gördüğünde tekrar denemez, müşteriye "sipariş bulunamadı" der.

**Neden A yanlış:** Retry sayısını artırmak sorunu çözmez — sorun retry yetersizliği değil, başarılı boş sonucun hata sanılması. 5 kez de denese sonuç aynı: boş dizi. Çünkü sipariş gerçekten yok.

**Neden C yanlış:** Prompt talimatı olasılıksal. Asıl sorun aracın yanıt yapısında — yapısal soruna yapısal çözüm gerekir. Prompt talimatı her durumda doğru çalışmaz.

**Neden D yanlış:** Aracı değiştirmek sorunu çözmez — yeni araç da aynı belirsiz yanıt yapısını kullanırsa aynı sorun devam eder. Kök neden aracın kapsamı değil, yanıt formatı.
