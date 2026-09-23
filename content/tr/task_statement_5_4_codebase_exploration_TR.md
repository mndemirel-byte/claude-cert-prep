# Task Statement 5.4: Kod Tabanı Keşfi (Codebase Exploration)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir agent büyük bir kod tabanını keşfederken uzun süre çalışır. Dosyaları okur, sınıfları inceler, bağımlılıkları haritalar. Bu süreçte **bağlam bozulması** (context degradation) kaçınılmaz bir sorundur. Agent, oturumun başlarında keşfettiği spesifik bilgileri kaybetmeye ve "tipik kalıplar" gibi genel ifadeler kullanmaya başlar.

Bu task statement, bağlam bozulmasını nasıl tespit edeceğini ve dört farklı stratejiyle nasıl önleyeceğini öğretir.

---

## Bağlam Bozulması (Context Degradation)

### Belirtiler

Uzun oturumlarda agent'ın davranışında şu değişiklikleri gözlemlersn:

1. **Genelleştirme:** Agent oturumun başında "UserService.authenticate() metodu 3. satırda null kontrolü yapmıyor" gibi spesifik bulgular rapor ederken, ilerleyen turda "bu tip servislerde genellikle authentication kontrolleri yapılır" gibi belirsiz ifadeler kullanmaya başlar.

2. **Çelişkili referanslar:** Agent daha önce keşfettiği bir sınıfı yanlış hatırlar veya var olmayan bir metoda referans verir.

3. **Bağlam doluluğu:** Verbose keşif çıktıları (dosya listeleri, grep sonuçları, tam dosya içerikleri) bağlamı doldurur ve önceki bulguların üzerine yazar.

### Neden Oluşur?

Context window dolduğunda en eski bilgiler düşmeye başlar. Verbose araç sonuçları (tüm dosya içerikleri, uzun grep çıktıları) bağlamı hızla tüketir. Agent'ın ilk turda keşfettiği kritik bulgular, 10. turda bağlamda artık mevcut olmayabilir.

---

## Dört Azaltma Stratejisi

### 1. Karalama Dosyaları (Scratchpad Files)

Anahtar bulguları bir dosyaya yaz, sonraki sorular için bu dosyayı referans al.

```bash
# Agent oturum sırasında bulgularını dosyaya yazar
echo "## Keşif Bulguları
- UserService.authenticate(): null kontrolü eksik (line 47)
- PaymentGateway: retry mekanizması yok
- DatabasePool: max connection = 10, ölçeklenme sorunu
" > /tmp/findings.md
```

**Avantaj:** Bulgular context window'dan bağımsız olarak kalıcı. Agent bağlamı dolduğunda bile dosyayı okuyarak önceki bulguları geri alabilir.

**Ne zaman kullanılır:** Tek agent'ın uzun keşif oturumlarında. Basit ve etkili.

### 2. Subagent Delegasyonu

Spesifik araştırmalar için subagent'lar oluştur. Ana agent üst düzey koordinasyonu sürdürür.

```
Coordinator Agent:
├── Subagent 1: "Authentication modülünü analiz et"
├── Subagent 2: "Database katmanını analiz et"  
└── Subagent 3: "API endpoint'lerini analiz et"
```

**Avantaj:** Her subagent temiz bağlamla başlar — bağlam bozulması riski düşük. Ana agent sadece koordinasyon ve sonuç birleştirme yapar.

**Ne zaman kullanılır:** Büyük kod tabanlarında paralel keşif gerektiğinde. Domain 1'deki multi-agent orkestrasyonuyla doğrudan bağlantılı.

### 3. Özet Enjeksiyonu (Summary Injection)

Bir keşif aşamasının bulgularını özetle, sonraki aşamanın subagent'larına enjekte et.

```
Aşama 1: Keşif → Bulgular özetlenir
    ↓
Özet enjeksiyonu → Subagent prompt'larına dahil edilir
    ↓
Aşama 2: Derinlemesine analiz (temiz bağlam + önceki bulgu özeti)
```

**Avantaj:** Aşamalar arası bilgi transferini sağlar. Subagent'lar önceki aşamanın bulgularını bilir ama verbose keşif çıktısını taşımaz.

**Ne zaman kullanılır:** Çok aşamalı araştırmalarda — keşif → analiz → sentez akışlarında.

### 4. /compact Komutu

Bağlam verbose keşif çıktılarıyla dolduğunda, `/compact` komutuyla bağlam kullanımını azalt.

**Ne zaman kullanılır:** Bağlam doluluk uyarısı geldiğinde veya agent'ın yanıtlarında bağlam bozulması belirtileri göründüğünde.

**Sınav notu:** `/compact` tek başına yeterli değil — scratchpad, subagent ve summary injection ile birlikte kullanılmalı.

---

## Çökme Kurtarma (Crash Recovery)

### Problem

Çok agent'lı bir sistem çalışırken bir agent çöker. Agent'ın o ana kadar topladığı bulgular kaybolur. Sistem yeniden başlatıldığında her şey sıfırdan mı keşfedilecek?

### Çözüm: Manifest Dosyası

Her agent yapılandırılmış durumunu bilinen bir dosya konumuna (manifest) dışa aktarır:

```json
// /tmp/agent_state/research_agent_manifest.json
{
  "agent_id": "research_agent_01",
  "phase": "analysis",
  "completed_tasks": [
    "source_collection",
    "initial_categorization"
  ],
  "pending_tasks": [
    "deep_analysis_geothermal",
    "cross_reference_check"
  ],
  "key_findings": [
    {"claim": "Solar grew 45%", "source": "IEA", "confidence": 0.95},
    {"claim": "Wind hit $120B", "source": "IRENA", "confidence": 0.88}
  ],
  "last_checkpoint": "2024-03-15T14:30:00Z"
}
```

### Kurtarma Akışı

1. Koordinatör yeniden başlatılır
2. Manifest dosyalarını yükler
3. Her agent'ın durumunu agent prompt'larına enjekte eder
4. Agent'lar kaldıkları yerden devam eder — sıfırdan başlamaz

**Kural:** Her agent yapılandırılmış durumunu düzenli olarak manifest dosyasına yazar. Çökme durumunda koordinatör bu manifestleri yükleyerek kurtarma yapar.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Bağlam bozulması | Uzun oturumlarda agent spesifik bulgular yerine genel ifadeler kullanmaya başlar |
| Neden oluşur | Verbose araç çıktıları bağlamı doldurur, önceki bulgular düşer |
| Scratchpad files | Bulguları dosyaya yaz, bağlamdan bağımsız referans |
| Subagent delegasyonu | Spesifik araştırmaları subagent'lara ver, ana agent koordine eder |
| Summary injection | Bir aşamanın bulgularını özetle, sonraki aşamaya enjekte et |
| /compact | Bağlam kullanımını azalt — tek başına yeterli değil |
| Crash recovery | Her agent manifest dosyasına durum yazar, kurtarma sırasında koordinatör yükler |

---

## Pratik Senaryo 1

> Bir developer büyük bir kod tabanı üzerinde 2 saattir keşif yapan bir agent oturumu çalıştırıyor. Agent başlangıçta "PaymentService.process() metodunda race condition var, satır 142'de lock mekanizması eksik" gibi spesifik bulgular raporluyordu.
>
> Şimdi ise "bu tip servislerde genellikle thread safety konuları göz önünde bulundurulmalıdır" gibi belirsiz ifadeler kullanıyor.
>
> **En etkili çözüm hangisidir?**
>
> **A)** Daha büyük context window'a sahip model kullan.
>
> **B)** Agent'ın system prompt'una "her zaman spesifik ol" talimatı ekle.
>
> **C)** Scratchpad dosyasına anahtar bulguları yaz. Sonraki araştırma aşamaları için subagent'lar oluştur ve bulgular özetini subagent prompt'larına enjekte et.
>
> **D)** Oturumu sonlandır ve sıfırdan başla.

### Doğru Cevap: C

**Neden C doğru:** Klasik bağlam bozulması belirtileri — spesifik bulgulardan genel ifadelere geçiş. Üç strateji birlikte uygulanır: scratchpad ile bulguları kalıcı hale getir, subagent'larla temiz bağlamda araştırma yap, summary injection ile aşamalar arası bilgiyi aktar.

**Neden A yanlış:** Daha büyük model sorunu geciktirir ama çözmez. 4 saat sonra aynı bozulma olur. Yapısal çözüm gerekli.

**Neden B yanlış:** Prompt talimatı olasılıksal. Sorun modelin "tembel" olması değil, bağlamdaki spesifik bilgilerin fiziksel olarak düşmüş olması. Bilgi context'te yoksa "spesifik ol" talimatı işe yaramaz.

**Neden D yanlış:** Sıfırdan başlamak önceki 2 saatlik keşfi tamamen kaybettirir. Bulguları kurtarma mekanizması olmadan yeniden başlamak verimsiz.

---

## Pratik Senaryo 2

> Bir multi-agent araştırma sistemi 3 subagent ile çalışıyor. Sistem bir çökme yaşıyor. Yeniden başlatıldığında koordinatör subagent'ları sıfırdan başlatıyor — daha önce tamamlanmış 2 saatlik veri toplama aşaması tekrarlanıyor.
>
> **Bu sorunu önlemek için hangi mekanizma uygulanmalıydı?**
>
> **A)** Daha güvenilir donanım kullan — çökme olmasın.
>
> **B)** Her agent yapılandırılmış durumunu düzenli olarak manifest dosyasına yazsın. Kurtarma sırasında koordinatör manifest dosyalarını yükleyerek agent'ları kaldıkları yerden başlatsın.
>
> **C)** Tüm agent'ların tam konuşma geçmişini veritabanında sakla ve kurtarma sırasında olduğu gibi geri yükle.
>
> **D)** Agent sayısını azalt — tek agent çökmesi tüm sistemi etkilemesin.

### Doğru Cevap: B

**Neden B doğru:** Crash recovery mekanizması. Her agent manifest dosyasına yapılandırılmış durum yazar (tamamlanan görevler, bekleyen görevler, anahtar bulgular). Koordinatör kurtarma sırasında bu manifestleri yükler ve agent prompt'larına enjekte eder. Agent'lar sıfırdan değil, kaldıkları yerden devam eder.

**Neden A yanlış:** Donanım güvenilirliği çökmeleri azaltır ama ortadan kaldırmaz. Kurtarma mekanizması her sistemde olmalı.

**Neden C yanlış:** Tam konuşma geçmişi çok verbose — kurtarma sırasında tüm geçmişi geri yüklemek bağlam bütçesini hemen tüketir. Manifest dosyası yapılandırılmış ve kompakt — sadece gerekli durum bilgisini içerir.

**Neden D yanlış:** Agent sayısını azaltmak çökme kurtarmayı çözmez. Tek agent bile çökebilir — kurtarma mekanizması gerekli.
