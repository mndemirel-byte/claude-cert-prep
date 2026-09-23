# Task Statement 5.1: Bağlam Koruma (Context Preservation)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Agent'lar uzun konuşmalar boyunca çalışır, araç sonuçlarını biriktirir ve önceki turlardan gelen bilgiye dayanarak karar verir. Bu süreçte **kritik bilgilerin kaybolması** en yaygın ve en tehlikeli hatadır. Bu task statement, bağlam kaybını nasıl önleyeceğini öğretir.

Sınavda bu kavramlar özellikle **Customer Support Resolution Agent** ve **Multi-Agent Research System** senaryolarında karşına çıkacak.

---

## Progressive Summarisation Tuzağı

Uzun konuşmalarda token bütçesini yönetmek için konuşma geçmişi özetlenebilir. İşte tam burada tehlike başlıyor.

### Problem

Özetleme sırasında sayısal değerler, tarihler, yüzdeler ve müşteri beklentileri **belirsiz ifadelere** dönüşür:

| Orijinal bilgi | Özetlenmiş hali |
|---|---|
| "Müşteri sipariş #8891 için $247.83 iade istiyor, sipariş 3 Mart'ta verilmiş" | "müşteri yakın tarihli bir sipariş için iade istiyor" |
| "Müşteri %15 indirim beklentisi var, son 3 siparişte toplam $1,200 harcamış" | "müşteri indirim istiyor, düzenli müşteri" |

Sipariş numarası, tutar, tarih — hepsi uçuyor. Agent daha sonra bu belirsiz özetle çalışmak zorunda kalınca doğru işlem yapamaz.

### Çözüm: Kalıcı "Vaka Gerçekleri" (Case Facts) Bloğu

Transaksiyonel gerçekleri ayrı bir yapılandırılmış bloğa çıkar. Bu bloğu **her prompt'a dahil et** ve **asla özetleme**.

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

---

## "Ortada Kaybolma" Etkisi (Lost in the Middle)

### Problem

Modeller uzun girdilerin **başını** ve **sonunu** güvenilir şekilde işler. Ancak **ortaya gömülmüş** bulgular gözden kaçabilir.

Düşün: 10 sayfalık bir araştırma raporunda 7 farklı kaynak var. Kritik bir istatistik 5. kaynağın ortasında gizli. Model bu istatistiği atlayabilir — baştan veya sondan bakan dikkat mekanizması onu kaçırır.

### Çözüm

İki yöntem birlikte uygulanır:

1. **Anahtar bulguların özetini BAŞA yerleştir.** Uzun girdinin en tepesinde, en önemli bulguların kısa bir özetini sun.
2. **Açık bölüm başlıkları (section headers) kullan.** İçeriği yapılandırılmış bölümlere ayır — model bölüm başlıklarını referans noktası olarak kullanabilir.

```
## ÖNEMLİ BULGULAR ÖZETİ
- Jeotermal enerji kapasitesi %23 arttı (Kaynak: IEA 2024)
- Rüzgâr enerjisi yatırımları $120B'ye ulaştı (Kaynak: IRENA)
- Güneş paneli maliyeti %14 düştü (Kaynak: BloombergNEF)

## DETAYLI BULGULAR
### 1. Jeotermal Enerji
[detaylı içerik...]

### 2. Rüzgâr Enerjisi
[detaylı içerik...]
```

---

## Araç Sonucu Budama (Tool Result Trimming)

### Problem

Bir sipariş arama aracı 40'tan fazla alan döndürür: dahili ID'ler, lojistik kodları, depo bilgileri, vergi detayları... Ama agent'ın ihtiyacı sadece 5 alan.

Bu verbose (uzun) sonuçlar bağlama eklendikçe **token bütçesi tükenir** ve gerçekten önemli bilgi birikmiş gereksiz verinin altında kaybolur.

### Çözüm

Araç sonuçlarını bağlama eklemeden **ÖNCE** ilgili alanlara kırp:

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

Bu, birikimli gereksiz veriden kaynaklanan token bütçesi tükenmesini önler.

---

## Tam Geçmiş Gereksinimi (Full History)

### Kural

Ardışık API isteklerinde **tam konuşma geçmişi** dahil edilmelidir. Önceki mesajları çıkarmak konuşma tutarlılığını bozar.

### Neden?

Claude API durumsuz (stateless) çalışır — her istek bağımsızdır. Önceki mesajları göndermezsen, model konuşmanın bağlamını kaybeder:

- Kullanıcı 3. turda "önceki soruma ek olarak..." derse, 1. ve 2. tur mesajları olmadan model ne sorulduğunu bilemez
- Kararlar önceki turlardaki araç sonuçlarına dayanıyorsa, o sonuçlar geçmişte olmalıdır

**İstisna:** Geçmiş çok uzadığında, eski turların **içeriği özetlenebilir** — ama vaka gerçekleri bloğu HER ZAMAN tam kalır.

---

## Üst-Akış Agent Optimizasyonu (Upstream Agent Optimisation)

### Problem

Bir araştırma agent'ı 3 sayfalık detaylı analiz ve düşünce zinciri döndürüyor. Bu sonuç, bağlam bütçesi sınırlı bir alt-akış (downstream) agent'a aktarılacak. 3 sayfalık verbose içerik alt-akış agent'ın bağlamını tüketir.

### Çözüm

Üst-akış agent'ları, verbose içerik ve düşünce zincirleri yerine **yapılandırılmış veri** döndürecek şekilde modifiye et:

```json
{
  "key_facts": [
    {"claim": "Solar capacity grew 45%", "confidence": 0.95},
    {"claim": "Wind investments hit $120B", "confidence": 0.88}
  ],
  "citations": [
    {"source": "IEA Report 2024", "url": "https://...", "page": 12}
  ],
  "relevance_score": 0.92,
  "coverage_gaps": ["Geothermal data unavailable"]
}
```

| Yaklaşım | Sonuç |
|---|---|
| Verbose döndür | Alt-akış agent bağlam bütçesini tüketir |
| Yapılandırılmış veri döndür | Anahtar bilgiler korunur, bütçe verimli kullanılır |

Bu, özellikle alt-akış agent'ların sınırlı bağlam bütçeleri olduğunda kritiktir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Progressive summarisation tuzağı | Özetleme sayısal değerleri, tarihleri, yüzdeleri belirsiz ifadelere dönüştürür |
| Case facts bloğu | Transaksiyonel gerçekleri ayrı blokta tut, ASLA özetleme |
| Lost in the middle | Ortaya gömülmüş bulgular kaçabilir → önemli bulguları başa koy |
| Section headers | Açık bölüm başlıkları model için referans noktası oluşturur |
| Tool result trimming | Verbose sonuçları ilgili alanlara kırp, SONRA bağlama ekle |
| Full history | API isteklerinde tam konuşma geçmişi gönder — tutarlılık için |
| Upstream optimisation | Agent'ları verbose yerine yapılandırılmış veri döndürecek şekilde modifiye et |

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

**Neden B doğru:** Klasik progressive summarisation tuzağı. Özetleme sırasında sayısal değerler belirsiz ifadelere dönüşmüş. Çözüm: transaksiyonel gerçekleri (sipariş no, tutar, tarih) ayrı bir case facts bloğuna çıkar, her prompt'a dahil et, asla özetleme.

**Neden A yanlış:** Sorun context window boyutu değil, özetleme stratejisi. Daha büyük model de aynı özetleme stratejisiyle aynı bilgiyi kaybeder.

**Neden C yanlış:** Prompt talimatı olasılıksal. "Unutma" demek yapısal bir soruna prompt çözümü — özetlenen bilgi context'ten fiziksel olarak çıkarılmışsa, talimat işe yaramaz.

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
