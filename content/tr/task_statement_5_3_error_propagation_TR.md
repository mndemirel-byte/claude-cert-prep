# Task Statement 5.3: Hata Yayılımı (Error Propagation)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Multi-agent sistemlerde ve veri çıkarım pipeline'larında hatalar kaçınılmazdır. Bir araç zaman aşımına uğrar, bir API erişim reddeder, bir veri kaynağı sonuç döndürmez. Kritik soru: **hata oluştuğunda ne yaparsın?**

Bu task statement, hataların nasıl yapılandırılmış şekilde raporlanacağını, iki yaygın anti-pattern'ı ve erişim hatası ile geçerli boş sonuç arasındaki farkı öğretir.

---

## Yapılandırılmış Hata Bağlamı (Structured Error Context)

Bir hata oluştuğunda, sadece "hata oluştu" demek yetmez. Hata raporunda dört bilgi olmalı:

### 1. Hata Türü (Failure Type)

Domain 2'den hatırla — dört kategori:

| Tür | Açıklama | Aksiyon |
|---|---|---|
| **Transient (Geçici)** | Ağ zaman aşımı, servis geçici çökmesi | Retry düşün |
| **Validation (Doğrulama)** | Geçersiz parametre, format hatası | Parametreleri düzelt |
| **Business (İş kuralı)** | İş mantığı reddi (örn. yetersiz bakiye) | Alternatif yaklaşım |
| **Permission (Yetki)** | Erişim reddedildi | Eskalasyon veya yetki talebi |

### 2. Ne Denendi (What Was Attempted)

Spesifik sorgu ve kullanılan parametreler:

```json
{
  "attempted_action": "journal_search",
  "query": "geothermal energy capacity 2023-2024",
  "parameters": {
    "database": "ScienceDirect",
    "date_range": "2023-01-01 to 2024-12-31",
    "filters": ["peer-reviewed"]
  }
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

```json
{
  "alternatives": [
    "Try alternative database: Google Scholar",
    "Use cached version from last sync",
    "Proceed with partial results and annotate gap"
  ]
}
```

---

## İki Anti-Pattern — SINAV KRİTİK

Sınavda bu iki anti-pattern **yanlış cevap seçeneği** olarak sürekli karşına çıkacak:

### Anti-Pattern 1: Sessiz Bastırma (Silent Suppression)

Boş sonuçları "başarılı" olarak işaretleyerek döndürme.

```json
// YANLIŞ — sessiz bastırma
{
  "status": "success",
  "results": [],
  "error": null
}
```

**Neden tehlikeli:** Üst katman hata olduğunu bilmiyor. Kurtarma mekanizması devreye giremez. Rapor eksik veri üzerinden yazılır ama kimse eksikliği bilmez.

### Anti-Pattern 2: İş Akışı Sonlandırma (Workflow Termination)

Tek bir hata yüzünden tüm pipeline'ı öldürme.

```
Kaynak 3/5 erişilemedi → TÜM ARAŞTIRMAYI İPTAL ET
```

**Neden tehlikeli:** 4 kaynak başarıyla işlenmiş — bu kısmi sonuçları çöpe atar. Tek bir başarısızlık yüzünden tüm iş kaybedilir.

### Doğru Yaklaşım

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
      "attempted": "journal_search for geothermal data",
      "suggestion": "retry or use alternative source"
    }
  ],
  "coverage_note": "Geothermal section limited due to ScienceDirect timeout"
}
```

---

## Erişim Hatası vs Geçerli Boş Sonuç — SINAV TUZAĞI

Bu ayrım sınavda çok ince şekilde test ediliyor. İki durumu karıştırmak ciddi hatalara yol açar:

### Erişim Hatası (Access Failure)

Araç veri kaynağına **erişemedi**:

- Ağ zaman aşımı
- API anahtarı geçersiz
- Servis çökmüş

→ **Retry düşünülebilir.** Veri orada olabilir ama erişemedik.

### Geçerli Boş Sonuç (Valid Empty Result)

Araç veri kaynağına **erişti**, eşleşen sonuç **bulamadı**:

- Veritabanında bu tarih aralığında kayıt yok
- Arama kriterlerine uyan müşteri yok
- Envanterde bu ürün mevcut değil

→ **Retry GEREKSIZ.** Veri kaynağına başarıyla erişildi ve cevap "sonuç yok". Bu **cevabın kendisi**. Tekrar denemek aynı sonucu verir.

### Karar Tablosu

| Durum | Araç kaynağa erişti mi? | Sonuç | Aksiyon |
|---|---|---|---|
| Erişim hatası | ❌ Hayır | Belirsiz | Retry düşün |
| Geçerli boş sonuç | ✅ Evet | Eşleşme yok | Retry yapma — bu CEVAP |

---

## Kapsam Açıklamaları (Coverage Annotations)

### Problem

Bir sentez raporu 5 enerji kaynağını kapsamalı. Ama jeotermal veri kaynağına erişilemedi. Rapor sessizce jeotermal bölümünü atlıyor.

Okuyucu raporu okuduğunda, jeotermalin kasıtlı olarak mı dışlandığını yoksa verilerin mi eksik olduğunu bilemez.

### Çözüm

Sentez çıktısında hangi bulguların iyi desteklendiğini, hangi alanların boşlukları olduğunu belirt:

```
## Araştırma Kapsamı
- Güneş enerjisi: ✅ Kapsamlı (3 kaynak)
- Rüzgâr enerjisi: ✅ Kapsamlı (2 kaynak)
- Hidroelektrik: ✅ Kapsamlı (2 kaynak)
- Biyokütle: ✅ Kısmi (1 kaynak)
- Jeotermal: ⚠️ Sınırlı — ScienceDirect erişim zaman aşımı nedeniyle veriler eksik
```

**Kural:** Sessiz ihmal yerine açık kapsam açıklaması. "Jeotermal enerji bölümü, erişilemeyen dergi kaynağı nedeniyle sınırlıdır" her zaman sessiz ihmelden iyidir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Yapılandırılmış hata bağlamı | Hata türü + ne denendi + kısmi sonuçlar + alternatifler |
| Sessiz bastırma | ❌ Boş sonucu başarılı gösterme — kurtarma engellenir |
| İş akışı sonlandırma | ❌ Tek hata için tüm pipeline'ı öldürme — kısmi sonuçlar kaybolur |
| Erişim hatası | Kaynağa erişilemedi → retry düşün |
| Geçerli boş sonuç | Kaynağa erişildi, eşleşme yok → retry GEREKSIZ, bu cevabın kendisi |
| Kapsam açıklamaları | Hangi alanlar iyi desteklenmiş, hangilerinde boşluk var — belirt |

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
> **B)** 4 kaynaktan gelen sonuçlarla devam et, başarısız kaynağı yapılandırılmış hata bilgisiyle raporla ve sentez çıktısında kapsam açıklaması ekle.
>
> **C)** ScienceDirect hatasını sessizce yoksay ve 4 kaynakla rapor yaz — kullanıcı farkı anlamaz.
>
> **D)** Tüm 5 kaynağı sonsuz döngüde retry et — sonunda hepsi çalışır.

### Doğru Cevap: B

**Neden B doğru:** Workflow termination anti-pattern'ından kaçınır. 4 başarılı kaynağın kısmi sonuçlarını korur, başarısız kaynağı yapılandırılmış hata bilgisiyle raporlar ve sentez çıktısında kapsam açıklaması ekler. Okuyucu hangi bölümlerin sınırlı olduğunu bilir.

**Neden A yanlış:** Workflow termination anti-pattern'ı. Tek başarısızlık yüzünden 4 başarılı kaynağın sonuçlarını çöpe atar.

**Neden C yanlış:** Silent suppression anti-pattern'ı. Hata sessizce yutulur, kimse eksikliği bilmez, kurtarma mekanizması devreye giremez.

**Neden D yanlış:** Sonsuz retry sistemi kilitler. Geçici hatalar "sonunda düzelir" varsayımı her zaman doğru değil. Makul sayıda retry sonra kısmi sonuçlarla devam et.

---

## Pratik Senaryo 2

> Bir müşteri destek agent'ı müşterinin siparişini arıyor. Araç şu sonucu döndürüyor:
>
> ```json
> {
>   "status": "success",
>   "results": [],
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
> **B)** Agent geçerli boş sonuç ile erişim hatasını karıştırıyor. Status "success" — araç kaynağa erişti ve eşleşme bulamadı. Bu cevabın kendisi. Retry gereksiz.
>
> **C)** Araç hatalı çalışıyor — her zaman sonuç döndürmelidir.
>
> **D)** Agent farklı parametrelerle retry etmeli — aynı parametrelerle değil.

### Doğru Cevap: B

**Neden B doğru:** Status "success" demek araç kaynağa başarıyla erişti. Boş sonuç = eşleşme yok. Bu bir erişim hatası değil, geçerli boş sonuç. Tekrar denemek aynı sonucu verir — gereksiz kaynak tüketimi.

**Neden A yanlış:** Daha fazla retry aynı geçerli boş sonucu döndürür. Sorun retry sayısında değil, sonuç yorumlamasında.

**Neden C yanlış:** Araç doğru çalışıyor. "Eşleşme yok" geçerli bir cevap — araç her zaman dolu sonuç döndürmek zorunda değil.

**Neden D yanlış:** Müşterinin verdiği bilgilerle arama yapıldı ve sonuç yok. Parametreleri değiştirmek (örn. farklı isim aramak) yanlış sonuçlara yol açabilir. Önce müşteriden ek bilgi istemek gerekir.
