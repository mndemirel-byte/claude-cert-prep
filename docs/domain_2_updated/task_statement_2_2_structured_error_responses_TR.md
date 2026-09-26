# Task Statement 2.2: Yapılandırılmış Hata Yanıtları (Structured Error Responses)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Araçlar her zaman başarılı olmaz. Timeout olur, geçersiz girdi gelir, yetki reddedilir. Mesele şu: **araç başarısız olduğunda, bunu Claude'a NASIL bildiriyorsun?**

Kötü cevap: her hata için aynı `"Error: operation failed"` metni. Buna **uniform error response** denir ve exam guide bunu açıkça anti-pattern olarak sayar — agent hatanın geçici mi, girdi kaynaklı mı, iş kuralı mı olduğunu bilemez; ya gereksiz yere tekrar dener ya da kurtarılabilir bir hatayı bırakır.

İyi cevap: **yapılandırılmış hata yanıtı** — bir hata bayrağı + hatanın kategorisi + tekrar denenebilir mi + insan tarafından okunabilir açıklama.

---

## İki Katman: Protokol Bayrağı ve Uygulama Metadata'sı

Bu ayrımı net öğren; sınav "MCP hangi alanla hata bildirir?" diye sorarsa cevap tek kelimedir: **`isError`**.

### Katman 1 — MCP'nin tanıdığı alan: `isError`

MCP `tools/call` sonucu iki alandan oluşur: `content` (içerik blokları) ve `isError` (boolean). Başka bir hata alanı yoktur.

```json
{
  "content": [
    { "type": "text", "text": "Veritabanı bağlantı zaman aşımı — 5 saniye sonra tekrar deneyin" }
  ],
  "isError": true
}
```

### Katman 2 — Senin eklediğin metadata: `errorCategory`, `isRetryable`, …

`errorCategory`, `isRetryable`, `description`, `customerMessage` **protokol alanı değildir**. Bunlar, senin `content` içindeki metne (genellikle JSON olarak) veya `structuredContent` alanına koyduğun **uygulama seviyesi** yapıdır. MCP bunları yorumlamaz; Claude okur ve karar verir.

```json
{
  "isError": true,
  "content": [
    {
      "type": "text",
      "text": "{\"errorCategory\":\"transient\",\"isRetryable\":true,\"description\":\"Veritabanı bağlantı zaman aşımı — 5 saniye sonra tekrar deneyin\"}"
    }
  ]
}
```

> Exam guide Skills maddesinde `"retriable: false"` (e ile) yazıyor; bu dokümanda `isRetryable` kullanıyoruz. Sınavda iki yazımı da tanı — kavram aynı.

### Messages API karşılığı: `is_error`

MCP kullanmadan kendi agentic loop'unu yazıyorsan (Domain 1.1), hata bildirimi `tool_result` bloğundaki **`is_error: true`** ile yapılır (snake_case):

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
  "content": "Rate limit exceeded. Retry after 60 seconds.",
  "is_error": true
}
```

Resmi kılavuz: hata metni **yönlendirici** olmalı — ne oldu + Claude şimdi ne denemeli. `"failed"` değil, `"Rate limit exceeded. Retry after 60 seconds."`

| Bağlam | Alan | Yazım |
|---|---|---|
| MCP tool result | `isError` | camelCase |
| Messages API `tool_result` | `is_error` | snake_case |
| Senin metadata'n | `errorCategory`, `isRetryable`, … | içerikte, protokol alanı değil |

---

## MCP'de Protokol Hatası vs Araç Yürütme Hatası

MCP spesifikasyonu iki ayrı hata mekanizması tanımlar:

| Tür | Nasıl döner | Ne için | Modele ulaşır mı? |
|---|---|---|---|
| **Protokol hatası** | JSON-RPC `error: { code, message }` | Bilinmeyen araç adı, şemaya uymayan argüman, sunucu çökmesi | **Hayır** — istemci katmanında kalır |
| **Araç yürütme hatası** | `result` içinde `isError: true` | API başarısızlığı, geçersiz girdi verisi, iş kuralı ihlali | **Evet** — Claude görür ve kendini düzeltebilir |

**Tasarım kuralı:** İş mantığı, API ve doğrulama hatalarını **`isError: true` ile sonuç olarak** döndür, protokol hatası olarak fırlatma. Protokol hatası modele ulaşmaz — Claude neyin yanlış gittiğini öğrenemez, girdiyi düzeltemez, alternatif yol arayamaz. `isError` tam olarak "modelin görmesi gereken hata" içindir.

---

## Dört Hata Kategorisi

Bu dördünü ezberle — sınav bunları birbirinden ayırt etmeni bekliyor:

| Kategori | Örnek | Tekrar denenebilir mi? | Agent'ın aksiyonu | Kime söylenir |
|---|---|---|---|---|
| **Transient (geçici)** | Timeout, servis geçici olarak yok, rate limit | ✅ Evet — aynı girdiyle, bekleyip | Backoff ile 2–3 retry; hâlâ başarısızsa yukarı yay | Koordinatör (kısmi sonuçla) |
| **Validation (doğrulama)** | Yanlış format, eksik zorunlu alan | ❌ Hayır (aynı girdiyle) — kurtarma: **girdiyi düzelt, yeni çağrı yap** | Girdiyi düzelt, bir kez daha çağır | Gerekirse kullanıcıdan eksik bilgi iste |
| **Business (iş kuralı)** | Limit aşımı, askıya alınmış hesap, politika ihlali | ❌ Hayır | Alternatif iş akışı (onay, escalation); müşteriye `customerMessage` ilet | Kullanıcı / müşteri |
| **Permission (yetki)** | Erişim reddedildi, kimlik bilgisi yetersiz | ❌ Hayır (aynı kimlikle) | Escalation / farklı kimlik bilgisi | Koordinatör veya insan |

### 1. Geçici Hatalar (Transient)

```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "{\"errorCategory\":\"transient\",\"isRetryable\":true,\"description\":\"Veritabanı bağlantı zaman aşımı — 5 saniye sonra tekrar deneyin\"}" }]
}
```

**Retry politikası:** üst sınır (2–3 deneme), üstel bekleme (1s → 2s → 4s), sınır aşılınca yukarı yay. Sonsuz retry sistemi kilitler; ilk hatada yayma yerel kurtarma fırsatını kaçırır.

**Timeout'un iki yüzü — sınav tuzağı:** Okuma işleminde (`lookup_order`) timeout sonrası retry güvenlidir. **Yazma** işleminde (`process_refund`, `send_email`) timeout, işlemin gerçekleşip gerçekleşmediğini belirsiz bırakır — körlemesine retry **çift iade / çift e-posta** riski taşır. Çözüm: idempotency anahtarı (aynı `request_id` ile tekrar → sunucu yinelemez) veya önce durum sorgulama. MCP **tool annotations** bu bilgiyi istemciye bildirir: `idempotentHint`, `destructiveHint`, `readOnlyHint`, `openWorldHint`. Güvenilmeyen sunucudan gelen annotation'lar "untrusted" kabul edilmelidir.

### 2. Doğrulama Hataları (Validation)

```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "{\"errorCategory\":\"validation\",\"isRetryable\":false,\"description\":\"customer_id sayısal olmalı — 'abc123' geçersiz format. Örnek: 004512\"}" }]
}
```

Konvansiyon: `isRetryable`, "**aynı istek olduğu gibi tekrarlansa** başarılı olabilir mi?" sorusunun cevabıdır. Validation için cevap hayır → `false`. Kurtarma yolu retry değil, **düzeltilmiş girdiyle yeni bir çağrıdır** — bu yüzden `description` alanı doğru formatı örneklemeli. Agent aynı hatalı girdiyle 3 kez deniyorsa sorun retry sayısı değil; agent'ın validation'ı transient sanmasıdır. (Bazı kaynaklar validation'ı "düzeltmeden sonra retryable" diye anlatır — sınavda iki çerçeveyi de tanı; kritik nokta aynı girdiyle körlemesine retry'ın yanlış olmasıdır.)

### 3. İş Kuralı Hataları (Business)

```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "{\"errorCategory\":\"business\",\"isRetryable\":false,\"description\":\"İade tutarı ($750) maksimum limiti ($500) aşıyor. Yönetici onayı gerekiyor.\",\"customerMessage\":\"İade talebiniz inceleme için yöneticiye iletilecektir.\"}" }]
}
```

`isRetryable: false` + **müşteriye iletilebilir mesaj**. Politika değişmediği sürece aynı işlem her seferinde başarısız olur; tekrar deneme yanlıştır. Agent tutarı kendi başına da değiştirmemeli — iş kararı müşteriye ait.

### 4. Yetki Hataları (Permission)

```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "{\"errorCategory\":\"permission\",\"isRetryable\":false,\"description\":\"Bu hesaba erişim yetkisi yok — yönetici seviyesi kimlik bilgileri gerekiyor\"}" }]
}
```

Yetki yükseltme (escalation) veya farklı kimlik bilgileri gerekir. Aynı kimlikle tekrar denemek anlamsızdır.

---

## Kritik Ayrım: Erişim Hatası vs Geçerli Boş Sonuç (SINAV TUZAĞI)

Bu ayrımı kesinlikle öğren. Sınav bunu test ediyor.

### Erişim Hatası (Access Failure)
Araç veri kaynağına **ulaşamadı** — timeout, kimlik doğrulama hatası. Veri var mı yok mu bilmiyorsun. **Retry kararı gerekir.**

```json
{
  "isError": true,
  "content": [{ "type": "text", "text": "{\"errorCategory\":\"transient\",\"isRetryable\":true,\"description\":\"Veritabanı bağlantı zaman aşımı\"}" }]
}
```

### Geçerli Boş Sonuç (Valid Empty Result) — BU HATA DEĞİL
Araç kaynağa **başarıyla** sorgu yaptı ve eşleşme bulamadı. Veri yok. **Tekrar deneme YANLIŞ.** Cevap "sonuç bulunamadı."

```json
{
  "isError": false,
  "content": [{ "type": "text", "text": "{\"results\":[],\"resultCount\":0,\"description\":\"Sorgu başarılı, eşleşen kayıt bulunamadı\"}" }]
}
```

Fark: Boş sonuçta `isError: false` — çünkü araç başarıyla çalıştı. Sadece sonuç boş. Agent tekrar denememeli, müşteriye "kayıt bulunamadı" demeli. Bu ikisini karıştırırsan kurtarma mantığı bozulur: ya boş sonucu 3 kez sorgularsın ya da timeout'u "veri yok" diye raporlarsın.

---

## Çoklu Agent Sistemlerinde Hata Yayılımı

Subagent'lar hataları nasıl yönetmeli? (Ayrıntı için bkz. Domain 5.3 — Error Propagation.)

1. **Geçici hataları yerel olarak kurtarmalı** — kendileri backoff ile 2–3 kez tekrar denemeli
2. **Sadece yerel olarak çözemedikleri hataları** koordinatöre yaymalı
3. Yayarken şunları dahil etmeli:
   - **Kısmi sonuçlar** — başarısızlıktan önce ne elde ettiler (atma!)
   - **Ne denendi** — hangi kurtarma adımları atıldı, kaç retry yapıldı
   - **Hata kategorisi** — koordinatör aynı ayrımı kendi kararında kullanır

Böylece koordinatör bilgilendirilmiş bir karar verebilir — aynı subagent'ı tekrar mı çağırsın, farklı bir subagent mı kullansın, yoksa insana mı yönlendirsin.

**Anti-pattern:** Hatayı sessizce yutup boş sonuç döndürmek. Koordinatör bunu "geçerli boş sonuç" olarak yorumlar — yukarıdaki tuzağın multi-agent versiyonu.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `isError` | MCP'nin **tek** hata alanı; `content` + `isError` = sonuç yapısı |
| `is_error` | Messages API `tool_result` karşılığı (snake_case) |
| Metadata | `errorCategory` + `isRetryable` + `description` (+ `customerMessage`) — `content` içinde, protokol alanı değil |
| Protokol hatası vs yürütme hatası | JSON-RPC error modele ulaşmaz; `isError: true` ulaşır → iş/API hatalarını `isError` ile döndür |
| Uniform error response | Anti-pattern: her hata aynı metin → agent doğru kurtarma kararı veremez |
| Dört kategori | Transient (backoff retry, `isRetryable: true`), Validation (aynı girdiyle retry yok — girdiyi düzelt, yeni çağrı), Business (retry yok, alternatif yol + müşteri mesajı), Permission (escalate) |
| Yazma işleminde timeout | Körlemesine retry = çift işlem riski → idempotency anahtarı / durum sorgusu; `idempotentHint`, `destructiveHint` |
| Erişim hatası vs boş sonuç | `isError: true` → retry kararı. `isError: false` + `results: []` → "bulunamadı", retry yok |
| Hata yayılımı | Subagent yerel kurtarma; çözemediğini kısmi sonuç + denenenler + kategori ile koordinatöre yayar |

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
> **B)** Araç yanıtı, erişim hatası ile geçerli boş sonucu ayırt etmiyor. Agent boş diziyi hata sanıyor. Çözüm: araç yanıtında `isError: false` ve içerikte `resultCount: 0` + "sorgu başarılı, eşleşme yok" açıklaması ile başarılı boş sonucu açıkça işaretle; gerçek erişim hatalarını `isError: true` + `errorCategory` ile ayır.
>
> **C)** Agent'ın system prompt'una "boş sonuç aldığında tekrar deneme" talimatı ekle.
>
> **D)** Sipariş sorgulama aracını daha geniş kapsamlı bir araçla değiştir.

### Doğru Cevap: B

**Neden B doğru:** Sorun, aracın erişim hatası ile geçerli boş sonucu ayırt edememesi. `status: 200` başarılı bir sorguyu gösteriyor ama agent bunu anlayamıyor çünkü yanıtta açık bir `isError` bayrağı ve "bu boşluk başarılı bir sorgunun sonucudur" bilgisi yok. Çözüm: yapılandırılmış yanıt formatı ile başarılı boş sonucu (`isError: false`, `resultCount: 0`) erişim hatasından (`isError: true`, `errorCategory: transient`) açıkça ayır. Agent `isError: false` gördüğünde tekrar denemez, müşteriye "sipariş bulunamadı" der.

**Neden A yanlış:** Retry sayısını artırmak sorunu çözmez — sorun retry yetersizliği değil, başarılı boş sonucun hata sanılması. 5 kez de denese sonuç aynı: boş dizi. Çünkü sipariş gerçekten yok.

**Neden C yanlış:** Prompt talimatı olasılıksal. Asıl sorun aracın yanıt yapısında — yapısal soruna yapısal çözüm gerekir. Ayrıca bu talimat gerçek erişim hatalarında (timeout sonrası boş dönen kötü tasarlanmış araç) retry'ı da engeller.

**Neden D yanlış:** Aracı değiştirmek sorunu çözmez — yeni araç da aynı belirsiz yanıt yapısını kullanırsa aynı sorun devam eder. Kök neden aracın kapsamı değil, yanıt formatı.
