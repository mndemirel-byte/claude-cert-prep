# Task Statement 2.4: MCP Sunucu Entegrasyonu (MCP Server Integration)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

MCP (Model Context Protocol), Claude'un dış araçlara ve veri kaynaklarına bağlanmasını sağlayan açık protokoldür. Bir MCP sunucusu bir kez yazılır; Claude Code, Claude Desktop, Agent SDK ve Messages API'nin MCP connector'ı aynı sunucuyu kullanabilir. Bu task statement, MCP sunucularının Claude Code'da nasıl yapılandırıldığını, kapsamlandırıldığını ve ne zaman özel sunucu inşa edilmesi gerektiğini öğretir.

---

## MCP'nin Üç Primitive'i

MCP sunucusu üç tür şey sunar (Intro to MCP kursu üçünü eşit ağırlıkla işler):

| Primitive | Ne | Kim tetikler | Claude Code'da nasıl görünür |
|---|---|---|---|
| **Tools** | Modelin çağırdığı fonksiyonlar (issue oluştur, sorgu çalıştır) | Model | `mcp__<server>__<tool>` adlı araçlar |
| **Resources** | Salt okunur içerik / veri katalogları (şema, doküman ağacı, issue listesi) | Uygulama / kullanıcı | `@server:protocol://kaynak` ile mention |
| **Prompts** | Sunucunun sunduğu hazır prompt şablonları | Kullanıcı | `/mcp__server__prompt` slash komutu |

---

## Kapsam Hiyerarşisi (Scoping)

Exam guide iki seviyeyi vurgular: **proje** (`.mcp.json`) ve **kullanıcı** (`~/.claude.json`). Claude Code'un gerçek modeli üç scope'tur; üçüncüsünü (local) bilmek "takımla paylaşmak istedim ama `.mcp.json`'a yazılmadı" hatasını açıklar.

| Scope | Nerede saklanır | Hangi projelerde yüklenir | Takımla paylaşılır mı | Ne için |
|---|---|---|---|---|
| **local** (`claude mcp add` **varsayılanı**) | `~/.claude.json` içinde, proje yoluna bağlı | Yalnızca o proje | ❌ | Kişisel deneme, tek projelik kimlik bilgisi |
| **project** | `.mcp.json` (repo kökü) | Yalnızca o proje | ✅ **versiyon kontrolü ile** | Takımın ortak araçları — herkes aynı konfigürasyonu kullanır |
| **user** | `~/.claude.json` üst seviye | **Tüm** projeler | ❌ | Kişisel, projeden bağımsız araçlar |

```bash
claude mcp add --transport http shared-server --scope project https://example.com/mcp   # → .mcp.json
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic   # → ~/.claude.json (tüm projeler)
claude mcp add --transport http stripe https://mcp.stripe.com                            # → local (varsayılan!)
```

**Öncelik sırası** (aynı ad birden fazla yerde tanımlıysa): local > project > user > plugin sunucuları > claude.ai connector'ları > organizasyon tarafından yönetilen (en yüksek).

### Proje `.mcp.json` için onay mekanizması — güvenlik

Repo'yu klonlayan biri farkında olmadan yabancı bir sunucu çalıştırmasın diye Claude Code, `.mcp.json`'dan gelen sunucuları interaktif oturumda **ilk kullanımda onay ister**. `/mcp` panelinde `⏸ Pending approval` olarak görünür. `claude -p` (headless) ve Agent SDK oturumlarında onay sorulmaz.

Ayarlar (`settings.json`):
- `enableAllProjectMcpServers: false` → tüm `.mcp.json` sunucularını reddet
- `enabledMcpjsonServers: [...]` / `disabledMcpjsonServers: [...]` → izin / kara liste
- `claude mcp reset-project-choices` → onay kararlarını sıfırla

Sınav senaryosu: "Takım `.mcp.json`'a sunucu ekledi, benim oturumumda araçlar görünmüyor." → Sunucu onay bekliyor (`/mcp` ile onayla) ya da ayarlarla devre dışı.

### Önemli Detay
Tüm yapılandırılmış sunuculardan gelen tüm araçlar **bağlantı anında keşfedilir** (`tools/list`) ve aynı anda kullanılabilir. Üç scope'un araçları tek havuzda birleşir — bu yüzden çok sunucu = çok araç = Domain 2.3'teki aşırı yükleme riski.

---

## Transport Türleri

| Transport | Nasıl çalışır | `.mcp.json` alanları | Ne zaman |
|---|---|---|---|
| **stdio** | Claude Code sunucuyu yerel alt süreç olarak başlatır | `type: "stdio"`, `command`, `args`, `env` | Yerel araçlar, npm/Python paketleri |
| **http** | Uzak sunucuya Streamable HTTP | `type: "http"`, `url`, `headers`, `oauth` | SaaS entegrasyonları (Notion, Stripe, Sentry…) |
| **sse** | Server-Sent Events — **deprecated** | `type: "sse"`, `url` | Yalnızca http sunmayan eski sunucular |

```bash
# stdio: "--" Claude'un seçeneklerini sunucu komutundan ayırır
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable -- npx -y airtable-mcp-server

# http + header
claude mcp add --transport http secure-api https://api.example.com/mcp --header "Authorization: Bearer token"
```

OAuth gerektiren uzak sunucular için `/mcp` panelinden tarayıcı akışı ya da `claude mcp login <server>`.

---

## Ortam Değişkeni Genişletmesi (Environment Variable Expansion)

`.mcp.json` dosyası `${DEGISKEN_ADI}` ve `${DEGISKEN_ADI:-varsayılan}` sözdizimini destekler. Genişletme `command`, `args`, `env`, `url` ve `headers` alanlarının **hepsinde** çalışır. Bu, kimlik bilgilerini versiyon kontrol dışında tutar.

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

**Avantajı:** Her geliştirici kendi token'ını yerel olarak ayarlar. Token'lar repoya girmez. Güvenlik korunur.

Detaylar:
- Değişken tanımsız ve varsayılan yoksa konfigürasyon yine yüklenir; `claude mcp list` uyarı gösterir, metin `${VAR}` olarak kalır.
- Güvenlik önlemi: uzak sunucunun `url`/`headers` alanında `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` gibi Claude'un kendi kimlik bilgileri **boş** okunur — bir `.mcp.json` senin API anahtarını yabancı sunucuya sızdıramaz.

---

## Araç Adlandırma: `mcp__<server>__<tool>`

MCP araçları Claude Code'da `mcp__<sunucu-adı>__<araç-adı>` biçiminde görünür (`mcp__github__create_issue`). Bu tam ad şuralarda kullanılır:

- İzin kuralları (`settings.json` → `permissions.allow: ["mcp__github__*"]`)
- Subagent `tools` listesi (Domain 2.3 / 1.3)
- Hook matcher'ları (Domain 1.5)
- Skill `allowed-tools`

Plugin'lerle gelen sunucular `mcp__plugin_<plugin>_<server>__<tool>` biçimini alır.

---

## MCP Kaynakları (Resources)

MCP sunucuları sadece araç değil, **kaynak (resource)** da sunabilir:

- Issue özetleri
- Dokümantasyon hiyerarşileri
- Veritabanı şemaları

**Faydası:** Agent'lara mevcut verilerin bir kataloğunu gösterir — keşif amaçlı araç çağrısı yapmaya gerek kalmaz. Gereksiz sorguları azaltır.

Örnek: Bir agent veritabanı şemasını MCP kaynağı olarak görür ve hangi tabloların mevcut olduğunu bilir — "tabloları listele", "kolonları göster" gibi 3–4 keşif çağrısı yerine doğrudan doğru tabloyu sorgular.

Claude Code'da: `@postgres:schema://orders` gibi mention ile kaynak içeriği konuşmaya çekilir; `ListMcpResourcesTool` / `ReadMcpResourceTool` yerleşik araçları programatik erişim sağlar.

---

## MCP Çıktı Limiti

Claude Code, MCP araç sonuçlarını varsayılan **25.000 token**'da keser (10.000'de uyarı; `MAX_MCP_OUTPUT_TOKENS` ile değişir). Limit aşılırsa sonuç dosyaya yazılır ve context'e dosya referansı girer. "Araç tüm tabloyu döndürüyor, context şişiyor" senaryosunun çözümü sunucu tarafında: sayfalama, filtreleme, `response_format: concise` (bkz. Domain 2.1 — çıktı tasarımı).

---

## İnşa Et vs Kullan Kararı (Build vs Use)

Bu karar sınavda test ediliyor. Kural net:

### Önce Topluluk (Community) MCP Sunucularını Değerlendir
Standart entegrasyonlar (Jira, GitHub, Slack, veritabanları) için **topluluk / resmi MCP sunucuları** zaten mevcut. Bunları kullan.

### Özel Sunucu Ne Zaman İnşa Edilir?
**Sadece** takıma özgü iş akışları topluluk sunucuları tarafından karşılanamadığında.

Örnekler:
- Şirketin özel iç API'sine bağlantı gerekiyor → özel sunucu gerekli
- Standart Jira entegrasyonu gerekiyor → topluluk sunucusu yeterli
- Jira var ama "sprint kapanışında 5 sistemden veri toplayıp bizim şablonla rapor üret" gibi takıma özgü bileşik iş akışı → topluluk sunucusu + özel bir "workflow" aracı (ya da özel sunucu)

### "Değerlendir" ne demek — kontrol listesi

| Kriter | Soru |
|---|---|
| Kapsam | İhtiyacın olan işlemleri (oluştur / güncelle / sorgula) sunuyor mu? |
| Bakım | Aktif mi, sürüm çıkıyor mu, resmi mi topluluk mu? |
| Kimlik doğrulama | Token / OAuth modeli senin güvenlik politikana uyuyor mu? |
| Araç kalitesi | Açıklamalar detaylı mı, araç sayısı makul mu (50 araçlı sunucu = context yükü)? |
| Güvenlik | Tool annotations ve açıklamalar güvenilmeyen kaynaktan geliyorsa "untrusted" — spec bunu zorunlu kılar |

### MCP Araç Açıklamalarını Zenginleştirme

Önemli bir detay: agent bazen MCP araçları yerine yerleşik araçları (Grep gibi) tercih edebilir. Mekanizma şu: yerleşik `Grep`'in açıklaması uzun, detaylı ve tanıdık; MCP aracı `"Searches code"` derse Claude daha "zengin görünen" yerleşik aracı seçer — MCP aracı aslında daha yetenekli olsa bile (semantik arama, indeks, çapraz repo).

**Çözüm:** MCP araç açıklamasını **yetenekleri ve çıktıyı** detaylandıracak şekilde zenginleştir: ne yapabildiği, ne döndürdüğü, yerleşik araçtan farkı ("Grep'ten farklı olarak sembol tanımlarını ve referanslarını dil-farkında çözer; sonuçlar dosya + satır + sembol türü içerir"). Exam guide'ın Skills ifadesi: *"explain capabilities and outputs in detail."* Bu, Domain 2.1'deki açıklama ilkelerinin MCP'ye uygulanmasıdır.

---

## Agent SDK ve API Tarafı

| Yol | Nasıl | Ne zaman |
|---|---|---|
| **Claude Code** | `.mcp.json` / `claude mcp add` | İnteraktif ve headless geliştirme |
| **Agent SDK** | `mcpServers` seçeneği (aynı JSON yapısı); `allowedTools: ["mcp__github__*"]` | Kendi agent uygulaman, Claude Code'un yeteneklerini programatik kullanmak |
| **Agent SDK in-process** | `createSdkMcpServer` + `tool()` — ayrı süreç yok, araç aynı uygulamada tanımlanır | Küçük, uygulamaya özel araçlar; alt süreç yönetmek istemediğinde |
| **Messages API MCP connector** | İstekte `mcp_servers: [{url, name, …}]` | Claude Code olmadan, doğrudan API'den uzak MCP sunucusuna bağlanmak |

Practice scenario'daki "MCP'ye gerek yok, Jira API'sini doğrudan kullan" şıkkı bu tabloya göre okunmalı: Messages API ile kendi tool fonksiyonunu yazıp Jira REST'i çağırmak **meşru bir mimaridir** (Building with the Claude API kursu tam bunu yapar). MCP'nin avantajı zorunluluk değil: standartlaşma, yeniden kullanılabilirlik (aynı sunucu her istemcide), keşif (`tools/list`) ve Claude Code bağlamında **tek entegrasyon yolu** olması.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `.mcp.json` | Proje scope — versiyon kontrol altında, takımla paylaşılır, ilk kullanımda onay ister |
| `~/.claude.json` | Kullanıcı scope (tüm projeler) **ve** local scope (tek proje, `claude mcp add` varsayılanı) — ikisi de kişisel |
| `--scope project` | Takımla paylaşmak için açıkça belirt; varsayılan local |
| Ortam değişkenleri | `${VAR}` / `${VAR:-default}` — command, args, env, url, headers; kimlik bilgileri repo dışında |
| Transport | stdio (yerel süreç), http (uzak), sse (deprecated) |
| `mcp__server__tool` | İzin, subagent `tools`, hook matcher, skill allowed-tools |
| Üç primitive | Tools (model çağırır), Resources (`@server:…`), Prompts (`/mcp__server__prompt`) |
| MCP kaynakları | İçerik katalogları — keşif sorguları azalır |
| Çıktı limiti | 25k token varsayılan → sunucu tarafında sayfalama |
| Build vs use | Standart entegrasyon → topluluk sunucusu. Takıma özgü iş akışı → özel sunucu |
| Açıklama zenginleştirme | Yetenek + çıktı detayı → agent yerleşik aracı MCP'ye tercih etmesin |
| SDK / API | `mcpServers`, in-process `createSdkMcpServer`, API `mcp_servers` connector |

---

## Pratik Senaryo

> Bir takım Jira entegrasyonu kurmak istiyor. Bir geliştirici özel bir MCP sunucusu inşa etmeyi öneriyor — Jira API'sine bağlanacak, issue oluşturacak, durum güncelleyecek ve sprint bilgisi çekecek.
>
> **Bu doğru yaklaşım mı?**
>
> **A)** Evet — özel sunucu takımın ihtiyaçlarına tam olarak uyar ve tam kontrol sağlar.
>
> **B)** Hayır — önce mevcut Jira MCP sunucusunu değerlendir. Standart issue oluşturma, durum güncelleme ve sprint bilgisi çekme zaten karşılanıyor. Sadece takıma özgü, karşılanmayan iş akışları varsa özel sunucu inşa et.
>
> **C)** Hayır — MCP'ye gerek yok; Claude Code'un Bash aracıyla Jira REST API'sine `curl` çağrıları yaptır.
>
> **D)** Hayır — Jira sunucusunu her geliştirici kendi `~/.claude.json` dosyasına `--scope user` ile eklesin; böylece herkes kendi token'ıyla çalışır.

### Doğru Cevap: B

**Neden B doğru:** Standart Jira işlemleri (issue oluşturma, durum güncelleme, sprint bilgisi) mevcut MCP sunucuları tarafından zaten karşılanıyor. Özel sunucu inşa etmek gereksiz efor — bakım, test, güncelleme maliyeti. Exam guide: "Choosing existing community MCP servers over custom implementations for standard integrations, reserving custom servers for team-specific workflows."

**Neden A yanlış:** "Tam kontrol" kulağa iyi gelse de, mevcut bir çözüm varken sıfırdan inşa etmek aşırı mühendislik. Sınav ilkesi: önce basit, düşük eforlu çözüm. Takıma özgü ihtiyaç ortaya çıkarsa o zaman özel sunucu (ya da mevcut sunucunun yanına küçük bir ek araç).

**Neden C yanlış:** Bash + `curl` Claude'a keşfedilebilir araç arayüzü, şema, yapılandırılmış hata yanıtı (`isError`) ve izin kuralı granülerliği vermez; her çağrı serbest metin komut olur, takımla paylaşılamaz, `Bash` izni gerektirir. (Not: Messages API ile *kendi tool fonksiyonunu* yazmak meşrudur — ama bu şık onu değil, Claude Code içinde MCP'yi atlamayı öneriyor.)

**Neden D yanlış:** Scope karışıklığı. Takımın ortak entegrasyonu `.mcp.json`'da (project scope) olmalı ki herkes aynı konfigürasyonu alsın; kişisel token `${JIRA_TOKEN}` ortam değişkeniyle dışarıda tutulur. Her geliştiricinin kendi user-scope tanımı yapması konfigürasyon sapmasına yol açar ve yeni gelen kişi kurulumu keşfedemez.
