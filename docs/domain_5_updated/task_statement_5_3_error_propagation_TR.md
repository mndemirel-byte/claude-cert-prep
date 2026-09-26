# Task Statement 5.3: Hata Yayılımı (Error Propagation)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Multi-agent sistemlerde ve veri çıkarım pipeline'larında hatalar kaçınılmazdır. Bir araç zaman aşımına uğrar, bir API erişim reddeder, bir veri kaynağı sonuç döndürmez. Kritik soru: **hata oluştuğunda ne yaparsın — ve kim yapar?**

Bu task statement, hataların iki katmanda nasıl ele alınacağını (subagent yerel kurtarma → koordinatöre yapılandırılmış yayma), üç anti-pattern'ı ve erişim hatası ile geçerli boş sonuç arasındaki farkı öğretir.

Sınav senaryosu: **Multi-Agent Research System** (koordinatör + web search / document analysis / synthesis / report subagent'ları). Resmi örnek soru Q8 tam bu statement'tan.

---

## İki Katmanlı Kurtarma — Kim Neyi Kurtarır?

Exam guide'ın Skills maddesi: *"Having subagents implement **local recovery for transient failures** and only propagate errors they cannot resolve, including what was attempted and partial results"*.

| Katman | Kim | Ne yapar | Ne yapmaz |
|---|---|---|---|
| **1. Yerel kurtarma** | Subagent (veya araç sarmalayıcısı) | Transient hatayı **sınırlı** sayıda retry / backoff ile kendi içinde çözmeye çalışır; alternatif kaynak dener | Sonsuz retry yapmaz; hatayı gizlemez |
| **2. Yapılandırılmış yayma** | Subagent → Koordinatör | Çözemediğini **dört alanlı** bağlamla yukarı iletir: hata türü, ne denendi, kısmi sonuçlar, alternatifler | Jenerik "search unavailable" demez; boş sonucu "success" diye işaretlemez |
| **3. Kurtarma kararı** | Koordinatör | Q8 gerekçesindeki üç seçenek: **değiştirilmiş sorguyla retry** / **alternatif yaklaşım** / **kısmi sonuçlarla devam** (+ kapsam notu) | Tek hata yüzünden tüm iş akışını sonlandırmaz |

Sınavın en cazip tuzağı katman 1'i doğru yapıp katman 2'yi bozan şıktır (aşağıda Anti-Pattern 3).

---

## Yapılandırılmış Hata Bağlamı (Structured Error Context)

Bir hata oluştuğunda, sadece "hata oluştu" demek yetmez. Hata raporunda dört bilgi olmalı:

### 1. Hata Türü (Failure Type)

Domain 2.2'den hatırla — dört kategori:

| Tür | Açıklama | Aksiyon (katman 1) | Aksiyon (katman 3) |
|---|---|---|---|
| **Transient (Geçici)** | Ağ zaman aşımı, servis geçici çökmesi | Sınırlı retry/backoff | Hâlâ yoksa alternatif kaynak veya kısmi devam |
| **Validation (Doğrulama)** | Geçersiz parametre, format hatası | Parametreyi düzelt, tekrar dene | Değiştirilmiş sorgu |
| **Business (İş kuralı)** | İş mantığı reddi | Retry yok | Alternatif yaklaşım |
| **Permission (Yetki)** | Erişim reddedildi | Retry yok | Eskalasyon veya yetki talebi |

### 2. Ne Denendi (What Was Attempted)

Spesifik sorgu, parametreler **ve yerel kurtarmada denenenler**:

```json
{
  "attempted_action": "journal_search",
  "query": "geothermal energy capacity 2023-2024",
  "parameters": {
    "database": "ScienceDirect",
    "date_range": "2023-01-01 to 2024-12-31",
    "filters": ["peer-reviewed"]
  },
  "local_recovery_tried": ["retry x3 with backoff (2s, 4s, 8s)", "cached copy: none available"]
}
```

### 3. Kısmi Sonuçlar (Partial Results)

Hata öncesi toplanan veriler:

```json
{
  "partial_results": {
    "sources_completed": ["IEA", "IRENA", "BloombergNEF"],
    "sources_failed": ["ScienceDirect"],
    "findings_so_far": [
      {"claim": "Solar capacity grew 45%", "source": "IEA"}
    ]
  }
}
```

### 4. Potansiyel Alternatif Yaklaşımlar

Denenmiş ve denenmemiş olanlar ayrı işaretlenir — koordinatör neyin hâlâ masada olduğunu görür:

```json
{
  "alternatives_untried": [
    "Try alternative database: Google Scholar",
    "Proceed with partial results and annotate gap"
  ],
  "alternatives_tried": [
    "Use cached version from last sync — no cache present"
  ]
}
```

---

## Üç Anti-Pattern — SINAV KRİTİK

Exam guide üç anti-pattern sayar; üçü de Q8'in yanlış şıklarıdır.

### Anti-Pattern 1: Sessiz Bastırma (Silent Suppression) — Q8 C

Erişilemediği halde boş sonucu "başarılı" olarak işaretleyerek döndürme.

```json
// YANLIŞ — kaynağa ERİŞİLEMEDİ ama success deniyor
{
  "status": "success",
  "results": [],
  "source_reached": false,     // ← gerçek bu; ama alan yok ya da yok sayılıyor
  "error": null
}
```

**Neden tehlikeli:** Koordinatör hata olduğunu bilmiyor. Kurtarma mekanizması devreye giremez. Rapor eksik veri üzerinden yazılır ama kimse eksikliği bilmez. Guide: "*prevents any recovery and risks incomplete research outputs*".

### Anti-Pattern 2: İş Akışı Sonlandırma (Workflow Termination) — Q8 D

Tek bir hata yüzünden tüm pipeline'ı öldürme.

```
Kaynak 3/5 erişilemedi → TÜM ARAŞTIRMAYI İPTAL ET
```

**Neden tehlikeli:** 4 kaynak başarıyla işlenmiş — bu kısmi sonuçları çöpe atar. Guide: "*terminates the entire workflow unnecessarily when recovery strategies could succeed*".

### Anti-Pattern 3: Jenerik Hata Durumu (Generic Error Status) — Q8 B

Subagent içinde exponential backoff'lu otomatik retry — **buraya kadar doğru** — ama tüm denemeler bitince koordinatöre yalnızca **"search unavailable"** döndürme.

```json
// YANLIŞ — yerel kurtarma doğru, yayma yanlış
{"status": "search_unavailable"}
```

**Neden tehlikeli:** Guide'ın Knowledge maddesi: "*generic error statuses ('search unavailable') hide valuable context from the coordinator*". Koordinatör hangi sorgunun, hangi kaynakta, ne tür bir hatayla başarısız olduğunu, kısmi sonuç olup olmadığını bilmez → "*preventing informed decisions*". Değiştirilmiş sorguyla retry mi, alternatif kaynak mı, kısmi devam mı — hiçbirine karar veremez.

**Sınav uyarısı:** Bu şık "retry", "exponential backoff" kelimeleriyle geldiği için doğru görünür. Retry doğrudur; **jenerik mesaj** yanlıştır. Katman 1 ✔, katman 2 ✘.

### Doğru Yaklaşım — Q8 A

```json
{
  "status": "partial_success",
  "completed_sources": 4,
  "failed_sources": 1,
  "findings": [...],
  "errors": [
    {
      "source": "ScienceDirect",
      "failure_type": "transient",
      "source_reached": false,
      "attempted": "journal_search for geothermal data; 3 retries with backoff",
      "partial_results": "none from this source",
      "alternatives_untried": ["Google Scholar", "proceed with coverage gap"]
    }
  ],
  "coverage_note": "Geothermal section limited due to ScienceDirect timeout"
}
```

### Resmi örnek soru (Exam Guide Q8)

> Web search subagent karmaşık bir konuyu araştırırken zaman aşımına uğruyor. Bu hata bilgisinin koordinatöre nasıl akacağını tasarlamalısın. Hangi yaklaşım akıllı kurtarmayı en iyi sağlar?
>
> **A)** Koordinatöre hata türü, denenen sorgu, varsa kısmi sonuçlar ve olası alternatif yaklaşımları içeren **yapılandırılmış hata bağlamı** döndür.
> **B)** Subagent içinde exponential backoff'lu otomatik retry uygula; tüm denemeler bitince yalnızca jenerik "search unavailable" durumu döndür.
> **C)** Zaman aşımını subagent içinde yakala ve **başarılı olarak işaretlenmiş boş sonuç kümesi** döndür.
> **D)** Zaman aşımı istisnasını doğrudan üst seviye bir handler'a yay ve **tüm araştırma iş akışını sonlandır**.
>
> **Doğru cevap: A.** Yapılandırılmış bağlam koordinatöre karar için gereken bilgiyi verir — "*whether to retry with a modified query, try an alternative approach, or proceed with partial results*". B jenerik durum bağlamı gizler; C hatayı başarı diye bastırır; D kurtarma mümkünken iş akışını gereksiz sonlandırır.

---

## Erişim Hatası vs Geçerli Boş Sonuç — SINAV TUZAĞI

Bu ayrım sınavda çok ince şekilde test ediliyor. İki durumu karıştırmak ciddi hatalara yol açar — ve ayrım **yanıtın içinde görünür olmalı**.

### Erişim Hatası (Access Failure)

Araç veri kaynağına **erişemedi**:

- Ağ zaman aşımı
- API anahtarı geçersiz
- Servis çökmüş

→ **Retry düşünülebilir** (katman 1, sınırlı). Veri orada olabilir ama erişemedik.

### Geçerli Boş Sonuç (Valid Empty Result)

Araç veri kaynağına **erişti**, eşleşen sonuç **bulamadı**:

- Veritabanında bu tarih aralığında kayıt yok
- Arama kriterlerine uyan müşteri yok
- Envanterde bu ürün mevcut değil

→ **Retry GEREKSİZ.** Veri kaynağına başarıyla erişildi ve cevap "sonuç yok". Bu **cevabın kendisi**. Tekrar denemek aynı sonucu verir. Sonraki adım retry değil, *yeni bir karar*dır: farklı sorgu (koordinatör), müşteriden ek tanımlayıcı (5.2), ya da kapsam notu.

### Yanıt şemasında ayrım — exam guide'ın Skills maddesi

*"Distinguishing access failures from valid empty results **in error reporting** so the coordinator can make appropriate decisions"*. Yani ayrım yalnızca agent'ın yorumunda değil, **araç/subagent yanıtında** yapılır. Aynı `{"status": "success", "results": []}` şekli iki farklı gerçeği anlatıyorsa şema bozuktur.

```json
// Geçerli boş sonuç — kaynağa erişildi, eşleşme yok
{
  "status": "ok",
  "source_reached": true,
  "match_count": 0,
  "query": "orders where phone = +90 555 ...",
  "message": "No orders found for this phone number"
}

// Erişim hatası — kaynağa erişilemedi
{
  "status": "error",
  "source_reached": false,
  "failure_type": "transient",
  "attempted": "orders lookup, 3 retries",
  "partial_results": null
}
```

Sessiz bastırmanın (Anti-Pattern 1) tam tanımı artık net: **`source_reached: false` iken `status: ok/success` demek.**

### Karar Tablosu

| Durum | Araç kaynağa erişti mi? | Sonuç | Aksiyon |
|---|---|---|---|
| Erişim hatası | ❌ Hayır (`source_reached: false`) | Belirsiz | Sınırlı retry (katman 1) → yapılandırılmış yayma |
| Geçerli boş sonuç | ✅ Evet (`source_reached: true`) | Eşleşme yok | Retry yapma — bu CEVAP; yeni karar (farklı sorgu / ek tanımlayıcı / kapsam notu) |

---

## Retry Kuralları — Domain'ler Arası Tek Tablo

"Retry ne zaman?" sorusu 4.4, 5.2 ve 5.3'te üç ayrı cevapla geçer. Tek tablo:

| Durum | Retry? | Kim | Kaynak |
|---|---|---|---|
| Transient erişim hatası (timeout, 5xx) | ✅ Sınırlı, backoff'lu | Subagent (katman 1) | 5.3 |
| Anlamsal çıkarım hatası, bilgi belgede **var** | ✅ Hata mesajıyla, 2–3 kez | Çıkarım döngüsü | 4.4 |
| Bilgi belgede **yok** / harici belgede | ❌ Nullable şema / belgeyi ekle | — | 4.4 |
| Geçerli boş sonuç | ❌ Cevap bu; müşteriden ek tanımlayıcı | Agent | 5.3 + 5.2 |
| Permission / business hatası | ❌ Eskalasyon / alternatif | Koordinatör | 5.3 |

---

## Kapsam Açıklamaları (Coverage Annotations)

### Problem

Bir sentez raporu 5 enerji kaynağını kapsamalı. Ama jeotermal veri kaynağına erişilemedi. Rapor sessizce jeotermal bölümünü atlıyor.

Okuyucu raporu okuduğunda, jeotermalin kasıtlı olarak mı dışlandığını yoksa verilerin mi eksik olduğunu bilemez.

### Çözüm

Sentez çıktısında hangi bulguların **iyi desteklendiğini** (well-supported), hangi alanların **boşlukları** olduğunu belirt:

```
## Araştırma Kapsamı
- Güneş enerjisi: ✅ Kapsamlı (3 kaynak)
- Rüzgâr enerjisi: ✅ Kapsamlı (2 kaynak)
- Hidroelektrik: ✅ Kapsamlı (2 kaynak)
- Biyokütle: ✅ Kısmi (1 kaynak)
- Jeotermal: ⚠️ Sınırlı — ScienceDirect erişim zaman aşımı nedeniyle veriler eksik
```

**Kural:** Sessiz ihmal yerine açık kapsam açıklaması. "Jeotermal enerji bölümü, erişilemeyen dergi kaynağı nedeniyle sınırlıdır" her zaman sessiz ihmalden iyidir.

Bu bölüm, 5.6'nın "iyi desteklenen / tartışmalı" ayrımıyla aynı raporun parçasıdır. Sentez raporunun iskeleti üç bölümdür: **Desteklenen bulgular / Tartışmalı bulgular (5.6) / Kapsam boşlukları (5.3)**.

### Nasıl test edilir? (Exam Guide Egzersiz 4, adım 19)

*"Simulate a subagent timeout and verify the coordinator receives structured error context (failure type, attempted query, partial results). Test that the coordinator can proceed with partial results and annotate the final output with coverage gaps."* — Yani kabul kriteri üç adımdır: timeout simülasyonu → koordinatör yapılandırılmış bağlamı alıyor mu → rapor kapsam notu taşıyor mu.

> **Güncel not (Agent SDK):** Subagent'ı *erken bitiren* bir API hatası (rate limit vb.) Agent SDK'da subagent'ın *sonucu* olarak koordinatöre teslim edilmez. Yani yapılandırılmış hata bağlamı altyapıdan otomatik gelmez; subagent'ın kendi çıktısı ya da **araç sarmalayıcısı** üretmelidir. Senaryodaki "ScienceDirect timeout" için doğru yer araç sarmalayıcısıdır — Domain 2.2'nin yapılandırılmış hata yanıtı şemasıyla aynı.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| İki katman | Subagent yerel kurtarma (sınırlı retry) → çözemediğini yapılandırılmış yay → koordinatör karar verir |
| Koordinatörün üç seçeneği | Değiştirilmiş sorguyla retry / alternatif yaklaşım / kısmi sonuçlarla devam |
| Yapılandırılmış hata bağlamı | Hata türü + ne denendi (yerel kurtarma dahil) + kısmi sonuçlar + alternatifler |
| Anti-pattern 1: sessiz bastırma | `source_reached: false` iken `success` — kurtarma engellenir |
| Anti-pattern 2: iş akışı sonlandırma | Tek hata için tüm pipeline'ı öldürme — kısmi sonuçlar kaybolur |
| Anti-pattern 3: jenerik durum | Retry doğru, "search unavailable" yanlış — koordinatör kör kalır |
| Erişim hatası | Kaynağa erişilemedi → sınırlı retry düşün |
| Geçerli boş sonuç | Kaynağa erişildi, eşleşme yok → retry GEREKSİZ; yeni karar |
| Şemada ayrım | `source_reached` / `failure_type` alanları — ayrım yanıtta görünür olmalı |
| Kapsam açıklamaları | Desteklenen / boşluklu — sessiz ihmal yok; 5.6 ile aynı rapor iskeleti |

---

## Pratik Senaryo 1

> Bir multi-agent araştırma sistemi 5 akademik kaynaktan veri topluyor. 4 kaynak başarıyla sonuç döndürdü. 5. kaynak (ScienceDirect) ağ zaman aşımı hatası verdi.
>
> Agent'ın mevcut davranışı: zaman aşımı sonrası tüm araştırmayı iptal ediyor ve "araştırma tamamlanamadı" mesajı döndürüyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Tüm araştırmayı iptal etmek doğru — eksik veriyle rapor yazılmamalı.
>
> **B)** Subagent sınırlı backoff'lu retry denesin; hâlâ başarısızsa hata türü, denenen sorgu ve kısmi sonuçları yapılandırılmış olarak koordinatöre iletsin; koordinatör 4 kaynakla devam edip sentez çıktısına kapsam açıklaması eklesin.
>
> **C)** Subagent sınırlı backoff'lu retry denesin; hâlâ başarısızsa koordinatöre "kaynak kullanılamıyor" durumu döndürsün ve koordinatör 4 kaynakla devam etsin.
>
> **D)** Subagent zaman aşımını yakalayıp boş sonuç kümesini başarılı olarak döndürsün; koordinatör 5 kaynağın tamamlandığını varsayarak sentezi başlatsın.

### Doğru Cevap: B

**Neden B doğru:** İki katmanın ikisi de doğru: yerel sınırlı retry, sonra yapılandırılmış yayma; koordinatör kısmi sonuçlarla devam edip kapsam notu düşüyor. Q8-A + Egzersiz 4 adım 19.

**Neden A yanlış:** Workflow termination anti-pattern'ı. Tek başarısızlık yüzünden 4 başarılı kaynağın sonuçlarını çöpe atar.

**Neden C yanlış:** En cazip yanlış şık (Q8-B). Yerel retry doğru ama "kaynak kullanılamıyor" jenerik durumu koordinatörü kör bırakır: alternatif veritabanı denenebilir miydi, kısmi bulgu var mıydı, hata transient miydi — bilinmez. Koordinatör devam etse bile raporun kapsam notu yazılamaz.

**Neden D yanlış:** Silent suppression (Q8-C). Kaynağa erişilemediği halde başarı bildirilir; koordinatör eksikliği bilmez, rapor sessizce eksik çıkar.

---

## Pratik Senaryo 2

> Bir müşteri destek agent'ı müşterinin siparişini arıyor. Araç şu sonucu döndürüyor:
>
> ```json
> {
>   "status": "ok",
>   "source_reached": true,
>   "match_count": 0,
>   "message": "No orders found matching criteria"
> }
> ```
>
> Agent bu sonucu "sipariş bulunamadı, tekrar deneyelim" olarak yorumluyor ve aynı sorguyu 3 kez daha çalıştırıyor.
>
> **Bu davranıştaki sorun nedir?**
>
> **A)** Agent retry sayısını artırmalı — 3 yetmez, 10 denemeli.
>
> **B)** Agent geçerli boş sonuç ile erişim hatasını karıştırıyor. `source_reached: true` — araç kaynağa erişti ve eşleşme bulamadı. Bu cevabın kendisi; retry gereksiz. Sonraki adım müşteriden ek tanımlayıcı istemek.
>
> **C)** Araç hatalı çalışıyor — her zaman en az bir sonuç döndürmelidir.
>
> **D)** Agent müşteriye sormadan başka alanlarla (e-posta, ad) arama yapmalı — aynı parametrelerle değil.

### Doğru Cevap: B

**Neden B doğru:** `source_reached: true` + `match_count: 0` = geçerli boş sonuç. Bu bir erişim hatası değil; tekrar denemek aynı sonucu verir. Doğru sonraki adım 5.2'deki gibi müşteriden ek tanımlayıcı istemektir.

**Neden A yanlış:** Daha fazla retry aynı geçerli boş sonucu döndürür. Sorun retry sayısında değil, sonuç yorumlamasında.

**Neden C yanlış:** Araç doğru çalışıyor — hatta iyi tasarlanmış: erişildiğini ve eşleşme olmadığını açıkça bildiriyor. "Eşleşme yok" geçerli bir cevap.

**Neden D yanlış:** Agent'ın müşteriye sormadan kendi başına başka alanlarla arama yapması yanlış müşteriye ulaşma riski taşır (5.2 sezgisel seçim tuzağı). Ek tanımlayıcı *müşteriden* istenir.

---

## Pratik Senaryo 3

> Bir araştırma koordinatörü web search subagent'ından şu yanıtı alıyor:
>
> ```json
> {"status": "success", "results": []}
> ```
>
> Loglar aynı sorgunun 30 saniye önce 12 sonuç döndürdüğünü ve araç sağlayıcısının o anda kesinti yaşadığını gösteriyor. Koordinatör "bu konuda kaynak yok" diye raporlayıp devam etmiş.
>
> **Kök neden nedir?**
>
> **A)** Koordinatör retry yapmalıydı — boş sonuç her zaman tekrar denenir.
>
> **B)** Subagent'ın yanıt şeması erişim hatası ile geçerli boş sonucu ayırt etmiyor; kesinti "success + boş dizi" olarak yayılmış (sessiz bastırma). Şemaya `source_reached` / `failure_type` alanları eklenmeli, subagent transient hatayı önce yerel retry ile denemeli, çözemezse yapılandırılmış hata döndürmeli.
>
> **C)** Koordinatör sonucu doğrulamak için aynı sorguyu ikinci bir subagent'a göndermeliydi.
>
> **D)** Araç sağlayıcısının kesintisi sistem dışı bir sorun; koordinatörün yapabileceği bir şey yok.

### Doğru Cevap: B

**Neden B doğru:** Şema, iki farklı gerçeği (erişilemedi / eşleşme yok) aynı şekle indirgiyor. Koordinatör bu yüzden kesintiyi "kaynak yok" sanmış. Çözüm hem şemada (ayrım görünür olmalı) hem katmanlarda (yerel retry → yapılandırılmış yayma).

**Neden A yanlış:** "Boş sonuç her zaman retry" tam ters hata: geçerli boş sonuçları da tekrar tekrar sorgular. Retry'a karar verebilmek için önce erişim durumunun *bilinmesi* gerekir — şema bunu vermiyor.

**Neden C yanlış:** İkinci subagent aynı bozuk şemayla aynı "success + boş" cevabı döndürür; sorun yayma katmanında, yürütmede değil.

**Neden D yanlış:** Kesinti dış sorun ama *sessiz kalması* sistemin sorunu: yapılandırılmış hata gelseydi koordinatör alternatif kaynak dener ya da rapora kapsam notu düşerdi.
