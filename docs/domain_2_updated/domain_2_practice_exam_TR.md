# Domain 2 — Pratik Sınav

## Araç Tasarımı ve MCP Entegrasyonu (Sınavın %18'i)

**Dağılım (10 soru):**
- 2 soru → Araç arayüz tasarımı, misrouting, bölme/birleştirme (2.1)
- 2 soru → Yapılandırılmış hata yanıtları (2.2)
- 2 soru → Araç dağılımı ve tool_choice (2.3)
- 2 soru → MCP sunucu entegrasyonu (2.4)
- 2 soru → Yerleşik araçlar (2.5)

**Geçme kriteri:** 8+/10

**Puanlama:**

| Puan | Değerlendirme |
|---|---|
| 10/10 | Domain hazır — sonraki domain'e geç |
| 8–9/10 | Geçer — yanlış soruların task statement'ını tekrar oku |
| 6–7/10 | Sınır — ilgili ders notlarını baştan çalış, sınavı tekrar çöz |
| ≤5/10 | Domain'i baştan çalış |

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
> **C)** Her aracın açıklamasını genişlet — hangi veri alanlarını döndürdüğünü, hangi sorgu türleri için kullanılacağını ve diğer araçlardan farkını açıkça belirt; gerekirse adları da netleştir (`get_billing_history`, `get_subscription_plan`).
>
> **D)** Claude'dan önce bir intent classifier ekle — sorguyu analiz edip doğru araca yönlendirsin.

### Doğru Cevap: C

**Neden C doğru:** Kök neden açıklamaların belirsiz olması — üç araç da "X bilgilerini getirir" formatında, Claude ayrım yapamıyor. Açıklamaları genişletmek (hangi veri alanlarını döndürdüğü, hangi sorgular için kullanılacağı, diğer araçlardan farkı) ve gerekirse yeniden adlandırmak düşük eforlu, yüksek etkili bir çözüm; exam guide'ın iki Skills maddesini ("writing descriptions that clearly differentiate" + "renaming tools and updating descriptions") birlikte uygular.

**Neden A yanlış:** Birleştirme belirsizliği ortadan kaldırmaz, aracın içine taşır — artık araç hangi veriyi döndüreceğini tahmin etmek zorunda. Üç farklı çıktı sözleşmesi tek araca sığmaz; görev ayrımı bozulur.

**Neden B yanlış:** Few-shot örnekler token maliyeti yaratır ve belirtiyi tedavi eder, kök nedeni değil. Prompt-based guidance olasılıksaldır; açıklamalar belirsizken güvenilir çözüm sağlamaz.

**Neden D yanlış:** Intent classifier ilk adım için aşırı mühendislik. Basit çözümü (açıklama iyileştirme) henüz denemedin. Classifier ekstra karmaşıklık ve bakım maliyeti getirir.

---

## Soru 2 (Task Statement 2.1)

> Bir agent'ın `analyze_document` aracı var. Tek bir çağrıda dokümanı özetliyor (çıktı: düz metin), anahtar verileri çıkarıyor (çıktı: JSON kayıt listesi) ve iddiaları doğruluyor (çıktı: iddia başına destekleniyor/desteklenmiyor + kanıt). Üç işlemin girdi gereksinimleri de farklı: doğrulama bir iddia listesi ister, özetleme istemez. Agent bazen sadece özet istendiğinde gereksiz doğrulama yapıyor, bazen de doğrulama istendiğinde sadece özet döndürüyor.
>
> **Kök neden ve çözüm nedir?**
>
> **A)** Aracın açıklaması yetersiz — daha detaylı açıklama yaz.
>
> **B)** Araç üç farklı amacı ve üç farklı girdi/çıktı sözleşmesini tek arayüzde birleştiriyor — `summarize_content`, `extract_data_points` ve `verify_claim_against_source` olarak amaca özel araçlara böl.
>
> **C)** System prompt'a "sadece istenen işlemi yap" talimatı ekle.
>
> **D)** Aracın girdi parametrelerine `operation_type` alanı ekle — Claude hangi işlemi istediğini belirtsin.

### Doğru Cevap: B

**Neden B doğru:** Bölme ölçütü "kaç işlem" değil, "kaç farklı amaç ve çıktı sözleşmesi". Burada üç farklı çıktı şeması ve farklı girdi gereksinimleri var — tek bir araç bunları tutarlı bir sözleşmeyle sunamaz. Amaca özel araçlara bölmek her aracı tek bir iş için, tanımlı girdi/çıktı sözleşmesiyle kesin şekilde tanımlar. Exam guide Skill: "Splitting generic tools into purpose-specific tools with defined input/output contracts."

**Neden A yanlış:** Açıklama iyileştirme Claude'un aracı *ne zaman* çağıracağını netleştirir ama aracın *ne döndüreceğini* değiştirmez — araç hâlâ üç işi birden yapıyor ve çıktı şeması belirsiz.

**Neden C yanlış:** Prompt talimatı olasılıksal. "Sadece istenen işlemi yap" demek aracın üç işi birden yapma yapısını değiştirmez — bu arayüz sorunu, prompt sorunu değil.

**Neden D yanlış:** `operation_type` parametresi işlemi seçtirir ama çıktı sözleşmesini çözmez — araç `operation_type`'a göre üç farklı şema döndürür, Claude hangi şemayı bekleyeceğini açıklamadan çıkaramaz; doğrulama için gereken `claims` parametresi diğer işlemlerde anlamsız kalır. Aynı iş akışının adımları olsaydı (bkz. `schedule_event` konsolidasyon örneği) tek araç savunulabilirdi; burada üç ayrı amaç var.

---

## Soru 3 (Task Statement 2.2)

> Bir agent uluslararası para transferi yapmaya çalışıyor. MCP aracı şu yanıtı döndürüyor:
>
> ```json
> {
>   "isError": true,
>   "content": [{ "type": "text", "text": "{\"errorCategory\":\"business\",\"isRetryable\":false,\"description\":\"Transfer tutarı ($15,000) günlük limiti ($10,000) aşıyor.\",\"customerMessage\":\"Günlük transfer limitiniz $10,000'dır. Daha yüksek limitler için hesap yöneticinizle iletişime geçin.\"}" }]
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

**Neden C doğru:** `errorCategory: "business"` ve `isRetryable: false` — bu bir iş kuralı ihlali, tekrar deneme YANLIŞ. Politika değişmediği sürece aynı işlem her seferinde başarısız olacak. Agent müşteriye `customerMessage`'daki bilgiyi iletmeli ve alternatif yol sunmalı.

**Neden A yanlış:** Bu geçici (transient) hata değil — iş kuralı hatası. Bekleme süresi politikayı değiştirmez. `isRetryable: false` açıkça tekrar denemeyi reddediyor.

**Neden B yanlış:** Tutarı otomatik olarak değiştirmek müşterinin isteğini geçersiz kılar. Bu iş kararı müşteriye ait; agent kendi başına $10,000'a düşürmemeli.

**Neden D yanlış:** Bu validation hatası değil — format doğru, tutar geçerli bir sayı. Sorun iş kuralı: günlük limit aşılmış. `errorCategory: "business"` bunu açıkça belirtiyor.

---

## Soru 4 (Task Statement 2.2)

> Kendi MCP sunucunu yazıyorsun. `lookup_order` aracı, sipariş numarası veritabanında yoksa `-32602 Invalid params` JSON-RPC protokol hatası fırlatıyor; veritabanı bağlantısı koptuğunda ise `content: []` ile boş sonuç döndürüyor. Üretimde agent, var olmayan sipariş numaralarında "bir hata oluştu" deyip duruyor, veritabanı kesintisinde ise müşteriye "siparişiniz bulunamadı" diyor.
>
> **Kök neden ve doğru tasarım nedir?**
>
> **A)** Retry sayısını artır — veritabanı kesintileri retry ile çözülür.
>
> **B)** İki durum da yanlış kanalda raporlanıyor. "Sipariş bulunamadı" geçerli bir boş sonuçtur → `isError: false` + `resultCount: 0`. Veritabanı kopması bir araç yürütme hatasıdır → `isError: true` + `errorCategory: "transient"`, `isRetryable: true`. Protokol hatası yalnızca bilinmeyen araç / şemaya uymayan argüman için kullanılmalı.
>
> **C)** Her iki durumda da protokol hatası fırlat — böylece istemci tutarlı davranır.
>
> **D)** System prompt'a "'bir hata oluştu' yerine 'sipariş bulunamadı' de" talimatı ekle.

### Doğru Cevap: B

**Neden B doğru:** MCP iki hata mekanizması tanımlar: protokol hatası (JSON-RPC `error`) modele **ulaşmaz** — istemci katmanında kalır; araç yürütme hatası (`isError: true`) modele ulaşır ve model kendini düzeltebilir. Var olmayan sipariş bir hata bile değil — başarılı sorgu, sıfır eşleşme (`isError: false`). Veritabanı kopması ise gerçek erişim hatası; `isError: true` + transient/retryable metadata ile agent'ın retry kararı vermesi sağlanır. Mevcut tasarım iki durumu tam tersine kodlamış.

**Neden A yanlış:** Retry, boş sonucu (var olmayan sipariş) değiştirmez ve boş dizi olarak dönen kesintiyi agent hata olarak tanımaz ki retry etsin. Sorun retry sayısı değil, sinyal yapısı.

**Neden C yanlış:** Protokol hatası modele ulaşmaz — Claude neyin yanlış gittiğini göremez, girdiyi düzeltemez, alternatif yol arayamaz. İş/API/doğrulama hataları `isError: true` ile *sonuç olarak* döndürülmeli.

**Neden D yanlış:** Prompt, aracın hangi durumda ne döndürdüğünü bilmiyor; iki durumu ayırt edemez. Yapısal soruna yapısal çözüm gerekir.

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
> **B)** Araçları role-specific agent'lara dağıt (agent başına 4–5 araç) ve ilk istekte `tool_choice: {"type": "tool", "name": "extract_metadata"}` ile zorunlu ilk adımı dayat; sonraki turlarda `tool_choice`'u `auto`'ya döndür.
>
> **C)** Araçları role-specific agent'lara dağıt ve tüm turlarda `tool_choice: {"type": "tool", "name": "extract_metadata"}` kullan — böylece adım asla atlanmaz.
>
> **D)** Tek bir "do_everything" aracı oluştur ve tüm işlemleri onun üzerinden yap.

### Doğru Cevap: B

**Neden B doğru:** İki sorunu birden çözer:
1. **Araç aşırı yüklemesi:** 16 araç → role-specific agent'lara dağıt (agent başına 4–5). Seçim güvenilirliği artar.
2. **Zorunlu ilk adım:** İlk istekte forced `tool_choice` ile metadata çıkarımı deterministik olarak zorlanır; model atlayamaz. Sonraki turlarda `auto`'ya dönülür ki model analize geçebilsin — exam guide: "ensure a specific tool is called first, then processing subsequent steps in follow-up turns."

**Neden A yanlış:** İki parçalı ama her ikisi de olasılıksal. Açıklama genişletme 16 araçlık seçim sorununu kısmen iyileştirir ama kök nedeni (çok fazla araç) çözmez. System prompt talimatı "her zaman metadata çıkar" %100 garanti etmez. Zorunlu adımlar için deterministik çözüm (tool_choice) gerekir.

**Neden C yanlış:** Dağıtım kısmı doğru ama `tool_choice` istek bazında çalışır; her turda forced bırakılırsa model **her turda** yine `extract_metadata`'yı çağırmaya zorlanır ve analize hiç geçemez — sonsuz metadata döngüsü. Forced seçim yalnızca ilk turda; sonra `auto`.

**Neden D yanlış:** Tek bir "do_everything" aracı, araç bölmenin tam tersi. Tüm karmaşıklığı tek araca yığmak Claude'un ne istediğini belirtmesini imkânsız kılar.

---

## Soru 6 (Task Statement 2.3)

> Bir belge işleme pipeline'ında Claude'a üç araç tanımlı: `classify_invoice`, `classify_receipt`, `classify_contract` — her biri farklı bir JSON şeması döndürür. Pipeline, Claude'un yanıtını doğrudan `json.loads` ile ayrıştırıyor. Üretimde bazen Claude araç çağırmak yerine "Bu belge bir fatura gibi görünüyor, sınıflandırmamı ister misiniz?" gibi metin döndürüyor ve pipeline çöküyor. Bazı belgelerde de Claude tek yanıtta iki sınıflandırma aracını birden çağırıyor.
>
> **Hangi konfigürasyon iki sorunu da çözer?**
>
> **A)** `tool_choice: {"type": "auto"}` + system prompt'a "her zaman bir araç çağır" talimatı.
>
> **B)** `tool_choice: {"type": "any"}` + `disable_parallel_tool_use: true` — model mutlaka üç araçtan birini çağırır, tam olarak bir tane.
>
> **C)** `tool_choice: {"type": "tool", "name": "classify_invoice"}` — belgelerin çoğu fatura.
>
> **D)** `tool_choice: {"type": "none"}` + çıktıyı regex ile ayrıştır.

### Doğru Cevap: B

**Neden B doğru:** `any` modelin metin yerine **mutlaka** bir araç çağırmasını garanti eder; hangisini seçeceği kendisine bırakılır — üç şemadan biri kesin gelir. Exam guide Skill: "Setting tool_choice: 'any' to guarantee the model calls a tool rather than returning conversational text." `disable_parallel_tool_use: true` ise tek yanıtta birden fazla `tool_use` bloğunu engeller; `any` ile birlikte "tam olarak bir araç çağrısı" garantisi verir.

**Neden A yanlış:** `auto` modele metin döndürme serbestliği bırakır; prompt talimatı olasılıksaldır. "Her zaman araç çağır" garantisi için deterministik `tool_choice` gerekir.

**Neden C yanlış:** Forced tek araç, makbuz ve sözleşmeleri de fatura şemasıyla sınıflandırmaya zorlar — yanlış şema, yanlış veri. Seçim modele bırakılmalı, çağırma zorunluluğu dayatılmalı: bu `any`'nin tanımıdır.

**Neden D yanlış:** `none` araç kullanımını tamamen kapatır — tam tersi yönde. Regex ile serbest metin ayrıştırmak yapılandırılmış çıktı garantisini atar.

---

## Soru 7 (Task Statement 2.4)

> Bir takım yeni bir projeye başlıyor. GitHub entegrasyonu için MCP sunucusu yapılandırılacak. Bir geliştirici şu `.mcp.json` dosyasını öneriyor:
>
> ```json
> {
>   "mcpServers": {
>     "github": {
>       "type": "stdio",
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
> **A)** Token'ı `.claude/settings.json` dosyasına taşı — MCP kimlik bilgileri ayarlar dosyasında saklanmalı.
>
> **B)** GitHub token doğrudan `.mcp.json` dosyasına yazılmış. Bu dosya versiyon kontrol altında olduğu için token repoya girecek. Token `${GITHUB_TOKEN}` ortam değişkeni olarak referans edilmeli; her geliştirici kendi token'ını yerel ortamında tanımlar.
>
> **C)** `.mcp.json` yerine `~/.claude.json` kullanılmalı — MCP konfigürasyonu her zaman kullanıcı seviyesinde olmalı.
>
> **D)** Token çok kısa — daha güçlü bir token üretilmeli.

### Doğru Cevap: B

**Neden B doğru:** `.mcp.json` versiyon kontrol altındadır — Git ile takip edilir ve repoya girer. Token doğrudan dosyaya yazılırsa herkes görebilir. Çözüm: `${GITHUB_TOKEN}` ortam değişkeni sözdizimi (gerekirse `${GITHUB_TOKEN:-}` ile varsayılan). Her geliştirici kendi token'ını yerel olarak ayarlar; token'lar repoya girmez. Exam guide: "Environment variable expansion in .mcp.json for credential management without committing secrets."

**Neden A yanlış:** `.claude/settings.json` da paylaşılan, versiyon kontrol altındaki bir proje dosyasıdır (Domain 3.1) — token yine repoya girer. Dosya değiştirmek sorunu taşır, çözmez; ayrıca settings.json MCP sunucu tanımı için doğru yer değildir.

**Neden C yanlış:** `.mcp.json` (proje) ve `~/.claude.json` (kullanıcı/local) farklı amaçlar için var. Takımın ortak araç konfigürasyonu paylaşılması gereken bilgidir — `.mcp.json`'da olması doğru. Sorun dosyanın yeri değil, token'ın hardcode edilmesi.

**Neden D yanlış:** Token'ın uzunluğu veya gücü buradaki güvenlik sorunu değil. En güçlü token bile repoya girerse tehlikeye girer.

---

## Soru 8 (Task Statement 2.4)

> Takım, kod tabanı için semantik arama yapan bir MCP sunucusu kurdu (`mcp__codesearch__search`). Sunucu dil-farkında sembol çözümleme, çapraz repo arama ve alaka sıralaması yapıyor. Aracın açıklaması: "Searches code." Gözlem: Claude Code neredeyse hiç bu aracı çağırmıyor; kod aramak için hep yerleşik `Grep`'i kullanıyor ve çok-repo sorgularında sonuç bulamıyor.
>
> **En etkili ilk adım nedir?**
>
> **A)** `Grep` aracını `disallowedTools` ile kapat — böylece Claude MCP aracını kullanmak zorunda kalır.
>
> **B)** MCP aracının açıklamasını zenginleştir: yeteneklerini (sembol çözümleme, çapraz repo, alaka sıralaması), ne döndürdüğünü (dosya + satır + sembol türü + skor) ve yerleşik `Grep`'ten ne zaman tercih edilmesi gerektiğini açıkça yaz.
>
> **C)** Sunucuyu `~/.claude.json`'a taşı — user scope sunucular önceliklidir.
>
> **D)** CLAUDE.md'ye "kod aramak için her zaman mcp__codesearch__search kullan" yaz.

### Doğru Cevap: B

**Neden B doğru:** Yerleşik `Grep`'in açıklaması uzun, detaylı ve tanıdık; MCP aracı "Searches code" derse Claude daha zengin görünen yerleşik aracı seçer — MCP aracı aslında daha yetenekli olsa bile. Exam guide Skill: "Enhancing MCP tool descriptions to explain capabilities and outputs in detail, preventing the agent from preferring built-in tools over more capable MCP tools." Domain 2.1'deki açıklama ilkelerinin MCP'ye uygulanması; düşük efor, kök neden.

**Neden A yanlış:** Grep'i kapatmak tek-repo, basit pattern aramalarında da Claude'u ağır MCP aracına mahkûm eder; belirtiyi zorla bastırır, seçim kalitesini iyileştirmez. Ayrıca MCP sunucusu çöktüğünde arama yeteneği tamamen kaybolur.

**Neden C yanlış:** Scope öncelik sırası (local > project > user) aynı *adlı* sunucu çakışmalarında geçerlidir; araç *seçimini* etkilemez. Sunucunun nerede tanımlı olduğu Claude'un hangi aracı tercih ettiğiyle ilgisizdir.

**Neden D yanlış:** CLAUDE.md talimatı olasılıksal ve "her zaman" ifadesi basit aramalarda da MCP'yi zorlar. Kök neden açıklamanın zayıflığı; önce onu düzelt. (Açıklama düzeltildikten sonra CLAUDE.md'ye "çok-repo aramalarda codesearch tercih et" gibi bir ipucu ek olarak düşünülebilir — ilk adım değil.)

---

## Soru 9 (Task Statement 2.5)

> Bir geliştirici büyük bir kod tabanında çalışıyor. Şu görevleri tamamlaması gerekiyor:
>
> 1. `fetchUserData` fonksiyonunu çağıran tüm dosyaları bulmak
> 2. Projedeki tüm `.config.yml` dosyalarını bulmak
> 3. Bulunan dosyalarda değişiklik yaptıktan sonra test paketini çalıştırmak
>
> **Her görev için doğru araç hangisidir?**
>
> **A)** 1: Grep, 2: Grep, 3: Grep — Grep her türlü aramayı yapar; testler için çıktıyı Grep'le kontrol et.
>
> **B)** 1: Glob (`**/*fetchUserData*`), 2: Grep (`.config.yml` pattern), 3: Bash.
>
> **C)** 1: Grep (`fetchUserData` — dosya içeriklerinde arar), 2: Glob (`**/*.config.yml` — dosya yollarında eşleştirir), 3: Bash (`npm test`).
>
> **D)** 1: Read (tüm dosyaları oku, filtrele), 2: Glob, 3: Edit.

### Doğru Cevap: C

**Neden C doğru:** Her araç kendi güçlü olduğu alanda: Grep içerik araması (fonksiyon çağrıları dosya *içinde*), Glob yol eşleştirmesi (uzantı dosya *adında*), Bash komut çalıştırma (test paketi — yerleşik bir aracın yapamadığı tek iş).

**Neden A yanlış:** Grep dosya içeriklerinde arar — `.config.yml` dosyalarını bulmak yol eşleştirmesi gerektirir (Glob). Ve Grep komut çalıştıramaz; test için Bash şart.

**Neden B yanlış:** 1 ve 2 ters eşlenmiş. Glob dosya yollarında arar — `fetchUserData` dosya adında geçmiyorsa hiçbir sonuç döndürmez. Fonksiyon çağrıları dosya içeriğindedir: Grep. Bash kısmı doğru.

**Neden D yanlış:** Tüm dosyaları Read ile okumak context bütçesi katili; Grep bu işi tek seferde yapar. Edit dosya değiştirir, test çalıştırmaz — 3 için Bash gerekir.

---

## Soru 10 (Task Statement 2.5)

> Claude Code'da `config.ts` dosyasında `timeout: 30` satırını `timeout: 60` yapmak istiyorsun. Edit aracı şu hatayı veriyor: "old_string `timeout: 30` dosyada 4 yerde geçiyor — eşleşme benzersiz değil." Dördü de farklı servis bloklarında ve yalnızca `paymentService` bloğundakini değiştirmek istiyorsun.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** `replace_all: true` ile Edit'i tekrar çalıştır — dört satır da güncellenir.
>
> **B)** `old_string`'i çevresindeki satırlarla genişlet (`paymentService: {\n  retries: 3,\n  timeout: 30`) ki yalnızca o bloğa eşleşsin; bu da olmazsa dosyayı Read ile yükleyip değiştirilmiş hâlini Write ile yaz.
>
> **C)** Bash ile `sed -i 's/timeout: 30/timeout: 60/' config.ts` çalıştır.
>
> **D)** Dosyayı Write ile sıfırdan yaz — Read'e gerek yok, içerik zaten belli.

### Doğru Cevap: B

**Neden B doğru:** Edit'in benzersizlik hatasında ilk adım en ucuz olanı: `old_string`'e bağlam ekleyip tek bir yerle eşleştirmek. Bu işe yaramazsa exam guide'ın saydığı yedek plan devreye girer: "When Edit fails due to non-unique text matches, using Read + Write as a fallback." Read → Write sırası zorunlu — Claude Code okunmamış mevcut dosyaya Write'ı reddeder.

**Neden A yanlış:** `replace_all` dört satırı da değiştirir; senaryo yalnızca `paymentService` bloğunu istiyor. `replace_all` "hepsini değiştirmek istiyorsan" içindir (değişken yeniden adlandırma gibi), seçici düzenleme için değil.

**Neden C yanlış:** `sed` de dört satırı birden değiştirir (aynı seçicilik sorunu) ve Edit'in benzersizlik güvencesi ile okunabilir diff'ini atar; izin de `Bash` seviyesinde kalır. Yerleşik araç varken Bash'e kaçmak yanlış.

**Neden D yanlış:** Write tüm dosyayı ezer; Read yapılmadan Claude Code mevcut dosyaya yazmayı reddeder ve Claude görmediği içeriği kaybedebilir. "İçerik zaten belli" varsayımı, dosyanın son hâlini bilmeden yapılan tehlikeli bir varsayımdır.

---

## Soru → Task Statement Eşleme Tablosu

| Soru | Task Statement | Test edilen kavram |
|---|---|---|
| 1 | 2.1 | Misrouting — açıklama genişletme + yeniden adlandırma, ilk adım ilkesi |
| 2 | 2.1 | Araç bölme ölçütü — farklı amaç + farklı çıktı sözleşmesi |
| 3 | 2.2 | Business hatası — `isRetryable: false`, `customerMessage`, retry yok |
| 4 | 2.2 | Protokol hatası vs `isError`; erişim hatası vs geçerli boş sonuç |
| 5 | 2.3 | Araç aşırı yüklemesi; forced `tool_choice` → sonraki turda `auto` |
| 6 | 2.3 | `any` ile garantili yapılandırılmış çıktı; `disable_parallel_tool_use` |
| 7 | 2.4 | `.mcp.json` + `${VAR}` — kimlik bilgilerini repo dışında tutma; scope ayrımı |
| 8 | 2.4 | MCP araç açıklamasını zenginleştirme — yerleşik araç tercihi sorunu |
| 9 | 2.5 | Grep (içerik) vs Glob (yol) vs Bash (komut) |
| 10 | 2.5 | Edit benzersizlik hatası → bağlam genişlet → Read + Write; `replace_all` ne zaman |
