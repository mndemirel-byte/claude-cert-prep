# Task Statement 3.3: Yol-Bazlı Kurallar (Path-Specific Rules)

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Bazen kuralların belirli **dosya türlerine** uygulanması gerekir — tüm test dosyaları, tüm API dosyaları, tüm Terraform dosyaları gibi. Bu dosyalar kod tabanının her yerine dağılmış olabilir. Dizin seviyesi CLAUDE.md dosyaları bu durumda yetersiz kalır çünkü bir **alt ağaca** bağlıdır. İşte yol-bazlı kurallar (path-specific rules) tam olarak bu sorunu çözer: kural bir dizine değil, bir **dosya yolu desenine** bağlanır.

---

## `.claude/rules/` Dosyaları ve YAML Frontmatter

`.claude/rules/` dizinine kural dosyaları koyarsın. Dosyanın başında YAML frontmatter ile **`paths`** alanında glob pattern belirtirsin:

```yaml
---
paths: ["terraform/**/*"]
---

Tüm Terraform dosyalarında:
- Her kaynak (resource) için açıklayıcı isim kullan
- Modülleri ayrı dizinlerde organize et
- State dosyasını remote backend'de tut
```

```yaml
---
paths:
  - "**/*.test.tsx"
  - "**/*.test.ts"
---

Tüm test dosyalarında:
- describe/it yapısı kullan
- Her test tek bir davranışı test etmeli
- Mock'ları dosya başında tanımla
- Test isimleri "should" ile başlamalı
```

**Kural, yalnızca Claude glob pattern'a uyan bir dosyayla çalışırken yüklenir.** Terraform dosyasına dokunmuyorsan, Terraform kuralları bağlama girmez.

### Bilmen gereken frontmatter kuralları

| Kural | Ayrıntı |
|---|---|
| `paths` yoksa | Dosya **koşulsuz**, başlangıçta, `.claude/CLAUDE.md` ile aynı öncelikte yüklenir. Yani `.claude/rules/` yalnızca path kuralları için değil; konuya göre bölünmüş genel kurallar için de kullanılır (Task 3.1) |
| `paths` biçimi | YAML listesi **veya** virgülle ayrılmış string; **brace expansion** desteklenir: `src/**/*.{ts,tsx}` |
| Tetikleyici | Claude eşleşen dosyayı **okuduğunda** yüklenir ("trigger when Claude reads files matching the pattern") — yalnızca düzenlerken değil. Exam guide "when editing" der; sınavda ikisi de kabul |
| Tek alan | `paths`, Claude Code'un okuduğu **tek** frontmatter alanıdır; diğerleri sessizce yok sayılır; frontmatter bağlama girmeden soyulur |
| Bozuk YAML | Frontmatter parse edilemezse dosya **koşulsuz** yüklenir → "kural her yerde yükleniyor, neden?" sorusunun cevabı. `claude --debug` hatayı gösterir |
| Keşif | `.claude/rules/` altındaki `.md` dosyaları alt klasörlerde **özyinelemeli** bulunur (`rules/frontend/`, `rules/backend/`) |
| Kişisel kurallar | `~/.claude/rules/` — makinedeki tüm projeler; proje kurallarından *önce* yüklenir, biri diğerini ezmez |
| Paylaşım | Symlink ile ortak kural seti birden çok projeye bağlanabilir |
| Nitelik | Kurallar da CLAUDE.md gibi **bağlamdır, zorlama değil** — garanti için hook (Domain 1.4) |

### Glob Cheat-Sheet (resmi tablo)

| Pattern | Neyi yakalar |
|---|---|
| `**/*.ts` | Herhangi bir dizindeki tüm TypeScript dosyaları |
| `src/**/*` | `src/` altındaki her şey |
| `*.md` | **Yalnızca proje kökündeki** Markdown dosyaları (alt dizinler hariç!) |
| `src/components/*.tsx` | Belirli bir dizindeki React bileşenleri (alt dizinler hariç) |
| `src/**/*.{ts,tsx}` | Brace expansion — iki uzantı tek desende |

> **Sınav tuzağı:** `*.md` ile `**/*.md` aynı değildir. "Tüm kod tabanındaki" ifadesi geçiyorsa `**/` gerekir.

---

## Dizin Seviyesi CLAUDE.md vs Yol-Bazlı Kurallar

Bu ayrım sınavın favori sorusudur. Kesin olarak öğren — ve **yanlış öğretilen noktaya dikkat et**:

| Özellik | Dizin Seviyesi CLAUDE.md | Yol-Bazlı Kurallar (`.claude/rules/` + `paths`) | Kök `.claude/rules/*.md` (`paths` yok) |
|---|---|---|---|
| Kapsam | **Bir alt ağaç** (o dizin ve altı) | **Tüm kod tabanı** — glob pattern ile | Tüm kod tabanı |
| Eşleştirme | Dosyanın bulunduğu dizin | Dosya yolu deseni (uzantı, dizin, kombinasyon) | — |
| Ne zaman yüklenir | **Talep üzerine** — o dizindeki bir dosya okununca | **Talep üzerine** — desene uyan bir dosya okununca | Başlangıçta, her zaman |
| Test dosyaları 50 dizine dağınıksa | 50 tane CLAUDE.md gerekir | `**/*.test.tsx` ile tek dosya | Her zaman yüklü olur (israf) |

### Kritik Fark — Kapsam Biçimi, Token Değil

İki mekanizma da **tembel (lazy) yüklenir**: alt dizin CLAUDE.md'si de path kuralı da yalnızca ilgili dosyalar okunduğunda bağlama girer. Yani token verimliliği açısından **aynı sınıftadırlar**. Gerçek fark **kapsamın nasıl tanımlandığı**:

- **Dizin CLAUDE.md** → "bu dizinin altındaki her şey" — teknoloji/paket sınırı dizin sınırıyla örtüşüyorsa (frontend/, backend/) ideal
- **Path kuralı** → "şu desene uyan her dosya, nerede olursa olsun" — dosya *türü* dizinlere yayılmışsa (test dosyaları, `.tf` dosyaları, `*/api/*`) tek çözüm

**Glob pattern'lar tüm kod tabanındaki dosyaları eşleştirir.** `**/*.test.tsx` pattern'ı hangi dizinde olursa olsun TÜM test dosyalarını yakalar. Dizin seviyesi CLAUDE.md ise yalnızca kendi alt ağacına uygulanır: test dosyaları 50 farklı dizine dağılmışsa 50 tane CLAUDE.md oluşturman gerekir — bakımı imkansız.

> **Sınav kuralı:** "Kod tabanına yayılmış / co-located / birçok dizinde" → yol-bazlı kural. "Bu klasör farklı teknoloji" → dizin CLAUDE.md. İkisi de "her zaman yüklü" değildir; her zaman yüklü olan kök CLAUDE.md ve `paths`'siz rules dosyalarıdır.

---

## Token Verimliliği

Yol-bazlı kuralların önemli avantajı: **sadece eşleşen dosyalarla çalışırken yüklenir.**

- Terraform dosyasına dokunmuyorsan → Terraform kuralları yüklenmez
- Test dosyası okumuyorsan → test kuralları yüklenmez
- Her zaman yüklenen kök CLAUDE.md'ye ve `paths`'siz kurallara kıyasla **daha az gereksiz bağlam, daha az token tüketimi**

Bu, Domain 5.1 (context preservation) ile aynı ilke: bağlama yalnızca o an gereken girer.

---

## Kullanım Senaryoları

### Test Kuralları
```yaml
---
paths: ["**/*.test.tsx", "**/*.test.ts", "**/*.spec.ts"]
---
```
Tüm test dosyalarına uygulanan kurallar — dizin fark etmez. (Exam guide Hazırlık Egzersizi 2: `paths: ["**/*.test.*"]`)

### API Kuralları
```yaml
---
paths: ["src/api/**/*", "src/routes/**/*"]
---
```
API ve route dosyalarına özgü kurallar. (Exam guide: `paths: ["src/api/**/*"]`)

### Altyapı Kuralları
```yaml
---
paths: ["**/*.tf", "**/*.tfvars"]
---
```
Dizinden bağımsız, uzantıya göre tüm Terraform dosyaları.

> **Güncel not (sınav cevabını değiştirmez):** Skill'ler de `paths` frontmatter'ı alabiliyor — skill'in *otomatik tetiklenmesini* bir dosya desenine bağlar. Sınavda "dosya türüne göre otomatik uygulanan konvansiyon" sorusunun cevabı hâlâ `.claude/rules/`'tur; skill'deki `paths` bir prosedürün ne zaman *önerileceğini* sınırlar.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `.claude/rules/` + `paths` frontmatter | Glob pattern ile yol-bazlı kurallar tanımla |
| `paths` yoksa | Dosya her oturumda, başlangıçta yüklenir (CLAUDE.md gibi) |
| Glob pattern | `**/*.test.tsx` — tüm kod tabanındaki test dosyaları; `*.md` yalnızca kök |
| Tetikleyici | Eşleşen dosya **okununca** (edit dahil) — Claude'un takdiri yok, **deterministik** |
| Dizin CLAUDE.md sınırlaması | Bir alt ağaca bağlı — dağınık dosya türleri için yetersiz |
| Dizin CLAUDE.md de tembel yüklenir | Fark token değil, **kapsam biçimi** (alt ağaç vs desen) |
| Bozuk YAML | Kural koşulsuz yüklenir → `claude --debug` |
| `~/.claude/rules/` | Kişisel kurallar, tüm projeler |
| Sınav tuzağı | "50 dizindeki test dosyalarına kural uygula" → yol-bazlı kurallar, dizin CLAUDE.md değil, skill değil |

---

## Pratik Senaryo 1

> Bir kod tabanında test dosyaları kaynak dosyalarla aynı dizinde bulunuyor (co-located: `Button.test.tsx`, `Button.tsx`'in yanında). 50'den fazla dizinde test dosyası var. Takım tüm testlerin aynı kuralları izlemesini istiyor: describe/it yapısı, tek davranış testi, mock'lar dosya başında.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** `.claude/rules/` dizininde `paths: ["**/*.test.tsx"]` glob pattern'ı ile yol-bazlı kural dosyası oluştur.
>
> **B)** Her 50 dizine ayrı `CLAUDE.md` dosyası koy — her birine test kurallarını yaz.
>
> **C)** Tek bir kök `CLAUDE.md` dosyasına tüm test kurallarını başlıklar altında yaz — Claude hangi bölümün geçerli olduğunu çıkarsın.
>
> **D)** Bir `/test-rules` skill'i oluştur — test yazarken çağrılsın.

### Doğru Cevap: A

**Neden A doğru:** `**/*.test.tsx` glob pattern'ı tüm kod tabanındaki test dosyalarını yakalar — hangi dizinde olursa olsun. Tek bir kural dosyası, 50+ dizindeki tüm test dosyalarına uygulanır. Bakımı kolay, token verimli (sadece test dosyasıyla çalışırken yüklenir) ve **deterministik** — dosya yolu eşleşince kural otomatik gelir. (Exam guide Q6'nın doğru cevabı.)

**Neden B yanlış:** 50 dizine 50 ayrı CLAUDE.md dosyası koymak bakım kabusudur. Bir kuralı değiştirmek istediğinde 50 dosyayı güncellemelisin. Yol-bazlı kuralların tam olarak çözdüğü sorun bu — CLAUDE.md dosyaları dizine bağlıdır ("directory-bound").

**Neden C yanlış:** Kök CLAUDE.md her zaman yüklenir — test dosyasıyla çalışmasan bile test kuralları bağlamda yer kaplar. Ayrıca "Claude hangi bölümün geçerli olduğunu çıkarsın" **çıkarıma** dayanır, açık eşleştirmeye değil — güvenilmez (exam guide'ın B şıkkı gerekçesi).

**Neden D yanlış:** Skill'ler talep üzerine yüklenir — ya kullanıcı çağırmayı hatırlar ya da Claude description'a bakıp yüklemeye *karar verir*. İkisi de **olasılıksaldır**; "dosya yoluna göre deterministik otomatik uygulama" gereksinimiyle çelişir (exam guide'ın C şıkkı gerekçesi). Yol-bazlı kurallar Claude'un takdirine bırakmaz.

---

## Pratik Senaryo 2

> Bir takımın Terraform konfigürasyon dosyaları `infrastructure/terraform/` dizininde. Ayrıca `modules/` dizininde de Terraform modülleri var. Takım tüm Terraform dosyalarında aynı isimlendirme ve organizasyon kurallarını uygulamak istiyor.
>
> **Hangi yaklaşım en uygun?**
>
> **A)** `infrastructure/terraform/CLAUDE.md` dizin seviyesi dosyası oluştur.
>
> **B)** `.claude/rules/terraform.md` dosyası oluştur — `paths: ["**/*.tf", "**/*.tfvars"]` frontmatter ile.
>
> **C)** Kök CLAUDE.md dosyasına Terraform kurallarını ekle.
>
> **D)** `.claude/rules/terraform.md` dosyası oluştur — `paths: ["*.tf"]` frontmatter ile.

### Doğru Cevap: B

**Neden B doğru:** Terraform dosyaları iki farklı dizinde (`infrastructure/terraform/` ve `modules/`). Glob pattern `**/*.tf` her iki dizindeki (ve gelecekte eklenecek her dizindeki) dosyaları da yakalar. Tek bir kural dosyası, tüm Terraform dosyalarına uygulanır. Token verimli — sadece `.tf` dosyasıyla çalışırken yüklenir.

**Neden A yanlış:** Dizin seviyesi CLAUDE.md sadece `infrastructure/terraform/` alt ağacındaki dosyalara uygulanır. `modules/` dizinindeki Terraform dosyaları bu kuralları almaz. İkinci bir CLAUDE.md oluşturmak gerekir — yol-bazlı kurallar bunu tek dosyayla çözer.

**Neden C yanlış:** Kök CLAUDE.md her zaman yüklenir. Python dosyası düzenlerken bile Terraform kuralları bağlamda olur — token israfı; dosya şişer, kurallar görmezden gelinmeye başlar.

**Neden D yanlış:** Glob tuzağı. `*.tf` yalnızca **proje kökündeki** `.tf` dosyalarını eşleştirir; alt dizinlerdeki hiçbir dosyayı yakalamaz. Kural hiçbir zaman yüklenmez. "Tüm kod tabanı" için `**/` şart.

---

## Pratik Senaryo 3

> Bir takım `.claude/rules/api.md` dosyasını `paths: ["src/api/**/*"]` ile oluşturdu. Ancak developer'lar frontend CSS dosyaları düzenlerken bile API kurallarının bağlamda göründüğünü fark ediyor. `/context` çıktısı kuralın her oturumda başlangıçta yüklendiğini gösteriyor. Dosyanın başı şöyle:
>
> ```
> --
> paths: ["src/api/**/*"]
> ---
> ```
>
> **Kök neden nedir?**
>
> **A)** `src/api/**/*` deseni çok geniş — `src/api/*.ts` olmalı.
>
> **B)** Frontmatter bozuk (açılış `---` eksik) — YAML parse edilemeyince Claude Code frontmatter'ı yok sayar ve kuralı **koşulsuz** yükler.
>
> **C)** `.claude/rules/` dosyaları her zaman başlangıçta yüklenir; koşullu yükleme için dosya `src/api/CLAUDE.md` olmalı.
>
> **D)** Path kuralları yalnızca dosya düzenlenirken devreye girer; CSS düzenlemesi de bir düzenleme olduğu için kural yükleniyor.

### Doğru Cevap: B

**Neden B doğru:** Resmi davranış: "If the YAML between the markers doesn't parse, Claude Code ignores the frontmatter and loads the rule as if it had no `paths`." Açılış işareti `--` (iki tire) olduğu için frontmatter tanınmıyor; dosya `paths`'siz bir kural gibi başlangıçta yükleniyor. `claude --debug` parse hatasını gösterir. Düzeltme: `---`.

**Neden A yanlış:** Desen geniş olsa bile CSS dosyalarını (`src/styles/...`) eşleştirmez; sorun desen değil, desenin hiç okunmaması.

**Neden C yanlış:** `paths` olan rules dosyaları koşullu yüklenir; dizin CLAUDE.md'ye taşımak gereksiz ve `src/api` dışındaki API dosyalarını kaçırır.

**Neden D yanlış:** Kural yalnızca *desene uyan* dosya okunduğunda/düzenlendiğinde yüklenir; CSS dosyası desene uymaz. Ayrıca `/context` başlangıçta yüklendiğini gösteriyor — tetiklenme değil, koşulsuz yükleme söz konusu.
