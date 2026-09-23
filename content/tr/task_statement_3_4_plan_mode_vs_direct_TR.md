# Task Statement 3.4: Plan Modu vs Doğrudan Çalıştırma

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code'a bir görev verdiğinde iki temel mod var: **plan modu** (önce düşün, sonra yap) ve **doğrudan çalıştırma** (hemen yap). Sınav, hangi durumda hangisinin kullanılacağını bilmeni bekliyor.

---

## Plan Modu — Önce Düşün, Sonra Yap

Plan modunda Claude Code önce **analiz eder, keşfeder, tasarlar** — sonra onay alınca uygular.

### Ne Zaman Kullanılır?

- **Karmaşık görevler** — büyük ölçekli değişiklikler
- **Birden fazla geçerli yaklaşım** var — hangisinin en iyi olduğunu değerlendirmek gerekiyor
- **Mimari kararlar** gerekiyor
- **Çok dosyalı değişiklikler** — örneğin 45+ dosyayı etkileyen kütüphane migrasyonu
- **Keşif gerekli** — kod tabanını incelemek ve tasarlamak, değişiklik yapmadan önce

### Örnekler

| Görev | Plan Modu mu? | Neden? |
|---|---|---|
| Monolit'i mikroservislere dönüştür | ✅ Evet | Mimari karar, çok fazla yaklaşım var |
| 30 dosyada loglama kütüphanesi değiştir | ✅ Evet | Çok dosyalı, önce etki analizi gerekli |
| Legacy kod tabanını anla ve yeniden yapılandır | ✅ Evet | Keşif gerekli, tasarım gerekli |

---

## Doğrudan Çalıştırma — Hemen Yap

Doğrudan çalıştırmada Claude Code planlamadan **hemen uygulamaya** geçer.

### Ne Zaman Kullanılır?

- **İyi anlaşılmış değişiklikler** — net ve sınırlı kapsam
- **Tek dosya hata düzeltmesi** — açık stack trace ile
- **Basit ekleme** — tarih doğrulama koşulu ekleme gibi
- **Doğru yaklaşım zaten biliniyor** — keşif veya karşılaştırma gerekmiyor

### Örnekler

| Görev | Doğrudan mı? | Neden? |
|---|---|---|
| Tek fonksiyonda null pointer düzelt | ✅ Evet | Açık hata, tek dosya, net çözüm |
| Tarih alanına validasyon ekle | ✅ Evet | Sınırlı kapsam, net gereksinim |
| README'ye kurulum adımları ekle | ✅ Evet | Basit ekleme |

---

## Explore Alt-Agent'ı

Çok aşamalı görevlerde **Explore alt-agent'ı** devreye girer:

- **Detaylı keşif çıktısını** ana konuşmadan izole eder
- Ana konuşmaya **özetler** döndürür
- **Context window tükenmesini önler**

Explore alt-agent'ını düşün: birisi senin için gidip araştırma yapıyor, sonra sana sadece önemli bulguları özetliyor — tüm ham veriyi değil.

### Ne Zaman Kullanılır?

- Kod tabanını keşfetmek ve anlamak gerektiğinde
- Çok fazla dosya incelenecekse
- Ana konuşmanın bağlamını korumak istiyorsan

---

## Kombinasyon Deseni (Hybrid Yaklaşım)

Pratikte ve sınavda en çok test edilen yaklaşım:

1. **Plan modu** ile araştırma ve tasarım yap
2. **Doğrudan çalıştırma** ile planlanan yaklaşımı uygula

Bu ikisini birleştirmek yaygın ve beklenen bir kalıptır.

### Örnek Akış

```
Görev: 30 dosyada log4j'den SLF4J'ye geçiş

Adım 1 (Plan modu):
- Etkilenen dosyaları keşfet
- Import pattern'larını analiz et
- Yapılandırma farklılıklarını belirle
- Migrasyon planı oluştur

Adım 2 (Doğrudan çalıştırma):
- Plana göre dosyaları güncelle
- Import'ları değiştir
- Yapılandırma dosyalarını güncelle
```

---

## Karar Tablosu

| Görev Özellikleri | Mod | Gerekçe |
|---|---|---|
| Karmaşık, çok yaklaşım var | **Plan modu** | Değerlendirme gerekli |
| Çok dosyalı değişiklik | **Plan modu** | Önce etki analizi |
| Mimari karar | **Plan modu** | Tasarım gerekli |
| Keşif gerekli | **Plan modu** | Önce anla, sonra yap |
| Tek dosya, net hata | **Doğrudan** | Açık çözüm, hemen yap |
| Basit ekleme, sınırlı kapsam | **Doğrudan** | Planlama gereksiz |
| Yaklaşım zaten biliniyor | **Doğrudan** | Değerlendirme gereksiz |
| Araştırma + uygulama | **Hybrid** | Plan → doğrudan çalıştırma |

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Plan modu | Karmaşık görevler, çok yaklaşım, mimari karar, keşif gerekli |
| Doğrudan çalıştırma | Net hata, sınırlı kapsam, yaklaşım biliniyor |
| Explore alt-agent'ı | Detaylı keşfi izole eder, ana konuşmaya özet döndürür, context korur |
| Hybrid yaklaşım | Plan modu → doğrudan çalıştırma: araştır, tasarla, sonra uygula |
| Sınav ipucu | "45 dosya", "migrasyon", "yeniden yapılandırma" → plan modu |
| Sınav ipucu | "tek dosya", "null pointer", "basit düzeltme" → doğrudan çalıştırma |

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
2. **Null pointer düzeltme = Doğrudan çalıştırma.** Tek dosya, stack trace mevcut, net hata, net çözüm. Planlama gereksiz.
3. **30 dosyada kütüphane migrasyonu = Plan modu.** Çok dosyalı değişiklik, önce etkilenen dosyaları keşfet, import pattern'larını analiz et, sonra uygula.

**Neden A yanlış:** Görev 2 (null pointer) için plan modu gereksiz — tek dosyada net hata, doğrudan düzelt.

**Neden C yanlış:** Görev 1 (monolit dönüşümü) için doğrudan çalıştırma tehlikeli — mimari kararı keşfetmeden ve tasarlamadan uygulamak kaos yaratır.

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
> **B)** Keşif aşamasında Explore alt-agent'ını kullan (detaylı çıktıyı izole eder, özet döndürür), sonra plan modunda tasarım yap, son olarak doğrudan çalıştırma ile uygula.
>
> **C)** 25 dosyayı sırayla Read ile oku, hepsini ana konuşmaya aktar.
>
> **D)** Plan modunda her şeyi tek seferde yap — keşif, tasarım ve uygulama birlikte.

### Doğru Cevap: B

**Neden B doğru:** Üç aşamalı hybrid yaklaşım:
1. **Explore alt-agent'ı** ile keşif — detaylı çıktı izole bağlamda kalır, ana konuşmaya sadece özetler döner. Context window korunur.
2. **Plan modu** ile tasarım — keşif bulgularına dayanarak yeniden yapılandırma planı oluştur.
3. **Doğrudan çalıştırma** ile uygulama — planı uygula.

**Neden A yanlış:** 25 dosyalık legacy modül, belirsiz bağımlılıklar — keşif kesinlikle gerekli. Doğrudan çalıştırma ile başlamak körü körüne değişiklik yapmak demek.

**Neden C yanlış:** 25 dosyayı sırayla ana konuşmaya aktarmak context window'u tüketir. Explore alt-agent'ı tam olarak bu sorunu çözer — izole eder, özetler.

**Neden D yanlış:** Keşif aşaması çok detaylı çıktı üretir — plan moduyla birleştirmek ana konuşmanın bağlamını kirletir. Explore alt-agent'ı keşfi izole etmek için var.
