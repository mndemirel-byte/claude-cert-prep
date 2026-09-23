# Task Statement 5.6: Bilgi Kaynağı Takibi (Information Provenance)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir multi-agent araştırma sistemi 5 farklı kaynaktan veri topluyor ve sentez raporu yazıyor. Rapor mükemmel yazılmış ama bir iddia sorgulanıyor: "Güneş enerjisi kapasitesi %45 arttı." Bu iddia hangi kaynaktan geliyor? Hangi tarihte yayımlanmış? Kaynağın orijinal ifadesi ne?

Bu bilgi sentez sırasında kaybolmuşsa → **atıf ölü**. Okuyucu iddianın güvenilirliğini değerlendiremez.

Bu task statement, bilgi kaynak eşleştirmelerinin nasıl korunacağını, çelişkili kaynakların nasıl ele alınacağını ve zamansal farkındalığı öğretir.

---

## Yapılandırılmış İddia-Kaynak Eşleştirmeleri (Claim-Source Mappings)

### Kavram

Her bulgu için beş bilgi parçası korunmalı:

| Bileşen | Açıklama | Örnek |
|---|---|---|
| **İddia (Claim)** | Bulgunun ifadesi | "Güneş enerjisi kapasitesi %45 arttı" |
| **Kaynak URL** | Orijinal kaynağın bağlantısı | "https://iea.org/reports/solar-2024" |
| **Doküman adı** | Kaynağın başlığı | "IEA Solar Market Report 2024" |
| **İlgili alıntı** | Kaynaktan ilgili pasaj | "Global solar PV capacity additions grew by 45%..." |
| **Yayım tarihi** | Kaynağın yayım tarihi | "2024-06-15" |

### Yapılandırılmış Format

```json
{
  "finding": {
    "claim": "Solar energy capacity grew 45% in 2024",
    "source_url": "https://iea.org/reports/solar-2024",
    "document_name": "IEA Solar Market Report 2024",
    "relevant_excerpt": "Global solar PV capacity additions grew by 45% year-on-year...",
    "publication_date": "2024-06-15"
  }
}
```

### Sentez Sırasında Koruma

Kritik kural: Alt-akış (downstream) agent'lar bu eşleştirmeleri **korur ve birleştirir**. Sentez sırasında iddialar yeniden ifade edilse bile kaynak bağlantısı korunmalı.

**YANLIŞ — sentez sırasında atıf kaybı:**
> "Yenilenebilir enerji sektöründe önemli büyümeler yaşandı. Güneş ve rüzgâr enerjisi yatırımları artış gösterdi."

**DOĞRU — sentez sırasında atıf korunması:**
> "Güneş enerjisi kapasitesi %45 arttı [IEA, 2024-06]. Rüzgâr enerjisi yatırımları $120B'ye ulaştı [IRENA, 2024-03]."

---

## Çelişki Yönetimi (Conflict Handling)

### Problem

İki güvenilir kaynak farklı istatistikler raporluyor:

- IEA: "Güneş enerjisi kapasitesi %45 arttı"
- BloombergNEF: "Güneş enerjisi kapasitesi %38 arttı"

### Yanlış Yaklaşım

Birini keyfi olarak seçme:

- ❌ "Daha güncel olanı seç"
- ❌ "Daha tanınmış kaynağı seç"
- ❌ "İkisinin ortalamasını al"

### Doğru Yaklaşım

Her iki değeri kaynak atıflarıyla birlikte sun — kararı tüketiciye bırak:

```json
{
  "claim": "Solar energy capacity growth in 2024",
  "conflicting_values": [
    {
      "value": "45%",
      "source": "IEA Solar Market Report 2024",
      "publication_date": "2024-06-15",
      "methodology_note": "Includes utility-scale and rooftop installations"
    },
    {
      "value": "38%",
      "source": "BloombergNEF New Energy Outlook",
      "publication_date": "2024-03-20",
      "methodology_note": "Utility-scale installations only"
    }
  ],
  "resolution_note": "Difference likely due to scope: IEA includes rooftop, BNEF does not"
}
```

**Kural:** Çelişkili kaynaklarda birini keyfi olarak seçme. Her iki değeri kaynak atıflarıyla sun, farkın olası nedenini belirt, kararı tüketiciye bırak.

---

## Zamansal Farkındalık (Temporal Awareness)

### Problem

İki kaynak farklı sayılar raporluyor ama bu bir çelişki değil — farklı zamanlardaki veriler:

- Kaynak A (Ocak 2024): "İşsizlik oranı %5.2"
- Kaynak B (Haziran 2024): "İşsizlik oranı %4.8"

Bu bir çelişki değil, zamana bağlı değişim. Ama tarihler belirtilmezse çelişki gibi görünür.

### Çözüm

Yapılandırılmış çıktılarda yayım/veri toplama tarihlerini zorunlu kıl:

```json
{
  "data_points": [
    {
      "metric": "Unemployment rate",
      "value": "5.2%",
      "data_collection_date": "2024-01-15",
      "publication_date": "2024-02-01",
      "source": "National Statistics Office"
    },
    {
      "metric": "Unemployment rate",
      "value": "4.8%",
      "data_collection_date": "2024-06-15",
      "publication_date": "2024-07-01",
      "source": "National Statistics Office"
    }
  ],
  "temporal_note": "Values reflect different time periods, not conflicting data"
}
```

**Kural:** Farklı tarihler farklı sayıları açıklar — çelişki değil, zamana bağlı değişim. Tarihler olmadan bu ayrım yapılamaz.

---

## İçeriğe Uygun Sunum (Content-Appropriate Rendering)

### Problem

Tüm bulguları tek bir düz format (örn. hep liste, hep tablo, hep paragraf) olarak sunmak bilgi kaybına ve okunabilirlik düşüşüne yol açar.

### Çözüm

Her içerik türü kendi doğal formatında sunulmalı:

| İçerik Türü | Uygun Format | Neden |
|---|---|---|
| Finansal veriler | Tablo | Sayısal karşılaştırma, sütunlar arası ilişki |
| Haber/gelişmeler | Nesir (prose) | Zaman akışı, bağlam, neden-sonuç |
| Teknik bulgular | Yapılandırılmış liste | Hızlı tarama, kategorizasyon |
| İstatistiksel karşılaştırma | Tablo + grafik açıklaması | Veri yoğunluğu, karşılaştırma kolaylığı |

**Kural:** Her şeyi tek bir düz formata sıkıştırma. Finansal veriyi tabloda, haberi nesirde, teknik bulguları yapılandırılmış listede sun.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| İddia-kaynak eşleştirmesi | Her iddia: claim + URL + doküman adı + alıntı + tarih |
| Sentez sırasında koruma | Alt-akış agent'lar eşleştirmeleri korur ve birleştirir |
| Atıf ölümü | Eşleştirme yoksa sentez sırasında atıf kaybolur |
| Çelişki yönetimi | Birini keyfi seçme — ikisini de kaynak atıflarıyla sun |
| Zamansal farkındalık | Farklı tarihler farklı sayıları açıklar — çelişki değil |
| Tarih zorunluluğu | Yayım/veri toplama tarihlerini yapılandırılmış çıktıda zorunlu kıl |
| İçerik formatı | Finansal → tablo, haber → nesir, teknik → yapılandırılmış liste |

---

## Pratik Senaryo 1

> Bir multi-agent araştırma sistemi enerji sektörü raporu yazıyor. Sentez agent'ı şu cümleyi üretiyor:
>
> "Yenilenebilir enerji sektöründe son yıllarda kayda değer büyüme gözlemlenmektedir. Güneş enerjisi kapasitesi önemli ölçüde artmıştır."
>
> Okuyucu soruyor: "%kaç arttı? Hangi kaynak? Hangi yıl?"
>
> Web search subagent aslında spesifik veriler bulmuştu: IEA raporuna göre %45, IRENA raporuna göre %42.
>
> **Kök neden ve çözüm nedir?**
>
> **A)** Sentez agent'ın system prompt'una "spesifik ol" talimatı ekle.
>
> **B)** Web search subagent'tan sentez agent'a aktarılan veriden yapılandırılmış iddia-kaynak eşleştirmeleri eksik. Aktarım formatını structured claim-source mappings içerecek şekilde değiştir.
>
> **C)** Sentez agent'ın context window'u küçük — daha büyük model kullan.
>
> **D)** Web search subagent'a daha detaylı arama yaptır.

### Doğru Cevap: B

**Neden B doğru:** Atıf ölümü — web search subagent spesifik veriler bulmuş ama sentez agent'a yapılandırılmış formatta aktarılmamış. Sentez agent kaynak ve değerleri bilmeden belirsiz ifadeler kullanıyor. Çözüm: structured claim-source mappings ile her iddiayı kaynak, URL, tarih ve değerle eşleştirerek aktar.

**Neden A yanlış:** Prompt talimatı yapısal sorunu çözmez. Sentez agent'a gelen veride kaynak eşleştirmesi yoksa, "spesifik ol" demek eksik veriyi yaratamaz.

**Neden C yanlış:** Sorun context window boyutu değil, veri formatı. Büyük model de yapılandırılmamış girdiden kaynak atıfı üretemez.

**Neden D yanlış:** Web search agent zaten spesifik veriler bulmuş — arama kalitesi sorun değil. Sorun aktarım formatında.

---

## Pratik Senaryo 2

> Bir araştırma raporu şu iki bulguyu içeriyor:
>
> - Kaynak A (IEA, Ocak 2024): "Küresel karbon emisyonları 37.4 Gt"
> - Kaynak B (IEA, Temmuz 2024): "Küresel karbon emisyonları 36.8 Gt"
>
> Agent bu durumu "çelişkili veri" olarak işaretliyor ve hangi değerin doğru olduğuna karar veremiyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Daha güncel olan değeri (36.8 Gt) kullan — son veri her zaman doğrudur.
>
> **B)** İkisinin ortalamasını al — 37.1 Gt.
>
> **C)** Her iki değeri kaynak atıfları ve tarihlerle birlikte sun. Farkın zamana bağlı olabileceğini belirt — farklı ölçüm dönemleri farklı sonuçlar verir.
>
> **D)** Her iki kaynağı da çıkar — çelişkili veri güvenilmez.

### Doğru Cevap: C

**Neden C doğru:** Zamansal farkındalık + çelişki yönetimi. İki değer aynı kaynaktan farklı tarihlerde — bu çelişki değil, farklı ölçüm dönemleri. Her iki değeri tarihlerle sun ve zamansal bağlamı belirt.

**Neden A yanlış:** "Son veri doğrudur" varsayımı her zaman geçerli değil. Ocak verisi 2023 yılına, Temmuz verisi 2024 ilk yarısına ait olabilir — farklı dönemleri ölçüyorlar.

**Neden B yanlış:** İstatistiklerin ortalamasını almak anlamsız — iki farklı dönemin ölçümlerini karıştırır. Sonuç ne birinci ne ikinci dönemi temsil eder.

**Neden D yanlış:** Çelişkili gibi görünen veriyi çıkarmak bilgi kaybı. Zamansal bağlamla açıklanabilen farklar güvenilmez değil.
