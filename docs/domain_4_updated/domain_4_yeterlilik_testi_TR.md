# Domain 4 Yeterlilik Testi: Prompt Engineering ve Yapılandırılmış Çıktı

## Genel Bilgiler

- **Domain Ağırlığı:** Sınavın %20'si
- **Soru Sayısı:** 10
- **Geçme Eşiği:** 8/10 (yüksek çıtayı hedefle)
- **Zorluk:** Sınav düzeyinde senaryo bazlı sorular
- **Kapsam:** Tüm 6 Task Statement (4.1 – 4.6)
- **Not:** Sorular ders notlarındaki pratik sorulardan farklı açılardan yazılmıştır; ders sorularını ezberlemek yetmez.

---

> Önce soruları yanıtla, ardından cevap anahtarına bak.

---

## Sorular

---

### Soru 1 — Task Statement 4.1 (Açık Kriterler)

Bir CI/CD kod inceleme agent'ı üç kategori raporluyor: güvenlik, mantık hataları, kod stili. Kod stili kategorisinin yanlış pozitif oranı %60. Bir takım lideri şöyle diyor: *"Yanlış pozitifler zararsız — geliştirici bir bakışta eler. Asıl risk kaçan hata; hiçbir kategoriyi kapatmayalım, hatta eşikleri gevşetelim."* Diğer bir mühendis kod stili kategorisini geçici olarak kapatmayı öneriyor.

**Hangi değerlendirme doğrudur?**

**A)** Takım lideri haklı; yanlış negatif her zaman yanlış pozitiften pahalıdır, tüm kategoriler açık kalmalı  
**B)** Mühendis haklı; yüksek yanlış pozitif kategorisi geliştirici güvenini tüketir ve bu, doğru çalışan güvenlik bulgularının da yok sayılmasına yol açar — kategori kapatılıp kriterleri netleştirilerek ölçüldükten sonra geri açılmalı  
**C)** İkisi de yanlış; doğru çözüm tüm kategoriler için "emin değilsen raporlama" talimatı eklemek  
**D)** İkisi de yanlış; kod stili kategorisi daha büyük bir modele taşınmalı  

---

### Soru 2 — Task Statement 4.1 (Açık Kriterler)

Bir agent'a şu ciddiyet tanımı verildi: *"Kritik: Sistemi tehdit eden sorunlar. Minör: Küçük sorunlar."*

Aşağıdakilerden hangisi bu tanımdan kaynaklanan temel sorundur?

**A)** "Kritik" ve "minör" terimleri teknik jargon değil, agent bunları anlayamaz  
**B)** Tanımlar nesir bazlı; "sistemi tehdit" öznel bir ifade olduğu için agent her çalıştırmada farklı kalibre eder  
**C)** İki seviye yeterli değil; en az beş seviye gerekir  
**D)** Bu tanımlar yalnızca güvenlik domaininde kullanılabilir, genel kod incelemesi için uygun değil  

---

### Soru 3 — Task Statement 4.2 / 4.3 / 4.4 (null teşhisi)

Bir fatura çıkarım pipeline'ında `invoice_date` alanı bazı belgelerde null dönüyor. İnceleme: bu belgelerde tarih *var*, ama "15 Ocak 2024" veya "Jan 15, '24" gibi serbest biçimlerde; tablo formatlı faturalarda (tarih ayrı hücrede) alan hep doğru çıkıyor.

**En etkili çözüm nedir?**

**A)** `invoice_date` alanını nullable yap — bilgi güvenilir biçimde çıkarılamıyor  
**B)** Hata mesajlı retry döngüsü ekle: "invoice_date null, belgede tarih var, tekrar dene"  
**C)** Serbest biçimli tarih içeren belgelerden başarılı çıkarım gösteren 2-4 few-shot örneği ekle (`<example>` etiketleriyle, gerekçeli)  
**D)** Bu belgeleri doğrudan insan incelemesine yönlendir  

---

### Soru 4 — Task Statement 4.2 (Few-Shot Prompting)

Bir kod inceleme agent'ı belirli durumları tutarsız sınıflandırıyor: "Bu yorum kodun davranışını yanlış mı anlatıyor, yoksa eski bir not mu?" sorusuna farklı çalıştırmalarda farklı yanıtlar veriyor. Talimatları üç kez yeniden yazdın — sorun devam ediyor.

**Bu durumda ne yapmalısın?**

**A)** Talimatları daha ayrıntılı hale getir; her olası senaryoyu ayrıca açıkla  
**B)** Belirsiz 2-4 durum için few-shot örnekleri ekle; her örnekte neden bir karar verildiğinin gerekçesini göster  
**C)** "Emin değilsen işaretleme" talimatı ekle (confidence-based filtering)  
**D)** Daha büyük bir model kullan — tutarsızlık kapasite sorunudur  

---

### Soru 5 — Task Statement 4.3 / 4.4 (Anlamsal Doğrulama)

Bir fatura çıkarım sistemi `strict: true` tool_use kullanıyor. Tüm JSON çıktıları şemaya uygun. Ancak downstream sistemde bazı faturalarda satır kalemleri toplamı belirtilen toplama eşit değil.

**Bu sorunu çözmek için en uygun tasarım nedir?**

**A)** Tool_use kaldır, prompt tabanlı JSON'a geç — strict mod aritmetiği bozuyor  
**B)** Şemaya `calculated_total` ekle; backend kendi toplamıyla çapraz kontrol etsin; uyuşmazlıkta hata mesajlı retry gönder; retry sonrası hâlâ uyuşmuyorsa belge muhtemelen kendi içinde çelişkili → `conflict_detected: true` ile insan incelemesine yönlendir  
**C)** Daha büyük model kullan — küçük model aritmetik hata yapıyor  
**D)** Tüm alanları "required" yap — eksik değer kalmasın  

---

### Soru 6 — Task Statement 4.3 (tool_choice)

Bir belge pipeline'ı iki aşamalı: önce `extract_metadata` aracı belgenin türünü ve dilini çıkarmalı, sonra türe göre `enrich_invoice` / `enrich_contract` araçlarından biri çalışmalı. İlk çağrıda modelin doğrudan bir enrichment aracına atlamaması gerekiyor.

**İlk çağrı için doğru `tool_choice` nedir?**

**A)** `{"type": "auto"}` — model sırayı kendisi anlar  
**B)** `{"type": "any"}` — model mutlaka bir araç çağırır  
**C)** `{"type": "tool", "name": "extract_metadata"}` — bu araç zorlanır; sonraki çağrıda `auto` veya `any`  
**D)** `{"type": "none"}` — ilk çağrıda metin olarak tür belirlensin  

---

### Soru 7 — Task Statement 4.4 (Retry Etkinlik Sınırı)

Bir sözleşme çıkarım sistemi `penalty_rate` alanı için null döndürüyor. İki retry gönderildi ("penalty_rate belgede olmalı, tekrar bak") — hâlâ null. Belgede şu satır var: *"Cezai şart oranı için Ek-B'ye bakınız."* Ek-B pipeline'a verilmemiş.

**Doğru teşhis ve çözüm nedir?**

**A)** Bilgi belgede yok → `penalty_rate` alanını nullable yap, null kabul et  
**B)** Bilgi harici bir belgede → retry işe yaramaz; Ek-B'yi bağlama ekleyip çıkarımı yeniden çalıştır  
**C)** Retry sayısını 5'e çıkar — model sonunda bulur  
**D)** `penalty_rate` için few-shot örneği ekle — model alanı tanımıyor  

---

### Soru 8 — Task Statement 4.5 (SLA Hesabı)

Bir şirket müşterilerine "yüklenen belge en geç 30 saat içinde işlenir" taahhüdü veriyor. Belgeler gün boyunca düzensiz geliyor. Maliyet için Message Batches API kullanılacak (işlem üst sınırı 24 saat, gecikme SLA'sı yok).

**Doğru planlama hangisidir?**

**A)** Batch kullanılamaz — Batch API'nin SLA'sı olmadığı için SLA'lı hiçbir işte kullanılmaz  
**B)** Günde bir batch (gece 02:00) — çoğu batch zaten 1 saatte biter  
**C)** En geç 6 saatte bir batch gönder (4 saat daha güvenli): en kötü gecikme = bekleme + 24 saat ≤ 30 saat  
**D)** Belgeleri geldikçe tek tek batch olarak gönder — her belge en geç 24 saatte biter  

---

### Soru 9 — Task Statement 4.6 (Doğrulama Mimarisi)

Bir extraction pipeline'ında model ince hataları (yanlış alana yerleşen değerler, gözden kaçan satır kalemleri) kaçırıyor. Üç öneri var: (1) çıkarım prompt'una "çıktını dikkatlice gözden geçir, hataları düzelt" talimatı ekle; (2) extended thinking'i açıp bütçeyi artır; (3) çıkarımı, üreticinin akıl yürütmesini görmeyen ayrı bir Claude çağrısıyla doğrulat.

**Hangisi en etkilidir?**

**A)** (1) — en ucuz; model kendi çıktısını en iyi bilir  
**B)** (2) — daha fazla düşünme bütçesi daha fazla doğrulama sağlar  
**C)** (3) — bağımsız instance üretim bağlamını taşımaz; self-review talimatı ve thinking aynı bağlamın içinde kalır  
**D)** (1) + (2) birlikte, (3) kadar etkili ve daha ucuzdur  

---

### Soru 10 — Bütünleşik Senaryo (Tüm Domain)

Bir ekip fatura işleme pipeline'ı geliştiriyor. Gereksinimler:
1. Farklı formatlarda faturalar geliyor (tablo, metin, iç içe liste)
2. JSON her zaman şemaya uygun olmalı
3. Anlamsal doğrulama (toplam uyuşmazlığı) gerekiyor
4. Haftada 2.000 fatura; maliyet kritik; müşteriye 36 saatlik işleme taahhüdü var
5. Bazı faturalarda `payment_terms` bilgisi yok
6. Yüksek güvenli alanlar otomatik, düşük güvenli alanlar insan incelemesine

**Bu sistemi doğru tanımlayan seçenek hangisidir?**

**A)** Senkron API (SLA olduğu için batch olmaz); tüm alanlar required; `tool_choice: auto`; doğrulama yok  
**B)** Format çeşitliliği için `<example>` etiketli few-shot; `strict: true` tool_use (payment_terms nullable); `calculated_total` + backend doğrulama + hata mesajlı retry; Batch API, en geç 12 saatte bir gönderim (12 + 24 ≤ 36); alan bazlı enum güven ile yönlendirme, belge tipi × alan doğruluk tablosuyla kalibre  
**C)** Her fatura için 50 instance'lı çok geçişli mimari; tüm alanlar required; retry yok; senkron API  
**D)** Prompt tabanlı JSON; tüm doğrulama insana; Batch API günde bir gönderim; few-shot yok  

---

## Cevap Anahtarı ve Açıklamalar

---

### Soru 1 → **B**

**Açıklama:**

Exam guide'ın 4.1 Knowledge maddesi: yüksek yanlış pozitif kategorileri, *doğru* kategorilere olan güveni de tüketir ("undermine confidence in accurate categories"). Güven bütündür; kod stili kategorisinin gürültüsü güvenlik bulgularının da yok sayılmasına yol açar — bu da dolaylı olarak kaçan hata demektir. Çözüm izolasyon + kriter netleştirme + etiketli sette ölçüm + geri açma.

- **(A) Yanlış:** "Yanlış pozitif zararsız" tezi 4.1'in çürüttüğü tezdir; eşik gevşetmek gürültüyü artırır.
- **(C) Yanlış:** "Emin değilsen raporlama" = confidence-based filtering; hem yanlış pozitifi hem gerçek bulguyu kontrolsüz biçimde eler.
- **(D) Yanlış:** Sorun kriter, kapasite değil.

**Kapsanan kavram:** Task 4.1 — Yanlış pozitif / güven ilişkisi ve izolasyon

---

### Soru 2 → **B**

**Açıklama:**

"Sistemi tehdit eden sorunlar" ifadesi yoruma açık. Claude her çalıştırmada bu eşiği farklı kalibre edebilir — aynı kod bazen kritik, bazen minör görünür. Çözüm: gerçek kod örnekleriyle (`<example>` etiketli) ciddiyet tanımlamak.

- **(A) Yanlış:** Terimler anlaşılıyor, sorun öznel olmalarıdır.
- **(C) Yanlış:** Seviye sayısı sorun değil; somutluk sorunu.
- **(D) Yanlış:** Bu tanımlar her domainde aynı belirsizlik sorununu taşır.

**Kapsanan kavram:** Task 4.1 — Nesir tanım vs. kod örnekli kalibrasyon

---

### Soru 3 → **C**

**Açıklama:**

"null üçlüsü"nün birinci durumu: bilgi belgede **var**, model farklı biçimi tanımıyor. Bu 4.2'nin işidir — few-shot, "bu biçimde tarih şurada" haritasını öğretir. Tablo formatında çalışıp serbest metinde çalışmaması, sorunun *format çeşitliliği* olduğunu doğrular (belge tipi × alan doğruluk tablosunun tipik bulgusu).

- **(A) Yanlış:** Nullable, bilgi *yokken* uydurmayı önler; bilgi varken null kabul etmek veri kaybıdır (4.3'ün alanı değil).
- **(B) Yanlış:** Retry format *uyuşmazlığını* düzeltir (yanlış biçimde çıkarılmış tarih); ama modelin hiç tanımadığı bir biçimi retry her seferinde aynı şekilde kaçırır — öğretmek gerekir.
- **(D) Yanlış:** Otomatik çözülebilir bir sorunu insana devretmek ölçeklenmez.

**Kapsanan kavram:** Task 4.2 — null üçlüsü (few-shot vs nullable vs retry)

---

### Soru 4 → **B**

**Açıklama:**

Talimat yeniden yazma defalarca denendi — işe yaramadı. Bu, talimat miktarının sorun olmadığını gösterir. Belirsiz durumlarda tutarsızlık için çözüm: o belirsiz durumların örneklerini + gerekçelerini göstermek (exam guide: "*show reasoning for why one action was chosen over plausible alternatives*").

- **(A) Yanlış:** Talimat uzatma zaten denendi ve başarısız oldu.
- **(C) Yanlış:** Confidence-based filtering; asıl sorun kararın *ne zaman* verileceğidir, güven değil.
- **(D) Yanlış:** Sorun model kapasitesi değil, belirsiz durumların nasıl ele alınacağı.

**Kapsanan kavram:** Task 4.2 — Belirsiz durumlarda few-shot + gerekçe

---

### Soru 5 → **B**

**Açıklama:**

Strict tool_use şema/sözdizimi hatalarını sıfırlar — ama toplam uyuşmazlığı **anlamsal** hatadır (exam guide: "*strict JSON schemas … do not prevent semantic errors, e.g., line items that don't sum to total*"). Çözüm katmanlı: `calculated_total` + backend'in bağımsız hesabı → hata mesajlı retry (bir satır yanlış okunduysa düzelir) → hâlâ uyuşmuyorsa belge kendi içinde çelişkilidir, retry bunu çözemez → `conflict_detected` + insan. Şık, 4.4'ün "retry etkin / etkin değil" ayrımını tek akışta kurar.

- **(A) Yanlış:** Prompt tabanlı JSON sözdizimi güvencesini kaybettirir; strict aritmetiği etkilemez.
- **(C) Yanlış:** Model değiştirmek doğrulama katmanının yerini tutmaz; çelişkili belgeyi hiçbir model "doğru" toplayamaz.
- **(D) Yanlış:** Required alan uydurma riskini artırır, toplamı doğrulamaz.

**Kapsanan kavram:** Task 4.3 + 4.4 — Strict'in sınırı, anlamsal doğrulama, retry → conflict akışı

---

### Soru 6 → **C**

**Açıklama:**

Exam guide'ın Skills maddesi birebir: "*Forcing a specific tool with `tool_choice: {"type": "tool", "name": "extract_metadata"}` to ensure a particular extraction runs **before enrichment steps**.*" Sıralı akışta `disable_parallel_tool_use: true` de eklenir.

- **(A) Yanlış:** `auto` araç çağrısını bile garanti etmez; sıra prompt'a bırakılır (olasılıksal).
- **(B) Yanlış:** `any` bir araç çağrısını garanti eder ama *hangisini* değil — model doğrudan `enrich_invoice`'a atlayabilir.
- **(D) Yanlış:** `none` bu turda hiç araç çağırtmaz; metin çıktısı yapılandırılmamıştır ve ekstra çağrı gerekir.

**Kapsanan kavram:** Task 4.3 — tool_choice modları, spesifik araç zorlama

---

### Soru 7 → **B**

**Açıklama:**

Exam guide'ın retry-etkisiz örneği: "*information exists only in an external document not provided*". Belge açıkça Ek-B'ye atıf yapıyor — bilgi *ulaşılabilir* ama bağlamda değil. Retry aynı belgeye bakar, yine null. Çözüm nullable değil, **eksik belgeyi eklemek**; sonra çıkarım (gerekirse retry) işe yarar.

- **(A) Yanlış:** Nullable, bilgi *hiçbir yerde* yokken doğrudur; burada atıf var — null kabul etmek veri kaybıdır.
- **(C) Yanlış:** Retry sayısı, modelin elinde olmayan bilgiyi üretmez.
- **(D) Yanlış:** Few-shot "nasıl çıkarılır"ı öğretir; bilgi bağlamda olmadığı sürece örnek işe yaramaz.

**Kapsanan kavram:** Task 4.4 — Retry etkinlik sınırı (harici belge)

---

### Soru 8 → **C**

**Açıklama:**

Exam guide Skills: "*4-hour windows to guarantee 30-hour SLA with 24-hour batch processing*". Formül: en kötü gecikme = bir sonraki gönderimi bekleme (P) + 24 saat işlem ≤ SLA → P ≤ 30 − 24 = **6 saat**. Guide'ın 4 saatlik penceresi 2 saat pay bırakır.

- **(A) Yanlış:** "Gecikme SLA'sı yok" ≠ "SLA verilemez"; 24 saatlik üst sınır hesap yapmaya yeter. SLA ≤ 24 saat olsaydı A doğru olurdu.
- **(B) Yanlış:** Günde bir gönderimde 02:05'te gelen belge 24 saat bekler + 24 saat işlem = 48 > 30. "Çoğu 1 saatte biter" ortalamadır, garanti değil.
- **(D) Yanlış:** Belge başına batch, batch'in amacını (toplu gönderim) yok eder ve rate limit / yönetim yükü yaratır; ayrıca "24 saatte biter" yine üst sınırdır — teknik olarak SLA'yı karşılar ama sorunun sorduğu *planlama* değildir.

**Kapsanan kavram:** Task 4.5 — SLA'ya göre gönderim sıklığı hesabı

---

### Soru 9 → **C**

**Açıklama:**

Exam guide 4.6 Knowledge: "*Independent review instances (without prior reasoning context) are more effective at catching subtle issues than **self-review instructions or extended thinking**.*" Doğrulama sorunu aynı oturumda *daha fazla şey yaparak* çözülmez; *bağlamı değiştirerek* çözülür.

- **(A) Yanlış:** "Kendi çıktısını en iyi bilir" tam olarak sorunun kaynağı — üretim varsayımlarını miras alır.
- **(B) Yanlış:** Thinking daha uzun düşündürür, *başka bir açıdan* düşündürmez; üretim bağlamının içinde çalışır.
- **(D) Yanlış:** İki yetersiz yöntemin toplamı bağlam sorununu çözmez.

**Kapsanan kavram:** Task 4.6 — Self-review sınırı; talimat / thinking / bağımsız instance üçlüsü

---

### Soru 10 → **B**

**Açıklama:**

Her gereksinim bir teknikle eşleşiyor:

| Gereksinim | Teknik |
|------------|--------|
| Format çeşitliliği | `<example>` etiketli few-shot (Task 4.2) |
| Şemaya uygun JSON | `strict: true` tool_use (Task 4.3) |
| Anlamsal doğrulama | `calculated_total` + backend hesabı + hata mesajlı retry (Task 4.4) |
| Maliyet + 36 saat taahhüt | Batch API; P ≤ 36 − 24 = 12 saat → en geç 12 saatte bir gönderim (Task 4.5) |
| payment_terms bazen yok | Nullable alan (Task 4.3) |
| Güven tabanlı yönlendirme | Alan bazlı enum güven; belge tipi × alan tablosuyla kalibrasyon (Task 4.6) |

- **(A) Yanlış:** "SLA olduğu için batch olmaz" — 36 > 24, batch mümkün; required alanlar uydurma yaratır; `auto` garanti vermez; doğrulama yok.
- **(C) Yanlış:** Geçiş sayısı dosya sayısına bağlıdır, "fatura başına 50 instance" maliyet sezgisinin yokluğudur; required-all uydurma riski; retry yok.
- **(D) Yanlış:** Prompt tabanlı JSON güvenilmez; günde bir gönderim 24 + 24 = 48 > 36 (SLA ihlali); tüm doğrulamayı insana bırakmak ölçeklenemez.

**Kapsanan kavram:** Task 4.1–4.6 bütünleşik uygulama

---

## Sonuç

| Puan | Değerlendirme |
|------|---------------|
| 10/10 | Mükemmel — Sınava hazırsın |
| 8-9/10 | İyi — Eksik Task Statement'ları tekrarla |
| 6-7/10 | Gelişiyor — Hatalı soruların kapsadığı Task'ları yeniden çalış |
| 5 ve altı | Temel kavramları yeniden oku, ardından testi tekrar dene |

---

## Hangi Soruyu Hangi Task Kapsıyor?

| Soru | Task Statement |
|------|----------------|
| 1 | 4.1 — Açık Kriterler (Yanlış pozitif / güven, izolasyon) |
| 2 | 4.1 — Açık Kriterler (Ciddiyet kalibrasyonu) |
| 3 | 4.2 (+4.3, 4.4) — null teşhisi: few-shot vs nullable vs retry |
| 4 | 4.2 — Few-Shot (Belirsiz karar tutarsızlığı) |
| 5 | 4.3 + 4.4 — Strict'in sınırı, anlamsal doğrulama, retry → conflict |
| 6 | 4.3 — tool_choice (spesifik araç zorlama) |
| 7 | 4.4 — Retry etkinlik sınırı (harici belge) |
| 8 | 4.5 — SLA'ya göre gönderim sıklığı hesabı |
| 9 | 4.6 — Self-review vs thinking vs bağımsız instance |
| 10 | 4.1–4.6 — Bütünleşik senaryo |

---

## Ek Alıştırma — Hızlı Ayırt Etme (cevaplar altta)

Ders notlarında işlenen ama ana teste sığmayan sınav noktaları. Her biri için tek kelimelik/tek satırlık cevap ver:

1. 500 belgelik batch'te 12 istek `expired`, 8 istek `errored` ("too large"). Hangisi değiştirilmeden, hangisi chunk'lanarak gönderilir?
2. Manuel extended thinking açık; `tool_choice: {"type": "any"}` gönderdin. Ne olur?
3. 14 dosyalık PR incelemesinde tutarsız derinlik ve çelişkili yorumlar var. "Daha büyük bağlam penceresi" ve "3 kez çalıştır, çoğunluk oyu" neden çözmez?
4. Dört few-shot örneğinin dördü de `TODO` yorumu içeriyor; agent `TODO`'suz hataları atlamaya başladı. Kural?
5. Pipeline script'i `claude "Analyze PR"` ile asılı kalıyor; `--batch` bayrağı çözer mi?
6. Extraction'da güven raporlaması bulgu başına mı, alan başına mı yapılır; kalibrasyon hangi tabloyla?

**Cevaplar:** (1) `expired` → aynen; `errored` too large → chunk'la. (2) Hata — manuel thinking ile `any`/`tool` desteklenmez; `auto` (+ `strict`) kullan. (3) Sorun sığma değil *dikkat seyreltmesi*; büyük pencere seyreltmeyi artırabilir, çoğunluk oyu üç kez aynı seyreltmeyi yaşar ve tutarsızlığı maskeler → geçişi böl. (4) Örnekler *çeşitli* olmalı; yüzeysel ortak özellik istenmeyen kalıp öğretir. (5) Hayır — `--batch` diye bir bayrak yok; cevap `-p`; Message Batches API ayrı bir Messages API özelliğidir. (6) Alan başına (enum güven + `confidence_reason`); belge tipi × alan doğruluk matrisiyle kalibre edilir.
