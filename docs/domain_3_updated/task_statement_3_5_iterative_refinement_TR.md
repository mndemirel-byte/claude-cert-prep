# Task Statement 3.5: Yinelemeli İyileştirme (Iterative Refinement)

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code'a bir görev verdin, sonuç beklediğin gibi değil. Nasıl iyileştirirsin? Bu task statement, Claude Code'un çıktısını **sistematik olarak** iyileştirme tekniklerini öğretiyor.

Sınav "hangi teknik en iyi?" diye sormaz; "**bu problem için** hangi teknik?" diye sorar. Bu yüzden teknikleri sıralamak yerine **problem → teknik** eşlemesi olarak öğren.

---

## Problem → Teknik Eşlemesi

| Belirti | Teknik | Exam guide'ın ifadesi |
|---|---|---|
| Düzyazı talimat **tutarsız yorumlanıyor** — her seferinde farklı sonuç | **Somut girdi/çıktı örnekleri** (2–3 before/after) | "the most effective way to communicate expected transformations **when prose descriptions are interpreted inconsistently**" |
| Davranış **doğrulanabilir**; edge case'ler kaçıyor | **Test güdümlü iterasyon** | "writing test suites first, then iterating by sharing test failures" |
| **Aşina olmadığın alan**; gereksinimlerde bilmediğin boşluklar var | **Mülakat deseni** | "having Claude ask questions to surface considerations the developer may not have anticipated **before implementing**" |
| Birden fazla düzeltme var | **Toplu vs sıralı** geri bildirim | "single message (interacting problems) versus sequentially (independent problems)" |
| Aynı konuda **iki düzeltmeden sonra** hâlâ yanlış | **`/clear` + daha iyi ilk prompt** | (best practices: "correcting over and over" anti-pattern'i) |

---

## Teknik 1: Somut Girdi/Çıktı Örnekleri

2-3 örnek göster — "bu girdiyi ver, bu çıktıyı al." Düzyazı açıklamaları tutarsız yorumlandığında bu, en etkili tekniktir.

**Neden etkili?** Düzyazı belirsizdir — "daha açıklayıcı" ne demek? "Daha temiz" ne demek? Herkes farklı yorumlar. Örnekler kesindir. Claude Code örneklerden genelleme yapmada, düzyazı açıklamalardan çıkarım yapmaktan çok daha başarılıdır. (Domain 4.2 — few-shot prompting ile aynı ilke, farklı bağlam.)

**Kural:** Düzyazı açıklamaları tutarsız yorumlanıyorsa, somut girdi/çıktı örneklerine geç. Daha uzun düzyazı yazmak sorunu çözmez.

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

**Edge case'ler için de aynı teknik:** Exam guide'ın örneği — "providing specific test cases with example input and expected output to fix edge case handling (e.g., **null values in migration scripts**)". Migrasyon betiği null değerlerde çöküyorsa "null'ları düzgün ele al" deme; `girdi: {email: null} → beklenen: satır atlanır, log yazılır` şeklinde somut vaka ver.

---

## Teknik 2: Test Güdümlü İterasyon (Test-Driven Iteration)

Önce testleri yaz, başarısız testleri Claude Code'la paylaş, iyileştirmeyi yönlendir.

**Nasıl çalışır:**
1. Beklenen davranışı tanımlayan testleri yaz — exam guide'a göre üç şeyi kapsamalı: **beklenen davranış, edge case'ler ve performans gereksinimleri**
2. Testlerin **önce başarısız olduğunu doğrula** (best practices: Claude'a mock implementasyon yazmamasını söyle)
3. Claude Code'un ürettiği kodu testlere karşı çalıştır
4. Başarısız testleri Claude Code'a göster
5. Claude Code testleri geçene kadar kodu iyileştirir

**Avantajı:** Başarı kriteri net ve nesnel. "İyi mi kötü mü" tartışması yok — testler ya geçer ya geçmez. Claude "bitti gibi görünüyor" yerine "test geçti" sinyaliyle durur ("give Claude a way to verify its work").

**Hafif versiyonu:** Ayrı test dosyası yazmadan prompt'a doğrulama kriteri koy: *"validateEmail fonksiyonu yaz. Test vakaları: user@example.com → true, invalid → false, user@.com → false. Uyguladıktan sonra testleri çalıştır."* (Domain 4.1 — explicit criteria ile bağ.)

**Varyant:** Testleri bir Claude oturumu yazsın, kodu başka bir oturum geçirsin (Writer/Reviewer kalıbı — Task 3.6 ve Domain 4.6).

---

## Teknik 3: Mülakat Deseni (Interview Pattern)

Claude Code'un uygulamadan önce **sana sorular sormasını** iste.

**Ne zaman kullanılır:** Aşina olmadığın bir alanda çalışırken, **uygulamaya başlamadan önce**. Claude Code'un soruları, tek başına düşünerek kaçıracağın noktaları yüzeye çıkarır. Exam guide'ın örnekleri: **cache invalidation stratejileri, failure mode'lar**.

**Nasıl çalışır (resmi prompt kalıbı):**
```
"[Kısa açıklama] inşa etmek istiyorum. AskUserQuestion aracını kullanarak beni 
detaylı mülakata al. Teknik uygulama, edge case'ler, riskler ve trade-off'ları sor. 
Bariz soruları sorma; düşünmemiş olabileceğim zor noktalara in. 
Her şeyi kapsayana kadar devam et, sonra tam spec'i SPEC.md'ye yaz."
```

Claude Code şu tür sorular sorar:
- "Cache ne zaman geçersiz kılınacak — yazma anında mı, TTL ile mi?"
- "Sağlayıcı zaman aşımına uğrarsa hangi failure mode: retry mı, degrade mı?"
- "Çok-çok ilişki gerekli mi? Soft delete kullanılacak mı?"

Bu sorular, sen tasarıma başlamadan önce eksik gereksinimleri ortaya çıkarır. Spec tamamlanınca **yeni bir oturumda** uygula — temiz bağlam. (Domain 5.2 — belirsizlikte eskalasyon ile bağ: Claude'un tahmin etmek yerine sorması.)

---

## Geri Bildirim Zamanlama Stratejisi

### Toplu Geri Bildirim (Batch) — Tek Detaylı Mesajda

**Ne zaman:** Düzeltmeler **birbiriyle etkileşiyor** — birini değiştirmek diğerlerini etkiliyor. Claude tüm resmi tek seferde görmeli; aksi halde ilk düzeltme ikincisini bozar, ikincisi birinciyi geri alır.

Örnek: "Fonksiyon adını değiştir, parametreleri güncelle ve çağrılan yerleri düzelt" — bunlar birbirine bağlı, tek mesajda ver. Ya da: "Hata yönetimini ekle **ve** yanıt formatını buna göre değiştir" — hata yönetimi yanıt formatını belirler; ayrı verirsen ikinci mesaj birinciyi yeniden yazdırır.

### Sıralı Geri Bildirim (Sequential) — Ayrı Mesajlarda

**Ne zaman:** Sorunlar **birbirinden bağımsız** — birini düzeltmek diğerini etkilemiyor. Her düzeltmeyi ayrı doğrulayabilirsin.

Örnek: "Dosya 1'deki girintiyi düzelt" ve "Dosya 2'deki hata mesajını güncelle" — bağımsız sorunlar, ayrı mesajlarda ver.

> **Ölçüt tek:** *Birini düzeltmek diğerinin çözümünü değiştiriyor mu?* Evet → toplu. Hayır → sıralı. Hangi dosyada olduğu ya da hangisinin "önemli" olduğu ölçüt değildir.

### Üçüncü Durum: Düzeltme Döngüsü Kilitlendi → `/clear`

Aynı konuda **iki düzeltmeden sonra** hâlâ yanlışsa, bağlam başarısız yaklaşımlarla dolmuştur. Üçüncü düzeltme yerine: `/clear` ile temiz oturum + öğrendiklerini içeren **daha iyi bir ilk prompt**. Resmi cümle: "A clean session with a better prompt almost always outperforms a long session with accumulated corrections."

Erken düzeltme araçları (kurs modülü: *Steering Long Sessions*):
- `Esc` — Claude'u ortasında durdur, bağlam korunur, yönlendir
- `Esc Esc` / `/rewind` — konuşmayı ve/veya kodu önceki checkpoint'e geri al
- "Undo that" — Claude değişiklikleri geri alsın
- `/clear` — ilgisiz görevler arasında bağlamı sıfırla

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Somut girdi/çıktı örnekleri | Düzyazı **tutarsız yorumlanıyorsa** en etkili — 2-3 before/after; daha uzun düzyazı çözüm değil |
| Edge case düzeltme | Somut test vakası: girdi + beklenen çıktı (null değer örneği) |
| Test güdümlü iterasyon | Testleri **önce** yaz (davranış + edge case + performans), başarısız olduğunu gör, başarısız testleri paylaş |
| Mülakat deseni | **Uygulamadan önce**, aşina olmadığın alanda; cache invalidation, failure mode'lar; `AskUserQuestion` → SPEC.md |
| Toplu geri bildirim | Etkileşimli düzeltmeler → tek detaylı mesaj |
| Sıralı geri bildirim | Bağımsız düzeltmeler → ayrı mesajlar |
| İki düzeltmeden sonra | `/clear` + daha iyi prompt; `Esc`, `/rewind` erken müdahale |
| Doğrulama | Claude'a çalıştırabileceği bir kontrol ver (test, build, screenshot) |
| Sınav tuzağı | "Düzyazı açıklaması tutarsız yorumlanıyor" → cevap: somut örnekler (daha detaylı düzyazı değil) |

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
> **A)** CLAUDE.md'ye daha detaylı bir düzyazı açıklama ekle — neyin "modern" olduğunu uzun uzun anlat.
>
> **B)** 2-3 somut girdi/çıktı örneği ver — "bu eski kodu ver, bu modern koda dönüştür" şeklinde before/after örnekleri.
>
> **C)** Claude Code'u farklı bir modelle çalıştır — daha akıllı model tutarlı olur.
>
> **D)** Her dönüşüm için ayrı bir skill oluştur — arrow function skill'i, destructuring skill'i.

### Doğru Cevap: B

**Neden B doğru:** Düzyazı açıklama tutarsız yorumlanıyor — bu tam olarak somut örneklere geçme sinyali. 2-3 before/after örneği modelin desen çıkarmasını ve tutarlı uygulamasını sağlar. "Modern" ne demek belirsiz — örnekler kesindir.

**Neden A yanlış:** Daha fazla düzyazı, daha fazla belirsizlik. Düzyazı zaten tutarsız yorumlanıyor — daha uzun düzyazı sorunu çözmez, karmaşıklık ekler ve CLAUDE.md'yi şişirir (Task 3.1).

**Neden C yanlış:** Sorun modelin zekası değil, talimatın belirsizliği. Farklı model de belirsiz talimatı farklı yorumlar.

**Neden D yanlış:** Aşırı mühendislik. Her dönüşüm türü için ayrı skill oluşturmak karmaşıklık yaratır. 2-3 örnek çok daha basit ve etkili.

---

## Pratik Senaryo 2

> Bir developer, Claude Code'un ürettiği bir API endpoint'ini iyileştirmek istiyor. Kod incelemesinde iki bulgu var:
>
> 1. Hata yönetimi (error handling) eksik — hatalar yakalanmıyor
> 2. Yanıt formatı tutarsız — başarı ve hata durumlarında farklı JSON şekilleri dönüyor
>
> Developer fark ediyor ki hata yönetimini nasıl ekleyeceği, hata durumundaki yanıt formatını da belirliyor.
>
> **Geri bildirimi nasıl vermeli?**
>
> **A)** İki sorunu tek detaylı mesajda ver — toplu geri bildirim.
>
> **B)** Önce hata yönetimini düzelt (tek mesaj), sonra yanıt formatını güncelle (ayrı mesaj) — sıralı geri bildirim.
>
> **C)** İkisini de düzyazı ile açıkla ve Claude Code'un önceliği kendisi belirlemesini iste.
>
> **D)** Önce yanıt formatını düzelt, sonra hata yönetimini ekle — format daha önemli.

### Doğru Cevap: A

**Neden A doğru:** İki düzeltme **etkileşiyor**: hata yönetiminin nasıl yapıldığı (throw mı, result nesnesi mi) hata yanıtının JSON şeklini belirler. Ayrı mesajlarda verirsen ilk düzeltme bir yanıt şekli üretir, ikinci düzeltme onu yeniden yazdırır — iki tur, çelişkili ara sonuç. Tek detaylı mesajda vermek Claude'un tüm resmi görüp tutarlı bir tasarım yapmasını sağlar. Exam guide: "addressing multiple interacting issues in a single detailed message when fixes interact."

**Neden B yanlış:** Sıralı geri bildirim **bağımsız** sorunlar içindir. Buradaki iki sorun aynı kod yolunu ve aynı veri şeklini etkiliyor; sıralı vermek yeniden iş yaratır.

**Neden C yanlış:** Önceliklendirmeyi Claude'a bırakmak tutarsız sonuçlar yaratabilir. Developer olarak sen etkileşimi görüyorsun; onu prompt'ta açıkça belirtmelisin.

**Neden D yanlış:** Sıra sorusu değil, etkileşim sorusu. Hangi sırayla verirsen ver, iki ayrı mesaj ikinci turda birinciyi yeniden yazdırır.

---

## Pratik Senaryo 3

> Bir developer, Claude Code ile bir dağıtık cache katmanı tasarlıyor. Bu alanda deneyimi yok. Doğrudan "Redis tabanlı cache katmanı yaz" dediğinde Claude çalışan bir kod üretiyor; ama production'da veri güncellenince eski değerler dönmeye devam ediyor ve Redis düştüğünde uygulama tamamen duruyor.
>
> **Bu sorunları uygulamadan ÖNCE yakalamak için hangi teknik kullanılmalıydı?**
>
> **A)** Test güdümlü iterasyon — önce Redis testlerini yaz.
>
> **B)** Mülakat deseni — Claude'a uygulamadan önce cache invalidation stratejisi, failure mode'lar ve trade-off'lar hakkında sorular sordurup spec çıkarmak.
>
> **C)** Somut girdi/çıktı örnekleri — 2-3 cache çağrısı örneği ver.
>
> **D)** Plan modu — Claude kod tabanını keşfetsin.

### Doğru Cevap: B

**Neden B doğru:** İki sorun (stale data → cache invalidation, Redis düşünce çökme → failure mode) exam guide'ın mülakat deseni için verdiği örneklerin ta kendisi: "surface design considerations (e.g., **cache invalidation strategies, failure modes**) before implementing solutions in **unfamiliar domains**." Developer bu alanı bilmediği için doğru soruları kendisi soramaz; Claude'un sorması gereksinim boşluklarını uygulamadan önce kapatır.

**Neden A yanlış:** Test yazmak için neyi test edeceğini bilmek gerekir; developer invalidation ve failure mode gereksinimlerinin varlığından bile habersiz. Testler mülakattan *sonra*, spec'ten türetilir.

**Neden C yanlış:** Örnekler dönüşüm/format belirsizliğini çözer; burada sorun tasarım gereksinimlerinin eksikliği.

**Neden D yanlış:** Plan modu kod tabanını keşfeder ama developer'ın *bilmediği* gereksinimleri kendiliğinden sormaz; mülakat deseni tam o boşluk için.
