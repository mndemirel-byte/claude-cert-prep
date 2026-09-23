EXTRA = {
1: [
{"ts":"Task Statement 1.4","body":"""Bir fintech şirketi, iade işlemlerini yürüten bir agent kuruyor. System prompt'ta şu talimat var: *"İade yapmadan önce mutlaka `verify_identity` aracını çağır."* Üretimde yapılan denetimde, 1.200 iadeden 14'ünün kimlik doğrulaması yapılmadan işlendiği görülüyor. Compliance ekibi bu oranın sıfır olmasını istiyor.

**En doğru çözüm hangisidir?**""",
 "opts":{"A":"System prompt'taki talimatı büyük harflerle ve üç kez tekrarlayarak güçlendir.",
         "B":"`issue_refund` aracının kod tarafına, aynı oturumda başarılı bir `verify_identity` çağrısı yoksa isteği reddeden bir prerequisite gate ekle.",
         "C":"Daha güçlü bir model kullan — daha büyük modeller talimatlara daha iyi uyar.",
         "D":"Her iadeden sonra bir denetim agent'ı çalıştırıp kimlik doğrulaması eksik olanları raporla."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Finansal ve compliance riski taşıyan kurallar prompt'la değil, programatik olarak zorlanır. Prompt-based guidance olasılıksaldır — %98,8 uyum bile compliance için yetersizdir. Prerequisite gate, kimlik doğrulaması yapılmamış bir iadeyi fiziksel olarak imkânsız kılar: %100 garanti.

**Neden A yanlış:** Talimatı tekrarlamak yine olasılıksal bir yaklaşımdır. Oran düşebilir ama sıfır garanti edilemez.

**Neden C yanlış:** Model gücü uyum oranını artırabilir ama deterministik garanti vermez. Sınav tuzağı: yüksek riskli senaryoda "daha büyük model" cevabı hiçbir zaman doğru değildir.

**Neden D yanlış:** Sonradan denetim hatayı tespit eder, engellemez. Para çoktan gitmiştir — compliance ekibinin istediği önleme, tespit değil."""},

{"ts":"Task Statement 1.5","body":"""Claude Agent SDK ile kurulan bir DevOps agent'ı, `run_shell` aracıyla komut çalıştırabiliyor. Ekip, üretim veritabanına yönelik `DROP` ve `TRUNCATE` içeren komutların **hiçbir koşulda** çalışmamasını istiyor. Ayrıca `list_pods` aracının döndürdüğü ham JSON'un Claude'a gitmeden önce sadeleştirilmesini (gereksiz metadata'nın atılmasını) istiyorlar.

**Bu iki gereksinim için doğru hook kombinasyonu hangisidir?**""",
 "opts":{"A":"Her ikisi için de system prompt talimatı — hook'lar gereksiz karmaşıklık ekler.",
         "B":"`DROP/TRUNCATE` engeli için PreToolUse hook (tool çağrısını yakalayıp reddet); JSON sadeleştirme için PostToolUse hook (tool sonucunu Claude'a gitmeden önce dönüştür).",
         "C":"Her ikisi için de PostToolUse hook — komut çalıştıktan sonra sonucu kontrol et, tehlikeliyse hata döndür.",
         "D":"`DROP/TRUNCATE` engeli için PostToolUse hook; JSON sadeleştirme için PreToolUse hook."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Hook'ların iki farklı noktası iki farklı işe yarar. Tool çağrısı **çalışmadan önce** yakalamak (PreToolUse) iş kurallarını deterministik olarak zorlar — tehlikeli komut hiç çalışmaz. Tool sonucu **Claude'a gitmeden önce** yakalamak (PostToolUse) veri normalizasyonu ve sadeleştirme içindir.

**Neden A yanlış:** "Hiçbir koşulda" ifadesi deterministik garanti gerektirir. Prompt olasılıksaldır; tek bir hata üretim veritabanını silebilir. Karar kuralı: tek hata para/veri kaybı yaratıyorsa → hook.

**Neden C yanlış:** PostToolUse komut **çalıştıktan sonra** devreye girer — `DROP` çoktan uygulanmıştır. Engelleme için çok geç.

**Neden D yanlış:** Hook noktaları ters eşleştirilmiş. PreToolUse sonucu göremez (henüz yok), PostToolUse çağrıyı engelleyemez (çoktan çalıştı)."""},

{"ts":"Task Statement 1.7","body":"""Bir developer, büyük bir monorepo'da refactoring yapan agent oturumunu dün akşam kapattı. Bu sabah devam etmek istiyor. Gece boyunca hiçbir dosya değişmedi, ancak developer refactoring için iki farklı stratejiyi (adapter pattern vs. doğrudan yeniden yazma) karşılaştırmak ve en iyisini seçmek istiyor.

**En uygun yaklaşım hangisidir?**""",
 "opts":{"A":"Oturumu resume et ve Claude'dan iki stratejiyi sırayla aynı oturumda denemesini iste.",
         "B":"Dünkü oturumu tamamen unut, her strateji için sıfırdan yeni bir oturum başlat ve kod tabanını yeniden keşfettir.",
         "C":"Dünkü oturumdan `fork_session` ile iki bağımsız dal oluştur — her dalda bir strateji dene, sonuçları karşılaştır.",
         "D":"Fresh start with summary injection yap — dünkü bulguların özetini yeni oturuma enjekte et ve tek stratejiyle ilerle."},
 "ans":"C",
 "expl":"""**Neden C doğru:** Bağlam geçerli (dosyalar değişmedi) ve amaç **aynı temelden farklı yaklaşımları karşılaştırmak**. Bu tam olarak `fork_session`'ın kullanım alanıdır: paylaşılan keşif bağlamı korunur, her dal bağımsız ilerler, birbirini kirletmez.

**Neden A yanlış:** Aynı oturumda iki stratejiyi sırayla denemek bağlamı kirletir — ikinci deneme, ilkinin kararlarından ve yarım kalan değişikliklerinden etkilenir. Temiz karşılaştırma yapılamaz.

**Neden B yanlış:** Kod tabanını iki kez yeniden keşfettirmek gereksiz maliyet. Dünkü bağlam hâlâ geçerli — atmak için bir sebep yok.

**Neden D yanlış:** Fresh start, bağlam bayatladığında (dosyalar değiştiğinde) kullanılır. Burada bayatlama yok; ayrıca "tek stratejiyle ilerle" karşılaştırma gereksinimini karşılamıyor."""},

{"ts":"Task Statement 1.3","body":"""Bir hukuki araştırma sisteminde coordinator, üç araştırma subagent'ının bulgularını bir yazım subagent'ına aktarıyor. Coordinator, aktarım için üç subagent'ın tüm konuşma geçmişini (toplam ~140K token) olduğu gibi yazım subagent'ının prompt'una ekliyor. Yazım subagent'ı sık sık önemli bulguları atlıyor ve bazen araştırma subagent'larının ara notlarını nihai bulgu sanıyor.

**Kök neden ve çözüm nedir?**""",
 "opts":{"A":"Yazım subagent'ının modeli yetersiz — daha büyük context window'lu bir model kullan.",
         "B":"Context passing hatalı — ham geçmiş yerine her subagent'tan yapılandırılmış, self-contained bir bulgu özeti (bulgu, kaynak, güven düzeyi) iste ve yalnızca bunları aktar.",
         "C":"Araştırma subagent'larını yazım subagent'ıyla aynı oturumda çalıştır ki ortak bir hafızaları olsun.",
         "D":"Yazım subagent'ına \"ara notları yoksay, sadece nihai bulguları kullan\" talimatı ekle."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Subagent'lara ham konuşma geçmişi aktarmak anti-pattern'dır. Yazım subagent'ı 140K token içinde neyin bulgu, neyin ara düşünce olduğunu ayırt edemiyor ve dikkat seyreliyor. Doğru handoff protokolü: her subagent yapılandırılmış, self-contained bir özet üretir (bulgu, kaynak, güven düzeyi), coordinator yalnızca bu özetleri aktarır. Her subagent tam olarak ihtiyaç duyduğu bilgiyi alır — fazlasını değil.

**Neden A yanlış:** Sorun context boyutu değil, aktarılan içeriğin yapısı. Daha büyük window da ara notları bulgu sanmayı çözmez.

**Neden C yanlış:** İzolasyon ilkesini bozar. Subagent'ların ortak hafızası olması bağlam kirliliğini artırır, azaltmaz.

**Neden D yanlış:** Prompt talimatıyla semptomu tedavi etmeye çalışıyor. Ara not ile bulgu arasındaki fark ham metinde açık değil — talimat bunu güvenilir şekilde çözemez."""},

{"ts":"Task Statement 1.2","body":"""Bir e-ticaret şirketi, ürün lansmanı için içerik üreten bir multi-agent sistem kuruyor: (1) pazar araştırması, (2) rakip fiyat analizi, (3) hedef kitle analizi, (4) bu üçünün çıktısına dayanan pazarlama metni yazımı. Şu an dört adım sırayla çalışıyor ve toplam süre 11 dakika. Ürün ekibi süreyi kısaltmak istiyor.

**Hangi düzenleme doğrudur?**""",
 "opts":{"A":"Dört adımı da paralel çalıştır — her subagent bağımsızdır.",
         "B":"İlk üç adımı (araştırma, fiyat, kitle) paralel çalıştır; hepsi tamamlanınca dördüncü adımı (metin yazımı) sıralı olarak başlat.",
         "C":"Dört adımı tek bir agent'a birleştir — subagent koordinasyonu gecikme yaratıyor.",
         "D":"Sıralı yapıyı koru ama her subagent'a daha küçük ve hızlı bir model ver."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Paralel/sıralı kararı **veri bağımlılığına** göre verilir. İlk üç adım birbirinden bağımsız — girdileri sadece ürün bilgisi. Dördüncü adım üçünün çıktısına bağımlı. Doğru desen: bağımsız olanlar paralel (fan-out), bağımlı olan sonra (fan-in). Süre yaklaşık en uzun araştırma adımı + yazım adımına düşer.

**Neden A yanlış:** Metin yazımı diğer üçünün çıktısını girdi olarak alıyor. Paralel başlarsa elinde veri olmadan yazar — bağımlılık ihlali.

**Neden C yanlış:** Birleştirme odak kaybı ve context şişmesi yaratır; ayrıca paralellik fırsatını tamamen kaldırır — muhtemelen daha da yavaşlar.

**Neden D yanlış:** Küçük model kalite kaybı riski taşır ve yapısal gecikmeyi (gereksiz sıralılık) çözmez. Önce mimariyi düzelt, sonra model seçimine bak."""},

{"ts":"Task Statement 1.6","body":"""Bir coordinator, 40 sayfalık bir sözleşmeyi incelemek için görevi **paragraf başına bir subagent** olacak şekilde ayrıştırıyor (~600 subagent). Sonuç: maliyet beklenenin 8 katı, toplam süre uzadı ve nihai raporda paragraflar arası çelişkiler (örneğin 3. bölümdeki tanımla 27. bölümdeki kullanım tutarsızlığı) hiç yakalanmıyor.

**Sorunun kaynağı nedir?**""",
 "opts":{"A":"Subagent sayısı çok fazla; koordinasyon ek yükü ve aşırı ince ayrıştırma bağlamı parçalıyor — ayrıştırmayı anlamlı birimlere (bölüm/madde) çek ve çapraz referans için ayrı bir bütünleştirme geçişi ekle.",
         "B":"Subagent'lar yeterince güçlü model kullanmıyor.",
         "C":"Coordinator'ın aggregate adımı yok — subagent çıktılarını birleştirecek bir özet subagent'ı ekle, ayrıştırma düzeyi doğru.",
         "D":"Sözleşme incelemesi ayrıştırmaya uygun değil — tek bir agent'a tüm dokümanı ver."},
 "ans":"A",
 "expl":"""**Neden A doğru:** Ayrıştırma granülerliği bir denge sorunudur. Çok kaba → tek agent boğulur; çok ince → koordinasyon maliyeti patlar ve **birimler arası ilişkiler kaybolur**. Paragraf, sözleşme için anlamlı bir birim değil; madde/bölüm anlamlıdır. Çapraz tutarlılık (3. bölüm ↔ 27. bölüm) ise hiçbir tekil subagent'ın göremeyeceği bir şey — bunun için ayrı bir bütünleştirme geçişi gerekir.

**Neden B yanlış:** Sorun model gücü değil, yapısal. Her subagent kendi paragrafını muhtemelen iyi inceliyor; kimse paragraflar arasına bakmıyor.

**Neden C yanlış:** Aggregate adımı gerekli ama "ayrıştırma düzeyi doğru" iddiası yanlış — 600 subagent maliyet ve süre sorununun doğrudan kaynağı. Sadece özet eklemek maliyeti çözmez.

**Neden D yanlış:** Aşırı tepki. 40 sayfa tek bağlamda dikkat seyrelmesi yaratır; sorun ayrıştırmanın kendisi değil, granülerliği."""},
],
2: [
{"ts":"Task Statement 2.2","body":"""Bir sipariş yönetim agent'ının `create_shipment` aracı hata durumunda şu yanıtı döndürüyor:

```json
{ "error": "Request failed" }
```

Agent, stok yetersizliği (kalıcı iş kuralı hatası) ile kargo API'sinin geçici zaman aşımı (transient) durumlarında aynı şekilde davranıyor: her ikisinde de 5 kez retry edip vazgeçiyor.

**Hata yanıtı nasıl yeniden tasarlanmalı?**""",
 "opts":{"A":"Hata mesajını daha uzun ve açıklayıcı bir doğal dil metnine çevir — agent metni okuyup karar versin.",
         "B":"Yapılandırılmış alanlar ekle: makine-okunabilir hata kodu, `isRetryable` bayrağı ve agent'a bir sonraki adımı söyleyen `suggestion` alanı (örn. \"stok yetersiz — müşteriye alternatif ürün öner\").",
         "C":"Tüm hataları exception olarak fırlat ve agentic loop'u sonlandır — hataları insan çözsün.",
         "D":"Retry sayısını 5'ten 2'ye düşür — böylece kalıcı hatalarda daha az zaman kaybedilir."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Yapılandırılmış hata yanıtı üç şey sağlar: (1) hata kodu ile tür ayrımı, (2) `isRetryable` ile retry kararının deterministik hale gelmesi — transient ise tekrar dene, iş kuralı hatasıysa deneme, (3) `suggestion` ile agent'ın sonraki adımı tahmin etmek yerine bilmesi. Agent bu alanlara göre doğru yolu seçer.

**Neden A yanlış:** Doğal dil hata mesajını parse ettirmek olasılıksaldır — "timeout" kelimesi geçiyor mu diye bakmak güvenilmez ve model değişince kırılır.

**Neden C yanlış:** Transient hatalar agent'ın kendi başına çözebileceği durumlardır; her seferinde insana eskalasyon otomasyonu anlamsızlaştırır.

**Neden D yanlış:** Retry sayısını değiştirmek kök nedeni (hata türlerinin ayırt edilememesi) çözmez. Transient hatalar 2 denemede çözülmeyebilir, kalıcı hatalar 2 denemede de gereksizdir."""},

{"ts":"Task Statement 2.3","body":"""Bir form doldurma agent'ında ilk adım her zaman `extract_fields` aracıyla belgeden alanların çıkarılması olmalı. Ancak agent, `tool_choice: "auto"` ile çalışırken bazen araç çağırmadan doğrudan metin yanıtı üretiyor ("Bu belge bir fatura gibi görünüyor...") ve akış bozuluyor.

**Doğru düzeltme hangisidir?**""",
 "opts":{"A":"System prompt'a \"her zaman önce extract_fields çağır\" talimatı ekle.",
         "B":"İlk çağrıda `tool_choice: {\"type\": \"tool\", \"name\": \"extract_fields\"}` kullan, sonraki turlarda `\"auto\"`'ya dön.",
         "C":"`tool_choice: \"any\"` kullan — agent mutlaka bir araç çağırır.",
         "D":"Diğer tüm araçları kaldır — tek araç kaldığında Claude onu çağırmak zorunda kalır."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Belirli bir aracın zorunlu ilk adım olması gereken durumda `tool_choice` ile o aracı isimle zorlarsın — deterministik. Sonraki turlarda `"auto"`'ya dönerek modelin kalan akışta kendi kararını vermesine izin verirsin.

**Neden A yanlış:** Prompt talimatı olasılıksal; "bazen" araç çağırmama sorunu tam olarak bunun yetersizliğinden kaynaklanıyor.

**Neden C yanlış:** `"any"` bir araç çağrısını garanti eder ama **hangisini** garanti etmez — agent `validate_form` ya da başka bir aracı seçebilir. Belirli araç için isimli zorlama gerekir.

**Neden D yanlış:** Araçları kaldırmak, akışın geri kalanında (doğrulama, gönderme) ihtiyaç duyulan yetenekleri de kaldırır. Yan etkisi büyük, çözüm değil."""},

{"ts":"Task Statement 2.4","body":"""Bir takım, projeye GitHub MCP sunucusu ekliyor. Config dosyasına şu satır yazıldı ve repo'ya commit edildi:

```json
{ "mcpServers": { "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_TOKEN": "ghp_AbC123..." } } } }
```

Güvenlik ekibi tokenin repo'da açık olmasına itiraz ediyor. Ancak takım, sunucu konfigürasyonunun tüm ekip üyeleri için ortak ve versiyon kontrolünde olmasını istiyor.

**Doğru düzenleme hangisidir?**""",
 "opts":{"A":"Konfigürasyonu her geliştiricinin kendi `~/.claude.json` dosyasına taşı — repo'da hiçbir MCP config olmasın.",
         "B":"Proje seviyesi `.mcp.json` dosyasında sunucuyu tanımla, token değerini `\"GITHUB_TOKEN\": \"${GITHUB_TOKEN}\"` ortam değişkeni sözdizimiyle referansla; her geliştirici tokeni kendi ortamında tanımlasın.",
         "C":"Tokeni base64 ile kodlayıp öyle commit et.",
         "D":"Repo'yu private yap — private repo'da token açık olabilir."},
 "ans":"B",
 "expl":"""**Neden B doğru:** `.mcp.json` proje seviyesidir — versiyon kontrolünde, takımla paylaşılır; sunucu tanımı burada durur. Kimlik bilgileri ise `${GITHUB_TOKEN}` ortam değişkeni sözdizimiyle referanslanır, böylece token repo dışında kalır. İki gereksinim (paylaşılan config + gizli kimlik bilgisi) aynı anda karşılanır.

**Neden A yanlış:** `~/.claude.json` kullanıcı seviyesidir — paylaşılmaz. Takımın "ortak ve versiyon kontrolünde" gereksinimini ihlal eder; her geliştirici aynı config'i elle kurmak zorunda kalır.

**Neden C yanlış:** Base64 şifreleme değil, kodlamadır — tek komutla geri çevrilir. Güvenlik sağlamaz.

**Neden D yanlış:** Private repo'da bile token git geçmişinde kalır, klonlanan her makineye yayılır ve rotasyon zorlaşır. Kimlik bilgileri hiçbir koşulda commit edilmez."""},

{"ts":"Task Statement 2.5","body":"""Claude Code'da çalışan bir developer, kod tabanında `PaymentGateway` sınıfının kullanıldığı **tüm çağrı noktalarını** bulmak ve ardından `config/` altındaki tüm `.yaml` dosyalarını listelemek istiyor. Agent ilk görev için Glob, ikinci görev için Grep kullanıyor ve her iki sonuç da eksik geliyor.

**Doğru araç eşleştirmesi nedir?**""",
 "opts":{"A":"Her iki görev için de Grep — Grep daha kapsamlıdır.",
         "B":"Çağrı noktaları için Grep (dosya içeriğinde `PaymentGateway` pattern'ı ara); YAML listesi için Glob (`config/**/*.yaml` yol pattern'ı ile eşleştir).",
         "C":"Her iki görev için de Glob — Glob daha hızlıdır.",
         "D":"Çağrı noktaları için Glob (`**/*PaymentGateway*`); YAML listesi için Grep (`.yaml` metnini ara)."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Grep dosya **içeriklerinde** metin pattern'ı arar — fonksiyon/sınıf çağrıları, importlar, hata mesajları. Glob dosya **yollarında** isim pattern'ı eşleştirir — uzantıya göre dosya bulma, config dosyaları. Çağrı noktaları içerik sorusu → Grep; YAML listesi yol sorusu → Glob.

**Neden A yanlış:** Grep ile dosya listeleme dolaylı ve gürültülüdür — ".yaml" metni içeriklerde de geçebilir, isimler yakalanmayabilir.

**Neden C yanlış:** Glob dosya içine bakmaz — `PaymentGateway` sınıf adı dosya adında geçmiyorsa (genellikle geçmez) hiçbir çağrı noktası bulunmaz. Senaryodaki eksik sonuçların nedeni tam olarak bu.

**Neden D yanlış:** Senaryodaki hatalı eşleştirmenin kendisi. Ters çevrilmiş kullanım her iki sonucu da eksik bırakır."""},
],
3: [
{"ts":"Task Statement 3.3","body":"""Büyük bir monorepo'da test dosyaları (`*.test.ts`, `*.spec.ts`) 60'tan fazla farklı dizine dağılmış durumda. Takım, yalnızca test dosyaları düzenlenirken yüklenecek özel kurallar (fixture kullanımı, mock standartları) tanımlamak istiyor ve bu kuralların diğer dosyalar üzerinde çalışırken bağlamı şişirmesini istemiyor.

**En uygun mekanizma hangisidir?**""",
 "opts":{"A":"Kök `CLAUDE.md`'ye test kurallarını ekle — her zaman yüklü olsun.",
         "B":"60+ dizinin her birine test kurallarını içeren bir `CLAUDE.md` koy.",
         "C":"`.claude/rules/` altında YAML frontmatter'ında `**/*.test.ts` ve `**/*.spec.ts` glob pattern'ları tanımlanmış bir yol-bazlı kural dosyası oluştur.",
         "D":"Test kurallarını bir skill'e taşı ve geliştiriciler test yazarken skill'i çağırsın."},
 "ans":"C",
 "expl":"""**Neden C doğru:** Yol-bazlı kurallar (`.claude/rules/` + glob pattern) tüm kod tabanında dağınık dosyaları tek tanımla yakalar ve **yalnızca eşleşen dosyalar düzenlenirken** yüklenir. Hem kapsam (60+ dizin) hem token verimliliği gereksinimi karşılanır. Sınav tuzağı: "N dizindeki test dosyalarına kural uygula" → yol-bazlı kural.

**Neden A yanlış:** Kök CLAUDE.md her zaman yüklüdür — test dışı işlerde de bağlamı şişirir. Gereksinimin tam tersi.

**Neden B yanlış:** Dizin seviyesi CLAUDE.md tek dizine uygulanır; 60+ kopya bakım kâbusu ve tutarsızlık kaynağıdır. Ayrıca o dizindeki test olmayan dosyalar için de yüklenir.

**Neden D yanlış:** Skill'ler manuel çağrılır; kuralların otomatik ve garantili uygulanmasını sağlamaz. Geliştirici çağırmayı unutursa kural uygulanmaz."""},

{"ts":"Task Statement 3.5","body":"""Bir developer, Claude Code'dan API hata mesajlarını belirli bir formatta yazmasını istiyor. Kök `CLAUDE.md`'ye üç paragraflık bir açıklama yazdı: *"Hata mesajları kullanıcı dostu olmalı, teknik detay içermemeli, ama geliştiriciye yardımcı olacak bağlam sunmalı..."*. Sonuç: her çalıştırmada format farklı çıkıyor — bazen çok teknik, bazen çok belirsiz.

**En etkili iyileştirme hangisidir?**""",
 "opts":{"A":"Açıklamayı beş paragrafa çıkar ve her kuralı daha ayrıntılı tanımla.",
         "B":"Düzyazı açıklamayı 2-3 somut before/after örneğiyle değiştir: kötü mesaj → iyi mesaj çiftleri.",
         "C":"Her seferinde çıktıyı elle düzelt ve Claude'a düzeltmeyi göster — zamanla öğrenir.",
         "D":"Daha büyük bir model kullan; küçük modeller uzun talimatları takip edemez."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Yinelemeli iyileştirmenin en etkili tekniği somut girdi/çıktı örnekleridir. "Kullanıcı dostu ama bağlam sunmalı" gibi düzyazı tanımlar öznel ve her çalıştırmada farklı yorumlanır. 2-3 before/after örneği hedefi kesinleştirir — model örneklerden düzyazıdan daha iyi genelleme yapar. Sınav tuzağı: "düzyazı tutarsız yorumlanıyor" → cevap somut örnekler.

**Neden A yanlış:** Daha fazla düzyazı, daha fazla yoruma açık ifade demektir. Tutarsızlığın kaynağı açıklamanın kısalığı değil, öznelliği.

**Neden C yanlış:** Claude oturumlar arası öğrenmez; her elle düzeltme tek seferliktir. Kalıcı iyileşme CLAUDE.md'deki tanıma yansımalı.

**Neden D yanlış:** Model boyutu öznel tanımı nesnel hale getirmez. Büyük model de "kullanıcı dostu"yu farklı yorumlar."""},

{"ts":"Task Statement 3.2","body":"""Bir takım, her PR öncesi aynı 6 adımlık kontrol listesini (lint, tip kontrolü, test, changelog güncelleme, güvenlik taraması, PR açıklaması oluşturma) Claude Code'a her seferinde elle yazıyor. Takım üyeleri adımları farklı sırayla ya da eksik yazıyor; sonuçlar tutarsız.

**En doğru çözüm hangisidir?**""",
 "opts":{"A":"6 adımı kök `CLAUDE.md`'ye yaz — her oturumda yüklü olsun.",
         "B":"`.claude/commands/` altında `pr-check.md` gibi bir özel slash komutu oluştur; 6 adımı tek bir yeniden kullanılabilir komutta tanımla ve repo'ya commit et.",
         "C":"Her geliştirici kendi kısayolunu `~/.claude/` altında tanımlasın.",
         "D":"Adımları bir CI pipeline'a taşı ve Claude Code'u devreden çıkar."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Tekrarlanan, çok adımlı bir iş akışı için özel slash komutu tam çözümdür: adımlar bir kez tanımlanır, `/pr-check` ile tutarlı biçimde çalışır, repo'ya commit edildiği için tüm takım aynı sürümü kullanır.

**Neden A yanlış:** CLAUDE.md sürekli geçerli **kurallar** içindir; bir iş akışı prosedürünü oraya yazmak her oturumda gereksiz token yükler ve "şimdi çalıştır" tetikleyicisi olmaz.

**Neden C yanlış:** Kişisel kısayollar paylaşılmaz — takım içi tutarsızlık sorunu aynen sürer.

**Neden D yanlış:** Bazı adımlar (PR açıklaması oluşturma, changelog yazımı) CI'da mekanik olarak yapılamaz. Ayrıca soru Claude Code iş akışını iyileştirmeyi soruyor, kaldırmayı değil."""},

{"ts":"Task Statement 3.6","body":"""Bir ekip, her PR'da Claude Code'un otomatik kod incelemesi yapmasını GitHub Actions'a ekledi. İki hafta sonra: inceleme adımı bazı PR'larda 25 dakika sürüyor, bazen agent PR'ı doğrudan `main`'e merge etmeye çalışıyor ve API maliyeti öngörülenin 4 katı.

**Hangi düzenleme seti bu üç sorunu doğru adresler?**""",
 "opts":{"A":"İnceleme adımını kaldır ve haftada bir manuel çalıştır.",
         "B":"Agent'ın izinlerini yalnızca okuma + yorum yazma ile sınırla (merge/push yetkisi yok), inceleme kapsamını yalnızca PR diff'iyle sınırla ve çalışmaya zaman/turn limiti koy.",
         "C":"Agent'a system prompt'ta \"asla merge yapma ve 5 dakikada bitir\" talimatı ver.",
         "D":"Daha küçük bir model kullan — hem hızlanır hem ucuzlar."},
 "ans":"B",
 "expl":"""**Neden B doğru:** CI/CD'de agent otonom çalışır, insan gözetimi yoktur — bu yüzden sınırlar **yapılandırmayla** konur: (1) izinler en dar kapsama çekilir (least privilege: okuma + yorum, merge yok), (2) kapsam diff ile sınırlanır ki agent tüm repo'yu gezip zaman/maliyet harcamasın, (3) turn/zaman limiti hem süreyi hem maliyeti sınırlar.

**Neden A yanlış:** Otomasyonun değerini yok eder; sorun otomasyon değil, sınırsız otomasyon.

**Neden C yanlış:** Prompt talimatı olasılıksaldır — "asla merge yapma" bir izin kısıtı değildir. Merge yetkisi varsa risk vardır. Yüksek riskli aksiyonlar izin katmanında engellenir.

**Neden D yanlış:** Model küçültmek inceleme kalitesini düşürür ve merge denemesi sorununu hiç çözmez. Maliyetin asıl kaynağı sınırsız kapsam."""},
],
4: [
{"ts":"Task Statement 4.5","body":"""Bir şirket, her gece 20.000 müşteri yorumunu sınıflandırmak istiyor; sonuçlar sabah 09:00'daki rapora yetişmeli, ancak dakika hassasiyeti önemli değil. Aynı ekip, kod deposunda her PR'da çalışan senkron bir inceleme adımı da işletiyor. Maliyeti düşürmek isteyen bir mühendis her iki iş yükünü de Batch API'ye taşımayı öneriyor.

**Doğru değerlendirme hangisidir?**""",
 "opts":{"A":"Her ikisini de Batch API'ye taşı — %50 tasarruf her yerde geçerli.",
         "B":"Gece sınıflandırmasını Batch API'ye taşı (gecikmeye toleranslı, %50 maliyet avantajı, 24 saat içinde tamamlanır); PR incelemesini senkron bırak (bloklayıcı iş akışı, batch'in SLA'sı yok).",
         "C":"Hiçbirini taşıma — Batch API üretim iş yükleri için güvenilir değil.",
         "D":"PR incelemesini Batch API'ye taşı (kod incelemesi uzun sürer), gece sınıflandırmasını senkron bırak (hacim büyük)."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Batch API kararı gecikme toleransına göre verilir. Gece sınıflandırması: büyük hacim, saatlik tolerans, kesin bitiş süresi yok → batch ideal (%50 tasarruf, 24 saate kadar işlem). PR incelemesi: geliştirici sonucu bekliyor, merge bloklanıyor → senkron zorunlu; batch'te SLA yoktur, PR saatlerce bekleyebilir.

**Neden A yanlış:** Bloklayıcı iş akışları (CI/CD, pre-merge) her zaman senkron. Batch'in SLA olmaması PR akışını kırar.

**Neden C yanlış:** Batch API tam da gecikmeye toleranslı büyük hacimli üretim iş yükleri için tasarlanmıştır.

**Neden D yanlış:** Eşleştirme ters. Hacim büyüklüğü senkron gerektirmez; gecikme toleransı belirleyicidir."""},

{"ts":"Task Statement 4.6","body":"""Bir kod inceleme sisteminde tek bir Claude oturumu 35 dosyalık bir PR'ı inceleyip ardından kendi bulgularını "tekrar gözden geçir" talimatıyla self-review yapıyor. Buna rağmen dosyalar arası veri akışı hataları (bir dosyada değişen dönüş tipinin başka bir dosyada kırdığı çağrı) sürekli kaçıyor.

**En etkili mimari değişiklik hangisidir?**""",
 "opts":{"A":"Self-review adımını 3 kez tekrarla — her turda yeni sorunlar yakalanır.",
         "B":"Dosya başına bağımsız inceleme instance'ları çalıştır (dikkat seyrelmesini önlemek için), ardından bulguları girdi olarak alan ayrı bir çapraz dosya bütünleştirme geçişi ekle; bulgu üreten instance'lar birbirinin bağlamını taşımasın.",
         "C":"35 dosyayı tek prompt'ta göndermek yerine daha büyük context window'lu bir model kullan.",
         "D":"İnceleme prompt'una \"dosyalar arası tip uyumsuzluklarına özellikle dikkat et\" cümlesi ekle."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Self-review sınırlıdır — aynı oturum aynı kör noktaları taşır. Çözüm iki katmanlı: (1) dosya başına bağımsız instance → her dosya tam dikkat alır, önceki bağlam kirliliği yok; (2) ayrı bir çapraz dosya bütünleştirme geçişi → veri akışı ve çelişki sorunları tam olarak burada yakalanır, çünkü bu geçişin girdisi tüm dosyaların bulgularıdır.

**Neden A yanlış:** Aynı oturumu tekrar tekrar döndürmek aynı kör noktaları tekrarlar. Kaçırılan şey bağlam yapısından kaynaklanıyor, çaba eksikliğinden değil.

**Neden C yanlış:** Sorun context'in sığmaması değil; 35 dosya tek bağlamda dikkat seyrelmesi yaratıyor. Daha büyük window seyrelmeyi çözmez.

**Neden D yanlış:** Prompt vurgusu yardımcı olabilir ama mimari sorunu (tek oturum, seyrelen dikkat, çapraz geçişin olmaması) çözmez."""},
],
5: []
}

# scenario tags for the base project questions: (domain, question no) -> scenario
BASE_SC = {
 (1,1):1,(1,2):3,(1,3):1,(1,4):3,(1,5):1,(1,6):1,(1,7):3,(1,8):5,(1,9):4,(1,10):4,
 (2,1):1,(2,2):3,(2,3):1,(2,4):3,(2,5):3,(2,6):4,(2,7):4,
 (3,1):2,(3,2):2,(3,3):2,(3,4):2,(3,5):2,(3,6):2,(3,7):2,(3,8):5,
 (4,1):5,(4,2):5,(4,3):6,(4,4):5,(4,5):6,(4,6):6,(4,7):6,(4,8):5,(4,9):5,(4,10):6,
 (5,1):1,(5,2):3,(5,3):1,(5,4):1,(5,5):3,(5,6):1,(5,7):4,(5,8):6,(5,9):3,(5,10):1,
}
# scenario tags for EXTRA questions, in order per domain
EXTRA_SC = {1:[1,4,2,3,3,3], 2:[1,6,2,4], 3:[2,2,2,5], 4:[5,5], 5:[]}

EXTRA2 = [
# ---- Scenario 4: Developer Productivity ----
{"d":2,"sc":4,"ts":"Task Statement 2.4","body":"""Bir geliştirici üretkenlik agent'ı, takımın Jira'sındaki açık işleri anlamak için her oturumda 15–20 keşif amaçlı araç çağrısı yapıyor (`list_projects`, sonra her proje için `list_issues`, sonra her issue için `get_issue`). Bu, oturumun ilk dakikalarını ve context bütçesinin önemli bir kısmını tüketiyor.

**En uygun çözüm hangisidir?**""",
 "opts":{"A":"Agent'a \"önce sadece en önemli 5 issue'ya bak\" talimatı ver.",
         "B":"MCP sunucusunda issue özetlerini bir **MCP resource** (içerik kataloğu) olarak sun — agent mevcut verinin haritasını tek seferde görsün, keşif çağrılarına gerek kalmasın.",
         "C":"Üç aracı tek bir `get_everything` aracında birleştir.",
         "D":"Keşif çağrılarının sonuçlarını dosyaya yazıp sonraki oturumlarda yeniden kullan."},
 "ans":"B",
 "expl":"""**Neden B doğru:** MCP resource'ları tam olarak bunun için var: içerik kataloglarını (issue özetleri, doküman hiyerarşileri, veritabanı şemaları) agent'a **keşif araç çağrısı yapmadan** görünür kılar. Araçlar aksiyon içindir, kaynaklar görünürlük içindir.

**Neden A yanlış:** Talimat keşif maliyetini azaltmaz — agent hangi 5 issue'nun önemli olduğunu bilmek için yine listeleme yapmak zorunda.

**Neden C yanlış:** Tek dev araç, tek çağrıda muazzam veri döndürür; context'i keşif çağrılarından daha fazla şişirir ve araç odağını bozar.

**Neden D yanlış:** Önbellek bayatlar (issue'lar değişir) ve sorunun doğasını değiştirmez — hâlâ araçla keşif yapılıyor, sadece ertelenmiş."""},

{"d":2,"sc":4,"ts":"Task Statement 2.4","body":"""Takım, semantik kod araması yapabilen güçlü bir MCP sunucusu (`code_search`: sembol tanımlarını, çağrı grafiğini ve tip bilgisini döndürür) yapılandırdı. Ancak loglara göre agent hemen her seferinde yerleşik Grep aracını tercih ediyor ve MCP aracını neredeyse hiç çağırmıyor. MCP aracının açıklaması: *"Kod araması yapar."*

**En etkili ilk adım hangisidir?**""",
 "opts":{"A":"Grep'i agent'ın araç setinden kaldır — böylece MCP aracını kullanmak zorunda kalır.",
         "B":"MCP aracının açıklamasını zenginleştir: ne döndürdüğünü (sembol tanımı, çağrı grafiği, tip bilgisi), hangi sorgular için Grep'ten üstün olduğunu ve örnek kullanımları açıkla.",
         "C":"System prompt'a \"her zaman code_search kullan, Grep kullanma\" yaz.",
         "D":"MCP sunucusunu kaldır — yerleşik araçlar yeterli."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Araç seçimi açıklamalara dayanır. \"Kod araması yapar\" açıklamasıyla agent, MCP aracının Grep'ten farkını göremez ve tanıdık olanı seçer. Yetenekleri ve çıktıları ayrıntılı anlatan bir açıklama, agent'ın daha yetenekli aracı **kendi kararıyla** tercih etmesini sağlar. Düşük efor, yüksek etki.

**Neden A yanlış:** Grep'in geçerli kullanım alanları var (hata mesajı arama, basit pattern). Kaldırmak yetenek kaybettirir; kök neden (zayıf açıklama) çözülmez.

**Neden C yanlış:** Katı prompt talimatı, Grep'in daha uygun olduğu durumlarda da MCP aracını zorlar; ayrıca olasılıksaldır. Açıklama düzeltilmeden talimat semptomu örtbas eder.

**Neden D yanlış:** Sorun MCP aracının gereksizliği değil, keşfedilememesi."""},

{"d":2,"sc":4,"ts":"Task Statement 2.5","body":"""Agent, bir dosyadaki `return null;` satırını `return defaultConfig;` ile değiştirmek için Edit aracını kullanıyor. Araç hata döndürüyor: dosyada `return null;` ifadesi 7 farklı yerde geçiyor ve hangisinin değiştirileceği belirsiz.

**Doğru yaklaşım hangisidir?**""",
 "opts":{"A":"Edit'i 7 kez çağır — hepsini değiştir.",
         "B":"Edit'e daha geniş, benzersiz bir bağlam ver (örn. fonksiyon imzasıyla birlikte önceki satırları da dahil et); bu da başarısız olursa Read ile tüm dosyayı yükle, hedeflenen değişikliği yap ve Write ile tamamını geri yaz.",
         "C":"Bash ile `sed` çalıştırıp ilk eşleşmeyi değiştir.",
         "D":"Dosyayı silip sıfırdan yeniden üret."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Edit benzersiz metin eşleşmesi gerektirir. İlk adım eşleşmeyi benzersiz hale getirecek kadar bağlam eklemek; bu mümkün değilse resmi yedek plan **Read + Write**: tam dosyayı yükle, değişikliği yap, tamamını yaz. Her zaman çalışır, sadece daha maliyetli.

**Neden A yanlış:** Yalnızca bir yerin değişmesi isteniyor; 7 yeri değiştirmek davranışı bozar.

**Neden C yanlış:** \"İlk eşleşme\" doğru yer olmayabilir; ayrıca sed'in kaçış kuralları hata yapmaya açık ve Claude Code'un dosya araçlarının güvenlik/izin katmanını atlar.

**Neden D yanlış:** Orantısız ve riskli — dosyanın geri kalanı yeniden üretimde değişebilir."""},

{"d":2,"sc":4,"ts":"Task Statement 2.5","body":"""Bir agent, 1.200 dosyalık tanımadığı bir kod tabanında \"iade akışının nasıl çalıştığını\" anlamakla görevlendirildi. Mevcut yaklaşım: agent önce tüm dosyaları Read ile okuyor, ardından cevap vermeye çalışıyor. Context çoğunlukla ilk 200 dosyada doluyor ve agent asıl akışa hiç ulaşamıyor.

**Doğru keşif stratejisi hangisidir?**""",
 "opts":{"A":"Daha büyük context window'lu model kullan ve tüm dosyaları okumaya devam et.",
         "B":"Artımlı keşif: Grep ile giriş noktalarını bul (örn. `refund`, `processRefund`), sonra yalnızca ilgili dosyaları Read ile aç ve importları takip ederek akışı izle.",
         "C":"Glob ile tüm `.ts` dosyalarını listele ve alfabetik sırayla oku.",
         "D":"Agent'a \"sadece önemli dosyaları oku\" talimatı ver."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Kod tabanı anlayışı **artımlı** inşa edilir: Grep ile giriş noktalarını bul, Read ile importları izleyerek akışı takip et. Yalnızca ilgili dosyalar context'e girer; 1.200 dosyanın belki 15'i okunur.

**Neden A yanlış:** 1.200 dosya hiçbir context'e sığmaz; sığsa bile dikkat seyrelmesi yaşanır. Yaklaşım yapısal olarak yanlış.

**Neden C yanlış:** Glob yol pattern'ı eşleştirir, içeriğe bakmaz; alfabetik okuma ilgililikle ilgisizdir.

**Neden D yanlış:** Agent neyin önemli olduğunu içeriğe bakmadan bilemez — talimat somut bir yöntem sunmuyor."""},

{"d":3,"sc":4,"ts":"Task Statement 3.4","body":"""Bir developer, çok fazlı bir görev üzerinde çalışıyor: önce büyük bir legacy modülü keşfedip anlamak, sonra bir dizi değişiklik uygulamak. Keşif aşaması onlarca dosya okuması ve uzun Grep çıktıları üretiyor; uygulama aşamasına gelindiğinde ana konuşmanın context'i keşif gürültüsüyle dolmuş oluyor ve Claude Code uygulamada tutarsızlaşıyor.

**En uygun yaklaşım hangisidir?**""",
 "opts":{"A":"Keşif aşamasını bir **Explore subagent**'a delege et — ayrıntılı okuma/arama çıktısı subagent'ın context'inde kalsın, ana konuşmaya yalnızca yapılandırılmış özet dönsün; ardından uygulama aşamasını temiz context'te yürüt.",
         "B":"Keşif ve uygulamayı aynı oturumda sürdür ama her 10 dosyada bir `/compact` çalıştır.",
         "C":"Keşif aşamasını atla — doğrudan uygulamaya geç, gerektikçe dosya oku.",
         "D":"Her dosya için ayrı oturum aç."},
 "ans":"A",
 "expl":"""**Neden A doğru:** Explore subagent tam olarak bu senaryo için var: gürültülü keşif çıktısını izole eder, ana konuşmaya özet döner, çok fazlı görevlerde context tükenmesini önler. Plan mode/keşif için subagent + uygulama için temiz context iyi bir kombinasyondur.

**Neden B yanlış:** `/compact` yardımcı olabilir ama özetleme sırasında spesifik bulgular (sınıf adları, satır numaraları) kaybolabilir; gürültünün ana context'e hiç girmemesi daha güvenilir.

**Neden C yanlış:** Legacy modülde keşifsiz değişiklik, bağımlılıkların geç fark edilmesi ve maliyetli yeniden iş demektir.

**Neden D yanlış:** Oturumlar arası bağlam kaybı — her oturum sıfırdan keşif yapar."""},

# ---- Scenario 6: Structured Data Extraction ----
{"d":4,"sc":6,"ts":"Task Statement 4.3","body":"""Bir sözleşme çıkarım şemasında `termination_date` alanı `required` olarak tanımlı. Denetimde, bitiş tarihi içermeyen belirsiz süreli sözleşmelerde modelin makul görünen ama uydurma tarihler ürettiği görüldü. JSON her zaman şemaya uygun.

**Kök neden ve düzeltme nedir?**""",
 "opts":{"A":"Model halüsinasyon yapıyor — daha büyük model kullan.",
         "B":"Alan `required` olduğu için model şemayı tatmin etmek amacıyla değer uyduruyor; alanı **nullable/optional** yap ve prompt'ta \"belgede yoksa null döndür\" kuralını belirt.",
         "C":"Retry döngüsü ekle — uydurma tarihler ikinci denemede düzelir.",
         "D":"`termination_date` alanını şemadan tamamen kaldır."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Şemada zorunlu tanımlanan bir alan, kaynak belgede bilgi yoksa modeli uydurmaya iter. Bilgi belgede bulunmayabiliyorsa alan **nullable** tasarlanır; null döndürmek geçerli bir çıktı olur ve halüsinasyon ortadan kalkar.

**Neden A yanlış:** Sorun model kapasitesi değil, şema tasarımının modeli zorlaması. Büyük model de zorunlu alanı doldurmaya çalışır.

**Neden C yanlış:** Retry, bilgi belgede mevcut değilse işe yaramaz — model yine uydurur. Retry format hatalarını düzeltir, eksik bilgiyi yaratmaz.

**Neden D yanlış:** Bitiş tarihi olan sözleşmelerde bu değerli bir alan; kaldırmak veri kaybıdır."""},

{"d":4,"sc":6,"ts":"Task Statement 4.3","body":"""Bir fatura çıkarım şemasında `expense_category` alanı şu enum'a sahip: `["travel","software","hardware","office"]`. Üretimde bu dört kategoriye uymayan giderler (eğitim, danışmanlık, hukuk) geldiğinde model bunları rastgele bir kategoriye sıkıştırıyor; muhasebe raporları yanlış çıkıyor.

**Şema nasıl düzeltilmeli?**""",
 "opts":{"A":"Enum'u kaldır, alanı serbest metin yap.",
         "B":"Enum'a `\"other\"` değeri ekle ve yanına `category_detail` (serbest metin) alanı koy; belirsiz durumlar için gerekirse `\"unclear\"` değeri de tanımla.",
         "C":"Her yeni gider türü için enum'u güncelle ve pipeline'ı yeniden deploy et.",
         "D":"Prompt'a \"uymayan giderleri office olarak işaretle\" talimatı ver."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Genişletilebilir kategoriler için standart desen: `"other"` + detay alanı. Model uymayan durumları sıkıştırmak yerine `other` seçer ve detayı serbest metinde verir; muhasebe bu kayıtları ayrıca inceleyebilir. `"unclear"` da belirsiz durumları açıkça işaretler.

**Neden A yanlış:** Enum'un sağladığı tutarlılık (aynı gider için hep aynı etiket) kaybolur; raporlama bozulur.

**Neden C yanlış:** Sürdürülemez — her yeni tür deploy gerektirir ve ilk geldiğinde yine yanlış sınıflanır.

**Neden D yanlış:** Yanlış veriyi kasıtlı üretmek; sorun görünmez hale gelir ama raporlar yine yanlıştır."""},

{"d":4,"sc":6,"ts":"Task Statement 4.4","body":"""Bir çıkarım pipeline'ında Pydantic doğrulaması `invoice_date` alanı için \"expected ISO 8601, got '15/03/2024'\" hatası veriyor. Mevcut retry mantığı aynı prompt'u hiçbir değişiklik yapmadan tekrar gönderiyor; başarı oranı %12.

**Retry nasıl tasarlanmalı?**""",
 "opts":{"A":"Retry sayısını 3'ten 8'e çıkar.",
         "B":"Retry isteğine orijinal belgeyi, başarısız çıkarımı ve **spesifik doğrulama hatasını** ekle (\"invoice_date ISO 8601 olmalı; '15/03/2024' bulundu\") — model hedefli düzeltme yapsın.",
         "C":"Doğrulamayı kaldır — tarih formatı downstream'de düzeltilsin.",
         "D":"Retry'da farklı bir model kullan."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Retry-with-error-feedback: model neyin yanlış olduğunu bilmeden aynı hatayı tekrarlar. Belge + başarısız çıktı + spesifik hata birlikte verildiğinde format hataları yüksek oranda düzelir. Bu bir format hatası — retry'ın tam olarak işe yaradığı sınıf.

**Neden A yanlış:** Aynı girdiyle daha fazla deneme aynı çıktıyı üretir; başarı oranı rastgeleliğe bağlı kalır.

**Neden C yanlış:** Doğrulama sinyalini kaldırmak sorunu downstream'e taşır ve diğer hataları da görünmez kılar.

**Neden D yanlış:** Sorun model değil, geri bildirimsiz retry. Model değiştirmek maliyet ve karmaşıklık ekler."""},

{"d":4,"sc":6,"ts":"Task Statement 4.5","body":"""5.000 belgelik bir Batch API gönderiminde 180 istek başarısız oldu: 140'ı \"context length exceeded\", 40'ı geçici sunucu hatası. Mühendis tüm 5.000 belgeyi aynı haliyle yeniden göndermeyi planlıyor.

**Doğru yaklaşım hangisidir?**""",
 "opts":{"A":"Planı uygula — batch tekrarı ucuzdur.",
         "B":"`custom_id` ile yalnızca 180 başarısız belgeyi ayıkla; context aşan 140'ını parçalara bölerek (chunking), geçici hata alan 40'ını olduğu gibi yeniden gönder.",
         "C":"180 belgeyi senkron API ile tek tek işle — batch güvenilmez.",
         "D":"Context aşan belgeleri pipeline'dan çıkar; sadece 40 geçici hatayı yeniden gönder."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Batch hata yönetiminin kuralı: `custom_id` ile istek-yanıt eşleştir, **yalnızca başarısızları** yeniden gönder ve nedene uygun değişiklikle gönder — boyut aşımı için chunking, geçici hata için aynen tekrar.

**Neden A yanlış:** 4.820 başarılı belgeyi yeniden işlemek gereksiz maliyet ve süre; ayrıca 140 belge değiştirilmeden yine başarısız olur.

**Neden C yanlış:** Batch güvenilmez değil; hatalar açıklanabilir nedenlere sahip. Senkron işleme maliyeti iki katına çıkarır ve context sorununu çözmez.

**Neden D yanlış:** 140 belgeyi atmak veri kaybı; chunking ile işlenebilirler."""},

{"d":5,"sc":6,"ts":"Task Statement 5.5","body":"""Bir çıkarım sistemi, güven skoru %90 üzerindeki alanları insan incelemesi olmadan doğrudan ERP'ye yazıyor. Altı aydır kimse bu \"yüksek güvenli\" çıktıları kontrol etmedi. Yeni bir tedarikçi, faturalarında farklı bir düzen kullanmaya başladı ve hatalar fark edilmeden sisteme aktı.

**Eksik olan mekanizma nedir?**""",
 "opts":{"A":"Güven eşiğini %99'a çıkar.",
         "B":"Yüksek güvenli çıkarımlardan **tabakalı rastgele örnekleme** ile sürekli bir kısmını insan incelemesine yönlendir — hata oranını izle ve yeni hata desenlerini (yeni belge düzeni gibi) erken yakala.",
         "C":"Tüm çıkarımları yeniden %100 insan incelemesine al.",
         "D":"Yeni tedarikçinin faturalarını manuel işle."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Yüksek güven \"denetim gerekmez\" demek değildir. Tabakalı rastgele örnekleme, otomatik yoldaki gerçek hata oranını ölçer ve dağılım kayması (yeni düzen, yeni tedarikçi) gibi **yeni hata desenlerini** görünür kılar. Kalıcı bir izleme mekanizmasıdır.

**Neden A yanlış:** Eşik yükseltmek modelin yanlış-güvenli olduğu durumları yakalamaz; model yeni düzende de %95 güven bildirebilir.

**Neden C yanlış:** Otomasyonun değerini yok eder; orantısız.

**Neden D yanlış:** Bu tedarikçiyi çözer ama bir sonraki değişikliği yine geç fark edersin — sistemik mekanizma yok."""},

# ---- Scenario 5: CI/CD ----
{"d":3,"sc":5,"ts":"Task Statement 3.6","body":"""CI'daki Claude Code incelemesi her yeni commit'te sıfırdan çalışıyor. Geliştiriciler, daha önce yorumlanmış ve hâlâ düzeltilmemiş sorunların her seferinde yeni yorum olarak tekrar eklendiğinden, PR'ların onlarca mükerrer yorumla dolduğundan şikâyet ediyor.

**En doğru düzeltme hangisidir?**""",
 "opts":{"A":"İncelemeyi yalnızca PR ilk açıldığında çalıştır.",
         "B":"Yeniden çalıştırmada önceki inceleme bulgularını context'e ver ve Claude'a yalnızca **yeni veya hâlâ giderilmemiş** sorunları raporlamasını, tekrarları atlamasını söyle.",
         "C":"Her çalıştırmadan önce PR'daki tüm eski yorumları sil.",
         "D":"İncelemeyi sadece son commit'in diff'iyle sınırla."},
 "ans":"B",
 "expl":"""**Neden B doğru:** Önceki bulgular context'e verildiğinde Claude neyin zaten raporlandığını bilir; yalnızca yeni ya da hâlâ açık sorunları bildirir. Mükerrer yorum sorunu kaynağında çözülür, geçmiş korunur.

**Neden A yanlış:** Sonraki commit'ler incelenmez — yeni hatalar kaçar.

**Neden C yanlış:** İnceleme geçmişi ve geliştirici tartışmaları silinir; ayrıca aynı sorunlar yine yeni yorum olarak gelir.

**Neden D yanlış:** Son commit önceki commit'lerdeki açık sorunları içermeyebilir; ayrıca dosyalar arası bağlam kaybolur."""},

{"d":3,"sc":5,"ts":"Task Statement 3.6","body":"""Bir CI adımı `claude -p \"PR'ı incele\"` çıktısını alıp satır satır PR yorumu olarak göndermeye çalışıyor. Çıktı serbest metin olduğu için parse işlemi sık sık kırılıyor: bazen madde işaretleri, bazen tablo, bazen paragraf geliyor; dosya adı ve satır numarası tutarsız konumlarda.

**Doğru çözüm hangisidir?**""",
 "opts":{"A":"Prompt'a \"her bulguyu 'dosya:satır — mesaj' formatında yaz\" talimatı ekle ve regex ile parse et.",
         "B":"`--output-format json` ve `--json-schema` bayraklarıyla çıktıyı bir şemaya (dosya, satır, ciddiyet, mesaj, öneri) zorla; CI adımı yapılandırılmış JSON'u doğrudan inline yorumlara dönüştürsün.",
         "C":"Çıktıyı olduğu gibi tek bir PR yorumu olarak yapıştır.",
         "D":"İncelemeyi interaktif modda çalıştırıp çıktıyı elle kopyala."},
 "ans":"B",
 "expl":"""**Neden B doğru:** CI'da makine-okunabilir çıktı için resmi mekanizma `--output-format json` + `--json-schema`. Şema zorlanır, format sürprizleri ortadan kalkar, inline PR yorumu üretimi deterministik olur.

**Neden A yanlış:** Prompt talimatıyla format istemek olasılıksaldır; regex sürekli kırılır. Şema zorlaması varken bunu kullanmak anti-pattern'dır.

**Neden C yanlış:** Inline, satır bazlı yorum değeri kaybolur; geliştirici hangi satırın kastedildiğini aramak zorunda kalır.

**Neden D yanlış:** CI otomasyondur; interaktif mod pipeline'ı askıya alır (`-p` tam da bu yüzden var)."""},
]
