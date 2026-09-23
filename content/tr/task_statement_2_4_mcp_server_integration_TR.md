# Task Statement 2.4: MCP Sunucu Entegrasyonu (MCP Server Integration)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

MCP (Model Context Protocol), Claude'un dış araçlara ve veri kaynaklarına bağlanmasını sağlayan protokoldür. Bu task statement, MCP sunucularının nasıl yapılandırıldığını, kapsamlandırıldığını ve ne zaman özel sunucu inşa edilmesi gerektiğini öğretir.

---

## Kapsam Hiyerarşisi (Scoping Hierarchy)

İki seviye var:

### 1. Proje Seviyesi: `.mcp.json`
- Proje deposunda (repository) bulunur
- **Versiyon kontrol altında** — Git ile takip edilir
- Takımla paylaşılır
- Takımdaki herkes aynı araç konfigürasyonunu kullanır

### 2. Kullanıcı Seviyesi: `~/.claude.json`
- Kullanıcının ev dizininde bulunur
- **Kişisel** — versiyon kontrol altında DEĞİL
- Takımla paylaşılmaz
- Kişisel araç tercihleri ve kimlik bilgileri için

### Önemli Detay
Tüm yapılandırılmış sunuculardan gelen tüm araçlar **bağlantı anında keşfedilir** ve aynı anda kullanılabilir.

---

## Ortam Değişkeni Genişletmesi (Environment Variable Expansion)

`.mcp.json` dosyası `${DEGISKEN_ADI}` sözdizimini destekler. Bu, kimlik bilgilerini versiyon kontrol dışında tutar.

```json
{
  "mcpServers": {
    "github": {
      "command": "github-mcp-server",
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Avantajı:** Her geliştirici kendi token'ını yerel olarak ayarlar. Token'lar repoya girmez. Güvenlik korunur.

---

## MCP Kaynakları (Resources)

MCP sunucuları sadece araç değil, **kaynak (resource)** da sunabilir:

- Issue özetleri
- Dokümantasyon hiyerarşileri
- Veritabanı şemaları

**Faydası:** Agent'lara mevcut verilerin bir kataloğunu gösterir — keşif amaçlı araç çağrısı yapmaya gerek kalmaz. Gereksiz sorguları azaltır.

Örnek: Bir agent veritabanı şemasını MCP kaynağı olarak görür ve hangi tabloların mevcut olduğunu bilir — rastgele sorgulama yapmak yerine doğrudan doğru tabloyu sorgular.

---

## İnşa Et vs Kullan Kararı (Build vs Use)

Bu karar sınavda test ediliyor. Kural net:

### Önce Topluluk (Community) MCP Sunucularını Değerlendir
Standart entegrasyonlar (Jira, GitHub, Slack, veritabanları) için **topluluk MCP sunucuları** zaten mevcut. Bunları kullan.

### Özel Sunucu Ne Zaman İnşa Edilir?
**Sadece** takıma özgü iş akışları topluluk sunucuları tarafından karşılanamadığında.

Örnekler:
- Şirketin özel iç API'sine bağlantı gerekiyor → özel sunucu gerekli
- Standart Jira entegrasyonu gerekiyor → topluluk sunucusu yeterli

### MCP Araç Açıklamalarını Zenginleştirme

Önemli bir detay: agent bazen MCP araçları yerine yerleşik araçları (Grep gibi) tercih edebilir. Bunun nedeni MCP aracının açıklamasının yetersiz olması olabilir. **MCP araç açıklamalarını zenginleştirerek** agent'ın doğru aracı seçmesini sağla.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `.mcp.json` | Proje seviyesi — versiyon kontrol altında, takımla paylaşılır |
| `~/.claude.json` | Kullanıcı seviyesi — kişisel, paylaşılmaz |
| Ortam değişkenleri | `${GITHUB_TOKEN}` sözdizimi — kimlik bilgilerini repo dışında tutar |
| MCP kaynakları | İçerik katalogları sunar — keşif sorguları azalır |
| Build vs use | Standart entegrasyon → topluluk sunucusu. Özel iş akışı → özel sunucu |
| Araç açıklama zenginleştirme | MCP araçlarının açıklamalarını iyileştir ki agent yerleşik araçları tercih etmesin |

---

## Pratik Senaryo

> Bir takım Jira entegrasyonu kurmak istiyor. Bir geliştirici özel bir MCP sunucusu inşa etmeyi öneriyor — Jira API'sine bağlanacak, issue oluşturacak, durum güncelleyecek ve sprint bilgisi çekecek.
>
> **Bu doğru yaklaşım mı?**
>
> **A)** Evet — özel sunucu takımın ihtiyaçlarına tam olarak uyar ve tam kontrol sağlar.
>
> **B)** Hayır — önce topluluk Jira MCP sunucusunu değerlendir. Standart issue oluşturma, durum güncelleme ve sprint bilgisi çekme zaten topluluk sunucusu tarafından karşılanıyor. Sadece takıma özgü özel iş akışları varsa özel sunucu inşa et.
>
> **C)** Hayır — Jira'nın kendi API'sini doğrudan kullan, MCP'ye gerek yok.
>
> **D)** Evet — ama önce GitHub MCP sunucusunu kur, sonra Jira sunucusunu onun üzerine inşa et.

### Doğru Cevap: B

**Neden B doğru:** Standart Jira işlemleri (issue oluşturma, durum güncelleme, sprint bilgisi) topluluk MCP sunucuları tarafından zaten karşılanıyor. Özel sunucu inşa etmek gereksiz efor — bakım maliyeti, test maliyeti, güncelleme maliyeti. Topluluk sunucusu yetmediğinde (takıma özgü özel iş akışı) o zaman özel sunucu düşünülmeli.

**Neden A yanlış:** "Tam kontrol" kulağa iyi gelse de, mevcut bir çözüm varken sıfırdan inşa etmek aşırı mühendislik. Sınav ilkesi: önce basit, düşük eforlu çözüm.

**Neden C yanlış:** MCP katmanı, Claude'un araçları keşfetmesini ve kullanmasını sağlayan standart protokoldür. Doğrudan API kullanımı agent mimarisine uygun değil.

**Neden D yanlış:** GitHub ve Jira bağımsız entegrasyonlar — birinin üzerine diğerini inşa etmek mantıksız.
