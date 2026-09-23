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

### ✅ Açık (Sınavda Doğru Cevap)

```
"Yalnızca şu durumları işaretle:
- İddia edilen davranış gerçek kod davranışıyla çelişiyorsa
- Güvenlik açığı mevcutsa (enjeksiyon, kimlik doğrulama atlatma, açık veri sızıntısı)
- Açık mantık hatası varsa (yanlış döngü koşulu, null pointer riski)

Şunları ATLA:
- Küçük stil tercihleri (boşluk, isimlendirme gelenekleri)
- Ekip içi yerel kalıplar
- Performans iyileştirme önerileri (kritik darboğaz değilse)"
```

**Neden işe yarar:**
- Her kural bir **karar ağacı düğümüdür** — Claude ya işaretler ya da atlar, yorum yok
- Aynı kod her seferinde **tutarlı sonuç** üretir
- İnsan incelemesi gerektiren belirsiz alan yoktur

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
- *"Dokümantasyon kategorisi için güven eşiğini artır"* — Belirsiz, işe yaramaz
- *"Agent'ı tamamen yeniden eğit"* — Orantısız, yavaş çözüm

### ✅ Doğru Çözüm

**Yüksek yanlış pozitif kategorisini geçici olarak devre dışı bırak**, o kategorinin prompt'unu geliştirirken diğer kategorilere olan güveni koru.

```
Adımlar:
1. "Dokümantasyon eksiklikleri" kategorisini pipeline'dan kaldır
2. Güvenlik ve mantık kategorileri normal çalışmaya devam eder
3. Dokümantasyon için yeni, açık kriterler yaz (aşağıdaki gibi)
4. Küçük veri setinde test et → Yanlış pozitif oranı kabul edilebilir olunca geri ekle
```

**Temel prensip:** Güveni yeniden kazanmak için en hızlı yol, kötü performans gösteren bileşeni izole etmektir.

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

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Belirsiz talimatlar → tutarsız çıktı.** "Muhafazakâr ol" bir talimat değil, bir dilektir. |
| 2 | **Açık kriterler = karar ağacı.** Her kural "işaretle" veya "atla" şeklinde biner. |
| 3 | **Bir kategorideki güven kaybı tüm agent'ı etkiler.** Güven bütündür, kategoriye özel değil. |
| 4 | **Çözüm: Sorunlu kategoriyi devre dışı bırak**, geliştir, geri ekle. Tüm sistemi yavaşlatma. |
| 5 | **Ciddiyet kalibrasyonu için nesir değil, gerçek kod örnekleri kullan.** |
| 6 | **CI/CD context'inde yanlış negatiften yanlış pozitif daha az zararlıdır** — ama her ikisi de iyi kriterlerle minimize edilir. |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Bir güvenlik tarama agent'ı bazen gerçek güvenlik açıklarını raporlamıyor, bazen önemsiz uyarılar veriyor. Geliştirici şöyle yazıyor: *"Sadece gerçek güvenlik sorunlarını raporla, emin değilsen atla."* Bu yeterli mi?

**A)** Evet, "gerçek güvenlik sorunu" kavramı Claude için yeterince açıktır  
**B)** Hayır, "gerçek" ve "emin değilsen" öznel ifadeler; kategorik kriterler gerekir  
**C)** Hayır, ama güven eşiği parametresi eklenmesi sorunu çözer  
**D)** Evet, güvenlik domaininde Claude iyi kalibrasyon yapar  

**✅ Cevap: B**

*Açıklama:* "Gerçek güvenlik sorunu" ve "emin değilsen" ifadeleri öznel. Claude her çalıştırmada farklı bir bar belirleyebilir. Doğru yaklaşım: "SQL enjeksiyonu, kimlik bilgisi hardcoding, authentication bypass — bunları raporla. Deprecation uyarıları, performans önerileri — bunları atla." şeklinde kategorik kriterler.

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
