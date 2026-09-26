# Task Statement 5.2: Eskalasyon ve Belirsizlik Çözümü (Escalation & Ambiguity Resolution)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir müşteri destek agent'ı her sorunu çözemez. Bazen insana yönlendirme (eskalasyon) gerekir. Ama **ne zaman** eskalasyon yapılacağını yanlış belirlemek ya aşırı eskalasyona (agent'ın işe yaramaz hale gelmesi) ya da yetersiz eskalasyona (politika ihlali, müşteri memnuniyetsizliği) yol açar.

Sınav senaryosu (**Customer Support Resolution Agent**): agent Agent SDK ile kurulmuş, arka uca `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human` MCP araçlarıyla erişiyor; hedef **%80+ ilk temasta çözüm (first-contact resolution, FCR)** "*while knowing when to escalate*". Eskalasyon kalibrasyonu bu metrikle ölçülür: aşırı eskalasyon FCR'yi düşürür, yetersiz eskalasyon yanlış çözüm ve politika ihlali üretir.

Bu task statement üç şeyi öğretir: **güvenilir** ve **güvenilmez** eskalasyon tetikleyicilerini ayırt etmek, kriterleri agent'a **nasıl öğreteceğini** (few-shot) ve belirsiz durumlarda nasıl hareket edileceğini.

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

### 2. Politika İstisnaları veya Boşlukları — "karmaşık vaka" değil

Müşterinin talebi belgelenmiş politika kapsamı dışında kaldığında. Örneğin:

- Politika sadece kendi sitesindeki fiyat eşleştirmesini kapsıyor, müşteri **rakip fiyat eşleştirmesi** istiyor (exam guide'ın kendi örneği)
- Politikada tanımlanmamış bir iade senaryosu (örneğin, hediye olarak alınmış ürün)
- Müşteri standart garanti süresini aşan bir talep yapıyor

Agent politika dışına çıkamaz — yetkisi yok. Eskalasyon gerekir.

**Exam guide'ın parantezi:** *"policy exceptions/gaps (**not just complex cases**)"*. Yani **karmaşıklık tek başına tetikleyici değildir.** Karmaşık ama politika *içindeki* vaka (üç kalemli kısmi iade, iki siparişin birleştirilmesi) agent'ın işidir. Tetikleyici olan *politika dışılık*tır, zorluk değil.

### 3. Anlamlı İlerleme Sağlayamama

Agent sorunu çözmek için çaba gösterdi ama ilerleyemiyor:

- Araç sonuçları çelişkili
- Gerekli bilgiye erişilemiyor (erişim hatası — önce yerel retry, bkz. 5.3)
- Müşteriden ek bilgi istendi, hâlâ eşleşme yok (geçerli boş sonuç — aşağıda)
- Agent'ın yetkisi dahilindeki tüm seçenekler tükenmiş

Bu tetikleyici 5.3'ün "erişim hatası vs geçerli boş sonuç" ayrımıyla aynı ağaçtır: erişim hatası → sınırlı retry → hâlâ yoksa eskalasyon; geçerli boş sonuç → müşteriden ek tanımlayıcı → hâlâ yoksa eskalasyon. "İlerleyemiyorum" ancak bu adımlar denenince doğrudur.

---

## İki Güvenilmez Tetikleyici — SINAV TUZAĞI

Bu iki tetikleyici sınavda **yanlış cevap seçeneği** olarak karşına çıkacak:

### 1. Duygu Bazlı Eskalasyon (Sentiment-Based)

**TUZAK:** "Müşteri kızgın → eskalasyon yap."

**Neden yanlış:** Hayal kırıklığı, vaka karmaşıklığıyla orantılı **DEĞİLDİR**. Müşteri çok kızgın olabilir ama sorun basit bir iade olabilir — agent sorunu 30 saniyede çözebilir. Exam guide'ın gerekçesi: duygu analizi "*solves a different problem entirely; sentiment doesn't correlate with case complexity*".

Kızgınlık ≠ eskalasyon gereksinimi.

### 2. Model Güven Skoru (Self-Reported Confidence)

**TUZAK:** "Modelin bildirdiği güven skoru %40'ın altında → eskalasyon yap."

**Neden yanlış:** LLM'in kendi güven bildirimi **kalibre değildir** — guide: "*the agent is already incorrectly confident on hard cases*". Model zor vakalarda yanlışlıkla yüksek güven bildirir, kolay vakalarda gereksiz belirsizlik gösterir. Kendi güven değerlendirmesi güvenilir bir eskalasyon kriteri değildir.

(5.5'te kalibre edilmiş alan-bazlı güvenin *inceleme yönlendirmesi* için kullanılabildiğini göreceksin — fark **kalibrasyon**dur. Burada söz konusu olan ham, kalibrasyonsuz skordur.)

---

## Kriterler Nasıl Öğretilir? — Few-Shot Örnekli Açık Kriterler

Tetikleyicileri bilmek yetmez; agent'ın bunları **uygulaması** gerekir. Exam guide'ın Skills maddesi: *"Adding explicit escalation criteria **with few-shot examples** to the system prompt demonstrating when to escalate versus resolve autonomously"*.

### Resmi örnek soru (Exam Guide Q3)

> Agent'ın FCR'si %55, hedef %80. Loglar agent'ın **basit** vakaları (fotoğraf kanıtlı standart hasar değişimi) eskalasyon ederken **karmaşık** vakaları (politika istisnası gerektirenler) kendi başına çözmeye çalıştığını gösteriyor. Eskalasyon kalibrasyonunu iyileştirmenin en etkili yolu nedir?
>
> **A)** System prompt'a, ne zaman eskalasyon yapılıp ne zaman özerk çözüleceğini gösteren **few-shot örnekli açık eskalasyon kriterleri** ekle.
> **B)** Agent her yanıttan önce 1–10 arası güven skoru bildirsin; eşiğin altında otomatik olarak insana yönlendir.
> **C)** Geçmiş biletlerle eğitilmiş **ayrı bir sınıflandırıcı model** kur; ana agent başlamadan hangi taleplerin eskalasyon gerektirdiğini tahmin etsin.
> **D)** Duygu analizi ile hayal kırıklığını tespit et; olumsuz duygu eşiği aşınca otomatik eskalasyon yap.
>
> **Doğru cevap: A.** Guide'ın gerekçesi: kök neden **belirsiz karar sınırları**; few-shot örnekli açık kriterler bunu doğrudan çözer ve "*the proportionate first response before adding infrastructure*"dır. B: self-reported güven kalibre değil. C: etiketli veri + ML altyapısı gerektirir, prompt optimizasyonu denenmeden **over-engineering**. D: farklı bir sorunu çözer; duygu karmaşıklıkla korele değil.

Senaryoda kalibrasyon **iki yönde** bozuk: basitleri eskalasyon, karmaşıkları özerk. Tek bir eşik bunu düzeltemez; ancak *örnekler* iki sınırı da gösterir.

### Orantılılık merdiveni

Domain 1 ve 4'teki ilkeyle aynı: **önce prompt, sonra altyapı.**

```
1. System prompt'a açık kriterler + few-shot örnekler   ← ilk müdahale (Q3-A)
2. Kriterlerin dayandığı politika verisini araçla sağla (politika lookup aracı)
3. Ölç: FCR, gereksiz eskalasyon oranı, politika ihlali sayısı (etiketli örnek set)
4. Hâlâ yetmiyorsa: ayrı sınıflandırıcı / yönlendirme katmanı   ← son çare (Q3-C)
```

### Örnek system prompt bloğu

```xml
<escalation_criteria>
ESKALASYON YAP:
- Müşteri açıkça insan temsilci istiyorsa (araştırma yapmadan, hemen)
- Talep yazılı politikada tanımlı değilse veya politika sessizse
- Çözüm için gerekli bilgiye ulaşılamıyor ve ek tanımlayıcı istendiği halde eşleşme yoksa

KENDİN ÇÖZ:
- Talep politikada tanımlıysa — müşteri kızgın olsa bile
- Vaka karmaşık ama her adımı politika içindeyse
</escalation_criteria>

<examples>
<example>
<request>Ürün kırık geldi, fotoğrafını ekliyorum, değişim istiyorum.</request>
<decision>RESOLVE</decision>
<why>Fotoğraf kanıtlı standart hasar değişimi politikanın 3.2 maddesi; araç: process_replacement</why>
</example>
<example>
<request>Rakip sitede 20$ daha ucuz, farkı iade edin.</request>
<decision>ESCALATE</decision>
<why>Politika yalnızca kendi site fiyat düşüşlerini kapsıyor; rakip eşleştirmesi tanımsız → policy gap</why>
</example>
<example>
<request>Bu üçüncü mesajım, artık bir insanla konuşmak istiyorum!</request>
<decision>ESCALATE_IMMEDIATELY</decision>
<why>Açık insan talebi; araştırma yapma, çözüm önerme</why>
</example>
<example>
<request>Sinir krizi geçireceğim, siparişim 3 gündür gelmedi!!!</request>
<decision>RESOLVE</decision>
<why>Duygu yoğun ama talep basit: kargo durumu sorgula, tahmini teslimatı ver; kızgınlık tetikleyici değil</why>
</example>
</examples>
```

Bu Domain 4.2'nin (few-shot) müşteri destek uygulamasıdır: belirsiz durum örnekleri, 2–4 tane, her biri gerekçeli.

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
| Vaka karmaşık ama politika içinde | Çöz — karmaşıklık tetikleyici değil |
| Talep politikada tanımsız / politika sessiz | Eskalasyon yap — reddetme de, kabul etme de |
| Müşteri çözüm sonrası tekrar insan istiyor | Eskalasyon yap |
| Müşteri açıkça "insan istiyorum" diyor | HEMEN eskalasyon yap — araştırma yapma |
| Model güven skoru düşük | Eskalasyon tetikleyicisi olarak KULLANMA |
| Müşteri kızgın (sadece duygu) | Eskalasyon tetikleyicisi olarak KULLANMA |

---

## Eskalasyon Bir Araç Çağrısıdır — El-Devir Bağlamı

Eskalasyon "insana bağlıyorum" cümlesi değil, `escalate_to_human` **araç çağrısı**dır ve parametreleri **5.1'in case facts bloğu**dur. Müşterinin temsilciye her şeyi baştan anlatması, eskalasyonun bağlam kaybıdır.

```json
{
  "tool": "escalate_to_human",
  "input": {
    "reason": "policy_gap",
    "reason_detail": "Competitor price match requested; policy covers own-site adjustments only",
    "case_facts": {
      "order_id": "#4412",
      "amount": 89.90,
      "customer_expectation": "match competitor price, refund $20 difference"
    },
    "attempted": ["policy_lookup: no competitor clause", "explained own-site policy to customer"],
    "customer_sentiment_note": "frustrated but cooperative"
  }
}
```

Sınav senaryosu: "Müşteri temsilciye bağlanınca sipariş numarasını ve talebini yeniden anlatmak zorunda kaldı" → cevap, eskalasyon çağrısına yapılandırılmış el-devir bağlamı eklemektir.

---

## Belirsiz Müşteri Eşleştirme (Ambiguous Customer Matching)

### Problem

Bir müşteri "Ahmet Yılmaz" adıyla arama yapıyorsun. `get_customer` 3 farklı "Ahmet Yılmaz" döndürüyor.

### Yanlış Yaklaşım

Sezgisel (heuristic) seçim yapma:

- ❌ En son sipariş vereni seç
- ❌ En aktif hesabı seç
- ❌ Adres veya şehir bazlı tahmin yap

### Doğru Yaklaşım

Ek tanımlayıcı bilgi iste:

> "Hesabınızı doğrulamak için e-posta adresinizi, telefon numaranızı veya sipariş numaranızı paylaşabilir misiniz?"

**Kural:** Birden fazla eşleşme varsa → ek tanımlayıcı iste. Sezgisel seçim YAPMA.

### Araç tarafı (Domain 2 bağı)

Exam guide "*when **tool results** return multiple matches*" diyor — yani `get_customer` **tüm eşleşmeleri döndürmeli**, "en olası" olanı seçip tek kayıt döndürmemeli. Aracın içine gömülü sezgisel seçim, agent'ın hiç göremediği bir yanlış eşleşme kaynağıdır. Araç belirsizliği yüzeye çıkarır (Domain 2.1), agent müşteriye sorar (5.2).

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Müşteri insan isterse | Hemen eskalasyon — önce çözme, araştırma yapma |
| Politika dışı / politika sessiz | Eskalasyon — agent yetkisi yok; reddetmek de politika dışına çıkmaktır |
| Karmaşık ama politika içinde | Çöz — karmaşıklık tetikleyici değil ("not just complex cases") |
| İlerleme sağlanamıyor | Eskalasyon — retry / ek tanımlayıcı denendikten sonra |
| Duygu bazlı eskalasyon | GÜVENİLMEZ — kızgınlık ≠ karmaşıklık |
| Model güven skoru | GÜVENİLMEZ — kalibrasyon zayıf, zor vakalarda yanlış yere güvenli |
| Kriterler nasıl öğretilir | System prompt'a açık kriterler + few-shot örnekler (Q3-A); altyapıdan önce **orantılı ilk müdahale** |
| Ayrı sınıflandırıcı | Son çare — etiketli veri + ML altyapısı; prompt denenmeden over-engineering (Q3-C) |
| Ölçüm | FCR (%80 hedef), gereksiz eskalasyon oranı, politika ihlali |
| Kızgın müşteri + basit sorun | Çöz, eskalasyon yapma |
| Müşteri çözüm sonrası yine insan isterse | O zaman eskalasyon yap |
| Eskalasyon = araç çağrısı | `escalate_to_human` + case facts el-devir bağlamı |
| Birden fazla müşteri eşleşmesi | Ek tanımlayıcı iste; araç tüm eşleşmeleri döndürmeli |

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
> **B)** Duygu bazlı eskalasyonu kaldır. Yerine üç geçerli tetikleyiciyi few-shot örneklerle system prompt'a yaz: müşteri açıkça insan isterse, politika dışı talep, anlamlı ilerleme sağlanamıyorsa.
>
> **C)** Duygu skorunu modelin güven skoruyla birleştir — ikisi birden düşükse eskalasyon yap.
>
> **D)** Geçmiş 100 eskalasyonla bir sınıflandırıcı eğit; hangi mesajların gerçekten eskalasyon gerektirdiğini o tahmin etsin.

### Doğru Cevap: B

**Neden B doğru:** Duygu bazlı eskalasyon güvenilmez bir tetikleyicidir — hayal kırıklığı vaka karmaşıklığıyla orantılı değildir. %65 yanlış eskalasyon bunu kanıtlıyor. Doğru çözüm: güvenilmez tetikleyiciyi kaldır, yerine üç geçerli tetikleyiciyi *few-shot örneklerle* koy — orantılı ilk müdahale.

**Neden A yanlış:** Eşik ayarlama aynı yapısal sorunu devam ettirir. -0.9'da bile duygu skoru vaka karmaşıklığını ölçmez — bazı basit vakaları hâlâ yanlış eskalasyon eder.

**Neden C yanlış:** İki güvenilmez metriği birleştirmek güvenilir bir metrik oluşturmaz. Duygu skoru da ham güven skoru da eskalasyon kararı için güvenilmez.

**Neden D yanlış:** Q3'ün C şıkkı: prompt kriterleri denenmeden ML altyapısı kurmak over-engineering. 100 örnek eğitim seti için de yetersiz. Sınıflandırıcı, kriterler yazılıp ölçüldükten sonra hâlâ yetmiyorsa gündeme gelir.

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
> **C)** Bu, politika boşluğu (policy gap) — agent yetkisi dışında. `escalate_to_human` ile eskalasyon yap, el-devir bağlamına sipariş no, talep ve politika boşluğunu yaz, müşteriye durumu açıkla.
>
> **D)** Müşterinin duygu durumuna göre karar ver — kızgınsa eskalasyon yap, sakinse reddet.

### Doğru Cevap: C

**Neden C doğru:** Politikada rakip fiyat eşleştirmesi tanımlanmamış — bu bir politika boşluğu; exam guide'ın "*policy is ambiguous or silent*" durumu. Agent politika dışına çıkamaz. Doğru hareket: yapılandırılmış bağlamla eskalasyon yap, insan temsilci karar versin.

**Neden A yanlış:** Agent politikayı geniş yorumlama yetkisine sahip değil. Politika sadece kendi site fiyatını kapsıyor — bunu genişletmek agent'ın yetkisini aşar.

**Neden B yanlış:** "Politikada yok" ≠ "politika yasaklıyor". Politika *sessizse* reddetmek de politika dışına çıkmaktır — olumsuz yönde. Sınavın "reddetmek güvenli taraftır" sezgisi tuzaktır; boşlukta karar agent'ın değil insanın.

**Neden D yanlış:** Duygu bazlı karar — güvenilmez tetikleyici. Eskalasyon kararı duyguya değil, politika boşluğuna dayanmalı.

---

## Pratik Senaryo 3

> Bir müşteri destek agent'ının FCR'si %58. Log analizi iki kalıp gösteriyor: (1) "Ürün eksik geldi, fotoğrafı ekte" gibi standart eksik-parça taleplerinin %40'ı eskalasyon ediliyor; (2) 90 günlük iade süresini 3 ay aşan talepler agent tarafından "müşteri memnuniyeti için" onaylanıyor.
>
> **En etkili ilk müdahale hangisidir?**
>
> **A)** Agent'ın güven skorunu her yanıttan önce bildirmesini iste; 6/10'un altında eskalasyon yapsın.
>
> **B)** System prompt'a açık eskalasyon kriterleri ekle ve her iki kalıp için gerekçeli few-shot örnekler yaz: eksik parça + fotoğraf → çöz (politika 3.1); süre aşımı → eskalasyon (politika istisnası).
>
> **C)** Eksik-parça taleplerini yakalayan bir regex ön filtresi ekle; süre aşımı için `process_refund` aracını 90 gün sonrası siparişlerde devre dışı bırak.
>
> **D)** Daha büyük bir model kullan; karar sınırlarını daha iyi kavrar.

### Doğru Cevap: B

**Neden B doğru:** Q3'ün iki yönlü kalibrasyon sorunu: basitler eskalasyon (aşırı), politika istisnaları özerk (yetersiz). Kök neden belirsiz karar sınırları; iki yönü de gösteren few-shot örnekli açık kriterler orantılı ilk müdahaledir.

**Neden A yanlış:** Self-reported güven kalibre değil; agent süre aşımı vakalarında zaten "yanlış yere güvenli". Eşik iki yönlü sorunu tek yönlü ölçüyle çözmeye çalışır.

**Neden C yanlış:** Aracı 90 gün sonrası devre dışı bırakmak (Domain 1 hook/izin kalıbı) *güvenlik ağı* olarak makuldür ama eskalasyon *kalibrasyonunu* düzeltmez: agent süre aşımını yine çözmeye çalışır, araç reddedince müşteriye ne diyeceğini bilmez. Regex ön filtre kırılgan bir altyapı katmanıdır; kriterler yazılmadan önce değil sonra düşünülür.

**Neden D yanlış:** Sorun model kapasitesi değil, prompt'ta karar sınırlarının olmaması; büyük model de tanımsız sınırı bilemez.
