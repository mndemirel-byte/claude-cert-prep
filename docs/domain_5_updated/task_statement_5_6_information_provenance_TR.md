# Task Statement 5.6: Bilgi Kaynağı Takibi (Information Provenance)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir multi-agent araştırma sistemi 5 farklı kaynaktan veri topluyor ve sentez raporu yazıyor. Rapor mükemmel yazılmış ama bir iddia sorgulanıyor: "Güneş enerjisi kapasitesi %45 arttı." Bu iddia hangi kaynaktan geliyor? Hangi tarihte yayımlanmış? Kaynağın orijinal ifadesi ne — kesin ölçüm mü, ön tahmin mi?

Bu bilgi sentez sırasında kaybolmuşsa → **atıf ölü**. Okuyucu iddianın güvenilirliğini değerlendiremez.

Bu task statement, bilgi kaynak eşleştirmelerinin nasıl korunacağını, çelişkili kaynakların **kim tarafından** ve nasıl ele alınacağını, zamansal farkındalığı ve raporun yapısını öğretir. 5.1'in "subagent metadata zorunluluğu" maddesiyle aynı omurgadadır: tarih, kaynak konumu, metodoloji.

Sınav senaryosu: **Multi-Agent Research System**. Egzersiz 4 adım 18 ve 20 bu statement'ın kabul kriterleridir.

---

## Yapılandırılmış İddia-Kaynak Eşleştirmeleri (Claim-Source Mappings)

### Kavram

Her bulgu için korunacak bilgi parçaları (Egzersiz 4 adım 18: "*claim, evidence excerpt, source URL/document name, and publication date*" + kaynağın kendi nitelendirmesi):

| Bileşen | Açıklama | Örnek |
|---|---|---|
| **İddia (Claim)** | Bulgunun ifadesi | "Güneş enerjisi kapasitesi %45 arttı" |
| **Kaynak URL** | Orijinal kaynağın bağlantısı | "https://iea.org/reports/solar-2024" |
| **Doküman adı** | Kaynağın başlığı | "IEA Solar Market Report 2024" |
| **İlgili alıntı** | Kaynaktan ilgili pasaj | "Global solar PV capacity additions grew by 45%..." |
| **Yayım tarihi** | Kaynağın yayım / veri toplama tarihi | "2024-06-15" |
| **Kaynağın nitelendirmesi** | Kaynağın iddiayı *nasıl* sunduğu | "preliminary estimate" / "measured" / "projected" |
| **Metodoloji notu** | Kaynağın kendi kapsam beyanı | "includes utility-scale and rooftop" |

### Yapılandırılmış Format

```json
{
  "finding": {
    "claim": "Solar energy capacity grew 45% in 2024",
    "source_url": "https://iea.org/reports/solar-2024",
    "document_name": "IEA Solar Market Report 2024",
    "relevant_excerpt": "Global solar PV capacity additions grew by 45% year-on-year (preliminary estimate)...",
    "publication_date": "2024-06-15",
    "source_characterization": "preliminary estimate",
    "methodology_note": "includes utility-scale and rooftop installations"
  }
}
```

### Sentez Sırasında Koruma

Kritik kural: Alt-akış (downstream) agent'lar bu eşleştirmeleri **korur ve birleştirir**. Sentez sırasında iddialar yeniden ifade edilse bile kaynak bağlantısı **ve nitelendirme** korunmalı.

**YANLIŞ — sentez sırasında atıf kaybı:**
> "Yenilenebilir enerji sektöründe önemli büyümeler yaşandı. Güneş ve rüzgâr enerjisi yatırımları artış gösterdi."

**YANLIŞ — atıf var, nitelendirme kaybolmuş (daha sinsi):**
> "Güneş enerjisi kapasitesi %45 arttı [IEA, 2024-06]." — kaynak "ön tahmin" demişti; sentez bunu kesin ölçüme yükseltti.

**DOĞRU — atıf ve nitelendirme korunmuş:**
> "IEA'nın ön tahminine göre güneş enerjisi kapasitesi %45 arttı [IEA, 2024-06, çatı üstü dahil]. Rüzgâr enerjisi yatırımları $120B'ye ulaştı [IRENA, 2024-03]."

**Kural:** Sentez, kaynağın kesinlik derecesini ne **yumuşatır** ne **sertleştirir**. Exam guide: "*preserving original source characterizations and methodological context*".

> **Güncel not (sınav cevabını değiştirmez):** Messages API'nin **Citations** özelliği (`document` bloklarında `citations: {enabled: true}`) belge analizi subagent'ına atıfı API seviyesinde zorlar — yanıt `cited_text` + belge indeksi + konum ile döner; claim-source eşleştirmesinin "alıntı + konum" kısmı elle şema yerine API'den alınabilir. Anthropic'in araştırma sisteminde de ayrı bir **CitationAgent** son işlem olarak atıf yerlerini belirler. Guide'ın cevabı yapılandırılmış eşleştirmedir; bu kutu "nasıl uygulanır" için.

---

## Çelişki Yönetimi (Conflict Handling) — Kim Karar Verir?

### Problem

İki güvenilir kaynak farklı istatistikler raporluyor:

- IEA: "Güneş enerjisi kapasitesi %45 arttı"
- BloombergNEF: "Güneş enerjisi kapasitesi %38 arttı"

### Yanlış Yaklaşım

Birini keyfi olarak seçme — hangi katmanda olursa olsun:

- ❌ "Daha güncel olanı seç"
- ❌ "Daha tanınmış kaynağı seç"
- ❌ "İkisinin ortalamasını al"
- ❌ Belge analizi subagent'ının "bence bu doğru" diye tek değer döndürmesi

### Doğru Yaklaşım — üç rol

Exam guide'ın Skills maddesi: "*Completing document analysis with conflicting values included and explicitly annotated, letting the **coordinator** decide how to reconcile **before passing to synthesis***".

| Rol | Ne yapar | Ne yapmaz |
|---|---|---|
| **Belge analizi subagent'ı** | Analizi *tamamlar*, her iki değeri kaynak, tarih ve metodoloji notuyla **işaretleyip** döndürür | Seçmez, ortalamaz, susmaz |
| **Koordinatör** | Uzlaştırma **kararını** verir: ikisini de sun / metodolojiye göre birini öne al / "tartışmalı" bölümüne koy / ek kaynak iste | Subagent'a "birini seç" demez |
| **Sentez agent'ı** | Koordinatörün kararına göre yazar; raporda **iki değeri de kaynağıyla** gösterir | Kendi başına uzlaştırmaz |

Nihai okuyucu iki değeri de görür; ama *mimarideki karar noktası* koordinatördür — "kararı okuyucuya bırak" tek başına yanlış değil, eksiktir.

```json
{
  "claim": "Solar energy capacity growth in 2024",
  "conflicting_values": [
    {
      "value": "45%",
      "source": "IEA Solar Market Report 2024",
      "publication_date": "2024-06-15",
      "source_characterization": "preliminary estimate",
      "methodology_note": "Includes utility-scale and rooftop installations (source: methodology section, p.4)"
    },
    {
      "value": "38%",
      "source": "BloombergNEF New Energy Outlook",
      "publication_date": "2024-03-20",
      "source_characterization": "measured",
      "methodology_note": "Utility-scale installations only (source: p.2 scope note)"
    }
  ],
  "conflict_status": "unresolved — coordinator decision required",
  "reconciliation_hypothesis": "Scope difference (rooftop inclusion) may explain the gap — hypothesis, not stated by either source"
}
```

**Uydurma gerekçe uyarısı:** `methodology_note` kaynakların *kendi* beyanından gelir (konumuyla). Farkın *nedenini* açıklayan cümle ise sentez agent'ın çıkarımıdır — kaynak öyle demediyse **hipotez** olarak etiketlenir (`reconciliation_hypothesis`), gerçek gibi yazılmaz. "Muhtemelen kapsam farkı" cümlesi, kaynağa dayanmıyorsa halüsinasyon kapısıdır.

---

## Zamansal Farkındalık (Temporal Awareness)

### Problem

İki kaynak farklı sayılar raporluyor ama bu bir çelişki değil — farklı zamanlardaki veriler:

- Kaynak A (Ocak 2024): "İşsizlik oranı %5.2"
- Kaynak B (Haziran 2024): "İşsizlik oranı %4.8"

Bu bir çelişki değil, zamana bağlı değişim. Ama tarihler belirtilmezse çelişki gibi görünür.

### Çözüm

Yapılandırılmış çıktılarda yayım/veri toplama tarihlerini **zorunlu** kıl (5.1 subagent metadata maddesiyle aynı):

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
  "temporal_note": "Values reflect different collection periods, not conflicting data"
}
```

### Revizyon ≠ zamansal fark — ince ayrım

| Durum | Ne oluyor | Doğru davranış |
|---|---|---|
| **Farklı dönemler** | Ocak verisi Ocak'ı, Haziran verisi Haziran'ı ölçüyor | İki değer de doğru; tarihlerle sun, çelişki değil |
| **Aynı dönemin revizyonu** | Aynı kurum aynı dönemin rakamını sonradan düzeltmiş ("2023 emisyonu 37.4 → 36.8 Gt, revize") | Güncel (revize) değer geçerli; ama "revize edildi, önceki değer X" notu düşülür |
| **Farklı kurumlar, farklı yöntem** | IEA vs BNEF | Çelişki yönetimi — koordinatör uzlaştırır |

Tarih olmadan bu üç durum ayırt edilemez. "Son veri her zaman doğrudur" yalnızca ikinci satırda geçerlidir; birinci satırda yanlıştır.

---

## Rapor İskeleti — Desteklenen / Tartışmalı / Boşluklu

Exam guide'ın Skills maddesi: "*Structuring reports with explicit sections distinguishing **well-established findings from contested ones**, preserving original source characterizations and methodological context*". Egzersiz 4 adım 20 bunu kabul kriteri yapar.

5.3'ün kapsam açıklamalarıyla birleşince sentez raporunun iskeleti üç bölümdür:

```
## 1. İyi Desteklenen Bulgular
Birden fazla bağımsız kaynağın uyuştuğu ya da tek güçlü kaynağın kesin ölçüm olarak
sunduğu bulgular. Her satırda kaynak, tarih, nitelendirme.
- Rüzgâr yatırımları $120B [IRENA 2024-03, ölçüm; BNEF 2024-03, ölçüm — uyumlu]

## 2. Tartışmalı Bulgular
Güvenilir kaynakların uyuşmadığı bulgular. Her iki değer, kaynak, tarih, metodoloji;
koordinatörün uzlaştırma notu ve varsa hipotez etiketi.
- Güneş kapasitesi artışı: %45 [IEA, ön tahmin, çatı üstü dahil] vs %38 [BNEF, ölçüm,
  yalnızca şebeke ölçeği] — kapsam farkı hipotezi (kaynaklar belirtmiyor)

## 3. Kapsam Boşlukları (5.3)
Erişilemeyen / eksik kaynaklar nedeniyle sınırlı kalan alanlar.
- Jeotermal: ScienceDirect zaman aşımı — tek kaynak, sınırlı
```

Sınavın "sentez raporu nasıl yapılandırılmalı?" sorusunun cevabı bu üçlüdür; "tek bir tutarlı anlatı yaz, çelişkileri çöz" distractor'dır.

---

## İçeriğe Uygun Sunum (Content-Appropriate Rendering)

### Problem

Tüm bulguları tek bir düz format (örn. hep liste, hep tablo, hep paragraf) olarak sunmak bilgi kaybına yol açar. Guide: "*rather than converting everything to a uniform format*".

### Çözüm

Her içerik türü kendi doğal formatında sunulmalı — ve formatı değiştirince *ne kaybolduğunu* bil:

| İçerik Türü | Uygun Format | Tekdüze formata çevrilince ne kaybolur |
|---|---|---|
| Finansal veriler | **Tablo** | Nesirde sütunlar arası karşılaştırma ve birimler kaybolur |
| Haber / gelişmeler | **Nesir (prose)** | Tabloda zaman akışı ve neden-sonuç bağı kaybolur |
| Teknik bulgular | **Yapılandırılmış liste** | Nesirde taranabilirlik ve kategori kaybolur |

**Kural:** Her şeyi tek bir düz formata sıkıştırma. Finansal veriyi tabloda, haberi nesirde, teknik bulguları yapılandırılmış listede sun.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| İddia-kaynak eşleştirmesi | Claim + URL + doküman adı + alıntı + tarih + **kaynağın nitelendirmesi** + metodoloji |
| Sentez sırasında koruma | Alt-akış agent'lar eşleştirmeleri korur ve birleştirir; nitelendirmeyi yumuşatmaz/sertleştirmez |
| Atıf ölümü | Eşleştirme yoksa sentez sırasında atıf kaybolur; nitelendirme kaybı daha sinsi |
| Çelişki — kim karar verir | Subagent işaretler, **koordinatör uzlaştırır**, sentez ikisini de kaynağıyla gösterir |
| Uydurma gerekçe | Fark nedeni kaynakta yoksa `hypothesis` etiketiyle; gerçek gibi yazma |
| Zamansal farkındalık | Farklı dönemler → ikisi de doğru; aynı dönemin revizyonu → güncel geçerli + not |
| Tarih zorunluluğu | Yayım/veri toplama tarihi yapılandırılmış çıktıda zorunlu (5.1 metadata) |
| Rapor iskeleti | Desteklenen / Tartışmalı / Kapsam boşlukları (5.3) |
| İçerik formatı | Finansal → tablo, haber → nesir, teknik → yapılandırılmış liste; tekdüze format bilgi kaybıdır |

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
> **A)** Sentez agent'ın system prompt'una "spesifik ol, kaynak göster" talimatı ekle.
>
> **B)** Web search subagent'tan sentez agent'a aktarılan veride yapılandırılmış iddia-kaynak eşleştirmeleri yok. Subagent çıktısını claim + alıntı + kaynak/URL + tarih + nitelendirme içerecek şekilde zorunlu kıl; sentez bu eşleştirmeleri korusun.
>
> **C)** Sentez agent'ın context window'u küçük — daha büyük model kullan.
>
> **D)** Sentez sonrası bir "doğrulama agent'ı" raporu okuyup her iddia için web'de kaynak arasın.

### Doğru Cevap: B

**Neden B doğru:** Atıf ölümü — web search subagent spesifik veriler bulmuş ama sentez agent'a yapılandırılmış formatta aktarılmamış. Çözüm kaynakta: subagent çıktı şeması claim-source eşleştirmesini zorunlu kılar (Egzersiz 4 adım 18), sentez korur.

**Neden A yanlış:** Prompt talimatı yapısal sorunu çözmez. Sentez agent'a gelen veride kaynak eşleştirmesi yoksa, "kaynak göster" demek eksik veriyi yaratamaz — ya da daha kötüsü, uydurtur.

**Neden C yanlış:** Sorun context window boyutu değil, veri formatı.

**Neden D yanlış:** Sonradan kaynak aramak, subagent'ın *zaten bulduğu* kaynağı yeniden keşfetmeye çalışmaktır; yanlış kaynağa bağlama riski taşır ve maliyeti ikiye katlar. Atıf, üretim anında korunur, sonradan üretilmez.

---

## Pratik Senaryo 2

> Bir araştırma raporu şu iki bulguyu içeriyor:
>
> - Kaynak A (IEA, Ocak 2024 yayını): "2023 küresel karbon emisyonları 37.4 Gt (ön tahmin)"
> - Kaynak B (IEA, Temmuz 2024 yayını): "2023 küresel karbon emisyonları 36.8 Gt (revize)"
>
> Agent bu durumu "çelişkili veri" olarak işaretliyor ve hangi değerin doğru olduğuna karar veremiyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** İkisinin ortalamasını al — 37.1 Gt.
>
> **B)** Her iki değeri farklı ölçüm dönemleri olarak sun — zamansal fark, çelişki değil.
>
> **C)** Aynı kurumun aynı dönem (2023) için yaptığı revizyon: güncel değer (36.8 Gt) geçerlidir; raporda "revize edildi, ön tahmin 37.4 Gt idi" notu ve iki yayın tarihiyle sun.
>
> **D)** Her iki kaynağı da çıkar — çelişkili veri güvenilmez.

### Doğru Cevap: C

**Neden C doğru:** İki değer *aynı dönemi* (2023) ölçüyor ve aynı kurumdan; ikincisi açıkça "revize". Bu ne çelişki ne zamansal fark — revizyondur. Güncel değer geçerli, ama nitelendirme (ön tahmin → revize) ve iki tarih korunur.

**Neden A yanlış:** Ortalama, ön tahmin ile revize değeri karıştırır; hiçbir kaynağın söylemediği bir sayı üretir.

**Neden B yanlış:** Sınavın ince tuzağı: "farklı yayın tarihi = farklı dönem" değildir. Her iki yayın da *2023*'ü ölçüyor. Zamansal fark, *veri toplama dönemi* farklıysa geçerlidir; burada yayın tarihi farklı, dönem aynı.

**Neden D yanlış:** Revizyonla açıklanabilen veriyi çıkarmak bilgi kaybı.

---

## Pratik Senaryo 3

> Bir koordinatör, belge analizi subagent'ına "sektör büyüme oranını çıkar" görevi veriyor. Subagent iki güvenilir raporda %45 ve %38 buluyor, "IEA daha güvenilir" diyerek yalnızca %45'i döndürüyor. Sentez raporu %45'i kesin rakam olarak yazıyor; müşteri BNEF'in %38'ini gösterip raporu sorguluyor.
>
> **Hangi rol hatalı davrandı ve doğru akış nedir?**
>
> **A)** Sentez agent'ı: iki kaynağı da web'de aramalı ve kendisi karşılaştırmalıydı.
>
> **B)** Belge analizi subagent'ı: çelişkiyi çözmek onun işi değil. İki değeri de kaynak, tarih, nitelendirme ve metodoloji notuyla işaretleyip analizi tamamlamalı; uzlaştırma kararını koordinatör vermeli; sentez ikisini de "tartışmalı bulgular" bölümünde kaynağıyla göstermeli.
>
> **C)** Koordinatör: subagent'a "her zaman en güncel kaynağı seç" kuralı vermeliydi.
>
> **D)** Kimse hatalı değil; IEA gerçekten daha güvenilir bir kaynak.

### Doğru Cevap: B

**Neden B doğru:** Exam guide'ın rol dağılımı: subagent işaretler ve tamamlar, koordinatör uzlaştırır, sentez ikisini de gösterir. Subagent'ın "daha güvenilir" yargısıyla tek değer döndürmesi keyfi seçimdir ve bilgiyi yukarı katmanlardan gizler.

**Neden A yanlış:** Sentez agent'ı uzlaştırma katmanı değildir; üstelik subagent'ın zaten bulduğu kaynağı yeniden aramak israftır.

**Neden C yanlış:** "En güncel" de keyfi bir seçim kuralı — farklı metodolojileri görünmez kılar; revizyon dışında geçerli değildir.

**Neden D yanlış:** Kaynak güvenilirliği yargısı bile olsa, iki güvenilir kaynak arasındaki fark *okuyucudan gizlenemez*; rapor "tartışmalı" bölümünde ikisini de göstermek zorundadır.
