# Task Statement 3.4: Plan Modu vs Doğrudan Çalıştırma

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code'a bir görev verdiğinde iki temel mod var: **plan modu** (önce düşün, sonra yap) ve **doğrudan çalıştırma** (hemen yap). Sınav, hangi durumda hangisinin kullanılacağını bilmeni bekliyor.

Bilinmesi gereken ilk şey: **plan modu bir *permission mode*'dur.** Claude'un ne yapabileceğini belirleyen mod döngüsünün (`default` → `acceptEdits` → `plan`) bir parçasıdır (bkz. Domain 1.4 ve Task 3.6). "Doğrudan çalıştırma" ise ayrı bir mod değil, plan modunda *olmamaktır*.

---

## Plan Modu — Önce Düşün, Sonra Yap

Plan modunda Claude Code **araştırır ve değişiklik önerir, ama uygulamaz**: dosyaları okur, keşif komutları çalıştırır, bir plan yazar — **kaynak kodu düzenlemez**. Düzenlemeler plan onaylanana kadar engellenir.

### Mekanizma (sınavın sormadığı ama dokümanların atladığı katman)

| Adım | Nasıl |
|---|---|
| Plan moduna gir | `Shift+Tab` (mod döngüsü: `⏸ plan mode on` görünene kadar) · tek bir prompt için `/plan` öneki · `claude --permission-mode plan` · proje varsayılanı için `.claude/settings.json` → `"permissions": {"defaultMode": "plan"}` |
| Keşif | Claude yerleşik **Plan** ve **Explore** subagent'larına delege eder — dosya okumaları ana bağlamı şişirmez |
| Plan | Claude planı sunar; `Ctrl+G` ile planı editöründe düzenleyebilirsin |
| Onay | **Yes, and use auto mode** (veya auto kapalıysa *Yes, auto-accept edits*) · **Yes, manually approve edits** · **No, keep planning** |
| Sonuç | **Onay = plan modundan çık + seçtiğin izin moduyla uygulamaya geç.** Yeniden planlamak için `Shift+Tab` ya da `/plan` |

> Dokümanların "hybrid yaklaşım" dediği şey (plan → doğrudan çalıştırma) ayrı bir teknik değil, plan modunun **normal yaşam döngüsüdür**: planla → onayla → uygula.

### Ne Zaman Kullanılır?

- **Karmaşık görevler** — büyük ölçekli değişiklikler
- **Birden fazla geçerli yaklaşım** var — hangisinin en iyi olduğunu değerlendirmek gerekiyor
- **Mimari kararlar** gerekiyor (servis sınırları, modül bağımlılıkları)
- **Çok dosyalı değişiklikler** — örneğin 45+ dosyayı etkileyen kütüphane migrasyonu
- **Keşif gerekli** — kod tabanını incelemek ve tasarlamak, değişiklik yapmadan önce
- **Aşina olmadığın kod** — yanlış problemi çözmeyi önler ("preventing costly rework")
- **Altyapı gereksinimleri farklı entegrasyon seçenekleri** arasında karar

### Örnekler

| Görev | Plan Modu mu? | Neden? |
|---|---|---|
| Monolit'i mikroservislere dönüştür | ✅ Evet | Mimari karar, çok fazla yaklaşım var (exam guide Q5) |
| 45 dosyada loglama kütüphanesi değiştir | ✅ Evet | Çok dosyalı, önce etki analizi gerekli |
| Legacy kod tabanını anla ve yeniden yapılandır | ✅ Evet | Keşif gerekli, tasarım gerekli |
| İki entegrasyon yaklaşımından birini seç (webhook vs polling; farklı altyapı) | ✅ Evet | Birden fazla geçerli yaklaşım, altyapı etkisi |

---

## Doğrudan Çalıştırma — Hemen Yap

Doğrudan çalıştırmada Claude Code planlamadan **hemen uygulamaya** geçer.

### Ne Zaman Kullanılır?

- **İyi anlaşılmış değişiklikler** — net ve sınırlı kapsam
- **Tek dosya hata düzeltmesi** — açık stack trace ile
- **Basit ekleme** — tek bir fonksiyona tarih doğrulama koşulu ekleme gibi
- **Doğru yaklaşım zaten biliniyor** — keşif veya karşılaştırma gerekmiyor

### Resmi Heuristik

> **"If you could describe the diff in one sentence, skip the plan."**
> Plan modu değer katar ama **ek yük getirir** ("adds overhead"). Yazım hatası düzeltme, log satırı ekleme, değişken yeniden adlandırma → doğrudan.

### Örnekler

| Görev | Doğrudan mı? | Neden? |
|---|---|---|
| Tek fonksiyonda null pointer düzelt (stack trace var) | ✅ Evet | Açık hata, tek dosya, net çözüm |
| Tarih alanına validasyon ekle | ✅ Evet | Sınırlı kapsam, net gereksinim |
| README'ye kurulum adımları ekle | ✅ Evet | Basit ekleme |
| Off-by-one hatası, hata mesajı mevcut | ✅ Evet | Diff bir cümleyle anlatılabilir |

---

## Explore Subagent'ı

Çok aşamalı görevlerde **Explore subagent'ı** devreye girer:

- Yerleşik (built-in) bir subagent; Claude gerektiğinde kendisi kullanır, sen de "use a subagent to investigate X" diyerek tetikleyebilirsin
- **Salt-okunur:** Write ve Edit araçları reddedilir — Explore *değişiklik yapamaz*, yalnızca keşfeder
- **Detaylı keşif çıktısını** ana konuşmadan izole eder; ana konuşmaya **özet** döndürür
- **Context window tükenmesini önler** — "the infinite exploration" anti-pattern'inin çözümü
- Claude derinlik belirtir: *quick* / *medium* / *very thorough*
- Plan modu, keşif için Explore ve **Plan** subagent'ını (o da salt-okunur) otomatik kullanır

Explore subagent'ını düşün: birisi senin için gidip araştırma yapıyor, sonra sana sadece önemli bulguları özetliyor — tüm ham veriyi değil.

### Ne Zaman Kullanılır?

- Kod tabanını keşfetmek ve anlamak gerektiğinde
- Çok fazla dosya incelenecekse
- Ana konuşmanın bağlamını korumak istiyorsan (Domain 5.1 ile bağ)

> **Sınav tuzağı:** "Explore subagent'ı ile 25 dosyayı düzelt" şıkkı yanlıştır — Explore salt-okunurdur. Değişiklik yapan subagent `general-purpose`'tır.

---

## Kombinasyon Deseni (Hybrid Yaklaşım)

Pratikte ve sınavda en çok test edilen yaklaşım:

1. **Plan modu** ile araştırma ve tasarım yap (keşif Explore/Plan subagent'larında)
2. Planı **onayla** → mod değişir
3. **Doğrudan çalıştırma** ile planlanan yaklaşımı uygula

Bu ikisini birleştirmek yaygın ve beklenen bir kalıptır — ve mekanik olarak plan onayının kendisidir.

### Örnek Akış

```
Görev: 30 dosyada log4j'den SLF4J'ye geçiş

Adım 1 (Plan modu — Shift+Tab):
- Etkilenen dosyaları keşfet (Explore subagent'ı)
- Import pattern'larını analiz et
- Yapılandırma farklılıklarını belirle
- Migrasyon planı oluştur → Ctrl+G ile gözden geçir

Adım 2 (Onay → doğrudan çalıştırma):
- "Yes, manually approve edits" (veya auto-accept)
- Plana göre dosyaları güncelle
- Import'ları değiştir
- Yapılandırma dosyalarını güncelle
- Testleri çalıştır (doğrulama)
```

> **İpucu (best practices):** Büyük planlarda planı/spec'i **yeni bir oturumda** uygulamak temiz bağlam sağlar; `showClearContextOnPlanAccept` ayarı onay sırasında bağlamı temizleme seçeneği ekler.

---

## Karar Tablosu

| Görev Özellikleri | Mod | Gerekçe |
|---|---|---|
| Karmaşık, çok yaklaşım var | **Plan modu** | Değerlendirme gerekli |
| Çok dosyalı değişiklik | **Plan modu** | Önce etki analizi |
| Mimari karar | **Plan modu** | Tasarım gerekli |
| Keşif gerekli / aşina değilsin | **Plan modu** | Önce anla, sonra yap |
| Tek dosya, net hata | **Doğrudan** | Açık çözüm, hemen yap |
| Basit ekleme, sınırlı kapsam | **Doğrudan** | Planlama gereksiz |
| Yaklaşım zaten biliniyor | **Doğrudan** | Değerlendirme gereksiz |
| Diff bir cümleyle anlatılabiliyor | **Doğrudan** | Plan ek yük |
| Araştırma + uygulama | **Hybrid** | Plan → onay → doğrudan çalıştırma |

---

## Sınavın Gerçek Distractor'ları (Exam Guide Q5)

Monolit → mikroservis sorusunun yanlış şıkları, "plan modu" cevabından daha öğreticidir:

| Şık | Neden yanlış |
|---|---|
| "Doğrudan başla, artımlı ilerle; servis sınırları uygulama sırasında kendini gösterir" | Bağımlılıklar geç keşfedilince **maliyetli yeniden iş** ("costly rework") |
| "Doğrudan çalıştır ama her servisin yapısını detaylı ön talimatla ver" | Kodu keşfetmeden doğru yapıyı zaten bildiğini varsayar |
| **"Doğrudan başla; beklenmedik karmaşıklık çıkarsa plan moduna geç"** | En çekici tuzak. Karmaşıklık *gereksinimde zaten yazılı* ("dozens of files", "decisions about service boundaries") — sonradan ortaya çıkacak bir şey değil. |

> **Sınav kuralı:** Soru metninde "birçok dosya", "mimari karar", "birden fazla yaklaşım" geçiyorsa "önce doğrudan dene" şıkkı **her zaman yanlıştır**.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Plan modu = permission mode | `Shift+Tab` / `/plan` / `--permission-mode plan`; okur, keşfeder, plan yazar, **düzenlemez** |
| Plan modu ne zaman | Karmaşık görevler, çok yaklaşım, mimari karar, çok dosya (45+), keşif gerekli, aşina değilsin |
| Doğrudan çalıştırma | Net hata, sınırlı kapsam, yaklaşım biliniyor, diff tek cümle |
| Onay akışı | auto / manuel onay / planlamaya devam; **onay = moddan çık + uygula** |
| Explore subagent'ı | Salt-okunur; detaylı keşfi izole eder, özet döndürür, context korur; plan modu otomatik kullanır |
| Hybrid yaklaşım | Plan → onay → doğrudan çalıştırma: plan modunun normal akışı |
| Q5 tuzağı | "Önce doğrudan, karmaşıklık çıkarsa plan" → yanlış; karmaşıklık zaten belli |
| Sınav ipucu | "45 dosya", "migrasyon", "yeniden yapılandırma", "servis sınırları" → plan modu |
| Sınav ipucu | "tek dosya", "null pointer", "stack trace", "basit düzeltme" → doğrudan çalıştırma |

---

## Pratik Senaryo 1

> Üç görev var. Her birini plan modu veya doğrudan çalıştırma olarak sınıflandır:
>
> 1. Bir monolit uygulamayı mikroservislere dönüştürmek
> 2. Tek bir fonksiyondaki null pointer hatasını düzeltmek (stack trace mevcut)
> 3. 30 dosyada bir loglama kütüphanesinden diğerine geçiş yapmak
>
> **A)** 1: Plan, 2: Plan, 3: Doğrudan
>
> **B)** 1: Plan, 2: Doğrudan, 3: Plan
>
> **C)** 1: Doğrudan, 2: Doğrudan, 3: Plan
>
> **D)** 1: Plan, 2: Doğrudan, 3: Doğrudan

### Doğru Cevap: B

**Neden B doğru:**
1. **Monolit → mikroservisler = Plan modu.** Mimari karar, birden fazla yaklaşım, büyük ölçekli değişiklik. Önce analiz et, tasarla, sonra uygula.
2. **Null pointer düzeltme = Doğrudan çalıştırma.** Tek dosya, stack trace mevcut, net hata, net çözüm — diff bir cümleyle anlatılabilir.
3. **30 dosyada kütüphane migrasyonu = Plan modu.** Çok dosyalı değişiklik, önce etkilenen dosyaları keşfet, import pattern'larını analiz et, sonra uygula.

**Neden A yanlış:** Görev 2 (null pointer) için plan modu gereksiz ek yük — tek dosyada net hata, doğrudan düzelt.

**Neden C yanlış:** Görev 1 (monolit dönüşümü) için doğrudan çalıştırma tehlikeli — mimari kararı keşfetmeden ve tasarlamadan uygulamak maliyetli yeniden iş yaratır.

**Neden D yanlış:** Görev 3 (30 dosya migrasyon) için doğrudan çalıştırma riskli — önce etki analizi ve plan gerekli.

---

## Pratik Senaryo 2

> Bir developer büyük bir kod tabanında çalışıyor. Legacy bir modülü anlamak ve yeniden yapılandırmak istiyor. Modül 25 dosyadan oluşuyor ve bağımlılıkları belirsiz.
>
> Developer şu yaklaşımı izlemek istiyor:
> - Önce kod tabanını keşfet ve bağımlılıkları haritalandır
> - Sonra yeniden yapılandırma planı oluştur
> - Son olarak planı uygula
>
> Ancak keşif aşamasında çok fazla detaylı çıktı üretileceğinden endişeli — ana konuşmanın bağlamı kirlenir.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Tüm süreci doğrudan çalıştırma ile yap — keşif gereksiz.
>
> **B)** Keşif aşamasında Explore subagent'ını kullan (detaylı çıktıyı izole eder, özet döndürür), plan modunda tasarım yap, planı onaylayıp doğrudan çalıştırma ile uygula.
>
> **C)** 25 dosyayı sırayla Read ile oku, hepsini ana konuşmaya aktar.
>
> **D)** Plan modunda her şeyi tek seferde yap — keşif, tasarım ve uygulama birlikte, moddan hiç çıkmadan.

### Doğru Cevap: B

**Neden B doğru:** Üç aşamalı hybrid yaklaşım:
1. **Explore subagent'ı** ile keşif — detaylı çıktı izole bağlamda kalır, ana konuşmaya sadece özetler döner. Context window korunur. (Plan modu bunu otomatik da yapar; developer açıkça "use a subagent to map the dependencies" diyebilir.)
2. **Plan modu** ile tasarım — keşif bulgularına dayanarak yeniden yapılandırma planı oluştur, `Ctrl+G` ile gözden geçir.
3. **Onay → doğrudan çalıştırma** ile uygulama.

**Neden A yanlış:** 25 dosyalık legacy modül, belirsiz bağımlılıklar — keşif kesinlikle gerekli. Doğrudan çalıştırma ile başlamak körü körüne değişiklik yapmak demek.

**Neden C yanlış:** 25 dosyayı sırayla ana konuşmaya aktarmak context window'u tüketir ("the infinite exploration" anti-pattern'i). Explore subagent'ı tam olarak bu sorunu çözer — izole eder, özetler.

**Neden D yanlış:** **Plan modu dosya düzenleyemez.** Keşif ve tasarım plan modunda olur (ve keşif zaten Plan/Explore subagent'larına delege edilir — bağlam kirlenmez), ama *uygulama* için planın onaylanıp moddan çıkılması gerekir. "Moddan hiç çıkmadan uygula" mekanik olarak imkânsızdır.

---

## Pratik Senaryo 3

> Bir developer'a şu görev verildi: "Ödeme servisini üçüncü taraf sağlayıcıya bağla. Webhook tabanlı ve polling tabanlı iki yaklaşım var; biri kuyruk altyapısı gerektiriyor, diğeri zamanlanmış görev. Değişiklik 20 civarı dosyayı etkileyecek."
>
> Developer'ın planı: "Doğrudan çalıştırma ile webhook yaklaşımını uygulamaya başlayayım; kuyruk altyapısıyla ilgili beklenmedik bir karmaşıklık çıkarsa plan moduna geçerim."
>
> **Bu yaklaşımın değerlendirmesi hangisidir?**
>
> **A)** Doğru — plan modu ek yük getirir; sorun çıkınca geçmek verimli.
>
> **B)** Yanlış — görev "birden fazla geçerli yaklaşım + farklı altyapı gereksinimleri + çok dosya" içeriyor; karmaşıklık gereksinimde zaten yazılı. Önce plan modunda iki yaklaşımı karşılaştırıp karar vermek, sonra uygulamak gerekir.
>
> **C)** Yanlış — görev tek başına Explore subagent'ı ile çözülmeli; plan modu gereksiz.
>
> **D)** Doğru — ama polling ile başlamak daha güvenli olur.

### Doğru Cevap: B

**Neden B doğru:** Exam guide'ın Skills maddesi birebir: "choosing between integration approaches with different infrastructure requirements" → plan modu. Karmaşıklık "beklenmedik" değil, gereksinimde açıkça belirtilmiş. Yanlış yaklaşımla 20 dosya değiştirip sonra kuyruk altyapısının uygun olmadığını keşfetmek maliyetli yeniden iştir — plan modunun önlediği şey tam olarak budur. (Exam guide Q5'in D şıkkının ders notu karşılığı.)

**Neden A yanlış:** "Plan modu ek yük" heuristiği *diff bir cümleyle anlatılabilen* küçük görevler içindir; iki mimari yaklaşım arasında seçim bu sınıfa girmez.

**Neden C yanlış:** Explore salt-okunurdur ve yalnızca keşif yapar; iki yaklaşımı değerlendirip plan çıkarmak plan modunun işidir (Explore'u içinde kullanır).

**Neden D yanlış:** Hangi yaklaşımın "güvenli" olduğu tam da karşılaştırılmadan bilinemez; sorun başlangıç seçimi değil, seçimin analizsiz yapılması.
