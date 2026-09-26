# Task Statement 2.5: Yerleşik Araçlar (Built-in Tools)

## Domain 2 — Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

---

## Temel Fikir

Claude Code'un yerleşik (built-in) araçları vardır. Task statement altı tanesini adıyla sayar: **Read, Write, Edit, Bash, Grep, Glob**. Sınav, bu araçların her birinin ne zaman kullanılacağını, özellikle **Grep ile Glob arasındaki farkı** ve **Edit başarısız olduğunda ne yapılacağını** bilmeni bekliyor.

| Araç | Ne yapar | İzin ister mi |
|---|---|---|
| **Read** | Dosya içeriğini okur (tamamı veya `offset`/`limit` ile bir bölümü) | Hayır |
| **Grep** | Dosya **içeriklerinde** pattern arar (ripgrep tabanlı) | Hayır |
| **Glob** | Dosya **yollarını** pattern ile eşleştirir | Hayır |
| **Edit** | Benzersiz metin eşleştirmesiyle hedefli değişiklik | Evet |
| **Write** | Dosyayı oluşturur veya **tamamen** üzerine yazar | Evet |
| **Bash** | Shell komutu çalıştırır (test, build, git, paket kurulumu) | Evet |

İzin sütunu önemli: okuma/arama araçları izin istemez, değişiklik yapan ve komut çalıştıran araçlar ister (Domain 3 — permission modes ile bağ).

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

**Çıktı modları — context bütçesi için önemli:**

| Mod | Ne döndürür | Ne zaman |
|---|---|---|
| `files_with_matches` (varsayılan) | Yalnızca dosya yolları | İlk keşif — en ucuz |
| `content` | Eşleşen satırlar (+ `-A/-B/-C` ile çevre satırlar) | Belirli dosyada bağlam gerektiğinde |
| `count` | Dosya başına eşleşme sayısı | "Nerede yoğun?" sorusu |

Grep ayrıca `glob` / `type` filtresi alır (`pattern: "fetchUserData", glob: "*.ts"`) — içerik araması + yol filtresi tek çağrıda.

### Glob — Dosya YOLLARINDA Eşleştirme
Dosya **adlarını ve yollarını** pattern ile eşleştirir. Sonuçlar değişiklik zamanına göre sıralı gelir.

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

### Güncel not (sınav cevabını değiştirmez)

Claude Code'un son sürümlerinde macOS/Linux/WSL'de Grep ve Glob varsayılan araç setinden çıkarıldı; Claude aramaları Bash içinden `grep`/`find` ile yapıyor (gömülü `ugrep` / `bfs`) ve bu çağrılar izin kurallarına **`Bash`** olarak ulaşıyor. **Exam guide Grep/Glob'u ayrı araçlar olarak tanımlar; sınavda cevap Grep/Glob'dur.** Ekip tooling kararlarında ise "arama artık Bash izni istiyor mu?" sorusunu bilmek pratikte önemli.

---

## Bash — Komut Çalıştırma

Bash, arama aracı değil, **eylem** aracıdır:

- Test çalıştırmak (`npm test`, `pytest`)
- Build almak, lint çalıştırmak
- Git işlemleri (`git status`, `git diff`, `git commit`)
- Paket kurmak, script çalıştırmak

**Ne zaman Bash DEĞİL:**
- Dosya içinde arama → Grep (yapılandırılmış çıktı, izin istemez)
- Dosya bulma → Glob
- Dosya okuma → Read (satır numaralı, `offset`/`limit`)
- Dosya değiştirme → Edit / Write (`sed -i` yerine — Edit izin kuralı granüler, geri alınabilir)

Kural: **Bash'i yalnızca yerleşik bir aracın yapamadığı iş için kullan.** Bash her seferinde izin ister ve çıktısı serbest metindir; yerleşik araçlar hem daha güvenli hem context açısından daha verimli.

---

## Read / Write / Edit

### Read — Dosya Okuma
Dosyanın tamamını veya `offset` + `limit` ile bir bölümünü okur. "Tüm dosyaları baştan okuma" ilkesinin dosya *içindeki* karşılığı: 2.000 satırlık dosyanın yalnızca ilgili 80 satırını oku (Domain 5 — context yönetimi).

Claude Code kuralı: mevcut bir dosyaya **Write veya Edit yapmadan önce Read gerekir** — okunmamış dosyaya yazma reddedilir. Bu, Claude'un görmediği içeriği ezmesini önler.

### Edit — Hedefli Değişiklik
Tam metin eşleştirmesi (`old_string` → `new_string`) ile **hedefli** değişiklik yapar. Regex veya bulanık eşleştirme yok. Hızlı, kesin, diff'i küçük.

**Ne zaman kullanılır:** Değiştirmek istediğin metin dosyada benzersiz (unique) olduğunda — varsayılan seçim.

### Edit Başarısız Olduğunda — Karar Akışı

Edit, `old_string` dosyada **birden fazla** yerde geçiyorsa (benzersiz değilse) başarısız olur. Sırayla:

1. **Bağlamı genişlet** — `old_string`'e çevresindeki 1–2 satırı ekle ki tek bir yerle eşleşsin. En ucuz çözüm; çoğu durumda yeter.
2. **`replace_all: true`** — tüm eşleşmeleri değiştirmek *istiyorsan* (değişken yeniden adlandırma, import yolu değişikliği). Tek çağrı, deterministik.
3. **Read + Write** — yukarıdakiler işe yaramıyorsa (dosya yapısı değişecek, çok sayıda farklı düzenleme): dosyanın tamamını Read ile yükle, değiştirilmiş hâlini Write ile yaz.

Exam guide yalnızca 3. adımı sayar: *"When Edit fails due to non-unique text matches, using Read + Write as a fallback for reliable file modifications."* Sınavda "Edit benzersiz metin bulamıyor → ne yapmalı?" sorusunun cevabı **Read + Write**'tır. Ama "aynı değişkeni 12 yerde yeniden adlandır" senaryosu gelirse `replace_all` daha doğru araçtır.

### Read + Write'ın maliyeti

"Güvenilir yedek plan" doğru; "her zaman çalışır, bedelsiz" değil:

- Tüm dosya context'e girer (büyük dosyada ciddi token maliyeti)
- Claude dosyanın **tamamını** yeniden üretir — değişmemesi gereken bölümlerde istemsiz değişiklik veya kesme riski
- Diff büyür, inceleme zorlaşır

Bu yüzden sıralama: Edit → bağlamı genişlet → `replace_all` → Read + Write.

### Özet

| Araç | Kullanım | Avantaj | Sınırlama |
|---|---|---|---|
| **Edit** | Benzersiz metin eşleştirmesi ile hedefli değişiklik | Hızlı, kesin, küçük diff | `old_string` benzersiz olmalı (ya da `replace_all`) |
| **Read + Write** | Tam dosya yükle + tam dosya yaz | Edit'in çalışmadığı her durumda çalışır | Tüm dosya context'e girer ve yeniden üretilir |

---

## Artımlı Kod Tabanı Anlama (Incremental Codebase Understanding)

Büyük bir kod tabanını anlamak için doğru yaklaşım:

1. **Grep ile giriş noktalarını bul** — `files_with_matches` modunda: fonksiyon tanımları, import ifadeleri, hata mesajları
2. **Grep `content` ile daraltılmış bağlam al** — yalnızca ilgili dosyada, `-C 3` gibi kısa çevreyle
3. **Read ile importları takip et** — giriş noktalarından akışları izle; gerekirse `offset`/`limit` ile bölüm bölüm
4. **Tüm dosyaları baştan okuma** — bu context bütçesi katili

> **Tüm dosyaları önceden (upfront) okumak YANLIŞ yaklaşımdır.** Bu, context window'u gereksiz veriyle doldurur. Bunun yerine: Grep ile hedefleri belirle, Read ile sadece gerekli dosyaları (ve bölümleri) oku.

### Fonksiyon Kullanımını Takip Etme — Wrapper Modüller

Bir fonksiyon `utils/date.ts`'te tanımlı ama `lib/index.ts` onu yeniden dışa aktarıyor (re-export); kullanıcılar `lib`'den import ediyor. Doğrudan tanım adını Grep'lemek çağıranların çoğunu kaçırır.

İki adım:
1. **Dışa aktarılan isimleri belirle** — wrapper modülde `export` ifadelerini Grep'le: `export { formatDate, parseDate as parse }` → dışarıya çıkan adlar `formatDate` ve **`parse`** (`parseDate` değil!)
2. **Her ismi kod tabanı genelinde Grep'le** — `formatDate` ve `parse` için ayrı ayrı; takma adla (alias) yeniden dışa aktarılan isimler tuzaktır

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Grep | Dosya İÇERİĞİNDE arama — fonksiyon çağrıları, hata mesajları, importlar; `files_with_matches` en ucuz mod |
| Glob | Dosya YOLLARINDA eşleştirme — uzantıya göre dosya bulma, config dosyaları |
| Bash | Komut çalıştırma (test, build, git) — arama/okuma/düzenleme için yerleşik araçları tercih et; izin ister |
| Read | Dosya okuma; `offset`/`limit` ile kısmi; Write/Edit öncesi zorunlu |
| Edit | Benzersiz metin eşleştirmesi ile hedefli değişiklik — hızlı ve kesin |
| Edit başarısız | Bağlamı genişlet → `replace_all` → Read + Write (sınav cevabı: Read + Write) |
| Read + Write | Güvenilir yedek — ama tüm dosya context'e girer ve yeniden üretilir |
| Artımlı anlama | Grep (files) → Grep (content) → Read (bölüm). Tüm dosyaları baştan okuma |
| Wrapper izleme | Önce `export` edilen adları (alias dahil) bul, sonra her adı Grep'le |
| Sınav tuzağı | Grep ile Glob'u karıştırmak — içerik araması mı, yol eşleştirmesi mi? |

---

## Pratik Senaryo

> Bir geliştirici, kod tabanındaki kullanımdan kaldırılmış (deprecated) bir fonksiyonu (`oldCalculate`) çağıran tüm dosyaları bulmak, bu dosyaların her biri için ilgili test dosyalarını da bulmak ve değişiklik sonrası testleri çalıştırmak istiyor.
>
> **Doğru araç sıralaması hangisidir?**
>
> **A)** Glob ile tüm `.ts` dosyalarını bul, sonra her birini Read ile oku ve `oldCalculate` içerenleri filtrele; testleri Bash ile çalıştır.
>
> **B)** Grep ile `oldCalculate` fonksiyon adını ara (çağıranları bulur), sonra Glob ile bulunan dosya adlarına karşılık gelen test dosyalarını eşleştir (`**/*.test.tsx`), değişiklikleri Edit ile yap, testleri Bash ile çalıştır.
>
> **C)** Bash ile `grep -r oldCalculate .` ve `find . -name "*.test.tsx"` çalıştır, değişiklikleri `sed -i` ile yap, testleri Bash ile çalıştır.
>
> **D)** Glob ile `**/*oldCalculate*` pattern'ını kullanarak fonksiyonu içeren dosyaları bul, Write ile dosyaları güncelle.

### Doğru Cevap: B

**Neden B doğru:** Her araç kendi güçlü olduğu alanda:
1. **Grep** ile `oldCalculate` fonksiyon adını dosya içeriklerinde ara → çağıran dosyalar
2. **Glob** ile `**/*.test.tsx` → test dosyaları, bulunan adlarla eşleştir
3. **Edit** ile hedefli değişiklik (izin granüler, diff küçük)
4. **Bash** ile `npm test` — yerleşik bir aracın yapamadığı tek iş bu

**Neden A yanlış:** Tüm `.ts` dosyalarını bulup hepsini okumak verimsiz — context bütçesi israfı. Grep doğrudan hedefi bulur. Bash kısmı doğru ama sıralamanın başı yanlış.

**Neden C yanlış:** Her şeyi Bash ile yapmak *çalışır* ama yerleşik araçların avantajlarını atar: Grep/Glob izin istemez ve yapılandırılmış çıktı verir; `sed -i` Edit'in benzersizlik güvencesini ve okunabilir diff'ini vermez, izin kuralları da `Bash(sed …)` seviyesinde kalır. Bash yalnızca son adım (test) için doğru araç.

**Neden D yanlış:** Glob dosya **yollarında** arama yapar, dosya **içeriklerinde** değil. `oldCalculate` fonksiyon adı dosya adında geçmiyorsa (ki genellikle geçmez), Glob hiçbir sonuç döndürmez. Ayrıca Write tüm dosyayı ezer — hedefli değişiklik için Edit doğru araç.
