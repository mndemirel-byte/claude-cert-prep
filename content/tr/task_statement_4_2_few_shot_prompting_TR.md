# Task Statement 4.2: Few-Shot Prompting

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Few-shot prompting: Claude'a talimat vermek yerine **örnek göstermek.** Modele "şunu yap" demek yerine "işte böyle yapılır" demek.

Bu teknik, **tutarlılık problemlerini çözmek için en etkili yoldur.** Daha ayrıntılı talimatlar değil. Güven eşikleri değil. Daha büyük model değil. **Örnekler.**

Sınavın bu konudaki soruları sana şunu sorar: *"Hangi durumda few-shot kullanmalısın, hangi durumda başka bir şey?"* Cevabı bilmek için önce ne zaman işe yaradığını anlamalısın.

---

## Few-Shot'u Ne Zaman Kullanmalısın?

Üç tetikleyici senaryo — bunları ezberle:

### Tetikleyici 1: Tutarsız Biçimlendirme

```
Sorun: Aynı verilerle çalışıyorsun ama çıktı formatı her çalıştırmada değişiyor.
Bazen JSON üretiyor, bazen markdown tablo, bazen düz metin.
Talimat ekledin: "Her zaman JSON formatında çıktı ver." Hâlâ tutarsız.

Çözüm: Few-shot örneği — tam olarak istediğin formatta girdi/çıktı çifti göster.
```

### Tetikleyici 2: Belirsiz Durumlarda Tutarsız Karar

```
Sorun: Claude belirli durumlarda (yorumun hata mı yoksa stil mi olduğu)
farklı kararlar veriyor. Bazen işaretliyor, bazen atlıyor.

Çözüm: O belirsiz durumun örneğini göster + o durumda neden 
bir yol seçildiğinin gerekçesini açıkla.
```

### Tetikleyici 3: Mevcut Bilgiyi Çekememe

```
Sorun: Belgede bilgi var, ama model onu bulamıyor veya 
"null" / "bulunamadı" döndürüyor.

Çözüm: Benzer format belgeden başarılı çıkarım gösteren örnek.
Bu modele "bu yapıda bilgi bu şekilde bulunur" diyorunu öğretir.
```

---

## İyi Bir Few-Shot Örneği Nasıl Kurulur?

**Kural 1: 2-4 örnek yeterli.** 10 örnek gerekmez. 2-4 hedeflenen, iyi seçilmiş örnek dramatik fark yaratır.

**Kural 2: Belirsiz/zor durumları seç.** Kolay durumları örnekleme — zaten iyi yapıyor. Sınır vakaları, edge-case'ler, model'in kararsız kaldığı noktalar için örnek göster.

**Kural 3: Her örnekte gerekçeyi göster.** Model, örnekten genelleme yapar — sadece kalıp eşleştirme yapmaz. Gerekçe, modelin yeni, benzer durumlara transferini sağlar.

### Yapı

```
Örnek 1:
Girdi: [zor durum A]
Düşünce: [neden X seçildi, Y değil]
Çıktı: [beklenen format/karar]

Örnek 2:
Girdi: [zor durum B — alternatif varyant]
Düşünce: [neden bu sefer farklı karar]
Çıktı: [beklenen format/karar]
```

---

## Somut Örnek: Kod İnceleme Agent'ı

### Senaryo

Agent bir yorumu inceliyor ve "bu bir hata mı yoksa stil tercih mi?" kararını vermek zorunda.

### ❌ Talimat Tabanlı (Tutarsız)

```
"Eğer yorum yanlış davranış anlatıyorsa hata olarak işaretle.
Eğer sadece öneride bulunuyorsa atla."
```

Bu talimat işe yarıyor gibi görünüyor, ama Claude "yanlış davranış" eşiğini her seferinde farklı kalibre ediyor.

### ✅ Few-Shot (Tutarlı)

```
Örnek 1:
Kod:
  def calculate_discount(price, rate):
      # rate değeri 0-100 arasında olmalı
      return price * rate  # Aslında rate 0-1 bekliyor

Karar: HATA
Gerekçe: Yorum 0-100 beklendiğini söylüyor, kod 0-1 bekliyor.
İddia edilen davranış gerçek davranışla çelişiyor → işaretle.

---

Örnek 2:
Kod:
  def get_users():
      # Belki cache eklenebilir
      return db.query("SELECT * FROM users")

Karar: ATLA
Gerekçe: Bu bir öneri, kod davranışını yanlış anlatmıyor.
Gerçek vs. iddia edilen çelişki yok → atla.
```

Şimdi Claude yeni durumlarla karşılaşınca bu gerekçe kalıbından genelleme yapıyor.

---

## Halüsinasyon Azaltma Etkisi

Bu özellikle **belge çıkarımı (document extraction)** görevlerinde kritik.

### Problem

Çeşitli formatlarda faturalar işliyorsun:
- Bazıları satır içi atıflar kullanıyor: "Kalem A (Birim fiyat: 50 TL)"
- Bazıları tablo formatında: `| Kalem | Miktar | Fiyat |`
- Bazıları düz metin: "Toplamda 3 adet kalem, her biri 50 TL"

Model bazı formatlarda alanları doğru çekiyor, bazılarında "null" döndürüyor veya **değer uyduruyor** (hallucination).

### Çözüm: Format Çeşitliliği Gösteren Few-Shot

```
Örnek A (Satır içi format):
Belge: "Kalem A (Birim fiyat: 50 TL, Adet: 3)"
Çıkarım: {"kalem": "Kalem A", "birim_fiyat": 50, "adet": 3}

Örnek B (Tablo format):
Belge: "| Kalem A | 3 | 50 TL |"
Çıkarım: {"kalem": "Kalem A", "birim_fiyat": 50, "adet": 3}

Örnek C (Düz metin):
Belge: "3 adet Kalem A, her biri 50 TL"
Çıkarım: {"kalem": "Kalem A", "birim_fiyat": 50, "adet": 3}

Örnek D (Bilgi yok):
Belge: "Kalem A gönderildi."
Çıkarım: {"kalem": "Kalem A", "birim_fiyat": null, "adet": null}
```

**Kritik son örnek:** Bilgi yoksa null — uydurma. Bu örnek olmadan model genellikle değer uydurmayı tercih eder.

---

## Few-Shot vs. Diğer Teknikler — Karar Matrisi

| Sorun | Çözüm |
|-------|-------|
| Tutarsız format | Few-shot örnekleri |
| Belirsiz durumlarda yanlış karar | Few-shot + gerekçe |
| Mevcut bilgiyi bulamıyor (null döndürüyor) | Few-shot, benzer format |
| Sözdizimi hatalı JSON çıktısı | Tool_use ile JSON şeması |
| Anlamsal hatalar (yanlış değer ama geçerli JSON) | Validation-retry loop |
| Yüksek maliyet, gecikmeli görevler | Batch API |

Sınav bu tabloyu senin bildiğini varsayar. Her senaryo için doğru tekniği eşleştiremezsen kayıp puan.

---

## Sınavın Tuzağı: "Daha Fazla Talimat" Tuzağı

Sınav sana şunu sunar:

> *Model tutarsız kararlar veriyor. Talimatları daha ayrıntılı hale getiriyorsun. Yine tutarsız. Ne yapmalısın?*

**Yanlış cevaplar:**
- "Daha uzun, daha ayrıntılı talimatlar yaz" — Talimat miktarı çözüm değil
- "Model'in güven parametresini ayarla" — Böyle bir parametren yok
- "Daha büyük bir model kullan" — Sorun modelin kapasitesi değil

**Doğru cevap:**
- "Sorunlu durumlar için 2-4 few-shot örneği ekle, her örnekte gerekçeyi göster"

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Few-shot, tutarlılık sorunları için en etkili tekniktir.** Daha fazla talimat değil. |
| 2 | **2-4 hedeflenen örnek yeterli.** Edge-case'leri, belirsiz durumları seç. |
| 3 | **Her örnekte gerekçeyi göster.** Model genelleme yapar, kalıp ezberlemez. |
| 4 | **Belge çıkarımında format çeşitliliği gösteren örnekler halüsinasyonu azaltır.** |
| 5 | **"Bilgi yoksa null" örneği kritik** — bu olmadan model uydurur. |
| 6 | **Tutarsız biçimlendirme, belirsiz karar, boş alan → üç few-shot tetikleyicisi.** |

---

## Pratik Sorular ve Cevap Açıklamaları

### Soru 1

Bir belge çıkarım pipeline'ı geliştiriyorsun. Bazı belgeler için "ödeme tarihi" alanı doğru çekiliyor, bazıları için null dönüyor — ama tarih belgede mevcut. Hangi çözüm en etkilidir?

**A)** Şema tanımına "ödeme tarihi zorunlu alan" olarak ekle  
**B)** Modele "Eğer tarih varsa mutlaka çıkar" talimatı ver  
**C)** Farklı tarih formatlarını (DD/MM/YYYY, "15 Ocak 2024", "Jan 15") gösteren few-shot örnekleri ekle  
**D)** Retry loop ekle: null döndürünce tekrar dene  

**✅ Cevap: C**

*Açıklama:* Sorun, model'in farklı tarih formatlarını tanımamasıdır. Few-shot örnekleri "bu formatta bilgi şurada bulunur" haritasını öğretir. Zorunlu alan (A) fabrication'a yol açar. Talimat (B) zaten denendi, işe yaramadı. Retry (D) aynı başarısız yaklaşımı tekrar dener.

---

### Soru 2

Bir kod inceleme agent'ının kaç few-shot örneği kullanması önerilir?

**A)** 1 — az ama etkili  
**B)** 2-4 — hedeflenen örnekler  
**C)** 10-15 — kapsamlı kapsama  
**D)** 50+ — maksimum tutarlılık  

**✅ Cevap: B**

*Açıklama:* 2-4 iyi seçilmiş örnek dramatik iyileşme sağlar. Daha fazla örnek bağlam penceresini doldurur ve marjinal getiri azalır. 1 örnek genelleme için yetersiz. 10+ nadiren gereklidir.

---

### Soru 3

Few-shot örneklerinde gerekçe (reasoning) göstermenin amacı nedir?

**A)** Claude'un düşünce sürecini yavaşlatmak ve daha dikkatli karar vermesini sağlamak  
**B)** Claude'un yeni, benzer durumlara örneklerden genelleme yapabilmesini sağlamak  
**C)** Claude'un hangi cevabın "doğru" olduğunu doğrulamasını sağlamak  
**D)** Talimatların uzunluğunu kısaltmak  

**✅ Cevap: B**

*Açıklama:* Gerekçe, modele sadece "şu durumda şunu yap" değil, "neden şunu yapıyorsun" da öğretir. Bu sayede model hiç görmediği yeni durumları aynı gerekçeyi uygulayarak doğru sınıflandırabilir. Bu transferability'nin temelidir.

---

### Soru 4

Bir extraction pipeline'da belge yapıları çok çeşitli: tablolar, düz metin, iç içe listeler. Halüsinasyonu (uydurma) azaltmak için en iyi yaklaşım nedir?

**A)** Sıkı JSON şeması tanımla — tüm alanlar required  
**B)** Her format türü için ayrı model deployment  
**C)** Çeşitli belge yapılarından başarılı çıkarım gösteren few-shot örnekleri + "bilgi yoksa null" örneği  
**D)** Güvenlik eşiğini artır: modele "emin değilsen yazma" de  

**✅ Cevap: C**

*Açıklama:* Halüsinasyon genellikle model'in formattan çıkarım yapmak yerine "makul" bir değer uydurmasından kaynaklanır. Few-shot, modele doğru çıkarım stratejisini öğretir. "Bilgi yoksa null" örneği ise uydurma yerine null dönmeyi öğretir. Sıkı required şema (A) tam tersine uydurma yapmasına yol açar.
