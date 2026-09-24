# Task Statement 1.4: İş Akışı Zorlaması ve Devir Teslim (Workflow Enforcement and Handoff)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Agentic loops, multi-agent orchestration, context passing — bunların hepsi Claude'un **esnek** ve **akıllı** kararlar vermesine dayanıyor. Ama bazı kararlar esnekliğe bırakılamaz. Bazı kurallar **her seferinde, istisnasız** uygulanmalıdır.

Bu task statement tam olarak bunu öğretiyor: **ne zaman Claude'a güvenirsin, ne zaman programmatik olarak zorlarsın?**

---

## Zorlama Spektrumu

İki yaklaşım var:

### Prompt-Based Guidance (Olasılıksal)

System prompt'a talimat yazarsın — "Müşteriyi her zaman önce doğrula." Bu çoğu zaman çalışır. Ama %100 garanti değildir. Claude bazen atlayabilir. Non-zero failure rate.

### Programmatic Enforcement (Deterministik)

Kodda bir gate/hook yazarsın — refund tool'u çağrılmadan önce, `verify_identity` tool'unun başarıyla tamamlanmış olup olmadığını kontrol eden bir prerequisite gate. Eğer doğrulama yapılmamışsa, refund tool'u fiziksel olarak çalışamaz. %100 garanti.

---

## Sınavın Karar Kuralı

Bu çok net ve sınavda tekrar tekrar test ediliyor:

- **Sonuçlar finansal, güvenlik veya uyumluluk (compliance) ile ilgiliyse** → **Programmatic enforcement.** Her zaman.
- **Sonuçlar düşük riskli ise** (format tercihleri, stil kuralları) → Prompt-based guidance yeterli.

> Sınav, yüksek riskli senaryolarda prompt-based çözümleri şık olarak sunacak. **Reddet.**

---

## Çoklu Sorunlu İstekleri Yönetme

Bir müşteri aynı anda birden fazla sorun bildirdiğinde:

1. İsteği ayrı sorunlara **ayrıştır** (decompose)
2. Her birini paylaşılan bağlam ile **paralel olarak** araştır
3. Tek bir **birleşik çözüm** sentezle

---

## Yapılandırılmış Devir Teslim Protokolleri

Bazen agent sorunu çözemez ve bir insan agent'a yönlendirmesi gerekir. Bu escalation'da kritik kural:

> **İnsan agent konuşma transcript'ine erişemez.** Handoff özeti kendi kendine yeterli (self-contained) olmalıdır.

Handoff özetinde bulunması gerekenler:

- **Müşteri kimliği** (customer ID)
- **Konuşma özeti** — ne oldu, müşteri ne istedi
- **Kök neden analizi** — sorunun kaynağı ne
- **İade tutarı** (varsa)
- **Önerilen aksiyon** — insan agent'ın ne yapması gerektiği

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Prompt-based guidance | Olasılıksal — çoğu zaman çalışır, %100 garanti değil |
| Programmatic enforcement | Deterministik — prerequisite gate ile fiziksel engel, %100 garanti |
| Karar kuralı | Finansal / güvenlik / compliance → programmatic. Düşük risk → prompt yeterli |
| Multi-concern requests | Ayrıştır → paralel araştır → birleşik çözüm sentezle |
| Handoff protocol | Self-contained özet: müşteri ID, özet, kök neden, tutar, önerilen aksiyon |
| Sınav tuzağı | Yüksek riskli senaryolarda prompt-based çözümler şık olarak sunulur — reddet |

---

## Pratik Senaryo

> Production verileri gösteriyor ki vakaların %8'inde, bir müşteri destek agent'ı hesap sahipliğini doğrulamadan (verify account ownership) iade işlemi yapıyor. Bu bazen yanlış hesaplara iade yapılmasına yol açıyor.
>
> **Bu sorunu nasıl çözersiniz?**
>
> **A)** Refund tool'unun çalışabilmesi için `verify_identity` tool'unun başarıyla tamamlanmış olmasını şart koşan programmatik bir prerequisite gate ekle.
>
> **B)** System prompt'u güçlendir: "Asla kimlik doğrulaması yapmadan iade işlemi yapma" talimatını ekle ve bunu kalın yazıyla vurgula.
>
> **C)** Few-shot örnekler ekle — doğru sıralamayı gösteren 3-4 örnek konuşma ekle.
>
> **D)** Bir routing classifier ekle — iade isteklerini önce doğrulama akışına yönlendirsin.

### Doğru Cevap: A

**Neden A doğru:** Finansal sonuçları olan bir işlem — yanlış hesaba iade yapılıyor. Bu %100 garanti gerektiriyor. Programmatik prerequisite gate, `verify_identity` tamamlanmadan refund tool'unun çalışmasını fiziksel olarak engeller. Sıfır hata oranı.

**Neden B yanlış:** Prompt güçlendirme olasılıksal — %92'den %97'ye çıkarabilir ama %100 garanti edemez. Zaten mevcut durumda %8 hata var, bu da prompt'un yetmediğinin kanıtı. Finansal risk devam eder.

**Neden C yanlış:** Few-shot örnekler de prompt-based guidance kategorisinde. Modelin davranışını *yönlendirir* ama *zorlamaz*. Aynı sorun — deterministik değil.

**Neden D yanlış:** Routing classifier sorunu farklı bir yere taşır ama çözmez. Classifier da hata yapabilir. Ve asıl mesele şu: refund tool'u hâlâ doğrulama olmadan çağrılabilir durumda. Gate yok, garanti yok.
