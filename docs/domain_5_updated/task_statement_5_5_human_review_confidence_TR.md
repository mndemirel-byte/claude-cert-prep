# Task Statement 5.5: İnsan İncelemesi ve Güven Kalibrasyonu (Human Review & Confidence Calibration)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir yapılandırılmış veri çıkarım pipeline'ı (extraction pipeline) çalıştırıyorsun. Model faturalardan alanları çıkarıyor, sözleşmelerden tarihleri okuyor, belgelerden miktarları alıyor. Sistem %97 genel doğruluk bildiriyor. Her şey yolunda gibi görünüyor — ta ki belirli bir belge türünde %40 hata oranı keşfedene kadar.

Bu task statement, toplam metriklerin nasıl yanıltabileceğini, güven kalibrasyonunu ve sınırlı insan incelemesi kapasitesinin nasıl yönlendirileceğini öğretir.

Sınav senaryosu: **Structured Data Extraction** — Domain 4 (çıkarım şeması, doğrulama) ile Domain 5'in kesiştiği senaryo; exam guide bu senaryonun "primary domains" listesine ikisini de yazar. Egzersiz 3 adım 15 bu statement'ın uygulama sırasıdır: *"have the model output field-level confidence scores, route low-confidence extractions to human review, and analyze accuracy by document type and field"*.

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

**Kural:** %97 genel doğruluk, belirli bir belge türünde %40 hata oranını gizleyebilir. Otomasyona geçmeden önce her zaman belge türü VE alan segmentine göre doğrula. (Domain 4.6'daki "belge tipi × alan doğruluk matrisi" aynı tablodur.)

---

## Tabakalı Rastgele Örnekleme (Stratified Random Sampling)

### Problem

Sistem yüksek güvenle çalışıyor — çıkarımların %95'i yüksek güven skoruyla döndürülüyor. Ama yeni bir belge formatı çıktığında (örn. yeni bir tedarikçinin fatura şablonu), model yüksek güvenle **yanlış** çıkarımlar yapabiliyor.

Bu "yeni hata kalıpları" (novel error patterns) mevcut güven eşikleriyle tespit edilemiyor — çünkü eşik yalnızca *düşük* güvenlileri insana gönderiyor.

### Neden "düz" rastgele örnekleme yetmez?

1.000 çıkarımdan rastgele 50 tane çekersen, el yazısı notlar (%10 hacim) ortalama 5 örnekle temsil edilir — %40'lık hata oranını istatistiksel olarak göremezsin. Toplam metrik tuzağı örneklemede tekrar eder.

### Çözüm: Üç boyutlu tabaka

Örnekleme **tabakalara** bölünür ve her tabakadan yeterli sayıda örnek alınır:

```
Tabakalar = belge türü × alan × güven bandı

Her hafta:
├── Belge türü başına (fatura / sözleşme / el yazısı / YENİ format): min. 30 örnek
│   └── Her türde alan başına dağılım (tutar / tarih / vergi no / ödeme koşulu)
│       └── Güven bandı:
│           ├── Düşük güven:  zaten %100 insan incelemesinde
│           ├── Orta güven:   %30 örnekleme
│           └── Yüksek güven: %5 örnekleme  ← BU KRİTİK
```

**Neden yüksek güvenli çıkarımlar da örneklenir?**

- Model yeni belge formatlarında yüksek güvenle yanlış yapabilir (uncalibrated confidence)
- Yavaş yavaş değişen belge formatları (drift) güven eşiklerini geçersiz kılabilir
- Sadece düşük güvenli olanları incelemek, yeni hata kalıplarını kaçırır

**Neden belge türü tabakası şart?** Küçük hacimli ama hatalı bir tür düz örneklemede görünmez; tabaka onu zorla temsil ettirir. Sınavda "düz rastgele örnekleme" distractor'dır; "yüksek güvenli çıkarımların **tabakalı** rastgele örneklemesi" doğru cevaptır.

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

> **Gösterim notu:** Sayısal skor (0.72) ile `high/medium/low` enum'u ikisi de kullanılır. Sayı "sahte kesinlik" verir — 0.72 bir olasılık *değildir*, modelin kendi tahminidir; kalibrasyon zaten onu bantlara indirger. Domain 4.6'da enum tercih edildi; hangisini seçersen seç, **ham skor karar vermez, kalibre bant karar verir.**

### Kalibrasyon Süreci

1. **Etiketli doğrulama seti (ground truth data) oluştur:** Gerçek değerleri bilinen belgelerden oluşan, belge türü × alan tabakalarını kapsayan bir test seti
2. **Kalibrasyon tablosu çıkar:** Modelin her güven bandında *gerçekten* ne kadar doğru olduğunu ölç
3. **Eşiği kapasiteye göre seç** ve yönlendirme kur

### Kalibrasyon tablosu — Senaryo 2'nin verisi

| Modelin bildirdiği güven bandı | Örnek sayısı | Etiketli setteki gerçek doğruluk | Yorum |
|---|---|---|---|
| 0.95–1.00 | 620 | %98 | Kalibre — otomatik kabul adayı |
| 0.85–0.95 | 210 | **%62** | **Kalibre değil** — model burada aşırı güvenli |
| 0.70–0.85 | 120 | %55 | İnsan incelemesi |
| < 0.70 | 50 | %31 | Öncelikli insan incelemesi |

"0.85 bandı %62 doğru" satırı, sezgisel %80 eşiğinin neden başarısız olduğunu gösterir: model "%85 eminim" derken üçte bir oranında yanılıyor. Kalibrasyon tabloyu **gerçek doğruluğa** çevirir; eşik ham skora değil bu sütuna konur.

### Eşiği kapasiteden türetme

İnsan inceleme kapasitesi sınırlıdır — günde 200 belge incelenebiliyorsa, eşik şu soruya göre seçilir: *"Hangi eşik, en düşük gerçek doğruluklu ~200 belgeyi kuyruğa gönderir?"*

```
if calibrated_accuracy(band) >= 0.97:            → otomatik kabul (+ %5 tabakalı örnekleme)
elif kuyruk_kapasitesi_doldu değil:               → insan incelemesi (düşük gerçek doğruluk önce)
else:                                             → sıraya al; kapasite açılınca incele
```

Exam guide'ın ifadesi: "*routing … to human review, **prioritizing limited reviewer capacity***" — kapasite eşiği belirler, eşik kapasiteyi değil.

### İki yönlendirme sinyali — güven tek başına yetmez

Exam guide'ın Skills maddesi: "*Routing extractions with **low model confidence or ambiguous/contradictory source documents** to human review*". Yani insan kuyruğuna iki kapıdan girilir:

| Sinyal | Kaynağı | Örnek | Not |
|---|---|---|---|
| **Düşük kalibre güven** | Model (kalibrasyon tablosu) | `payment_terms` 0.45 | Yukarıdaki süreç |
| **Belirsiz / çelişkili kaynak belge** | Belge doğrulaması (Domain 4.4 `conflict_detected`, 4.3 `"unclear"` enum) | Satır toplamları ≠ belgede yazan toplam; belge iki farklı vade tarihi içeriyor | Model güveni **yüksek olsa bile** insana gider |

İkinci sinyal olmadan sistem "tutarlı biçimde emin ama belge kendi içinde çelişkili" durumu kaçırır — model çelişkiyi fark etmeden bir değeri yüksek güvenle seçebilir.

### İnceleme Kapasitesi Önceliklendirmesi

```
Önceliklendirme:
1. Çelişkili/belirsiz kaynak belgeler (conflict_detected)     → İLK İNCELE
2. Düşük kalibre güvenli alanlar                               → İKİNCİ
3. Orta bant                                                   → ÜÇÜNCÜ
4. Yüksek güvenli tabakalı örnekleme (%5)                      → SON (ama ATLA değil)
```

---

## Ham Güven vs Kalibre Güven — Üç Domain'i Uzlaştıran Kural

Üç yerde "güven" geçiyor ve üçü farklı şey söylüyor gibi görünüyor:

| Yer | Kullanım | Verdict | Neden |
|---|---|---|---|
| **Domain 4.1** | Ham güvenle *çıktıyı filtrelemek* ("emin değilsen raporlama") | ❌ Tuzak (confidence-based filtering) | Model kendi barını koyar, hem FP hem FN'i kontrol edemezsin |
| **5.2** | Ham güvenle *eskalasyon kararı* | ❌ Tuzak | Zor vakalarda yanlış yere güvenli |
| **5.5** | **Kalibre** güven + tabakalı örnekleme ile *inceleme dikkatini yönlendirmek* | ✅ Doğru | Etiketli set skoru gerçek doğruluğa çevirir; örnekleme kalibrasyonun bozulmasını yakalar |

**Ortak nokta:** Ham güven **asla tek başına karar vermez.** 5.5'te de karar veren şey ham skor değil, kalibrasyon tablosu + kapasite + ikinci sinyaldir.

### Drift ve kapalı döngü

Yeni tedarikçi şablonu = dağılım kayması. Yüksek güvenden tabakalı örnekleme bunu **erken uyarı** olarak yakalar; yakalanan yeni hata kalıbı → (a) etiketli sete eklenir, yeniden kalibrasyon; (b) Domain 4.2'ye o formata özgü few-shot örneği; (c) Domain 4.1'e kriter düzeltmesi. Domain 4'ün "kapalı iyileştirme döngüsü" burada kapanır: `detected_pattern` (4.4) ve tabakalı örnekleme (5.5) döngünün iki veri kaynağıdır.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Toplam metrik tuzağı | %97 genel doğruluk, belirli türde %40 hatayı gizleyebilir |
| İki boyutlu doğrulama | Belge türüne göre VE alan segmentine göre — otomasyondan önce |
| Tabakalı örnekleme | Belge türü × alan × güven bandı; yüksek güvenden de örnekle — düz rastgele yetmez |
| Alan seviyesi güven | Her alan için ayrı skor; ham skor karar vermez, kalibre bant verir |
| Kalibrasyon tablosu | Güven bandı → etiketli setteki gerçek doğruluk; eşik bu sütuna konur |
| Kapasite | Eşik, günlük inceleme kapasitesinden türetilir |
| İki sinyal | Düşük kalibre güven **veya** çelişkili/belirsiz kaynak belge → insan |
| 4.1 / 5.2 / 5.5 | Ham güven filtre/eskalasyon için tuzak; kalibre güven yönlendirme için doğru |
| Drift | Örnekleme erken uyarıdır; bulgu → yeniden kalibrasyon + few-shot/kriter güncellemesi |

---

## Pratik Senaryo 1

> Bir belge çıkarım sistemi %97 genel doğruluk bildiriyor. Yönetim, sistemi tam otomasyona geçirmeyi planlıyor — tüm insan incelemesini kaldıracak.
>
> İç denetim, el yazısı notlardan yapılan çıkarımlarda %40 hata oranı tespit ediyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** %97 genel doğruluk yeterli — tam otomasyona geç, haftalık düz rastgele 50 örnekle izle.
>
> **B)** Tüm belge türleri için insan incelemesini sürdür — %97 bile güvenilmez.
>
> **C)** Doğruluğu belge türüne ve alan segmentine göre ayrı ayrı değerlendir. Yüksek doğruluktaki türleri otomatikleştir, düşük doğruluktaki türleri (el yazısı notlar) insan incelemesinde tut; otomatik türlerde tabakalı örneklemeyle izle.
>
> **D)** El yazısı notları pipeline'dan tamamen çıkar — sorun çözülür.

### Doğru Cevap: C

**Neden C doğru:** Toplam metrik tuzağından kaçınır. Doğruluğu belge türüne ve alan segmentine göre ayrı değerlendirir. Standart faturalar (%99.5) otomasyona uygun, el yazısı notlar (%60) insan incelemesi gerektirir. Otomatik türlerde tabakalı örnekleme drift'i yakalar.

**Neden A yanlış:** Toplam metrik tuzağı; üstelik düz rastgele 50 örnek el yazısı türünü ~5 örnekle temsil eder — %40'lık hata görünmez kalır, tuzak örneklemede tekrar eder.

**Neden B yanlış:** Tüm türler için insan incelemesi gereksiz kaynak harcaması. Yüksek doğruluklu türler için insan incelemesi katma değer sağlamaz.

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
> **B)** Güven eşiği etiketli doğrulama setiyle (ground truth) kalibre edilmemiş; modelin %85'i gerçekte %62'ye karşılık geliyor. Çözüm: güven bandı → gerçek doğruluk tablosu çıkar, eşiği gerçek doğruluk sütununa ve inceleme kapasitesine göre koy.
>
> **C)** Daha büyük model kullan — güven skorları daha doğru olur.
>
> **D)** Modelden güven skorunu `high/medium/low` enum olarak iste; sayısal skor güvenilmez.

### Doğru Cevap: B

**Neden B doğru:** Ham güven skoru kalibre edilmemiş. Model %85 diyor ama gerçek doğruluk %62 — ciddi kalibrasyon farkı. Çözüm: etiketli setle kalibrasyon tablosu; eşik ham skora değil gerçek doğruluğa konur ve kapasiteden türetilir.

**Neden A yanlış:** Eşiği artırmak kalibrasyon sorununu çözmez. %95 bandının gerçek doğruluğu da bilinmiyor; sezgisel eşik yerine veri bazlı kalibrasyon gerekli.

**Neden C yanlış:** Daha büyük model güven kalibrasyonunu garanti etmez. Kalibrasyon model boyutundan bağımsız bir süreç — her model için ayrıca yapılmalı.

**Neden D yanlış:** Gösterimi değiştirmek kalibrasyonu değiştirmez; `high` enum'u da kalibre edilmeden "%85 → %62" ile aynı yanılgıyı taşır. Enum tercih edilebilir (sahte kesinlik vermez) ama kalibrasyonun *yerine* geçmez.

---

## Pratik Senaryo 3

> Bir fatura çıkarım sistemi kalibre edilmiş alan-bazlı güvenle çalışıyor; %92 üstü kalibre güvenli alanlar otomatik kabul ediliyor. Bir tedarikçinin faturalarında satır kalemleri toplamı ile belgede yazan "Genel Toplam" tutarlı değil; model `total_amount` alanını belgedeki değerden %96 güvenle çıkarıyor ve fatura otomatik geçiyor. Muhasebe ay sonunda 40 hatalı ödeme buluyor.
>
> **Sistemde eksik olan nedir?**
>
> **A)** Kalibrasyon bozulmuş; eşiği %98'e çıkar.
>
> **B)** Yönlendirme yalnızca güvene bakıyor; ikinci sinyal eksik. Belge doğrulaması (`calculated_total` ≠ `stated_total` → `conflict_detected`) çelişkili belgeleri model güveni ne olursa olsun insan incelemesine göndermeli — öncelikli sıraya.
>
> **C)** Model daha dikkatli olsun diye system prompt'a "toplamları kontrol et" talimatı ekle.
>
> **D)** Bu tedarikçinin faturalarını pipeline'dan çıkar.

### Doğru Cevap: B

**Neden B doğru:** Exam guide'ın Skills maddesi: düşük güven **veya** çelişkili kaynak belge → insan. Model çelişkiyi fark etmeden belgedeki değeri yüksek güvenle seçmiş; kalibrasyon doğru bile olsa güven bu hatayı yakalayamaz. Domain 4.4'ün `conflict_detected` bayrağı yönlendirmenin ikinci kapısıdır.

**Neden A yanlış:** Kalibrasyon bozulmamış — model o alanda gerçekten %96 doğru olabilir; sorun belgenin kendi içinde çelişkili olması. Eşik ne kadar yükselirse yükselsin belge tutarsızlığını ölçmez.

**Neden C yanlış:** Talimat olasılıksal; deterministik doğrulama (toplama) kodla yapılır, modele bırakılmaz (Domain 4.4).

**Neden D yanlış:** Veri kaybı; sorun tedarikçi değil, çelişkili belge sinyalinin eksikliği — başka tedarikçilerde de olur.
