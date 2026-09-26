# Task Statement 3.6: CI/CD Entegrasyonu

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code sadece terminal'de etkileşimli olarak kullanılmaz — **CI/CD pipeline'larına** da entegre edilebilir. PR inceleme, test üretimi, kod analizi gibi görevler otomatik olarak çalıştırılabilir. Bu task statement, CI/CD entegrasyonunun **nasıl yapılandırılacağını** ve **yaygın tuzaklarını** öğretiyor (kurs modülleri: *Routines and Headless*, *GitHub Actions and Code Review*).

CI'daki bir Claude Code çağrısının **dört bileşeni** var; sınav her birini ayrı sorar:

1. **Etkileşimsizlik** → `-p`
2. **İzinler** → `--allowedTools` / `--permission-mode`
3. **Yapılandırılmış çıktı** → `--output-format json` + `--json-schema`
4. **Bağlam** → CLAUDE.md, mevcut testler, önceki inceleme bulguları, pipe ile diff

---

## 1. `-p` Flag'i — Non-Interactive Mod (Print Mode)

Bu, sınavın en çok test ettiği tek konsepttir. **Ezberle.**

### Problem

CI/CD pipeline'ında şu komut çalıştırılıyor:

```bash
claude "Analyze this PR"
```

Pipeline **sonsuza kadar asılı kalıyor.** Loglar, Claude'un **etkileşimli girdi beklediğini** gösteriyor.

### Çözüm

```bash
claude -p "Analyze this PR"
```

`-p` (`--print`) flag'i Claude Code'u **non-interactive modda** çalıştırır: etkileşimli terminal arayüzü açılmaz, prompt işlenir, çıktı yazdırılır ve süreç çıkar. Çıkış kodu: **0 başarı, sıfır dışı hata** — pipeline buna göre dallanabilir.

> **CI pipeline'ında `-p` flag'i olmadan Claude Code çalıştırırsan, pipeline asılı kalır.** Bu kadar basit.

### stdin ile besleme

Non-interactive mod stdin okur; Claude Code bir Unix aracı gibi pipe'a girer:

```bash
git diff main | claude -p "Review this diff for typos; report file:line and the issue"
gh pr diff "$PR" | claude -p --append-system-prompt "You are a security engineer." --output-format json
```

Diff'i pipe etmenin ek faydası: Claude'un diff'i okumak için **Bash iznine ihtiyacı kalmaz** (bkz. bölüm 2). stdin sınırı 10 MB.

---

## 2. CI'da İzinler — `-p` Tek Başına Yetmez

**Bu, sınavın "ikinci seviye" sorusudur.** `-p` etkileşimli *arayüzü* kaldırır ama **izin sistemini kaldırmaz**: `-p` oturumu **Manual (`default`) modda** başlar. Claude bir dosya düzenlemek veya Bash komutu çalıştırmak istediğinde izin ister; CI'da kimse cevap vermez → istek **reddedilir**, iş yapılmaz (ya da bir permission host varsa bekler).

| Belirti | Cevap |
|---|---|
| Pipeline asılı, "waiting for input" | `-p` eksik |
| `-p` var, Claude "I need permission to edit…" diyor, hiçbir dosya değişmiyor | İzin yapılandırması eksik ↓ |

### Seçenekler

```bash
# (a) Belirli araçları ön-onayla — izin kuralı sözdizimi
claude -p "Run the test suite and fix failures" --allowedTools "Bash(npm test *),Read,Edit"

# (b) Mod bazlı taban çizgisi
claude -p "Apply the lint fixes" --permission-mode acceptEdits   # dosya düzenlemeleri + mkdir/mv/cp otomatik
claude -p "…" --permission-mode dontAsk                          # istem gerektiren HER ŞEY reddedilir — kilitli CI
claude -p "…" --permission-mode auto                             # classifier onaylar/reddeder

# (c) Son çare
claude -p "…" --dangerously-skip-permissions                     # = bypassPermissions
```

- `--allowedTools` **izin kuralı sözdizimi** kullanır: `Bash(git diff *)` — ` *` ile prefix eşleşmesi (boşluk önemli: `git diff*` → `git diff-index`'i de yakalar)
- `dontAsk` resmi tavsiye: "Use this mode for CI pipelines or restricted environments where you pre-define what Claude may do; the session never waits for input." — okumalar ve `--allowedTools`'taki araçlar çalışır, geri kalanı sessizce reddedilir
- `--max-turns N` (limit aşılınca hata ile çıkar) ve `--max-budget-usd` ile kaçak çalıştırmaları sınırla
- Domain 1.4 (permission modes) ve Task 3.4 (plan modu da bir permission mode) ile bağ

> **Sınav kuralı:** "Asılı kalıyor" → `-p`. "`-p` var ama değişiklik yapmıyor / permission denied" → `--allowedTools` veya `--permission-mode`. Timeout wrapper, `echo yes |`, sürüm güncelleme → her zaman yanlış.

---

## 3. Yapılandırılmış CI Çıktısı

CI/CD pipeline'larında insan okunur metin yetmez — otomatik sistemler **makine tarafından ayrıştırılabilir (machine-parseable)** çıktı ister.

### Üç çıktı formatı

| `--output-format` | Ne verir |
|---|---|
| `text` (varsayılan) | Düz metin |
| `json` | Tek JSON nesnesi: `result` (metin), `session_id`, `total_cost_usd`, kullanım metadata'sı |
| `stream-json` | Satır başına bir olay (`--verbose` ile) — gerçek zamanlı akış |

### JSON Şema ile Yapılandırılmış Bulgular

```bash
claude -p "Review this PR" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"issues":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string"},"message":{"type":"string"}}}},"summary":{"type":"string"}},"required":["issues","summary"]}' \
  | jq '.structured_output'
```

- Yapılandırılmış sonuç JSON'un **`structured_output`** alanına gelir; serbest metin `result` alanında kalır
- `--json-schema` yalnızca print modunda çalışır; geçersiz şema → `Error: --json-schema is not a valid JSON Schema` ile çıkış
- Domain 4.3 (structured output) ile aynı ilke, CLI yüzeyinde

**Avantajı:** Otomatik sistemler `issues[]` dizisini ayrıştırıp her bulguyu **PR'a inline yorum olarak** gönderebilir — exam guide'ın "machine-parseable structured findings for automated posting as inline PR comments" maddesi.

---

## 4. Bağlam — CI'daki Claude Ne Bilmeli?

### 4a. CI için CLAUDE.md

CI/CD pipeline'ında Claude Code test üretmek veya kod incelemek için çağrılıyorsa, **CLAUDE.md dosyasında proje bağlamının belgelenmiş olması** kritik önem taşır. `claude -p` varsayılan olarak etkileşimli oturumla aynı bağlamı yükler — CLAUDE.md dahil.

**CLAUDE.md'de olması gerekenler (exam guide):**
- **Test standartları** — hangi framework (vitest, jest), hangi pattern (describe/it)
- **Değerli test kriterleri** — neyin test edilmesi gerektiğini tanımlayan kurallar (iş mantığı, edge case; getter/setter değil)
- **Mevcut fixture'lar** — test altyapısında neler var, sıfırdan mock oluşturma
- **İnceleme kriterleri** — review'da neye bakılacak

**CLAUDE.md yoksa ne olur?** Claude Code test üretirken **düşük değerli şablon testler (boilerplate)** üretir — gerçek iş mantığını test etmeyen, sadece boş çerçevelerden oluşan testler; framework tutarsız olur; fixture'lar kullanılmaz.

> **Güncel not (sınav cevabını değiştirmez):** Resmi tavsiye CI/scriptlerde `--bare` kullanmak: hook, skill, MCP, auto memory **ve CLAUDE.md** yüklenmez → her makinede aynı sonuç, hızlı başlangıç ("will become the default for `-p`"). `--bare` kullanıyorsan proje bağlamını `--append-system-prompt-file` / `--settings` ile *açıkça* verirsin. Kullanmıyorsan CLAUDE.md otomatik gelir — ama repodaki `.mcp.json` sunucuları ve hook'lar da onaysız çalışır (güvenlik notu). **Sınav cevabı: CLAUDE.md.**

### 4b. Mevcut Test Dosyalarını Bağlama Ver — Ayrı Bir Madde!

Exam guide'ın CLAUDE.md'den **ayrı** saydığı Skills maddesi: "Providing **existing test files in context** so test generation avoids suggesting **duplicate scenarios** already covered by the test suite."

| Belirti | Çözüm |
|---|---|
| Testler boş şablon, yanlış framework, fixture kullanmıyor | CLAUDE.md'ye standartları/fixture'ları yaz |
| Testler **zaten var olan senaryoları yeniden öneriyor** | **Mevcut test dosyalarını** prompt'a/bağlama ver (`@tests/auth.test.ts` veya stdin) |

CLAUDE.md *kuralları* verir; mevcut testler *neyin zaten kapsandığını* verir. İkisi farklı sorunları çözer.

### 4c. Artımlı İnceleme Bağlamı (Incremental Review Context)

Yeni commit'ler geldiğinde incelemeyi tekrar çalıştırırsan, **daha önceki inceleme bulgularını bağlama dahil et** ve Claude'a **sadece yeni veya hâlâ çözülmemiş sorunları raporlamasını** talimat ver.

**Neden?** Önceki bulguları dahil etmezsen, Claude aynı sorunları tekrar raporlar → **yinelenen yorumlar** → developer güvenini aşındırır.

**Doğru yaklaşım — 3. bölümle birleşik akış:**
```bash
# İlk çalıştırma: bulguları JSON olarak sakla
claude -p "Review this PR" --output-format json --json-schema "$SCHEMA" \
  | jq '.structured_output' > previous_findings.json

# Yeni commit: önceki bulguları ver, yalnızca yeni/çözülmemişleri iste
gh pr diff "$PR" | claude -p "Review this PR. Previous review findings: $(cat previous_findings.json).
Report ONLY new or still-unaddressed issues." --output-format json --json-schema "$SCHEMA"
```

---

## Oturum Bağlam İzolasyonu — Aynı Oturum Kendini İnceleyemez

Bu çok önemli ve sınavda test ediliyor:

> **Kodu üreten aynı Claude oturumu, kendi değişikliklerini incelemede DAHA AZ ETKİLİDİR.**

### Neden?

Aynı oturum, kodu yazarken yaptığı akıl yürütme bağlamını (reasoning context) taşır. Bu bağlam, kendi kararlarını sorgulamasını **daha az olası** kılar. Kendi mantığını zaten onaylamış — tekrar inceleyince aynı sonuca varır. Best practices: "A reviewer running in a fresh context **sees only the diff and the criteria you give it, not the reasoning that produced the change**."

### Mekanizma: CI'da "aynı oturum" nasıl olur?

Her `claude -p` çağrısı **varsayılan olarak yeni bir oturumdur** — izolasyon bedava gelir. Aynı oturumu sürdürmenin tek yolu **`--continue`** (son oturum) veya **`--resume <session_id>`**'dir. Dolayısıyla:

```bash
# ❌ YANLIŞ — inceleme, üretimin reasoning bağlamını miras alır
claude -p "Implement the user auth module" --output-format json | jq -r .session_id > sid
claude -p "Now review the changes you made for security issues" --resume "$(cat sid)"

# ✅ DOĞRU — bağımsız inceleme oturumu; yalnızca diff'i görür
claude -p "Implement the user auth module" --allowedTools "Edit,Bash(npm test *)"
git diff main | claude -p "Review this diff for security issues" --output-format json --json-schema "$SCHEMA"
```

Aynı ilke etkileşimli kullanımda **Writer/Reviewer** kalıbıdır (iki ayrı oturum) ve Claude Code içinde **adversarial review subagent**'ıdır (taze bağlamda yalnızca diff'i gören subagent). Domain 4.6 (multi-instance review) ile bağ.

> **Sınav kuralı:** "İnceleme neredeyse hiç sorun bulmuyor ama insanlar buluyor" + "aynı oturum / `--continue`" → bağımsız inceleme oturumu. Prompt'u iyileştirmek, model değiştirmek, CLAUDE.md'ye kriter eklemek kök nedeni çözmez.

---

## GitHub Actions ile Entegrasyon

Exam guide'ın "inline PR comments" ifadesinin somut karşılığı `anthropics/claude-code-action@v1`'dir (kurs modülü: *GitHub Actions and Code Review*).

| Konu | Ayrıntı |
|---|---|
| Kurulum | `/install-github-app` (GitHub App + secret + workflow PR'ı) veya manuel: `.github/workflows/claude.yml` |
| **Etkileşimli mod** | Workflow'da `prompt` yoksa Claude issue/PR yorumundaki **`@claude`** mention'ını bekler |
| **Otomasyon modu** | `prompt` varsa her GitHub olayında çalışır: PR açıldığında inceleme, cron ile günlük rapor |
| `claude_args` | CLI bayrakları: `--allowedTools "mcp__github_inline_comment__create_inline_comment"`, `--max-turns 5`, `--model …` |
| Kimlik bilgisi | **Yalnızca GitHub Secrets**: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}` veya `claude_code_oauth_token`. **Asla repoya commit etme** |
| CLAUDE.md | Action repo kökündeki CLAUDE.md'yi okur — "Define project standards in CLAUDE.md" |
| Maliyet | `--max-turns`, workflow timeout, concurrency; CLAUDE.md'yi kısa tut (her çalıştırmada okunur) |

```yaml
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: read, id-token: write }
    steps:
      - uses: actions/checkout@v6
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/code-review:code-review --comment ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
          claude_args: '--allowedTools "mcp__github_inline_comment__create_inline_comment"'
```

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `-p` / `--print` | CI/CD'de zorunlu — non-interactive mod. Yoksa pipeline asılı kalır. Çıkış kodu 0 / sıfır dışı |
| İzinler | `-p` Manual modda başlar; değişiklik için `--allowedTools "Edit,Bash(npm test *)"` veya `--permission-mode acceptEdits/dontAsk/auto` |
| `--output-format json` | Makine tarafından ayrıştırılabilir; `result`, `session_id`, `total_cost_usd` |
| `--json-schema` | Şemaya uygun çıktı → **`structured_output`** alanı; inline PR yorumları için |
| stdin pipe | `git diff main \| claude -p "…"` — Bash izni gerekmez |
| CI için CLAUDE.md | Test standartları, değerli test kriterleri, fixture'lar, inceleme kriterleri — yoksa şablon testler |
| Mevcut test dosyaları | Bağlama ver → yinelenen test senaryosu önerileri biter (CLAUDE.md'den ayrı madde) |
| Artımlı inceleme | Önceki bulguları dahil et, "sadece yeni/çözülmemiş sorunları raporla" |
| Oturum izolasyonu | Her `claude -p` yeni oturum; **`--continue`/`--resume` ile inceleme yapma** — bağımsız oturum diff'i taze görür |
| GitHub Actions | `@claude` (etkileşimli) vs `prompt` (otomasyon); secrets; `claude_args` |
| `--bare` (güncel not) | CI'da deterministik başlangıç; CLAUDE.md'yi de atlar → bağlamı açıkça ver |
| Sınav favori sorusu | "Pipeline asılı kalıyor" → `-p`. "Değişiklik yapmıyor" → izinler |

---

## Pratik Senaryo 1

> Bir CI pipeline betiği şu komutu çalıştırıyor:
>
> ```bash
> claude "Analyze this PR for potential bugs"
> ```
>
> Pipeline sonsuza kadar asılı kalıyor. Loglar, Claude'un girdi beklediğini gösteriyor.
>
> **Doğru düzeltme hangisidir?**
>
> **A)** Komutu bir timeout wrapper'ına sar — 60 saniye sonra otomatik sonlandırsın.
>
> **B)** `-p` flag'ini ekle — `claude -p "Analyze this PR for potential bugs"` — non-interactive modda çalıştırsın.
>
> **C)** Pipeline'a `echo "yes" |` pipe ekle — otomatik olarak "yes" cevabı versin.
>
> **D)** Claude Code sürümünü güncelle — eski sürümdeki bir bug olabilir.

### Doğru Cevap: B

**Neden B doğru:** `-p` flag'i Claude Code'u non-interactive modda (print mode) çalıştırır. Etkileşimli arayüz açılmaz, doğrudan analiz eder, çıktıyı yazdırır ve çıkar. CI/CD pipeline'larında her zaman `-p` kullan.

**Neden A yanlış:** Timeout sorunu çözmez — Claude'un analizini yarıda keser ve hiçbir çıktı üretmez. Sorun Claude'un etkileşimli arayüz açması, çözüm onu kapatmak (`-p`).

**Neden C yanlış:** `echo "yes"` pipe'ı güvenilmez ve tehlikeli. Etkileşimli arayüz stdin'den "yes" beklemez; ayrıca ne sorulduğunu bilmeden onay vermek izin mekanizmasını körlemesine atlamak demek.

**Neden D yanlış:** Bu bir bug değil, beklenen davranış. Claude Code varsayılan olarak etkileşimli modda çalışır. CI'da `-p` flag'i gerekli.

---

## Pratik Senaryo 2

> Bir takım CI pipeline'ında Claude Code ile otomatik kod inceleme yapıyor. Pipeline şu adımları izliyor:
> 1. `claude -p "Implement the feature described in the issue" --output-format json` → `session_id` kaydediliyor
> 2. `claude -p "Review the changes you just made for bugs and security issues" --resume $SESSION_ID`
>
> İnceleme sonuçları çok olumlu — neredeyse hiç sorun bulamıyor. Ama insan reviewer'lar aynı kodda birçok sorun tespit ediyor.
>
> **Kök neden nedir?**
>
> **A)** Claude Code'un inceleme yetenekleri yetersiz — farklı bir model kullanılmalı.
>
> **B)** `--resume` ile inceleme, kodu üreten oturumun reasoning bağlamını miras alıyor — kendi kararlarını sorgulamıyor. İnceleme, `--resume` olmadan **bağımsız bir `claude -p` çağrısında**, yalnızca diff'i görerek yapılmalı.
>
> **C)** İnceleme prompt'u yetersiz — daha detaylı inceleme talimatları eklenmeli.
>
> **D)** CLAUDE.md dosyasında inceleme standartları eksik.

### Doğru Cevap: B

**Neden B doğru:** Oturum bağlam izolasyonu kuralı. `--resume` aynı oturumu sürdürür; inceleme, kodu yazarken yapılan akıl yürütmeyi taşır — kendi kararlarını zaten haklı görmüş, tekrar inceleyince aynı sonuca varır. Bağımsız bir `claude -p` çağrısı (varsayılan: yeni oturum) kodu ilk kez, yalnızca diff olarak görür ve önyargısız inceleme yapar.

**Neden A yanlış:** Sorun modelin yeteneği değil, bağlamsal önyargı. Aynı model bağımsız oturumda çok daha etkili inceleme yapar.

**Neden C yanlış:** Prompt iyileştirme kısmen yardımcı olabilir ama kök nedeni çözmez. Aynı oturum kendi kodunu inceliyor — prompt ne kadar iyi olursa olsun, reasoning bağlamı önyargı yaratır.

**Neden D yanlış:** CLAUDE.md inceleme kriterleri için önemli ama buradaki sorun yapısal — oturum izolasyonu. Standartlar olsa bile aynı oturum kendi kodunu sorgulamada yetersiz kalır.

---

## Pratik Senaryo 3

> Bir CI pipeline her PR'da Claude Code ile inceleme yapıyor. Yeni commit'ler geldiğinde inceleme tekrar çalıştırılıyor. Developer'lar şikâyet ediyor: "Claude aynı sorunları her seferinde tekrar raporluyor — zaten düzelttiğim şeyleri tekrar söylüyor."
>
> **Çözüm hangisidir?**
>
> **A)** Her çalıştırmada farklı bir prompt kullan — Claude aynı prompt'u görünce aynı bulguları üretir.
>
> **B)** İncelemeyi sadece son commit'e karşı çalıştır — önceki dosyaları görmezden gel.
>
> **C)** Önceki inceleme bulgularını bağlama dahil et ve Claude'a "sadece yeni veya hâlâ çözülmemiş sorunları raporla" talimatı ver.
>
> **D)** İnceleme sıklığını azalt — her PR'da değil, merge'den önce tek sefer çalıştır.

### Doğru Cevap: C

**Neden C doğru:** Artımlı inceleme bağlamı. Önceki bulguları (ideal olarak bir önceki çalıştırmanın `structured_output` JSON'u) bağlama dahil edersen, Claude neyin zaten raporlandığını ve neyin düzeltildiğini bilir. "Sadece yeni veya çözülmemiş sorunları raporla" talimatıyla yinelenen yorumlar ortadan kalkar. Developer güveni korunur.

**Neden A yanlış:** Farklı prompt kullanmak sorunu çözmez — Claude önceki bulguları bilmiyorsa, aynı sorunları yeniden keşfedecek ve raporlayacak.

**Neden B yanlış:** Sadece son commit'e bakmak, dosya genelindeki sorunları kaçırır. Bir commit daha büyük bir sorunu kısmen düzeltmiş olabilir — tüm bağlam gerekli.

**Neden D yanlış:** Sıklığı azaltmak sorunu çözmez, erteler. Ve erken geri bildirim avantajını kaybettirir.

---

## Pratik Senaryo 4

> Bir CI job'ı şu komutu çalıştırıyor:
>
> ```bash
> claude -p "Fix all ESLint errors in src/" --output-format json
> ```
>
> Job asılı kalmıyor, sıfır çıkış koduyla bitiyor; ama `result` alanında "I need permission to edit src/utils.ts…" benzeri metinler var ve hiçbir dosya değişmemiş.
>
> **Kök neden ve düzeltme nedir?**
>
> **A)** `-p` flag'i düzenlemeyi engelliyor — CI'da `-p` kaldırılmalı.
>
> **B)** `-p` oturumu Manual izin modunda başlar; CI'da izin istemine cevap verecek kimse olmadığı için düzenlemeler reddediliyor. `--allowedTools "Edit,Bash(npx eslint *)"` ya da `--permission-mode acceptEdits` eklenmeli.
>
> **C)** `--output-format json` düzenlemeyi kapatıyor — `text` kullanılmalı.
>
> **D)** Komut `timeout 300` ile sarılmalı — Claude yeterli süre bulamıyor.

### Doğru Cevap: B

**Neden B doğru:** `-p` yalnızca etkileşimli arayüzü kaldırır; izin sistemi aynen çalışır ve `-p` Manual modda başlar. Düzenleme izni istenip cevap alınamayınca eylem reddedilir, Claude bunu metinle bildirir ve süreç "başarıyla" çıkar. CI'da yapılacak işi önceden tanımla: `--allowedTools` ile belirli araçlar/komutlar, ya da `acceptEdits` (dosya düzenlemeleri otomatik) / `dontAsk` (kilitli) / `auto` (classifier) modu.

**Neden A yanlış:** `-p` olmadan pipeline asılı kalır (Senaryo 1). `-p` düzenlemeyi engellemez; izinler engeller.

**Neden C yanlış:** Çıktı formatı yalnızca sonucun nasıl yazdırılacağını belirler; izinlerle ilgisi yok.

**Neden D yanlış:** Süre sorunu değil; job zaten normal bitiyor. Timeout, reddedilen izni onaylamaz.
