# Domain 3 — Pratik Sınav

## Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

**Dağılım (10 soru):**
- 2 soru → CLAUDE.md Hiyerarşisi (3.1)
- 2 soru → Özel Komutlar ve Skill'ler (3.2)
- 1 soru → Yol-Bazlı Kurallar (3.3)
- 2 soru → Plan Modu vs Doğrudan Çalıştırma (3.4)
- 1 soru → Yinelemeli İyileştirme (3.5)
- 2 soru → CI/CD Entegrasyonu (3.6)

**Geçme kriteri:** 8+/10

| Soru | Task Statement | Test edilen kavram |
|---|---|---|
| 1 | 3.1 | `CLAUDE.local.md` vs `~/.claude/CLAUDE.md` |
| 2 | 3.1 | `@yol` import başlangıçta yüklenir vs dizin CLAUDE.md talep üzerine |
| 3 | 3.2 | `allowed-tools` (sınav dili) + `context: fork` + kişisel skill |
| 4 | 3.2 | `disable-model-invocation` — yan etkili skill'i yalnızca kullanıcı çağırsın |
| 5 | 3.3 | Dağınık API dosyaları → glob kuralı; deterministik vs olasılıksal |
| 6 | 3.4 | "Önce doğrudan, gerekirse plan" tuzağı |
| 7 | 3.4 | Explore salt-okunur; hybrid akış |
| 8 | 3.5 | Etkileşen düzeltmeler → tek mesaj |
| 9 | 3.6 | `-p` var ama değişiklik yok → izinler |
| 10 | 3.6 | Yinelenen test senaryoları → mevcut testleri bağlama ver (CLAUDE.md'den ayrı) |

---

## Soru 1 (Task Statement 3.1)

> Bir developer, çalıştığı e-ticaret projesinde Claude Code'un her oturumda kendi lokal sandbox URL'ini (`http://localhost:4010`) ve kendi test müşteri kimliğini bilmesini istiyor. Bu bilgiler kişisel — repoya girmemeli. Developer aynı zamanda iki başka projede de çalışıyor ve bu bilgilerin o projelerde bağlamda **görünmemesini** istiyor.
>
> **En uygun konum hangisidir?**
>
> **A)** `~/.claude/CLAUDE.md` — kişisel, Git'te değil.
>
> **B)** Proje kökünde `CLAUDE.local.md`, `.gitignore`'a eklenmiş.
>
> **C)** `.claude/CLAUDE.md` — proje seviyesi, her oturumda yüklenir.
>
> **D)** `.claude/rules/sandbox.md`, `paths: ["**/*"]` frontmatter'ı ile.

### Doğru Cevap: B

**Neden B doğru:** İki kısıt: kişisel (repoya girmesin) **ve** projeye özgü (diğer projelere sızmasın). `CLAUDE.local.md` tam bu kesişim için var — proje kökünde durur, `CLAUDE.md` ile birlikte yüklenir, `.gitignore`'a eklenir.

**Neden A yanlış:** `~/.claude/CLAUDE.md` kişiseldir ama makinedeki **her projede** yüklenir — diğer iki projede sandbox URL'i bağlama girer.

**Neden C yanlış:** Proje seviyesi dosya Git'e girer; kişisel test kimliği takımla paylaşılır.

**Neden D yanlış:** `.claude/rules/` proje kapsamındadır ve Git'e girer; ayrıca `**/*` deseni "her dosya" demektir — koşulsuz kuralla aynı, kişisellik sağlamaz.

---

## Soru 2 (Task Statement 3.1)

> Bir monorepo'nun kök `.claude/CLAUDE.md` dosyası 600 satıra ulaştı: genel standartlar + `web/` için React kuralları + `api/` için Go kuralları + `infra/` için Terraform kuralları. Takım iki şikâyette bulunuyor: (1) Claude bazı kuralları görmezden geliyor, (2) `api/` içinde çalışırken bile React kuralları token harcıyor.
>
> Bir developer şu çözümü öneriyor: kök dosyayı dört parçaya bölüp `@docs/react.md`, `@docs/go.md`, `@docs/terraform.md` ile import etmek.
>
> **Bu öneri iki şikâyetin hangisini çözer?**
>
> **A)** İkisini de — import edilen dosyalar yalnızca ilgili dizinde çalışırken yüklenir.
>
> **B)** Yalnızca (1)'i kısmen — dosya organize olur ama import edilen dosyalar **başlangıçta** birlikte yüklenir; toplam bağlam aynı kalır, React kuralları `api/`'de de harcanmaya devam eder. (2) için `web/CLAUDE.md`, `api/CLAUDE.md`, `infra/CLAUDE.md` dizin seviyesi dosyaları (talep üzerine yüklenir) gerekir.
>
> **C)** Hiçbirini — import sözdizimi yalnızca `~/.claude/CLAUDE.md`'de çalışır.
>
> **D)** Yalnızca (2)'yi — import'lar tembel yüklenir ama dosya boyutu değişmez.

### Doğru Cevap: B

**Neden B doğru:** `@yol` import'u **organizasyon** aracıdır: dosyalar başlangıçta CLAUDE.md ile birlikte bağlama girer, token tasarrufu sağlamaz. Şişkinliğin görmezden gelinen kurallara yol açması (şikâyet 1) kısmen düzelir çünkü dosya okunabilir hale gelir; ama asıl çözüm toplam yüklü metni azaltmaktır. Bunu yalnızca **talep üzerine** yüklenen mekanizmalar yapar: dizin seviyesi CLAUDE.md (o dizindeki dosya okununca) veya `paths` kuralları.

**Neden A yanlış:** Import'lar tembel yüklenmez; bu, 3.1 ile 3.3'ün en çok karıştırıldığı nokta.

**Neden C yanlış:** Import her CLAUDE.md'de çalışır (göreli yol import eden dosyaya göre çözülür).

**Neden D yanlış:** Tam tersi — import'lar başlangıçta yüklenir; (2) çözülmez.

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
> **B)** `/deploy-checklist` → `.claude/commands/` (proje kapsamlı). `/deep-analyze` → `~/.claude/skills/deep-analyze/SKILL.md` olarak, `context: fork`, `agent: Explore` ve `allowed-tools: Read Grep Glob` frontmatter'ı ile.
>
> **C)** Her ikisi de CLAUDE.md dosyasına prosedür olarak yazılmalı.
>
> **D)** `/deploy-checklist` → `~/.claude/commands/`. `/deep-analyze` → `.claude/skills/`.

### Doğru Cevap: B

**Neden B doğru:** Üç gereksinimi de karşılıyor:
1. `/deploy-checklist` takım genelinde → `.claude/commands/` (proje kapsamlı, Git'te, paylaşılır — exam guide Q4)
2. `/deep-analyze` kişisel ve detaylı çıktı → `~/.claude/skills/` (kişisel) + `context: fork` (izole bağlam, ana konuşma temiz)
3. Sadece okuma araçları → sınav dilinde `allowed-tools: Read Grep Glob`. **Not:** Gerçek davranışta `allowed-tools` *ön-onaylar*, kısıtlamaz; gerçek kısıtlama `disallowed-tools: Write, Edit, Bash` ya da `agent: Explore` (Write/Edit'i zaten reddeder) ile sağlanır. Bu şıkta `agent: Explore` o garantiyi de veriyor.

**Neden A yanlış:** `/deep-analyze` kişisel istek — takım reposuna koymak herkese dağıtır. `context: fork` / araç kısıtı frontmatter'ı da skill dizin yapısında tanımlanır.

**Neden C yanlış:** Bunlar göreve özgü prosedürler — CLAUDE.md evrensel standartlar için, her zaman yüklü.

**Neden D yanlış:** Tam tersi yerleştirme. `/deploy-checklist` takım genelinde olmalı; `/deep-analyze` kişisel olmalı.

---

## Soru 4 (Task Statement 3.2)

> Bir takım `.claude/skills/release/SKILL.md` adlı bir skill oluşturdu: sürüm etiketi atar, changelog üretir ve `git push --tags` çalıştırır. Skill'in `description`'ı "Yeni bir sürüm yayınlar" şeklinde. Bir developer "bu değişikliklerin bir sonraki sürüme girip girmeyeceğini düşünüyorum" diye sohbet ederken Claude skill'i kendiliğinden yükleyip sürüm yayınlama adımlarına başlıyor.
>
> **Doğru düzeltme hangisidir?**
>
> **A)** Skill'i `~/.claude/skills/` dizinine taşı — kişisel skill'ler otomatik tetiklenmez.
>
> **B)** Frontmatter'a `disable-model-invocation: true` ekle — skill yalnızca kullanıcı `/release` yazınca yüklensin; Claude description eşleşmesiyle çağıramasın.
>
> **C)** `context: fork` ekle — skill izole bağlamda çalışsın.
>
> **D)** `allowed-tools: Bash(git push *)` kaldır — Claude push yapamasın.

### Doğru Cevap: B

**Neden B doğru:** Skill'ler iki yoldan tetiklenir: kullanıcı `/ad` yazar **veya** Claude `description`'ın konuşmayla eşleştiğine karar verir. Yan etkili iş akışlarında (deploy, release, commit) ikinci yol tehlikelidir. `disable-model-invocation: true` tam bu durum için var: "Only you can invoke it manually." Resmi best-practices örneği de bunu kullanır (`fix-issue` skill'i).

**Neden A yanlış:** Kişisel skill'ler de description'a göre otomatik tetiklenir; konum tetikleme yolunu değiştirmez.

**Neden C yanlış:** Fork, çıktıyı izole eder; skill'in yanlışlıkla *başlamasını* engellemez — arka planda release yapmaya devam eder.

**Neden D yanlış:** `allowed-tools`'u kaldırmak yalnızca izin istemini geri getirir; skill yine tetiklenir, adımlara başlar ve push için izin sorar. Kök neden tetikleme, izin değil.

---

## Soru 5 (Task Statement 3.3)

> Bir kod tabanında API endpoint dosyaları `src/api/`, `src/routes/` ve `modules/*/api/` dizinlerinde dağınık olarak bulunuyor. Takım tüm API dosyalarında aynı kuralları uygulamak istiyor: rate limiting kontrolü, input validation, standardize edilmiş hata yanıtları. Kuralların **Claude'un takdirine bırakılmadan, otomatik** uygulanması gerekiyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** `src/api/CLAUDE.md`, `src/routes/CLAUDE.md` ve her `modules/*/api/CLAUDE.md` dosyasına aynı kuralları kopyala.
>
> **B)** `.claude/rules/api-conventions.md` dosyası oluştur — `paths: ["src/api/**/*", "src/routes/**/*", "modules/*/api/**/*"]` frontmatter'ı ile.
>
> **C)** Kök CLAUDE.md dosyasına tüm API kurallarını yaz.
>
> **D)** Bir `/api-rules` skill'i oluştur — description'ına "API dosyası düzenlerken kullan" yaz, Claude gerektiğinde yüklesin.

### Doğru Cevap: B

**Neden B doğru:** Yol-bazlı kurallar glob pattern ile tüm kod tabanındaki API dosyalarını yakalar — hangi dizinde olursa olsun. Tek bir kural dosyası, dağınık API dosyalarının tamamına uygulanır; eşleşen dosya okununca **deterministik** olarak yüklenir. Token verimli — sadece API dosyasıyla çalışırken bağlamda.

**Neden A yanlış:** Her dizine aynı kuralları kopyalamak bakım kabusu. Bir kural değiştiğinde tüm kopyaları güncellemek gerekir. CLAUDE.md dosyaları dizine bağlıdır.

**Neden C yanlış:** Kök CLAUDE.md her zaman yüklenir. Frontend CSS dosyası düzenlerken bile API kuralları bağlamda yer kaplar — token israfı ve dosya şişmesi.

**Neden D yanlış:** En çekici distractor. Claude description'a göre skill'i *yükleyebilir* — ama bu **olasılıksal** bir karardır; "Claude'un takdirine bırakılmadan" gereksinimiyle çelişir. Exam guide Q6'nın C şıkkı gerekçesi: "relies on Claude choosing to load them, contradicting the need for deterministic automatic application based on file paths."

---

## Soru 6 (Task Statement 3.4)

> Bir developer'a "mevcut REST API'yi GraphQL'e dönüştür" görevi verildi: 40+ endpoint etkileniyor, şema tasarımı ve resolver yapısı hakkında kararlar gerekiyor. Developer şöyle düşünüyor: "Plan modu ek yük getirir. Doğrudan çalıştırma ile ilk birkaç endpoint'i dönüştüreyim; beklenmedik karmaşıklık çıkarsa plan moduna geçerim."
>
> **Bu yaklaşımın değerlendirmesi hangisidir?**
>
> **A)** Doğru — küçük adımlarla başlamak riski azaltır; karmaşıklık çıkınca planlamak verimlidir.
>
> **B)** Yanlış — karmaşıklık "beklenmedik" değil, gereksinimde zaten yazılı (40+ endpoint, şema kararları). Önce plan modunda keşif ve tasarım, onaydan sonra uygulama gerekir.
>
> **C)** Yanlış — görev tamamen Explore subagent'ına devredilmeli.
>
> **D)** Doğru — ama önce `/clear` ile bağlam temizlenmeli.

### Doğru Cevap: B

**Neden B doğru:** Exam guide Q5'in D şıkkının birebir karşılığı: "Begin in direct execution mode and only switch to plan mode if you encounter unexpected complexity" → resmi gerekçe: "ignores that the complexity is already stated in the requirements, not something that might emerge later." Çok dosya + mimari karar + birden fazla yaklaşım → plan modu. İlk endpoint'leri yanlış şema tasarımıyla dönüştürüp sonra plan yapmak maliyetli yeniden iştir.

**Neden A yanlış:** "Plan modu ek yük" heuristiği diff'i bir cümleyle anlatılabilen görevler içindir; 40 endpoint'lik dönüşüm bu sınıfta değildir.

**Neden C yanlış:** Explore salt-okunurdur; yalnızca keşif yapar, tasarım kararı vermez ve uygulamaz.

**Neden D yanlış:** `/clear` bağlamı sıfırlar; yanlış mod seçimini düzeltmez.

---

## Soru 7 (Task Statement 3.4)

> Bir developer 30 dosyada lodash kütüphanesini native JavaScript fonksiyonlarıyla değiştirmek istiyor. Yaklaşımını şöyle planlamış:
>
> 1. Plan modunda etkilenen dosyaları keşfet ve migrasyon stratejisini belirle
> 2. Planı onaylayıp doğrudan çalıştırma ile uygula
>
> Bir takım arkadaşı itiraz ediyor: "Keşif çok fazla dosya okuyacak, ana bağlam dolar. Keşfi ve **uygulamayı** Explore subagent'ına ver."
>
> **Hangi değerlendirme doğrudur?**
>
> **A)** Takım arkadaşı haklı — Explore hem keşfi izole eder hem de değişiklikleri yapar.
>
> **B)** Developer'ın yaklaşımı doğru (hybrid: plan → onay → doğrudan çalıştırma). Keşif zaten plan modunda Plan/Explore subagent'larına delege edilir, ana bağlam korunur; ama Explore **salt-okunurdur** (Write/Edit reddedilir) — uygulamayı yapamaz.
>
> **C)** İkisi de yanlış — 30 dosya az; tüm süreç doğrudan çalıştırma olmalı.
>
> **D)** İkisi de yanlış — tüm süreç plan modunda kalmalı, onay gerekmez.

### Doğru Cevap: B

**Neden B doğru:** Hybrid yaklaşım plan modunun normal yaşam döngüsüdür: keşif (subagent'larda) → plan → onay → uygulama. Takım arkadaşının endişesi (bağlam dolması) plan modunun yerleşik Explore/Plan delegasyonuyla zaten karşılanır. Ama önerisinin ikinci yarısı yanlış: Explore'un araç seti salt-okunurdur; değişiklik yapan yerleşik subagent `general-purpose`'tır ve zaten uygulama ana oturumda plan onayından sonra yapılır.

**Neden A yanlış:** Explore Write/Edit'i reddeder — uygulama yapamaz.

**Neden C yanlış:** 30 dosyalık migrasyon keşif ve planlama gerektirir; doğrudan başlamak yeniden iş yaratır.

**Neden D yanlış:** Plan modu dosya düzenleyemez; uygulama için onay ve mod değişimi şarttır.

---

## Soru 8 (Task Statement 3.5)

> Bir developer, Claude Code'un yazdığı bir ödeme fonksiyonunu inceliyor. İki bulgu var:
>
> 1. Para birimi dönüşümü yanlış yuvarlanıyor (kuruş kaybı)
> 2. Fonksiyonun döndürdüğü tutar, yuvarlama sonucuna göre loglanıyor ve fatura kaydına yazılıyor — yuvarlama değişince log formatı ve fatura alanı da değişmeli
>
> Developer önce yalnızca yuvarlamayı düzelttirdi; Claude bunu yaptı ama log ve fatura kodu eski davranışa göre kaldı. İkinci mesajda log/faturayı düzelttirince Claude yuvarlama fonksiyonunu yeniden yazdı.
>
> **Developer ne yapmalıydı?**
>
> **A)** İki bulguyu tek detaylı mesajda vermeliydi — düzeltmeler etkileşiyor; Claude tüm resmi görmeden tutarlı bir değişiklik yapamaz.
>
> **B)** Önce log/faturayı, sonra yuvarlamayı düzelttirmeliydi — sıra yanlıştı.
>
> **C)** Her bulgu için ayrı bir skill oluşturmalıydı.
>
> **D)** 2-3 somut girdi/çıktı örneği vermeliydi — düzyazı tutarsız yorumlanıyor.

### Doğru Cevap: A

**Neden A doğru:** Bulgular **etkileşiyor**: yuvarlama kararı, log formatını ve fatura alanını belirliyor. Sıralı verilince her tur diğerini bozuyor — tam olarak exam guide'ın "single detailed message when fixes interact" kuralının ihlali. Tek mesajda "yuvarlamayı şöyle düzelt **ve** log/fatura kodunu yeni sonuca göre güncelle" demek Claude'un tutarlı bir tasarım yapmasını sağlar.

**Neden B yanlış:** Sıra sorunu değil, etkileşim sorunu; hangi sırayla verilirse verilsin iki ayrı mesaj ikinci turda birinciyi yeniden yazdırır.

**Neden C yanlış:** Skill'ler tekrarlayan prosedürler içindir; tek seferlik düzeltmeler için aşırı mühendislik.

**Neden D yanlış:** Sorun düzyazının belirsizliği değil (Claude her düzeltmeyi doğru yaptı); sorun düzeltmelerin ayrı verilmesi.

---

## Soru 9 (Task Statement 3.6)

> Bir CI job'ı şu komutu çalıştırıyor:
>
> ```bash
> claude -p "Add missing null checks in src/services/" --output-format json
> ```
>
> Job asılı kalmıyor, çıkış kodu 0. Ama `result` alanında "I need permission to edit src/services/user.ts…" yazıyor ve hiçbir dosya değişmemiş.
>
> **Kök neden ve düzeltme nedir?**
>
> **A)** `-p` düzenlemeyi engelliyor — CI'da `-p` kaldırılmalı.
>
> **B)** `-p` oturumu Manual izin modunda başlar; CI'da izin istemine cevap verecek kimse olmadığından düzenlemeler reddediliyor. `--allowedTools "Edit"` (veya `--permission-mode acceptEdits`) eklenmeli.
>
> **C)** `--output-format json` düzenlemeyi kapatıyor — `text` kullanılmalı.
>
> **D)** Komut `timeout 600` ile sarılmalı.

### Doğru Cevap: B

**Neden B doğru:** `-p` yalnızca etkileşimli arayüzü kaldırır; izin sistemi çalışmaya devam eder ve `-p` Manual modda başlar. Düzenleme izni istenip cevap alınamayınca eylem reddedilir, Claude bunu metinle bildirir, süreç "başarıyla" çıkar. CI'da yapılacak işi önceden tanımla: `--allowedTools` ile araçlar/komutlar ya da `acceptEdits` / `dontAsk` / `auto` modu.

**Neden A yanlış:** `-p` olmadan pipeline asılı kalır. `-p` düzenlemeyi engellemez; izinler engeller.

**Neden C yanlış:** Çıktı formatı yalnızca sonucun yazdırılma biçimidir; izinlerle ilgisi yok.

**Neden D yanlış:** Süre sorunu değil; job zaten bitiyor. Timeout reddedilen izni onaylamaz.

---

## Soru 10 (Task Statement 3.6)

> Bir takım CI pipeline'ında `claude -p "Generate tests for the changed files"` ile otomatik test üretimi yapıyor. CLAUDE.md'de test standartları (vitest, describe/it), değerli test kriterleri ve fixture'lar belgelenmiş; üretilen testler framework ve stil açısından doğru. Ancak developer'lar şikâyet ediyor: "Claude her PR'da `tests/auth.test.ts` içinde zaten var olan senaryoların (geçersiz token, süresi dolmuş oturum) aynısını yeniden öneriyor."
>
> **Kök neden ve çözüm nedir?**
>
> **A)** CLAUDE.md'ye "yinelenen test yazma" kuralı eklenmeli.
>
> **B)** Claude mevcut test dosyalarını görmüyor — **mevcut test dosyalarını bağlama ver** (örn. `@tests/auth.test.ts` veya değişen modüllerin test dosyalarını prompt'a dahil et), böylece zaten kapsanan senaryoları önermesin.
>
> **C)** `-p` yerine etkileşimli mod kullanılmalı.
>
> **D)** `--json-schema` ile çıktı yapılandırılmalı.

### Doğru Cevap: B

**Neden B doğru:** Exam guide'ın CLAUDE.md'den **ayrı** saydığı Skills maddesi: "Providing existing test files in context so test generation avoids suggesting duplicate scenarios already covered by the test suite." CLAUDE.md *kuralları* verir (bu senaryoda zaten çalışıyor: framework ve stil doğru); *neyin zaten test edildiğini* ancak mevcut test dosyaları gösterir.

**Neden A yanlış:** "Yinelenen test yazma" kuralı, Claude neyin var olduğunu görmüyorsa uygulanamaz — bilgi eksikliği kuralla giderilmez.

**Neden C yanlış:** Etkileşimli mod CI'da asılı kalır; sorun mod değil, bağlam.

**Neden D yanlış:** Yapılandırılmış çıktı, çıktının *biçimini* düzenler; yinelenen *içeriği* engellemez.

---

## Puanlama

| Doğru | Değerlendirme |
|---|---|
| 10/10 | Domain 3 tamam — bir sonraki domain'e geç |
| 8–9/10 | Geçti — yanlış sorunun task statement'ını bir kez daha oku |
| 6–7/10 | İlgili task statement dosyalarını yeniden çalış, sınavı tekrarla |
| ≤5/10 | Domain 3'ü baştan çalış; özellikle 3.2 (tetikleme + `allowed-tools`) ve 3.6 (izinler) |
