# Domain 1 — Practice Exam

## Agentic Architecture & Orchestration (27% of Exam)

**Dağılım:**
- 3 soru → Agentic loops & orchestration (1.1, 1.2)
- 2 soru → Subagent invocation & context (1.3)
- 2 soru → Enforcement & hooks (1.4, 1.5)
- 2 soru → Decomposition (1.6)
- 1 soru → Session management (1.7)

**Geçme kriteri:** 8+/10

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
> Kullanıcılar iki farklı sorun bildiriyor:
> 1. Agent bazen 10 döngüden sonra yanıt vermeden duruyor
> 2. Agent bazen "Here's my final answer so far, let me search for more details" dediği halde duruyor
>
> **Bu iki sorunu da çözen doğru yaklaşım hangisidir?**
>
> **A)** Iteration cap'i 10'dan 25'e çıkar ve "final answer" yerine "task complete" ifadesini kontrol et.
>
> **B)** `response.stop_reason` alanını kontrol et — `"end_turn"` ise çık, `"tool_use"` ise tool'u çalıştırıp devam et.
>
> **C)** Her döngüde Claude'a "İşin bitti mi?" diye sor ve cevabını parse et.
>
> **D)** Iteration cap'i kaldır ve sadece `response.content[0].type == "text"` kontrolü yap.

### Correct Answer: B

**Why B is correct:** Kod iki anti-pattern'ı birden içeriyor — arbitrary iteration cap (10 döngü limiti) ve natural language parsing ("final answer" ifadesini arama). `stop_reason` alanı her iki sorunu da çözer: agent işi bitirdiğinde `"end_turn"` döner, devam etmesi gerektiğinde `"tool_use"` döner. Tahmin veya parsing gerekmez.

**Why A is wrong:** Cap'i yükseltmek ve farklı bir string aramak aynı iki anti-pattern'ı devam ettirir — arbitrary iteration cap + natural language parsing. Rakam ve string değişse de yapısal sorun aynı.

**Why C is wrong:** Natural language parsing anti-pattern'ının farklı bir versiyonu. Claude'un "evet bittim" demesi de belirsiz ve güvenilmez.

**Why D is wrong:** Content-type check anti-pattern'ı. Claude text ve tool_use bloklarını aynı yanıtta döndürebilir. Text görünce çıkmak erken sonlanmaya neden olur.

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
> **B)** `query_database` tool'unu çalıştır, sonucu conversation history'ye ekle, Claude'a geri gönder.
>
> **C)** Text bloğunu kullanıcıya göster, sonra tool'u çalıştır ve yeni bir döngü başlat.
>
> **D)** Claude'a "Bu tool çağrısını onaylıyor musun?" diye sor.

### Correct Answer: B

**Why B is correct:** `stop_reason` `"tool_use"` — bu tek önemli sinyal. Claude hem text hem tool_use bloğu döndürmüş ama `stop_reason` açıkça "devam etmem gerekiyor" diyor. Tool'u çalıştır, sonucu conversation history'ye ekle, Claude'a geri gönder. Text bloğu Claude'un "yüksek sesle düşünmesi" — karar mekanizması değil.

**Why A is wrong:** Content-type check anti-pattern'ı. Text bloğu var diye döngüyü sonlandırmak erken çıkış. `stop_reason` hâlâ `"tool_use"`.

**Why C is wrong:** Text bloğunu kullanıcıya göstermek yanlış değil ama asıl mesele `stop_reason`'a göre hareket etmek. "Yeni bir döngü başlat" ifadesi belirsiz — doğru olan mevcut conversation history'ye tool sonucunu ekleyip devam etmek.

**Why D is wrong:** Agentic loop'ta Claude kendi kararlarını verir. Her tool çağrısı için onay istemek loop'un amacını ortadan kaldırır.

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

**Why B is correct:** Sorun context passing'te. Coordinator düz metin olarak aktarıyor — synthesis agent hangi iddianın hangi kaynaktan geldiğini bilmiyor. Çözüm: structured metadata formatı — her claim'i source URL, doküman adı ve sayfa numarasıyla eşleştiren JSON yapısı. Synthesis agent bu yapılandırılmış veriyle doğru atıf yapabilir.

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
> **B)** `process_refund` tool'unun çalışabilmesi için `verify_order_history` tool'unun başarıyla tamamlanmış olmasını şart koşan bir tool call interception hook ekle.
>
> **C)** Few-shot örneklerle doğru sıralamayı göster — 5 farklı senaryo ekle.
>
> **D)** İade tutarını $100 ile sınırla.

### Correct Answer: B

**Why B is correct:** Finansal sonuçları olan bir işlem — yanlış siparişe iade. Tool call interception hook, `verify_order_history` başarıyla tamamlanmadan `process_refund` tool'unun çalışmasını fiziksel olarak engeller. %100 garanti, sıfır hata.

**Why A is wrong:** Prompt tekrarı olasılıksal. Kalın yazı ve tekrarlama başarı oranını artırabilir ama %100 garanti edemez. Zaten mevcut prompt'ta talimat var ve %5 hata veriyor.

**Why C is wrong:** Few-shot örnekler de prompt-based guidance. Modelin davranışını yönlendirir ama zorlamaz. Deterministik değil.

**Why D is wrong:** Tutarı sınırlamak sorunu çözmez — $100 altı iadelerde de yanlış siparişe iade yapılabilir. Ve asıl sorun doğrulama eksikliği, tutar değil.

---

## Question 6 (Task Statement 1.5)

> Farklı MCP tool'ları tarih bilgisini farklı formatlarda döndürüyor:
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
> **B)** Her tool'un API'sini ISO 8601 döndürecek şekilde değiştir.
>
> **C)** PostToolUse hook ile tüm tool sonuçlarındaki tarihleri standart bir formata dönüştür, Claude'a göndermeden önce.
>
> **D)** Claude'a tarih formatlarını açıklayan bir referans tablosu ekle.

### Correct Answer: C

**Why C is correct:** PostToolUse hook'un tam kullanım amacı bu — farklı tool'lardan gelen heterojen veriyi, Claude'a göndermeden önce standart formata dönüştürmek. Hook deterministik çalışır, her tool sonucu Claude'a ulaşmadan önce normalize edilir. Claude her zaman temiz, tutarlı tarih formatı görür.

**Why A is wrong:** Prompt talimatı olasılıksal. Claude Unix timestamp'i doğru çeviremeyebilir veya farklı formatlarda tutarsız davranabilir. Format dönüşümü kod işi, model işi değil.

**Why B is wrong:** Üçüncü parti API'leri değiştirmek çoğu zaman mümkün değil — MCP tool'ları dış servisler. Ve kontrol senin elinde olmalı, dış bağımlılıklarda değil.

**Why D is wrong:** Referans tablosu da prompt-based guidance. Claude'un tabloyu doğru uygulaması garantili değil. Yapısal çözüm gereken yerde bilgi ekleme yaklaşımı.

---

## Question 7 (Task Statement 1.3)

> Bir coordinator aynı anda 3 subagent başlatması gerekiyor: web search, document analysis ve data visualization. Mevcut implementasyon her birini sırayla başlatıyor — önce web search tamamlanıyor, sonra document analysis, sonra data visualization.
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

**Why B is correct:** Parallel spawning. Coordinator tek bir yanıtta birden fazla Task tool çağrısı yaparsa, subagent'lar paralel başlar. 3 subagent × 15 saniye sırayla = 45 saniye. Paralel başlatmayla ≈ 15 saniye. 3 kat hız artışı, hiçbir özellikten feragat etmeden.

**Why A is wrong:** Daha hızlı model her subagent'ı kısaltabilir ama sıralı yapı devam eder. 3 × 10 saniye = 30 saniye hâlâ paralel 15 saniyeden yavaş. Ve model değişikliği başka sorunlar yaratabilir.

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

**Why D is correct:** Attention dilution'ın klasik belirtileri — tutarsız derinlik (ilk dosyalara detaylı, son dosyalara yüzeysel) ve çelişkili değerlendirmeler (aynı pattern'a farklı tepki). Multi-pass mimari: önce her dosyayı ayrı ayrı analiz et (per-file local analysis), sonra dosyalar arası tutarsızlıkları ve bağımlılıkları kontrol et (cross-file integration pass). Her iki sorunu da çözer.

**Why A is wrong:** Sorun context window boyutu değil, dikkat dağılımı. Daha büyük model de tek geçişte 20 dosyaya odaklanmaya çalışırken aynı yapısal sorunu yaşar.

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
> **B)** Dynamic adaptive decomposition — önce yapıyı haritala, yüksek etkili alanları belirle, bağımlılıklar ortaya çıktıkça planı güncelle.
>
> **C)** Tüm dosyaları tek geçişte analiz et ve en önemli 5 dosyaya test yaz.
>
> **D)** Rastgele 10 dosya seç ve onlara test yaz.

### Correct Answer: B

**Why B is correct:** Legacy kod tabanı = bilinmeyen bağımlılıklar, değişken test edilebilirlik, keşif gerektiren problem. Bu açık uçlu araştırma görevidir. Dynamic adaptive decomposition her adımda keşfedilen bilgiye göre planı günceller — önce yapıyı haritalarsın, yüksek etkili alanları belirlersin, bağımlılıklar ortaya çıktıkça önceliklendirirsin.

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
> **C)** Değişiklikler kapsamlı olduğu için fresh start with summary injection yap — önceki bulguların yapılandırılmış özetini yeni oturuma enjekte et.
>
> **D)** fork_session ile iki dal oluştur ve en iyi sonucu seç.

### Correct Answer: C

**Why C is correct:** 5 dosyada kapsamlı değişiklik — fonksiyonlar silinmiş, yeni modüller eklenmiş, API değişmiş. Bu "birkaç dosya değişmiş" seviyesini aşıyor. Tool sonuçları tamamen bayat. Resume + spesifik bildirim bile yetmeyebilir çünkü değişiklikler çok kapsamlı. Fresh start with summary injection: yeni temiz oturum + önceki bulguların yapılandırılmış özeti. Stale veriden arınmış, önceki bilgiyi kaybetmeden yeni başlangıç.

**Why A is wrong:** Prompt talimatı olasılıksal ve sorunu yanlış yerde çözmeye çalışıyor. Asıl mesele context'teki verinin bayat olması — "dosyaları kontrol et" talimatı bunu garantili çözmez.

**Why B is wrong:** Sorun context window boyutu değil, stale data. Daha büyük model de eski tool sonuçlarına dayanarak aynı hatalı tavsiyeleri verir.

**Why D is wrong:** fork_session farklı yaklaşımları karşılaştırmak içindir. Buradaki sorun stale context — dallanma yapsan bile her iki dal da aynı bayat veriden başlar, sorun çözülmez.
