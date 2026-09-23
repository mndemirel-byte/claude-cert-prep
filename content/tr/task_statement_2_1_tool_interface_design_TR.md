# Task Statement 2.1: Araç Arayüz Tasarımı (Tool Interface Design)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Claude bir agent olarak çalışırken, **araçlara (tools)** erişimi vardır — veritabanı sorgulama, müşteri bilgisi çekme, e-posta gönderme, API çağrısı yapma gibi fonksiyonlar. Bu araçları sen tanımlarsın ve API üzerinden Claude'a verirsin.

Kritik nokta: **Claude hangi aracı çağıracağına neredeyse tamamen aracın açıklamasına (description) bakarak karar verir.** Aracın adına değil. System prompt'taki örneklere değil. **Açıklama**, TEK mekanizmadır.

Şöyle düşün: karanlık bir odada 6 tane etiketsiz düğme var. Birisi sana her düğmenin tek cümlelik açıklamasını okuyor. Sadece bu açıklamalara dayanarak doğru düğmeye basmalısın. İki açıklama birbirine çok benziyorsa, bazen yanlış düğmeye basacaksın.

Claude'un kötü yazılmış araç açıklamalarıyla yaşadığı durum tam olarak bu.

---

## İyi Bir Araç Açıklaması Neleri İçerir?

Beş temel bileşen:

1. **Aracın ne yaptığı** — birincil amacı, açıkça belirtilmiş
2. **Hangi girdileri beklediği** — formatlar, tipler, kısıtlamalar
3. **İyi çalıştığı örnek sorgular** — somut kullanım senaryoları
4. **Sınır durumları ve kısıtlamalar** — ne YAPMADIĞI
5. **Açık sınırlar** — bu aracı benzer araçlara karşı NE ZAMAN kullanmalı

### Kötü Açıklama

```
get_customer: "Müşteri bilgilerini getirir."
```

### İyi Açıklama

```
get_customer: "Müşteri profil verilerini (ad, e-posta, hesap seviyesi, tercihler) 
müşteri ID veya e-posta adresi kullanarak getirir. 'Bu müşteri kim' veya 'hangi 
plandalar' gibi kimlik odaklı sorgular için kullan. Sipariş ile ilgili sorgular 
için KULLANMA — onun yerine lookup_order kullan."
```

Fark: İkincisi Claude'a tam olarak bu aracı ne zaman seçeceğini ve ne zaman SEÇMEMESİ gerektiğini söylüyor.

---

## Yanlış Yönlendirme Problemi (Misrouting) — Sınav Favorisi

Sınavın çok sevdiği senaryo: birbirine benzeyen açıklamalara sahip iki araç var ve Claude sürekli yanlış olanı seçiyor.

### Örnek Senaryo

- `get_customer`: "Müşteri bilgilerini getirir"
- `lookup_order`: "Sipariş bilgilerini getirir"

Kullanıcı: *"12345 numaralı siparişin durumunu kontrol et."*

Claude `get_customer`'ı seçiyor. Neden? İki açıklama da "bilgileri getirir" diyor ve sorgu belirsiz. Açıklamalar Claude'un ayrım yapması için çok vague.

### Dört Olası Çözüm ve Değerlendirmesi

| Çözüm | Karar | Neden |
|---|---|---|
| **Araç açıklamalarını genişlet** | **✅ Doğru** | Düşük efor, yüksek etki. Kök nedeni doğrudan çözer. |
| System prompt'a few-shot örnekler ekle | ❌ Yanlış | Açıklama sorununu çözmek yerine token maliyeti yaratır. Belirtiyi tedavi eder. |
| Claude'dan önce bir routing classifier ekle | ❌ Yanlış | İlk adım için aşırı mühendislik. Basit çözümü henüz denemedin. |
| İki aracı birleştir | ❌ Yanlış | Çok fazla efor, görev ayrımını bozar. |

> **Sınav ilkesi: Sınav, ilk adım olarak düşük eforlu, yüksek etkili çözümleri tercih eder.** Classifier'dan önce daha iyi açıklamalar. Her zaman.

---

## Araç Bölme (Tool Splitting)

Bazen tam tersi sorun olur — bir araç çok geniş kapsamlıdır. Tek bir `analyze_document` aracı hem özetliyor, hem veri çıkarıyor, HEM de iddiaları doğruluyor — üç işi birden yapıyor.

### Çözüm: Amaca Özel Araçlara Böl

- `extract_data_points` — dokümandan yapılandırılmış veri çeker
- `summarize_content` — özet üretir
- `verify_claim_against_source` — belirli bir iddianın kaynakla desteklenip desteklenmediğini kontrol eder

Her araç tek bir iş yapar, kesin şekilde açıklanmış, tanımlı girdi/çıktı sözleşmesi ile.

---

## System Prompt Çakışmaları — Sinsi Tuzak

Araç açıklamaların mükemmel olsa bile, **system prompt'taki anahtar kelimeye duyarlı talimatlar bunları geçersiz kılabilir.**

Örnek: System prompt "kullanıcı bir siparişten bahsettiğinde her zaman önce müşteri kimliğini kontrol et" diyorsa, Claude araç açıklamalarından bağımsız olarak sipariş sorgularını `get_customer`'a yönlendirebilir.

**Kural:** Araç açıklamalarını güncelledikten sonra system prompt'u her zaman çakışmalar açısından gözden geçir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Araç açıklaması | Claude'un araç seçimi için TEK mekanizma |
| İyi açıklama | Ne yapar + girdiler + örnekler + sınırlamalar + açık sınırlar |
| Misrouting | Benzer açıklamalar → yanlış araç seçimi. İlk çözüm: açıklamaları genişlet |
| Araç bölme | Geniş kapsamlı aracı amaca özel araçlara böl |
| System prompt çakışması | Prompt'taki talimatlar iyi açıklamaları geçersiz kılabilir — çakışma kontrolü yap |
| Sınav ilkesi | Düşük efor, yüksek etki → classifier'dan önce açıklama, birleştirmeden önce bölme |

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
> **B)** Hayır — önce araç açıklamalarını genişletmeli. `search_knowledge_base`'e "SSS, ürün dokümantasyonu, nasıl yapılır kılavuzları için kullan" ve `search_tickets`'a "mevcut destek talepleri, şikayet geçmişi, açık vakalar için kullan" gibi açık sınırlar eklemeli.
>
> **C)** Hayır — iki aracı tek bir `search_all` aracında birleştirmeli.
>
> **D)** Hayır — system prompt'a her iki aracın ne zaman kullanılacağını gösteren 5 few-shot örnek eklemeli.

### Doğru Cevap: B

**Neden B doğru:** Kök neden açıklamaların belirsiz olması — iki araç da "ilgili bilgileri arar" diyor. Claude ayrım yapamıyor. Açıklamaları genişletmek düşük eforlu, yüksek etkili bir çözüm ve kök nedeni doğrudan hedef alıyor.

**Neden A yanlış:** Routing classifier ilk adım için aşırı mühendislik. Basit çözümü (açıklama iyileştirme) henüz denemedin. Classifier ekstra karmaşıklık ve bakım maliyeti getirir.

**Neden C yanlış:** Birleştirme görev ayrımını bozar. İki farklı veri kaynağını (bilgi tabanı ve destek talepleri) tek araçta birleştirmek araç odağını kaybettirir.

**Neden D yanlış:** Few-shot örnekler token maliyeti yaratır ve belirtiyi tedavi eder, kök nedeni değil. Açıklamalar belirsizken örnekler güvenilir çözüm sağlamaz.
