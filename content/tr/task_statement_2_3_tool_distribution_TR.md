# Task Statement 2.3: Araç Dağılımı ve tool_choice (Tool Distribution & tool_choice)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Bir agent'a kaç araç verirsin? Hepsini mi, yoksa sadece ihtiyacı olanları mı? Bu task statement tam olarak bu soruyu cevaplıyor.

---

## Araç Aşırı Yüklemesi Problemi (Tool Overload)

Bir agent'a 18 araç verirsen, seçim güvenilirliği düşer. Claude hangi aracı ne zaman kullanacağına karar vermekte zorlanır.

**Optimal:** Agent başına **4-5 araç**, rolüne göre kapsamlandırılmış.

Temel kural: **Her agent sadece kendi rolü için gereken araçlara sahip olmalı.**

- Sentez agent'ının web arama araçları olmamalı
- Web arama agent'ının doküman analiz araçları olmamalı
- Her agent kendi işine odaklı araç setine sahip olmalı

---

## tool_choice Konfigürasyonu

Üç mod var — sınav bunları birbirinden ayırt etmeni bekliyor:

### 1. `"auto"` (Varsayılan)
Model araç çağırıp çağırmamaya **kendisi** karar verir. Araç çağırmak yerine doğrudan metin yanıt da verebilir.

**Ne zaman kullanılır:** Genel operasyon. Çoğu durumda bu mod yeterli.

### 2. `"any"`
Model **mutlaka** bir araç çağırmalı ama hangisini çağıracağına kendisi karar verir.

**Ne zaman kullanılır:** Birden fazla şemadan birinden **garantili yapılandırılmış çıktı** istediğinde. Model metin yerine mutlaka bir araç çağırmalı.

### 3. `{"type": "tool", "name": "extract_metadata"}`
Model **mutlaka** bu belirli aracı çağırmalı. Seçim şansı yok.

**Ne zaman kullanılır:** Zorunlu ilk adımları dayatmak için. Örneğin, zenginleştirme (enrichment) adımlarından önce metadata çıkarımını zorunlu kılmak.

### Özet Tablo

| Mod | Davranış | Kullanım Alanı |
|---|---|---|
| `"auto"` | Model karar verir — araç veya metin | Genel operasyon, varsayılan |
| `"any"` | Mutlaka araç çağırır, hangisini seçer | Garantili yapılandırılmış çıktı |
| `{"type":"tool","name":"X"}` | Mutlaka belirtilen aracı çağırır | Zorunlu ilk adımlar |

---

## Kapsamlı Çapraz Rol Araçları (Scoped Cross-Role Tools) — SINAV SORUSU

Bu kalıp sınavda doğrudan test ediliyor. Senaryoyu ve çözümü iyi öğren.

### Problem

Bir sentez agent'ı sık sık basit doğrulama (fact verification) için koordinatöre kontrolü geri veriyor. Her seferinde 2-3 ek tur-dönüş (round-trip) oluyor ve toplam gecikme **%40** artıyor. Doğrulamaların **%85'i** basit arama (simple lookup).

### Çözüm: Kapsamlandırılmış verify_fact Aracı

Sentez agent'a **kapsamlandırılmış bir `verify_fact` aracı** ver — sadece basit aramalar yapabilir. Karmaşık doğrulamalar hâlâ koordinatör üzerinden yönlendirilir.

**Sonuç:**
- Vakaların %85'inde koordinatör tur-dönüş gecikmesi ortadan kalkar
- Kalan %15 karmaşık doğrulama hâlâ koordinatör üzerinden akar
- Gecikme önemli ölçüde azalır, mimari bütünlük korunur

### Neden Diğer Çözümler Yanlış?

| Çözüm | Neden Yanlış |
|---|---|
| Tüm doğrulamayı sentez agent'a ver | Çok geniş yetki — basit olmayan doğrulamalarda hata riski |
| Koordinatörü daha hızlı yap | Yapısal gecikmeyi çözmez — tur-dönüş hâlâ var |
| Doğrulama adımını kaldır | Fonksiyonalite kaybı — doğrulama önemli bir kalite adımı |
| Sentez agent'a tam fetch_url ver | Çok geniş kapsamlı — güvenlik riski, odak kaybı |

---

## Genel Araçları Kısıtlanmış Alternatiflerle Değiştirme

Subagent'lara genel amaçlı araçlar vermek yerine, kısıtlanmış alternatifler ver:

- ❌ `fetch_url` — her URL'yi çekebilir, güvenlik riski
- ✅ `load_document` — sadece doküman URL'lerini doğrulayıp çeker

Daha güvenli, daha odaklı, daha az hata riski.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Araç aşırı yüklemesi | 18 araç = seçim güvenilirliği düşer. Optimal: agent başına 4-5 araç |
| `"auto"` | Varsayılan — model araç veya metin seçer |
| `"any"` | Mutlaka araç çağırır, hangisini seçer — garantili yapılandırılmış çıktı |
| `{"type":"tool","name":"X"}` | Belirli aracı zorlar — zorunlu ilk adımlar |
| Scoped cross-role tools | Basit işlemler için kapsamlı araç ver, karmaşık olanlar koordinatörden aksın |
| Kısıtlanmış alternatifler | fetch_url yerine load_document — güvenlik ve odak |

---

## Pratik Senaryo

> Bir sentez agent'ı nihai rapor yazarken sık sık iddiaları doğrulaması gerekiyor. Her doğrulama için koordinatöre kontrol veriyor, koordinatör web search subagent'ı çağırıyor, sonuç geri dönüyor. Bu süreç görev başına 2-3 ek tur-dönüş ekliyor ve toplam gecikmeyi %40 artırıyor. Doğrulamaların %85'i "X doğru mu?" şeklinde basit arama.
>
> **Gecikmeyi azaltmanın doğru yolu hangisidir?**
>
> **A)** Koordinatörü daha hızlı bir modelle çalıştır.
>
> **B)** Sentez agent'a kapsamlandırılmış bir `verify_fact` aracı ver — basit aramalar doğrudan agent'ta çözülsün, karmaşık doğrulamalar koordinatör üzerinden aksın.
>
> **C)** Doğrulama adımını kaldır — sentez agent'ın doğrulama olmadan rapor yazmasına izin ver.
>
> **D)** Sentez agent'a tam kapsamlı `fetch_url` aracı ver — her türlü doğrulamayı kendisi yapsın.

### Doğru Cevap: B

**Neden B doğru:** Vakaların %85'i basit arama — bunlar için koordinatöre gitmek gereksiz gecikme yaratıyor. Kapsamlandırılmış `verify_fact` aracı basit doğrulamaları agent'ta çözer, karmaşık olanlar hâlâ koordinatör üzerinden akar. Gecikme azalır, mimari bütünlük korunur.

**Neden A yanlış:** Daha hızlı model tur-dönüş yapısını değiştirmez. Her doğrulama hâlâ koordinatörden geçer — biraz daha hızlı ama yapısal gecikme devam eder.

**Neden C yanlış:** Fonksiyonalite kaybı. Doğrulama raporun kalitesini koruyan önemli bir adım — kaldırmak sorunu çözmez, yeni sorun yaratır.

**Neden D yanlış:** `fetch_url` çok geniş kapsamlı — her URL'yi çekebilir, güvenlik riski oluşturur. Kısıtlanmış araç (`verify_fact`) güvenli ve odaklı alternatif.
