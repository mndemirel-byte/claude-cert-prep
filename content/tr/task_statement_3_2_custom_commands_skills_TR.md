# Task Statement 3.2: Özel Slash Komutları ve Skill'ler

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code'da tekrarlayan iş akışlarını **özel komutlar** ve **skill'ler** olarak tanımlayabilirsin. Bunlar `/review`, `/test-setup`, `/brainstorm` gibi slash komutlarıyla çağrılır. Sınav, bunların **nereye konulacağını**, **nasıl yapılandırılacağını** ve **CLAUDE.md'den farkını** bilmeni bekliyor.

---

## Dizin Yapısı

### Proje Kapsamlı Komutlar (Paylaşılan)

```
.claude/commands/
```

- Proje deposunda bulunur
- **Versiyon kontrol altında** — Git ile paylaşılır
- Takımdaki herkes kullanabilir
- Örnek: `/review`, `/deploy-checklist`, `/test-all`

### Kişisel Komutlar (Paylaşılmayan)

```
~/.claude/commands/
```

- Kullanıcının ev dizininde bulunur
- **Paylaşılmaz** — sadece sen kullanırsın
- Takım arkadaşlarını etkilemez
- Örnek: Kişisel `/brainstorm`, `/quick-fix`

### Skill Dosyaları

```
.claude/skills/
```

- `SKILL.md` dosyaları içerir
- **İsteğe bağlı çağrılır** (on-demand invocation)
- Yapılandırma seçenekleri (frontmatter) ile özelleştirilebilir

---

## Skill Frontmatter Seçenekleri

Skill dosyalarının başında YAML frontmatter ile davranışı yapılandırabilirsin. Üç kritik seçenek:

### 1. `context: fork` — İzole Alt-Agent Bağlamı

```yaml
---
context: fork
---
```

- Skill'i **izole bir alt-agent** bağlamında çalıştırır
- Detaylı/gürültülü çıktı bu izole bağlamda kalır
- **Ana konuşma temiz kalır** — sadece özet döner
- **Kullanım alanı:** Kod tabanı analizi, beyin fırtınası, keşif görevleri — çok fazla çıktı üreten her şey

### 2. `allowed-tools` — Araç Kısıtlaması

```yaml
---
allowed-tools:
  - Read
  - Grep
  - Glob
---
```

- Skill'in kullanabileceği araçları **kısıtlar**
- Skill çalışması sırasında **yıkıcı (destructive) eylemleri engeller**
- Örneğin, bir analiz skill'inin dosya yazma veya silme yetkisi olmamalı

### 3. `argument-hint` — Parametre İpucu

```yaml
---
argument-hint: "Analiz edilecek dosya yolunu girin"
---
```

- Skill **argüman olmadan** çağrıldığında geliştiriciye ne girmesi gerektiğini söyler
- Kullanıcı deneyimini iyileştirir

---

## Kritik Ayrım: Skill vs CLAUDE.md

Bu ayrımı sınav doğrudan test ediyor. Karıştırma.

| Özellik | CLAUDE.md | Skill |
|---|---|---|
| Yüklenme | **Her zaman yüklü** — otomatik | **İsteğe bağlı** — çağrıldığında |
| Amaç | Evrensel standartlar | Göreve özgü iş akışları |
| Örnek | "Tüm fonksiyonlar JSDoc ile belgelenmeli" | "/review — PR'ı gözden geçir" |
| Kural | Evrensel standartları buraya koy | Göreve özgü prosedürleri buraya koy |

> **Göreve özgü prosedürleri CLAUDE.md'ye koyma. Evrensel standartları skill'lere koyma.**

- ✅ CLAUDE.md → "Tüm API endpoint'leri camelCase isimlendirme kullanmalı"
- ✅ Skill → "/migrate — Veritabanı migrasyon betiği oluştur"
- ❌ CLAUDE.md → "Migrasyon yaparken şu adımları izle" (göreve özgü — skill olmalı)
- ❌ Skill → "Her zaman TypeScript strict mode kullan" (evrensel — CLAUDE.md olmalı)

---

## Kişisel Skill Özelleştirmesi

Takım skill'lerinin kişisel varyantlarını oluşturmak istiyorsan:

1. `~/.claude/skills/` dizinine koy (kişisel, paylaşılmaz)
2. **Farklı isim** kullan — takım skill'leriyle çakışmasın
3. Takım arkadaşlarını etkilemeden kişisel iş akışını özelleştir

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `.claude/commands/` | Proje kapsamlı — Git'te, takımla paylaşılır |
| `~/.claude/commands/` | Kişisel — paylaşılmaz |
| `.claude/skills/` + `SKILL.md` | İsteğe bağlı çağrılan iş akışları |
| `context: fork` | İzole alt-agent — detaylı çıktı burada kalır, ana konuşma temiz |
| `allowed-tools` | Skill'in kullanabileceği araçları kısıtlar — yıkıcı eylemleri engeller |
| `argument-hint` | Argüman olmadan çağrıldığında parametre ipucu gösterir |
| Skill vs CLAUDE.md | Skill = göreve özgü, isteğe bağlı. CLAUDE.md = evrensel, her zaman yüklü |
| Kişisel skill'ler | `~/.claude/skills/` — farklı isimle, takımı etkilemeden |

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
> **B)** `/review` → `.claude/commands/` (proje kapsamlı, paylaşılır). `/brainstorm` → `~/.claude/skills/` dizininde `SKILL.md` olarak, `context: fork` frontmatter'ı ile (kişisel, izole bağlamda çalışır).
>
> **C)** İkisi de CLAUDE.md dosyasına talimat olarak yazılmalı.
>
> **D)** İkisi de `~/.claude/commands/` dizinine konulmalı — kişisel tercih meselesi.

### Doğru Cevap: B

**Neden B doğru:** İki farklı gereksinim, iki farklı çözüm:
- `/review` herkesin kullanacağı bir komut → `.claude/commands/` (proje kapsamlı, Git'te, paylaşılır)
- `/brainstorm` kişisel, detaylı çıktı üretiyor → `~/.claude/skills/` (kişisel, paylaşılmaz) + `context: fork` (izole bağlam, ana konuşma temiz kalır)

**Neden A yanlış:** `/brainstorm` kişisel istek — takım komutlarına koymak herkesi etkiler. Ayrıca `context: fork` yapılandırması gerekiyor ama commands dizininde bu frontmatter desteği skill'ler gibi çalışmaz.

**Neden C yanlış:** Bunlar göreve özgü prosedürler — CLAUDE.md evrensel standartlar için. Ayrıca CLAUDE.md her zaman yüklü, isteğe bağlı çağrı mekanizması yok.

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
> **B)** Göreve özgü bir prosedür (migrasyon adımları) CLAUDE.md'de — bu bir skill olmalı, isteğe bağlı çağrılmalı.
>
> **C)** Talimatlar İngilizce olmalı — Claude Türkçe talimatları yanlış yorumluyor.
>
> **D)** CLAUDE.md yerine `.claude/rules/` dizinine taşınmalı.

### Doğru Cevap: B

**Neden B doğru:** Migrasyon prosedürü göreve özgü bir iş akışı — her konuşmada gerekli değil. CLAUDE.md her zaman yüklenir, bu da her seferinde gereksiz token tüketimi ve bağlam kirliliği demek. Doğru yer: `.claude/skills/` dizininde bir skill dosyası olarak tanımla, sadece migrasyon gerektiğinde çağrılsın.

**Neden A yanlış:** Dosyanın uzunluğu asıl sorun değil — sorun görev-spesifik bir prosedürün her zaman yüklenen bir dosyada olması.

**Neden C yanlış:** Dil meselesi değil. Claude Türkçe talimatları iyi işler. Sorun yapısal — içeriğin yeri.

**Neden D yanlış:** `.claude/rules/` dizini yol bazlı kurallar için (Task 3.3'te işlenecek). Migrasyon prosedürü bir dosya yoluna bağlı değil, göreve bağlı — skill olmalı.
