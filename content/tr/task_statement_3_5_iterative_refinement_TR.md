# Task Statement 3.5: Yinelemeli İyileştirme (Iterative Refinement)

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code'a bir görev verdin, sonuç beklediğin gibi değil. Nasıl iyileştirirsin? Bu task statement, Claude Code'un çıktısını **sistematik olarak** iyileştirme tekniklerini öğretiyor.

---

## Teknik Hiyerarşisi

Üç temel teknik var — en etkiliden en az etkiliye doğru sıralanmış:

### 1. Somut Girdi/Çıktı Örnekleri (En Etkili)

2-3 örnek göster — "bu girdiyi ver, bu çıktıyı al." Düzyazı açıklamaları her zaman yener.

**Neden en etkili?** Claude Code örneklerden genelleme yapmada, düzyazı açıklamalardan çıkarım yapmaktan çok daha başarılıdır.

**Kural:** Düzyazı açıklamaları tutarsız yorumlanıyorsa, somut girdi/çıktı örneklerine geç.

#### Kötü Yaklaşım (Düzyazı)
```
"Fonksiyon isimlerini daha açıklayıcı yap ve camelCase kullan."
```

#### İyi Yaklaşım (Somut Örnekler)
```
Örnek 1:
  Girdi:  function proc(d) { ... }
  Çıktı:  function processUserData(userData) { ... }

Örnek 2:
  Girdi:  function calc(a, b) { ... }
  Çıktı:  function calculateTotalPrice(basePrice, taxRate) { ... }

Örnek 3:
  Girdi:  function chk(u) { ... }
  Çıktı:  function checkUserPermissions(userId) { ... }
```

Model bu örneklerden desen çıkarır ve tutarlı şekilde uygular.

### 2. Test Güdümlü İterasyon (Test-Driven Iteration)

Önce testleri yaz, başarısız testleri Claude Code'la paylaş, iyileştirmeyi yönlendir.

**Nasıl çalışır:**
1. Beklenen davranışı tanımlayan testler yaz
2. Claude Code'un ürettiği kodu testlere karşı çalıştır
3. Başarısız testleri Claude Code'a göster
4. Claude Code testleri geçene kadar kodu iyileştirir

**Avantajı:** Başarı kriteri net ve nesnel. "İyi mi kötü mü" tartışması yok — testler ya geçer ya geçmez.

### 3. Mülakat Deseni (Interview Pattern)

Claude Code'un uygulamadan önce **sana sorular sormasını** iste.

**Ne zaman kullanılır:** Aşina olmadığın bir alanda çalışırken. Claude Code'un soruları, tek başına düşünerek kaçıracağın noktaları yüzeye çıkarır.

**Nasıl çalışır:**
```
"Bu veritabanı şemasını tasarlamadan önce, bana gereksinimler hakkında 
sorular sor. Cevaplarıma göre tasarımı yap."
```

Claude Code şu tür sorular sorar:
- "Çok-çok ilişki gerekli mi?"
- "Yumuşak silme (soft delete) kullanılacak mı?"
- "Hangi alanlar indekslenmeli?"

Bu sorular, sen tasarıma başlamadan önce eksik gereksinimleri ortaya çıkarır.

---

## Geri Bildirim Zamanlama Stratejisi

### Toplu Geri Bildirim (Batch) — Tek Mesajda

**Ne zaman:** Düzeltmeler **birbiriyle etkileşiyor** — birini değiştirmek diğerlerini etkiliyor.

Örnek: "Fonksiyon adını değiştir, parametreleri güncelle ve çağrılan yerleri düzelt" — bunlar birbirine bağlı, tek mesajda ver.

### Sıralı Geri Bildirim (Sequential) — Ayrı Mesajlarda

**Ne zaman:** Sorunlar **birbirinden bağımsız** — birini düzeltmek diğerini etkilemiyor.

Örnek: "Dosya 1'deki girintiyi düzelt" ve "Dosya 2'deki hata mesajını güncelle" — bağımsız sorunlar, ayrı mesajlarda ver.

---

## Örnek Bazlı İletişim — Düzyazı Başarısız Olduğunda

Bu senaryo sınavda doğrudan test ediliyor:

> Bir developer bir kod dönüşümünü düzyazı ile açıklıyor. Claude Code her seferinde farklı yorumluyor.

**Çözüm:** Düzyazıyı bırak, somut girdi/çıktı örneklerine geç.

**Neden?** Düzyazı belirsizdir — "daha açıklayıcı" ne demek? "Daha temiz" ne demek? Herkes farklı yorumlar. Örnekler ise kesindir — "bu girdiyi ver, bu çıktıyı al." Yorum farkı yok.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Somut girdi/çıktı örnekleri | En etkili teknik — 2-3 before/after örneği göster |
| Test güdümlü iterasyon | Testleri yaz, başarısız testleri paylaş, iyileştirmeyi yönlendir |
| Mülakat deseni | Claude Code'un sorular sormasını iste — eksik gereksinimleri ortaya çıkarır |
| Toplu geri bildirim | Etkileşimli düzeltmeler → tek mesajda |
| Sıralı geri bildirim | Bağımsız düzeltmeler → ayrı mesajlarda |
| Düzyazı başarısız olduğunda | Somut örneklere geç — model örneklerden daha iyi genelleme yapar |
| Sınav tuzağı | "Düzyazı açıklaması tutarsız yorumlanıyor" → cevap: somut örnekler |

---

## Pratik Senaryo 1

> Bir developer, Claude Code'a şu talimatı veriyor:
>
> *"Fonksiyonları daha okunaklı yap ve modern JavaScript syntax'ına çevir."*
>
> Claude Code her seferinde farklı sonuç üretiyor — bazen arrow function kullanıyor, bazen kullanmıyor; bazen destructuring yapıyor, bazen yapmıyor. Tutarsız.
>
> **İlk denenmesi gereken teknik hangisidir?**
>
> **A)** System prompt'a daha detaylı düzyazı açıklama ekle — neyin "modern" olduğunu uzun uzun açıkla.
>
> **B)** 2-3 somut girdi/çıktı örneği ver — "bu eski kodu ver, bu modern koda dönüştür" şeklinde before/after örnekleri.
>
> **C)** Claude Code'u farklı bir modelle çalıştır — daha akıllı model tutarlı olur.
>
> **D)** Her dönüşüm için ayrı bir komut oluştur — arrow function komutu, destructuring komutu.

### Doğru Cevap: B

**Neden B doğru:** Düzyazı açıklama tutarsız yorumlanıyor — bu tam olarak somut örneklere geçme sinyali. 2-3 before/after örneği model'in desen çıkarmasını ve tutarlı uygulamasını sağlar. "Modern" ne demek belirsiz — örnekler kesindir.

**Neden A yanlış:** Daha fazla düzyazı, daha fazla belirsizlik. Düzyazı zaten tutarsız yorumlanıyor — daha uzun düzyazı sorunu çözmez, karmaşıklık ekler.

**Neden C yanlış:** Sorun modelin zekası değil, talimatın belirsizliği. Farklı model de belirsiz talimatı farklı yorumlar.

**Neden D yanlış:** Aşırı mühendislik. Her dönüşüm türü için ayrı komut oluşturmak karmaşıklık yaratır. 2-3 örnek çok daha basit ve etkili.

---

## Pratik Senaryo 2

> Bir developer, Claude Code'un ürettiği bir API endpoint'ini iyileştirmek istiyor. İki sorun var:
>
> 1. Hata yönetimi (error handling) eksik — bu, yanıt formatını ve kontrol akışını etkiliyor
> 2. README'deki API dokümantasyonu güncel değil — endpoint'in açıklaması yanlış
>
> **Geri bildirimi nasıl vermeli?**
>
> **A)** İki sorunu tek mesajda ver — toplu geri bildirim.
>
> **B)** Önce hata yönetimini düzelt (tek mesaj), sonra dokümantasyonu güncelle (ayrı mesaj) — sıralı geri bildirim.
>
> **C)** İkisini de düzyazı ile açıkla ve Claude Code'un önceliği kendisi belirlemesini iste.
>
> **D)** Hata yönetimi için test yaz, dokümantasyon için örnek ver — farklı teknikler kullan.

### Doğru Cevap: B

**Neden B doğru:** İki sorun birbirinden bağımsız — hata yönetimi kodla ilgili, dokümantasyon README ile ilgili. Birini düzeltmek diğerini etkilemiyor. Bağımsız sorunlar → sıralı geri bildirim. Önce hata yönetimini düzelt (bu, yanıt formatını ve akışı etkileyeceği için önce yapılmalı), sonra güncellenen koda göre dokümantasyonu düzelt.

**Neden A yanlış:** Toplu geri bildirim etkileşimli düzeltmeler içindir — birini değiştirmek diğerini etkiliyorsa. Burada sorunlar bağımsız.

**Neden C yanlış:** Önceliklendirmeyi Claude Code'a bırakmak tutarsız sonuçlar yaratabilir. Developer olarak sen akışı yönlendirmelisin.

**Neden D yanlış:** Farklı teknikler kullanmak yanlış değil ama soru geri bildirim zamanlamasını soruyor. Kök mesele: bağımsız sorunlar → sıralı. Bu, teknik seçiminden bağımsız doğru zamanlama.
