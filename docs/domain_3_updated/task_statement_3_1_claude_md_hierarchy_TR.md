# Task Statement 3.1: CLAUDE.md Hiyerarşisi

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code çalıştığında, **nasıl davranacağını** belirleyen `CLAUDE.md` adlı talimat dosyalarını arar. Kodlama standartları, isimlendirme kuralları, test gereksinimleri, projeye özgü bağlam — hepsi bu dosyalarda tanımlanır. Bunu, kod tabanın için **kalıcı bir system prompt** olarak düşün.

Kritik nokta: **Üç seviye var** ve sınav, hangi seviyenin ne işe yaradığını bilip bilmediğini sürekli test ediyor. İkinci kritik nokta: CLAUDE.md **bağlamdır, zorlama değildir** — resmi ifadeyle "Claude treats them as context, not enforced configuration." Bir eylemin *her seferinde, istisnasız* engellenmesi gerekiyorsa çözüm CLAUDE.md değil, **hook**'tur (bkz. Domain 1.4 / 1.5).

---

## Üç Seviye (Sınavın Saydığı)

### 1. Kullanıcı Seviyesi: `~/.claude/CLAUDE.md`

- Senin **ev dizininde** bulunur
- **Sadece SANA** uygulanır — ama **makinendeki HER projede**
- **Versiyon kontrol altında DEĞİL** — Git'te yok, paylaşılmaz
- Repoyu klonlayan yeni takım üyeleri bu talimatları **ALMAZ**
- **Kullanım alanı:** Projeden bağımsız kişisel tercihler (kod stili, kişisel kısayollar)
- **Tuzak:** Projeye özgü bir şeyi (staging URL'i, test verisi) buraya yazarsan **diğer projelerine de sızar** — onun yeri `CLAUDE.local.md` (aşağıda)

### 2. Proje Seviyesi: `.claude/CLAUDE.md` veya kök dizindeki `CLAUDE.md`

- **Repoda** bulunur
- **Versiyon kontrol altında** — Git ile takip edilir, paylaşılır
- Repoyu klonlayan **HERKES** bu talimatları alır
- **Kullanım alanı:** Takım genelindeki standartlar, build/test komutları, API kuralları, isimlendirme kuralları, mimari kararlar

### 3. Dizin Seviyesi: Alt dizin içindeki `CLAUDE.md` dosyaları

- Claude Code **o dizindeki (ve altındaki) dosyalar** üzerinde çalışırken uygulanır
- **Başlangıçta yüklenmez** — Claude o alt dizindeki bir dosyayı okuduğunda *talep üzerine* yüklenir (lazy loading)
- **Kullanım alanı:** Pakete özgü kurallar (örneğin, `frontend/` klasörü `backend/`'den farklı kurallara sahip)

### Sınavın Saymadığı Ama Bilmen Gereken İki Konum

| Konum | Ne | Neden önemli |
|---|---|---|
| `./CLAUDE.local.md` | Proje kökünde, `.gitignore`'a eklenen **kişisel + projeye özgü** dosya (sandbox URL'leri, tercih edilen test verisi) | "Kişisel ama yalnızca bu projede" senaryosunun doğru cevabı — `~/.claude/CLAUDE.md` değil |
| Managed policy CLAUDE.md (`/etc/claude-code/CLAUDE.md`, macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`) | IT/DevOps'un dağıttığı **kurum geneli** dosya; bireysel ayarla devre dışı bırakılamaz | 40 kişilik ekipte güvenlik/uyum kurallarının yeri |

> **Sınav kuralı:** Exam guide üç seviye sayar → "kaç seviye?" sorusunun cevabı **üç**. `CLAUDE.local.md` ve managed policy, şıklarda *distractor* ya da "en uygun konum" sorusunun cevabı olarak çıkabilir.

---

## Özet Tablo

| Seviye | Konum | Paylaşılır mı? | Git'te mi? | Kimin için? | Ne zaman yüklenir? |
|---|---|---|---|---|---|
| Managed | `/etc/claude-code/CLAUDE.md` vb. | ✅ (kurum) | ❌ (MDM ile dağıtılır) | Makinedeki herkes | Başlangıçta, en önce |
| Kullanıcı | `~/.claude/CLAUDE.md` | ❌ Hayır | ❌ Hayır | Sadece sen, tüm projeler | Başlangıçta |
| Proje | `.claude/CLAUDE.md` veya kök `CLAUDE.md` | ✅ Evet | ✅ Evet | Tüm takım | Başlangıçta |
| Yerel | `./CLAUDE.local.md` | ❌ Hayır | ❌ (`.gitignore`) | Sadece sen, bu proje | Başlangıçta, proje dosyasından sonra |
| Dizin | Alt dizindeki `CLAUDE.md` | ✅ Evet | ✅ Evet | O alt ağaçta çalışanlar | **Talep üzerine** (o dizinde dosya okununca) |

---

## Yükleme Mekanizması — "Hangi Seviye Kazanır?"

Bu, sınavın dolaylı sorduğu ama dokümanların çoğunun atladığı nokta:

- Claude Code çalışma dizini **ve üstündeki tüm dizinlerdeki** `CLAUDE.md` / `CLAUDE.local.md` dosyalarını **başlangıçta** yükler. `foo/bar/` içinde başlatırsan `foo/CLAUDE.md` ve `foo/bar/CLAUDE.md` ikisi de gelir.
- **Alt dizinlerdeki** dosyalar başlangıçta yüklenmez; Claude o dizindeki bir dosyayı okuduğunda eklenir.
- Bulunan tüm dosyalar bağlama **art arda eklenir** (kök dizinden çalışma dizinine doğru; her seviyede `CLAUDE.local.md`, `CLAUDE.md`'den sonra). **Hiçbir seviye diğerini ezmez.**
- Sonuç: İki dosyada **çelişen** kural varsa Claude *herhangi birini* uygulayabilir. Çözüm "öncelik ayarlamak" değil, **çelişkiyi kaldırmak**.

> **Sınav kuralı:** "Proje CLAUDE.md'si kullanıcı CLAUDE.md'sini geçersiz kılar" şıkkı **yanlıştır** — ikisi birleştirilir.

---

## Modüler Organizasyon

Her şeyi tek bir devasa `CLAUDE.md` dosyasına tıkmak zorunda değilsin. İki mekanizma var:

### `@yol` İmport Sözdizimi (Sınavın adıyla: "@import syntax")

`CLAUDE.md` içinden dış dosyaları `@dosya/yolu` ile referans edebilirsin. **"import" diye bir kelime yazılmaz** — `@` işareti doğrudan yolun önüne gelir ve cümlenin içinde durabilir:

```markdown
Proje özeti için @README, npm komutları için @package.json dosyasına bak.

# Standartlar
@docs/standards/api-conventions.md
@docs/standards/testing-rules.md

# Kişisel tercihler (worktree'ler arasında paylaşmak için)
@~/.claude/my-project-instructions.md
```

Her paket için ilgili standartları içe aktarabilirsin — temiz ve modüler.

**Bilmen gereken kurallar:**
- Göreli yollar **import eden dosyaya göre** çözülür (çalışma dizinine göre değil)
- İmport edilen dosya başka dosyaları import edebilir — en fazla **4 seviye**
- Backtick veya kod bloğu içindeki `@yol` **import edilmez** (`` `@README` `` düz metindir)
- Çalışma dizini **dışına** çıkan import'lar (`@~/...`) ilk seferde onay diyaloğu açar — repoya başkasının koyduğu dosyalara karşı koruma
- **İmport'lar başlangıçta yüklenir.** Token tasarrufu *sağlamaz*, yalnızca **organizasyon** sağlar. Token tasarrufu isteyen iki mekanizma: alt dizin CLAUDE.md'leri ve path-scoped rules (Task 3.3).

> **Sınav kuralı:** Exam guide bu özelliğe **"@import syntax"** der. Sınavda terimi böyle tanı; kodda `@yol` yaz.

### `.claude/rules/` Dizini

Konuya özel kural dosyalarını bu dizine koyabilirsin:

- `testing.md` — test kuralları
- `api-conventions.md` — API kuralları
- `deployment.md` — dağıtım kuralları

Tek büyük dosya yerine organize edilmiş, konuya göre ayrılmış kurallar.

**Tanım (3.2 ve 3.3 ile aynı):** `.claude/rules/*.md` dosyaları; başında `paths` frontmatter'ı **yoksa** her oturumda başlangıçta, `.claude/CLAUDE.md` ile aynı öncelikte yüklenir; **varsa** yalnızca eşleşen dosyalarla çalışırken yüklenir (Task 3.3). `.md` dosyaları alt klasörlerde (`rules/frontend/`, `rules/backend/`) özyinelemeli keşfedilir. `~/.claude/rules/` ile **kişisel** kurallar da tanımlanabilir (tüm projeler). Paylaşılan kural setleri symlink ile bağlanabilir.

---

## İyi Bir CLAUDE.md Nasıl Yazılır? (Kurs modülü: "A CLAUDE.md That Follows")

- **`/init`** komutu kod tabanını analiz edip başlangıç CLAUDE.md'si üretir; dosya varsa iyileştirme önerir.
- **Boyut:** dosya başına **200 satır altı** hedefle. Şişmiş CLAUDE.md'de Claude kuralların yarısını görmezden gelir — "kural yazılı ama uygulanmıyor" senaryosunun en yaygın cevabı **budama**dır.
- **Somutluk:** "Format code properly" değil "2-space indentation"; "Test your changes" değil "Run `npm test` before committing".
- **Ne koyma:** Claude'un koddan çıkarabileceği şeyler, standart dil kuralları, sık değişen bilgi, dosya dosya kod tabanı açıklaması. Her satır için: *"Bunu silsem Claude hata yapar mı?"* Hayırsa sil.
- **Çok adımlı prosedür** (migrasyon adımları) CLAUDE.md'ye değil skill'e (Task 3.2); **yalnızca belirli dosyalara** uygulanan kural path-scoped rule'a (Task 3.3).
- Doğrulama: `/context` ile dosyanın **Memory files** altında listelendiğini gör.

---

## Hata Ayıklama Araçları: `/memory` ve `/context`

Claude Code oturumlar arasında tutarsız davranıyorsa iki komut var:

| Komut | Ne yapar | Sınav |
|---|---|---|
| `/memory` | Kullanıcı ve proje kapsamındaki CLAUDE.md / CLAUDE.local.md konumlarını **listeler ve editörde açar**; auto memory'yi açıp kapatır | Exam guide: "verify which memory files are loaded and diagnose inconsistent behavior" → **sınav cevabı `/memory`** |
| `/context` | **Bu oturumda gerçekten yüklenen** CLAUDE.md ve rules dosyalarını **Memory files** altında gösterir | Pratikte asıl teşhis aracı |

"Bende çalışıyor ama takım arkadaşımda çalışmıyor" sorusunu teşhis etmenin yolu: iki makinede `/memory` (veya `/context`) çıktısını karşılaştır — fark genellikle `~/.claude/CLAUDE.md`'dedir.

---

## Sınavın Favori Tuzağı — Yeni Takım Üyesi Sorunu

Bu senaryo neredeyse her sınav setinde karşına çıkacak:

> Developer A'nın Claude Code'u takımın isimlendirme kurallarını mükemmel uyguluyor. Geçen hafta katılan Developer B ise Claude Code'dan tutarsız isimler alıyor. İkisi de aynı repo üzerinde çalışıyor.

**Kök neden:** Kurallar Developer A'nın **kullanıcı seviyesi** konfigürasyonunda (`~/.claude/CLAUDE.md`). Bu dosya Git'te yok, paylaşılmıyor. Developer B bu talimatları hiç almıyor.

**Çözüm:** Talimatları `.claude/CLAUDE.md` dosyasına (proje seviyesi) taşı — versiyon kontrol altında ve paylaşılır.

> **Sınav kuralı:** "Yeni takım üyesi talimatları almıyor" → cevap neredeyse her zaman: **talimatlar kullanıcı seviyesinde, proje seviyesine taşınmalı.**

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Kullanıcı seviyesi (`~/.claude/CLAUDE.md`) | Sadece sana, **tüm projelerde** — Git'te yok, paylaşılmaz |
| Proje seviyesi (`.claude/CLAUDE.md`) | Herkese uygulanır — Git'te, paylaşılır |
| Dizin seviyesi (alt dizindeki `CLAUDE.md`) | O alt ağaçta çalışırken, **talep üzerine** yüklenir |
| `CLAUDE.local.md` | Kişisel + projeye özgü, `.gitignore`'da — sınav saymaz ama şıkta çıkar |
| Yükleme | Dosyalar **birleştirilir**, hiçbiri diğerini ezmez; çelişki → Claude rastgele seçer |
| `@yol` ("@import syntax") | Dış dosyayı referans et — modüler; **başlangıçta yüklenir**, token tasarrufu yok |
| `.claude/rules/` | Konuya özel kural dosyaları; `paths` yoksa her zaman, varsa koşullu |
| `/memory` | Bellek dosyalarını listele/aç — sınavın "hangi dosyalar yüklü" cevabı |
| `/context` | Bu oturumda gerçekten yüklenenleri gösterir |
| CLAUDE.md = bağlam | Zorlama değil; istisnasız kural → hook |
| 200 satır | Şişmiş dosya → kurallar görmezden gelinir → buda / rules'a böl / skill'e taşı |
| Sınav tuzağı | Yeni üye talimatları almıyor → talimatlar kullanıcı seviyesinde |

---

## Pratik Senaryo 1

> Developer A ve Developer B aynı repoyu klonlayarak çalışıyor. Developer A, Claude Code'dan mükemmel API isimlendirme kuralları alıyor. Developer B ise tutarsız isimler alıyor. İkisi de aynı branch üzerinde çalışıyor.
>
> **Kök neden nedir?**
>
> **A)** Developer B'nin Claude Code sürümü eski — güncellenmeli.
>
> **B)** API isimlendirme kuralları Developer A'nın kullanıcı seviyesi konfigürasyonunda (`~/.claude/CLAUDE.md`) — proje seviyesine (`.claude/CLAUDE.md`) taşınmalı.
>
> **C)** Developer B'nin bilgisayarında Claude Code cache'i bozulmuş — cache temizlenmeli.
>
> **D)** Her iki developer da `/memory` komutuyla belleklerini senkronize etmeli.

### Doğru Cevap: B

**Neden B doğru:** Klasik sınav tuzağı. Developer A talimatları alıyor, Developer B almıyor, aynı repo — tek fark Developer A'nın kişisel konfigürasyonu. `~/.claude/CLAUDE.md` dosyası Git'te yok, paylaşılmaz. Çözüm: `.claude/CLAUDE.md` dosyasına taşı, herkes alsın.

**Neden A yanlış:** Sürüm farkı bu tür bir davranış farkını açıklamaz. İki developer da aracı kullanabiliyor — sorun talimatların eksikliğinde.

**Neden C yanlış:** Cache sorunu talimatların tamamen eksik olmasını açıklamaz. Sorun yapısal — dosya yeri.

**Neden D yanlış:** `/memory` komutu teşhis aracıdır, senkronizasyon aracı değil. Bellek dosyalarını gösterir ama başka birinin dosyalarını kopyalamaz.

---

## Pratik Senaryo 2

> Bir takım büyük bir projede çalışıyor. Proje kök dizininde `.claude/CLAUDE.md` dosyası var ve genel kodlama standartlarını içeriyor. Ancak `frontend/` klasöründe React'e özgü kurallar, `backend/` klasöründe ise Go'ya özgü kurallar gerekiyor. Takım, backend'de çalışırken React kurallarının bağlamda **hiç yer kaplamamasını** istiyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Tüm kuralları (genel + React + Go) tek bir kök `.claude/CLAUDE.md` dosyasına yaz.
>
> **B)** `frontend/CLAUDE.md` ve `backend/CLAUDE.md` dizin seviyesi dosyaları oluştur — Claude Code o dizindeki dosyalar üzerinde çalışırken ilgili kuralları yüklesin.
>
> **C)** Kök `.claude/CLAUDE.md` içinden `@docs/react-rules.md` ve `@docs/go-rules.md` ile iki dosyayı import et.
>
> **D)** Her developer kendi `~/.claude/CLAUDE.md` dosyasına çalıştığı alana göre kuralları yazmalı.

### Doğru Cevap: B

**Neden B doğru:** Dizin seviyesi CLAUDE.md dosyaları tam olarak bu amaç için var — farklı alt dizinlerdeki farklı teknoloji gereksinimleri. `frontend/CLAUDE.md` React kurallarını, `backend/CLAUDE.md` Go kurallarını içerir. Her iki dosya da Git'te, paylaşılır ve **yalnızca o dizindeki dosyalar okunduğunda talep üzerine** yüklenir — backend'de çalışırken React kuralları bağlama hiç girmez.

**Neden A yanlış:** Tüm kuralları tek dosyaya tıkmak gereksiz token kullanımı yaratır. Backend'de çalışırken React kurallarını yüklemek bağlamı kirletir; ayrıca dosya şişer ve kurallar görmezden gelinmeye başlar.

**Neden C yanlış:** Bu en çekici distractor. `@yol` import'u **organizasyon** sağlar ama import edilen dosyalar kök CLAUDE.md ile birlikte **başlangıçta** yüklenir — backend'de çalışırken React kuralları yine bağlamda olur. Gereksinim "hiç yer kaplamasın" olduğu için import yetersiz. (Gereksinim yalnızca "tek dosya şişmesin" olsaydı C de kabul edilebilirdi.)

**Neden D yanlış:** Kullanıcı seviyesi konfigürasyonu paylaşılmaz ve tüm projelere sızar. Yeni takım üyeleri bu kuralları almaz; standartlaşma sağlanamaz.

---

## Pratik Senaryo 3

> Bir developer, projenin staging ortamının URL'ini ve kendi test hesabının bilgilerini Claude Code'un her oturumda bilmesini istiyor. Bu bilgiler kişisel — takımla paylaşılmamalı ve repoya girmemeli. Ancak developer başka projelerde çalışırken bu bilgilerin bağlamda **olmamasını** istiyor.
>
> **Bilgiler nereye yazılmalı?**
>
> **A)** `~/.claude/CLAUDE.md` — kişisel, paylaşılmaz.
>
> **B)** `.claude/CLAUDE.md` — proje seviyesi, her oturumda yüklenir.
>
> **C)** Proje kökünde `CLAUDE.local.md` — `.gitignore`'a eklenmiş.
>
> **D)** `.claude/rules/staging.md` — konuya özel kural dosyası.

### Doğru Cevap: C

**Neden C doğru:** İki kısıt var: kişisel (repoya girmesin) **ve** projeye özgü (diğer projelere sızmasın). `CLAUDE.local.md` tam bu kesişim için tasarlandı — proje kökünde durur, `CLAUDE.md` ile birlikte yüklenir, `.gitignore`'a eklenir.

**Neden A yanlış:** `~/.claude/CLAUDE.md` kişiseldir ama makinedeki **her projede** yüklenir — başka bir projede çalışırken staging URL'i bağlama girer, hatta Claude onu yanlış projede kullanmaya kalkabilir.

**Neden B yanlış:** Proje seviyesi dosya Git'e girer; kişisel hesap bilgileri takımla paylaşılır.

**Neden D yanlış:** `.claude/rules/` proje kapsamındadır ve Git'e girer; ayrıca "kural" değil, kişisel bağlam söz konusu.
