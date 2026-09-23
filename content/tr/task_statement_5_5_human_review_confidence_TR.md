# Task Statement 5.5: İnsan İncelemesi ve Güven Kalibrasyonu (Human Review & Confidence Calibration)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir yapılandırılmış veri çıkarım pipeline'ı (extraction pipeline) çalıştırıyorsun. Model faturalardan alanları çıkarıyor, sözleşmelerden tarihleri okuyor, belgelerden miktarları alıyor. Sistem %97 genel doğruluk bildiriyor. Her şey yolunda gibi görünüyor — ta ki belirli bir belge türünde %40 hata oranı keşfedene kadar.

Bu task statement, toplam metriklerin nasıl yanıltabileceğini, güven kalibrasyonunu ve insan incelemesi kapasitesinin nasıl optimize edileceğini öğretir.

---

## Toplam Metrik Tuzağı (Aggregate Metrics Trap)

### Problem

Sistem genelinde **%97 doğruluk** harika görünüyor. Ama bu rakam tüm belge türlerinin ortalaması:

| Belge Türü | Hacim | Doğruluk |
|---|---|---|
| Standart faturalar | %70 | %99.5 |
| Sözleşmeler | %20 | %98 |
| El yazısı notlar | %10 | %60 |

El yazısı notlar toplam hacmin sadece %10'u ama **%40 hata oranına** sahip. Bu hata, yüksek hacimli standart faturaların %99.5'lik doğruluğuyla örtülüyor.

### Çözüm

Otomasyona geçmeden önce doğruluğu **iki boyutta** doğrula:

1. **Belge türüne göre:** Her belge türünün ayrı doğruluk oranını hesapla
2. **Alan segmentine göre:** Her çıkarılan alanın ayrı doğruluk oranını hesapla

```
Doğruluk Analizi:
├── Belge türüne göre:
│   ├── Standart faturalar: %99.5 ✅ Otomasyona uygun
│   ├── Sözleşmeler: %98 ✅ Otomasyona uygun
│   └── El yazısı notlar: %60 ❌ İnsan incelemesi gerekli
│
└── Alan segmentine göre:
    ├── Toplam tutar: %99 ✅
    ├── Tarih: %97 ✅
    ├── Vergi numarası: %94 ⚠️ İzlenmeli
    └── Ödeme koşulları: %78 ❌ İnsan incelemesi gerekli
```

**Kural:** %97 genel doğruluk, belirli bir belge türünde %40 hata oranını gizleyebilir. Otomasyona geçmeden önce her zaman belge türü VE alan segmentine göre doğrula.

---

## Tabakalı Rastgele Örnekleme (Stratified Random Sampling)

### Problem

Sistem yüksek güvenle çalışıyor — çıkarımların %95'i yüksek güven skoruyla döndürülüyor. Ama yeni bir belge formatı çıktığında (örn. yeni bir tedarikçinin fatura şablonu), model yüksek güvenle **yanlış** çıkarımlar yapabiliyor.

Bu "yeni hata kalıpları" (novel error patterns) mevcut güven eşikleriyle tespit edilemiyor.

### Çözüm

Yüksek güvenli çıkarımlardan bile düzenli olarak rastgele örnekler al ve insanlarla doğrula:

```
Her hafta:
├── Düşük güvenli çıkarımlar: %100 insan incelemesi (zaten yapılıyor)
├── Orta güvenli çıkarımlar: %30 örnekleme
└── Yüksek güvenli çıkarımlar: %5 örnekleme ← BU KRİTİK
```

**Neden yüksek güvenli çıkarımlar da örneklenir?**

- Model yeni belge formatlarında yüksek güvenle yanlış yapabilir (uncalibrated confidence)
- Yavaş yavaş değişen belge formatları (drift) güven eşiklerini geçersiz kılabilir
- Sadece düşük güvenli olanları incelemek, yeni hata kalıplarını kaçırır

---

## Alan Seviyesi Güven Kalibrasyonu (Field-Level Confidence)

### Kavram

Model her çıkarılan alan için ayrı güven skoru verir:

```json
{
  "invoice_number": {"value": "INV-2024-001", "confidence": 0.99},
  "total_amount": {"value": 1547.83, "confidence": 0.95},
  "tax_id": {"value": "TR1234567890", "confidence": 0.72},
  "payment_terms": {"value": "Net 30", "confidence": 0.45}
}
```

### Kalibrasyon Süreci

1. **Etiketli doğrulama setleri (ground truth data) oluştur:** Gerçek değerleri bilinen belgelerden oluşan bir test seti
2. **Güven eşiklerini kalibre et:** Model'in %90 güven dediği alanlarda gerçekten %90 doğruluk var mı?
3. **Eşik bazlı yönlendirme kur:**

```
if confidence >= 0.90: → otomatik kabul
if 0.70 <= confidence < 0.90: → insan incelemesi kuyruğuna ekle
if confidence < 0.70: → öncelikli insan incelemesi
```

### İnceleme Kapasitesi Optimizasyonu

İnsan inceleme kapasitesi sınırlıdır — günde 200 belge incelenebiliyorsa, bu kapasiteyi en etkili nasıl kullanırsın?

**Kural:** Sınırlı inceleme kapasitesini en yüksek belirsizlikli öğelere önceliklendir.

```
Önceliklendirme:
1. Düşük güvenli alanlar (confidence < 0.70) → İLK İNCELE
2. Orta güvenli alanlar (0.70-0.90) → İKİNCİ
3. Yüksek güvenli örnekleme (%5) → SON (ama ATLA değil)
```

Bu yaklaşımla:
- En riskli çıkarımlar ilk incelenir
- Sınırlı insan kapasitesi en yüksek etkili alanlara yönlendirilir
- Yüksek güvenli örnekleme yeni hata kalıplarını tespit eder

---

## Kalibrasyon vs Güven Skoru — Kritik Ayrım

**Ham güven skoru:** Model'in kendi değerlendirmesi. Kalibrasyon yapılmamışsa güvenilmez olabilir (Task 5.2'deki model güven skoru tuzağını hatırla).

**Kalibre edilmiş güven:** Etiketli doğrulama setleriyle doğrulanmış ve ayarlanmış eşikler. Model "%90 güvenli" dediğinde gerçekten %90 doğruluk var.

**Sınav notu:** Task 5.2'de "model güven skoru eskalasyon tetikleyicisi olarak güvenilmez" dedik. Burada ise "alan seviyesi güven kalibrasyonu ile insan incelemesine yönlendirme" diyoruz. Fark nedir?

- **5.2:** Ham, kalibre edilmemiş güven skoru → eskalasyon kararı için güvenilmez
- **5.5:** Etiketli veriyle kalibre edilmiş güven eşikleri → inceleme yönlendirmesi için güvenilir

Anahtar fark: **kalibrasyon**. Ham güven skoru güvenilmez, kalibre edilmiş güven skoru kullanılabilir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Toplam metrik tuzağı | %97 genel doğruluk, belirli türde %40 hatayı gizleyebilir |
| İki boyutlu doğrulama | Belge türüne göre VE alan segmentine göre doğrula |
| Tabakalı örnekleme | Yüksek güvenli çıkarımlardan da örnekle — yeni hata kalıplarını yakala |
| Alan seviyesi güven | Her alan için ayrı güven skoru, kalibre edilmiş eşiklerle |
| Ground truth data | Etiketli doğrulama setleriyle eşikleri kalibre et |
| İnceleme kapasitesi | Sınırlı kapasiteyi en yüksek belirsizlikli öğelere önceliklendir |
| Ham vs kalibre güven | Ham güven güvenilmez, kalibre edilmiş güven kullanılabilir |

---

## Pratik Senaryo 1

> Bir belge çıkarım sistemi %97 genel doğruluk bildiriyor. Yönetim, sistemi tam otomasyona geçirmeyi planlıyor — tüm insan incelemesini kaldıracak.
>
> İç denetim, el yazısı notlardan yapılan çıkarımlarda %40 hata oranı tespit ediyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** %97 genel doğruluk yeterli — tam otomasyona geç.
>
> **B)** Tüm belge türleri için insan incelemesini sürdür — %97 bile güvenilmez.
>
> **C)** Doğruluğu belge türüne ve alan segmentine göre ayrı ayrı değerlendir. Yüksek doğruluktaki türleri otomatikleştir, düşük doğruluktaki türleri (el yazısı notlar) insan incelemesinde tut.
>
> **D)** El yazısı notları pipeline'dan tamamen çıkar — sorun çözülür.

### Doğru Cevap: C

**Neden C doğru:** Toplam metrik tuzağından kaçınır. Doğruluğu belge türüne ve alan segmentine göre ayrı değerlendirir. Standart faturalar (%99.5) otomasyona uygun, el yazısı notlar (%60) insan incelemesi gerektirir. Her türü kendi performansına göre değerlendir.

**Neden A yanlış:** Toplam metrik tuzağı. %97 genel doğruluk, el yazısı notlardaki %40 hata oranını gizliyor. Tam otomasyon bu tür belgelerde ciddi hatalara yol açar.

**Neden B yanlış:** Tüm türler için insan incelemesi gereksiz kaynak harcaması. %99.5 doğruluklu standart faturalar için insan incelemesi katma değer sağlamaz.

**Neden D yanlış:** El yazısı notları çıkarmak veri kaybıdır. Doğru çözüm bu türü insan incelemesine yönlendirmek, pipeline'dan çıkarmak değil.

---

## Pratik Senaryo 2

> Bir çıkarım sistemi alan seviyesi güven skoru veriyor. Sistem tasarımcısı şu kuralı uygulamış: "Güven skoru %80'in üzerindeyse otomatik kabul et."
>
> %80 eşiği herhangi bir doğrulama verisi olmadan, sezgisel olarak belirlenmiş.
>
> Son 1.000 belgenin analizi şunu gösteriyor: model %85 güven dediği alanlarda gerçek doğruluk %62.
>
> **Bu durumun kök nedeni ve çözümü nedir?**
>
> **A)** Eşiği %95'e çıkar — daha muhafazakâr ol.
>
> **B)** Güven eşikleri etiketli doğrulama setleri (ground truth data) ile kalibre edilmemiş. Model'in %85 güveni gerçek %62 doğruluğa karşılık geliyor. Çözüm: etiketli veriyle eşikleri kalibre et.
>
> **C)** Daha büyük model kullan — güven skorları daha doğru olur.
>
> **D)** Güven skorunu tamamen kaldır — işe yaramıyor.

### Doğru Cevap: B

**Neden B doğru:** Ham güven skoru kalibre edilmemiş. Model %85 diyor ama gerçek doğruluk %62 — ciddi kalibrasyon farkı. Çözüm: etiketli doğrulama setleriyle eşikleri kalibre et. Model'in %85'inin gerçekte %62'ye karşılık geldiğini biliyorsan, eşiğini buna göre ayarlarsın.

**Neden A yanlış:** Eşiği artırmak kalibrasyon sorununu çözmez. %95'te de model'in güveni gerçek doğrulukla uyumsuz olabilir. Sezgisel eşik yerine veri bazlı kalibrasyon gerekli.

**Neden C yanlış:** Daha büyük model güven kalibrasyonunu garanti etmez. Kalibrasyon model boyutundan bağımsız bir süreç — her model için ayrıca yapılmalı.

**Neden D yanlış:** Güven skoru kalibre edildiğinde çok değerli bir araç. Sorunu düzeltmek yerine aracı kaldırmak yanlış. Kalibrasyon yapılmış güven skoru insan incelemesi yönlendirmesini optimize eder.
