# Task Statement 4.2: Few-Shot Prompting

## Domain 4 — Prompt Engineering ve Yapılandırılmış Çıktı (Sınavın %20'si)

---

## Temel Fikir

Few-shot prompting: Claude'a talimat vermek yerine **örnek göstermek.** Modele "şunu yap" demek yerine "işte böyle yapılır" demek.

Bu teknik, **tutarlılık problemlerini çözmek için en etkili yoldur.** Daha ayrıntılı talimatlar değil. Güven eşikleri değil. Daha büyük model değil. **Örnekler.**

Exam guide'ın tam cümlesi: *"Few-shot examples as the most effective technique for achieving consistently formatted, actionable output **when detailed instructions alone produce inconsistent results**."* — yani few-shot, talimatın *yerine* değil, talimat yetmediğinde *üstüne* gelir.

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

**Sınavın format örneği:** kod inceleme bulgusu için dört alan — *location, issue, severity, suggested fix*. Bu dört alanı gösteren tek bir örnek, "bulguları yapılandırılmış ver" talimatından daha etkilidir:

```xml
<example>
location: src/auth.py:42
issue: Kullanıcı girdisi f-string ile SQL sorgusuna gömülüyor
severity: critical
suggested_fix: Parametreli sorgu kullan: cursor.execute("... WHERE id = %s", (user_id,))
</example>
```

### Tetikleyici 2: Belirsiz Durumlarda Tutarsız Karar

```
Sorun: Claude belirli durumlarda (yorumun hata mı yoksa stil mi olduğu)
farklı kararlar veriyor. Bazen işaretliyor, bazen atlıyor.

Çözüm: O belirsiz durumun örneğini göster + o durumda neden 
bir yol seçildiğinin gerekçesini açıkla.
```

**Sınavın belirsiz-durum örnekleri** (bu kelimelerle gelir):
- *Tool selection for ambiguous requests* — "kullanıcı 'raporu güncelle' dedi: dosya düzenleme aracı mı, e-posta aracı mı?" → örnekle hangi ipucunun hangi aracı seçtirdiğini göster (Domain 1/2 ile bağ)
- *Branch-level test coverage gaps* — "bu `if/else`'in yalnızca bir dalı test edilmiş; bu bir bulgu mu?" → örnekle "evet, dal kapsaması eksik → bulgu; ama sadece log satırı içeren dal → atla" göster
- *Acceptable code patterns vs genuine issues* — kod tabanında bilinçli olarak kullanılan, dışarıdan hata gibi görünen kalıplar (Task 4.1'deki "local patterns"); örnek olmadan model bunları her seferinde yeniden "keşfeder"

### Tetikleyici 3: Mevcut Bilgiyi Çekememe

```
Sorun: Belgede bilgi var, ama model onu bulamıyor veya 
"null" / "bulunamadı" döndürüyor.

Çözüm: Benzer format belgeden başarılı çıkarım gösteren örnek.
Bu modele "bu yapıda bilgi bu şekilde bulunur" diyorunu öğretir.
```

**Sınavın belge-yapısı örnekleri:** *inline citations vs bibliographies* (atıf metin içinde mi, kaynakçada mı), *methodology sections vs embedded details* (yöntem ayrı bölümde mi, paragrafa gömülü mü), *narrative descriptions vs structured tables*, *informal measurements* ("yaklaşık üç kilo", "bir avuç" → sayısal alan). Exam guide'ın dünyası akademik/bilimsel belge; bu dokümandaki fatura örnekleri aynı ilkenin iş dünyası hâlidir.

### "null" üçlüsü — hangi null hangi statement'ın işi?

Sınavın en ince ayrımı. Aynı belirti ("alan null döndü"), üç farklı teşhis:

| Durum | Belirti | Doğru araç | Statement |
|-------|---------|------------|-----------|
| Bilgi belgede **var**, model bulamıyor | null / boş alan | Few-shot: benzer yapıdan başarılı çıkarım örneği | 4.2 |
| Bilgi belgede **yok**, model uyduruyor | makul görünen ama sahte değer | Şemada alanı nullable yap | 4.3 |
| Bilgi belgede **yok**, retry gönderiliyor | tekrar null / tekrar uydurma | Retry işe yaramaz; nullable + insan | 4.4 |
| Bilgi **başka bir belgede** (ek, referans) | null | Eksik belgeyi bağlama ekle, sonra retry | 4.4 |

---

## İyi Bir Few-Shot Örneği Nasıl Kurulur?

**Kural 1: 2-4 örnek yeterli.** 10 örnek gerekmez. 2-4 hedeflenen, iyi seçilmiş örnek dramatik fark yaratır.

> **Sınav vs. resmi kılavuz:** Exam guide "2-4 targeted few-shot examples" der → **sınav cevabı 2-4**. Claude'un resmi prompting kılavuzu "3-5 examples for best results" der. İkisi de aynı şeyi söylüyor: *az ama iyi seçilmiş*; 10+ hiçbir kaynakta önerilmiyor.

**Kural 2: Belirsiz/zor durumları seç — ve çeşitli olsun.** Kolay durumları örnekleme — zaten iyi yapıyor. Sınır vakaları, edge-case'ler, model'in kararsız kaldığı noktalar için örnek göster. Resmi kılavuzun uyarısı: örnekler yeterince **çeşitli** değilse Claude *istemediğin* kalıpları öğrenir — her örnekteki fatura numarası "INV-" ile başlıyorsa bunu kural sanır; her "HATA" örneği bir yorum satırıysa yorum olmayan hataları atlar.

**Kural 3: Her örnekte gerekçeyi göster.** Model, örnekten genelleme yapar — sadece kalıp eşleştirme yapmaz. Gerekçe, modelin yeni, benzer durumlara transferini sağlar. Resmi kılavuz gerekçeyi örneklerin içinde `<thinking>` etiketiyle göstermeyi önerir; model bu akıl yürütme stilini kendi thinking'ine genelleştirir.

**Kural 4: Örnekleri `<example>` etiketleriyle sar.** Tek örnek `<example>…</example>`, birden çok örnek `<examples>` içinde. Bu, Claude'un örneği *talimattan* ve *incelenecek girdiden* ayırt etmesini sağlar. Etiketsiz örnek en sık görülen hata: model örneği görevin bir parçası sanır ve örneğe cevap verir.

### Yapı

```xml
<examples>
<example>
<input>[zor durum A]</input>
<thinking>[neden X seçildi, Y değil]</thinking>
<output>[beklenen format/karar]</output>
</example>

<example>
<input>[zor durum B — alternatif varyant]</input>
<thinking>[neden bu sefer farklı karar]</thinking>
<output>[beklenen format/karar]</output>
</example>
</examples>
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

```xml
<examples>
<example>
<input>
  def calculate_discount(price, rate):
      # rate değeri 0-100 arasında olmalı
      return price * rate  # Aslında rate 0-1 bekliyor
</input>
<thinking>Yorum 0-100 beklendiğini söylüyor, kod 0-1 bekliyor.
İddia edilen davranış gerçek davranışla çelişiyor → işaretle.</thinking>
<output>
location: pricing.py:1
issue: Yorum rate için 0-100 aralığı vaat ediyor, kod 0-1 bekliyor
severity: major
suggested_fix: Yorumu "rate 0-1 arasında" olarak düzelt veya rate/100 uygula
</output>
</example>

<example>
<input>
  def get_users():
      # Belki cache eklenebilir
      return db.query("SELECT * FROM users")
</input>
<thinking>Bu bir öneri, kod davranışını yanlış anlatmıyor.
Gerçek vs. iddia edilen çelişki yok → atla.</thinking>
<output>ATLA</output>
</example>
</examples>
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

```xml
<examples>
<example format="satır içi">
<document>Kalem A (Birim fiyat: 50 TL, Adet: 3)</document>
<thinking>Parantez içinde "Birim fiyat: 50 TL" → birim_fiyat=50; "Adet: 3" → adet=3</thinking>
<output>{"kalem": "Kalem A", "birim_fiyat": 50, "adet": 3}</output>
</example>

<example format="tablo">
<document>| Kalem A | 3 | 50 TL |</document>
<thinking>Sütun sırası başlıktan: Kalem | Miktar | Fiyat → 2. sütun adet, 3. sütun birim fiyat</thinking>
<output>{"kalem": "Kalem A", "birim_fiyat": 50, "adet": 3}</output>
</example>

<example format="düz metin">
<document>3 adet Kalem A, her biri 50 TL</document>
<thinking>"her biri 50 TL" birim fiyattır, toplam değil</thinking>
<output>{"kalem": "Kalem A", "birim_fiyat": 50, "adet": 3}</output>
</example>

<example format="bilgi yok">
<document>Kalem A gönderildi.</document>
<thinking>Belgede fiyat ve adet geçmiyor → uydurma, null döndür</thinking>
<output>{"kalem": "Kalem A", "birim_fiyat": null, "adet": null}</output>
</example>
</examples>
```

**Kritik son örnek:** Bilgi yoksa null — uydurma. Bu örnek olmadan model genellikle değer uydurmayı tercih eder.

**Halüsinasyonu azaltan asıl şey:** yalnızca "başarılı çıkarım" göstermek değil, `<thinking>` satırında **belgedeki kanıtı** göstermek ("2. sütun adet"). Model, değeri belgede *bulma* alışkanlığını öğrenir; bulamayınca null der.

---

## Few-Shot vs. Diğer Teknikler — Karar Matrisi

| Sorun | Çözüm |
|-------|-------|
| Tutarsız format | Few-shot örnekleri |
| Belirsiz durumlarda yanlış karar | Few-shot + gerekçe |
| Mevcut bilgiyi bulamıyor (null döndürüyor) | Few-shot, benzer format |
| Sözdizimi hatalı JSON çıktısı | Tool_use ile JSON şeması (4.3) |
| Anlamsal hatalar (yanlış değer ama geçerli JSON) | Validation-retry loop (4.4) |
| Bilgi belgede yok, model uyduruyor | Nullable şema alanı (4.3) |
| Yüksek maliyet, gecikmeli görevler | Batch API (4.5) |

Sınav bu tabloyu senin bildiğini varsayar. Her senaryo için doğru tekniği eşleştiremezsen kayıp puan.

**Few-shot'ın yapamadığı:** few-shot *format ve karar tutarlılığı* sağlar, **doğruluk garantisi vermez**. Model yine bozuk JSON üretebilir (→ tool_use), toplamı yanlış hesaplayabilir (→ validation). Sınav "tutarlılık" kelimesini görünce few-shot, "garanti" kelimesini görünce tool_use, "doğrulama" kelimesini görünce retry bekler.

**Maliyet notu:** her örnek token'dır. Sabit few-shot bloğu (system prompt + örnekler + şema) tüm isteklerde aynıysa **prompt caching** ile önbelleklenir; batch indirimiyle (4.5) birlikte kullanılabilir. (Domain 5 ile bağ.)

---

## Sınavın Tuzağı: "Daha Fazla Talimat" Tuzağı

Sınav sana şunu sunar:

> *Model tutarsız kararlar veriyor. Talimatları daha ayrıntılı hale getiriyorsun. Yine tutarsız. Ne yapmalısın?*

**Yanlış cevaplar:**
- "Daha uzun, daha ayrıntılı talimatlar yaz" — Talimat miktarı çözüm değil
- "Emin değilsen atla de / güven eşiği koy" — Confidence-based filtering (4.1); böyle bir API parametresi de yok
- "Daha büyük bir model kullan" — Sorun modelin kapasitesi değil

**Doğru cevap:**
- "Sorunlu durumlar için 2-4 few-shot örneği ekle, her örnekte gerekçeyi göster"

---

## Key Takeaway Listesi

| # | Temel Çıkarım |
|---|---------------|
| 1 | **Few-shot, talimat yetmediğinde tutarlılık için en etkili tekniktir.** Daha fazla talimat değil. |
| 2 | **2-4 hedeflenen örnek yeterli** (sınav; resmi kılavuz 3-5). Edge-case'leri, belirsiz durumları seç; **çeşitli** olsun, istemeden kalıp öğretme. |
| 3 | **Her örnekte gerekçeyi göster** (`<thinking>`). Model genelleme yapar, kalıp ezberlemez. |
| 4 | **Örnekleri `<example>` / `<examples>` etiketleriyle sar** — talimattan ve girdiden ayrılsın. |
| 5 | **Belge çıkarımında format çeşitliliği + belgedeki kanıt gösteren örnekler halüsinasyonu azaltır.** |
| 6 | **"Bilgi yoksa null" örneği kritik** — bu olmadan model uydurur. Bilgi *var* ama null → few-shot; bilgi *yok* → nullable şema (4.3). |
| 7 | **Tutarsız biçimlendirme, belirsiz karar, boş alan → üç few-shot tetikleyicisi.** Few-shot doğruluk garantisi vermez → tool_use / validation. |

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

*Açıklama:* 2-4 iyi seçilmiş örnek dramatik iyileşme sağlar (exam guide; resmi prompting kılavuzu 3-5 der — aynı mertebe). Daha fazla örnek bağlam penceresini doldurur ve marjinal getiri azalır. 1 örnek genelleme için yetersiz ve tek kalıbı ezberletir. 10+ nadiren gereklidir.

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

---

### Soru 5

Bir kod inceleme agent'ına 4 few-shot örneği eklendi; dördü de `TODO` yorumu içeren kod parçalarında "HATA" kararı gösteriyor. Agent şimdi `TODO` içermeyen bariz hataları atlıyor, `TODO` içeren doğru kodu ise işaretliyor. Sorun nedir?

**A)** 4 örnek çok fazla; 2'ye düşürülmeli  
**B)** Örnekler çeşitli değil; model istemeden "TODO = hata" kalıbını öğrendi. `TODO`'suz hata ve `TODO`'lu doğru kod örnekleri eklenmeli  
**C)** Örneklerde gerekçe eksik; gerekçe eklenince model TODO'yu yok sayar  
**D)** Few-shot bu görev için uygun değil; talimat tabanlı yaklaşıma dönülmeli  

**✅ Cevap: B**

*Açıklama:* Resmi kılavuzun "diverse" uyarısı: örnekler tek bir yüzeysel özelliği paylaşıyorsa model o özelliği karar kuralı sanır. Çözüm örnek sayısı değil (A), örnek **çeşitliliği**dir. Gerekçe (C) yardımcı olur ama dört örnek de aynı yüzeysel ipucunu taşıdığı sürece kalıp kırılmaz. (D) tekniği değil, örnek seçimini suçlamak gerekir.
