# Domain 5 Yeterlilik Testi: Bağlam Yönetimi ve Güvenilirlik

## Genel Bilgiler

- **Domain Ağırlığı:** Sınavın %15'i
- **Soru Sayısı:** 10 (+ 5 soruluk ek alıştırma bölümü)
- **Geçme Eşiği:** 8/10
- **Zorluk:** Sınav düzeyinde senaryo bazlı sorular — şıklar benzer uzunlukta ve her biri kısmen makul
- **Kapsam:** Tüm 6 Task Statement (5.1 – 5.6)

---

> Önce soruları yanıtla, ardından cevap anahtarına bak. Ders dosyalarındaki senaryolar bu testte tekrar etmez; her soru kavramı yeni bir açıdan sınar.

---

## Sorular

---

### Soru 1 — Task Statement 5.2 (Eskalasyon kalibrasyonu) — Exam Guide Q3

Müşteri destek agent'ının ilk temasta çözüm oranı %55; hedef %80. Loglar agent'ın fotoğraf kanıtlı standart hasar değişimi gibi basit vakaları eskalasyon ederken, politika istisnası gerektiren karmaşık durumları kendi başına çözmeye çalıştığını gösteriyor.

**Eskalasyon kalibrasyonunu iyileştirmenin en etkili yolu nedir?**

**A)** System prompt'a, ne zaman eskalasyon yapılıp ne zaman özerk çözüleceğini gösteren few-shot örnekli açık eskalasyon kriterleri ekle.

**B)** Agent her yanıttan önce 1–10 arası güven skoru bildirsin; skor eşiğin altındaysa talebi otomatik olarak insana yönlendir.

**C)** Geçmiş biletlerle eğitilmiş ayrı bir sınıflandırıcı model kur; ana agent işlemeye başlamadan hangi taleplerin eskalasyon gerektirdiğini tahmin etsin.

**D)** Duygu analizi ile müşteri hayal kırıklığını ölç; olumsuz duygu eşiği aşıldığında otomatik eskalasyon yap.

---

### Soru 2 — Task Statement 5.3 (Hata yayılımı) — Exam Guide Q8

Web search subagent karmaşık bir konuyu araştırırken zaman aşımına uğruyor. Bu hata bilgisinin koordinatör agent'a nasıl akacağını tasarlaman gerekiyor.

**Hangi yaklaşım akıllı kurtarmayı en iyi sağlar?**

**A)** Koordinatöre hata türü, denenen sorgu, varsa kısmi sonuçlar ve olası alternatif yaklaşımları içeren yapılandırılmış hata bağlamı döndür.

**B)** Subagent içinde exponential backoff'lu otomatik retry uygula; tüm denemeler tükenince koordinatöre jenerik "search unavailable" durumu döndür.

**C)** Zaman aşımını subagent içinde yakala ve başarılı olarak işaretlenmiş boş bir sonuç kümesi döndür.

**D)** Zaman aşımı istisnasını doğrudan üst seviye bir handler'a yay ve tüm araştırma iş akışını sonlandır.

---

### Soru 3 — Task Statement 5.1 (Çok konulu oturum)

Case facts bloğu kullanan bir müşteri destek agent'ı, tek konulu konuşmalarda kusursuz çalışıyor. Bir müşteri aynı konuşmada iki farklı sipariş için iade ve bir fatura itirazı açıyor; 7. turda agent fatura itirazına ilk siparişin iade tutarıyla cevap veriyor.

**Kök neden ve çözüm nedir?**

**A)** Case facts bloğu özetleme sırasında bozulmuş; bloğu özetlenen geçmişin dışına taşı ve her prompt'a dahil et.

**B)** Araç sonuçları bağlamı doldurmuş; sipariş sorgularını iade için gerekli alanlara kırpıp sonra bağlama ekle.

**C)** Tek bir case facts bloğu birden fazla konuyu temsil edemiyor; konu başına yapılandırılmış kayıt ve aktif konu alanı içeren ayrı bir bağlam katmanı kur.

**D)** Konuşma geçmişi tam gönderilmiyor; ardışık isteklere tüm önceki turları dahil et.

---

### Soru 4 — Task Statement 5.1 (Lost in the middle)

Bir koordinatör, 7 subagent'ın araştırma çıktısını art arda birleştirip sentez agent'a veriyor. Sentez raporu ilk iki ve son iki subagent'ın bulgularını ayrıntılı işlerken 3–5. subagent'ların bulgularını neredeyse hiç kullanmıyor. Subagent çıktılarının her biri yapılandırılmış ve kısa.

**En etkili düzeltme hangisidir?**

**A)** Sentez agent'a "tüm subagent bulgularını eşit ağırlıkla değerlendir" talimatı ekle.

**B)** Subagent'ları verbose içerik yerine yapılandırılmış veri döndürecek şekilde yeniden tasarla.

**C)** Subagent sayısını 4'e düşür; daha az girdi daha dengeli işlenir.

**D)** Koordinatör birleştirilmiş girdinin başına anahtar bulgular özeti koysun ve her subagent çıktısını açık bölüm başlıklarıyla ayırsın.

---

### Soru 5 — Task Statement 5.3 (Erişim hatası vs geçerli boş sonuç)

Bir araştırma koordinatörü, belge analizi subagent'ından `{"status": "success", "results": []}` alıyor. Loglar aynı sorgunun bir saat önce 9 sonuç döndürdüğünü ve belge deposunun o sırada bakımda olduğunu gösteriyor. Koordinatör "bu konuda belge yok" diye raporlamış.

**Kök neden nedir?**

**A)** Koordinatör boş sonucu görünce sorguyu bir kez daha denemeliydi; boş sonuç her zaman tekrar denenir.

**B)** Subagent'ın yanıt şeması erişim hatası ile geçerli boş sonucu ayırt etmiyor; bakım kesintisi "başarı + boş dizi" olarak yayılmış.

**C)** Koordinatör sonucu doğrulamak için ikinci bir subagent'a aynı sorguyu göndermeliydi.

**D)** Belge deposunun bakımı sistem dışı bir olay; koordinatörün yapabileceği bir şey yok.

---

### Soru 6 — Task Statement 5.4 (Bağlam bozulması mekanizması)

Bir mimar, kod tabanı keşfi yapan agent'ın uzun oturumlarda "tipik kalıplar"a kaydığını fark ediyor ve ekibe şu açıklamayı yapıyor: "Context window dolunca en eski mesajlar düşüyor, o yüzden büyük pencereli bir modele geçmeliyiz."

**Bu açıklamanın ve önerinin değerlendirmesi hangisidir?**

**A)** Açıklama doğru, öneri doğru: pencere büyüdükçe daha az mesaj düşer, bozulma gecikir.

**B)** Açıklama yanlış: API mesaj düşürmez, sınır aşılırsa hata döner; Claude Code ise özetler. Bozulma, sınırdan önce dikkat bütçesinin seyrelmesi (context rot) ve compact sonrası özet kaybıyla oluşur; pencere büyütmek dikkat kalitesini çözmez.

**C)** Açıklama doğru, öneri yanlış: mesajlar düşer ama çözüm daha sık `/compact` çalıştırmaktır.

**D)** Açıklama yanlış: bozulmanın nedeni modelin talimatı unutmasıdır; system prompt'a "spesifik ol" eklemek yeterlidir.

---

### Soru 7 — Task Statement 5.4 (Scratchpad vs CLAUDE.md, /compact vs /clear)

Claude Code ile 3 saatlik bir keşif oturumunda bağlam doluluk uyarısı geliyor. Bulgular yalnızca konuşmanın içinde. Developer aynı işe devam edecek. Ekip iki öneri tartışıyor: (1) bulguları CLAUDE.md'ye yazıp `/clear` çalıştırmak, (2) bulguları NOTES.md'ye yazdırıp odak talimatlı `/compact` çalıştırmak.

**Hangisi doğru ve neden?**

**A)** (1): CLAUDE.md her oturumda otomatik yüklenir, bulgular hiç kaybolmaz; `/clear` en temiz bağlamı verir.

**B)** İkisi de yanlış: doğru çözüm otomatik compact'i kapatıp pencere dolana kadar devam etmektir.

**C)** (2): NOTES.md oturumun çalışma belleğidir, CLAUDE.md ise kalıcı talimat dosyası — bulgular oraya yazılırsa her oturumu şişirir; `/compact <odak>` anlatıyı özetlerken kritik bulguları korur, `/clear` ise özetlemeden sıfırlar.

**D)** İkisi de doğru: dosya seçimi ve komut seçimi tercih meselesidir.

---

### Soru 8 — Task Statement 5.5 (Tabakalı örnekleme + ikinci sinyal)

Kalibre edilmiş alan-bazlı güvenle çalışan bir çıkarım sistemi, %92 üstü alanları otomatik kabul ediyor ve kalite ekibi haftada düz rastgele 50 çıkarımı elle kontrol ediyor. İki ay sonra iki sorun ortaya çıkıyor: (1) yeni bir tedarikçinin fatura şablonunda model yüksek güvenle yanlış vade tarihi çıkarıyor; hacmi düşük olduğu için 50'lik örneklemde hiç görünmemiş; (2) satır toplamı ile belgedeki genel toplamın uyuşmadığı faturalar model %95 güvenle geçmiş.

**Bu iki sorunu birlikte çözen tasarım hangisidir?**

**A)** Örneklemeyi belge türü × alan × güven bandı tabakalarına böl (her tabakadan minimum örnek, yüksek güvenden de); yönlendirmeye ikinci sinyal ekle: belge doğrulaması çelişki bulursa (`conflict_detected`) güven ne olursa olsun insan incelemesine gönder.

**B)** Haftalık örneklemi 200'e çıkar ve otomatik kabul eşiğini %98'e yükselt.

**C)** Yeni tedarikçinin faturalarını insan incelemesine yönlendir ve modele "toplamları kontrol et" talimatı ekle.

**D)** Güven skorunu enum olarak iste ve `high` dışındaki her şeyi insana gönder.

---

### Soru 9 — Task Statement 5.6 (Çelişki — kim karar verir)

Belge analizi subagent'ı iki güvenilir raporda farklı büyüme oranı buluyor (%45 ve %38, farklı metodoloji). Sistem tasarımcısı üç seçenek tartışıyor.

**Exam guide'ın rol dağılımına uyan hangisidir?**

**A)** Subagent metodolojiyi değerlendirip daha güvenilir bulduğu tek değeri döndürsün; koordinatör ve sentez o değerle ilerlesin.

**B)** Subagent iki değerin ortalamasını ve standart sapmasını döndürsün; rapor aralık olarak yazsın.

**C)** Subagent iki değeri de döndürsün; sentez agent'ı daha güncel olanı seçip tek rakam yazsın, dipnotta diğerini belirtsin.

**D)** Subagent iki değeri de kaynak, tarih, nitelendirme ve metodoloji notuyla işaretleyip analizi tamamlasın; uzlaştırma kararını koordinatör versin; sentez raporda ikisini de "tartışmalı bulgular" bölümünde kaynağıyla göstersin.

---

### Soru 10 — Bütünleşik Senaryo (Tüm Domain)

Bir şirket müşteri destek + araştırma + belge çıkarımı içeren bir multi-agent sistem işletiyor. Beş sorun raporlanıyor:

1. Müşteri temsilciye eskalasyon edildiğinde sipariş numarasını ve talebini baştan anlatmak zorunda kalıyor
2. Basit hasar değişimleri eskalasyon ediliyor, garanti süresi aşılmış talepler agent tarafından onaylanıyor
3. Araştırma subagent'ı zaman aşımında backoff'lu retry yapıyor, sonra "kaynak kullanılamıyor" döndürüyor; koordinatör alternatif kaynak deneyemiyor
4. Sentez raporu IEA'nın "ön tahmin" dediği rakamı kesin ölçüm gibi yazıyor
5. %97 toplam doğruluk bildiren çıkarım sisteminde düşük hacimli bir belge türü haftalık düz rastgele örneklemde hiç görünmüyor

**Beş sorunu doğru kavramla eşleştiren seçenek hangisidir?**

**A)**
1. Konuşma geçmişini özetleme
2. Duygu eşiğini düşür
3. Retry sayısını artır
4. Sentez agent'a "kaynak göster" talimatı
5. Örneklem boyutunu büyüt

**B)**
1. `escalate_to_human` çağrısına case facts el-devir bağlamı
2. Few-shot örnekli açık eskalasyon kriterleri (iki yönlü kalibrasyon)
3. Jenerik durum yerine yapılandırılmış hata bağlamı (retry doğru, mesaj yanlış)
4. Claim-source eşleştirmesinde kaynağın nitelendirmesini koru
5. Belge türü × alan × güven bandı tabakalı örnekleme

**C)**
1. Daha büyük context window
2. Ayrı bir eskalasyon sınıflandırıcısı eğit
3. Zaman aşımında iş akışını durdur, insan müdahalesi iste
4. Sentez sonrası doğrulama agent'ı kaynak arasın
5. Otomatik kabul eşiğini %99'a çıkar

**D)**
1. Eskalasyonu kaldır, agent her şeyi çözsün
2. Modelin güven skoruna göre eskalasyon
3. Subagent hatayı yakalayıp boş sonuç döndürsün
4. Rakamı rapordan çıkar
5. Düşük hacimli türü pipeline'dan çıkar

---

## Cevap Anahtarı ve Açıklamalar

---

### Soru 1 → **A**

**Açıklama:** Exam guide'ın kendi sorusu ve gerekçesi: kök neden **belirsiz karar sınırları**; few-shot örnekli açık kriterler bunu doğrudan çözer ve altyapı eklemeden önce **orantılı ilk müdahale**dir. Kalibrasyon iki yönde bozuk (basitler eskalasyon, karmaşıklar özerk); ancak örnekler iki sınırı da gösterir.

- **(B) Yanlış:** LLM'in self-reported güveni kalibre değildir — agent zor vakalarda zaten yanlış yere güvenli. Eşik iki yönlü sorunu tek yönlü ölçüyle çözmeye çalışır.
- **(C) Yanlış:** Over-engineering — etiketli veri ve ML altyapısı gerektirir; prompt optimizasyonu henüz denenmemiş.
- **(D) Yanlış:** Farklı bir sorunu çözer; duygu vaka karmaşıklığıyla korele değil.

**Kapsanan kavram:** Task 5.2 — Few-shot örnekli eskalasyon kriterleri, orantılılık merdiveni

---

### Soru 2 → **A**

**Açıklama:** Yapılandırılmış hata bağlamı koordinatöre karar için gereken bilgiyi verir: değiştirilmiş sorguyla retry mi, alternatif yaklaşım mı, kısmi sonuçlarla devam mı.

- **(B) Yanlış:** En cazip yanlış şık. Yerel retry (katman 1) doğru; ama jenerik "search unavailable" (katman 2) bağlamı koordinatörden gizler — hangi sorgu, ne tür hata, kısmi sonuç var mı bilinmez.
- **(C) Yanlış:** Sessiz bastırma — hatayı başarı diye işaretlemek her türlü kurtarmayı engeller ve eksik araştırma çıktısı riski yaratır.
- **(D) Yanlış:** Kurtarma stratejileri işe yarayabilecekken tüm iş akışını gereksiz sonlandırır.

**Kapsanan kavram:** Task 5.3 — Üç anti-pattern, iki katmanlı kurtarma

---

### Soru 3 → **C**

**Açıklama:** Case facts tek vaka içindir; exam guide çok konulu oturumlar için "*structured issue data … into a separate context layer*" ister. Konu başına kayıt + aktif konu alanı, agent'ın hangi konuda olduğunu belirsizlikten kurtarır.

- **(A) Yanlış:** Sorun bloğun özetlenmesi değil, *yapısı*: tek `order_id` ve tek `refund_amount` üç konuyu temsil edemez. Blok zaten dışarıda tutuluyor.
- **(B) Yanlış:** Araç sonucu şişmesi başka bir semptom (bütçe tükenmesi) üretir; konuların karışması değil.
- **(D) Yanlış:** Geçmiş tam gönderilse de tek bloklu yapı konuları ayıramaz; yapısal sorun.

**Kapsanan kavram:** Task 5.1 — Çok konulu oturum bağlam katmanı

---

### Soru 4 → **D**

**Açıklama:** Lost-in-the-middle, exam guide'ın diliyle "*aggregated inputs*"ta çıkar; sorun *birleştirmeyi yapan* koordinatörün formatındadır. Çözüm: anahtar bulgular özeti başa + açık bölüm başlıkları.

- **(A) Yanlış:** Talimat dikkat mekanizmasını değiştirmez; ortadaki içerik yine ortadadır.
- **(B) Yanlış:** Soru zaten çıktıların yapılandırılmış ve kısa olduğunu söylüyor — upstream optimizasyonu yapılmış; sorun birleştirme düzeni.
- **(C) Yanlış:** Kapsamı daraltır; 4 subagent'ta da 2. ve 3. ortada kalır.

**Kapsanan kavram:** Task 5.1 — Lost in the middle (aggregated inputs)

---

### Soru 5 → **B**

**Açıklama:** Aynı JSON şekli iki farklı gerçeği (erişilemedi / eşleşme yok) anlatıyorsa şema bozuktur. Exam guide ayrımı "*in error reporting*" ister: `source_reached` / `failure_type` alanları. Bakım kesintisi sessiz bastırma olarak yayılmış.

- **(A) Yanlış:** "Boş sonuç her zaman retry" ters hata: geçerli boş sonuçları da tekrar tekrar sorgular. Retry kararı erişim durumunun *bilinmesini* gerektirir; şema onu vermiyor.
- **(C) Yanlış:** İkinci subagent aynı bozuk şemayla aynı cevabı döndürür.
- **(D) Yanlış:** Kesinti dış olay ama *sessiz kalması* sistemin hatası; yapılandırılmış hata gelseydi koordinatör bekleyip yeniden deneyebilir ya da kapsam notu düşerdi.

**Kapsanan kavram:** Task 5.3 — Erişim hatası vs geçerli boş sonuç, yanıt şemasında ayrım

---

### Soru 6 → **B**

**Açıklama:** Messages API mesaj düşürmez, sınır aşılırsa hata döner; Claude Code sınıra yaklaşınca otomatik compact eder. Bozulma iki mekanizmayla oluşur: sınırdan önce context rot (dikkat bütçesi), compact sonrası özet kaybı. Q12'nin gerekçesiyle: "*larger context windows don't solve attention quality issues*".

- **(A) Yanlış:** Hem açıklama hem öneri yanlış; pencere büyütmek aynı bağlam kirliliğini daha geniş alanda yaşatır.
- **(C) Yanlış:** Açıklama yine yanlış; daha sık compact, odak talimatı ve scratchpad olmadan özet kaybını artırır.
- **(D) Yanlış:** Sorun talimat değil, dikkat ve özetleme; "spesifik ol" erişilemeyen bilgiyi geri getirmez.

**Kapsanan kavram:** Task 5.4 — Bağlam bozulması mekanizması, büyük pencere distractor'ı

---

### Soru 7 → **C**

**Açıklama:** Scratchpad (NOTES.md) oturumun çalışma belleği, CLAUDE.md projenin kalıcı talimat dosyasıdır (Domain 3.1); keşif bulguları CLAUDE.md'ye yazılırsa her oturumu şişirir ve ilgisiz oturumları kirletir. `/compact <odak>` aynı işte devam ederken anlatıyı özetler, kritik bulguları korur; `/clear` özetlemez, sıfırlar — ilgisiz işe geçerken kullanılır.

- **(A) Yanlış:** CLAUDE.md'nin "hiç kaybolmaz" özelliği tam da sorundur; `/clear` devam edilecek işte bağlamı tümden atar.
- **(B) Yanlış:** Otomatik compact'i kapatmak sınıra dayanınca hata almak demektir.
- **(D) Yanlış:** Dosya seçimi (oturum belleği vs kalıcı talimat) ve komut seçimi (özetle vs sıfırla) tercih değil, semantik farktır.

**Kapsanan kavram:** Task 5.4 — Scratchpad vs CLAUDE.md, `/compact` vs `/clear`

---

### Soru 8 → **A**

**Açıklama:** İki sorun, iki mekanizma. (1) Düz rastgele örnekleme düşük hacimli türü temsil etmez — toplam metrik tuzağı örneklemede tekrar eder; tabakalı örnekleme (belge türü × alan × güven bandı, yüksek güvenden de) yeni hata kalıbını yakalar. (2) Model çelişkili belgeyi fark etmeden bir değeri yüksek güvenle seçebilir; exam guide düşük güven **veya** çelişkili/belirsiz kaynak belgeyi insana gönderir — `conflict_detected` ikinci kapıdır.

- **(B) Yanlış:** Daha büyük düz örneklem düşük hacimli türü yine seyrek görür; eşik yükseltmek belge tutarsızlığını ölçmez.
- **(C) Yanlış:** Tedarikçiye özel yönlendirme semptomu yamalar (sonraki yeni şablonu yakalamaz); toplama kontrolü deterministik doğrulamadır, modele bırakılmaz.
- **(D) Yanlış:** Gösterim değişikliği kalibrasyonu değiştirmez; `high` dışını insana göndermek kapasiteyi boğar ve çelişkili belge yine `high` ile geçer.

**Kapsanan kavram:** Task 5.5 — Tabakalı örnekleme, iki yönlendirme sinyali

---

### Soru 9 → **D**

**Açıklama:** Exam guide'ın rol dağılımı: belge analizi subagent'ı çelişkili değerleri işaretleyip analizi *tamamlar*; **koordinatör** sentezden önce uzlaştırma kararını verir; sentez raporda "iyi desteklenen / tartışmalı" ayrımıyla ikisini de kaynağıyla gösterir.

- **(A) Yanlış:** Subagent'ın "daha güvenilir" yargısıyla tek değer döndürmesi keyfi seçimdir; bilgiyi üst katmanlardan gizler.
- **(B) Yanlış:** Ortalama/aralık, hiçbir kaynağın söylemediği bir sayı üretir; metodoloji farkını görünmez kılar.
- **(C) Yanlış:** "Daha güncel" de keyfi bir kuraldır (revizyon dışında geçerli değil) ve sentez agent'ı uzlaştırma katmanı değildir.

**Kapsanan kavram:** Task 5.6 — Çelişki yönetimi, rol dağılımı, rapor iskeleti

---

### Soru 10 → **B**

**Açıklama:** Her sorun farklı bir Domain 5 kavramıyla eşleşiyor:

| Sorun | Kavram | Çözüm |
|-------|--------|-------|
| 1. Eskalasyonda baştan anlatma | Task 5.2 + 5.1 — El-devir bağlamı | `escalate_to_human` + case facts |
| 2. Basitler eskalasyon, istisnalar onay | Task 5.2 — İki yönlü kalibrasyon (Q3) | Few-shot örnekli açık kriterler |
| 3. Retry sonrası jenerik durum | Task 5.3 — Anti-pattern 3 (Q8-B) | Yapılandırılmış hata bağlamı |
| 4. "Ön tahmin" → kesin ölçüm | Task 5.6 — Kaynak nitelendirmesi | Claim-source eşleştirmesinde `source_characterization` |
| 5. Düşük hacimli tür örneklemde yok | Task 5.5 — Tabakalı örnekleme | Belge türü × alan × güven bandı |

- **(A) Yanlış:** Her çözüm yüzeysel: özetleme el-devir bağlamı vermez; duygu eşiği kalibrasyonu düzeltmez; retry sayısı jenerik mesajı çözmez; talimat nitelendirmeyi yaratmaz; büyük düz örneklem düşük hacimli türü yine kaçırır.
- **(C) Yanlış:** Orantısız/yanlış: büyük pencere el-devirle ilgisiz; sınıflandırıcı prompt denenmeden over-engineering; iş akışı durdurmak anti-pattern; sonradan kaynak aramak nitelendirmeyi geri getirmez; %99 eşik tabaka sorununu çözmez.
- **(D) Yanlış:** Aşırı çözümler: eskalasyonu kaldırmak politika ihlali; güven skoru güvenilmez tetikleyici; boş sonuç döndürmek sessiz bastırma; rakamı çıkarmak bilgi kaybı; türü çıkarmak veri kaybı.

**Kapsanan kavram:** Task 5.1–5.6 bütünleşik uygulama

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
| 1 | 5.2 — Few-shot örnekli eskalasyon kriterleri (Exam Guide Q3) |
| 2 | 5.3 — Üç anti-pattern, iki katmanlı kurtarma (Exam Guide Q8) |
| 3 | 5.1 — Çok konulu oturum bağlam katmanı |
| 4 | 5.1 — Lost in the middle (aggregated inputs) |
| 5 | 5.3 — Erişim hatası vs geçerli boş sonuç, yanıt şeması |
| 6 | 5.4 — Bağlam bozulması mekanizması |
| 7 | 5.4 — Scratchpad vs CLAUDE.md, `/compact` vs `/clear` |
| 8 | 5.5 — Tabakalı örnekleme + çelişkili belge sinyali |
| 9 | 5.6 — Çelişki yönetimi, rol dağılımı |
| 10 | 5.1–5.6 — Bütünleşik senaryo |

---

## Ek Alıştırma Bölümü (5 soru — puana dahil değil)

### Ek 1 — 5.1 (Subagent metadata)

Sentez agent'ı, iki subagent'tan gelen "işsizlik %5.2" ve "işsizlik %4.8" bulgularını çelişki olarak raporluyor. Subagent çıktıları `{claim, source, relevance}` alanlarını içeriyor.

**A)** Sentez agent'a "çelişkileri kaynak güvenilirliğine göre çöz" talimatı ekle.
**B)** Subagent çıktı şemasına yayım/veri toplama tarihi, kaynak konumu ve metodoloji alanlarını zorunlu kıl; sentez tarihleri görünce zamansal farkı çelişkiden ayırır.
**C)** İki subagent'ı tek subagent'ta birleştir; tek kaynak çelişki üretmez.
**D)** Sentez agent'a web araması verip tarihleri kendisi bulmasını iste.

**Cevap: B.** 5.1'in metadata maddesi ve 5.6'nın zamansal farkındalığı aynı çözüm: tarih zorunlu. (A) kaynak güvenilirliği zamansal farkı çözmez; (C) kapsam kaybı; (D) subagent'ın zaten bildiği tarihi yeniden aramak.

---

### Ek 2 — 5.2 (Politika sessiz)

Politika "hediye alınan ürünlerde iade, hediye makbuzuyla yapılır" diyor. Müşteri hediye makbuzu olmadan, alıcının sipariş numarasıyla iade istiyor. Politikada bu durum yok.

**A)** Sipariş numarası doğrulanabildiğine göre iadeyi yap; politika geniş yorumlanır.
**B)** "Hediye makbuzu olmadan iade yapılamaz" diyerek reddet; politika bunu gerektiriyor.
**C)** Politika bu durumda sessiz — policy gap; el-devir bağlamıyla eskalasyon yap, müşteriye açıkla.
**D)** Müşterinin ne kadar kızgın olduğuna göre karar ver.

**Cevap: C.** Politika bir yolu tanımlıyor ama bu yolun dışını *yasaklamıyor* — sessiz. (A) yetki aşımı; (B) "yok" ≠ "yasak", reddetmek de politika dışına çıkmak; (D) güvenilmez tetikleyici.

---

### Ek 3 — 5.3 (Koordinatörün üç seçeneği)

Koordinatör, web search subagent'ından yapılandırılmış hata alıyor: `failure_type: transient, attempted: "query X, 3 retries", partial_results: 2 of 5 sources, alternatives_untried: ["Google Scholar"]`.

**Koordinatörün seçenekleri hangileridir?**

**A)** Yalnızca iş akışını durdurup insan beklemek.
**B)** Değiştirilmiş sorguyla yeniden denemek, alternatif kaynağı (Google Scholar) denemek veya 2 kaynakla devam edip rapora kapsam notu düşmek.
**C)** Aynı sorguyu aynı kaynakta 10 kez daha denemek.
**D)** Kısmi sonuçları atıp sıfırdan başlamak.

**Cevap: B.** Q8'in gerekçesindeki üçlü. Yapılandırılmış bağlam tam da bu üç kararı mümkün kılar; jenerik durum olsaydı hiçbiri seçilemezdi.

---

### Ek 4 — 5.4 (Manifest vs resume)

Çok agent'lı sistem çökme sonrası kurtarma için iki tasarım tartışılıyor: (1) her subagent'ın `session_id`'sini saklayıp `resume` ile tam transkripti geri yüklemek; (2) her agent'ın tamamlanan/bekleyen görevler ve anahtar bulguları içeren manifest yazması, koordinatörün bunu prompt'a enjekte etmesi.

**A)** (1): Transkript eksiksizdir, hiçbir bilgi kaybolmaz.
**B)** (2): Manifest kompakt uygulama durumudur; transkript verbose'dur, geri yüklenince bağlam bütçesini tüketir ve makineye bağlıdır — SDK dokümanı da sonuçları uygulama durumu olarak yakalayıp yeni oturuma vermeyi önerir.
**C)** İkisi aynı sonucu verir.
**D)** Hiçbiri: çökmeyi önlemek için daha güvenilir altyapı gerekir.

**Cevap: B.** Exam guide'ın cevabı manifest; güncel SDK bile "don't rely on session resume" der.

---

### Ek 5 — 5.6 (Revizyon)

Aynı istatistik kurumu Şubat'ta "2025 enflasyonu %38.2 (öncü)" ve Mayıs'ta "2025 enflasyonu %37.9 (kesinleşmiş)" yayımlıyor. Rapor iki değeri "farklı dönemlerin verisi" diye yan yana sunuyor.

**A)** Doğru: yayın tarihleri farklı, dolayısıyla zamansal fark.
**B)** Yanlış: iki değer aynı dönemi (2025) ölçüyor; bu revizyon. Kesinleşmiş değer geçerli, "öncü %38.2 idi, revize edildi" notu ve iki tarih korunur.
**C)** Yanlış: ortalama alınmalı.
**D)** Yanlış: öncü değer ilk yayın olduğu için esastır.

**Cevap: B.** Yayın tarihi farkı ≠ veri dönemi farkı. Revizyonda güncel geçerli, nitelendirme ve tarihler korunur.
