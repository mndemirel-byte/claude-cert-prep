# Task Statement 4.1: Açık Kriterler (Explicit Criteria)

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Bir Claude agent'ını kod inceleme, güvenlik taraması veya belge analizi gibi görevler için yönlendirirken, en sık yapılan hata şu: **belirsiz, öznel talimatlar vermek.**

> *"Sadece önemli bulguları raporla."*
> *"Güvenden emin olmadığın durumlarda muhafazakâr ol."*
> *"Yalnızca yüksek güvenilirlikli sorunları işaretle."*

Bu talimatlar **çalışmaz.** Claude'un "önemli" veya "yüksek güvenilirlik" kavramını senin kastettiğin şekilde anlaması için hiçbir sebebi yoktur.

Doğru yaklaşım: **Kategorik, somut kriterler.** Claude'a "ne hissetmeli"ni değil, **ne yapması gerektiğini** söyle.

> **Sınav terimi:** Exam guide bu yanlış yaklaşıma **"confidence-based filtering"** (güven tabanlı filtreleme) der ve doğru yaklaşımı "specific categorical criteria" olarak adlandırır. Şıklarda "emin değilsen atla", "yüksek güvenilirlikli bulguları raporla", "muhafazakâr ol" gördüğünde bunların hepsi aynı distractor'dır: confidence-based filtering.

> **Resmi prompting ilkesi (altın kural):** Prompt'unu, görev hakkında çok az bağlamı olan bir meslektaşına göster ve uygulamasını iste. O karışırsa Claude da karışır. İstenen çıktı biçimi ve sınırlar konusunda spesifik ol; adımların sırası ya da eksiksizliği önemliyse numaralı adımlar kullan. (Kursun *Being clear and direct* / *Being specific* dersleri.)

---

## Belirsiz vs. Açık Kriterler — Yan Yana

### ❌ Belirsiz (Sınavda Yanlış Cevap)

```
"Yalnızca yüksek güvenilirlikli bulguları raporla. Emin olmadığın
durumlarda muhafazakâr olmayı tercih et. Önemsiz sorunları atla."
```

**Neden işe yaramaz:**
- "Yüksek güvenilirlik" sayısal bir eşik değildir, Claude her seferinde farklı bir bar belirler
- "Önemsiz" öznel bir kavramdır; Claude'un iş bağlamına erişimi yoktur
- Belirsiz talimatlar **tutarsız çıktı** üretir — aynı kod, farklı çalıştırmalarda farklı bulgular
- "Muhafazakâr ol" **kesinliği (precision) artırmaz** — model yalnızca daha az raporlar; yanlış pozitifleri değil, gerçek bulguları da atlar

### ✅ Açık (Sınavda Doğru Cevap)

```
"Yalnızca şu durumları işaretle:
- İddia edilen davranış gerçek kod davranışıyla çelişiyorsa
- Güvenlik açığı mevcutsa (enjeksiyon, kimlik doğrulama atlatma, açık veri sızıntısı)
- Açık mantık hatası varsa (yanlış döngü koşulu, null pointer riski)

Şunları ATLA:
- Küçük stil tercihleri (boşluk, isimlendirme gelenekleri)
- Ekip içi yerel kalıplar (local patterns — bu kod tabanında kabul edilmiş,
  dışarıdan hata gibi görünen ama bilinçli tercih olan kalıplar)
- Performans iyileştirme önerileri (kritik darboğaz değilse)"
```

**Neden işe yarar:**
- Her kural bir **karar ağacı düğümüdür** — Claude ya işaretler ya da atlar, yorum yok
- Aynı kod her seferinde **tutarlı sonuç** üretir
- İnsan incelemesi gerektiren belirsiz alan yoktur

**Sınav dili:** raporla → *bugs, security*; atla → *minor style, local patterns*. "Local patterns" (kabul edilebilir kod kalıpları) kavramı Task 4.2'de few-shot örneğiyle tekrar karşına çıkar: "acceptable code patterns vs genuine issues".

---

## Yanlış Pozitif Güven Problemi — Sınavın En Sevdiği Tuzak

Bu konuyu iyi anla: **sınav seni burada yanıltmaya çalışır.**

### Senaryo

Bir CI/CD pipeline'ında kod inceleme agent'ın var. Agent üç kategori raporluyor:
- **Güvenlik açıkları** → %95 doğruluk
- **Mantık hataları** → %90 doğruluk
- **Dokümantasyon eksiklikleri** → %40 doğruluk (çok fazla yanlış alarm)

Geliştiriciler "dokümantasyon eksiklikleri" bulgularının yarısının saçmalık olduğunu fark etti. Sonra ne oluyor?

**Asıl sorun:** Geliştiriciler artık **güvenlik açığı bulgularına da şüpheyle bakıyor.** Bir kategori güven kaybına uğradığında, tüm agent çıktısı güvenilmez görünüyor.

### Sınavın Sunduğu Yanlış Cevaplar

- *"Tüm kategorileri daha muhafazakâr yap"* — Hayır, bu gerçek sorunları kaçırır
- *"Dokümantasyon kategorisi için güven eşiğini artır"* — Belirsiz, işe yaramaz (confidence-based filtering)
- *"Agent'ı tamamen yeniden eğit"* — Orantısız, yavaş çözüm
- *"Yanlış pozitifler zararsızdır, geliştirici zaten eler; hepsini raporla"* — Hayır; yanlış pozitifin maliyeti tam olarak **güven kaybıdır** ve bu kayıp doğru kategorileri de işe yaramaz hale getirir

### ✅ Doğru Çözüm

**Yüksek yanlış pozitif kategorisini geçici olarak devre dışı bırak**, o kategorinin prompt'unu geliştirirken diğer kategorilere olan güveni koru.

```
Adımlar:
1. "Dokümantasyon eksiklikleri" kategorisini pipeline'dan kaldır
2. Güvenlik ve mantık kategorileri normal çalışmaya devam eder
3. Dokümantasyon için yeni, açık kriterler yaz (aşağıdaki gibi)
4. Etiketli bir test setinde ölç → Yanlış pozitif oranı kabul edilebilir olunca geri ekle
```

**Temel prensip:** Güveni yeniden kazanmak için en hızlı yol, kötü performans gösteren bileşeni izole etmektir.

### "Geri ekle" kararı nasıl verilir? — Eval

4. adım sezgiyle değil ölçümle verilir. Kursun *Prompt Evaluation* modülünün özü:

```
1. Etiketli test seti hazırla: 50–100 gerçek kod parçası, her biri için
   "bu kategoride gerçekten bulgu var mı?" cevabı insan tarafından verilmiş
2. Yeni kriterlerle agent'ı bu set üzerinde çalıştır
3. Yanlış pozitif / yanlış negatif oranını hesapla
   - Kod tabanlı grading: beklenen bulgu kümesi ile çıktıyı karşılaştır
   - Model tabanlı grading: ikinci bir Claude, bulguların doğruluğunu puanlar
4. Eşiği geçince kategoriyi geri aç; geçmezse kriterleri yeniden yaz, tekrar ölç
```

Aynı etiketli set Task 4.6'da güven eşiklerini kalibre etmek ve Task 4.5'te büyük batch öncesi prompt'u doğrulamak için de kullanılır — Domain 4'ün yatay teması budur: **değişikliği ölçmeden geri alma / ileri alma.**

---

## Ciddiyet Kalibrasyonu — Kod Örnekleriyle

Sınav seni burada da yanıltmaya çalışır: *"Ciddiyet seviyelerini tanımla"* derken sana **nesir açıklamalar** içeren cevaplar sunar.

Doğru cevap her zaman **gerçek kod örnekleri** içerir.

### ❌ Yanlış Kalibrasyon (Nesir Açıklama)

```
"Kritik: Sistemi çökertebilecek veya veri sızdırabilecek sorunlar.
Majör: Önemli işlevselliği etkileyen hatalar.
Minör: Küçük sorunlar."
```

**Neden işe yaramaz:** Claude'un "sistemi çökertebilecek" tanımı seninki ile örtüşmeyebilir.

### ✅ Doğru Kalibrasyon (Kod Örnekleriyle)

```python
# KRİTİK — her zaman raporla:
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL enjeksiyonu
    # → Doğrudan veri tabanı saldırısına açık

password = "admin123"  # Kod içinde sabit kimlik bilgisi
# → Kimlik bilgisi sızıntısı

# MAJÖR — raporla:
def calculate_total(items):
    total = 0
    for i in range(len(items) + 1):  # Off-by-one hatası
        total += items[i]

# MİNÖR — atla:
def getUserData():  # camelCase yerine snake_case olmalı
    pass  # Sadece stil; işlevselliği etkilemiyor
```

**Neden işe yarar:** Claude artık kendi yorum yapmıyor — "bu koda benziyor mu?" diye kontrol ediyor.

### Prompt'a nasıl gömülür? — `<example>` etiketleri

Yukarıdaki kod örnekleri gerçek bir prompt'ta talimattan ayrılması için XML etiketleriyle sarılır (resmi prompting kılavuzu; kursun *Structure with XML tags* dersi). Aksi halde model örneği "incelenecek kod" sanabilir.

```xml
<severity_examples>
<example severity="critical">
query = f"SELECT * FROM users WHERE id = {user_id}"
<why>Kullanıcı girdisi doğrudan SQL'e gömülüyor → enjeksiyon</why>
</example>
<example severity="major">
for i in range(len(items) + 1): total += items[i]
<why>Off-by-one: son iterasyon IndexError üretir</why>
</example>
<example severity="minor">
def getUserData(): ...
<why>Yalnızca isimlendirme stili; davranış doğru → ATLA</why>
</example>
</severity_examples>
```

Bu yapı Task 4.2'nin (few-shot) aynısıdır — ciddiyet kalibrasyonu aslında few-shot'ın bir özel hâlidir.

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Belirsiz talimatlar → tutarsız çıktı.** "Muhafazakâr ol" bir talimat değil, bir dilektir. Sınav adı: *confidence-based filtering*. |
| 2 | **Açık kriterler = karar ağacı.** Her kural "işaretle" veya "atla" şeklinde biner. Raporla: bugs, security. Atla: minor style, local patterns. |
| 3 | **Bir kategorideki güven kaybı tüm agent'ı etkiler.** Güven bütündür, kategoriye özel değil. |
| 4 | **Çözüm: Sorunlu kategoriyi devre dışı bırak**, geliştir, etiketli sette ölç, geri ekle. Tüm sistemi yavaşlatma. |
| 5 | **Ciddiyet kalibrasyonu için nesir değil, gerçek kod örnekleri kullan** — `<example>` etiketleri içinde. |
| 6 | **Yanlış pozitifin maliyeti güven, yanlış negatifin maliyeti kaçan hatadır.** Açık kriterler ikisini de düşürür; güven eşiği yalnızca birini diğerine takas eder. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Bir güvenlik tarama agent'ı bazen gerçek güvenlik açıklarını raporlamıyor, bazen önemsiz uyarılar veriyor. Geliştirici şöyle yazıyor: *"Sadece gerçek güvenlik sorunlarını raporla, emin değilsen atla."* Bu yeterli mi?

**A)** Evet, "gerçek güvenlik sorunu" kavramı Claude için yeterince açıktır  
**B)** Hayır, "gerçek" ve "emin değilsen" öznel ifadeler; kategorik kriterler gerekir  
**C)** Hayır, ama prompt'a bir güven eşiği eklemek ("%80'in altındaysa raporlama") sorunu çözer  
**D)** Evet, güvenlik domaininde Claude iyi kalibrasyon yapar  

**✅ Cevap: B**

*Açıklama:* "Gerçek güvenlik sorunu" ve "emin değilsen" ifadeleri öznel. Claude her çalıştırmada farklı bir bar belirleyebilir. Doğru yaklaşım: "SQL enjeksiyonu, kimlik bilgisi hardcoding, authentication bypass — bunları raporla. Deprecation uyarıları, performans önerileri — bunları atla." şeklinde kategorik kriterler. (C) confidence-based filtering'in yüzdeli hâlidir — modelin kendi güven tahmini kalibre değildir, eşik yalnızca daha az raporlamaya yol açar; hem "gerçek açık kaçıyor" hem "önemsiz uyarı" sorununu aynı anda çözemez.

---

### Soru 2

Bir pipeline'da üç analiz kategorisi var: güvenlik (%92 doğruluk), performans (%88 doğruluk), kod stili (%35 doğruluk). Geliştiriciler güvenlik bulgularına güveni kaybetmeye başlıyor. En iyi eylem nedir?

**A)** Tüm kategorilerin eşiklerini %90 üstüne çek  
**B)** Kod stili kategorisini geçici olarak devre dışı bırak, diğerlerini çalıştırmaya devam et  
**C)** Agent'ı daha büyük bir modelle değiştir  
**D)** Üç kategori için de daha fazla örnek veri topla  

**✅ Cevap: B**

*Açıklama:* Sorun kod stili kategorisinin güveni zehirlemesi. Çözüm izolasyon: kötü kategoriyi kaldır, iyi kategoriler çalışmaya devam etsin. Eşik çekmek (A) gerçek sorunları kaçırır. Model değiştirmek (C) orantısız. Daha fazla veri toplamak (D) kök nedeni çözmez — problem prompt kriterleri.

---

### Soru 3

Ciddiyet seviyeleri için en etkili tanım hangisidir?

**A)** "Kritik: Sistem güvenliğini tehdit eden sorunlar. Majör: Önemli işlevselliği bozan hatalar."  
**B)** Somut kod örnekleriyle her seviyeyi gösteren şema: "Kritik: `query = f"SELECT * FROM users WHERE id = {user_id}"` gibi enjeksiyon kalıpları"  
**C)** Her seviye için yüzde güven eşiği: "Kritik: %95+, Majör: %80-95"  
**D)** Geliştiricilerin past review notlarından derlenen genel açıklamalar  

**✅ Cevap: B**

*Açıklama:* Nesir açıklamalar (A) yoruma açıktır. Güven eşikleri (C) tutarsız kalibrasyon sağlar. Past notlar (D) yapılandırılmamıştır. Gerçek kod örnekleri Claude'a "bu koda benziyor mu?" sorusunu sordurur — yorum yok, kalıp eşleştirme var.

---

### Soru 4

Bir agent'a şu talimat veriliyor: *"Yalnızca yüksek öncelikli sorunları raporla."* Hangi sorun ortaya çıkar?

**A)** Agent çalışmaz; "yüksek öncelik" geçerli bir parametre değil  
**B)** Agent her şeyi raporlar, filtreleme yapmaz  
**C)** "Yüksek öncelik" öznel olduğu için çalıştırmalar arasında tutarsız sonuçlar üretir  
**D)** Agent yanlış bir hata mesajı döndürür  

**✅ Cevap: C**

*Açıklama:* Claude çalışır ve filtreleme yapar, ama "yüksek öncelik" eşiğini her seferinde farklı belirler. Aynı kod tabanı farklı bulgular üretebilir. Tutarsızlık, belirsiz kriterlerin asıl maliyetidir.

---

### Soru 5

Bir kod inceleme agent'ına geçen ay *"emin değilsen raporlama"* talimatı eklendi. Yanlış pozitifler azaldı, ama geliştiriciler artık production'da çıkan iki SQL enjeksiyonunun PR incelemesinde hiç işaretlenmediğini fark etti. Ne olmuş, ne yapılmalı?

**A)** Talimat işe yaradı; enjeksiyonlar için ayrı bir "her zaman raporla" istisnası eklenmeli, gerisi aynı kalsın  
**B)** Güven eşiği yanlış pozitifle birlikte gerçek bulguları da eledi; talimat kaldırılıp yerine kategorik kriterler (enjeksiyon, credential, auth bypass → raporla; stil, öneri → atla) konmalı  
**C)** Model kapasitesi yetersiz; daha büyük model kullanılmalı  
**D)** Talimat "emin değilsen insan incelemesine yönlendir" olarak değiştirilmeli  

**✅ Cevap: B**

*Açıklama:* Confidence-based filtering'in klasik sonucu: model "emin olma" barını kendi belirler ve yalnızca daha az raporlar — hangi bulguların gittiğini kontrol edemezsin. (A) semptomu yamalar; her yeni kaçan hata için yeni istisna gerekir ve altta yatan belirsiz talimat durur. (C) sorun kapasite değil, kriter. (D) "emin değilsen" ifadesini korur; yönlendirme (Task 4.6) kategorik kriterlerin *üstüne* konur, yerine değil.
