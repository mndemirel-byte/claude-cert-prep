# Task Statement 2.5: Yerleşik Araçlar (Built-in Tools)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Claude Code'un yerleşik (built-in) araçları vardır — dosya okuma, yazma, arama gibi temel operasyonlar. Sınav, bu araçların her birinin ne zaman kullanılacağını ve özellikle **Grep ile Glob arasındaki farkı** bilmeni bekliyor.

---

## Grep vs Glob — Kritik Ayrım

Bu ikisini karıştırmak sınavda zaman kaybettirir veya yanlış cevaba götürür.

### Grep — Dosya İÇERİĞİNDE Arama
Dosyaların **içindeki metinlerde** pattern arar.

**Kullanım alanları:**
- Bir fonksiyonu çağıran yerleri bulmak
- Hata mesajlarını aramak
- Import ifadelerini bulmak
- Belirli bir değişken adının kullanıldığı dosyaları bulmak

**Örnek:** "deprecatedFunction" adlı fonksiyonu çağıran tüm dosyaları bul → **Grep**

### Glob — Dosya YOLLARINDA Eşleştirme
Dosya **adlarını ve yollarını** pattern ile eşleştirir.

**Kullanım alanları:**
- Uzantıya göre dosya bulmak (`**/*.test.tsx`)
- Konfigürasyon dosyalarını bulmak (`**/config.*`)
- Belirli bir dizin yapısındaki dosyaları listelemek

**Örnek:** Tüm test dosyalarını bul → **Glob** (`**/*.test.tsx`)

### Özet Tablo

| Araç | Ne Arar | Nerede Arar | Örnek |
|---|---|---|---|
| **Grep** | Metin pattern | Dosya **içerikleri** | Fonksiyon çağrıları, hata mesajları, importlar |
| **Glob** | İsim pattern | Dosya **yolları** | Uzantıya göre dosya bulma, config dosyaları |

---

## Read / Write / Edit

### Edit — Hedefli Değişiklik
Benzersiz metin eşleştirmesi kullanarak **hedefli** değişiklik yapar. Hızlı ve kesin.

**Ne zaman kullanılır:** Değiştirmek istediğin metin dosyada benzersiz (unique) olduğunda.

### Edit Başarısız Olduğunda — Read + Write Yedek Planı

Edit bazen başarısız olur — eğer eşleştirmek istediğin metin dosyada **benzersiz değilse** (birden fazla yerde geçiyorsa). Bu durumda yedek plan:

1. **Read** — dosyanın tamamını yükle
2. **Write** — değiştirilmiş dosyanın tamamını yaz

**Read + Write**, Edit'in benzersiz bağlantı metni bulamadığı durumlarda güvenilir yedek plandır.

### Özet

| Araç | Kullanım | Avantaj | Sınırlama |
|---|---|---|---|
| **Edit** | Benzersiz metin eşleştirmesi ile hedefli değişiklik | Hızlı, kesin | Metin benzersiz olmalı |
| **Read + Write** | Tam dosya yükle + tam dosya yaz | Her zaman çalışır | Daha yavaş, tüm dosyayı işler |

---

## Artımlı Kod Tabanı Anlama (Incremental Codebase Understanding)

Büyük bir kod tabanını anlamak için doğru yaklaşım:

1. **Grep ile giriş noktalarını bul** — fonksiyon tanımları, import ifadeleri
2. **Read ile importları takip et** — giriş noktalarından akışları izle
3. **Tüm dosyaları baştan okuma** — bu context bütçesi katili

> **Tüm dosyaları önceden (upfront) okumak YANLIŞ yaklaşımdır.** Bu, context window'u gereksiz veriyle doldurur. Bunun yerine: Grep ile hedefleri belirle, Read ile sadece gerekli dosyaları oku.

### Fonksiyon Kullanımını Takip Etme

Wrapper modülleri arasında fonksiyon kullanımını izlemek için:
1. Önce dışa aktarılan (exported) isimleri belirle
2. Sonra her ismi kod tabanı genelinde Grep ile ara

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Grep | Dosya İÇERİĞİNDE arama — fonksiyon çağrıları, hata mesajları, importlar |
| Glob | Dosya YOLLARINDA eşleştirme — uzantıya göre dosya bulma, config dosyaları |
| Edit | Benzersiz metin eşleştirmesi ile hedefli değişiklik — hızlı ve kesin |
| Read + Write | Edit başarısız olduğunda yedek plan — tam dosya yükle ve yaz |
| Artımlı anlama | Grep → Read → takip. Tüm dosyaları baştan okuma — context bütçesi katili |
| Sınav tuzağı | Grep ile Glob'u karıştırmak — içerik araması mı, yol eşleştirmesi mi? |

---

## Pratik Senaryo

> Bir geliştirici, kod tabanındaki kullanımdan kaldırılmış (deprecated) bir fonksiyonu (`oldCalculate`) çağıran tüm dosyaları bulmak ve bu dosyaların her biri için ilgili test dosyalarını da bulmak istiyor.
>
> **Doğru araç sıralaması hangisidir?**
>
> **A)** Glob ile tüm `.ts` dosyalarını bul, sonra her birini Read ile oku ve `oldCalculate` içerenleri filtrele.
>
> **B)** Grep ile `oldCalculate` fonksiyon adını ara (çağıranları bulur), sonra Glob ile bulunan dosya adlarına karşılık gelen test dosyalarını eşleştir (`**/*.test.tsx`).
>
> **C)** Read ile tüm dosyaları sırayla oku ve `oldCalculate` string'ini manuel olarak ara.
>
> **D)** Glob ile `**/*oldCalculate*` pattern'ını kullanarak fonksiyonu içeren dosyaları bul.

### Doğru Cevap: B

**Neden B doğru:** İki adımlı doğru sıralama:
1. **Grep** ile `oldCalculate` fonksiyon adını dosya içeriklerinde ara → bu fonksiyonu çağıran dosyaları bulur
2. **Glob** ile bulunan dosya adlarına karşılık gelen test dosyalarını eşleştir (`**/*.test.tsx`)

Her araç kendi güçlü olduğu alanda kullanılıyor: Grep içerik araması, Glob yol eşleştirmesi.

**Neden A yanlış:** Tüm `.ts` dosyalarını bulup hepsini okumak verimsiz — context bütçesi israfı. Grep doğrudan hedefi bulur.

**Neden C yanlış:** Tüm dosyaları sırayla okumak en kötü yaklaşım — çok yavaş, context bütçesi katili. Grep bu işi tek seferde yapar.

**Neden D yanlış:** Glob dosya **yollarında** arama yapar, dosya **içeriklerinde** değil. `oldCalculate` fonksiyon adı dosya adında geçmiyorsa (ki genellikle geçmez), Glob hiçbir sonuç döndürmez. İçerik araması için Grep gerekir.
