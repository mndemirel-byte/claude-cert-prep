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

### Çözüm: Bağımsız Instance

```
Instance A → Belgeyi analiz eder → Çıkarım X
Instance B → Belgeyi BAĞIMSIZ olarak inceler (X'i görmeden)
           VEYA
Instance B → Belge + X'i görür ama kendi oturumunda, A'nın bağlamı olmadan

Fark: B, A'nın gözden kaçırdığı tutarsızlıkları daha büyük olasılıkla yakalar
```

---

## Çok Geçişli Mimari (Multi-Pass Architecture)

Büyük bir kod tabanını analiz ediyorsun. Tek geçişte tüm dosyaları verirsen ne olur?

### Tek Geçiş Problemi

```
Sorun: Dikkat seyreltmesi (attention dilution)
- 50 dosya tek seferde veriliyor
- Model erken dosyalara daha fazla dikkat eder
- Geç dosyalar yüzeysel analiz alır
- Çelişkili bulgular (dosya A'da X güvenli, dosya B'de X tehlikeli) fark edilmeyebilir
```

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

---

## Güven Tabanlı Yönlendirme (Confidence-Based Routing)

Her bulgu eşit değildir. Bazı bulgular açık, bazıları belirsiz.

### Yapı

Modelden her bulgu için kendi güvenini raporlamasını iste:

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
1. Etiketlenmiş doğrulama seti oluştur (güvenlik uzmanı incelemeli 100 bulgu)
2. Model'in güven seviyelerini gerçek sonuçlarla karşılaştır
3. Optimal eşiği bul: "medium" güven → %X hata oranı

Sonuç: Güven eşikleri somut hata oranlarına dayanır — sezgiye değil
```

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

---

## Sınavın Tuzağı: "Aynı Model Kendi Çıktısını İnceleyebilir"

Sınav şöyle bir seçenek sunar:

> *"Maliyet azaltmak için aynı model oturumunda hem extraction hem doğrulama adımı çalıştırıyoruz."*

**Bu yaklaşımın sorunu:**
- Aynı oturum = aynı bağlam = aynı kör noktalar
- Model kendi önceki muhakemesini doğal buluyor
- Bağımsız incelemenin faydası ortadan kalkıyor

**Doğru yaklaşım:**
- İnceleme için **ayrı API çağrısı** (bağımsız bağlam)
- Yüksek riskli bulgular için **farklı system prompt** ile ikinci instance
- Kritik kararlar için **insan doğrulaması**

---

## Tam Mimari: CI/CD Kod İnceleme Pipeline'ı

```
PR Açıldı
│
├─ [Paralel] Dosya bazlı analiz (N instance, her biri 1 dosya)
│   ├─ src/auth.py → {bulgular, güven}
│   ├─ src/api.py  → {bulgular, güven}
│   └─ src/db.py   → {bulgular, güven}
│
├─ [Çapraz dosya] Entegrasyon analizi (bağımsız instance)
│   ├─ Veri akışı kontrolü
│   ├─ Çelişki tespiti
│   └─ Sistem geneli örüntüler
│
├─ [Yönlendirme] Güven tabanlı sıralama
│   ├─ Yüksek güven → Otomatik işaretleme
│   └─ Düşük güven → İnsan inceleme kuyruğu
│
└─ [Çıktı] PR yorumu + öncelikli bulgular listesi
```

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Self-review sınırlıdır** — aynı oturum, aynı kör noktalar. |
| 2 | **Bağımsız instance** önceki bağlam taşımadan daha fazla ince sorunu yakalar. |
| 3 | **Dosya başına analiz** dikkat seyreltmesini önler — her dosya tam dikkat alır. |
| 4 | **Çapraz dosya entegrasyon geçişi** veri akışı ve çelişki sorunlarını yakalar. |
| 5 | **Güven tabanlı yönlendirme:** yüksek güven → otomatik, düşük güven → insan. |
| 6 | **Güven eşikleri etiketlenmiş doğrulama setiyle kalibre edilir** — sezgi değil. |
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

Büyük bir kod tabanını (50 dosya) analiz etmek için en iyi mimari nedir?

**A)** Tüm 50 dosyayı tek instance'a tek seferde ver  
**B)** Her dosyayı ayrı instance'da analiz et, ardından bağımsız çapraz dosya entegrasyon geçişi çalıştır  
**C)** En büyük 10 dosyayı analiz et, gerisini atla  
**D)** Dosyaları 5'erli gruplara böl, her grup için ayrı batch gönder  

**✅ Cevap: B**

*Açıklama:* Tek seferde 50 dosya → dikkat seyreltmesi, tutarsız derinlik. Dosya başına analiz her dosyaya eşit dikkat sağlar. Çapraz dosya geçişi ise veri akışı ve dosyalar arası çelişkileri yakalar. Bu iki aşamalı mimari her iki sorunu da çözer.

---

### Soru 3

Güven tabanlı yönlendirmede güven eşikleri nasıl kalibre edilmeli?

**A)** Geliştirici sezgisine dayanarak belirlenir  
**B)** Model'in önerisine göre ayarlanır  
**C)** Etiketlenmiş doğrulama seti üzerinden güven seviyeleri gerçek sonuçlarla karşılaştırılır  
**D)** Sektör standardı eşikleri kullanılır (%80 güven = yüksek)  

**✅ Cevap: C**

*Açıklama:* "Medium güven → insan incelemesi" kararı sezgiye değil veriye dayanmalıdır. Güvenlik uzmanlarının doğruladığı etiketlenmiş bulgular üzerinden model güven seviyelerinin gerçek hata oranlarıyla korelasyonu ölçülür. Bu somut eşik verir.

---

### Soru 4

Dosya A'da "rate limiting yok — kritik" bulgusu var. Çapraz dosya geçişi dosya B'de genel rate limiting middleware'i buluyor. Bu nasıl ele alınmalı?

**A)** Dosya A'daki bulguyu otomatik kapat — middleware mevcut  
**B)** Middleware atlanabilir mi? Belirsizlik var → conflict_detected: true ile işaretle, insan incelesin  
**C)** Her iki bulguyu da raporla, çelişkiyi yoksay  
**D)** Dosya A'yı yeniden analiz et, retry döngüsü başlat  

**✅ Cevap: B**

*Açıklama:* Middleware'in auth endpoint'ini kapsayıp kapsamadığı otomatik olarak belirlenemiyor. Bu tür belirsizliklerde `conflict_detected: true` ile işaretleyip insan incelemesine yönlendirmek doğru yaklaşımdır. Otomatik kapatmak (A) güvenlik riski yaratır; yoksaymak (C) çelişkiyi çözmez.
