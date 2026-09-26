# Task Statement 3.2: Özel Slash Komutları ve Skill'ler

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code'da tekrarlayan iş akışlarını **özel komutlar** ve **skill'ler** olarak tanımlayabilirsin. Bunlar `/review`, `/test-setup`, `/brainstorm` gibi slash komutlarıyla çağrılır. Sınav, bunların **nereye konulacağını**, **nasıl yapılandırılacağını** ve **CLAUDE.md'den farkını** bilmeni bekliyor.

Bir skill'i "paketlenmiş tekrar eden prosedür" olarak düşün (kurs modülü: *Verification Skills*): CLAUDE.md her oturumda yüklenen *gerçekler*dir, skill ise gerektiğinde yüklenen *prosedür*dür.

---

## Dizin Yapısı

### Proje Kapsamlı Komutlar (Paylaşılan)

```
.claude/commands/<ad>.md   →  /ad
```

- Proje deposunda bulunur
- **Versiyon kontrol altında** — Git ile paylaşılır
- Takımdaki herkes kullanabilir
- Örnek: `/review`, `/deploy-checklist`, `/test-all`

### Kişisel Komutlar (Paylaşılmayan)

```
~/.claude/commands/<ad>.md   →  /ad
```

- Kullanıcının ev dizininde bulunur
- **Paylaşılmaz** — sadece sen kullanırsın
- Takım arkadaşlarını etkilemez
- Örnek: Kişisel `/brainstorm`, `/quick-fix`

### Skill Dosyaları

```
.claude/skills/<ad>/SKILL.md     →  /ad   (proje, Git'te)
~/.claude/skills/<ad>/SKILL.md   →  /ad   (kişisel)
```

- Her skill kendi **dizininde**, içinde `SKILL.md` (zorunlu) + isteğe bağlı destekleyici dosyalar (`reference.md`, `examples.md`, `scripts/`)
- Komut adı **dizin adından** gelir
- YAML frontmatter ile yapılandırılır (aşağıda)

> **Güncel not (sınav cevabını değiştirmez):** `.claude/commands/<ad>.md` artık skill'lerin **legacy eşdeğeri** — hâlâ çalışır ve aynı şekilde `/ad` üretir; ama skill'ler destekleyici dosya ve ek frontmatter alanları taşıdığı için tercih edilir. Aynı isimde hem skill hem komut varsa **skill kazanır**. Exam guide ikisini ayrı sayıyor → sınavda "takım geneli `/review` komutu nereye?" sorusunun cevabı `.claude/commands/` (resmi örnek soru Q4).

---

## Skill'ler Nasıl Tetiklenir? — İki Yol

Bu ayrım dokümanların çoğunda eksik, sınavda ise örnek sorunun (Q6) gerekçesinde geçiyor:

| Yol | Nasıl | Kontrol alanı |
|---|---|---|
| **Kullanıcı** | `/ad argümanlar` yazar | `user-invocable: false` → `/` menüsünde görünmez, yalnızca Claude çağırır (arka plan bilgisi için) |
| **Claude** | Skill'in `description`'ı konuşmayla eşleşince **kendisi yükler** | `disable-model-invocation: true` → Claude otomatik çağıramaz, yalnızca kullanıcı (yan etkili iş akışları: deploy, commit, PR açma) |

Her skill'in `description`'ı **her zaman** bağlamdadır (Claude'un ne zaman çağıracağına karar verebilmesi için); tam içerik yalnızca çağrılınca yüklenir. Bu yüzden `description` "ne yapar + **ne zaman kullanılır**" içermeli.

> **Sınav kuralı:** "Skill'ler isteğe bağlıdır" doğru ama eksik. Skill'in yüklenmesi *olasılıksaldır* (kullanıcı hatırlar ya da Claude karar verir); path-scoped kuralın yüklenmesi *deterministiktir* (dosya yolu eşleşir). Exam guide Q6'nın C şıkkını tam bu gerekçeyle eler: "requires manual skill invocation **or relies on Claude choosing to load them**, contradicting the need for deterministic automatic application."

---

## SKILL.md Anatomisi

```markdown
---
name: deep-analyze
description: Bir modülün bağımlılık grafiğini çıkarır ve riskleri raporlar. Büyük refactor öncesi kullan.
argument-hint: [modül-yolu]
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools: Read Grep Glob
---

$ARGUMENTS modülünü analiz et:

## Mevcut durum
!`git log --oneline -10 -- $ARGUMENTS`

1. Glob ve Grep ile modülün dosyalarını bul
2. İçe/dışa aktarımları çıkar, bağımlılık grafiğini oluştur
3. Riskleri (döngüsel bağımlılık, test edilmemiş export) dosya referanslarıyla listele
```

| Öğe | Ne yapar |
|---|---|
| `$ARGUMENTS` | Çağrıdaki tüm argümanlar (`/deep-analyze src/auth` → `src/auth`); `$0`, `$1` ile tek tek (0-tabanlı); `arguments: [issue, branch]` ile isimli (`$issue`) |
| `` !`komut` `` | **Dinamik bağlam:** komut skill gönderilmeden *önce* çalışır, çıktısı yerine yazılır (`git diff HEAD`, `git status`) |
| Destekleyici dosyalar | `SKILL.md` **500 satır altı** tutulur; detay `reference.md`'ye, betikler `scripts/`'e (progressive disclosure) |
| `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}` | Skill dizini ve proje kökü yer tutucuları |

---

## Skill Frontmatter Seçenekleri — Sınavın Üç Kritik Alanı

### 1. `context: fork` — İzole Alt-Agent Bağlamı

```yaml
---
context: fork
agent: Explore
---
```

- Skill'i **izole bir alt-agent** bağlamında çalıştırır; skill içeriği alt-agent'ın **görev prompt'u** olur
- **`agent:`** hangi subagent'ta çalışacağını seçer: yerleşik `Explore` / `Plan` / `general-purpose` ya da `.claude/agents/`'taki özel bir agent — araç seti, izinler ve model o agent'tan gelir (bkz. Domain 1.3)
- Varsayılan olarak **arka planda** çalışır (sen çalışmaya devam edersin); `background: false` ile beklet
- Detaylı/gürültülü çıktı izole bağlamda kalır; **ana konuşmaya sadece özet döner**
- **Kullanım alanı:** Kod tabanı analizi, beyin fırtınası, keşif — çok fazla çıktı üreten her şey
- **Ne zaman KULLANMA:** Fork edilen skill **konuşma geçmişini görmez.** "Az önce yazdığın kodu gözden geçir" gibi bağlama muhtaç bir skill'e `context: fork` koyarsan alt-agent neyi inceleyeceğini bilemez. Bu, sınavın ters distractor'ıdır.

### 2. `allowed-tools` — Sınav Dili vs Gerçek Davranış

```yaml
---
allowed-tools: Read Grep Glob
---
# veya izin kuralı sözdizimiyle:
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
```

| | Ne diyor |
|---|---|
| **Sınav (exam guide)** | "Configuring allowed-tools in skill frontmatter to **restrict tool access** during skill execution … to prevent destructive actions." → Sınavda "skill yalnızca okuma araçlarını kullansın" sorusunun cevabı **`allowed-tools`**. |
| **Gerçek davranış (dokümantasyon)** | `allowed-tools` listelenen araçları **ön-onaylar** — skill'i çağıran tur boyunca izin istemi çıkmaz. "**Doesn't restrict which tools are available; every tool remains callable.**" Yani `allowed-tools: Read` yazan skill yine de Write çağırabilir (izin isteyerek). İzin **tur bazlıdır**: bir sonraki kullanıcı mesajında kalkar. Deny kuralları onu ezer. |
| **Gerçekten kısıtlamak için** | **`disallowed-tools: Write, Edit, Bash`** — skill aktifken araçları havuzdan kaldırır. Ya da `context: fork` + kısıtlı `agent` (Explore zaten Write/Edit'i reddeder). |

> **Ezberle:** Sınavda `allowed-tools` = kısıtlama. Gerçek hayatta `allowed-tools` = "izin sormadan kullan", `disallowed-tools` = kısıtlama. 40 kişilik ekipte bir analiz skill'inin dosya silmeyeceğine güvenmek için `disallowed-tools` ya da Explore fork'u kullan.

### 3. `argument-hint` — Parametre İpucu

```yaml
---
argument-hint: [dosya-yolu] [format]
---
```

- **Sınav tanımı:** Skill **argüman olmadan** çağrıldığında geliştiriciye ne girmesi gerektiğini söyler
- **Gerçek davranış:** `/` menüsünde otomatik tamamlama sırasında ipucu olarak görünür — `[issue-number]` gibi kısa, köşeli parantezli biçim
- Kullanıcı deneyimini iyileştirir; işlevsel bir zorlama değildir

### Diğer alanlar (Architect seviyesi için)

| Alan | Ne yapar |
|---|---|
| `disable-model-invocation: true` | Claude otomatik çağıramaz — yan etkili iş akışları |
| `user-invocable: false` | `/` menüsünde görünmez — yalnızca Claude'un yüklediği arka plan bilgisi |
| `model`, `effort` | Bu skill çalışırken model/efor geçersiz kılma |
| `paths` | Skill'in otomatik tetiklenmesini dosya desenine bağlar (3.3'teki kurallarla aynı glob) |
| `hooks` | Skill çağrılınca kaydedilen hook'lar |

---

## Kritik Ayrım: Skill vs CLAUDE.md (ve diğerleri)

Bu ayrımı sınav doğrudan test ediyor. Karıştırma.

| Özellik | CLAUDE.md | Skill |
|---|---|---|
| Yüklenme | **Her zaman yüklü** — otomatik | **Talep üzerine** — kullanıcı çağırır ya da Claude karar verir |
| Amaç | Evrensel standartlar, gerçekler | Göreve özgü iş akışları, prosedürler |
| Örnek | "Tüm fonksiyonlar JSDoc ile belgelenmeli" | "/review — PR'ı gözden geçir" |
| Kural | Evrensel standartları buraya koy | Göreve özgü prosedürleri buraya koy |

> **Göreve özgü prosedürleri CLAUDE.md'ye koyma. Evrensel standartları skill'lere koyma.**

- ✅ CLAUDE.md → "Tüm API endpoint'leri camelCase isimlendirme kullanmalı"
- ✅ Skill → "/migrate — Veritabanı migrasyon betiği oluştur"
- ❌ CLAUDE.md → "Migrasyon yaparken şu adımları izle" (göreve özgü — skill olmalı)
- ❌ Skill → "Her zaman TypeScript strict mode kullan" (evrensel — CLAUDE.md olmalı)

### Beşli Karar Tablosu (sınavın gerçek şık seti)

Exam guide Q6'nın dört şıkkı tam olarak bu mekanizmalardır. Hepsini bir arada gör:

| İhtiyaç | Mekanizma | Yüklenme |
|---|---|---|
| Her oturumda geçerli gerçek/standart | `CLAUDE.md` | Her zaman |
| Konuya göre bölünmüş standart | `.claude/rules/*.md` (`paths` yok) | Her zaman |
| Yalnızca belirli dosya türlerinde geçerli kural | `.claude/rules/*.md` + `paths` | Dosya eşleşince (deterministik) |
| Çok adımlı, ara sıra gereken prosedür | Skill (`SKILL.md`) | Çağrılınca (kullanıcı veya Claude) |
| İstisnasız zorlama ("asla main'e push etme") | Hook (`PreToolUse` vb.) | Her araç çağrısında, deterministik |
| İzole bağlam / farklı araç seti | Subagent (`.claude/agents/`) veya `context: fork` | Delege edilince |

---

## Kişisel Skill Özelleştirmesi

Takım skill'lerinin kişisel varyantlarını oluşturmak istiyorsan:

1. `~/.claude/skills/` dizinine koy (kişisel, paylaşılmaz)
2. **Farklı isim** kullan — takım skill'leriyle çakışmasın
3. Takım arkadaşlarını etkilemeden kişisel iş akışını özelleştir

**Neden farklı isim?** Aynı isimde skill'ler için öncelik **Enterprise > Personal > Project**'tir. `~/.claude/skills/review/` oluşturursan proje reposundaki `review` skill'i *senin için* gölgelenir — takım etkilenmez ama sen takım standardını kaybedersin ve "bende farklı çalışıyor" sorunu doğar. `review-mine` gibi farklı isim ikisini de erişilebilir tutar.

> Dipnot: Kişisel skill'ler (`~/.claude/skills/`) bulut ve Cowork oturumlarında yüklenmez; oralarda yalnızca claude.ai hesabında etkin skill'ler ve repodaki `.claude/skills/` gelir.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `.claude/commands/` | Proje kapsamlı — Git'te, takımla paylaşılır (legacy ama sınav cevabı) |
| `~/.claude/commands/` | Kişisel — paylaşılmaz |
| `.claude/skills/<ad>/SKILL.md` | Talep üzerine yüklenen iş akışları; komut adı = dizin adı |
| Tetikleme | Kullanıcı `/ad` **veya** Claude `description`'a göre; `disable-model-invocation` ile yalnızca kullanıcı |
| `context: fork` | İzole alt-agent (`agent:` ile seçilir) — detaylı çıktı orada kalır, özet döner; **konuşma geçmişini görmez** |
| `allowed-tools` | Sınav: araçları kısıtlar. Gerçek: ön-onaylar (tur bazlı); kısıtlayan `disallowed-tools` |
| `argument-hint` | Argüman ipucu (`[issue-number]`) — sınav: argümansız çağrıda ne girileceğini söyler |
| `$ARGUMENTS`, `` !`cmd` `` | Argüman yerleştirme; dinamik bağlam |
| Skill vs CLAUDE.md | Skill = göreve özgü prosedür, talep üzerine. CLAUDE.md = evrensel, her zaman |
| Kişisel skill'ler | `~/.claude/skills/` — farklı isimle; aynı isim → Personal > Project gölgeler |

---

## Pratik Senaryo 1

> Bir takım iki şey istiyor:
> 1. Herkesin kullanacağı bir `/review` komutu — PR'ları gözden geçirsin
> 2. Bir developer kişisel bir `/brainstorm` skill'i istiyor — çok detaylı çıktı üretiyor, ana konuşmayı kirletmesin
>
> **Her biri nereye konulmalı ve nasıl yapılandırılmalı?**
>
> **A)** İkisi de `.claude/commands/` dizinine konulmalı — takım paylaşımı için.
>
> **B)** `/review` → `.claude/commands/` (proje kapsamlı, paylaşılır). `/brainstorm` → `~/.claude/skills/brainstorm/SKILL.md` olarak, `context: fork` frontmatter'ı ile (kişisel, izole bağlamda çalışır).
>
> **C)** İkisi de CLAUDE.md dosyasına talimat olarak yazılmalı.
>
> **D)** İkisi de `~/.claude/commands/` dizinine konulmalı — kişisel tercih meselesi.

### Doğru Cevap: B

**Neden B doğru:** İki farklı gereksinim, iki farklı çözüm:
- `/review` herkesin kullanacağı bir komut → `.claude/commands/` (proje kapsamlı, Git'te, paylaşılır) — exam guide Q4 ile aynı
- `/brainstorm` kişisel, detaylı çıktı üretiyor → `~/.claude/skills/` (kişisel, paylaşılmaz) + `context: fork` (izole bağlam, ana konuşma temiz kalır)

**Neden A yanlış:** `/brainstorm` kişisel bir istek — proje reposuna koymak onu takımın tamamına dağıtır ve `/` menüsünü herkes için kirletir. Kişisel iş akışının yeri `~/.claude/`.

**Neden C yanlış:** Bunlar göreve özgü prosedürler — CLAUDE.md evrensel standartlar için. Ayrıca CLAUDE.md her zaman yüklü; "kirletmesin" gereksinimini tam tersine çevirir.

**Neden D yanlış:** `/review` takım genelinde olmalı — kişisel dizine koymak diğer takım üyelerinin erişememesi demek. Yeni üyeler bu komutu almaz.

---

## Pratik Senaryo 2

> Bir takımın `.claude/CLAUDE.md` dosyasında şu talimat var:
>
> ```
> Veritabanı migrasyonu yaparken:
> 1. Önce mevcut şemayı yedekle
> 2. Migrasyon betiğini oluştur
> 3. Test ortamında çalıştır
> 4. Sonuçları doğrula
> ```
>
> Claude Code her konuşmada bu talimatları yüklüyor — migrasyon yapılmasa bile.
>
> **Sorun nedir?**
>
> **A)** CLAUDE.md dosyası çok uzun — kısaltılmalı.
>
> **B)** Göreve özgü bir prosedür (migrasyon adımları) CLAUDE.md'de — bu bir skill olmalı, talep üzerine yüklenmeli.
>
> **C)** Talimatlar İngilizce olmalı — Claude Türkçe talimatları yanlış yorumluyor.
>
> **D)** CLAUDE.md yerine `.claude/rules/migrations.md` dosyasına taşınmalı.

### Doğru Cevap: B

**Neden B doğru:** Migrasyon prosedürü göreve özgü bir iş akışı — her konuşmada gerekli değil. CLAUDE.md her zaman yüklenir, bu da her seferinde gereksiz token tüketimi ve bağlam kirliliği demek. Doğru yer: `.claude/skills/migrate/SKILL.md` — yalnızca migrasyon gerektiğinde yüklensin. Yan etkili bir prosedür olduğu için `disable-model-invocation: true` ile yalnızca kullanıcı çağırsın.

**Neden A yanlış:** Dosyanın uzunluğu asıl sorun değil — sorun görev-spesifik bir prosedürün her zaman yüklenen bir dosyada olması. Kısaltsan da her oturumda yüklenir.

**Neden C yanlış:** Dil meselesi değil. Claude Türkçe talimatları iyi işler. Sorun yapısal — içeriğin yeri.

**Neden D yanlış:** `paths` frontmatter'ı olmayan bir `.claude/rules/` dosyası **yine her oturumda başlangıçta yüklenir** — CLAUDE.md ile aynı öncelikte. Taşımak dosyayı böler ama "her zaman yüklü" sorununu çözmez. (Migrasyon adımlarını `paths: ["migrations/**"]` ile sınırlamak da yanlış: prosedür bir dosya yoluna değil, bir *göreve* bağlıdır.)

---

## Pratik Senaryo 3

> Bir developer, "az önce yazdığın kodu güvenlik açısından gözden geçir ve bulguları listele" adımını `/security-check` skill'i olarak tanımladı. Çıktı uzun olduğu için skill'e `context: fork` ve `agent: Explore` ekledi. Ama skill her çağrıldığında "hangi kodu inceleyeceğimi bilmiyorum" diyor ve rastgele dosyalar okuyor.
>
> **Sorun nedir?**
>
> **A)** `agent: Explore` salt-okunur olduğu için kodu inceleyemiyor — `general-purpose` kullanılmalı.
>
> **B)** `context: fork` skill'i izole bir bağlamda çalıştırır — alt-agent **konuşma geçmişini görmez**, dolayısıyla "az önce yazdığın kod" ifadesinin karşılığı yoktur. Ya fork'u kaldır ya da incelenecek dosyaları `$ARGUMENTS` / `` !`git diff HEAD` `` ile açıkça skill'e ver.
>
> **C)** `allowed-tools: Read Grep` eklenmeli ki Claude dosyaları okuyabilsin.
>
> **D)** Skill `~/.claude/skills/` yerine `.claude/skills/` dizinine taşınmalı.

### Doğru Cevap: B

**Neden B doğru:** `context: fork`'un tanımı "yeni, izole bağlam"dır; skill içeriği alt-agent'ın *tek* girdisidir. Ana konuşmada az önce ne yazıldığı orada yoktur. Çözüm: fork'u kaldırıp ana bağlamda çalıştırmak (çıktı uzunsa `disallowed-tools` ile kısıtlayıp özet istemek) ya da bağlamı skill'e açıkça taşımak — en temizi `` !`git diff HEAD` `` ile değişen kodu skill içeriğine gömmek.

**Neden A yanlış:** Explore okuma yapabilir; sorun *neyi* okuyacağını bilmemesi. Agent türü değişse de fork izolasyonu aynı kalır.

**Neden C yanlış:** `allowed-tools` yalnızca izin istemini kaldırır; Read zaten kullanılabiliyor (rastgele dosyalar okuyor). Sorun izin değil, bağlam.

**Neden D yanlış:** Skill'in konumu paylaşımı belirler, bağlam görünürlüğünü değil.
