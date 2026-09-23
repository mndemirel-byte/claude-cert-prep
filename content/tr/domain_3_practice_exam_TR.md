# Domain 3 — Pratik Sınav

## Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

**Dağılım:**
- 2 soru → CLAUDE.md Hiyerarşisi (3.1)
- 1 soru → Özel Komutlar ve Skill'ler (3.2)
- 1 soru → Yol-Bazlı Kurallar (3.3)
- 2 soru → Plan Modu vs Doğrudan Çalıştırma (3.4)
- 1 soru → Yinelemeli İyileştirme (3.5)
- 1 soru → CI/CD Entegrasyonu (3.6)

**Geçme kriteri:** 7+/8

---

## Soru 1 (Task Statement 3.1)

> Bir takımda 4 developer aynı repo üzerinde çalışıyor. Developer A, Claude Code'un test yazarken her zaman `vitest` framework'ünü kullanmasını ve `describe/it` yapısını takip etmesini sağlayan kurallar tanımlamış. Diğer 3 developer ise Claude Code'dan tutarsız test çıktıları alıyor — bazen `jest` kullanıyor, bazen `mocha` kullanıyor.
>
> Developer A'nın kuralları `~/.claude/CLAUDE.md` dosyasında tanımlı.
>
> **Kök neden ve çözüm nedir?**
>
> **A)** Diğer developer'ların Claude Code sürümleri farklı — herkes aynı sürüme güncellenmeli.
>
> **B)** Kurallar kullanıcı seviyesinde (`~/.claude/CLAUDE.md`) — sadece Developer A'ya uygulanıyor. Proje seviyesine (`.claude/CLAUDE.md`) taşınmalı ki tüm takım alsın.
>
> **C)** Her developer kendi `~/.claude/CLAUDE.md` dosyasına aynı kuralları kopyalamalı.
>
> **D)** Developer A `/memory` komutuyla bellekleri senkronize etmeli.

### Doğru Cevap: B

**Neden B doğru:** `~/.claude/CLAUDE.md` kullanıcı seviyesi — Git'te yok, paylaşılmaz. Sadece Developer A bu kuralları alıyor. Çözüm: `.claude/CLAUDE.md` (proje seviyesi) dosyasına taşı. Versiyon kontrol altında, repoyu klonlayan herkes bu kuralları alır.

**Neden A yanlış:** Sürüm farkı test framework tercihini açıklamaz. Sorun talimatların eksikliğinde, yazılımın sürümünde değil.

**Neden C yanlış:** Manuel kopyalama sürdürülebilir değil — kurallar değiştiğinde herkesin güncellemesi gerekir. Proje seviyesi dosya otomatik olarak herkese ulaşır.

**Neden D yanlış:** `/memory` teşhis aracıdır, senkronizasyon aracı değil.

---

## Soru 2 (Task Statement 3.1)

> Bir projenin kök dizininde `.claude/CLAUDE.md` dosyası genel kodlama standartlarını içeriyor. Proje şu yapıya sahip:
>
> ```
> /
> ├── .claude/CLAUDE.md  (genel standartlar)
> ├── frontend/          (React)
> ├── backend/           (Python/FastAPI)
> └── infrastructure/    (Terraform)
> ```
>
> Takım, her alt dizin için farklı dile ve framework'e özgü kurallar uygulamak istiyor. Aynı zamanda `.claude/CLAUDE.md` dosyasının çok büyümesini istemiyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Tüm kuralları tek `.claude/CLAUDE.md` dosyasına yaz — büyüklük sorun değil.
>
> **B)** Her alt dizine dizin seviyesi `CLAUDE.md` dosyaları oluştur (`frontend/CLAUDE.md`, `backend/CLAUDE.md`, `infrastructure/CLAUDE.md`) ve/veya `.claude/CLAUDE.md`'de `@import` sözdizimi ile modüler dosyaları referans et.
>
> **C)** Her developer kendi `~/.claude/CLAUDE.md` dosyasına çalıştığı alana göre kuralları yazsın.
>
> **D)** Tüm kuralları skill dosyalarına taşı — her seferinde ilgili skill'i çağırsınlar.

### Doğru Cevap: B

**Neden B doğru:** İki mekanizma birlikte çalışır: dizin seviyesi CLAUDE.md dosyaları o dizine özgü kuralları uygular (React kuralları frontend'de, Python kuralları backend'de). `@import` sözdizimi ise modüler organizasyon sağlar — tek büyük dosya yerine dış dosyaları referans et. Her iki yaklaşım da versiyon kontrol altında ve paylaşılır.

**Neden A yanlış:** Tek dosyaya her şeyi tıkmak token israfı yaratır. Backend'de çalışırken React kurallarını yüklemenin anlamı yok.

**Neden C yanlış:** Kullanıcı seviyesi paylaşılmaz. Yeni üyeler kuralları almaz. Standartlaşma sağlanamaz.

**Neden D yanlış:** Skill'ler isteğe bağlı çağrılır — evrensel standartlar her zaman yüklü olmalı. Skill'ler göreve özgü prosedürler için, CLAUDE.md evrensel standartlar için.

---

## Soru 3 (Task Statement 3.2)

> Bir takım şu gereksinimlere sahip:
>
> 1. Tüm takımın kullanacağı bir `/deploy-checklist` komutu — deployment öncesi kontrol listesi
> 2. Bir developer, büyük kod tabanı analizleri yapan kişisel bir `/deep-analyze` skill'i istiyor — çok detaylı çıktı üretiyor ve ana konuşmayı kirletmemeli
> 3. `/deep-analyze` skill'i sadece okuma araçlarını kullanmalı — dosya yazma veya silme yapmamalı
>
> **Doğru konfigürasyon hangisidir?**
>
> **A)** Her ikisi de `.claude/commands/` dizinine konulmalı.
>
> **B)** `/deploy-checklist` → `.claude/commands/` (proje kapsamlı). `/deep-analyze` → `~/.claude/skills/` dizininde `SKILL.md` olarak, `context: fork` ve `allowed-tools: [Read, Grep, Glob]` frontmatter'ı ile.
>
> **C)** Her ikisi de CLAUDE.md dosyasına prosedür olarak yazılmalı.
>
> **D)** `/deploy-checklist` → `~/.claude/commands/`. `/deep-analyze` → `.claude/skills/`.

### Doğru Cevap: B

**Neden B doğru:** Üç gereksinimi de karşılıyor:
1. `/deploy-checklist` takım genelinde → `.claude/commands/` (proje kapsamlı, Git'te, paylaşılır)
2. `/deep-analyze` kişisel ve detaylı çıktı → `~/.claude/skills/` (kişisel) + `context: fork` (izole bağlam, ana konuşma temiz)
3. Sadece okuma araçları → `allowed-tools: [Read, Grep, Glob]` (yıkıcı eylemler engellenir)

**Neden A yanlış:** `/deep-analyze` kişisel istek — takım komutlarına koymak herkesi etkiler. Ayrıca `context: fork` ve `allowed-tools` yapılandırması skill frontmatter'ında yapılır.

**Neden C yanlış:** Bunlar göreve özgü prosedürler — CLAUDE.md evrensel standartlar için. CLAUDE.md her zaman yüklü, isteğe bağlı çağrı yok.

**Neden D yanlış:** Tam tersi yerleştirme. `/deploy-checklist` takım genelinde olmalı (`.claude/commands/`), kişisel dizine koymak paylaşılmaz. `/deep-analyze` kişisel olmalı (`~/.claude/skills/`), takım dizinine koymak herkesi etkiler.

---

## Soru 4 (Task Statement 3.3)

> Bir kod tabanında API endpoint dosyaları `src/api/`, `src/routes/` ve `modules/*/api/` dizinlerinde dağınık olarak bulunuyor. Takım tüm API dosyalarında aynı kuralları uygulamak istiyor: rate limiting kontrolü, input validation, standardize edilmiş hata yanıtları.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** `src/api/CLAUDE.md`, `src/routes/CLAUDE.md` ve her `modules/*/api/CLAUDE.md` dosyasına aynı kuralları kopyala.
>
> **B)** `.claude/rules/api-conventions.md` dosyası oluştur — `paths: ["src/api/**/*", "src/routes/**/*", "modules/*/api/**/*"]` frontmatter'ı ile.
>
> **C)** Kök CLAUDE.md dosyasına tüm API kurallarını yaz.
>
> **D)** Bir `/api-rules` skill'i oluştur — API dosyasına dokunulduğunda çağrılsın.

### Doğru Cevap: B

**Neden B doğru:** Yol-bazlı kurallar glob pattern ile tüm kod tabanındaki API dosyalarını yakalar — hangi dizinde olursa olsun. Tek bir kural dosyası, dağınık API dosyalarının tamamına uygulanır. Token verimli — sadece API dosyası düzenlenirken yüklenir.

**Neden A yanlış:** Her dizine aynı kuralları kopyalamak bakım kabusu. Bir kural değiştiğinde tüm kopyaları güncellemek gerekir. Yol-bazlı kurallar bunu tek dosyayla çözer.

**Neden C yanlış:** Kök CLAUDE.md her zaman yüklenir. Frontend CSS dosyası düzenlerken bile API kuralları bağlamda yer kaplar — token israfı.

**Neden D yanlış:** Skill'ler isteğe bağlı çağrılır — her API dosyasına dokunulduğunda skill çağırmayı hatırlamak gerekir. Yol-bazlı kurallar otomatik yüklenir.

---

## Soru 5 (Task Statement 3.4)

> Bir developer'a üç görev verilmiş:
>
> 1. Mevcut REST API'yi GraphQL'e dönüştürmek — 40+ endpoint etkileniyor
> 2. Tek bir fonksiyondaki off-by-one hatasını düzeltmek — hata mesajı ve stack trace mevcut
> 3. Büyük bir legacy modülü anlamak — 30 dosya, belirsiz bağımlılıklar — keşif aşamasında çok detaylı çıktı bekleniyor
>
> **Her görev için doğru mod hangisidir?**
>
> **A)** 1: Plan modu, 2: Doğrudan çalıştırma, 3: Explore alt-agent'ı + Plan modu
>
> **B)** 1: Doğrudan çalıştırma, 2: Doğrudan çalıştırma, 3: Plan modu
>
> **C)** 1: Plan modu, 2: Plan modu, 3: Doğrudan çalıştırma
>
> **D)** Hepsi plan modu — güvenli tarafta kal.

### Doğru Cevap: A

**Neden A doğru:**
1. **REST → GraphQL = Plan modu.** 40+ endpoint, mimari karar, çok dosyalı değişiklik. Önce analiz et, şema tasarla, sonra uygula.
2. **Off-by-one hatası = Doğrudan çalıştırma.** Stack trace mevcut, tek dosya, net hata. Planlama gereksiz.
3. **Legacy modül keşfi = Explore alt-agent'ı + Plan modu.** 30 dosya, belirsiz bağımlılıklar — Explore alt-agent'ı detaylı keşfi izole eder (ana konuşma temiz kalır), sonra Plan moduyla yeniden yapılandırma tasarlanır.

**Neden B yanlış:** 40+ endpoint migrasyonunu doğrudan çalıştırma ile yapmak çok riskli. Önce etki analizi ve şema tasarımı gerekli.

**Neden C yanlış:** Off-by-one hatası için plan modu gereksiz. Legacy modül için doğrudan çalıştırma tehlikeli — keşif olmadan değişiklik yapmak.

**Neden D yanlış:** Basit hata düzeltmeleri için plan modu zaman kaybı. Doğru modu doğru göreve eşleştirmek önemli.

---

## Soru 6 (Task Statement 3.4)

> Bir developer 30 dosyada lodash kütüphanesini native JavaScript fonksiyonlarıyla değiştirmek istiyor. Yaklaşımını şöyle planlamış:
>
> 1. Önce plan modunda etkilenen dosyaları keşfet ve migrasyon stratejisini belirle
> 2. Sonra doğrudan çalıştırma ile planı uygula
>
> **Bu yaklaşım doğru mu?**
>
> **A)** Hayır — tüm süreç plan modunda olmalı, doğrudan çalıştırmaya geçmemeli.
>
> **B)** Evet — hybrid yaklaşım doğru. Plan modu ile araştır ve tasarla, doğrudan çalıştırma ile uygula.
>
> **C)** Hayır — tüm süreç doğrudan çalıştırma olmalı, 30 dosya az sayı.
>
> **D)** Hayır — plan modu yerine Explore alt-agent'ı kullanılmalı.

### Doğru Cevap: B

**Neden B doğru:** Hybrid yaklaşım (plan → doğrudan çalıştırma) yaygın ve beklenen bir kalıptır. Plan moduyla 30 dosyadaki lodash kullanımlarını keşfet, hangi native fonksiyonlarla değiştirileceğini belirle, sonra doğrudan çalıştırma ile uygula. En verimli yaklaşım.

**Neden A yanlış:** Plan modunda uygulamaya geçmek gereksiz yavaşlık. Plan tamamlandıktan sonra doğrudan çalıştırma daha hızlı.

**Neden C yanlış:** 30 dosyalık migrasyon keşif ve planlama gerektirir. Doğrudan çalıştırma ile başlamak sorunlara yol açar.

**Neden D yanlış:** Explore alt-agent'ı keşif aşamasının bir parçası olabilir ama tek başına yetmez. Plan modu keşif + tasarımı kapsar. Explore, çok detaylı keşif çıktısını izole etmek gerektiğinde ek olarak kullanılır.

---

## Soru 7 (Task Statement 3.5)

> Bir developer Claude Code'a şu talimatı veriyor:
>
> *"Hata mesajlarını daha kullanıcı dostu yap — teknik jargonu kaldır ve açıklayıcı mesajlar yaz."*
>
> Claude Code her seferinde farklı sonuç üretiyor — bazen çok resmi, bazen çok informal, bazen Türkçe karışımlı. Tutarsız.
>
> **İlk denenmesi gereken teknik hangisidir?**
>
> **A)** Prompt'a "tutarlı ol" talimatı ekle.
>
> **B)** 2-3 somut girdi/çıktı örneği ver — eski hata mesajı → yeni hata mesajı şeklinde before/after örnekleri.
>
> **C)** Her hata mesajı için ayrı bir komut oluştur.
>
> **D)** Claude Code'u test modunda çalıştır ve her çıktıyı manuel olarak kontrol et.

### Doğru Cevap: B

**Neden B doğru:** Düzyazı talimat tutarsız yorumlanıyor — "kullanıcı dostu" herkes için farklı bir şey ifade ediyor. Somut örnekler kesindir — "bu eski mesajı ver, bu yeni mesajı al" şeklinde 2-3 before/after örneği, modelin desen çıkarmasını ve tutarlı uygulamasını sağlar.

**Neden A yanlış:** "Tutarlı ol" da bir düzyazı talimat — belirsiz. Claude zaten tutarlı olmaya çalışıyor, sorun talimatın belirsizliği.

**Neden C yanlış:** Aşırı mühendislik. Yüzlerce hata mesajı için yüzlerce komut oluşturmak pratik değil. 2-3 örnek çok daha basit ve etkili.

**Neden D yanlış:** Manuel kontrol sürdürülebilir değil. Otomatik iyileştirme yerine her çıktıyı kontrol etmek Claude Code'un avantajını kaybettirir.

---

## Soru 8 (Task Statement 3.6)

> Bir takım CI pipeline'ında Claude Code ile otomatik test üretimi yapıyor. Üretilen testler:
>
> - Boş test çerçevelerinden oluşuyor — gerçek iş mantığını test etmiyor
> - Mevcut fixture'ları kullanmıyor — her testte sıfırdan mock oluşturuyor
> - Framework tutarsız — bazen jest, bazen vitest kullanıyor
>
> Pipeline komutu: `claude -p "Generate tests for the changed files"`
>
> **Kök neden ve çözüm nedir?**
>
> **A)** `-p` flag'i test kalitesini düşürüyor — etkileşimli modda çalıştırılmalı.
>
> **B)** CLAUDE.md dosyasında test standartları, değerli test kriterleri ve mevcut fixture'lar belgelenmemiş. Bu bilgileri CLAUDE.md'ye eklemek, Claude Code'un yüksek kaliteli, standartlara uygun testler üretmesini sağlar.
>
> **C)** Claude Code test üretimi için uygun değil — başka bir araç kullanılmalı.
>
> **D)** Her test dosyası için ayrı bir prompt yazılmalı.

### Doğru Cevap: B

**Neden B doğru:** Claude Code CLAUDE.md dosyasından proje bağlamını alır. Test standartları, framework tercihi (vitest), fixture'lar ve değerli test kriterleri CLAUDE.md'de belgelenmemişse, Claude Code genel şablon testler üretir. Bu bilgileri eklediğinde: doğru framework, mevcut fixture'lar, iş mantığını test eden anlamlı testler üretir.

**Neden A yanlış:** `-p` flag'i test kalitesini etkilemez — sadece etkileşimli girdi beklemesini kapatır. CI'da zorunlu. Kalite sorunu bağlam eksikliğinden kaynaklanıyor.

**Neden C yanlış:** Claude Code test üretimi yapabilir — doğru bağlam verildiğinde. Sorun aracın yeteneği değil, konfigürasyon eksikliği.

**Neden D yanlış:** Her dosya için ayrı prompt sürdürülebilir değil. CLAUDE.md ile standartları bir kez tanımla, her çalıştırmada otomatik uygulanır.
