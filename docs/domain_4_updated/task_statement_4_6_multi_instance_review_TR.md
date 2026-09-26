# Task Statement 4.6: Çok Örnekli İnceleme (Multi-Instance Review)

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Bir model kendi çıktısını kendi oturumunda incelerse, özgün bağlamını taşıdığından aynı hataları gözden kaçırması yüksek ihtimaldir. Çözüm: **bağımsız bir instance, önceki bağlam olmadan yeniden inceler.**

Bu, yazılım geliştirmede "kendi kodunu kendi gözden geçirme" sorununa benzer — bir insan da bunu iyi yapamaz.

---

## Self-Review'un Sınırlaması

### Senaryo

Bir model karmaşık bir fatura belgesini analiz etti ve 8 satır kalemi çıkardı. Şimdi aynı modelden kendi çıkarımını doğrulaması isteniyor.

### Neden Başarısız Olur?

```
Model kendi analizine baktığında:
- Orijinal belgeyi oluştururken kullandığı bağlam hâlâ aktif
- "Bu yorumu ben yaptım, o zaman makul görünüyordu" eğilimi
- Kendi mantık hataları doğal görünür — çünkü o mantıkla oluşturdu
- Kaçırdığı bilgiler yeniden kaçırılabilir — dikkat aynı yerlere gider

Sonuç: Kendi çıktısını incelerken ince hataları atlama ihtimali yüksek
```

Exam guide'ın cümlesi: "*a model retains reasoning context from generation, making it less likely to question its own decisions in the same session*".

### Üç seçenek — sınavın karşılaştırdığı üçlü

Exam guide bağımsız instance'ı iki şeyle karşılaştırır: "*more effective … than **self-review instructions** or **extended thinking***". Sınav şıkları tam olarak bu üçlüdür:

| Yaklaşım | Ne yapar | Neden yetmez |
|----------|----------|--------------|
| **Self-review talimatı** ("Cevabını dikkatlice gözden geçir, hataları düzelt") | Aynı oturumda ikinci bir bakış ister | Aynı bağlam, aynı kör noktalar; model kendi akıl yürütmesini "doğrulanmış" sayar |
| **Extended thinking** (thinking'i aç / bütçesini artır) | Aynı oturumda daha uzun düşünür | Daha uzun düşünmek *farklı* düşünmek değildir; thinking üretim bağlamının **içinde** çalışır, dışında değil. "Daha fazla düşünme = daha fazla doğrulama" sınavın tuzağıdır |
| **Bağımsız instance** (ayrı API çağrısı, üretim akıl yürütmesi olmadan) | Çıktıyı sıfır bağlamla görür | ✅ Üretimin varsayımlarını miras almaz; ince tutarsızlıkları yakalar |

**Kural:** Doğrulama sorununu *aynı oturumda daha fazla şey yaparak* (talimat, thinking) çözemezsin; *bağlamı değiştirerek* çözersin.

### Çözüm: Bağımsız Instance

```
Instance A → Belgeyi analiz eder → Çıkarım X

Bağımsız inceleme (exam guide'ın tanımı):
Instance B → Belge + X'i görür; ama A'nın AKIL YÜRÜTMESİNİ görmez
             (ayrı API çağrısı; A'nın konuşma geçmişi / thinking'i yok)
→ B, "X doğru mu?" sorusuna A'nın varsayımlarını miras almadan bakar

Alternatif teknik — çift çıkarım + fark alma:
Instance B → Belgeyi X'i HİÇ GÖRMEDEN bağımsız çıkarır → Çıkarım Y
→ X ≠ Y olan alanlar insan incelemesine gider
(Bu "inceleme" değil "yeniden üretim"dir; daha pahalı, alan-bazlı uyuşmazlık verir)
```

Sınavın Skills maddesi birincisidir: "*Using a second independent Claude instance to review generated code **without the generator's reasoning context***" — inceleyici *çıktıyı görür*, *akıl yürütmeyi görmez*.

### Farklı rol / system prompt ile ikinci instance

Bağımsızlığı bir adım ileri götürmek için inceleyiciye **farklı bir rol** verilir — "adversarial reviewer":

```
System (inceleyici): "Sen bir denetçisin. Aşağıdaki çıkarımın HATALI olduğunu varsay.
Her alan için belgede kanıt ara; kanıt bulamadığın her değeri 'doğrulanamadı' olarak işaretle.
Çıkarımı yapan modelin gerekçesini görmüyorsun — yalnızca belge ve sonuç var."
```

Domain 3.6'daki Writer/Reviewer kalıbı ve "inceleyici yalnızca diff'i görür, onu üreten akıl yürütmeyi görmez" ilkesiyle aynı şey; Domain 1.3'te subagent'ların temiz bağlamla başlaması da aynı ilkenin orkestrasyon hâli.

---

## Çok Geçişli Mimari (Multi-Pass Architecture)

Büyük bir kod tabanını analiz ediyorsun. Tek geçişte tüm dosyaları verirsen ne olur?

### Tek Geçiş Problemi

```
Sorun: Dikkat seyreltmesi (attention dilution)
- 50 dosya tek seferde veriliyor
- Model erken dosyalara daha fazla dikkat eder
- Geç dosyalar yüzeysel analiz alır
- Aynı kalıp dosya A'da işaretlenir, dosya B'de atlanır → ÇELİŞKİLİ geri bildirim
- Bariz hatalar kaçar

Belirtiler (exam guide Q12): "bazı dosyalara ayrıntılı, bazılarına yüzeysel yorum;
bariz hatalar kaçmış; birbiriyle çelişen geri bildirim"
```

**Kelime uyarısı:** "Çelişkili bulgu" bu bölümde tek geçişin *belirtisi*; aşağıdaki "Çelişkili Bulgular" bölümünde ise çapraz geçişin *bilerek ürettiği* bir çıktı (iki instance'ın farklı kararı işaretlenir). Aynı kelime, iki farklı anlam.

### Çok Geçişli Çözüm

```
Aşama 1: Dosya başına yerel analiz
  - Her dosya ayrı ayrı analiz edilir
  - Tutarlı derinlik garantisi — her dosya tam dikkat alır
  - Çıktı: Dosya başına bulgular

Aşama 2: Çapraz dosya entegrasyon geçişi
  - Ayrı bir instance, tüm dosya bulgularını görür
  - Veri akışı sorunlarını tespit eder (A'da temizlenen veri B'de temiz mi?)
  - Çelişkili bulguları işaretler
  - Sistem düzeyinde örüntüleri yakalar
```

```python
def multi_pass_review(files: dict) -> dict:
    
    # Aşama 1: Dosya başına yerel analiz
    file_findings = {}
    for filename, content in files.items():
        findings = analyze_file(filename, content)  # Ayrı instance
        file_findings[filename] = findings
    
    # Aşama 2: Çapraz dosya entegrasyon
    integration_findings = cross_file_analysis(file_findings)  # Ayrı instance
    
    return {
        "per_file": file_findings,
        "cross_file": integration_findings,
        "total_findings": merge_and_deduplicate(file_findings, integration_findings)
    }
```

**Maliyet ve paralellik:** N dosya = N çağrı. İnceleme bloklamıyorsa (gece auditi) Aşama 1'in N çağrısı **tek batch** olarak gönderilir (Task 4.5, %50), Aşama 2 batch bitince tek çağrıdır. Bloklayan PR incelemesinde N çağrı senkron ve paralel yapılır. "Her belge için 50 instance" gibi bir tasarım ise maliyet sezgisinin yokluğudur — geçiş sayısı dosya sayısına, belge sayısına değil bağlıdır.

### Q12'nin distractor'ları — neden yanlış?

| Şık | Neden çekici | Neden yanlış |
|-----|--------------|--------------|
| "Daha küçük PR iste" | Kök nedene dokunuyor gibi | Süreç değişikliği; 14 dosyalık meşru PR'lar olur. İnceleme mimarisi PR boyutuna bağımlı olmamalı |
| "Daha büyük bağlam penceresi olan model" | "Sığmıyor" sanılır | Dosyalar zaten sığıyor; sorun *dikkat*, pencere boyutu değil. Daha büyük pencere seyreltmeyi artırabilir |
| "Aynı incelemeyi 3 kez çalıştır, çoğunluk oyu (consensus voting)" | Tutarsızlığı istatistikle çözüyor gibi | Üç geçiş de aynı seyreltmeyi yaşar; çoğunluk, tutarsızlığı *maskeler*, çelişkinin nedenini çözmez; maliyet 3× |
| **"Dosya başına yerel geçiş + ayrı entegrasyon geçişi"** | — | ✅ Kök neden (attention dilution) doğrudan giderilir |

---

## Güven Tabanlı Yönlendirme (Confidence-Based Routing)

Her bulgu eşit değildir. Bazı bulgular açık, bazıları belirsiz.

### Yapı

Modelden her bulgu için kendi güvenini raporlamasını iste — **enum olarak, yüzde olarak değil**:

```json
{
  "finding_id": "SEC-003",
  "description": "Potansiyel kimlik doğrulama atlatma",
  "severity": "critical",
  "confidence": "low",
  "confidence_reason": "Kod karmaşık; kimlik doğrulama mantığı tam analiz için bağlam eksik",
  "recommendation": "Güvenlik uzmanı incelemesi gerekli"
}
```

Neden enum? Modelin self-reported güveni **kalibre değildir**; "%83" sahte kesinlik verir ve seni Task 4.1'deki "güven eşiği" tuzağına geri götürür. `high/medium/low` + `confidence_reason`, kalibrasyon setiyle (aşağıda) anlamlı hale getirilir. `confidence_reason`, Task 4.4'teki `detected_pattern` gibi bir **geri besleme alanı**dır: sık görülen düşük-güven nedenleri → 4.1 kriterine / 4.2 örneğine geri döner.

### Alan bazlı güven (extraction için)

Kod incelemede güven *bulgu* başınadır. Belge çıkarımında ise **alan** başına raporlanır — Hazırlık Egzersizi 3 adım 15: "*field-level confidence scores, route low-confidence extractions to human review, and analyze accuracy **by document type and field***".

```json
{
  "invoice_number": {"value": "INV-2024-117", "confidence": "high"},
  "payment_due_date": {"value": "2024-02-15", "confidence": "low",
                       "confidence_reason": "Belgede iki farklı tarih var; hangisi vade belirsiz"},
  "total_amount": {"value": 125050, "confidence": "high"}
}
```

Yönlendirme bulgu değil **alan** düzeyinde yapılır: `payment_due_date` insan kuyruğuna gider, diğer alanlar otomatik geçer — tüm belge değil.

### Yönlendirme Mantığı

```python
def route_findings(findings: list) -> dict:
    auto_approve = []
    human_review = []
    
    for finding in findings:
        if finding["confidence"] == "high":
            auto_approve.append(finding)  # Pipeline'a devam
        elif finding["confidence"] in ["medium", "low"]:
            human_review.append(finding)   # İnsan incelemesi kuyruğu
    
    return {
        "automated": auto_approve,
        "human_review": human_review
    }
```

### Güven Eşiği Kalibrasyonu

```
Nasıl kalibre edilir?
1. Etiketlenmiş doğrulama seti oluştur (güvenlik uzmanı incelemeli 100 bulgu /
   muhasebe tarafından doğrulanmış 100 fatura)
2. Model'in güven seviyelerini gerçek sonuçlarla karşılaştır
3. Optimal eşiği bul: "medium" güven → %X hata oranı

Sonuç: Güven eşikleri somut hata oranlarına dayanır — sezgiye değil
```

**Belge tipi × alan doğruluk matrisi** (Egzersiz 3 adım 15): kalibrasyon toplu bir sayı değil, bir tablodur —

| | `total_amount` | `payment_due_date` | `line_items` |
|---|---|---|---|
| Tablo formatlı fatura | %98 | %95 | %97 |
| Düz metin fatura | %91 | **%71** | %84 |
| İç içe liste | %95 | %88 | **%76** |

Bu tablo iki karar verdirir: (1) hangi hücreler için "high" güvene rağmen insan kontrolü gerekir, (2) **hangi format için few-shot örneği eklenmeli** (Task 4.2 — "düz metin + vade tarihi" örneği). Bu, Task 4.1'deki eval setiyle aynı settir; Domain 4'ün kapalı döngüsü buradan geçer.

---

## Çelişkili Bulgular — Aynı Kod, Farklı Instance Kararları

```
Instance A: auth.py → "rate limiting yok, kritik"
Instance B (çapraz dosya geçişi): middleware.py'de rate limiting görüldü
→ auth.py bulgusu: yanlış alarm mı, yoksa middleware atlanabilir mi?

Bu çelişki otomatik işaretlenir:
{
  "conflict_detected": true,
  "finding_a": "auth.py: rate limiting yok — kritik",
  "finding_b": "middleware.py: genel rate limiting var",
  "resolution": "human_review",
  "conflict_reason": "Middleware'in auth endpoint'ini kapsayıp kapsamadığı belirsiz"
}
```

Bu, çapraz geçişin *istenen* çıktısıdır — Task 4.4'teki `conflict_detected` + açıklama deseninin aynısı.

---

## Sınavın Tuzağı: "Aynı Model Kendi Çıktısını İnceleyebilir"

Sınav şöyle seçenekler sunar:

> *"Maliyet azaltmak için aynı model oturumunda hem extraction hem doğrulama adımı çalıştırıyoruz."*
> *"Doğruluğu artırmak için extraction çağrısında extended thinking'i açıp bütçeyi 10k token'a çıkardık."*

**Bu yaklaşımların sorunu:**
- Aynı oturum = aynı bağlam = aynı kör noktalar
- Model kendi önceki muhakemesini doğal buluyor
- Thinking daha uzun düşündürür, *başka bir açıdan* düşündürmez
- Bağımsız incelemenin faydası ortadan kalkıyor

**Doğru yaklaşım:**
- İnceleme için **ayrı API çağrısı** (bağımsız bağlam, üreticinin akıl yürütmesi yok)
- Yüksek riskli bulgular için **farklı system prompt** (adversarial reviewer) ile ikinci instance
- Kritik kararlar için **insan doğrulaması** (güven yönlendirmesiyle)

---

## Tam Mimari: CI/CD Kod İnceleme Pipeline'ı

```
PR Açıldı
│
├─ [Paralel] Dosya bazlı analiz (N instance, her biri 1 dosya)
│   ├─ src/auth.py → {bulgular, güven, confidence_reason}
│   ├─ src/api.py  → {bulgular, güven, confidence_reason}
│   └─ src/db.py   → {bulgular, güven, confidence_reason}
│
├─ [Çapraz dosya] Entegrasyon analizi (bağımsız instance, dosya bulgularını görür)
│   ├─ Veri akışı kontrolü
│   ├─ Çelişki tespiti (conflict_detected)
│   └─ Sistem geneli örüntüler
│
├─ [Yönlendirme] Güven tabanlı sıralama
│   ├─ Yüksek güven → Otomatik işaretleme
│   └─ Düşük/orta güven → İnsan inceleme kuyruğu
│
└─ [Çıktı] PR yorumu + öncelikli bulgular listesi
    └─ [Geri besleme] dismiss edilen bulgular + detected_pattern + confidence_reason
        → 4.1 kriter / 4.2 örnek güncellemesi → eval setinde ölçüm
```

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Self-review sınırlıdır** — aynı oturum, aynı kör noktalar. Self-review *talimatı* da **extended thinking** de bunu çözmez; bağlamı değiştirmek çözer. |
| 2 | **Bağımsız instance** çıktıyı görür, üreticinin *akıl yürütmesini* görmez; adversarial rol ile daha etkili. |
| 3 | **Dosya başına analiz** dikkat seyreltmesini önler — her dosya tam dikkat alır. Daha büyük bağlam penceresi veya çoğunluk oyu bunu çözmez. |
| 4 | **Çapraz dosya entegrasyon geçişi** veri akışı ve çelişki sorunlarını yakalar. Bloklamayan incelemede Aşama 1 tek batch olabilir. |
| 5 | **Güven tabanlı yönlendirme:** enum güven (`high/medium/low`) + `confidence_reason`; yüksek → otomatik, düşük → insan. Extraction'da **alan** bazlı. |
| 6 | **Güven eşikleri etiketlenmiş doğrulama setiyle kalibre edilir** — belge tipi × alan matrisi; sezgi değil. |
| 7 | **Çelişkili bulgular** `conflict_detected: true` ile işaretlenir, insan inceler. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Bir kod inceleme sistemi her çıkarımı aynı Claude oturumunda doğruluyor. Hangi temel sorunu yaşar?

**A)** Doğrulama adımı çok pahalıdır  
**B)** Model kendi muhakeme bağlamını taşıdığından aynı hataları gözden kaçırabilir  
**C)** Aynı oturumda iki çağrı yapılamaz  
**D)** Çıktı formatı değişir  

**✅ Cevap: B**

*Açıklama:* Aynı oturumdaki model, ilk çıkarımı oluştururken kullandığı bağlamı taşır. Bu bağlam nedeniyle kendi hatalarını "makul" bulma eğilimi artar. Bağımsız instance bu bağlamı taşımaz ve ince tutarsızlıkları daha iyi yakalar.

---

### Soru 2

14 dosyalık bir PR'ın tek geçişli incelemesinde bazı dosyalara ayrıntılı, bazılarına yüzeysel yorum geliyor; bariz bir hata kaçmış ve iki dosya için çelişkili geri bildirim var. En iyi yeniden yapılandırma nedir?

**A)** Daha büyük bağlam penceresine sahip bir model kullan — tüm dosyalar rahat sığsın  
**B)** Her dosyayı ayrı geçişte yerel sorunlar için analiz et, ardından çapraz dosya veri akışına odaklanan ayrı bir entegrasyon geçişi çalıştır  
**C)** Aynı incelemeyi üç kez çalıştır, çoğunluğun işaretlediği bulguları raporla  
**D)** Geliştiricilerden daha küçük PR açmalarını iste  

**✅ Cevap: B**

*Açıklama:* Exam guide Q12. Belirtiler (tutarsız derinlik, kaçan bariz hata, çelişkili geri bildirim) **attention dilution**'ın belirtileridir; kök nedeni yalnızca geçişi bölmek giderir. (A) sorun sığma değil dikkat — pencere büyüyünce seyreltme artabilir. (C) üç geçiş de aynı seyreltmeyi yaşar; çoğunluk tutarsızlığı maskeler, 3× maliyet. (D) inceleme mimarisini PR boyutuna bağımlı kılar; meşru büyük PR'lar olur.

---

### Soru 3

Güven tabanlı yönlendirmede güven eşikleri nasıl kalibre edilmeli?

**A)** Geliştirici sezgisine dayanarak belirlenir  
**B)** Model'in önerisine göre ayarlanır  
**C)** Etiketlenmiş doğrulama seti üzerinden güven seviyeleri gerçek sonuçlarla karşılaştırılır  
**D)** Sektör standardı eşikleri kullanılır (%80 güven = yüksek)  

**✅ Cevap: C**

*Açıklama:* "Medium güven → insan incelemesi" kararı sezgiye değil veriye dayanmalıdır. Güvenlik uzmanlarının doğruladığı etiketlenmiş bulgular üzerinden model güven seviyelerinin gerçek hata oranlarıyla korelasyonu ölçülür. Bu somut eşik verir — ve belge tipi × alan matrisi hangi hücrelerin zayıf olduğunu gösterir.

---

### Soru 4

Dosya A'da "rate limiting yok — kritik" bulgusu var. Çapraz dosya geçişi dosya B'de genel rate limiting middleware'i buluyor. Bu nasıl ele alınmalı?

**A)** Dosya A'daki bulguyu otomatik kapat — middleware mevcut  
**B)** Middleware atlanabilir mi? Belirsizlik var → conflict_detected: true ile işaretle, insan incelesin  
**C)** Her iki bulguyu da raporla, çelişkiyi yoksay  
**D)** Dosya A'yı yeniden analiz et, retry döngüsü başlat  

**✅ Cevap: B**

*Açıklama:* Middleware'in auth endpoint'ini kapsayıp kapsamadığı otomatik olarak belirlenemiyor. Bu tür belirsizliklerde `conflict_detected: true` ile işaretleyip insan incelemesine yönlendirmek doğru yaklaşımdır. Otomatik kapatmak (A) güvenlik riski yaratır; yoksaymak (C) çelişkiyi çözmez.

---

### Soru 5

Bir extraction pipeline'ında modelin ince hataları kaçırdığı görülüyor. Üç öneri masada: (1) prompt'a "çıktını dikkatlice gözden geçir ve düzelt" talimatı ekle, (2) extended thinking'i açıp bütçeyi artır, (3) çıkarımı, üreticinin akıl yürütmesini görmeyen ayrı bir Claude çağrısına doğrulat. Hangisi en etkilidir ve neden?

**A)** (2) — daha fazla düşünme bütçesi daha fazla doğrulama demektir  
**B)** (1) — en ucuzu ve model kendi çıktısını en iyi bilir  
**C)** (3) — üretim bağlamını taşımayan bağımsız instance, self-review talimatı ve thinking'in aksine kendi varsayımlarını miras almaz  
**D)** (1) ve (2) birlikte — talimat + thinking bağımsız instance kadar etkilidir ve daha ucuzdur  

**✅ Cevap: C**

*Açıklama:* Exam guide: "*Independent review instances … are more effective at catching subtle issues than self-review instructions or extended thinking*". (A) thinking aynı bağlamın *içinde* daha uzun düşünür; farklı açı sağlamaz. (B) "kendi çıktısını en iyi bilir" tam olarak sorunun kaynağıdır. (D) iki yetersiz yöntemi toplamak bağlam sorununu çözmez.
