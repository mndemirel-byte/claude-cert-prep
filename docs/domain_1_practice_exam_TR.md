# Domain 1 — Practice Exam

## Agentic Architecture & Orchestration (Sınavın %27'si)

**Dağılım (16 soru):**
- 4 soru → Agentic loops (1.1): Q1, Q3, Q11, Q12
- 5 soru → Orchestration & context (1.2, 1.3): Q2, Q4, Q7, Q14, Q16
- 3 soru → Enforcement & hooks (1.4, 1.5): Q5, Q6, Q13
- 2 soru → Decomposition (1.6): Q8, Q9
- 2 soru → Session management (1.7): Q10, Q15

**Geçme kriteri:** 13+/16 (~%80)

---

## Question 1 (Task Statement 1.1)

> Bir müşteri destek agent'ı aşağıdaki loop mantığıyla çalışıyor:
>
> ```python
> for i in range(10):
>     response = call_claude(messages)
>     if "final answer" in response.content[0].text.lower():
>         return response
>     # execute tools and continue
> ```
>
> Kullanıcılar üç farklı sorun bildiriyor:
> 1. Agent bazen 10 döngüden sonra yanıt vermeden duruyor
> 2. Agent bazen "Here's my final answer so far, let me search for more details" dediği halde duruyor
> 3. Bazı isteklerde loop `AttributeError: 'ToolUseBlock' object has no attribute 'text'` hatasıyla çöküyor
>
> **Bu üç sorunu da çözen doğru yaklaşım hangisidir?**
>
> **A)** Iteration cap'i 10'dan 25'e çıkar, "final answer" yerine "task complete" ifadesini kontrol et ve `.text` erişimini `try/except` ile sar.
>
> **B)** `response.stop_reason` alanını kontrol et — `"end_turn"` ise çık, `"tool_use"` ise `response.content` listesinin tamamındaki tool_use bloklarını çalıştırıp devam et.
>
> **C)** Her döngüde Claude'a "İşin bitti mi?" diye sor ve cevabını parse et.
>
> **D)** Iteration cap'i kaldır ve sadece `response.content[0].type == "text"` kontrolü yap.

### Correct Answer: B

**Why B is correct:** Kod üç ayrı hata içeriyor: arbitrary iteration cap (10 döngü limiti, sessizce duruyor), natural language parsing ("final answer" ifadesini arama) ve `content[0]` varsayımı (ilk blok bir `tool_use` bloğuysa `.text` yok → çöküyor). `stop_reason` kontrolü ilk iki sorunu çözer; `content` listesinin tamamını dolaşmak üçüncüsünü. Tahmin, parsing ya da ilk-blok varsayımı gerekmez.

**Why A is wrong:** Cap'i yükseltmek, farklı bir string aramak ve hatayı `try/except` ile yutmak üç anti-pattern'ı da devam ettirir. Rakam, string ve hata yönetimi değişse de yapısal sorunlar aynı — özellikle `try/except` çökmeyi gizler ama loop'un hâlâ yanlış karar vermesini engellemez.

**Why C is wrong:** Natural language parsing anti-pattern'ının farklı bir versiyonu. Claude'un "evet bittim" demesi de belirsiz ve güvenilmez; ayrıca her döngüye fazladan bir API çağrısı ekler.

**Why D is wrong:** Content-type check anti-pattern'ı. Claude text ve tool_use bloklarını aynı yanıtta döndürebilir. Text görünce çıkmak erken sonlanmaya neden olur — ve `content[0]` varsayımı yine yerinde duruyor.

---

## Question 2 (Task Statement 1.2)

> Bir multi-agent research sistemi "global food security challenges" hakkında rapor üretiyor. Sistem: coordinator, web search subagent, document analysis subagent ve synthesis subagent içeriyor.
>
> Nihai rapor mükemmel yazılmış ama sadece iklim değişikliği ve su kıtlığını kapsıyor. Tedarik zinciri bozulmaları, siyasi istikrarsızlık ve biyoteknoloji tamamen eksik.
>
> Web search subagent bağımsız test edildiğinde "food security supply chain disruption" sorgusuyla mükemmel sonuçlar döndürüyor.
>
> **Kök neden nedir?**
>
> **A)** Web search subagent'ın arama algoritması yetersiz.
>
> **B)** Synthesis subagent bazı konuları filtrelemiş.
>
> **C)** Coordinator'ın task decomposition'ı eksik — sadece iklim ve su konularını subtask olarak oluşturmuş.
>
> **D)** Subagent'lar coordinator'ın tam conversation history'sine erişemiyor.

### Correct Answer: C

**Why C is correct:** Narrow decomposition failure. Subagent'lar bağımsız test edildiğinde mükemmel çalışıyor — sorun onlarda değil. Coordinator "global food security challenges"ı sadece iklim ve su olarak parçalamış. Tedarik zinciri, siyasi istikrarsızlık ve biyoteknoloji hiç subtask olarak oluşturulmamış. Hatayı kaynağına izle — coordinator'ın decomposition'ı.

**Why A is wrong:** Web search subagent bağımsız testte mükemmel sonuç veriyor. Arama yeteneği sorunsuz — kendisine o konular hiç sorulmamış.

**Why B is wrong:** Synthesis subagent sadece aldığı veriyi sentezler. Tedarik zinciri hakkında araştırma yapılmadıysa, filtreleyecek bir şey yok.

**Why D is wrong:** Isolation principle tuzağı. Subagent'lara tam conversation history vermek doğru mimari yaklaşım değil. Çözüm coordinator'ın decomposition'ını genişletmek.

---

## Question 3 (Task Statement 1.1)

> Bir agentic loop'ta Claude şu yanıtı döndürüyor:
>
> - `response.content[0]` → type: "text", text: "I found some relevant data. Let me query the sales database for Q3 numbers."
> - `response.content[1]` → type: "tool_use", name: "query_database", input: {...}
> - `response.stop_reason` → "tool_use"
>
> **Loop ne yapmalı?**
>
> **A)** Text bloğunu kullanıcıya göster ve döngüyü sonlandır — Claude bir metin yanıtı verdi.
>
> **B)** `query_database` tool'unu çalıştır, sonucu `tool_result` bloğu olarak conversation history'ye ekle, Claude'a geri gönder. Text bloğu isteğe bağlı olarak kullanıcıya ara durum mesajı (streaming) şeklinde gösterilebilir.
>
> **C)** Text bloğunu nihai yanıt olarak kullanıcıya sun, conversation history'yi sıfırla ve tool sonucuyla yeni bir konuşma başlat.
>
> **D)** Claude'a "Bu tool çağrısını onaylıyor musun?" diye sor.

### Correct Answer: B

**Why B is correct:** `stop_reason` `"tool_use"` — bu tek önemli sinyal. Claude hem text hem tool_use bloğu döndürmüş ama `stop_reason` açıkça "devam etmem gerekiyor" diyor. Tool'u çalıştır, sonucu `tool_use_id` ile eşleşen bir `tool_result` bloğu olarak mevcut history'ye ekle, Claude'a geri gönder. Text bloğu Claude'un "yüksek sesle düşünmesi" — kullanıcıya ilerleme mesajı olarak göstermek zararsızdır, ama döngü kararı `stop_reason`'a göre verilir.

**Why A is wrong:** Content-type check anti-pattern'ı. Text bloğu var diye döngüyü sonlandırmak erken çıkış. `stop_reason` hâlâ `"tool_use"`.

**Why C is wrong:** İki hata birden: text bloğunu *nihai* yanıt saymak (erken sonlanma) ve history'yi sıfırlamak. Tool sonucu, Claude'un kendi tool_use bloğunu içeren mevcut history'nin devamı olarak gönderilmelidir; history sıfırlanırsa `tool_result`'ın eşleşeceği `tool_use` bloğu ortada kalmaz ve API isteği reddeder.

**Why D is wrong:** Agentic loop'ta Claude kendi kararlarını verir. Her tool çağrısı için Claude'a onay sormak anlamsızdır — insan onayı gerekiyorsa bu `PreToolUse` hook'unda `ask` kararıyla yapılır, loop'ta ek bir Claude çağrısıyla değil.

---

## Question 4 (Task Statement 1.3)

> Bir coordinator, web search subagent'ın bulgularını synthesis subagent'a aktarıyor. Aktarım şu formatta yapılıyor:
>
> ```
> "Solar energy capacity grew 45% in 2024. Wind energy investments
> reached $120B. Geothermal projects expanded in Iceland and Kenya."
> ```
>
> Synthesis subagent iyi bir rapor yazıyor ama hiçbir iddiada kaynak belirtmiyor.
>
> **En etkili çözüm hangisidir?**
>
> **A)** Synthesis subagent'ın system prompt'una "her iddia için kaynak belirt" talimatı ekle.
>
> **B)** Coordinator'ın context passing mekanizmasını structured metadata formatına geçir — her iddiayı kaynak URL, doküman adı ve sayfa numarasıyla eşleştir.
>
> **C)** Web search subagent'a sonuçlarını APA formatında döndürmesini söyle.
>
> **D)** Synthesis subagent'a coordinator'ın tam konuşma geçmişini ver.

### Correct Answer: B

**Why B is correct:** Sorun context passing'te. Coordinator düz metin olarak aktarıyor — synthesis agent hangi iddianın hangi kaynaktan geldiğini bilmiyor. Çözüm: structured metadata formatı — her claim'i source URL, doküman adı ve sayfa numarasıyla eşleştiren JSON yapısı; bu şema web search subagent'ın prompt'una konur ki yapı zincirin başında oluşsun. Synthesis agent bu yapılandırılmış veriyle doğru atıf yapabilir.

**Why A is wrong:** "Kaynak belirt" talimatı olasılıksal ve kök nedeni çözmez. Synthesis agent'a gelen veride kaynak bilgisi yapılandırılmış şekilde yoksa, prompt talimatı eksik veriyi yaratamaz.

**Why C is wrong:** APA formatı sunum formatıdır, veri yapısı değil. Sorun formatın güzelliği değil, metadata'nın içerikten ayrılmamış olması. APA string'i de hâlâ düz metin — structured claim-source eşleştirmesi yapmaz.

**Why D is wrong:** Isolation principle tuzağı. Tam konuşma geçmişi vermek izolasyon ilkesini ihlal eder ve sorunu çözmez.

---

## Question 5 (Task Statement 1.4)

> Bir e-ticaret agent'ı bazen müşterinin sipariş geçmişini doğrulamadan iade işliyor. Bu vakaların %5'inde yanlış siparişe iade yapılıyor ve şirket para kaybediyor.
>
> Mevcut system prompt'ta şu talimat var: "İade işlemeden önce mutlaka müşterinin sipariş geçmişini doğrula."
>
> **Doğru çözüm hangisidir?**
>
> **A)** System prompt'a bu talimatı 3 kez tekrarla ve kalın yazıyla vurgula.
>
> **B)** `process_refund` tool'unun çalışabilmesi için `verify_order_history` tool'unun başarıyla tamamlanmış olmasını şart koşan bir `PreToolUse` hook ekle; reddedildiğinde `permissionDecisionReason` ile "önce verify_order_history çağır" bilgisini Claude'a ilet.
>
> **C)** Few-shot örneklerle doğru sıralamayı göster — 5 farklı senaryo ekle.
>
> **D)** İade tutarını $100 ile sınırla.

### Correct Answer: B

**Why B is correct:** Finansal sonuçları olan bir işlem — yanlış siparişe iade. `PreToolUse` hook, `verify_order_history` başarıyla tamamlanmadan `process_refund` tool'unun çalışmasını fiziksel olarak engeller; kural ihlali sıfıra iner. Red nedeni Claude'a iletildiği için agent doğrulamayı çağırıp iadeyi doğru sırayla tamamlar.

**Why A is wrong:** Prompt tekrarı olasılıksal. Kalın yazı ve tekrarlama başarı oranını artırabilir ama %100 garanti edemez. Zaten mevcut prompt'ta talimat var ve %5 hata veriyor.

**Why C is wrong:** Few-shot örnekler de prompt-based guidance. Modelin davranışını yönlendirir ama zorlamaz. Deterministik değil.

**Why D is wrong:** Tutarı sınırlamak sorunu çözmez — $100 altı iadelerde de yanlış siparişe iade yapılabilir. Ve asıl sorun doğrulama eksikliği, tutar değil.

---

## Question 6 (Task Statement 1.5)

> Bir agent, üç farklı **üçüncü parti** MCP server'ından (kaynak kodlarına erişimin yok) tarih bilgisi alıyor:
> - CRM tool → Unix timestamp (1719849600)
> - Shipping tool → "June 15, 2024"
> - Payment tool → "2024-06-15T00:00:00Z"
>
> Claude bazen tarih karşılaştırmalarında hata yapıyor çünkü formatlar tutarsız.
>
> **Doğru çözüm hangisidir?**
>
> **A)** Claude'un system prompt'una "tüm tarihleri ISO 8601 formatına çevir" talimatı ekle.
>
> **B)** Üç MCP server'ının sağlayıcılarından API'lerini ISO 8601 döndürecek şekilde değiştirmelerini iste.
>
> **C)** `PostToolUse` hook ile tüm tool sonuçlarındaki tarihleri `updatedToolOutput` üzerinden standart bir formata dönüştür, Claude'a göndermeden önce.
>
> **D)** Claude'a tarih formatlarını açıklayan bir referans tablosu ekle.

### Correct Answer: C

**Why C is correct:** `PostToolUse` hook'un tam kullanım amacı bu — farklı tool'lardan gelen heterojen veriyi, Claude'a ulaşmadan önce kodla standart formata dönüştürmek. `updatedToolOutput` tool sonucunun kendisini değiştirir; hook deterministik çalışır, Claude her zaman temiz, tutarlı tarih formatı görür.

**Why A is wrong:** Prompt talimatı olasılıksal. Claude Unix timestamp'i doğru çeviremeyebilir veya farklı formatlarda tutarsız davranabilir. Format dönüşümü kod işi, model işi değil.

**Why B is wrong:** Üçüncü parti sağlayıcıların API'lerini değiştirmesini beklemek kontrolü dış bağımlılığa bırakır — olsa bile zaman alır ve garanti değildir. Normalizasyon senin sınırında yapılmalı. (Not: tool'lar senin kendi MCP server'ın olsaydı kaynakta düzeltmek meşru bir seçenek olurdu — soru bu yüzden "üçüncü parti" diyor.)

**Why D is wrong:** Referans tablosu da prompt-based guidance. Claude'un tabloyu doğru uygulaması garantili değil. Yapısal çözüm gereken yerde bilgi ekleme yaklaşımı.

---

## Question 7 (Task Statement 1.3)

> Bir coordinator aynı anda 3 subagent başlatması gerekiyor: web search, document analysis ve data visualization. Üç subagent birbirinden bağımsız — hiçbiri diğerinin çıktısına ihtiyaç duymuyor. Mevcut implementasyon her birini sırayla başlatıyor — önce web search tamamlanıyor, sonra document analysis, sonra data visualization.
>
> Toplam süre: 45 saniye. Her subagent yaklaşık 15 saniye sürüyor.
>
> **Gecikmeyi azaltmanın doğru yolu hangisidir?**
>
> **A)** Her subagent için daha hızlı bir model kullan.
>
> **B)** Coordinator'ın tek bir yanıtında birden fazla Task tool çağrısı yaparak subagent'ları paralel başlat.
>
> **C)** Subagent'ların birbirleriyle doğrudan iletişim kurmasını sağla — coordinator'ı atla.
>
> **D)** Subagent sayısını 2'ye düşür — data visualization'ı kaldır.

### Correct Answer: B

**Why B is correct:** Parallel spawning. Alt görevler bağımsız olduğu için coordinator tek bir yanıtta birden fazla Task tool çağrısı yaparsa, subagent'lar paralel başlar. 3 subagent × 15 saniye sırayla = 45 saniye. Paralel başlatmayla ≈ 15 saniye. 3 kat hız artışı, hiçbir özellikten feragat etmeden.

**Why A is wrong:** Daha hızlı model her subagent'ı kısaltabilir ama sıralı yapı devam eder. 3 × 10 saniye = 30 saniye hâlâ paralel 15 saniyeden yavaş. Ve model değişikliği kalite kaybı yaratabilir.

**Why C is wrong:** Hub-and-spoke mimarisinin temel kuralını ihlal eder — tüm iletişim coordinator üzerinden akar. Doğrudan iletişim observability, error handling ve kontrol kayıplarına yol açar.

**Why D is wrong:** Fonksiyonalite kaybı. Sorunu çözmek yerine özellik kaldırmak doğru yaklaşım değil.

---

## Question 8 (Task Statement 1.6)

> Bir kod inceleme agent'ı 20 dosyalık bir PR'ı tek geçişte analiz ediyor. Sonuçlar:
>
> - İlk 5 dosyaya detaylı, kaliteli geri bildirim veriyor
> - 15-20 arasındaki dosyalardaki bariz null pointer bug'larını tamamen kaçırıyor
> - `async/await` pattern'ını 4. dosyada "best practice" olarak övüyor ama 18. dosyada aynı pattern'ı "anti-pattern" olarak işaretliyor
>
> **Sorun ve çözüm nedir?**
>
> **A)** Context window yetersiz — daha büyük model kullanılmalı.
>
> **B)** Dosyalar önem sırasına göre sıralanmalı.
>
> **C)** System prompt'a "tüm dosyalara eşit dikkat göster ve tutarlı ol" talimatı eklenmeli.
>
> **D)** Multi-pass mimarisine geçilmeli: per-file local analysis + cross-file integration pass.

### Correct Answer: D

**Why D is correct:** Attention dilution'ın klasik belirtileri — tutarsız derinlik (ilk dosyalara detaylı, son dosyalara yüzeysel) ve çelişkili değerlendirmeler (aynı pattern'a farklı tepki). Multi-pass mimari: önce her dosyayı ayrı ayrı, aynı kriterlerle analiz et (per-file local analysis — paralel çalıştırılabilir), sonra bulgular üzerinde dosyalar arası tutarsızlıkları ve bağımlılıkları kontrol et (cross-file integration pass). Her iki sorunu da çözer.

**Why A is wrong:** Sorun context window boyutu değil, dikkat dağılımı — 20 dosya zaten sığıyor. Daha büyük model de tek geçişte 20 dosyaya aynı kriterleri aynı derinlikte uygulamakta aynı yapısal sorunu yaşar.

**Why B is wrong:** Sıralama değişikliği hangi dosyaların ihmal edildiğini değiştirir ama attention dilution'ı çözmez. Hâlâ tek geçiş, hâlâ dikkat dağılımı.

**Why C is wrong:** Prompt talimatı olasılıksal ve yapısal bir soruna prompt çözümü. "Eşit dikkat göster" demek attention dilution'ı ortadan kaldırmaz — bu mimari bir sorun.

---

## Question 9 (Task Statement 1.6)

> Bir agent "legacy kod tabanına test ekleme" görevi alıyor. Kod tabanı büyük ve karmaşık — bağımlılıklar önceden bilinmiyor, test edilebilirlik dosyadan dosyaya değişiyor.
>
> **Hangi decomposition stratejisi daha uygun?**
>
> **A)** Fixed sequential pipeline — önce tüm dosyaları listele, sonra her birine test yaz, sonra çalıştır.
>
> **B)** Dynamic adaptive decomposition — önce yapıyı haritala, yüksek etkili alanları belirle, bağımlılıklar ortaya çıktıkça planı güncelle; keşif fazına açık bir durma kriteri ve bütçe koy.
>
> **C)** Tüm dosyaları tek geçişte analiz et ve en önemli 5 dosyaya test yaz.
>
> **D)** Rastgele 10 dosya seç ve onlara test yaz.

### Correct Answer: B

**Why B is correct:** Legacy kod tabanı = bilinmeyen bağımlılıklar, değişken test edilebilirlik, keşif gerektiren problem. Bu açık uçlu araştırma görevidir. Dynamic adaptive decomposition her adımda keşfedilen bilgiye göre planı günceller — önce yapıyı haritalarsın, yüksek etkili alanları belirlersin, bağımlılıklar ortaya çıktıkça önceliklendirirsin. Durma kriteri ve bütçe, keşfin sonsuza kadar sürmesini önler.

**Why A is wrong:** Fixed sequential pipeline tahmin edilebilir görevler içindir. Legacy kod tabanında bağımlılıklar önceden bilinmiyor — önceden belirlenmiş sıralı adımlar beklenmedik bulgulara uyum sağlayamaz.

**Why C is wrong:** Tek geçişte tüm dosyalar = attention dilution riski. Ve sadece 5 dosyaya odaklanmak kapsamı keyfi olarak daraltır.

**Why D is wrong:** Rastgele seçim hiçbir stratejik değer taşımaz. Yüksek etkili alanları kaçırma riski çok yüksek.

---

## Question 10 (Task Statement 1.7)

> Bir developer 3 gündür bir kod tabanı üzerinde çalışan agent oturumunu resume ediyor. Arada developer 5 dosyada kapsamlı değişiklikler yapmış — bazı fonksiyonlar silinmiş, yeni modüller eklenmiş, API yapısı değişmiş.
>
> Agent resume sonrası silinmiş fonksiyonları referans eden tavsiyeler veriyor ve yeni modüllerden habersiz davranıyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Agent'ın system prompt'una "her oturumda dosyaları baştan kontrol et" talimatı ekle.
>
> **B)** Daha büyük context window'a sahip bir model kullan.
>
> **C)** Değişiklikler kapsamlı ve yapısal olduğu için fresh start with summary injection yap — önceki bulguların yapılandırılmış özetini (bulgular, kararlar, kalan işler, değişen dosyalar) yeni oturuma enjekte et.
>
> **D)** fork_session ile iki dal oluştur ve en iyi sonucu seç.

### Correct Answer: C

**Why C is correct:** 5 dosyada kapsamlı değişiklik — fonksiyonlar silinmiş, yeni modüller eklenmiş, API değişmiş. Bu "birkaç dosya değişmiş" seviyesini aşıyor; yapı değişmiş. Tool sonuçları tamamen bayat. Resume + spesifik bildirim bile yetmeyebilir çünkü agent'ın context'indeki yapısal varsayımlar geçersiz. Fresh start with summary injection: yeni temiz oturum + önceki bulguların yapılandırılmış özeti. Stale veriden arınmış, önceki bilgiyi kaybetmeden yeni başlangıç.

**Why A is wrong:** Prompt talimatı olasılıksal ve sorunu yanlış yerde çözmeye çalışıyor. Asıl mesele context'teki verinin bayat olması — "dosyaları kontrol et" talimatı bunu garantili çözmez.

**Why B is wrong:** Sorun context window boyutu değil, stale data. Daha büyük model de eski tool sonuçlarına dayanarak aynı hatalı tavsiyeleri verir.

**Why D is wrong:** fork_session farklı yaklaşımları karşılaştırmak içindir. Buradaki sorun stale context — dallanma yapsan bile her iki dal da aynı bayat veriden başlar, sorun çözülmez.

---

## Question 11 (Task Statement 1.1) — YENİ

> Bir rapor üreten agent'ın loop'u yalnızca `end_turn` ve `tool_use` değerlerini kontrol ediyor; diğer her durumda yanıtı nihai kabul edip kullanıcıya sunuyor. Kullanıcılar iki şikayet bildiriyor:
>
> 1. Uzun raporlar bazen cümlenin ortasında kesiliyor ve öyle sunuluyor
> 2. Web search tool'u (sunucu taraflı) kullanılan bazı isteklerde agent birkaç aramadan sonra "araştırmayı tamamlayamadım" benzeri yarım bir yanıt veriyor
>
> **Kök neden ve düzeltme hangisidir?**
>
> **A)** `max_tokens` değeri çok düşük — 4096'dan 8192'ye çıkarmak iki sorunu da çözer.
>
> **B)** Loop `max_tokens` ve `pause_turn` stop_reason değerlerini ele almıyor. `max_tokens` → yanıt kesik, bitmiş sayma, devam ettir; `pause_turn` → sunucu taraflı tool döngüsü duraklatıldı, yanıtı olduğu gibi history'ye ekleyip tekrar gönder.
>
> **C)** System prompt'a "raporu kısa tut ve aramaları 3 ile sınırla" talimatı ekle.
>
> **D)** Loop'a "yanıt noktayla bitmiyorsa devam et" kontrolü ekle.

### Correct Answer: B

**Why B is correct:** İki belirti iki farklı `stop_reason` değerine karşılık geliyor. Sorun 1: çıktı `max_tokens` sınırına takılmış — loop bunu tanımadığı için kesik yanıtı "bitmiş" sayıyor. Sorun 2: sunucu taraflı tool (web search) iterasyon limitine gelince API `pause_turn` döndürür; loop bunu da tanımadığı için yarım araştırmayı sunuyor. Doğru loop tüm `stop_reason` değerlerini ele alır: `max_tokens` → devam ettir, `pause_turn` → aynı history ile tekrar gönder.

**Why A is wrong:** `max_tokens`'ı yükseltmek birinci sorunu bir süreliğine öteler ama loop hâlâ `max_tokens` durumunu tanımaz — daha uzun rapor yine kesilir. İkinci sorunla (`pause_turn`) hiçbir ilgisi yok.

**Why C is wrong:** Prompt tabanlı ve semptomu gizlemeye çalışıyor. Raporu kısaltmak kullanıcının istediği çıktıyı vermez; aramaları sınırlamak `pause_turn`'ün doğru işlenmesinin yerini tutmaz.

**Why D is wrong:** Natural language parsing anti-pattern'ının bir çeşidi — noktalama işaretinden tamamlanma çıkarımı yapmak güvenilmez. `stop_reason` tam olarak bunun için var.

---

## Question 12 (Task Statement 1.1) — YENİ

> Bir agent, üç bölgenin stok verisini karşılaştırmak için Claude'a `get_inventory` tool'unu veriyor. Claude tek yanıtta üç `tool_use` bloğu döndürüyor (her bölge için bir tane). Geliştiricinin kodu şöyle:
>
> ```python
> for block in response.content:
>     if block.type == "tool_use":
>         result = get_inventory(**block.input)
>         messages.append({"role": "user", "content": [
>             {"type": "tool_result", "tool_use_id": block.id, "content": result}
>         ]})
> ```
>
> İkinci API çağrısı 400 hatası döndürüyor.
>
> **Sorun nedir?**
>
> **A)** Claude aynı anda yalnızca bir tool çağırabilir; `tool_choice` ile `disable_parallel_tool_use: true` ayarlanmalı.
>
> **B)** Her `tool_result` ayrı bir user mesajı olarak ekleniyor. Bir assistant yanıtındaki tüm `tool_use` bloklarının sonuçları, hemen sonraki **tek bir** user mesajının `content` listesinde toplanmalı.
>
> **C)** `tool_result` blokları `assistant` rolüyle gönderilmeli.
>
> **D)** Assistant yanıtı history'ye eklenmeden tool sonuçları gönderilmiş; önce `response.content` assistant mesajı olarak eklenmeli, sonra da her sonuç ayrı user mesajı olarak.

### Correct Answer: B

**Why B is correct:** Kural: assistant turundaki her `tool_use` bloğu için hemen sonraki user mesajında karşılık gelen bir `tool_result` bulunmalı. Kod üç ayrı user mesajı üretiyor; ilk user mesajı yalnızca bir sonucu içerdiğinden diğer iki `tool_use` bloğu karşılıksız kalıyor ve API isteği reddediyor. Düzeltme: üç `tool_result` bloğunu tek bir listede toplayıp tek user mesajı olarak eklemek.

**Why A is wrong:** Paralel tool çağrısı bir hata değil, özelliktir ve latency'yi azaltır. Kapatmak semptomu ortadan kaldırır ama doğru olan loop'u paralel çağrıyı işleyecek şekilde yazmaktır.

**Why C is wrong:** `tool_result` blokları her zaman `user` rolüyle gönderilir. Rol doğru; mesaj yapısı yanlış.

**Why D is wrong:** Assistant yanıtının history'ye eklenmesi gerektiği doğru (kodda görünmüyor olabilir), ama "her sonuç ayrı user mesajı" kısmı tam olarak hatanın kendisi. Yarısı doğru, yarısı yanlış bir şık.

---

## Question 13 (Task Statement 1.5) — YENİ

> Bir finans agent'ı `wire_transfer` tool'uyla para transferi yapabiliyor. Ekip, $10.000 üzerindeki transferlerin yönetici onayı olmadan gerçekleşmemesini istiyor. Bir geliştirici şu çözümü öneriyor: "`wire_transfer` için bir `PostToolUse` hook yazalım; tutar $10.000'ı aşıyorsa ve onay yoksa hook işlemi engellesin."
>
> **Bu öneri hakkında doğru değerlendirme hangisidir?**
>
> **A)** Öneri doğru — `PostToolUse` tool sonucunu görebildiği için tutarı kontrol edip engelleyebilir.
>
> **B)** Öneri yanlış — `PostToolUse` çalıştığında transfer zaten gerçekleşmiştir; engelleme yapamaz. Kontrol `PreToolUse` hook'unda olmalı: tutar eşiği aşıyorsa ve onay yoksa `permissionDecision: "deny"` (ya da insan onayı için `"ask"`) döndürülmeli.
>
> **C)** Öneri yanlış — hook yerine system prompt'a "$10.000 üzeri transferlerde onay iste" talimatı yeterli.
>
> **D)** Öneri doğru ama eksik — `PostToolUse` hook'una ek olarak `Stop` hook'u da eklenmeli.

### Correct Answer: B

**Why B is correct:** `PostToolUse` tool çalıştıktan **sonra** tetiklenir — para çoktan gitmiştir. Bu hook sonucu dönüştürebilir ya da loglayabilir ama işlemi geri alamaz. Tool çağrısını engellemek `PreToolUse`'un işidir: tutar `input`'ta görünür, eşik aşılıyor ve onay yoksa `deny` (red nedeniyle birlikte) ya da insan onayı akışı için `ask` döndürülür.

**Why A is wrong:** `PostToolUse`'un sonucu görmesi engelleme yetkisi vermez; zamanlama olarak iş işten geçmiştir. Klasik sınav tuzağı.

**Why C is wrong:** Finansal işlem, tek başarısızlığın maliyeti yüksek — prompt olasılıksaldır, deterministik garanti gerekir.

**Why D is wrong:** `Stop` hook'u ana agent turunu bitirdiğinde çalışır; transferle ilgisi yok. Yanlış hook'a bir yanlış hook daha eklemek çözüm değil.

---

## Question 14 (Task Statement 1.2) — YENİ

> Bir coordinator, "yapay zeka düzenlemeleri" raporu için dört araştırma subagent'ı başlatıyor: "AB düzenlemeleri", "ABD düzenlemeleri", "küresel düzenleme eğilimleri" ve "AI Act analizi". Loglar: "küresel eğilimler" subagent'ı AB ve ABD kaynaklarının çoğunu yeniden çekmiş; "AI Act analizi" ile "AB düzenlemeleri" subagent'ları neredeyse aynı dokümanları işlemiş. Token maliyeti beklenenin 2 katı, sentez raporunda AI Act üç farklı yerde üç farklı şekilde anlatılıyor.
>
> **Kök neden ve en etkili düzeltme hangisidir?**
>
> **A)** Synthesis subagent'ına "tekrar eden bölümleri birleştir" talimatı ekle.
>
> **B)** Coordinator'ın scope partitioning'i hatalı — alt görevler örtüşüyor ("küresel eğilimler" AB/ABD'yi kapsıyor, "AI Act" AB'nin alt kümesi). Ayrık kapsamlarla yeniden ayrıştır ve her subagent prompt'una neyi kapsamayacağını açıkça yaz.
>
> **C)** Subagent'ların birbirleriyle konuşmasını sağla ki hangi kaynağın çekildiğini paylaşsınlar.
>
> **D)** Subagent sayısını 2'ye düşür: "AB" ve "ABD".

### Correct Answer: B

**Why B is correct:** Bu bir kapsam örtüşmesi sorunu — dar ayrıştırmanın tersi. Şemsiye alt görev ("küresel eğilimler") ve alt küme alt görev ("AI Act" ⊂ "AB") diğerleriyle çakışıyor. Coordinator alt görevleri ayrık tanımlamalı (ör. "AB — AI Act dahil", "ABD", "AB ve ABD dışındaki ülkeler", ve gerekirse "sektörler arası karşılaştırma" gibi ayrık bir eksen) ve sınırları prompt'ta belirtmeli. Tekrar kaynağında önlenir; maliyet ve tutarsızlık birlikte çözülür.

**Why A is wrong:** Semptomu en sonda maskeler; tekrar eden araştırmanın maliyeti zaten ödenmiştir. Hatayı kaynağına izle.

**Why C is wrong:** Hub-and-spoke ihlali — observability ve kontrol kaybı; kök nedeni (örtüşen ayrıştırma) çözmez.

**Why D is wrong:** Kapsamı keyfi olarak daraltır — küresel eğilimler ve AB/ABD dışı ülkeler raporlanmaz. Sorun subagent sayısı değil, kapsamların örtüşmesi.

---

## Question 15 (Task Statement 1.7 / 1.3) — YENİ

> Bir geliştirici, Agent SDK ile bir kod tabanı analizi oturumu yürütmüş ve session ID'sini kaydetmiş. Şimdi aynı analizden iki bağımsız refactoring denemesi başlatmak istiyor ve şu kodu yazıyor:
>
> ```python
> options = ClaudeAgentOptions(fork_session=True)
> ```
>
> Her çalıştırmada agent analizi sıfırdan yapıyor; önceki oturumdan hiçbir şey hatırlamıyor.
>
> **Sorun nedir?**
>
> **A)** `fork_session` tek başına bir oturum belirtmez — hangi oturumun dallanacağını söyleyen `resume="<session_id>"` ile birlikte kullanılmalı. `resume` olmadan her çalıştırma yeni, boş bir oturumdur.
>
> **B)** `fork_session` yerine `continue_conversation=True` kullanılmalı; bu son oturumu otomatik bulur ve dallandırır.
>
> **C)** Agent SDK oturumları diske yazmaz; analiz özeti manuel olarak prompt'a enjekte edilmeli.
>
> **D)** `fork_session=True` yerine `fork_session="<session_id>"` yazılmalı.

### Correct Answer: A

**Why A is correct:** `fork_session` bir bayraktır: "resume ettiğin oturumun üzerine yazma, yeni bir ID ile dallan" der. Hangi oturumun kopyalanacağını `resume` belirler. `resume` verilmediğinde dallanacak bir şey yoktur — SDK yeni, boş bir oturum açar ve agent haliyle sıfırdan başlar. Doğru kullanım: `ClaudeAgentOptions(resume="<session_id>", fork_session=True)` — her deneme için bir kez.

**Why B is wrong:** `continue_conversation` en son oturumu **devam ettirir**, dallandırmaz — iki deneme aynı oturumu sırayla kirletir. Ayrıca "en son" oturumun analiz oturumu olduğu garanti değil.

**Why C is wrong:** Oturumlar diske yazılır; `resume` tam olarak bunun için var. Manuel özet enjeksiyonu (fresh start) geçerli bir teknik ama burada gereksiz — analiz bayat değil, sadece yanlış seçenekle çağrılmış.

**Why D is wrong:** `fork_session` boolean'dır; oturum kimliği `resume` parametresine yazılır.

---

## Question 16 (Task Statement 1.3) — YENİ

> Bir coordinator agent, araştırma subagent'ları başlatıyor; bu subagent'lar kendi alt konuları için başka subagent'lar başlatıyor, onlar da daha alt konular için yenilerini. Loglar üç seviye derinlikte onlarca subagent gösteriyor. Bir çalıştırmanın maliyeti beklenenin 8 katı, hangi bulgunun hangi subagent'tan geldiği izlenemiyor ve bazı alt-alt konular birbiriyle örtüşüyor.
>
> **En uygun düzeltme hangisidir?**
>
> **A)** Her subagent'a daha ucuz bir `model` ata — maliyet düşer.
>
> **B)** İç içe subagent derinliğini sınırla (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, ör. 1) ve ayrıştırmayı coordinator'da merkezileştir: coordinator alt konuları kendisi ayrık olarak belirlesin, subagent'lar yalnızca kendilerine verilen kapsamı araştırsın ve yeni subagent açmasın.
>
> **C)** Subagent'ların birbirleriyle doğrudan iletişim kurmasını sağla ki örtüşmeyi kendileri çözsünler.
>
> **D)** Tüm subagent'ları kaldır; coordinator tek başına araştırsın.

### Correct Answer: B

**Why B is correct:** Kontrolsüz iç içe spawning üç sorunu birden üretiyor: maliyet katlanması, observability kaybı (hub-and-spoke'un "her şey coordinator'dan geçer" ilkesi derinlikle erozyona uğruyor) ve ayrıştırmanın dağılması (her seviye kendi ayrıştırmasını yapınca kapsam örtüşüyor). Derinlik sınırı ve merkezi ayrıştırma her üçünü de çözer: coordinator tek ayrıştırma noktasıdır, subagent'lar yaprak düğümlerdir.

**Why A is wrong:** Ucuz model maliyeti azaltır ama subagent sayısını, observability kaybını ve kapsam örtüşmesini değiştirmez. Semptomlardan yalnızca birine, o da kısmen.

**Why C is wrong:** Hub-and-spoke ihlali; observability sorununu daha da kötüleştirir.

**Why D is wrong:** Paralelliğin ve uzmanlaşmanın faydasını tamamen yok eder; tek agent'ta attention dilution riski. Sorun subagent kullanmak değil, derinliği ve ayrıştırmayı kontrol etmemek.
