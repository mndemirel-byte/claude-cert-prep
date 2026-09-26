# Task Statement 2.1: Araç Arayüz Tasarımı (Tool Interface Design)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Claude bir agent olarak çalışırken, **araçlara (tools)** erişimi vardır — veritabanı sorgulama, müşteri bilgisi çekme, e-posta gönderme, API çağrısı yapma gibi fonksiyonlar. Bu araçları sen tanımlarsın ve API üzerinden Claude'a verirsin.

Kritik nokta: **Claude hangi aracı çağıracağına birincil olarak aracın açıklamasına (description) bakarak karar verir.** Açıklama, araç seçiminin **birincil** mekanizmasıdır — ama tek mekanizması değil. Aracın **adı**, parametre adları ve `input_schema` içindeki parametre açıklamaları da seçimi etkiler. Exam guide bu yüzden "araçları yeniden adlandır **ve** açıklamaları güncelle" der; Anthropic'in kendi ölçümleri de isimlendirme ve namespacing'in (`asana_search` vs `jira_search`) araç seçimi üzerinde önemli etkisi olduğunu gösteriyor.

Şöyle düşün: karanlık bir odada 6 tane düğme var. Her düğmenin üzerinde kısa bir etiket (araç adı) ve birisi sana her düğmenin birkaç cümlelik açıklamasını okuyor. Etiketler birbirine benziyorsa **ve** açıklamalar belirsizse, bazen yanlış düğmeye basacaksın.

Claude'un kötü tasarlanmış araç arayüzleriyle yaşadığı durum tam olarak bu.

---

## Bir Araç Tanımının Anatomisi

Messages API'de bir araç üç parçadan oluşur:

```json
{
  "name": "get_customer",
  "description": "Müşteri profil verilerini (ad, e-posta, hesap seviyesi, tercihler) müşteri ID veya e-posta adresi ile getirir. 'Bu müşteri kim' veya 'hangi plandalar' gibi kimlik odaklı sorgular için kullan. Sipariş ile ilgili sorgular için KULLANMA — onun yerine lookup_order kullan. Sipariş geçmişi veya fatura bilgisi döndürmez.",
  "input_schema": {
    "type": "object",
    "properties": {
      "customer_id": {
        "type": "string",
        "description": "Müşteri kimliği, 'CUST-' öneki + 6 hane (örn. CUST-004512). E-posta adresi biliniyorsa email alanını kullan."
      },
      "email": {
        "type": "string",
        "description": "Müşterinin kayıtlı e-posta adresi. customer_id verilmediğinde kullanılır."
      }
    },
    "required": []
  }
}
```

| Parça | Rolü | Tasarım kuralı |
|---|---|---|
| `name` | Kısa, ayırt edici kimlik. Regex: `^[a-zA-Z0-9_-]{1,128}$` | Amaç + nesne (`lookup_order`, `search_support_tickets`); benzer araçları önek/sonekle namespace'le (`jira_search`, `asana_search`) |
| `description` | Claude'un "ne zaman bu araç" kararını verdiği asıl metin | **En az 3–4 cümle**, karmaşık araçta daha fazla (resmi Anthropic kılavuzu) |
| `input_schema` | JSON Schema — parametreler, tipler, zorunluluk | Her parametreye `description`; sınırlı değer kümesi varsa `enum`; belirsiz isimler yerine açık isimler (`user` değil `user_id`) |

MCP'de aynı yapı `inputSchema` (camelCase) adıyla gelir; kavram aynı.

---

## İyi Bir Araç Açıklaması Neleri İçerir?

Beş temel bileşen:

1. **Aracın ne yaptığı** — birincil amacı, açıkça belirtilmiş
2. **Hangi girdileri beklediği** — formatlar, tipler, kısıtlamalar
3. **İyi çalıştığı örnek sorgular** — somut kullanım senaryoları
4. **Sınır durumları ve kısıtlamalar** — ne YAPMADIĞI, ne DÖNDÜRMEDİĞİ
5. **Açık sınırlar** — bu aracı benzer araçlara karşı NE ZAMAN kullanmalı / kullanmamalı

### Kötü Açıklama

```
get_customer: "Müşteri bilgilerini getirir."
```

### İyi Açıklama

```
get_customer: "Müşteri profil verilerini (ad, e-posta, hesap seviyesi, tercihler)
müşteri ID veya e-posta adresi kullanarak getirir. 'Bu müşteri kim' veya 'hangi
plandalar' gibi kimlik odaklı sorgular için kullan. Sipariş ile ilgili sorgular
için KULLANMA — onun yerine lookup_order kullan. Sipariş geçmişi veya fatura
bilgisi döndürmez."
```

Fark: İkincisi Claude'a tam olarak bu aracı ne zaman seçeceğini, ne zaman SEÇMEMESİ gerektiğini ve **ne döndürmediğini** söylüyor.

### Anthropic'in resmi örneği

Resmi dokümantasyondaki iyi/kötü çift:

- ❌ `"Gets the stock price for a ticker."`
- ✅ `"Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company."`

Dört cümle: ne yapar, girdi kısıtı, ne döndürür, ne zaman kullanılır, ne döndürmez.

---

## Yanlış Yönlendirme Problemi (Misrouting) — Sınav Favorisi

Sınavın çok sevdiği senaryo: birbirine benzeyen adlara ve açıklamalara sahip iki araç var ve Claude sürekli yanlış olanı seçiyor.

Exam guide'ın kendi örneği: `analyze_content` vs `analyze_document` — neredeyse aynı açıklamalarla. Resmi örnek soru (Q2): `get_customer` ("Retrieves customer information") vs `lookup_order` ("Retrieves order details").

### Örnek Senaryo

- `get_customer`: "Müşteri bilgilerini getirir"
- `lookup_order`: "Sipariş bilgilerini getirir"

Kullanıcı: *"12345 numaralı siparişin durumunu kontrol et."*

Claude `get_customer`'ı seçiyor. Neden? İki açıklama da "bilgileri getirir" diyor, iki araç da benzer kimlik formatları kabul ediyor. Açıklamalar Claude'un ayrım yapması için çok belirsiz.

### Olası Çözümler ve Değerlendirmesi

| Çözüm | Karar | Neden |
|---|---|---|
| **Araç açıklamalarını genişlet** (girdi formatları, örnek sorgular, sınır durumları, "X yerine Y kullan") | **✅ Doğru ilk adım** | Düşük efor, yüksek etki. Kök nedeni doğrudan çözer. |
| **Araçları yeniden adlandır + açıklamaları güncelle** | **✅ Aynı kategoride** | Exam guide'ın Skills maddesi: "Renaming tools and updating descriptions to eliminate functional overlap." Açıklama genişletmeyle birlikte yapılır; ikisi rakip değil. |
| System prompt'a few-shot örnekler ekle | ❌ Yanlış | Açıklama sorununu çözmek yerine token maliyeti yaratır. Belirtiyi tedavi eder. |
| Claude'dan önce bir routing classifier ekle | ❌ Yanlış | İlk adım için aşırı mühendislik. Basit çözümü henüz denemedin. |
| İki aracı tek `lookup_entity` aracında birleştir | ❌ Yanlış | Ayrımı Claude'dan aracın içine taşır; belirsizlik yok olmaz, yer değiştirir. Görev ayrımını bozar. |

> **Sınav ilkesi: Sınav, ilk adım olarak düşük eforlu, yüksek etkili çözümleri tercih eder.** Classifier'dan önce daha iyi açıklamalar (ve adlar). Her zaman.

---

## Araç Bölme vs Araç Birleştirme

### Bölme (Tool Splitting)

Bir araç çok geniş kapsamlıdır. Tek bir `analyze_document` aracı hem özetliyor, hem veri çıkarıyor, HEM de iddiaları doğruluyor — üç farklı amaç, üç farklı çıktı şeması.

**Çözüm: Amaca özel araçlara böl**

- `extract_data_points` — dokümandan yapılandırılmış veri çeker (çıktı: JSON kayıt listesi)
- `summarize_content` — özet üretir (çıktı: metin)
- `verify_claim_against_source` — belirli bir iddianın kaynakla desteklenip desteklenmediğini kontrol eder (çıktı: destekleniyor/desteklenmiyor + kanıt)

Her araç tek bir iş yapar, kesin şekilde açıklanmış, **tanımlı girdi/çıktı sözleşmesi** ile.

### Birleştirme (Consolidation) — karşı kutup

Bölme her zaman doğru değildir. Anthropic'in "Writing tools for agents" kılavuzu tam tersi hatayı da uyarır: API endpoint'lerini birebir yansıtan çok sayıda küçük araç (`list_users`, `list_events`, `create_event`) yerine, bir insanın yapacağı iş akışını kapsayan tek bir araç (`schedule_event`) daha iyi sonuç verir.

**Bölme ölçütü "kaç işlem" değil, "kaç farklı amaç ve çıktı sözleşmesi":**

| Durum | Karar |
|---|---|
| Üç işlem, üç farklı çıktı şeması, farklı sorgu türleri tetikliyor (`analyze_document`) | **Böl** |
| Üç API çağrısı ama tek bir iş akışı, tek bir sonuç (`schedule_event`) | **Birleştir** |
| İki araç, aynı veri kaynağı, yalnızca açıklamalar belirsiz | **Ne böl ne birleştir — açıklamaları düzelt** |

---

## Araç Çıktısının Tasarımı

Exam guide "expected inputs, **outputs**" der — arayüz tasarımı yalnızca girdi tarafı değildir. Araç ne döndürürse Claude onunla düşünür.

- **Anlamlı bağlam döndür:** `user_id: "a8f3-…"` yerine `user: "Ayşe Yılmaz (a8f3-…)"`. Anthropic'in ölçümü: UUID'leri anlamlı isimlerle değiştirmek Claude'un doğruluğunu belirgin artırıyor.
- **`response_format` parametresi:** `concise` (varsayılan, yalnızca gerekli alanlar) / `detailed` (tüm alanlar). Agent ihtiyacına göre seçer.
- **Sayfalama, filtreleme, kesme:** Claude Code MCP araç çıktısını varsayılan 25.000 token'da keser. Sayfalama (`page`, `limit`), aralık seçimi ve kesilen yanıtta "daha dar bir sorgu dene" yönergesi ver.
- **Açıklamada ne döndürdüğünü yaz:** "Sipariş geçmişi döndürmez" gibi negatif sınırlar Claude'un yanlış beklentiyle aracı çağırmasını önler.

---

## System Prompt Çakışmaları — Sinsi Tuzak

Araç açıklamaların mükemmel olsa bile, **system prompt'taki anahtar kelimeye duyarlı talimatlar bunları geçersiz kılabilir.**

Örnek: System prompt "kullanıcı bir siparişten bahsettiğinde her zaman önce müşteri kimliğini kontrol et" diyorsa, Claude araç açıklamalarından bağımsız olarak sipariş sorgularını `get_customer`'a yönlendirebilir.

**Kural:** Araç açıklamalarını güncelledikten sonra system prompt'u her zaman çakışmalar açısından gözden geçir.

---

## Araç Seçimini Test Etme

Exam guide'ın hazırlık önerisi: *"Test tool selection reliability with ambiguous requests."*

Araç açıklamalarını değiştirdikten sonra "doğru olmuş" diye varsayma. Küçük bir değerlendirme seti kur:

1. 20–30 gerçekçi, **belirsiz** kullanıcı sorgusu yaz ("hesabımla ilgili bir sorun var", "geçen ayki şeyi tekrar gönder")
2. Her sorgu için beklenen aracı belirle
3. Sorguları çalıştır, Claude'un seçtiği aracı kaydet
4. Misrouting oranını ölç; en çok karışan çifti bul; o çiftin açıklamalarını/adlarını düzelt; tekrar ölç

Bu, Domain 4'teki değerlendirme (eval) disiplininin araç tasarımına uygulanmış hâlidir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Araç açıklaması | Claude'un araç seçimi için **birincil** mekanizma (ad + schema da etkiler) |
| İyi açıklama | Ne yapar + girdiler + örnekler + sınırlamalar + açık sınırlar; en az 3–4 cümle |
| `input_schema` | Her parametreye açıklama, `enum` ile değer kümesi, açık parametre adları |
| Misrouting | Benzer ad/açıklama → yanlış araç seçimi. İlk çözüm: açıklamaları genişlet + gerekirse yeniden adlandır |
| Araç bölme | Farklı amaç + farklı çıktı sözleşmesi → böl. Aynı iş akışı → birleştir. |
| Çıktı tasarımı | Anlamlı bağlam, `response_format`, sayfalama, "ne döndürmez" |
| System prompt çakışması | Prompt'taki talimatlar iyi açıklamaları geçersiz kılabilir — çakışma kontrolü yap |
| Sınav ilkesi | Düşük efor, yüksek etki → classifier'dan önce açıklama/ad; birleştirmeden önce bölme (amaçlar farklıysa) |

---

## Pratik Senaryo

> Bir agent'ın iki aracı var: `search_knowledge_base` ve `search_tickets`. İki aracın da açıklaması "İlgili bilgileri arar" diyor. Kullanıcılar, destek talebi sorgularının sıklıkla bilgi tabanına gittiğini bildiriyor.
>
> Bir geliştirici, sorguyu analiz edip Claude görmeden önce doğru araca yönlendiren bir routing classifier eklemeyi öneriyor.
>
> **Bu doğru ilk adım mı? Neden?**
>
> **A)** Evet — routing classifier sorguyu analiz edip doğru araca yönlendirir, misrouting'i çözer.
>
> **B)** Hayır — önce araç açıklamalarını genişletmeli. `search_knowledge_base`'e "SSS, ürün dokümantasyonu, nasıl yapılır kılavuzları için kullan; müşteriye özel vaka kayıtları içermez" ve `search_tickets`'a "mevcut destek talepleri, şikayet geçmişi, açık vakalar için kullan; genel dokümantasyon içermez" gibi açık sınırlar eklemeli. Gerekirse adları da `search_kb_articles` / `search_support_tickets` olarak netleştirmeli.
>
> **C)** Hayır — iki aracı tek bir `search_all` aracında birleştirmeli.
>
> **D)** Hayır — system prompt'a her iki aracın ne zaman kullanılacağını gösteren 5 few-shot örnek eklemeli.

### Doğru Cevap: B

**Neden B doğru:** Kök neden açıklamaların (ve adların) belirsiz olması — iki araç da "ilgili bilgileri arar" diyor. Claude ayrım yapamıyor. Açıklamaları genişletmek ve gerekirse yeniden adlandırmak düşük eforlu, yüksek etkili bir çözüm ve kök nedeni doğrudan hedef alıyor. Exam guide'ın Skills listesindeki iki madde ("writing tool descriptions that clearly differentiate" + "renaming tools and updating descriptions") tam olarak bu.

**Neden A yanlış:** Routing classifier ilk adım için aşırı mühendislik. Basit çözümü (açıklama iyileştirme) henüz denemedin. Classifier ekstra karmaşıklık ve bakım maliyeti getirir.

**Neden C yanlış:** Birleştirme görev ayrımını bozar. İki farklı veri kaynağını (bilgi tabanı ve destek talepleri) tek araçta birleştirmek belirsizliği ortadan kaldırmaz, aracın içine taşır — artık araç hangi kaynağı arayacağını tahmin etmek zorunda.

**Neden D yanlış:** Few-shot örnekler token maliyeti yaratır ve belirtiyi tedavi eder, kök nedeni değil. Açıklamalar belirsizken örnekler güvenilir çözüm sağlamaz.
