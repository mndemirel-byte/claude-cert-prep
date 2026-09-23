# Domain 5 Yeterlilik Testi: Bağlam Yönetimi ve Güvenilirlik

## Genel Bilgiler

- **Domain Ağırlığı:** Sınavın %15'i
- **Soru Sayısı:** 10
- **Geçme Eşiği:** 8/10
- **Zorluk:** Sınav düzeyinde senaryo bazlı sorular
- **Kapsam:** Tüm 6 Task Statement (5.1 – 5.6)

---

> Önce soruları yanıtla, ardından cevap anahtarına bak.

---

## Sorular

---

### Soru 1 — Task Statement 5.1 (Bağlam Koruma)

Bir müşteri destek agent'ı uzun konuşmalar boyunca çalışıyor. Token bütçesini yönetmek için konuşma geçmişi her 5 turda bir özetleniyor. Müşteri 3. turda şunları belirtmiş: "Sipariş #7723 için $189.50 iade istiyorum, sipariş 15 Şubat'ta verildi."

10\. turda agent müşteriye şunu söylüyor: "Hangi siparişiniz için yardımcı olabilirim?"

Aynı zamanda, araç sonuçları olduğu gibi bağlama ekleniyor — her sipariş sorgusu 45 alanla döndürülüyor.

**Bu iki sorunu birden çözen yaklaşım hangisidir?**

**A)** Context window'u büyüt ve özetleme sıklığını her 10 tura düşür

**B)** Transaksiyonel gerçekleri (sipariş no, tutar, tarih) kalıcı bir "case facts" bloğuna çıkar ve asla özetleme. Araç sonuçlarını ilgili 5 alana kırp, sonra bağlama ekle.

**C)** Agent'ın system prompt'una "müşteri bilgilerini asla unutma" talimatı ekle ve araç sonuçlarını JSON formatında sakla

**D)** Özetleme yapma — tüm konuşma geçmişini olduğu gibi tut

---

### Soru 2 — Task Statement 5.1 (Bağlam Koruma)

Bir multi-agent araştırma sisteminde web search agent her sorgu için 3 sayfalık detaylı analiz, düşünce zinciri ve alternatif hipotezler döndürüyor. Alt-akış synthesis agent'ın bağlam bütçesi 8K token. 3 kaynaktan sonra bütçe tükeniyor — ama 7 kaynak analiz edilmeli.

**En etkili çözüm hangisidir?**

**A)** Synthesis agent'ın bağlam bütçesini 64K'ya çıkar

**B)** Kaynak sayısını 3'e düşür — bütçeye sığar

**C)** Web search agent'ı yapılandırılmış veri (anahtar gerçekler, atıflar, ilgililik skoru) döndürecek şekilde modifiye et — verbose içerik ve düşünce zincirleri yerine

**D)** Synthesis agent'a "kısa yaz" talimatı ekle

---

### Soru 3 — Task Statement 5.2 (Eskalasyon)

Bir müşteri destek agent'ına müşteri şunu yazıyor: "Bu sipariş 3 gündür gelmedi, çok sinirleniyorum artık!" Agent, sipariş durumunu kontrol ediyor ve siparişin bugün teslim edileceğini görüyor.

**Agent ne yapmalı?**

**A)** Müşteri kızgın → hemen insan temsilciye eskalasyon yap

**B)** Hayal kırıklığını kabul et ve çözümü sun: "Gecikme için özür dilerim. Siparişiniz bugün teslim edilecek — takip numaranız X."

**C)** Müşterinin güven skorunu kontrol et — düşükse eskalasyon yap

**D)** Müşteriye "sakin olun" de ve beklemeye devam etmesini söyle

---

### Soru 4 — Task Statement 5.2 (Eskalasyon)

Bir müşteri "Rakip sitede bu ürün $20 daha ucuz, fiyat eşleştirmesi istiyorum" diyor. Agent politika dokümanını kontrol ediyor: "Kendi sitemizdeki fiyat düşüşlerinde farkı iade ederiz." Politikada rakip fiyat eşleştirmesi hakkında bilgi yok.

Aynı zamanda, "Ahmet Yılmaz" adıyla müşteri araması yapılıyor ve 4 farklı "Ahmet Yılmaz" eşleşiyor.

**Bu iki durumu doğru ele alan yaklaşım hangisidir?**

**A)** Rakip fiyat eşleştirmesini politikayı geniş yorumlayarak kabul et. 4 eşleşmeden en son sipariş vereni seç.

**B)** Rakip fiyat eşleştirmesini reddet — politikada yok. En aktif müşteri hesabını seç.

**C)** Rakip fiyat eşleştirmesi politika boşluğu — eskalasyon yap. Müşteri eşleştirmesi için ek tanımlayıcı bilgi iste (e-posta, telefon, sipariş no).

**D)** Müşterinin duygu durumuna göre karar ver — kızgınsa eskalasyon yap, sakinse reddet. 4 eşleşmeden rastgele birini seç.

---

### Soru 5 — Task Statement 5.3 (Hata Yayılımı)

Bir araştırma pipeline'ı 6 akademik veritabanından veri topluyor. 5 veritabanı başarıyla sonuç döndürdü. 6. veritabanı (PubMed) ağ zaman aşımı hatası verdi. Agent'ın mevcut davranışı: hata oluştuğunda boş sonuç dizisini `"status": "success"` ile döndürüyor.

**Bu davranıştaki sorun ve doğru çözüm nedir?**

**A)** Sorun yok — boş sonuç geçerli bir sonuçtur

**B)** Silent suppression anti-pattern'ı. Erişim hatasını başarılı olarak işaretlemek kurtarma mekanizmasını engeller. Doğru: hata türünü (transient), neyin denendiğini ve kısmi sonuçları yapılandırılmış olarak raporla.

**C)** Pipeline'ı tamamen durdur — eksik veriyle devam etmek tehlikeli

**D)** PubMed'i sonsuz döngüde retry et — sonunda çalışır

---

### Soru 6 — Task Statement 5.3 (Hata Yayılımı)

Bir müşteri destek agent'ı müşterinin telefon numarasıyla sipariş arıyor. Araç şu sonucu döndürüyor:

```json
{
  "status": "success",
  "results": [],
  "message": "No orders found for this phone number"
}
```

Agent bu sonucu alıp aynı telefon numarasıyla 3 kez daha retry ediyor.

**Bu davranıştaki sorun nedir?**

**A)** Retry sayısı az — 10 kez denemeli

**B)** Farklı parametrelerle retry etmeli — telefon yerine e-posta denesin

**C)** Agent geçerli boş sonuç ile erişim hatasını karıştırıyor. Status "success" — araç kaynağa erişti, eşleşme bulamadı. Bu cevabın kendisi, retry gereksiz.

**D)** Araç hatalı — her zaman en az bir sonuç döndürmelidir

---

### Soru 7 — Task Statement 5.4 (Kod Tabanı Keşfi)

Bir developer, 4 saattir bir agent oturumuyla büyük bir kod tabanını analiz ediyor. Agent başlangıçta spesifik sınıf isimleri, satır numaraları ve metot imzaları raporluyordu. Şimdi ise "bu modüllerde genellikle dependency injection kullanılır" gibi genel ifadeler kullanıyor.

Aynı zamanda, ekip bu agent oturumlarının çökme durumunda sıfırdan başlamak zorunda kaldığından şikâyet ediyor.

**Bu iki sorunu birden çözen yaklaşım hangisidir?**

**A)** Daha büyük context window'a sahip model kullan ve oturumu hiç kapatma

**B)** Anahtar bulguları scratchpad dosyasına yaz. Derinlemesine araştırmaları subagent'lara delege et. Her agent durumunu manifest dosyasına yazsın — çökme sonrası koordinatör manifestleri yükleyerek kurtarma yapsın.

**C)** Agent'a "spesifik ol" talimatı ekle ve çökme durumunda tüm konuşma geçmişini veritabanında sakla

**D)** Oturumu her 1 saatte bir yeniden başlat — bağlam bozulması olmasın

---

### Soru 8 — Task Statement 5.5 (İnsan İncelemesi ve Güven Kalibrasyonu)

Bir belge çıkarım sistemi %96 genel doğruluk bildiriyor. Yönetim tam otomasyona geçmeyi planlıyor. Alan seviyesi güven eşikleri %80 olarak belirlenmiş — herhangi bir doğrulama verisi olmadan, sezgisel olarak.

İç denetim iki bulgu raporluyor:
1. El yazısı belgelerde %35 hata oranı var
2. Model %85 güven dediği alanlarda gerçek doğruluk %58

**Bu iki sorunu birden ele alan yaklaşım hangisidir?**

**A)** Güven eşiğini %95'e çıkar ve el yazısı belgeleri pipeline'dan çıkar

**B)** Doğruluğu belge türüne ve alan segmentine göre ayrı değerlendir — el yazısı belgeleri insan incelemesine yönlendir. Güven eşiklerini etiketli doğrulama setleriyle (ground truth data) kalibre et.

**C)** Daha büyük model kullan — hem doğruluk hem güven skoru iyileşir

**D)** Tüm belge türleri için %100 insan incelemesi sürdür — otomasyon güvenilmez

---

### Soru 9 — Task Statement 5.6 (Bilgi Kaynağı Takibi)

Bir araştırma raporunda iki kaynak aynı metrik için farklı değerler bildiriyor:

- IEA (Mart 2024): "Küresel rüzgâr kapasitesi 1,021 GW"
- GWEC (Haziran 2024): "Küresel rüzgâr kapasitesi 1,089 GW"

Sentez agent'ı bu durumu "çelişkili veri" olarak işaretleyip her iki kaynağı da rapordan çıkarıyor.

**Doğru yaklaşım hangisidir?**

**A)** Daha güncel olan GWEC değerini kullan — son veri doğrudur

**B)** İkisinin ortalamasını al — 1,055 GW

**C)** Her iki değeri kaynak atıfları ve tarihlerle birlikte sun. Farkın farklı ölçüm dönemlerinden kaynaklanabileceğini belirt — zamansal bağlam.

**D)** Her iki kaynağı da rapordan çıkarmak doğru — çelişkili veri güvenilmez

---

### Soru 10 — Bütünleşik Senaryo (Tüm Domain)

Bir şirket müşteri destek + araştırma + belge çıkarımı içeren kapsamlı bir multi-agent sistemi kuruyor. Sistem şu sorunları yaşıyor:

1. Müşteri destek agent'ı 8. turda müşterinin sipariş numarasını tekrar soruyor
2. Kızgın müşteriler otomatik olarak insan temsilciye yönlendiriliyor — vakaların %60'ı agent'ın çözebileceği basit taleplerdi
3. Araştırma pipeline'ında bir kaynak zaman aşımı verdiğinde tüm araştırma iptal ediliyor
4. Sentez raporu "sektörde önemli gelişmeler yaşandı" gibi belirsiz ifadeler içeriyor — spesifik değerler ve kaynaklar yok
5. Belge çıkarımında %95 genel doğruluk bildiriliyor ama belirli belge türlerinde performans test edilmemiş

**Bu 5 sorunu doğru eşleştiren seçenek hangisidir?**

**A)** Tüm sorunlar daha büyük model ile çözülür

**B)**
1. Case facts bloğu → transaksiyonel gerçekleri koru
2. Duygu bazlı eskalasyonu kaldır → üç geçerli tetikleyici koy
3. Kısmi sonuçlarla devam et → yapılandırılmış hata raporla + kapsam açıklaması
4. Structured claim-source mappings → iddia-kaynak eşleştirmelerini koru
5. Belge türüne göre doğrulama → tabakalı performans analizi

**C)**
1. Özetleme sıklığını azalt
2. Eskalasyon eşiğini düşür
3. Retry sayısını artır
4. Daha detaylı system prompt yaz
5. Güven eşiğini %99'a çıkar

**D)**
1. Tam konuşma geçmişini tut — asla özetleme
2. Tüm müşterileri insan temsilciye yönlendir
3. Hatalı kaynağı pipeline'dan çıkar
4. Sentez agent'a "spesifik ol" talimatı ekle
5. Tüm belge türleri için %100 insan incelemesi

---

## Cevap Anahtarı ve Açıklamalar

---

### Soru 1 → **B**

**Açıklama:**

İki sorun birden var: progressive summarisation tuzağı (sipariş bilgileri özetleme sırasında kaybolmuş) ve araç sonucu şişmesi (45 alan olduğu gibi bağlama ekleniyor). Çözüm: case facts bloğu ile transaksiyonel gerçekleri koru + tool result trimming ile verbose sonuçları ilgili alanlara kırp.

- **(A) Yanlış:** Büyük context window ve düşük özetleme sıklığı sorunu geciktirir, çözmez. 10. turda da aynı bilgi kaybı olacak.
- **(C) Yanlış:** Prompt talimatı olasılıksal. Özetlenen bilgi context'ten fiziksel olarak çıkarılmışsa, talimat işe yaramaz. JSON formatı araç sonucu şişmesini çözmez.
- **(D) Yanlış:** Asla özetlememek token bütçesini hızla tüketir — uzun konuşmalarda sürdürülemez.

**Kapsanan kavram:** Task 5.1 — Case facts bloğu + Tool result trimming

---

### Soru 2 → **C**

**Açıklama:**

Upstream agent optimisation. Sorun synthesis agent'ta değil, web search agent'ın verbose çıktısında. 3 sayfalık düşünce zinciri yerine yapılandırılmış veri (anahtar gerçekler, atıflar, ilgililik skoru) döndürmek token bütçesini verimli kullanır.

- **(A) Yanlış:** Bütçe artırma pahalı ve yapısal sorunu çözmez — 15 kaynağa çıkınca yine aynı sorun.
- **(B) Yanlış:** Kapsamı daraltmak araştırma kalitesini düşürür.
- **(D) Yanlış:** Yanlış yerde çözüm. Sorun synthesis agent'ın çıktısında değil, girdisinde.

**Kapsanan kavram:** Task 5.1 — Upstream agent optimisation

---

### Soru 3 → **B**

**Açıklama:**

Müşteri kızgın ama sorun basit — sipariş bugün teslim edilecek. Duygu bazlı eskalasyon güvenilmez tetikleyici. Doğru: hayal kırıklığını kabul et, çözümü sun.

- **(A) Yanlış:** Duygu bazlı eskalasyon — kızgınlık vaka karmaşıklığıyla orantılı değil.
- **(C) Yanlış:** Model güven skoru güvenilmez eskalasyon tetikleyicisi.
- **(D) Yanlış:** "Sakin olun" müşteri deneyimini bozar ve sorunu çözmez.

**Kapsanan kavram:** Task 5.2 — Güvenilmez tetikleyiciler + Hayal kırıklığı nüansı

---

### Soru 4 → **C**

**Açıklama:**

İki ayrı sorun: (1) Rakip fiyat eşleştirmesi politikada tanımlanmamış — politika boşluğu, eskalasyon gerekir. (2) 4 müşteri eşleşmesi — sezgisel seçim değil, ek tanımlayıcı bilgi iste.

- **(A) Yanlış:** Politikayı geniş yorumlama yetkisi yok. Sezgisel müşteri seçimi hatalı eşleşme riski taşır.
- **(B) Yanlış:** Direkt reddetme politika boşluğu durumunda uygun değil — insan karar vermeli. Sezgisel müşteri seçimi yanlış.
- **(D) Yanlış:** Duygu bazlı karar güvenilmez. Rastgele müşteri seçimi kabul edilemez.

**Kapsanan kavram:** Task 5.2 — Politika boşluğu + Belirsiz müşteri eşleştirme

---

### Soru 5 → **B**

**Açıklama:**

Silent suppression anti-pattern'ı. Erişim hatasını `"success"` olarak işaretlemek tüm kurtarma mekanizmalarını engeller. Doğru: hata türünü (transient/ağ zaman aşımı), neyin denendiğini (PubMed sorgusu, parametreler) ve kısmi sonuçları yapılandırılmış olarak raporla.

- **(A) Yanlış:** Bu erişim hatası, geçerli boş sonuç değil. Ağ zaman aşımı = kaynağa erişilemedi.
- **(C) Yanlış:** Workflow termination anti-pattern'ı. 5 başarılı kaynağın sonuçlarını çöpe atar.
- **(D) Yanlış:** Sonsuz retry sistemi kilitler.

**Kapsanan kavram:** Task 5.3 — Silent suppression + Yapılandırılmış hata bağlamı

---

### Soru 6 → **C**

**Açıklama:**

Erişim hatası vs geçerli boş sonuç ayrımı. Status `"success"` → araç kaynağa başarıyla erişti. `results: []` → eşleşme bulamadı. Bu bir erişim hatası değil, geçerli boş sonuç. Tekrar denemek aynı sonucu verir.

- **(A) Yanlış:** Daha fazla retry aynı geçerli boş sonucu döndürür.
- **(B) Yanlış:** Parametreleri keyfi değiştirmek yanlış müşteriye ulaşma riski taşır. Önce müşteriden ek bilgi istemek gerekir.
- **(D) Yanlış:** Araç doğru çalışıyor — "eşleşme yok" geçerli bir cevap.

**Kapsanan kavram:** Task 5.3 — Erişim hatası vs geçerli boş sonuç

---

### Soru 7 → **B**

**Açıklama:**

İki sorun: (1) Bağlam bozulması — spesifik bulgulardan genel ifadelere geçiş. Çözüm: scratchpad + subagent delegasyonu. (2) Çökme kurtarma eksikliği. Çözüm: her agent manifest dosyasına durum yazar, koordinatör kurtarma sırasında yükler.

- **(A) Yanlış:** Büyük model bağlam bozulmasını geciktirir, çözmez. "Hiç kapatma" çökme durumunu görmezden gelir.
- **(C) Yanlış:** Prompt talimatı bağlam bozulmasını çözmez — bilgi fiziksel olarak düşmüş. Tam geçmişi veritabanında saklamak verbose veriyi geri yükler — bağlam bütçesini hemen tüketir.
- **(D) Yanlış:** Her saat yeniden başlatmak önceki bulguları kaybettirir — sürdürülebilir değil.

**Kapsanan kavram:** Task 5.4 — Bağlam bozulması + Crash recovery

---

### Soru 8 → **B**

**Açıklama:**

İki sorun: (1) Toplam metrik tuzağı — %96 genel doğruluk el yazısı belgelerdeki %35 hatayı gizliyor. Çözüm: belge türüne göre ayrı değerlendir, düşük performanslı türleri insan incelemesine yönlendir. (2) Kalibre edilmemiş güven — %85 güven = %58 doğruluk. Çözüm: etiketli doğrulama setleriyle kalibre et.

- **(A) Yanlış:** Eşik artırma kalibrasyon sorununu çözmez. El yazısı belgeleri çıkarmak veri kaybıdır.
- **(C) Yanlış:** Büyük model ne kalibrasyon ne belge türü performansını garanti eder.
- **(D) Yanlış:** %100 insan incelemesi gereksiz kaynak harcaması — %99.5 doğruluklu standart faturalar için gereksiz.

**Kapsanan kavram:** Task 5.5 — Toplam metrik tuzağı + Güven kalibrasyonu

---

### Soru 9 → **C**

**Açıklama:**

Zamansal farkındalık + çelişki yönetimi. IEA Mart 2024 ve GWEC Haziran 2024 — farklı ölçüm dönemleri farklı değerler verir. Bu çelişki değil, zamana bağlı değişim. Her iki değeri tarihlerle sun, zamansal bağlamı belirt.

- **(A) Yanlış:** "Son veri doğrudur" varsayımı her zaman geçerli değil — farklı dönemleri ölçüyorlar.
- **(B) Yanlış:** Ortalaması anlamlı değil — farklı dönemlerin karışımı.
- **(D) Yanlış:** Her iki kaynağı çıkarmak bilgi kaybı — zamansal bağlamla açıklanabilir.

**Kapsanan kavram:** Task 5.6 — Zamansal farkındalık + Çelişki yönetimi

---

### Soru 10 → **B**

**Açıklama:**

Her sorun farklı bir Domain 5 kavramıyla eşleşiyor:

| Sorun | Kavram | Çözüm |
|-------|--------|-------|
| 1. Sipariş no tekrar soruluyor | Task 5.1 — Progressive summarisation | Case facts bloğu |
| 2. Kızgın müşteriler gereksiz eskalasyon | Task 5.2 — Güvenilmez tetikleyici | Duygu bazlı → üç geçerli tetikleyici |
| 3. Tek hata tüm araştırmayı iptal ediyor | Task 5.3 — Workflow termination | Kısmi sonuçlarla devam + hata raporla |
| 4. Sentez raporunda belirsiz ifadeler | Task 5.6 — Atıf ölümü | Claim-source mappings |
| 5. Belge türüne göre test edilmemiş | Task 5.5 — Toplam metrik tuzağı | Tabakalı doğrulama |

- **(A) Yanlış:** Büyük model yapısal sorunları çözmez — her sorun farklı bir mimari düzeltme gerektirir.
- **(C) Yanlış:** Her çözüm yüzeysel — kök nedeni ele almaz (özetleme sıklığı, eskalasyon eşiği, retry sayısı, prompt talimatı, güven eşiği).
- **(D) Yanlış:** Aşırı çözümler — asla özetlememek, tüm müşterileri yönlendirmek, kaynağı çıkarmak, %100 insan incelemesi hepsi kaynak israfı ve veri kaybı.

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
| 1 | 5.1 — Case facts bloğu + Tool result trimming |
| 2 | 5.1 — Upstream agent optimisation |
| 3 | 5.2 — Güvenilmez tetikleyiciler + Hayal kırıklığı nüansı |
| 4 | 5.2 — Politika boşluğu + Belirsiz müşteri eşleştirme |
| 5 | 5.3 — Silent suppression + Yapılandırılmış hata bağlamı |
| 6 | 5.3 — Erişim hatası vs geçerli boş sonuç |
| 7 | 5.4 — Bağlam bozulması + Crash recovery |
| 8 | 5.5 — Toplam metrik tuzağı + Güven kalibrasyonu |
| 9 | 5.6 — Zamansal farkındalık + Çelişki yönetimi |
| 10 | 5.1–5.6 — Bütünleşik senaryo |
