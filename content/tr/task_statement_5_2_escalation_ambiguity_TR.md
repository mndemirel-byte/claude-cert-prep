# Task Statement 5.2: Eskalasyon ve Belirsizlik Çözümü (Escalation & Ambiguity Resolution)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir müşteri destek agent'ı her sorunu çözemez. Bazen insana yönlendirme (eskalasyon) gerekir. Ama **ne zaman** eskalasyon yapılacağını yanlış belirlemek ya aşırı eskalasyona (agent'ın işe yaramaz hale gelmesi) ya da yetersiz eskalasyona (müşteri memnuniyetsizliği) yol açar.

Bu task statement, **güvenilir** ve **güvenilmez** eskalasyon tetikleyicilerini ayırt etmeyi ve belirsiz durumlarda nasıl hareket edileceğini öğretir.

---

## Üç Geçerli Eskalasyon Tetikleyicisi

Sınavda bunlar "her zaman eskalasyon yap" senaryolarıdır:

### 1. Müşteri Açıkça İnsan Talep Ediyor

Müşteri "Bir insanla konuşmak istiyorum" dediğinde → **hemen eskalasyon yap.**

**KRİTİK:** Önce sorunu çözmeye ÇALIŞMA. Önce araştırma YAPMA. Müşterinin isteğini hemen yerine getir.

Bu, sınavda en sık test edilen tuzaktır:

> Müşteri: "Bir insanla konuşmak istiyorum."
> ❌ Agent: "Anlıyorum, ama önce sorununuzu çözmeye çalışayım..."
> ✅ Agent: "Hemen sizi bir temsilciye bağlıyorum."

### 2. Politika İstisnaları veya Boşlukları

Müşterinin talebi belgelenmiş politika kapsamı dışında kaldığında. Örneğin:

- Politika sadece kendi sitesindeki fiyat eşleştirmesini kapsıyor, müşteri rakip fiyat eşleştirmesi istiyor
- Politikada tanımlanmamış bir iade senaryosu (örneğin, hediye olarak alınmış ürün)
- Müşteri standart garanti süresini aşan bir talep yapıyor

Agent politika dışına çıkamaz — yetkisi yok. Eskalasyon gerekir.

### 3. Anlamlı İlerleme Sağlayamama

Agent sorunu çözmek için çaba gösterdi ama ilerleyemiyor:

- Araç sonuçları çelişkili
- Gerekli bilgiye erişilemiyor
- Agent'ın yetkisi dahilindeki tüm seçenekler tükenmiş

---

## İki Güvenilmez Tetikleyici — SINAV TUZAĞI

Bu iki tetikleyici sınavda **yanlış cevap seçeneği** olarak karşına çıkacak:

### 1. Duygu Bazlı Eskalasyon (Sentiment-Based)

**TUZAK:** "Müşteri kızgın → eskalasyon yap."

**Neden yanlış:** Hayal kırıklığı, vaka karmaşıklığıyla orantılı **DEĞİLDİR**. Müşteri çok kızgın olabilir ama sorun basit bir iade olabilir — agent sorunu 30 saniyede çözebilir.

Kızgınlık ≠ eskalasyon gereksinimi.

### 2. Model Güven Skoru (Self-Reported Confidence)

**TUZAK:** "Modelin güven skoru %40'ın altında → eskalasyon yap."

**Neden yanlış:** Model genellikle zor vakalarda **yanlışlıkla yüksek güven** bildirir, kolay vakalarda ise **gereksiz belirsizlik** gösterir. Model'in kendi güven değerlendirmesi güvenilir bir eskalasyon kriteri değildir.

---

## Hayal Kırıklığı Nüansı — Detaylı Karar Akışı

Bu konu sınavda ince ayrımlarla test ediliyor. Karar akışını tam olarak öğren:

### Senaryo A: Müşteri kızgın + sorun basit

Müşteri sinirli ama sorun agent'ın çözebileceği bir iade talebi.

→ **Eskalasyon YAPMA.** Hayal kırıklığını kabul et, çözümü sun:

> "Yaşadığınız rahatsızlık için özür dilerim. Siparişiniz için iadenizi hemen başlatabilirim."

### Senaryo B: Müşteri kızgın + agent çözüm sundu + müşteri yine insan istiyor

Agent çözüm sunmuş ama müşteri **tekrar** insan talep ediyor.

→ **Eskalasyon YAP.** Müşteri çözüm teklifinden sonra bile insan tercihini yineliyorsa, artık isteğini yerine getir.

### Senaryo C: Müşteri açıkça "insan istiyorum" diyor

Müşterinin ilk mesajı doğrudan insan talebi.

→ **Hemen eskalasyon YAP.** Araştırma yapma, çözüm sunma, soru sorma — doğrudan yönlendir.

### Karar Tablosu

| Durum | Eylem |
|---|---|
| Müşteri kızgın, sorun basit | Hayal kırıklığını kabul et + çözüm sun |
| Müşteri çözüm sonrası tekrar insan istiyor | Eskalasyon yap |
| Müşteri açıkça "insan istiyorum" diyor | HEMEN eskalasyon yap — araştırma yapma |
| Model güven skoru düşük | Eskalasyon tetikleyicisi olarak KULLANMA |
| Müşteri kızgın (sadece duygu) | Eskalasyon tetikleyicisi olarak KULLANMA |

---

## Belirsiz Müşteri Eşleştirme (Ambiguous Customer Matching)

### Problem

Bir müşteri "Ahmet Yılmaz" adıyla arama yapıyorsun. Sistem 3 farklı "Ahmet Yılmaz" döndürüyor.

### Yanlış Yaklaşım

Sezgisel (heuristic) seçim yapma:

- ❌ En son sipariş vereni seç
- ❌ En aktif hesabı seç
- ❌ Adres veya şehir bazlı tahmin yap

### Doğru Yaklaşım

Ek tanımlayıcı bilgi iste:

> "Hesabınızı doğrulamak için e-posta adresinizi, telefon numaranızı veya sipariş numaranızı paylaşabilir misiniz?"

**Kural:** Birden fazla eşleşme varsa → ek tanımlayıcı iste. Sezgisel seçim YAPMA.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Müşteri insan isterse | Hemen eskalasyon — önce çözme |
| Politika dışı talep | Eskalasyon — agent yetkisi yok |
| İlerleme sağlanamıyor | Eskalasyon — tüm seçenekler tükenmiş |
| Duygu bazlı eskalasyon | GÜVENİLMEZ — kızgınlık ≠ karmaşıklık |
| Model güven skoru | GÜVENİLMEZ — kalibrasyon zayıf |
| Kızgın müşteri + basit sorun | Çöz, eskalasyon yapma |
| Müşteri çözüm sonrası yine insan isterse | O zaman eskalasyon yap |
| Birden fazla müşteri eşleşmesi | Ek tanımlayıcı iste, sezgisel seçim yapma |

---

## Pratik Senaryo 1

> Bir müşteri destek agent'ı şu mantıkla çalışıyor: "Müşterinin mesajındaki duygu skoru -0.7'nin altına düşerse otomatik olarak insan temsilciye yönlendir."
>
> Son 100 eskalasyonun analizi şunu gösteriyor: eskalasyon edilen vakaların %65'i agent'ın 1 adımda çözebileceği basit iade talepleriydi. Müşteriler sadece hayal kırıklığını ifade ediyordu.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Duygu eşiğini -0.7'den -0.9'a düşür — daha az hassas hale getir.
>
> **B)** Duygu bazlı eskalasyonu kaldır. Yerine üç geçerli tetikleyici koy: müşteri açıkça insan isterse, politika dışı talep, anlamlı ilerleme sağlanamıyorsa.
>
> **C)** Duygu skorunu güven skoruyla birleştir — ikisi birden düşükse eskalasyon yap.
>
> **D)** Agent'a "müşteri kızgınsa önce sakinleştir, sonra eskalasyon yap" talimatı ekle.

### Doğru Cevap: B

**Neden B doğru:** Duygu bazlı eskalasyon güvenilmez bir tetikleyicidir — hayal kırıklığı vaka karmaşıklığıyla orantılı değildir. %65 yanlış eskalasyon bunu kanıtlıyor. Doğru çözüm: güvenilmez tetikleyiciyi kaldır, yerine üç geçerli tetikleyiciyi koy.

**Neden A yanlış:** Eşik ayarlama aynı yapısal sorunu devam ettirir. -0.9'da bile duygu skoru vaka karmaşıklığını ölçmez — bazı basit vakaları hâlâ yanlış eskalasyon eder.

**Neden C yanlış:** İki güvenilmez metriği birleştirmek güvenilir bir metrik oluşturmaz. Duygu skoru da güven skoru da eskalasyon kararı için güvenilmez.

**Neden D yanlış:** "Sakinleştir sonra eskalasyon yap" hâlâ duygu bazlı karar veriyor. Sorunun karmaşıklığını değerlendirmiyor.

---

## Pratik Senaryo 2

> Bir müşteri agent'a şunu yazıyor: "Sipariş #4412 için rakip sitedeki fiyatla eşleştirme istiyorum."
>
> Agent politika dokümanını kontrol ediyor. Politika şöyle diyor: "Kendi sitemizde aynı ürünün fiyatı düştüyse, fiyat farkını iade ederiz."
>
> Politikada rakip fiyat eşleştirmesi hakkında **hiçbir ifade yok.**
>
> **Agent ne yapmalı?**
>
> **A)** Politikayı geniş yorumlayarak rakip fiyat eşleştirmesini de kapsadığını varsay ve işlemi yap.
>
> **B)** Müşteriye "rakip fiyat eşleştirmesi yapamıyoruz" de ve konuşmayı sonlandır.
>
> **C)** Bu, politika boşluğu (policy gap) — agent yetkisi dışında. İnsan temsilciye eskalasyon yap ve müşteriye durumu açıkla.
>
> **D)** Müşterinin duygu durumuna göre karar ver — kızgınsa eskalasyon yap, sakinse reddet.

### Doğru Cevap: C

**Neden C doğru:** Politikada rakip fiyat eşleştirmesi tanımlanmamış — bu bir politika boşluğu. Agent politika dışına çıkamaz, ama talebi doğrudan reddetme yetkisi de net değil. Doğru hareket: eskalasyon yap, insan temsilci karar versin.

**Neden A yanlış:** Agent politikayı geniş yorumlama yetkisine sahip değil. Politika sadece kendi site fiyatını kapsıyor — bunu genişletmek agent'ın yetkisini aşar.

**Neden B yanlış:** Direkt reddetme müşteri deneyimini bozar ve agent'ın bu kararı verme yetkisi net değil. Politikada "rakip eşleştirmesi YAPILMAZ" yazmıyor — boşluk var.

**Neden D yanlış:** Duygu bazlı karar — güvenilmez tetikleyici. Eskalasyon kararı duyguya değil, politika boşluğuna dayanmalı.
