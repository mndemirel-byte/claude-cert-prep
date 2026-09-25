# Task Statement 1.4: İş Akışı Zorlaması ve Devir Teslim (Workflow Enforcement and Handoff)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Agentic loop'lar, multi-agent orkestrasyon, context passing — bunların hepsi Claude'un **esnek** ve **akıllı** kararlar vermesine dayanıyor. Ama bazı kararlar esnekliğe bırakılamaz. Bazı kurallar **her seferinde, istisnasız** uygulanmalıdır.

Bu task statement tam olarak bunu öğretiyor: **ne zaman Claude'a güvenirsin, ne zaman programatik olarak zorlarsın?**

---

## Zorlama Spektrumu (The Enforcement Spectrum)

İki yaklaşım var:

### Prompt Tabanlı Yönlendirme (Olasılıksal)

System prompt'a talimat yazarsın — "Müşteriyi her zaman önce doğrula." Bu çoğu zaman çalışır. Ama %100 garanti değildir. Claude bazen atlayabilir. Sıfırdan büyük bir hata oranı (non-zero failure rate) her zaman vardır.

### Programatik Zorlama (Deterministik)

Kodda bir gate yazarsın — refund tool'u çağrılmadan önce, `verify_identity` tool'unun başarıyla tamamlanmış olup olmadığını kontrol eden bir **prerequisite gate**. Eğer doğrulama yapılmamışsa, refund tool'u fiziksel olarak çalışamaz. Kural kodda olduğu için modelin "hatırlamasına" bağlı değildir.

---

## Prerequisite Gate Nasıl Uygulanır? — İki Kalıp

Exam guide'ın Skills maddesi: *"Implementing programmatic prerequisites blocking downstream tool calls."* Bunu uygulamanın iki yolu var; sınav senaryosunun bağlamına göre hangisinin geçerli olduğunu bilmelisin.

### Kalıp 1: Kendi agentic loop'unda tool dispatcher gate'i (Messages API)

Tool çağrılarını sen çalıştırıyorsan (1.1'deki loop), zorlama noktası tool dispatcher'dır. Durumu (state) sen tutarsın; ön koşul sağlanmadıysa tool'u çalıştırmaz, Claude'a **`is_error: true` ile açıklayıcı bir hata** döndürürsün.

```python
state = {"verified_customer_id": None}

def dispatch(block):
    if block.name == "verify_identity":
        result = verify_identity(**block.input)
        if result["ok"]:
            state["verified_customer_id"] = result["customer_id"]
        return tool_result(block.id, result)

    if block.name == "process_refund":
        if state["verified_customer_id"] is None:              # GATE
            return tool_result(
                block.id,
                "Reddedildi: process_refund çağrılmadan önce verify_identity "
                "başarıyla tamamlanmalı. Önce kimliği doğrula.",
                is_error=True,
            )
        return tool_result(block.id, process_refund(**block.input))
```

### Kalıp 2: Agent SDK / Claude Code'da `PreToolUse` hook'u

Loop'u Agent SDK ya da Claude Code yönetiyorsa, tool çağrısı gerçekleşmeden **önce** araya giren `PreToolUse` hook'unu kullanırsın. Hook, `permissionDecision: "deny"` döndürerek çağrıyı engeller ve `permissionDecisionReason` ile nedenini Claude'a iletir. (Hook mekanizmasının ayrıntıları Task Statement 1.5'te.)

```python
async def refund_gate(input_data, tool_use_id, context):
    if input_data["tool_name"] == "process_refund" and not state["verified_customer_id"]:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason":
                    "process_refund için önce verify_identity başarıyla tamamlanmalı.",
            }
        }
    return {}
```

İki kalıbın ortak noktası: **kural kodda yaşar, prompt'ta değil.** Fark yalnızca loop'u kimin yönettiği.

### "Sıfır hata" ne anlama gelir — ve ne anlama gelmez

Gate, **kuralın ihlal edilmesini** sıfıra indirir: doğrulama olmadan iade *gerçekleşemez*. Ama gate tek başına Claude'un görevi doğru tamamlamasını garanti etmez. Engellenen çağrının **nedeni Claude'a geri bildirilmezse** (boş bir hata ya da sessiz bir red), Claude ne yapması gerektiğini anlamaz — aynı çağrıyı tekrarlar, pes eder ya da "iade yapamıyorum" der. Bu yüzden her iki kalıpta da red mesajı **eyleme dönük** olmalıdır: neyin engellendiği ve **önce ne yapılması gerektiği**. Gate + açıklayıcı red = deterministik kural + kendini düzelten agent.

---

## Sınavın Karar Kuralı

Bu çok net ve sınavda tekrar tekrar test ediliyor:

- **Sonuçlar finansal, güvenlik veya uyumluluk (compliance) ile ilgiliyse** → **Programatik zorlama.** Her zaman.
- **Sonuçlar düşük riskli ise** (format tercihleri, stil kuralları, ton) → Prompt tabanlı yönlendirme yeterli.

Ölçüt şu soru: **Tek bir başarısızlık para kaybı, güvenlik ihlali ya da yasal risk yaratıyor mu?** Evetse prompt yetmez.

> Sınav, yüksek riskli senaryolarda prompt tabanlı çözümleri şık olarak sunacak — "talimatı güçlendir", "kalın yaz", "few-shot örnek ekle", "3 kez tekrarla". Hepsi aynı kategoride: olasılıksal. **Reddet.**

Bir de ters tuzak var: düşük riskli bir tercih için (örneğin "yanıtları madde işaretiyle ver") hook yazmak aşırı mühendisliktir. Doğru cevap her zaman "hook" değildir — doğru cevap riskle orantılı olandır.

---

## Çok Konulu İstek Yönetimi (Multi-Concern Request Handling)

Bir müşteri aynı anda birden fazla sorun bildirdiğinde:

1. İsteği ayrı sorunlara **ayrıştır** (decompose)
2. Her birini paylaşılan bağlam ile **paralel olarak** araştır
3. Tek bir **birleşik çözüm** sentezle

Örnek: *"Kargom hâlâ gelmedi, üstelik bana yanlış tutarda fatura kesilmiş ve artık hesabımı kapatmak istiyorum."*

- Ayrıştırma: (a) teslimat gecikmesi, (b) fatura hatası, (c) hesap kapatma talebi — üç bağımsız iş.
- Paralel araştırma: kargo takibi, fatura kaydı ve hesap durumu aynı müşteri bağlamıyla (müşteri ID, sipariş no) aynı anda sorgulanır.
- Birleşik yanıt: üç konuyu tek, tutarlı bir mesajda ele al — üç ayrı yanıt değil.

Ne zaman paralel **olmaz**: konular birbirine bağlıysa. Örneğin hesap kapatma, açık bir iade tamamlanmadan yapılamıyorsa (c) konusu (b)'ye bağımlıdır — önce iade, sonra kapatma. Ayrıştırma yine yapılır, ama yürütme sırası bağımlılığa göre belirlenir (1.3'teki paralel/sıralı kuralı).

Sık yapılan hata: agent'ın yalnızca ilk sorunu ele alıp diğerlerini unutması. Ayrıştırma adımı bunu önler — her konu açıkça listelenir ve her biri için bir sonuç üretilmeden yanıt tamamlanmış sayılmaz.

---

## Yapılandırılmış Devir Teslim Protokolleri (Structured Handoff Protocols)

Bazen agent sorunu çözemez ve bir insan temsilciye yönlendirmesi (escalation) gerekir. Bu devirde kritik kural:

> **İnsan temsilcinin konuşma transcript'ine erişemeyeceğini varsay.** Handoff özeti kendi kendine yeterli (self-contained) olmalıdır — insan, özeti okuyup başka hiçbir şeye bakmadan devam edebilmelidir.

Handoff özetinde bulunması gerekenler:

- **Müşteri kimliği** (customer ID) ve doğrulama durumu (kimlik doğrulandı mı, nasıl)
- **Konuşma özeti** — ne oldu, müşteri ne istedi
- **Kök neden analizi** — sorunun kaynağı ne (ya da neden belirlenemedi)
- **Şimdiye kadar yapılan aksiyonlar** — hangi tool'lar çağrıldı, ne denendi, ne sonuç verdi. İnsanın aynı şeyi tekrar denememesi ve müşteriye aynı soruları tekrar sormaması için kritik.
- **İade / işlem tutarı** (varsa)
- **Neden escalate edildiği** — agent'ın yetkisi dışında mı, belirsizlik mi, müşteri talebi mi
- **Önerilen aksiyon** — insan temsilcinin ne yapması gerektiği

Handoff özeti serbest metin değil, **yapılandırılmış** olmalı (sabit alanlar, tercihen JSON) — 1.3'teki structured context passing ilkesi burada da geçerli. İnsan, başka bir sistem ya da başka bir agent tüketebilir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Prompt tabanlı yönlendirme | Olasılıksal — çoğu zaman çalışır, garanti değil |
| Programatik zorlama | Deterministik — prerequisite gate ile kural kodda yaşar |
| İki uygulama kalıbı | Kendi loop'unda dispatcher gate (`is_error` ile red) / Agent SDK'da `PreToolUse` hook (`permissionDecision: deny`) |
| Red mesajı | Eyleme dönük olmalı — neyin engellendiği + önce ne yapılacağı; aksi halde agent takılır |
| Karar kuralı | Finansal / güvenlik / compliance → programatik. Düşük risk → prompt yeterli. Riskle orantılı ol |
| Multi-concern requests | Ayrıştır → bağımsızları paralel araştır → bağımlıları sırayla → tek birleşik çözüm |
| Handoff protocol | Self-contained, yapılandırılmış özet: müşteri ID, özet, kök neden, **yapılan aksiyonlar**, tutar, escalation nedeni, önerilen aksiyon |
| Exam trap | "Prompt'u güçlendir / few-shot ekle / tekrarla" yüksek riskte distractor; düşük riskte hook aşırı mühendislik |

---

## Pratik Senaryo 1

> Production verileri gösteriyor ki vakaların %8'inde, bir müşteri destek agent'ı hesap sahipliğini doğrulamadan (verify account ownership) iade işlemi yapıyor. Bu bazen yanlış hesaplara iade yapılmasına yol açıyor.
>
> **Bu sorunu nasıl çözersiniz?**
>
> **A)** Refund tool'unun çalışabilmesi için `verify_identity` tool'unun başarıyla tamamlanmış olmasını şart koşan programatik bir prerequisite gate ekle.
>
> **B)** System prompt'u güçlendir: "Asla kimlik doğrulaması yapmadan iade işlemi yapma" talimatını ekle ve bunu kalın yazıyla vurgula.
>
> **C)** Few-shot örnekler ekle — doğru sıralamayı gösteren 3-4 örnek konuşma ekle.
>
> **D)** Bir routing classifier ekle — iade isteklerini önce doğrulama akışına yönlendirsin.

### Doğru Cevap: A

**Neden A doğru:** Finansal sonuçları olan bir işlem — yanlış hesaba iade yapılıyor. Bu deterministik garanti gerektiriyor. Programatik prerequisite gate, `verify_identity` tamamlanmadan refund tool'unun çalışmasını fiziksel olarak engeller. Kural ihlali sıfıra iner.

**Neden B yanlış:** Prompt güçlendirme olasılıksal — %92'den %97'ye çıkarabilir ama %100 garanti edemez. Zaten mevcut durumda %8 hata var, bu da prompt'un yetmediğinin kanıtı. Finansal risk devam eder.

**Neden C yanlış:** Few-shot örnekler de prompt tabanlı yönlendirme kategorisinde. Modelin davranışını *yönlendirir* ama *zorlamaz*. Aynı sorun — deterministik değil.

**Neden D yanlış:** Routing classifier sorunu farklı bir yere taşır ama çözmez. Classifier da hata yapabilir. Ve asıl mesele şu: refund tool'u hâlâ doğrulama olmadan çağrılabilir durumda. Gate yok, garanti yok.

---

## Pratik Senaryo 2

> Bir ekip, Senaryo 1'deki sorunu çözmek için `process_refund` çağrılarını engelleyen bir `PreToolUse` hook'u ekliyor. Hook, `verify_identity` tamamlanmamışsa `permissionDecision: "deny"` döndürüyor — başka bir şey döndürmüyor.
>
> Yanlış hesaba iade vakaları sıfıra düşüyor. Ancak yeni bir şikayet başlıyor: agent artık birçok konuşmada müşteriye "Şu anda iade işlemi yapamıyorum, lütfen daha sonra tekrar deneyin" diyor ve kimlik doğrulaması yapmayı hiç denemiyor.
>
> **Sorun nedir?**
>
> **A)** Hook çok katı — `deny` yerine `ask` döndürmeli ki insan onayıyla iade yapılabilsin.
>
> **B)** Hook çağrıyı engelliyor ama Claude'a **neden** engellendiğini söylemiyor. `permissionDecisionReason` ile "önce `verify_identity` çağır" bilgisi verilmeli; böylece agent kendini düzeltip doğru sırayı izler.
>
> **C)** Gate yaklaşımı bu senaryoya uygun değil — system prompt'a dönülüp doğrulama talimatı güçlendirilmeli.
>
> **D)** `process_refund` tool'u agent'tan tamamen kaldırılmalı; iadeleri her zaman insan yapmalı.

### Doğru Cevap: B

**Neden B doğru:** Gate doğru çalışıyor — kural ihlali sıfır. Eksik olan geri bildirim. Claude sessiz bir red görünce ne yapması gerektiğini bilmiyor; "iade yapamıyorum" sonucuna varıyor. Red mesajı eyleme dönük olursa ("process_refund için önce verify_identity başarıyla tamamlanmalı") agent doğrulamayı çağırır, sonra iadeyi yapar. Deterministik kural korunur, görev de tamamlanır.

**Neden A yanlış:** `ask` insan onayı ister; kuralı deterministik olmaktan çıkarmaz ama her iadeyi insana bağlar — ölçeklenmez ve asıl sorunu (agent'ın neden engellendiğini bilmemesi) çözmez.

**Neden C yanlış:** Prompt'a dönmek Senaryo 1'deki %8 hataya geri dönmektir. Sorun gate'te değil, gate'in iletişiminde.

**Neden D yanlış:** Tool'u kaldırmak agent'ın işlevini yok eder. Amaç iadeyi yasaklamak değil, doğru sırayla yapılmasını garanti etmek — gate bunu zaten sağlıyor.
