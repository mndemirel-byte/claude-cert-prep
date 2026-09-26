# Task Statement 5.4: Kod Tabanı Keşfi (Codebase Exploration)

## Domain 5 — Bağlam Yönetimi ve Güvenilirlik (Sınavın %15'i)

---

## Temel Fikir

Bir agent büyük bir kod tabanını keşfederken uzun süre çalışır. Dosyaları okur, sınıfları inceler, bağımlılıkları haritalar. Bu süreçte **bağlam bozulması** (context degradation) kaçınılmaz bir sorundur. Agent, oturumun başlarında keşfettiği spesifik bilgileri kaybetmeye ve "tipik kalıplar" gibi genel ifadeler kullanmaya başlar.

Bu task statement, bağlam bozulmasını nasıl tespit edeceğini, dört stratejiyle nasıl önleyeceğini ve çökme sonrası nasıl kurtarılacağını öğretir.

Sınav senaryosu: **Code Generation with Claude Code** — kod tabanı keşfi Claude Code oturumunda (interaktif ya da Agent SDK ile) yapılır; `/compact`, subagent ve scratchpad Claude Code araçlarıdır.

---

## Bağlam Bozulması (Context Degradation)

### Belirtiler

Uzun oturumlarda agent'ın davranışında şu değişiklikleri gözlemlersin:

1. **Genelleştirme:** Agent oturumun başında "UserService.authenticate() metodu 47. satırda null kontrolü yapmıyor" gibi spesifik bulgular rapor ederken, ilerleyen turda "bu tip servislerde genellikle authentication kontrolleri yapılır" gibi belirsiz ifadeler kullanmaya başlar. Exam guide: "*referencing 'typical patterns' rather than specific classes discovered earlier*".

2. **Tutarsız cevaplar:** Aynı soruya 3. turda ve 30. turda farklı cevap verir. Guide: "*models start giving inconsistent answers*".

3. **Çelişkili referanslar:** Daha önce keşfettiği bir sınıfı yanlış hatırlar veya var olmayan bir metoda referans verir.

4. **Bağlam doluluğu:** Verbose keşif çıktıları (dosya listeleri, grep sonuçları, tam dosya içerikleri) bağlamı doldurur.

### Neden Oluşur? — Mekanizmayı doğru bil

Yaygın yanlış açıklama: "Context window dolunca en eski bilgiler düşer." **Böyle olmaz.** Messages API eski mesajları sessizce atmaz; pencere aşılırsa istek **hata döner** (prompt too long). Claude Code'da ise sınıra yaklaşınca **otomatik compact** (özetleme) çalışır. Bozulmanın gerçek nedenleri iki tanedir:

| Aşama | Ne olur | Adı |
|---|---|---|
| **Limit dolmadan önce** | Her token modelin sınırlı **dikkat bütçesinden** harcar; bağlam büyüdükçe model ortadaki/eski spesifik bulguyu bulamaz, genel kalıplara kayar | **Context rot** (Anthropic'in terimi) |
| **Compact sonrası** | Özetleme sırasında spesifik bulgular (satır numarası, sınıf adı) belirsiz ifadelere dönüşür — 5.1'in progressive summarization tuzağının kod tabanı versiyonu | Özet kaybı |

**Sınav sonucu:** "Daha büyük context window'a sahip model kullan" distractor'ının gerçek gerekçesi budur — exam guide Q12'nin diliyle: "*larger context windows don't solve attention quality issues*". Pencere büyüklüğü dikkat kalitesini artırmaz; sorunu geciktirmez bile, aynı bağlam kirliliğini daha geniş bir alanda yaşarsın.

---

## Dört Azaltma Stratejisi — Hangi Semptoma Hangisi?

| Semptom | Strateji | Neden çalışır |
|---|---|---|
| Spesifik bulgular kayboluyor | **1. Scratchpad dosyası** | Bulgu bağlamın dışında, diskte kalıcı |
| Verbose keşif çıktısı bağlamı dolduruyor | **2. Subagent delegasyonu** | Verbose çıktı subagent'ın bağlamında kalır, ebeveyne yalnızca özet döner |
| Aşamalar arası bilgi aktarımı gerekiyor | **3. Summary injection** | Subagent hiçbir şey miras almaz; ne bilmesi gerekiyorsa prompt'una yazılır |
| Bağlam doldu ve bulgular güvende | **4. `/compact <odak>`** | Anlatı özetlenir, odak talimatıyla kritik bulgular korunur |
| Çökme | **Manifest** (aşağıda) | Kurtarma yapılandırılmış duruma dayanır, transkripte değil |

Sınav dört şıkta dördünü verir; ayırt edici olan *semptom*dur.

### 1. Karalama Dosyaları (Scratchpad Files)

Anahtar bulguları bir dosyaya yaz, sonraki sorular için bu dosyayı referans al. Anthropic'in adı: **structured note-taking**.

```markdown
<!-- NOTES.md — oturumun çalışma belleği -->
## Keşif Bulguları
- UserService.authenticate(): null kontrolü eksik (src/auth/user_service.py:47)
- PaymentGateway: retry mekanizması yok (src/payments/gateway.py)
- DatabasePool: max connection = 10, ölçeklenme sorunu (config/db.yaml)

## Açık Sorular
- refund akışı PaymentGateway'i doğrudan mı çağırıyor, queue üzerinden mi?
```

**Avantaj:** Bulgular context window'dan bağımsız olarak kalıcı. Bağlam compact edilse bile agent dosyayı okuyarak önceki bulguları geri alabilir.

**Scratchpad ≠ CLAUDE.md — sınav distractor'ı.** CLAUDE.md her oturumda yüklenen *kalıcı talimat* dosyasıdır (Domain 3.1: kurallar, konvansiyonlar, komutlar). Oturuma özgü keşif bulguları CLAUDE.md'ye yazılırsa (a) her oturumun bağlamını şişirir, (b) sonraki, ilgisiz oturumları eski bulgularla kirletir. Scratchpad oturumun *çalışma belleği*, CLAUDE.md projenin *anayasası*dır.

> **Güncel not:** Aynı kalıbın API tarafı **memory tool** (beta) — agent'ın bağlam dışında kalıcı bir bellek dizinine yazıp okumasını sağlar. Anthropic'in çok ajanlı araştırma sisteminde lider agent planını bağlam sınırına yaklaşmadan belleğe kaydeder. Sınav cevabı scratchpad dosyasıdır; memory tool aynı fikrin araç biçimi.

### 2. Subagent Delegasyonu

Spesifik araştırmalar için subagent'lar oluştur. Ana agent üst düzey koordinasyonu sürdürür. Exam guide'ın örnekleri: "*find all test files*", "*trace refund flow dependencies*".

```
Ana agent (koordinasyon):
├── Subagent 1: "Tüm test dosyalarını bul ve kapsamı özetle"
├── Subagent 2: "Refund akışının bağımlılıklarını izle"
└── Subagent 3: "API endpoint'lerini listele ve auth gereksinimlerini çıkar"
```

**Neden çalışır (Agent SDK mekanizması):** Subagent **temiz bağlamla** başlar — ebeveynin konuşma geçmişini ve araç sonuçlarını **almaz**. Ara araç çağrıları ve okuduğu 40 dosya subagent'ın kendi bağlamında kalır; ebeveyne **yalnızca son mesaj** (özet) döner. Guide'ın ifadesi: "*isolating verbose exploration output while the main agent coordinates high-level understanding*".

**Maliyeti:** Subagent hiçbir şeyi miras almadığı için ne bilmesi gerekiyorsa prompt'una yazılır. Exam guide Egzersiz 4 adım 16: "*each subagent receives its research findings directly in its prompt rather than relying on automatic context inheritance*". Bu, üçüncü stratejinin gerekçesidir.

**Ne zaman kullanılır:** Büyük kod tabanlarında paralel keşif gerektiğinde. Claude Code'un yerleşik `Explore` subagent'ı ve Domain 1'deki multi-agent orkestrasyonuyla doğrudan bağlantılı.

### 3. Özet Enjeksiyonu (Summary Injection)

Bir keşif aşamasının bulgularını özetle, sonraki aşamanın subagent'larına **prompt'larında** enjekte et.

```
Aşama 1: Keşif → bulgular scratchpad'e + kısa özet
    ↓
Özet enjeksiyonu → Aşama 2 subagent'larının prompt'una
    ↓
Aşama 2: Derinlemesine analiz (temiz bağlam + önceki bulgu özeti)
```

**Avantaj:** Aşamalar arası bilgi transferini sağlar. Subagent'lar önceki aşamanın bulgularını bilir ama verbose keşif çıktısını taşımaz.

**Ne zaman kullanılır:** Çok aşamalı araştırmalarda — keşif → analiz → sentez akışlarında. Strateji 2 ile birlikte gelir: subagent miras almadığı için enjeksiyon şarttır.

### 4. `/compact` Komutu

Bağlam verbose keşif çıktılarıyla dolduğunda, `/compact` konuşma geçmişini özetler ve yerine özeti koyar. Exam guide'ın Skills maddesi: "*Using /compact to reduce context usage during extended exploration sessions when context fills with verbose discovery output*".

| Komut / mekanizma | Ne yapar | Ne zaman |
|---|---|---|
| `/compact` | Geçmişi özetler, devam eder | Aynı işte devam edeceksin, bağlam doldu |
| `/compact Odaklan: bulunan bug'lar ve dosya yolları` | **Odak talimatı** — özetleyiciye neyi koruyacağını söyler | Kritik bulguları özet kaybından korumak için (5.1 tuzağının çözümü) |
| CLAUDE.md'de `# Compact instructions` bölümü | Kalıcı odak talimatı | Her compact'te aynı şeyler korunacaksa |
| Otomatik compact | Sınıra yaklaşınca kendiliğinden çalışır | Müdahale gerekmez; ama odak talimatı yoksa özet kaybı yaşanır |
| `/clear` | Özetlemez, **sıfırlar** | İlgisiz bir işe geçerken; devam etmeyeceksen |
| `/context` | Neyin yer kapladığını gösterir | Compact'ten önce teşhis |

**Doğru cevap olduğu durum:** Bağlam verbose keşif çıktısıyla dolmuş **ve** bulgular zaten scratchpad'e alınmış. O zaman `/compact <odak>` en ucuz çözümdür. Bulgular scratchpad'de değilse önce oraya yaz, sonra compact et — aksi halde özet kaybı yaşarsın. Bu sıralama dokümanın yorumudur; exam guide `/compact`'i bağımsız bir strateji olarak sayar.

---

## Çökme Kurtarma (Crash Recovery)

### Problem

Çok agent'lı bir sistem çalışırken bir agent çöker. Agent'ın o ana kadar topladığı bulgular kaybolur. Sistem yeniden başlatıldığında her şey sıfırdan mı keşfedilecek?

### Çözüm: Manifest Dosyası

Her agent yapılandırılmış durumunu bilinen bir dosya konumuna (manifest) dışa aktarır. Exam guide: "*each agent exports state to a known location, and the coordinator loads a manifest on resume*".

```json
// state/research_agent_manifest.json
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
    {"claim": "Solar grew 45%", "source": "IEA", "source_location": "p.12", "publication_date": "2024-06-15"},
    {"claim": "Wind hit $120B", "source": "IRENA", "source_location": "exec summary", "publication_date": "2024-03-20"}
  ],
  "last_checkpoint": "2024-03-15T14:30:00Z"
}
```

### Kurtarma Akışı

1. Koordinatör yeniden başlatılır
2. Manifest dosyalarını yükler
3. Her agent'ın durumunu agent prompt'larına enjekte eder (summary injection ile aynı mekanizma)
4. Agent'lar kaldıkları yerden devam eder — sıfırdan başlamaz

**Kural:** Her agent yapılandırılmış durumunu düzenli olarak (checkpoint) manifest dosyasına yazar. Çökme durumunda koordinatör bu manifestleri yükleyerek kurtarma yapar. Manifest özetlenmez (5.1 tablosu: yapılandırılmış kayıt asla özetlenmez).

### Manifest vs oturum resume — "tam geçmişi geri yükle" neden yanlış?

> **Güncel not:** Agent SDK oturumu diske (`.jsonl`) yazar; `resume=<session_id>` veya `continue_conversation=True` ile *tam transkript* geri yüklenir, `fork_session` ile dallanır. Yani "tam konuşma geçmişini sakla ve geri yükle" bugün *mümkün*. Neden yine de sınav cevabı manifest? SDK dokümanının kendi tavsiyesi: "*Don't rely on session resume … capture the results you need as application state and pass them into a fresh session's prompt — often more robust.*" Üç neden: (1) transkript verbose'dur, geri yüklenince bağlam bütçesini hemen tüketir ve bozulma kaldığı yerden devam eder; (2) oturum dosyası makineye bağlıdır, farklı host/container'da `SessionStore` gerekir; (3) manifest *uygulama durumu*dur — kompakt, taşınabilir, denetlenebilir. Resume "kaldığın yerden devam", manifest "bildiğin yerden devam"dır.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Bağlam bozulması belirtileri | Spesifik → genel ("tipik kalıplar"), tutarsız cevaplar, çelişkili referanslar |
| Neden oluşur | Context rot (dikkat bütçesi) + compact sonrası özet kaybı — "eski mesajlar düşer" **değil** |
| Büyük pencere distractor'ı | Pencere boyutu dikkat kalitesini çözmez (Q12 gerekçesi) |
| Scratchpad | Bulguları dosyaya yaz (NOTES.md); CLAUDE.md **değil** — o kalıcı talimat dosyası |
| Subagent delegasyonu | Temiz bağlam, verbose çıktı içeride kalır, yalnızca son mesaj döner; hiçbir şey miras almaz |
| Summary injection | Aşama özetini sonraki subagent'ların prompt'una yaz — miras almadıkları için şart |
| `/compact` | Odak talimatıyla (`/compact <odak>`, CLAUDE.md compact instructions); `/clear` sıfırlar, özetlemez |
| Crash recovery | Her agent manifest yazar, koordinatör yükler ve prompt'a enjekte eder; transkript resume değil |

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
> **C)** Anahtar bulguları scratchpad dosyasına yaz; sonraki araştırma aşamaları için subagent'lar oluştur ve bulgular özetini subagent prompt'larına enjekte et.
>
> **D)** Bulguları CLAUDE.md'ye yaz; böylece her oturumda otomatik yüklenir.

### Doğru Cevap: C

**Neden C doğru:** Klasik bağlam bozulması belirtileri — spesifik bulgulardan genel ifadelere geçiş. Üç strateji birlikte uygulanır: scratchpad ile bulguları kalıcı hale getir, subagent'larla temiz bağlamda araştırma yap, summary injection ile aşamalar arası bilgiyi aktar.

**Neden A yanlış:** Pencere boyutu dikkat kalitesini artırmaz (context rot). Daha büyük pencerede aynı verbose çıktı aynı bozulmayı üretir.

**Neden B yanlış:** Prompt talimatı olasılıksal. Sorun modelin "tembel" olması değil, dikkatinin bağlam kirliliğiyle seyrelmesi ve compact sonrası spesifik bilgilerin özette kaybolması. "Spesifik ol" demek erişemediği bilgiyi geri getirmez.

**Neden D yanlış:** CLAUDE.md kalıcı talimat dosyasıdır; oturuma özgü bulgular oraya yazılırsa her oturumun bağlamını şişirir ve ilgisiz oturumları kirletir. Scratchpad oturum belleği, CLAUDE.md proje anayasasıdır.

---

## Pratik Senaryo 2

> Bir multi-agent araştırma sistemi 3 subagent ile çalışıyor. Sistem bir çökme yaşıyor. Yeniden başlatıldığında koordinatör subagent'ları sıfırdan başlatıyor — daha önce tamamlanmış 2 saatlik veri toplama aşaması tekrarlanıyor.
>
> **Bu sorunu önlemek için hangi mekanizma uygulanmalıydı?**
>
> **A)** Daha güvenilir donanım kullan — çökme olmasın.
>
> **B)** Her agent yapılandırılmış durumunu (tamamlanan/bekleyen görevler, anahtar bulgular) düzenli olarak manifest dosyasına yazsın. Kurtarma sırasında koordinatör manifest dosyalarını yükleyip agent prompt'larına enjekte ederek agent'ları kaldıkları yerden başlatsın.
>
> **C)** Agent SDK'nın oturum kalıcılığını kullan: her subagent'ın `session_id`'sini sakla, çökme sonrası `resume` ile tam konuşma geçmişini geri yükle.
>
> **D)** Agent sayısını azalt — tek agent çökmesi tüm sistemi etkilemesin.

### Doğru Cevap: B

**Neden B doğru:** Crash recovery mekanizması. Her agent manifest dosyasına yapılandırılmış durum yazar; koordinatör kurtarma sırasında bu manifestleri yükler ve agent prompt'larına enjekte eder. Agent'lar sıfırdan değil, kaldıkları yerden devam eder.

**Neden A yanlış:** Donanım güvenilirliği çökmeleri azaltır ama ortadan kaldırmaz. Kurtarma mekanizması her sistemde olmalı.

**Neden C yanlış:** Teknik olarak mümkün ama üç sorunu var: tam transkript verbose'dur ve geri yüklenince bağlam bütçesini hemen tüketir; oturum dosyası makineye bağlıdır; ve SDK dokümanının kendi tavsiyesi resume'a güvenmek yerine sonuçları uygulama durumu olarak yakalayıp yeni oturuma prompt'la vermektir — yani manifest.

**Neden D yanlış:** Agent sayısını azaltmak çökme kurtarmayı çözmez. Tek agent bile çökebilir — kurtarma mekanizması gerekli.

---

## Pratik Senaryo 3

> Claude Code ile 3 saattir bir monolitin modül sınırlarını çıkaran bir developer, bağlam doluluk uyarısı alıyor. Bulguların çoğu henüz yalnızca konuşma içinde; hiçbir dosyaya yazılmadı. Developer hemen `/compact` çalıştırıyor ve devam ediyor; 20 dakika sonra agent "ödeme modülünün hangi servislere bağımlı olduğunu daha önce konuşmuştuk ama detayını hatırlamıyorum" diyor.
>
> **Ne yanlış gitti ve doğru sıra ne olmalıydı?**
>
> **A)** `/compact` yerine `/clear` kullanılmalıydı; temiz bağlam daha iyi çalışır.
>
> **B)** Compact odak talimatı olmadan çalıştı ve bulgular hiçbir dosyada olmadığı için özette kayboldu. Doğru sıra: önce bulguları scratchpad'e yazdır, sonra `/compact Odaklan: modül sınırları ve bağımlılık listesi` ile özetle.
>
> **C)** Otomatik compact'i kapatıp daha büyük pencereli bir model seçilmeliydi.
>
> **D)** Bağımlılık listesi CLAUDE.md'ye yazılmalıydı; compact CLAUDE.md'yi özetlemez.

### Doğru Cevap: B

**Neden B doğru:** Compact'in özetleyicisi neyi koruyacağını bilmiyordu (odak talimatı yok) ve bulgular bağlam dışında hiçbir yerde değildi — 5.1'in progressive summarization tuzağı. Scratchpad + odaklı compact ikisini de çözer.

**Neden A yanlış:** `/clear` özetlemez, sıfırlar — bulguların tamamı giderdi. Aynı işte devam ederken `/clear` yanlış araçtır.

**Neden C yanlış:** Pencere boyutu özet kaybını ve context rot'u çözmez; otomatik compact'i kapatmak sınıra dayanınca hata almak demektir.

**Neden D yanlış:** CLAUDE.md compact'ten etkilenmez, doğru — ama oturuma özgü bağımlılık listesi oraya ait değildir; her sonraki oturum bu listeyle açılır. Doğru yer scratchpad.
