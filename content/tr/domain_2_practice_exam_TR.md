# Domain 2 — Pratik Sınav

## Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

**Dağılım:**
- 2 soru → Araç açıklamaları ve misrouting (2.1)
- 2 soru → Hata yönetimi ve kategoriler (2.2)
- 1 soru → Araç dağılımı ve tool_choice (2.3)
- 1 soru → MCP sunucu konfigürasyonu (2.4)
- 1 soru → Yerleşik araçlar (2.5)

**Geçme kriteri:** 6+/7

---

## Soru 1 (Task Statement 2.1)

> Bir müşteri destek agent'ının 3 aracı var:
>
> - `get_account_info`: "Hesap bilgilerini getirir"
> - `get_billing_info`: "Fatura bilgilerini getirir"
> - `get_subscription_info`: "Abonelik bilgilerini getirir"
>
> Kullanıcılar şikâyet ediyor: "Aboneliğimi yükseltmek istiyorum" dediğinde agent `get_account_info` çağırıyor, fatura sorguları `get_subscription_info`'ya gidiyor. Genel misrouting oranı %30.
>
> **İlk adım olarak ne yapılmalı?**
>
> **A)** Üç aracı tek bir `get_customer_data` aracında birleştir — Claude tek araçla hata yapamaz.
>
> **B)** System prompt'a "fatura soruları için get_billing_info, abonelik soruları için get_subscription_info kullan" şeklinde few-shot örnekler ekle.
>
> **C)** Her aracın açıklamasını genişlet — hangi veri alanlarını döndürdüğünü, hangi sorgu türleri için kullanılacağını ve diğer araçlardan farkını açıkça belirt.
>
> **D)** Claude'dan önce bir intent classifier ekle — sorguyu analiz edip doğru araca yönlendirsin.

### Doğru Cevap: C

**Neden C doğru:** Kök neden açıklamaların belirsiz olması — üç araç da "X bilgilerini getirir" formatında, Claude ayrım yapamıyor. Açıklamaları genişletmek (hangi veri alanlarını döndürdüğü, hangi sorgular için kullanılacağı, diğer araçlardan farkı) düşük eforlu, yüksek etkili bir çözüm ve kök nedeni doğrudan hedef alıyor.

**Neden A yanlış:** Birleştirme görev ayrımını bozar. Üç farklı veri kaynağını tek araçta birleştirmek araç odağını kaybettirir ve geri döndürülen veri miktarını gereksiz artırır. Ayrıca çok fazla efor gerektirir.

**Neden B yanlış:** Few-shot örnekler token maliyeti yaratır ve belirtiyi tedavi eder, kök nedeni değil. Açıklamalar belirsizken örnekler güvenilir çözüm sağlamaz. Prompt-based guidance olasılıksaldır.

**Neden D yanlış:** Intent classifier ilk adım için aşırı mühendislik. Basit çözümü (açıklama iyileştirme) henüz denemedin. Classifier ekstra karmaşıklık ve bakım maliyeti getirir.

---

## Soru 2 (Task Statement 2.1)

> Bir agent'ın `analyze_document` aracı var. Bu araç tek bir çağrıda dokümanı özetliyor, anahtar verileri çıkarıyor ve iddiaları doğruluyor. Agent bazen sadece özet istendiğinde gereksiz doğrulama yapıyor, bazen de doğrulama istendiğinde sadece özet döndürüyor.
>
> **Kök neden ve çözüm nedir?**
>
> **A)** Aracın açıklaması yetersiz — daha detaylı açıklama yaz.
>
> **B)** Araç çok geniş kapsamlı — `summarize_content`, `extract_data_points` ve `verify_claim_against_source` olarak üç amaca özel araca böl.
>
> **C)** System prompt'a "sadece istenen işlemi yap" talimatı ekle.
>
> **D)** Aracın girdi parametrelerine `operation_type` alanı ekle — Claude hangi işlemi istediğini belirtsin.

### Doğru Cevap: B

**Neden B doğru:** Araç üç farklı işi birden yapıyor — özetleme, veri çıkarma, doğrulama. Claude tek bir araç çağrısıyla üçünü de tetikliyor ve hangi çıktının istendiğini kontrol edemiyor. Amaca özel araçlara bölmek her aracı tek bir iş için kesin şekilde tanımlar. Claude tam olarak istediği işlemi seçebilir.

**Neden A yanlış:** Açıklama iyileştirme tek bir aracın ne yaptığını netleştirir ama yapısal sorunu çözmez — araç hâlâ üç işi birden yapıyor. Daha iyi açıklama Claude'un aracı ne zaman çağıracağını iyileştirir ama aracın davranışını değiştirmez.

**Neden C yanlış:** Prompt talimatı olasılıksal. "Sadece istenen işlemi yap" demek aracın üç işi birden yapma yapısını değiştirmez — bu mimari bir sorun, prompt sorunu değil.

**Neden D yanlış:** `operation_type` parametresi bir geçici çözüm — karmaşıklığı aracın içine taşır. Araç hâlâ üç farklı mantığı barındırıyor, sadece bir switch eklemiş olursun. Temiz mimari: her araç tek bir iş yapar.

---

## Soru 3 (Task Statement 2.2)

> Bir agent uluslararası para transferi yapmaya çalışıyor. Araç şu yanıtı döndürüyor:
>
> ```json
> {
>   "isError": true,
>   "errorCategory": "business",
>   "isRetryable": false,
>   "description": "Transfer tutarı ($15,000) günlük limiti ($10,000) aşıyor.",
>   "customerMessage": "Günlük transfer limitiniz $10,000'dır. Daha yüksek limitler için hesap yöneticinizle iletişime geçin."
> }
> ```
>
> **Agent ne yapmalı?**
>
> **A)** 5 saniye bekleyip tekrar dene — geçici bir hata olabilir.
>
> **B)** Transfer tutarını otomatik olarak $10,000'a düşürüp tekrar dene.
>
> **C)** Tekrar denememeli. Müşteriye `customerMessage`'daki bilgiyi iletmeli ve alternatif yol sunmalı (hesap yöneticisine yönlendirme).
>
> **D)** Girdiyi düzeltip tekrar denemeli — validation hatası olabilir.

### Doğru Cevap: C

**Neden C doğru:** `errorCategory: "business"` ve `isRetryable: false` — bu bir iş kuralı ihlali, tekrar deneme YANLIŞ. Politika değişmediği sürece aynı işlem her seferinde başarısız olacak. Agent müşteriye `customerMessage`'daki bilgiyi iletmeli ve alternatif yol sunmalı (hesap yöneticisine yönlendirme).

**Neden A yanlış:** Bu geçici (transient) hata değil — iş kuralı hatası. Bekleme süresi politikayı değiştirmez. 5 saniye sonra da, 5 dakika sonra da aynı hata döner. `isRetryable: false` açıkça tekrar denemeyi reddediyor.

**Neden B yanlış:** Tutarı otomatik olarak değiştirmek müşterinin isteğini geçersiz kılar. Müşteri $15,000 transfer etmek istiyor — agent kendi başına $10,000'a düşürmemeli. Bu iş kararı müşteriye ait.

**Neden D yanlış:** Bu validation hatası değil — format doğru, tutar geçerli bir sayı. Sorun iş kuralı: günlük limit aşılmış. `errorCategory: "business"` bunu açıkça belirtiyor. Validation hataları girdi formatıyla ilgilidir (yanlış tip, eksik alan).

---

## Soru 4 (Task Statement 2.2)

> Bir multi-agent sistemde web search subagent bir API çağrısında timeout alıyor. Subagent 2 kez daha deniyor ama başarısız oluyor.
>
> **Subagent ne yapmalı?**
>
> **A)** Hatayı sessizce yutmalı ve boş sonuç döndürmeli — koordinatörü gereksiz bilgiyle meşgul etmemeli.
>
> **B)** Hemen ilk timeout'ta koordinatöre yaymalı — yerel retry zaman kaybı.
>
> **C)** Hatayı koordinatöre yaymalı — kısmi sonuçları (timeout'tan önce ne elde etti) ve denenen kurtarma adımlarını (2 retry yapıldı) dahil etmeli.
>
> **D)** Sonsuz döngüde retry yapmalı — transient hatalar sonunda düzelir.

### Doğru Cevap: C

**Neden C doğru:** Subagent yerel kurtarmayı denedi (2 retry) ve başarısız oldu. Artık yerel olarak çözemediği bir hata var. Doğru davranış: hatayı koordinatöre yay, ama bilgilendirilmiş bir şekilde — kısmi sonuçları ve denenen kurtarma adımlarını dahil et. Böylece koordinatör ne yapacağına karar verebilir: farklı bir subagent dene, farklı bir kaynak kullan, veya insana yönlendir.

**Neden A yanlış:** Hatayı sessizce yutmak en tehlikeli yaklaşım. Koordinatör sorundan habersiz kalır, boş sonucu "veri yok" olarak yorumlayabilir (erişim hatası vs boş sonuç karışıklığı). Bilgi kaybı ve yanlış kararlar.

**Neden B yanlış:** İlk timeout'ta hemen yayılma, yerel kurtarma fırsatını kaçırır. Transient hatalar genellikle retry ile çözülür — subagent önce kendisi denemeli. Her geçici hatayı koordinatöre yaymak gereksiz yük ve gecikme yaratır.

**Neden D yanlış:** Sonsuz döngüde retry sistemi kilitler. Transient hatalar "sonunda düzelir" varsayımı her zaman doğru değil — servis uzun süre çökebilir. Makul sayıda retry (2-3) sonra çözemediysen yukarı yay.

---

## Soru 5 (Task Statement 2.3)

> Bir araştırma agent'ına 16 araç verilmiş: 5 web arama aracı, 4 doküman analiz aracı, 3 veritabanı sorgulama aracı, 2 e-posta aracı ve 2 takvim aracı. Agent sık sık yanlış araç seçiyor ve görevleri tamamlamakta zorlanıyor.
>
> Aynı zamanda, agent'ın metadata çıkarımı yapması zorunlu bir ilk adım olmasına rağmen, bazen bu adımı atlayıp doğrudan analiz yapıyor.
>
> **Bu iki sorunu birden çözen yaklaşım hangisidir?**
>
> **A)** Tüm araç açıklamalarını genişlet ve system prompt'a "her zaman önce metadata çıkar" talimatı ekle.
>
> **B)** Araçları role-specific agent'lara dağıt (agent başına 4-5 araç) ve metadata çıkarımı için `tool_choice: {"type": "tool", "name": "extract_metadata"}` kullanarak zorunlu ilk adımı dayat.
>
> **C)** Araç sayısını 8'e düşür — en az kullanılan araçları kaldır.
>
> **D)** Tek bir "do_everything" aracı oluştur ve tüm işlemleri onun üzerinden yap.

### Doğru Cevap: B

**Neden B doğru:** İki sorunu birden çözer:
1. **Araç aşırı yüklemesi:** 16 araç → role-specific agent'lara dağıt (agent başına 4-5 araç). Seçim güvenilirliği artar.
2. **Zorunlu ilk adım:** `tool_choice: {"type": "tool", "name": "extract_metadata"}` ile metadata çıkarımını deterministik olarak zorla. Model atlayamaz — fiziksel olarak bu aracı çağırmak zorunda.

**Neden A yanlış:** İki parçalı bir çözüm ama her ikisi de olasılıksal. Açıklama genişletme 16 araçlık seçim sorununu kısmen iyileştirir ama kök nedeni (çok fazla araç) çözmez. System prompt talimatı "her zaman metadata çıkar" olasılıksal — %100 garanti etmez. Zorunlu adımlar için deterministik çözüm (tool_choice) gerekir.

**Neden C yanlış:** Araç sayısını düşürmek fonksiyonalite kaybı yaratır. Ve hangi araçları kaldıracağını "en az kullanılan" kriterine göre seçmek yanlış — az kullanılan araç kritik bir araç olabilir. Asıl çözüm araçları kaldırmak değil, doğru agent'lara dağıtmak.

**Neden D yanlış:** Tek bir "do_everything" aracı, araç bölmenin (tool splitting) tam tersi. Tüm karmaşıklığı tek bir araca yığmak Claude'un ne istediğini belirtmesini imkânsız kılar. Soru 2'deki `analyze_document` sorununun daha büyük versiyonu.

---

## Soru 6 (Task Statement 2.4)

> Bir takım yeni bir projeye başlıyor. GitHub entegrasyonu için MCP sunucusu yapılandırılacak. Bir geliştirici şu `.mcp.json` dosyasını öneriyor:
>
> ```json
> {
>   "mcpServers": {
>     "github": {
>       "command": "github-mcp-server",
>       "env": {
>         "GITHUB_TOKEN": "ghp_abc123def456ghi789"
>       }
>     }
>   }
> }
> ```
>
> **Bu konfigürasyondaki güvenlik sorunu nedir?**
>
> **A)** `github-mcp-server` komutu yanlış — doğru komut `mcp-github` olmalı.
>
> **B)** GitHub token doğrudan `.mcp.json` dosyasına yazılmış. Bu dosya versiyon kontrol altında olduğu için token repoya girecek. Token `${GITHUB_TOKEN}` ortam değişkeni olarak referans edilmeli.
>
> **C)** `.mcp.json` yerine `~/.claude.json` kullanılmalı — MCP konfigürasyonu her zaman kullanıcı seviyesinde olmalı.
>
> **D)** Token çok kısa — daha güçlü bir token üretilmeli.

### Doğru Cevap: B

**Neden B doğru:** `.mcp.json` versiyon kontrol altındadır — Git ile takip edilir ve repoya girer. Token doğrudan dosyaya yazılırsa, repo'ya push edildiğinde herkes token'ı görebilir. Güvenlik ihlali. Çözüm: `${GITHUB_TOKEN}` ortam değişkeni sözdizimini kullan. Her geliştirici kendi token'ını yerel olarak ayarlar, token'lar repoya girmez.

**Neden A yanlış:** Komut adı konfigürasyonun güvenlik sorunu değil. Soru güvenlik sorununu soruyor — doğru komut adı ayrı bir konu.

**Neden C yanlış:** `.mcp.json` (proje seviyesi) ve `~/.claude.json` (kullanıcı seviyesi) farklı amaçlar için var. Proje seviyesindeki araç konfigürasyonu takımla paylaşılması gereken bilgidir — `.mcp.json`'da olması doğru. Sorun dosyanın yeri değil, token'ın hardcode edilmesi.

**Neden D yanlış:** Token'ın uzunluğu veya gücü buradaki güvenlik sorunu değil. Sorun token'ın nerede saklandığı — versiyon kontrol altındaki bir dosyada açık metin olarak bulunması. En güçlü token bile repoya girerse tehlikeye girer.

---

## Soru 7 (Task Statement 2.5)

> Bir geliştirici büyük bir kod tabanında çalışıyor. Şu iki görevi tamamlaması gerekiyor:
>
> 1. `fetchUserData` fonksiyonunu çağıran tüm dosyaları bulmak
> 2. Projedeki tüm `.config.yml` dosyalarını bulmak
>
> **Her görev için doğru araç hangisidir?**
>
> **A)** Her ikisi için de Grep kullan — Grep her türlü aramayı yapar.
>
> **B)** Görev 1 için Glob (`**/*fetchUserData*`), Görev 2 için Grep (`fetchUserData` pattern).
>
> **C)** Görev 1 için Grep (`fetchUserData` pattern — dosya içeriklerinde arar), Görev 2 için Glob (`**/*.config.yml` — dosya yollarında eşleştirir).
>
> **D)** Her ikisi için de Read kullan — tüm dosyaları oku ve manuel filtrele.

### Doğru Cevap: C

**Neden C doğru:** Her araç kendi güçlü olduğu alanda kullanılıyor:
1. **Grep** ile `fetchUserData` fonksiyon adını dosya **içeriklerinde** ara → bu fonksiyonu çağıran dosyaları bulur
2. **Glob** ile `**/*.config.yml` pattern'ını dosya **yollarında** eşleştir → config dosyalarını bulur

Grep = içerik araması. Glob = yol eşleştirmesi. Her biri doğru yerde.

**Neden A yanlış:** Grep dosya içeriklerinde arama yapar — `.config.yml` dosyalarını bulmak için dosya yollarında eşleştirme gerekir, bu Glob'un işi. Grep ile dosya uzantısına göre arama yapamazsın (dosya içeriğinde ".config.yml" string'i aramak farklı bir şey).

**Neden B yanlış:** Tam tersi eşleştirme yapılmış. Glob dosya **yollarında** arama yapar — `fetchUserData` fonksiyon adı dosya adında geçmiyorsa (ki genellikle geçmez) Glob hiçbir sonuç döndürmez. Fonksiyon çağrıları dosya **içeriklerinde** bulunur — bu Grep'in işi.

**Neden D yanlış:** Tüm dosyaları Read ile okumak en kötü yaklaşım — çok yavaş, context bütçesi katili. Grep ve Glob bu işleri tek seferde, verimli şekilde yapar. Tüm dosyaları önceden okumak asla doğru yaklaşım değil.
