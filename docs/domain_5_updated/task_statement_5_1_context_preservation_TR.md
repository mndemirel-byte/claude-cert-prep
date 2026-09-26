# Task Statement 5.1: Bağlam Koruma (Context Preservation)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Agent'lar uzun konuşmalar boyunca çalışır, araç sonuçlarını biriktirir ve önceki turlardan gelen bilgiye dayanarak karar verir. Bu süreçte **kritik bilgilerin kaybolması** en yaygın ve en tehlikeli hatadır. Bu task statement, bağlam kaybını nasıl önleyeceğini öğretir.

Sınavda bu kavramlar üç senaryoda karşına çıkar: **Customer Support Resolution Agent** (case facts, araç sonucu kırpma, çok konulu oturum), **Multi-Agent Research System** (lost in the middle, upstream agent optimizasyonu, subagent metadata) ve **Structured Data Extraction** (yapılandırılmış aktarım).

> **Sıra önemli:** Exam guide'ın varsayılanı **tam konuşma geçmişini göndermek**tir. Özetleme bir *tasarım tercihi* değil, bağlam sınırına yaklaşınca başvurulan bir *risk*tir; case facts bloğu ise o riske karşı *koruma*dır. Sınav senaryosunda "her 5 turda bir özetleniyor" cümlesi genellikle bir semptomun **nedeni** olarak verilir.

---

## Neyi Özetlersin, Neyi Asla? — Domain 5'in Omurgası

Bu tablo 5.1, 5.4 ve 5.6'nın ortak kuralıdır. Üç dokümanda üç farklı kelimeyle geçer ("case facts", "manifest", "claim-source mapping") ama kural tektir:

| İçerik türü | Özetlenebilir mi? | Neden |
|---|---|---|
| Anlatı: müşterinin durumu anlatışı, duygusal akış, agent'ın açıklamaları | ✅ Evet | Bilgi değeri düşük, token maliyeti yüksek |
| Verbose araç çıktısı (40 alanlı sipariş kaydı, ham grep sonucu) | ✅ Evet — hatta **önce kırp** | Çoğu alan ilgisiz |
| Ara akıl yürütme (düşünce zinciri, alternatif hipotezler) | ✅ Evet | Sonuç önemli, yol değil |
| **Case facts** (sipariş no, tutar, tarih, durum, müşteri beklentisi) | ❌ **Asla** | Özet "yakın tarihli bir sipariş"e çevirir |
| **Konu kaydı** (çok konulu oturumda her konunun yapılandırılmış durumu) | ❌ Asla | Konular birbirine karışır |
| **Manifest** (agent durumu — 5.4) | ❌ Asla | Kurtarma buna dayanır |
| **Claim-source eşleştirmesi** (5.6) | ❌ Asla | Atıf ölür |

**Tek cümle:** *Anlatı özetlenir, yapılandırılmış kayıt asla.*

---

## Progressive Summarization Tuzağı

Uzun konuşmalarda token bütçesini yönetmek için konuşma geçmişi özetlenebilir. İşte tam burada tehlike başlıyor.

### Problem

Özetleme sırasında sayısal değerler, tarihler, yüzdeler ve müşteri beklentileri **belirsiz ifadelere** dönüşür:

| Orijinal bilgi | Özetlenmiş hali |
|---|---|
| "Müşteri sipariş #8891 için $247.83 iade istiyor, sipariş 3 Mart'ta verilmiş" | "müşteri yakın tarihli bir sipariş için iade istiyor" |
| "Müşteri %15 indirim beklentisi var, son 3 siparişte toplam $1,200 harcamış" | "müşteri indirim istiyor, düzenli müşteri" |

Sipariş numarası, tutar, tarih — hepsi uçuyor. Agent daha sonra bu belirsiz özetle çalışmak zorunda kalınca doğru işlem yapamaz.

### Çözüm: Kalıcı "Vaka Gerçekleri" (Case Facts) Bloğu

Transaksiyonel gerçekleri ayrı bir yapılandırılmış bloğa çıkar. Bu bloğu **her prompt'a dahil et**, özetlenen geçmişin **dışında** tut ve **asla özetleme**.

```json
{
  "case_facts": {
    "customer_name": "Ahmet Yılmaz",
    "order_id": "#8891",
    "order_date": "2024-03-03",
    "refund_amount": 247.83,
    "refund_currency": "USD",
    "customer_expectation": "full refund to original payment method",
    "loyalty_tier": "Gold",
    "total_spend_last_12m": 1200.00
  }
}
```

**Temel kural:** Konuşma geçmişi özetlenebilir. Vaka gerçekleri **ASLA** özetlenmez.

**Nereye konur?** System prompt'un sonunda ya da her kullanıcı mesajının başında sabit bir blok olarak. Bu iki yer hem "başta/sonda güvenilir işlenir" kuralından (aşağıda) yararlanır hem de blok değişmediği sürece **prompt cache**'ten okunur — tam geçmiş göndermenin maliyetini düşüren şey de zaten caching'dir.

---

## Çok Konulu Oturumlar — Konu Bazlı Bağlam Katmanı

Case facts tek bir vaka için yeterlidir. Müşteri aynı konuşmada **iki iade + bir fatura itirazı** açtığında tek bir blok yetmez: agent "hangi konuda ilerliyoruz?" sorusunu cevaplayamaz ve ilk iadenin tutarını ikinci konuya taşır.

### Çözüm: Konu başına yapılandırılmış kayıt

Exam guide'ın ifadesi: *"structured issue data (order IDs, amounts, statuses) into a separate context layer for multi-issue sessions"*.

```json
{
  "issues": [
    {"issue_id": "I-1", "type": "refund", "order_id": "#8891", "amount": 247.83, "status": "refund_initiated"},
    {"issue_id": "I-2", "type": "refund", "order_id": "#8902", "amount": 59.90, "status": "awaiting_photo"},
    {"issue_id": "I-3", "type": "billing_dispute", "invoice_id": "INV-2211", "amount": 120.00, "status": "open"}
  ],
  "active_issue": "I-2"
}
```

Agent her turda `active_issue`'yu okur, konu değişince kaydı günceller. Katman özetlenmez; konuşma anlatısı özetlenir.

**Sınav ipucu:** "Müşteri ikinci konuyu açınca agent ilkinin tutarını unuttu / iki konuyu karıştırdı" senaryosunun cevabı "case facts" değil, **konu bazlı yapılandırılmış katman**dır.

---

## "Ortada Kaybolma" Etkisi (Lost in the Middle)

### Problem

Modeller uzun girdilerin **başını** ve **sonunu** güvenilir şekilde işler. Ancak **ortaya gömülmüş** bulgular gözden kaçabilir.

Exam guide'ın kelimesi **"aggregated inputs"** — sorun özellikle *birleştirilmiş* girdilerde çıkar: koordinatör 7 subagent'ın çıktısını art arda ekleyip sentez agent'a verir; 4. subagent'ın kritik istatistiği ortada kalır. Yani sorunun kaynağı çoğu zaman **koordinatörün birleştirme formatı**dır, tek bir uzun belge değil.

### Çözüm

İki yöntem birlikte uygulanır — ve ikisi de *birleştirmeyi yapan* agent'ın işidir:

1. **Anahtar bulguların özetini BAŞA yerleştir.** Birleştirilmiş girdinin en tepesinde, en önemli bulguların kısa bir özetini sun.
2. **Açık bölüm başlıkları (section headers) kullan.** İçeriği yapılandırılmış bölümlere ayır — model bölüm başlıklarını referans noktası olarak kullanabilir.

```
## ÖNEMLİ BULGULAR ÖZETİ
- Jeotermal enerji kapasitesi %23 arttı (Kaynak: IEA 2024)
- Rüzgâr enerjisi yatırımları $120B'ye ulaştı (Kaynak: IRENA)
- Güneş paneli maliyeti %14 düştü (Kaynak: BloombergNEF)

## DETAYLI BULGULAR
### 1. Jeotermal Enerji (subagent: web-search-01)
[detaylı içerik...]

### 2. Rüzgâr Enerjisi (subagent: doc-analysis-02)
[detaylı içerik...]
```

---

## Araç Sonucu Budama (Tool Result Trimming)

### Problem

Bir sipariş arama aracı 40'tan fazla alan döndürür: dahili ID'ler, lojistik kodları, depo bilgileri, vergi detayları... Ama agent'ın ihtiyacı sadece 5 alan.

Exam guide: araç sonuçları bağlamda birikir ve **ilgililiğiyle orantısız** token tüketir. Gerçekten önemli bilgi birikmiş gereksiz verinin altında kaybolur.

### Çözüm

Araç sonuçlarını bağlama eklenmeden **ÖNCE** ilgili alanlara kırp. Bunun üç yeri vardır:

| Nerede | Nasıl | Ne zaman |
|---|---|---|
| **(a) Aracın kendisinde** | `lookup_order` zaten yalnızca iade için gerekli alanları döndürür | Aracı sen tasarlıyorsan — Domain 2.1 (araç yanıtı tasarımı). En temiz çözüm. |
| **(b) Agent döngüsünde** | Sonuç bağlama eklenmeden önce filtrelenir (aşağıdaki kod) | Aracı değiştiremiyorsan — **sınavın cevabı bu** |
| **(c) API tarafında** | Context editing: `clear_tool_uses_20250919` eski araç sonuçlarını sunucu tarafında temizler | Güncel not — aşağıdaki kutu |

```python
# YANLIŞ: Ham sonucu olduğu gibi bağlama ekle
context.append(order_lookup_result)  # 40+ alan

# DOĞRU: Sadece gerekli alanları filtrele
relevant_fields = {
    "order_id": result["order_id"],
    "status": result["status"],
    "total": result["total"],
    "date": result["order_date"],
    "items": result["line_items"]
}
context.append(relevant_fields)  # 5 alan
```

---

## Tam Geçmiş Gereksinimi (Full History)

### Kural

Ardışık API isteklerinde **tam konuşma geçmişi** dahil edilmelidir. Önceki mesajları çıkarmak konuşma tutarlılığını bozar.

### Neden?

Messages API durumsuz (stateless) çalışır — her istek bağımsızdır. Önceki mesajları göndermezsen, model konuşmanın bağlamını kaybeder:

- Kullanıcı 3. turda "önceki soruma ek olarak..." derse, 1. ve 2. tur mesajları olmadan model ne sorulduğunu bilemez
- Kararlar önceki turlardaki araç sonuçlarına dayanıyorsa, o sonuçlar geçmişte olmalıdır

### Ne zaman özetlenir?

Yalnızca bağlam sınırına yaklaşınca. O zaman da eski turların **anlatısı** özetlenir; case facts / konu kaydı **tam kalır** (yukarıdaki tablo).

> **Agent SDK notu:** Agent SDK oturumu diske yazar ve `resume` / `continue_conversation` ile geri yükler — yani geçmişi *sen* göndermezsin, SDK gönderir. Ama SDK da **tam geçmişi** gönderir; bağlam yine tüketilir. "Agent SDK kullanıyoruz, geçmiş sorunu yok" bir tuzaktır: kural değişmez, işi kim yaptığı değişir.

> **Güncel durum (sınav cevabını değiştirmez):** "Özetleme" bugün üç biçimde var. (1) **Claude Code:** `/compact`, sınıra yaklaşınca otomatik compact, `/compact <odak talimatı>` ve CLAUDE.md'de `# Compact instructions` bölümü (bkz. 5.4). (2) **Messages API sunucu tarafı compaction** (beta): isteğe bağlı ya da token eşiğinde; **özel özetleme prompt'u** verilebilir; son turlar birebir korunabilir. (3) **Context editing:** eski araç sonuçlarını / thinking bloklarını temizleme. Üçünde de ders aynı: özet prompt'una "sipariş no, tutar, tarih, müşteri beklentisi **birebir** korunacak" yazılmazsa progressive summarization tuzağı sunucu tarafında da yaşanır.

---

## Üst-Akış Agent Optimizasyonu (Upstream Agent Optimisation)

### Problem

Bir araştırma agent'ı 3 sayfalık detaylı analiz ve düşünce zinciri döndürüyor. Bu sonuç, bağlam bütçesi sınırlı bir alt-akış (downstream) agent'a aktarılacak. 3 sayfalık verbose içerik alt-akış agent'ın bağlamını tüketir.

### Çözüm

Üst-akış agent'ları, verbose içerik ve düşünce zincirleri yerine **yapılandırılmış veri** döndürecek şekilde modifiye et. Exam guide'ın üçlüsü: **key facts, citations, relevance scores**.

```json
{
  "key_facts": [
    {
      "claim": "Solar capacity grew 45%",
      "source": "IEA Solar Market Report 2024",
      "source_location": "p.12, Table 3",
      "publication_date": "2024-06-15",
      "methodology": "includes utility-scale and rooftop",
      "relevance": 0.92
    },
    {
      "claim": "Wind investments hit $120B",
      "source": "IRENA Renewable Energy Finance 2024",
      "source_location": "Executive summary",
      "publication_date": "2024-03-20",
      "methodology": "utility-scale only",
      "relevance": 0.85
    }
  ],
  "coverage_gaps": ["Geothermal data unavailable"]
}
```

| Yaklaşım | Sonuç |
|---|---|
| Verbose döndür | Alt-akış agent bağlam bütçesini tüketir |
| Yapılandırılmış veri döndür | Anahtar bilgiler korunur, bütçe verimli kullanılır |

### Subagent'lardan metadata zorunluluğu

Exam guide'ın ayrı bir Skills maddesi: *"Requiring subagents to include metadata (dates, source locations, methodological context) in structured outputs to support accurate downstream synthesis"*. Yukarıdaki JSON'daki `publication_date`, `source_location`, `methodology` alanları bu yüzden var. Bunlar olmadan sentez agent'ı iki farklı tarihin verisini çelişki sanır (5.6 zamansal farkındalık) ya da atıf üretemez (5.6 provenance). Metadata, upstream optimizasyonunun ayrılmaz parçasıdır — "az ama yapılandırılmış" demek "az ama **etiketli**" demektir.

> **`relevance` ≠ `confidence`.** Alan adı bilinçli olarak ilgililik. Modelin kendi bildirdiği güven skoru kalibre edilmemiştir (5.2: eskalasyon için güvenilmez; 5.5: etiketli setle kalibre edilmeden kullanılmaz). İlgililik skoru yalnızca **sıralama** içindir, karar için değil.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Tam geçmiş (varsayılan) | Ardışık isteklerde tam konuşma geçmişi gönder — SDK kullansan da kural aynı |
| Progressive summarization tuzağı | Özetleme sayısal değerleri, tarihleri, yüzdeleri, müşteri beklentisini belirsiz ifadelere dönüştürür |
| Case facts bloğu | Transaksiyonel gerçekleri ayrı blokta, özetlenen geçmişin dışında tut, ASLA özetleme |
| Konu bazlı katman | Çok konulu oturumda konu başına yapılandırılmış kayıt + `active_issue` |
| Anlatı vs kayıt | Anlatı özetlenir, yapılandırılmış kayıt (case facts / manifest / claim-source) asla |
| Lost in the middle | Birleştirilmiş girdilerde ortadaki bulgular kaçar → özet başa + bölüm başlıkları (koordinatörün işi) |
| Tool result trimming | Verbose sonuçları ilgili alanlara kırp, SONRA bağlama ekle (araçta / döngüde / API'de) |
| Upstream optimisation | Key facts + citations + relevance; verbose ve düşünce zinciri yok |
| Subagent metadata | Tarih, kaynak konumu, metodoloji zorunlu — sentez bunlarsız yanlış yorumlar |

---

## Pratik Senaryo 1

> Bir müşteri destek agent'ı 15 turdan fazla konuşma yürütüyor. Token bütçesini yönetmek için konuşma geçmişi düzenli olarak özetleniyor. 12. turda agent müşteriye "Hangi sipariş için iade istiyorsunuz?" diye soruyor — oysa müşteri 2. turda sipariş numarasını, tutarı ve tarihi açıkça belirtmişti.
>
> **Kök neden ve çözüm nedir?**
>
> **A)** Modelin bağlam penceresi (context window) çok küçük — daha büyük model kullan.
>
> **B)** Özetleme sırasında sipariş numarası, tutar ve tarih gibi transaksiyonel gerçekler kaybolmuş. Çözüm: bu bilgileri kalıcı bir "case facts" bloğuna çıkar ve asla özetleme.
>
> **C)** Agent'ın system prompt'una "müşteri bilgilerini asla unutma" talimatı ekle.
>
> **D)** Özetleme sıklığını azalt — her 15 turda bir özetle, 5 turda bir değil.

### Doğru Cevap: B

**Neden B doğru:** Klasik progressive summarization tuzağı. Özetleme sırasında sayısal değerler belirsiz ifadelere dönüşmüş. Çözüm: transaksiyonel gerçekleri (sipariş no, tutar, tarih) ayrı bir case facts bloğuna çıkar, her prompt'a dahil et, asla özetleme.

**Neden A yanlış:** Sorun context window boyutu değil, özetleme stratejisi. Daha büyük pencere de aynı özetleme stratejisiyle aynı bilgiyi kaybeder — ve pencere büyüklüğü dikkat kalitesini artırmaz.

**Neden C yanlış:** Prompt talimatı olasılıksal. Özetlenen bilgi bağlamda artık *yoksa*, "unutma" talimatı onu geri getiremez — yapısal soruna prompt çözümü.

**Neden D yanlış:** Özetleme sıklığını azaltmak sorunu geciktirir ama çözmez. 15. turda da aynı bilgi kaybı olacak.

---

## Pratik Senaryo 2

> Bir multi-agent araştırma sisteminde web search agent, synthesis agent'a sonuçları aktarıyor. Web search agent her sorgu için 3 sayfalık detaylı analiz, düşünce zinciri ve alternatif yorumlar döndürüyor. Synthesis agent'ın bağlam bütçesi 8K token ile sınırlı.
>
> Synthesis agent 3 kaynaktan sonra "yetersiz bağlam" hatası veriyor — 5 kaynağı analiz etmesi gerekiyor.
>
> **En etkili çözüm hangisidir?**
>
> **A)** Synthesis agent'ın bağlam bütçesini 32K token'a çıkar.
>
> **B)** Web search agent'ı yapılandırılmış veri (anahtar gerçekler, atıflar, ilgililik skoru) döndürecek şekilde modifiye et — verbose içerik ve düşünce zincirleri yerine.
>
> **C)** Synthesis agent'a "özet yaz, detay verme" talimatı ekle.
>
> **D)** Kaynak sayısını 3'e düşür — bütçeye sığar.

### Doğru Cevap: B

**Neden B doğru:** Upstream agent optimisation. Sorun synthesis agent'ta değil, web search agent'ın verbose çıktısında. Agent'ı yapılandırılmış veri döndürecek şekilde modifiye etmek — anahtar gerçekler, atıflar, ilgililik skoru — token bütçesini verimli kullanır ve 5 kaynağı da kapsar.

**Neden A yanlış:** Bütçeyi artırmak pahalı ve temel sorunu çözmez. Verbose içerik hâlâ gereksiz token harcar — 10 kaynağa çıkınca yine aynı sorun.

**Neden C yanlış:** Yanlış yerde çözüm arıyor. Sorun synthesis agent'ın çıktısında değil, girdisinde. Gelen veri zaten verbose — synthesis agent'a talimat vermek bunu değiştirmez.

**Neden D yanlış:** Kapsamı daraltmak kaliteyi düşürür. 5 kaynak gerekiyorsa 3'e düşürmek eksik araştırma demek.

---

## Pratik Senaryo 3

> Bir müşteri destek agent'ı case facts bloğu kullanıyor ve tek konulu konuşmalarda sorunsuz çalışıyor. Bir müşteri aynı konuşmada önce #8891 numaralı sipariş için $247.83 iade, sonra #8902 için hasarlı ürün değişimi, sonra da bir fatura itirazı açıyor. 9. turda agent değişim talebine "$247.83 tutarındaki iadeniz için fotoğraf bekliyoruz" diye cevap veriyor — iki konuyu karıştırmış.
>
> **Kök neden ve çözüm nedir?**
>
> **A)** Case facts bloğu özetlenmiş; bloğu "asla özetleme" kuralıyla tekrar koru.
>
> **B)** Tek bir case facts bloğu birden fazla konuyu taşıyamıyor; her konu için ayrı yapılandırılmış kayıt ve `active_issue` alanı içeren konu bazlı bir bağlam katmanı kur.
>
> **C)** Her yeni konu için yeni bir konuşma başlat; agent tek seferde tek konu yürütsün.
>
> **D)** Agent'a "konuları karıştırma" talimatı ekle ve özetleme sıklığını düşür.

### Doğru Cevap: B

**Neden B doğru:** Case facts tek vaka içindir. Çok konulu oturumda exam guide'ın istediği şey konu başına yapılandırılmış kayıt (order ID, tutar, durum) tutan **ayrı bir bağlam katmanı**dır; `active_issue` agent'ın hangi konuda olduğunu belirsizlikten kurtarır.

**Neden A yanlış:** Blok özetlenmemiş; sorun bloğun *yapısı* — tek bir `order_id` ve tek bir `refund_amount` alanı üç konuyu temsil edemez.

**Neden C yanlış:** Müşteri deneyimini bozar ve gerçek dünyada uygulanamaz; müşteri konuları aynı konuşmada açar. Mimari sorunun ürün kısıtıyla çözülmesi.

**Neden D yanlış:** Talimat olasılıksal; agent karıştırmak *istemiyor*, elinde konuları ayıran veri yapısı yok. Özetleme sıklığı bu senaryoda sorunun nedeni değil.
