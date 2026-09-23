# Domain 4 Yeterlilik Testi: Prompt Engineering ve Yapılandırılmış Çıktı

## Genel Bilgiler

- **Domain Ağırlığı:** Sınavın %20'si
- **Soru Sayısı:** 10
- **Geçme Eşiği:** 8/10 (yüksek çıtayı hedefle)
- **Zorluk:** Sınav düzeyinde senaryo bazlı sorular
- **Kapsam:** Tüm 6 Task Statement (4.1 – 4.6)

---

> Önce soruları yanıtla, ardından cevap anahtarına bak.

---

## Sorular

---

### Soru 1 — Task Statement 4.1 (Açık Kriterler)

Bir CI/CD pipeline'ında çalışan kod inceleme agent'ı üç kategori raporluyor: güvenlik açıkları, mantık hataları ve kod stili sorunları. Geliştiriciler "kod stili" kategorisinin %60 yanlış pozitif oranına sahip olduğunu fark etti. Bu durum güvenlik bulgularına olan güveni de sarsmaya başladı.

**En iyi kısa vadeli eylem nedir?**

**A)** Güvenlik ve mantık kategorilerinin güven eşiklerini %95'e çek, tüm kategorileri daha muhafazakâr yap  
**B)** Üç kategori için de daha büyük bir model kullan  
**C)** Kod stili kategorisini geçici olarak devre dışı bırak; güvenlik ve mantık kategorileri çalışmaya devam etsin, kod stili promptu iyileştir  
**D)** Agent'ı tamamen yeniden yapılandır; kategorileri birleştir

---

### Soru 2 — Task Statement 4.1 (Açık Kriterler)

Bir agent'a şu ciddiyet tanımı verildi: *"Kritik: Sistemi tehdit eden sorunlar. Minör: Küçük sorunlar."*

Aşağıdakilerden hangisi bu tanımdan kaynaklanan temel sorundur?

**A)** "Kritik" ve "minör" terimleri teknik jargon değil, agent bunları anlayamaz  
**B)** Tanımlar nesir bazlı; "sistemi tehdit" öznel bir ifade olduğu için agent her çalıştırmada farklı kalibre eder  
**C)** İki seviye yeterli değil; en az beş seviye gerekir  
**D)** Bu tanımlar yalnızca güvenlik domaininde kullanılabilir, genel kod incelemesi için uygun değil  

---

### Soru 3 — Task Statement 4.2 (Few-Shot Prompting)

Bir extraction pipeline farklı belge formatlarını işliyor: bazı faturalar tablo formatında, bazıları düz metin, bazıları iç içe liste. Model bazen bilgi mevcut olmasına rağmen alanları "null" döndürüyor.

**En etkili çözüm nedir?**

**A)** JSON şemasında tüm alanları "required" yap — null dönmeyi engeller  
**B)** Modele "Eğer bilgi varsa mutlaka çıkar, hiçbir zaman null döndürme" talimatı ver  
**C)** Her format türünden başarılı çıkarım gösteren 2-4 few-shot örneği ekle; biri "bilgi yoksa null" senaryosu içermeli  
**D)** Her belge formatı için ayrı model deploy et  

---

### Soru 4 — Task Statement 4.2 (Few-Shot Prompting)

Bir kod inceleme agent'ı belirli durumları tutarsız sınıflandırıyor: "Bu yorum kodun davranışını yanlış mı anlatıyor, yoksa eski bir not mu?" sorusuna farklı çalıştırmalarda farklı yanıtlar veriyor. Talimatları üç kez yeniden yazdın — sorun devam ediyor.

**Bu durumda ne yapmalısın?**

**A)** Talimatları daha ayrıntılı hale getir; her olası senaryoyu ayrıca açıkla  
**B)** Belirsiz 2-4 durum için few-shot örnekleri ekle; her örnekte neden bir karar verildiğinin gerekçesini göster  
**C)** Güven eşiği parametre olarak ekle: "Emin değilsen işaretleme"  
**D)** Daha büyük bir model kullan — tutarsızlık kapasite sorunudur  

---

### Soru 5 — Task Statement 4.3 (Tool_use ile Yapılandırılmış Çıktı)

Bir fatura çıkarım sistemi tool_use kullanıyor. Tüm JSON çıktıları sözdizimsel olarak geçerli. Ancak downstream sistemde fatura toplamlarında uyuşmazlık bildiriliyor: satır kalemleri toplamı belirtilen toplama eşit değil.

**Bu sorunu çözmek için en uygun yaklaşım nedir?**

**A)** Tool_use kaldır, prompt tabanlı JSON'a geç  
**B)** Şemaya `calculated_total` alanı ekle; validation adımında `stated_total == calculated_total` kontrol et; uyuşmazlık varsa retry gönder  
**C)** Daha büyük model kullan — küçük model aritmetik hata yapıyor  
**D)** Tüm alanları "required" yap — eksik değer kalmasın  

---

### Soru 6 — Task Statement 4.3 (Tool_use ile Yapılandırılmış Çıktı)

Bir pipeline bilinmeyen formatlarda belgeler alıyor (fatura, sözleşme, makbuz veya diğer). Her format için farklı extraction araçları tanımlandı. **Garantili yapılandırılmış çıktı** isteniyor.

**Hangi `tool_choice` ayarı kullanılmalı?**

**A)** `"auto"` — model en uygun aracı seçer  
**B)** `{"type": "tool", "name": "extract_invoice"}` — her belge fatura aracıyla işlenir  
**C)** `"any"` — model mutlaka bir araç çağırır, hangisini seçeceğine kendisi karar verir  
**D)** `tool_choice` belirtme — varsayılan davranış garantili çıktı sağlar  

---

### Soru 7 — Task Statement 4.4 (Validation-Retry Döngüleri)

Bir extraction sistemi `payment_terms` alanı için sürekli null döndürüyor. Retry mesajı gönderildi: *"payment_terms null olamaz, zorunlu alan."* İkinci denemede de null döndü.

**Doğru teşhis ve çözüm nedir?**

**A)** Retry sayısını artır — model zamanla doğru değeri bulur  
**B)** Daha güçlü model kullan — küçük model alanı görmüyor  
**C)** Bilgi belgede muhtemelen yok; retry etkisiz. `payment_terms`'i nullable/optional yap  
**D)** Few-shot örneği ekle: "payment_terms nasıl çıkarılır" göster  

---

### Soru 8 — Task Statement 4.5 (Toplu İşleme)

Bir mühendislik takımı iki görev çalıştırıyor: (a) her gece arşivlenen 200 belgenin haftalık analizi, (b) pull request açıldığında çalışan güvenlik taraması. Maliyet azaltmak için ikisini de Batch API'ye taşımayı planlıyorlar.

**Bu plan doğru mu? Açıkla.**

**A)** Evet, her iki görev de Batch için uygun  
**B)** Evet ama yalnızca haftalık analiz batch kullanmalı; güvenlik taraması senkron kalmalı  
**C)** Hayır, Batch API yalnızca 10'dan az belge için kullanılabilir  
**D)** Evet ama batch işlemleri yalnızca gece 00:00-06:00 arasında çalışır  

---

### Soru 9 — Task Statement 4.6 (Çok Örnekli İnceleme)

Bir kod inceleme sistemi her dosyayı ayrı instance'da analiz ediyor (50 dosya = 50 çağrı). Dosya başına bulgular toplanıyor. Ancak bazı cross-file sorunları gözden kaçıyor: örneğin dosya A'da temizlenen verinin dosya B'de güvensiz kullanılması.

**Bu sorunu çözmek için ne yapmalısın?**

**A)** Tüm 50 dosyayı tek bir instance'a ver — cross-file bağlamı görür  
**B)** Dosya başına analizlere ek olarak, tüm dosya bulgularını gösteren bağımsız bir çapraz dosya entegrasyon geçişi çalıştır  
**C)** Dosyaları 5'erli gruplara böl, her grup için tek instance kullan  
**D)** Cross-file sorunları insan incelemesine bırak, otomasyon sadece dosya başına çalışsın  

---

### Soru 10 — Bütünleşik Senaryo (Tüm Domain)

Bir ekip fatura işleme pipeline'ı geliştiriyor. Gereksinimler:
1. Farklı formatlarda faturalar geliyor (tablo, metin, iç içe liste)
2. JSON her zaman sözdizimsel olarak geçerli olmalı
3. Anlamsal doğrulama (toplam uyuşmazlığı) gerekiyor
4. Haftada 2.000 fatura işleniyor, maliyet kritik
5. Bazı faturalarda `payment_terms` bilgisi yok
6. Yüksek güvenli bulgular otomatik, düşük güvenli bulgular insan incelemesine

**Bu sistemi doğru tanımlayan seçenek hangisidir?**

**A)** Tüm 2.000 faturayı senkron API ile işle; şemada tüm alanları required yap; tool_choice: auto; doğrulama adımı yok  
**B)** Fatura formatları için few-shot örnekleri; tool_use ile JSON şeması (payment_terms nullable); calculated_total ile validation; batch API (gecikme toleranslı); güven tabanlı yönlendirme  
**C)** Her fatura için çok geçişli mimari (50 instance); tüm alanlar required; retry döngüsü yok; senkron API  
**D)** Prompt tabanlı JSON (tool_use yok); tüm doğrulama insana bırak; batch API; few-shot yok  

---

## Cevap Anahtarı ve Açıklamalar

---

### Soru 1 → **C**

**Açıklama:**

Güven problemi izolasyon gerektirir. Kod stili kategorisi yüksek yanlış pozitifle diğer kategorilerin güvenilirliğini zehirliyor. Çözüm: kötü performans gösteren kategoriyi geçici olarak kaldır, iyi kategoriler çalışmaya devam etsin, kötü olanı ayrıca iyileştir.

- **(A) Yanlış:** Eşik çekmek gerçek sorunları kaçırır; sorun ölçüt yanlışlığı, eşik değil.
- **(B) Yanlış:** Daha büyük model prompt kalibrasyonu sorununu çözmez.
- **(D) Yanlış:** Tamamen yeniden yapılandırma orantısız ve yavaş çözüm.

**Kapsanan kavram:** Task 4.1 — Yanlış pozitif güven problemi ve izolasyon çözümü

---

### Soru 2 → **B**

**Açıklama:**

"Sistemi tehdit eden sorunlar" ifadesi yoruma açık. Claude her çalıştırmada bu eşiği farklı kalibre edebilir — aynı kod bazen kritik, bazen minör görünür. Çözüm: gerçek kod örnekleriyle ciddiyet tanımlamak.

- **(A) Yanlış:** Terimler anlaşılıyor, sorun öznel olmalarıdır.
- **(C) Yanlış:** Seviye sayısı sorun değil; somutluk sorunu.
- **(D) Yanlış:** Bu tanımlar genel geçersizlik sorununa sahip.

**Kapsanan kavram:** Task 4.1 — Nesir tanım vs. kod örnekli kalibrasyon

---

### Soru 3 → **C**

**Açıklama:**

Model belgedeki bilgiyi bulamıyor — format çeşitliliği sorunu. Few-shot örnekleri her format için "bilgi buradadır" haritasını öğretir. "Bilgi yoksa null" örneği ise uydurma yerine null dönmeyi sağlar.

- **(A) Yanlış:** Required alan fabrication'a yol açar — model zorunlu alana değer uydurmak zorunda kalır.
- **(B) Yanlış:** Bu talimat zaten denendi, format sorununu çözmez.
- **(D) Yanlış:** Ayrı model aşırı mühendislik.

**Kapsanan kavram:** Task 4.2 — Belge çıkarımında halüsinasyon azaltma

---

### Soru 4 → **B**

**Açıklama:**

Talimat yeniden yazma defalarca denendi — işe yaramadı. Bu, talimat miktarının sorun olmadığını gösterir. Belirsiz durumlarda tutarsızlık için çözüm: o belirsiz durumların örneklerini + gerekçelerini göstermek.

- **(A) Yanlış:** Talimat uzatma zaten denendi ve başarısız oldu.
- **(C) Yanlış:** Güven eşiği "emin değilsen atla" — ama asıl sorun kararın ne zaman verilmesi gerektiği.
- **(D) Yanlış:** Sorun model kapasitesi değil, belirsiz durumların nasıl ele alınacağı.

**Kapsanan kavram:** Task 4.2 — Belirsiz durumlarda few-shot + gerekçe

---

### Soru 5 → **B**

**Açıklama:**

Tool_use sözdizimi sorunlarını çözer — JSON geçerli. Ama anlamsal hataları (yanlış toplam) engellemez. `calculated_total` şemaya eklenince model her satırı toplayarak doldurur; validation adımında uyuşmazlık tespit edilir ve retry ile düzeltme şansı doğar.

- **(A) Yanlış:** Prompt tabanlı JSON sözdizimi güvencesini kaybettirir.
- **(C) Yanlış:** Model değiştirmek bu tür anlamsal tutarsızlığı çözmez.
- **(D) Yanlış:** Required alan uydurma riskini artırır, toplamı doğrulamaz.

**Kapsanan kavram:** Task 4.3 — Tool_use sınırları + anlamsal doğrulama

---

### Soru 6 → **C**

**Açıklama:**

`"any"` modeli mutlaka bir araç çağırmaya zorlar — garantili yapılandırılmış çıktı. Belge tipine göre hangi aracı seçeceğini model belirler.

- **(A) Yanlış:** `"auto"` metin yanıtı dönebilir — garanti yok.
- **(B) Yanlış:** Spesifik araç zorlama tüm belgeleri fatura olarak ele alır — hatalı sınıflandırma.
- **(D) Yanlış:** Varsayılan `"auto"` — garanti yok.

**Kapsanan kavram:** Task 4.3 — tool_choice modları

---

### Soru 7 → **C**

**Açıklama:**

İki retry'dan sonra hâlâ null — sorun bilginin belgede olmamasıdır. Model aynı belgeye bakıyor; bilgi yoksa retry yardımcı olmaz. Doğru çözüm: alanı nullable yapmak.

- **(A) Yanlış:** Retry, kaynak sorununu çözmez — sadece zaman ve para harcar.
- **(B) Yanlış:** Daha büyük model da aynı belgeye bakacak.
- **(D) Yanlış:** Few-shot "nasıl çıkarılır" öğretir, ama bilgi yoksa hiçbir örnek yardımcı olmaz.

**Kapsanan kavram:** Task 4.4 — Retry etkinlik sınırı

---

### Soru 8 → **B**

**Açıklama:**

Haftalık arşiv analizi gecikmeye toleranslı — batch uygun. PR güvenlik taraması bloklanabilir iş akışı — geliştiriciler merge öncesi sonucu bekliyor, senkron şart.

- **(A) Yanlış:** PR güvenlik taraması bekleyemez.
- **(C) Yanlış:** Batch API belge sayısına göre kısıtlı değil.
- **(D) Yanlış:** Batch API zaman dilimine göre çalışmaz.

**Kapsanan kavram:** Task 4.5 — Senkron vs. Batch karar kuralı

---

### Soru 9 → **B**

**Açıklama:**

Dosya başına analiz dikkat seyreltmesini önler — bu kısım doğru çalışıyor. Ama cross-file sorunları tespit etmek için tüm dosya bulgularını gören bağımsız bir entegrasyon geçişi gerekir.

- **(A) Yanlış:** 50 dosyayı tek instance'a vermek dikkat seyreltmesine yol açar.
- **(C) Yanlış:** Gruplama kısmi çözüm; tam cross-file görünüm sağlamaz.
- **(D) Yanlış:** Otomasyon cross-file sorunları da tespit edebilir — insan devreye girmeden önce.

**Kapsanan kavram:** Task 4.6 — Çok geçişli mimari

---

### Soru 10 → **B**

**Açıklama:**

Her gereksinim bir teknikle eşleşiyor:

| Gereksinim | Teknik |
|------------|--------|
| Format çeşitliliği | Few-shot örnekleri (Task 4.2) |
| Geçerli JSON | Tool_use + JSON şeması (Task 4.3) |
| Anlamsal doğrulama | calculated_total + validation (Task 4.4) |
| Maliyet + gecikme toleransı | Batch API (Task 4.5) |
| payment_terms bazen yok | Nullable alan (Task 4.3) |
| Güven tabanlı yönlendirme | confidence routing (Task 4.6) |

- **(A) Yanlış:** Required alanlar uydurma yaratır; auto tool_choice garanti vermez; doğrulama yok.
- **(C) Yanlış:** 2.000 fatura için her birine 50 instance aşırı kaynak; required all fabrication riski.
- **(D) Yanlış:** Prompt tabanlı JSON güvenilmez; tüm doğrulamayı insana bırakmak ölçeklenemez.

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
| 1 | 4.1 — Açık Kriterler (Güven izolasyonu) |
| 2 | 4.1 — Açık Kriterler (Ciddiyet kalibrasyonu) |
| 3 | 4.2 — Few-Shot (Belge çıkarımı, halüsinasyon) |
| 4 | 4.2 — Few-Shot (Belirsiz karar tutarsızlığı) |
| 5 | 4.3 — Tool_use (Anlamsal doğrulama) |
| 6 | 4.3 — Tool_use (tool_choice modları) |
| 7 | 4.4 — Validation-Retry (Etkinlik sınırı) |
| 8 | 4.5 — Batch Processing (Senkron vs. Batch) |
| 9 | 4.6 — Multi-Instance (Çok geçişli mimari) |
| 10 | 4.1–4.6 — Bütünleşik senaryo |
