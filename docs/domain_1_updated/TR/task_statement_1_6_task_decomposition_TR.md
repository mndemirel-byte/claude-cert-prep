# Task Statement 1.6: Görev Ayrıştırma Stratejileri (Task Decomposition Strategies)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Büyük görevleri nasıl parçalara ayırırsın? İki temel pattern var ve her birinin ne zaman doğru olduğunu bilmen gerekiyor. Seçim kriteri tek bir soruya iner: **adımlar önceden biliniyor mu, yoksa yol boyunca mı keşfediliyor?**

---

## Pattern 1: Sabit Sıralı Pipeline (Fixed Sequential Pipeline / Prompt Chaining)

İşi önceden belirlenmiş sıralı adımlara bölersin. Her adımın çıktısı bir sonraki adımın girdisi olur.

Örnek — kod inceleme:

1. Her dosyayı tek tek analiz et
2. Sonra tüm dosyalar arası bağımlılıkları kontrol eden bir entegrasyon geçişi yap

**Ne zaman kullanılır:** Tahmin edilebilir, yapılandırılmış, çok yönlü görevler — kod inceleme, doküman işleme, veri dönüştürme, "önce çıkar → sonra doğrula → sonra biçimlendir" gibi akışlar.

**Avantajı:** Tutarlı ve güvenilir; her adım tek bir işe odaklanır, çıktı kalitesi öngörülebilir.

**Sınırlaması:** Beklenmedik bulgulara uyum sağlayamaz — adım 2'de "aslında adım 1'i farklı yapmalıydım" diyemez.

### Adımlar arası programatik gate'ler

Prompt chaining'in gücü yalnızca sıralamada değil, adımlar **arasına** kod koyabilmende. Her adımın çıktısı bir sonrakine gitmeden önce programatik olarak kontrol edilir:

- Çıkarım adımı boş ya da şemaya uymayan sonuç döndürdüyse → sonraki adıma geçme, yeniden dene ya da hata ver
- Analiz adımı "kritik güvenlik açığı" işaretlediyse → biçimlendirme adımını atla, doğrudan escalate et
- Adım çıktısı token bütçesini aştıysa → özetle, sonra devam et

Bu gate'ler 1.4'teki deterministik zorlama mantığının pipeline'a uygulanmış hali: modelin "bir sonraki adıma hazır mıyım?" diye karar vermesine güvenmek yerine, kod karar verir.

---

## Pattern 2: Dinamik Uyarlanabilir Ayrıştırma (Dynamic Adaptive Decomposition)

Alt görevleri her adımda keşfedilen bilgiye göre dinamik olarak üretirsin.

Örnek — "legacy bir kod tabanına test ekle":

- Önce yapıyı haritalarsın
- Yüksek etkili alanları belirlersin
- Bağımlılıklar ortaya çıktıkça önceliklendirilmiş bir plan oluşturursun

**Ne zaman kullanılır:** Açık uçlu araştırma görevleri, keşif gerektiren problemler, alt görevlerin önceden bilinemediği durumlar.

**Avantajı:** Probleme uyum sağlar; keşfedilen her bilgi planı iyileştirir.

**Sınırlaması:** Daha az öngörülebilir — süre, maliyet ve kapsam önceden kestirilemez.

### Durma kriteri ve bütçe

Dinamik ayrıştırmanın en büyük riski **sonu gelmeyen keşif**: agent her adımda yeni alt görevler üretir, hiçbir zaman "yeterince biliyorum" demez. Bu yüzden dinamik plan her zaman açık sınırlarla tasarlanır:

- **Hedef tanımı:** "Test kapsamı en riskli 5 modülde %70'e çıkınca dur" gibi ölçülebilir bir bitiş noktası
- **Bütçe:** Maksimum alt görev sayısı, tur sayısı ya da token bütçesi (1.1'deki güvenlik ağı mantığı)
- **Derinlik sınırı:** Alt görev kaç seviye dallanabilir (1.3'teki nesting depth)
- **Getiri eşiği:** Yeni keşifler plana anlamlı bir şey eklemiyorsa keşif fazını bitir, yürütmeye geç

Sınavda "agent haftalardır kod tabanını haritalıyor ama tek test yazmadı" senaryosunun cevabı, dinamik ayrıştırmayı terk etmek değil, **durma kriteri ve bütçe eklemek**tir.

---

## Anthropic'in Pattern Terminolojisiyle Eşleme

Sınav, Anthropic'in "Building Effective Agents" rehberindeki desen adlarını kullanabilir. Domain 1'de öğrendiklerin bu desenlere şöyle karşılık gelir:

| Building Effective Agents deseni | Ne yapar | Domain 1'deki karşılığı |
|---|---|---|
| **Prompt chaining** | Sabit sıralı adımlar, aralarında programatik gate | Bu dersteki Pattern 1 |
| **Routing** | Girdiyi sınıflandırıp uygun özel akışa yönlendir | 1.2'deki dinamik subagent seçimi |
| **Parallelization — sectioning** | Bağımsız alt görevleri paralel çalıştır, birleştir | 1.3'teki parallel spawning; bu dersteki per-file pass |
| **Parallelization — voting** | Aynı görevi birden fazla kez çalıştır, çoğunluğa/birleşime bak | Domain 4'teki multi-instance review |
| **Orchestrator-workers** | Merkezi orkestratör alt görevleri dinamik üretir ve dağıtır | 1.2'deki hub-and-spoke; bu dersteki Pattern 2 |
| **Evaluator-optimizer** | Üret → değerlendir → iyileştir döngüsü | 1.2'deki yinelemeli iyileştirme |

Rehberin ana ilkesi sınavın da ana ilkesi: **en basit yeterli deseni seç.** Sabit pipeline yetiyorsa orkestratör kurma; tek agent yetiyorsa subagent açma. Karmaşıklık yalnızca ölçülebilir bir fayda sağlıyorsa eklenir.

---

## Attention Dilution Problemi (Sınav Tuzağı)

Bu çok önemli. Tek bir geçişte çok fazla dosyayı veya veriyi işlersen, Claude'un dikkati dağılır. Sonuç: bazı dosyalara detaylı geri bildirim verir, diğerlerindeki bariz hataları kaçırır. Daha da kötüsü — **aynı pattern'ı bir dosyada sorunlu olarak işaretlerken, başka bir dosyada aynı kodu onaylar**. Bu tutarsızlık attention dilution'ın belirtisidir.

### Neden "daha büyük model / daha büyük context window" çözmez?

Sınavın favori distractor'ı. Attention dilution bir **kapasite** sorunu değildir — 14 dosya context window'a sığıyor, sorun sığmaması değil. Sorun, tek geçişte tüm dosyalara **aynı kriterleri aynı derinlikte** uygulamanın yapısal olarak zor olması: model geçişin başında kurduğu değerlendirme çerçevesini sona doğru gevşetir, öncelikleri kayar, ilk dosyalarda bulduğu sorun tipleri sonraki dosyalarda "normal" görünmeye başlar. Daha büyük context window daha fazla dosya sığdırır — ve aynı sorunu daha büyük ölçekte yaşatır.

### Çözüm: Multi-pass mimari

- **Pass 1 — Per-file local analysis:** Her dosyayı ayrı ayrı, aynı prompt ve aynı kriterlerle incele. Yerel sorunları yakala. Her dosya "ilk dosya" muamelesi görür — tutarlılık buradan gelir.
- **Pass 2 — Cross-file integration:** Pass 1'in yapılandırılmış çıktılarını al; dosyalar arası veri akışı, bağımlılık ve tutarsızlıkları kontrol et. Bu geçiş kaynak kodun tamamını değil, Pass 1'in bulgularını görür — dolayısıyla kendisi de attention dilution'a girmez.

Per-file geçişleri yerel sorunları tutarlı şekilde yakalar; entegrasyon geçişi dosyalar arası sorunları yakalar.

### Maliyet trade-off'u

Multi-pass daha fazla API çağrısı demektir: 14 dosya için 14 + 1 çağrı, tek geçişte 1 çağrı yerine. Bu kabul edilebilir bir trade-off'tur çünkü (a) per-file çağrılar bağımsızdır ve **paralel** çalıştırılabilir (toplam süre artmaz), (b) her çağrı küçüktür (toplam token maliyeti tek büyük çağrıdan çok farklı değildir), (c) kaçırılan bir bug'ın maliyeti ek çağrılardan yüksektir. Sınavda "multi-pass çok pahalı, tek geçişe dön" şıkkı distractor'dır.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Fixed sequential pipeline (prompt chaining) | Önceden belirlenmiş sıralı adımlar, aralarında programatik gate — tahmin edilebilir görevler için |
| Dynamic adaptive decomposition | Keşfedilen bilgiye göre dinamik alt görevler — açık uçlu araştırma için; **durma kriteri ve bütçe şart** |
| Seçim kriteri | Adımlar önceden biliniyor mu? Evet → pipeline. Hayır → dinamik |
| Building Effective Agents eşlemesi | Prompt chaining, routing, parallelization (sectioning/voting), orchestrator-workers, evaluator-optimizer — en basit yeterli deseni seç |
| Attention dilution | Tek geçişte çok fazla veri → tutarsız derinlik ve çelişkili değerlendirmeler; kapasite değil tutarlılık sorunu |
| Multi-pass architecture | Per-file local analysis (paralel) + cross-file integration — attention dilution'ın çözümü |
| Exam trap | "Daha büyük model", "prompt'a eşit dikkat göster yaz", "multi-pass pahalı" — hiçbiri yapısal sorunu çözmez |

---

## Pratik Senaryo 1

> Bir kod inceleme agent'ı 14 dosyalık bir pull request'i tek geçişte analiz ediyor. Sonuçlar:
>
> - Bazı dosyalara çok detaylı geri bildirim veriyor, diğerlerindeki bariz bug'ları kaçırıyor
> - Bir pattern'ı 3. dosyada "anti-pattern" olarak işaretliyor, ama 11. dosyada aynı kodu onaylıyor
>
> **Sorun nedir ve nasıl düzeltilir?**
>
> **A)** Agent'ın context window'u yetersiz — daha büyük bir model kullanılmalı.
>
> **B)** Tek geçişte 14 dosya işlemek attention dilution'a neden oluyor — per-file local analysis + cross-file integration olmak üzere multi-pass mimarisine geçilmeli.
>
> **C)** Agent'ın system prompt'una "her dosyaya eşit dikkat göster" talimatı eklenmeli.
>
> **D)** Dosyalar alfabetik sırayla değil, öncelik sırasına göre sıralanmalı.

### Doğru Cevap: B

**Neden B doğru:** 14 dosyayı tek geçişte işlemek Claude'un dikkatini dağıtıyor. Tutarsız derinlik ve aynı pattern'a farklı tepkiler vermesi bunun klasik belirtisi. Multi-pass mimari — önce her dosyayı ayrı ayrı, aynı kriterlerle analiz et, sonra bulgular üzerinde dosyalar arası entegrasyon geçişi yap — her iki sorunu da çözer.

**Neden A yanlış:** Sorun context window boyutu değil, dikkat dağılımı. 14 dosya zaten sığıyor. Daha büyük model tek geçişte aynı tutarlılık sorununu yaşar; daha büyük context window ise daha fazla dosyanın aynı sorunu yaşamasına yol açar.

**Neden C yanlış:** Prompt talimatı olasılıksal. "Eşit dikkat göster" demek attention dilution'ı çözmez — bu yapısal bir mimari sorunu, prompt sorunu değil.

**Neden D yanlış:** Sıralama değişikliği hangi dosyaların ihmal edildiğini değiştirir ama sorunu çözmez. Hâlâ tek geçiş, hâlâ dikkat dağılımı.

---

## Pratik Senaryo 2

> Bir ekip, müşteri destek e-postalarını işleyen bir agent kuruyor. Her e-posta için yapılacaklar sabit: (1) yapılandırılmış alanları çıkar (müşteri, ürün, sorun tipi), (2) sorunu sınıflandır, (3) yanıt taslağı üret, (4) taslağı ton ve uyumluluk açısından kontrol et. Ekip bunu "her adımda keşfedilen bilgiye göre alt görev üreten" dinamik bir orkestratörle uyguluyor. Sonuç: bazı e-postalar için orkestratör 12 alt görev üretiyor, bazıları için 2; işlem süresi öngörülemiyor; adım 1'in çıkardığı alanlar boş olsa bile adım 3 çalışıp uydurma bir yanıt üretiyor.
>
> **En uygun düzeltme hangisidir?**
>
> **A)** Orkestratöre daha ayrıntılı bir system prompt yaz — her e-posta için tam olarak 4 alt görev üretmesini söyle.
>
> **B)** Bu iş sabit ve öngörülebilir dört adımdan oluşuyor — dinamik orkestratör yerine prompt chaining pipeline'ı kur; adımlar arasına programatik gate koy (çıkarılan alanlar boşsa adım 3'e geçme, yeniden dene ya da escalate et).
>
> **C)** Her e-posta için 4 subagent'ı paralel başlat — süre öngörülebilir olur.
>
> **D)** Adım 3'e "alanlar boşsa yanıt üretme" talimatı ekle.

### Doğru Cevap: B

**Neden B doğru:** Adımlar önceden biliniyor ve her e-posta için aynı — bu dinamik ayrıştırma değil, sabit pipeline işi. Dinamik orkestratör burada gereksiz karmaşıklık ve öngörülemezlik yaratıyor. Prompt chaining her e-postayı aynı 4 adımdan geçirir; adımlar arasındaki programatik gate ise boş çıkarım sonucunun bir sonraki adıma sızmasını deterministik olarak engeller. "En basit yeterli desen" ilkesi.

**Neden A yanlış:** Dinamik orkestratörü prompt'la sabit davranmaya zorlamak, yanlış deseni yamamaktır. Olasılıksal olarak "genellikle 4" alt görev üretir, ama sabit pipeline'ın öngörülebilirliğini vermez ve boş-alan sorununu çözmez.

**Neden C yanlış:** Adımlar birbirine bağımlı — sınıflandırma çıkarıma, taslak sınıflandırmaya ihtiyaç duyar. Paralel başlatma yalnızca bağımsız alt görevler içindir (1.3); burada her adım bir öncekinin çıktısıyla çalışır.

**Neden D yanlış:** Prompt talimatı olasılıksal. Adım 3'ün "alanlar boş" durumunu fark edip durmasına güvenmek yerine, adımlar arasına kod gate'i koymak deterministik çözümdür. Ayrıca ana sorunu (yanlış desen seçimi) ele almıyor.
