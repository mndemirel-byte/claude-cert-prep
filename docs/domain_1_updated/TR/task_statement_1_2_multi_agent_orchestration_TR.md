# Task Statement 1.2: Çoklu Agent Orkestrasyonu (Multi-Agent Orchestration)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Döngüye sahip tek bir agent güçlüdür, ancak bazı problemler tek bir agent'ın iyi başa çıkamayacağı kadar karmaşıktır. Uzmanlara ihtiyacın var. İşte **çoklu agent orkestrasyonu** tam olarak burada devreye girer.

Sınavın test ettiği mimari **hub-and-spoke** (merkez ve bağlantı) olarak adlandırılır. Anthropic'in "Building Effective Agents" terminolojisinde bu desenin adı **orchestrator-workers**'tır — sınavda iki isim de geçebilir. Bir tekerlek hayal et:

- **Merkez (hub)**, **koordinatör agent**'tır (orchestrator). Merkezde oturur ve işleri yönetir.
- **Bağlantılar (spoke'lar)**, **subagent'lardır** (workers) — her biri tek bir konuda uzmanlaşmış birimler (örneğin, web araması, doküman analizi, kod inceleme, sentez).

Kritik kural: **TÜM iletişim koordinatör üzerinden akar.** Subagent'lar birbirleriyle asla doğrudan iletişim kurmaz. Web arama agent'ı sentez agent'ın ihtiyaç duyduğu bir şey bulursa, bunu yandan aktarmaz — sonuçlarını koordinatöre döndürür ve koordinatör ilgili bilgiyi sentez agent'a iletir.

---

## Neden Önemli

Bu hub-and-spoke deseni sana üç şey kazandırır:

1. **Gözlemlenebilirlik (Observability)** — tüm bilgi akışı tek bir noktadan geçer, böylece her şeyi loglayabilir ve izleyebilirsin.
2. **Tutarlı hata yönetimi** — bir subagent başarısız olursa, koordinatör bunu yakalar ve ne yapılacağına karar verir.
3. **Kontrol** — koordinatör her subagent'ın hangi bağlamı göreceğine karar verir, bu da bilgi sızıntısını önler ve subagent'ların odaklanmasını sağlar.

### Alternatif topolojiler — ve sınav neden hub-and-spoke'u tercih ediyor

| Topoloji | Nasıl çalışır | Uygun olduğu yer | Zayıflığı |
|---|---|---|---|
| **Tek agent** | Bir loop, tüm tool'lar | Basit, dar kapsamlı görevler | Context şişer, dikkat dağılır (bkz. 1.6) |
| **Sıralı pipeline** | A → B → C, her çıktı bir sonrakinin girdisi | Adımları önceden bilinen, öngörülebilir işler | Beklenmedik bulgulara uyum sağlayamaz |
| **Hub-and-spoke** | Koordinatör dağıtır, toplar, değerlendirir | Açık uçlu, çok yönlü araştırma ve analiz | Koordinatör darboğaz olabilir; ayrıştırma hatası her şeyi etkiler |
| **Peer-to-peer** | Subagent'lar birbirine doğrudan mesaj atar | — | Gözlemlenebilirlik ve hata yönetimi kaybolur; **sınavda distractor** |

Sınavda "subagent'lar birbirleriyle doğrudan konuşsun, koordinatörü atla" şıkkı her zaman yanlıştır.

---

## İzolasyon İlkesi (En Sık Yanlış Anlaşılan Kavram)

Bu, sınavın en çok vurguladığı kavramdır. Hafızana kazı:

> **Subagent'lar koordinatörün konuşma geçmişini otomatik olarak MİRAS ALMAZ. Subagent'lar çağrılar arasında bellek PAYLAŞMAZ. Bir subagent'ın ihtiyaç duyduğu her bilgi, prompt'una açıkça dahil edilmelidir.**

Her subagent'ı, kendisine bir görev verdiğin yepyeni bir çalışan gibi düşün. Projede neler olduğu hakkında hiçbir şey bilmiyorlar — sen brifinglerinde söylemedikçe. Bir şeyden bahsetmeyi unutursan, basitçe o bilgiden habersiz olurlar.

### Tam olarak ne miras alınır, ne alınmaz?

"Hiçbir şey miras almaz" sınav için yeterli bir kısaltma, ama teknik olarak nüans var (Claude Code / Agent SDK bağlamında):

| Subagent **alır** | Subagent **almaz** |
|---|---|
| Kendi system prompt'u (AgentDefinition içindeki `prompt`) | Koordinatörün **konuşma geçmişi** |
| Koordinatörün Task çağrısında yazdığı görev prompt'u | Koordinatörün system prompt'u |
| Kendisine tanımlı tool'lar | Diğer subagent'ların ürettiği ara bulgular |
| Proje CLAUDE.md dosyaları | Önceki çağrılardaki kendi belleği (her çağrı sıfırdan başlar) |

İstisna: `fork_session` ile oluşturulan bir dal, fork noktasına kadar olan geçmişi alır (bkz. 1.3 ve 1.7). Bu, isolation ilkesinin ihlali değil, bilinçli bir tasarım seçimidir.

Sınav mesajı değişmez: **koordinatörün bildiği bir şeyin subagent tarafından da bilinmesini istiyorsan, onu prompt'a yazmak zorundasın.**

---

## Koordinatörün Sorumlulukları

Koordinatör aşağıdakilerin tamamını yapar:

- **Görev ayrıştırma (Task decomposition)** — karmaşık bir isteği alt görevlere böler
- **Kapsam bölümleme (Scope partitioning)** — alt görevlerin birbiriyle **örtüşmemesini** sağlar
- **Dinamik subagent seçimi** — hangi subagent'lara ihtiyaç olduğuna karar verir (her zaman hepsine değil)
- **Bağlam aktarımı (Context passing)** — her subagent'a tam olarak ihtiyaç duyduğu bilgiyi verir
- **Sonuç birleştirme (Result aggregation)** — subagent'lardan gelen çıktıları toplar ve birleştirir
- **Yinelemeli iyileştirme (Iterative refinement)** — birleştirilmiş çıktıyı değerlendirir, eksiklikleri tespit eder ve gerekirse yeniden görevlendirir
- **Hata yönetimi (Error handling)** — başarısızlıkları yakalar ve nasıl kurtarılacağına karar verir

Aşağıda sınavın ayrıca vurguladığı üç sorumluluğu açıyoruz.

---

## Kapsam Bölümleme — Duplication'ı Önlemek

Exam guide'ın açıkça saydığı bir beceri: *"Partitioning research scope to minimize duplication across subagents."*

Ayrıştırma yalnızca "konuyu parçala" demek değil; parçaların **ayrık (non-overlapping)** olmasını da sağlamak demek. Kötü ayrıştırmanın iki belirtisi vardır: (1) bazı konular hiç kapsanmaz (aşağıdaki "dar ayrıştırma"), (2) aynı konu birden fazla subagent tarafından kapsanır.

Örnek — "elektrikli araç pazarı" araştırması:

- **Kötü:** Subagent A → "EV pazarı genel", Subagent B → "EV batarya teknolojisi", Subagent C → "EV üreticileri". A'nın kapsamı B ve C ile örtüşür; üçü de Tesla'nın batarya stratejisini araştırır.
- **İyi:** A → "talep ve satış verileri (bölge bazlı)", B → "batarya ve şarj altyapısı teknolojisi", C → "üretici stratejileri ve rekabet". Her subagent'ın sınırı prompt'ta açıkça yazılır: *"Batarya teknolojisine girme — o başka bir subagent'ın kapsamı."*

Belirtiler ve maliyeti: aynı kaynaklar birden çok kez çekilir (token maliyeti), synthesis agent'a çelişkili ya da tekrar eden bulgular gider, rapor aynı şeyi iki kez söyler. Sınavda "iki subagent aynı kaynakları getiriyor ve maliyet ikiye katlanıyor" senaryosunun cevabı: **koordinatörün kapsam sınırlarını prompt'larda açıkça tanımlaması** — subagent'ları azaltmak ya da birbirleriyle konuşturmak değil.

---

## Dinamik Seçim — "Hepsinden Geçir" Anti-Pattern'ı

Exam guide: *"Designing coordinators that dynamically select subagents rather than routing through all."*

Koordinatör her isteği mevcut tüm subagent'lardan geçirmemelidir. Basit bir soru ("Bu fonksiyon ne yapıyor?") için web search, doküman analizi ve veri görselleştirme subagent'larının hepsini başlatmak:

- gereksiz maliyet ve latency yaratır,
- ilgisiz çıktılar synthesis'e gürültü olarak girer,
- hata yüzeyini büyütür (her ek subagent bir başarısızlık noktası).

Doğru yaklaşım: koordinatör isteği analiz eder ve **yalnızca gerekli** subagent'ları seçer. Bu seçim modele bırakılır (model-driven) — koordinatörün prompt'unda her subagent'ın ne zaman kullanılacağı açıkça tanımlanır, koordinatör buna göre karar verir. Sınavda "her istek için tüm subagent'ları sırayla çalıştır" şıkkı bir distractor'dır.

---

## Yinelemeli İyileştirme — Evaluator-Optimizer Döngüsü

Exam guide: *"Implementing iterative refinement loops where the coordinator evaluates synthesis output."*

Koordinatörün işi synthesis çıktısını almakla bitmez. "Building Effective Agents"taki **evaluator-optimizer** desenine karşılık gelen bir döngü kurar:

1. Synthesis subagent taslağı üretir.
2. Koordinatör taslağı **açık kriterlere göre** değerlendirir: Tüm alt konular kapsandı mı? Her iddianın kaynağı var mı? Çelişkili bulgular çözüldü mü?
3. Boşluk varsa koordinatör **hedefli** yeniden görevlendirme yapar — her şeyi baştan çalıştırmaz, yalnızca eksik alt konu için ilgili subagent'ı tekrar çağırır.
4. Kriterler karşılanınca ya da **iterasyon bütçesi** dolunca döngü biter.

İki önemli nüans: Değerlendirme kriterleri prompt'ta açık olmalı ("iyi mi?" değil, "şu 5 alt konu kapsandı mı?"). Ve döngünün bir üst sınırı olmalı — aksi halde koordinatör sonsuza kadar "biraz daha iyileştir" diyebilir (1.1'deki güvenlik ağı mantığı burada da geçerli).

---

## Dar Ayrıştırma Hatası (Sınav Tuzağı)

Bu, sınavın test ettiği belirli bir başarısızlık modudur. Şöyle çalışır:

Bir kullanıcı soruyor: *"Yapay zekanın yaratıcı endüstriler üzerindeki etkisi nedir?"*

Koordinatör bunu alt görevlere ayrıştırır, ancak yalnızca görsel sanatlar hakkında alt görevler oluşturur — dijital resim, grafik tasarım, illüstrasyon. Müzik, yazarlık, film ve oyun sektörünü tamamen atlar.

Her subagent kendisine verilen alt görevde mükemmel iş çıkarır. Sentez iyi yazılmıştır. Ama nihai rapor sadece görsel sanatları kapsar.

**Hata nerede?** Subagent'larda değil. Sentezde değil. Hata **koordinatörün görev ayrıştırmasındadır**. Problemi en baştan çok dar dilimleyerek parçalamıştır. Sınav, **hatayı kaynağına kadar izlemeni** bekler, alt bileşenleri suçlamanı değil.

Teşhis yöntemi: Subagent'ı eksik konuyla **bağımsız olarak test et**. İyi sonuç veriyorsa sorun subagent'ta değil, ona o konunun hiç verilmemiş olmasında — yani koordinatörde.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Hub-and-spoke (orchestrator-workers) | Merkezde koordinatör, bağlantılarda subagent'lar, TÜM iletişim koordinatör üzerinden |
| İzolasyon ilkesi | Subagent'lar konuşma geçmişini miras almaz — her bağlam parçası açıkça aktarılmalı |
| Koordinatör sorumlulukları | Ayrıştırma, kapsam bölümleme, dinamik seçim, bağlam aktarımı, birleştirme, iyileştirme, hata yönetimi |
| Kapsam bölümleme | Alt görevler ayrık olmalı; örtüşme = tekrar eden kaynaklar + maliyet + çelişkili bulgular |
| Dinamik seçim | Yalnızca gerekli subagent'ları başlat — "hepsinden geçir" anti-pattern |
| Yinelemeli iyileştirme | Koordinatör synthesis'i açık kriterlerle değerlendirir, hedefli yeniden görevlendirir, iterasyon bütçesi vardır |
| Dar ayrıştırma | Nihai çıktıda konu başlıkları tamamen eksikse, hatayı koordinatörün ayrıştırmasına kadar izle |
| Subagent'lar arası doğrudan iletişim yok | Peer-to-peer şıkkı her zaman distractor |

---

## Pratik Senaryo 1

> Bir çoklu agent araştırma sistemi; bir koordinatör, bir web arama subagent'ı, bir doküman analiz subagent'ı ve bir sentez subagent'ından oluşuyor. Bir kullanıcı "yenilenebilir enerji teknolojileri" hakkında rapor istiyor.
>
> Nihai rapor iyi yazılmış ve kapsamlı araştırılmış, ancak yalnızca güneş ve rüzgâr enerjisini kapsıyor. Jeotermal, gel-git, biyokütle ve nükleer füzyon tamamen eksik.
>
> Web arama ve doküman analiz subagent'ları doğru çalışıyor — bağımsız olarak jeotermal veya gel-git enerjisi sorguları ile test edildiklerinde mükemmel sonuçlar döndürüyorlar.
>
> **Kök neden nedir?**
>
> **A)** Web arama subagent'ının arama sorguları çok dar ve daha geniş arama terimleri gerekiyor.
>
> **B)** Koordinatörün görev ayrıştırması jeotermal, gel-git, biyokütle ve füzyonu araştırma alt konuları olarak dahil edememiş.
>
> **C)** Sentez subagent'ı sonuçları birleştirirken bazı araştırma konularını filtrelemiş.
>
> **D)** Subagent'ların daha geniş kapsamı anlayabilmesi için koordinatörün tam konuşma geçmişine erişmesi gerekiyor.

### Doğru Cevap: B

**Neden B doğru:** Subagent'lar doğru sorgular verildiğinde mükemmel çalışıyor — sorun, onlara jeotermal, gel-git, biyokütle veya füzyon hakkında hiç *sorulmamış* olması. Koordinatör "yenilenebilir enerji teknolojileri"ni yalnızca güneş ve rüzgâr alt konularına ayrıştırmış. Hata, koordinatörün görev ayrıştırma adımından kaynaklanıyor.

**Neden A yanlış:** Web arama subagent'ı bağımsız testte jeotermal veya gel-git sorguları ile mükemmel sonuçlar döndürüyor. Arama yeteneği sorunsuz — kendisine o konuları araması hiç söylenmemiş. Hata yukarı akışta (upstream).

**Neden C yanlış:** Sentez subagent'ı yalnızca aldığı veriyi sentezleyebilir. Jeotermal veya gel-git hakkında hiç araştırma yapılmadıysa, filtreleyecek bir şey yok. Eksik konular en başından hiç araştırılmamış.

**Neden D yanlış:** Bu, izolasyon ilkesi tuzağıdır. Subagent'lara koordinatörün tam konuşma geçmişini vermek iyi mimarinin tam tersidir. Subagent'lar yalnızca koordinatör tarafından açıkça aktarılan belirli bağlamı almalıdır. Çözüm, koordinatörün ayrıştırmasını iyileştirmektir — izolasyon ilkesini bozmak değil.

---

## Pratik Senaryo 2

> Bir koordinatör, "kurumsal siber güvenlik tehditleri" raporu için üç araştırma subagent'ı başlatıyor: "genel tehdit ortamı", "fidye yazılımı (ransomware)" ve "kimlik avı (phishing)". Loglar, üç subagent'ın da aynı 6 sektör raporunu indirdiğini ve ransomware konusunun hem birinci hem ikinci subagent tarafından ayrıntılı araştırıldığını gösteriyor. Toplam token maliyeti beklenenin 2,5 katı ve sentez raporunda aynı istatistikler farklı ifadelerle üç kez tekrar ediyor.
>
> **En etkili çözüm hangisidir?**
>
> **A)** Subagent sayısını bire düşür — tek bir subagent tüm konuyu araştırsın.
>
> **B)** Subagent'ların birbirleriyle doğrudan iletişim kurmasını sağla, böylece hangi kaynağın zaten indirildiğini paylaşabilsinler.
>
> **C)** Koordinatörün ayrıştırmasını ayrık kapsamlarla yeniden tasarla — her subagent'ın prompt'una neyi kapsayacağı **ve kapsamayacağı** açıkça yazılsın; "genel tehdit ortamı" gibi diğerleriyle örtüşen şemsiye alt görevler kaldırılsın.
>
> **D)** Sentez subagent'ına "tekrar eden bilgileri birleştir" talimatı ekle.

### Doğru Cevap: C

**Neden C doğru:** Sorun kapsam bölümlemede. "Genel tehdit ortamı" alt görevi diğer ikisinin şemsiyesi — doğal olarak ransomware ve phishing'i de araştırıyor. Koordinatörün alt görevleri ayrık tanımlaması ve sınırları prompt'ta açıkça belirtmesi ("ransomware'e girme, o ayrı bir subagent'ın kapsamı") tekrarı kaynağında önler; maliyet ve tutarsızlık birlikte çözülür.

**Neden A yanlış:** Tek subagent'a dönmek paralelliğin hız avantajını yok eder ve tek geçişte çok fazla konu attention dilution riski yaratır (bkz. 1.6). Sorun subagent sayısı değil, kapsamların örtüşmesi.

**Neden B yanlış:** Hub-and-spoke ilkesinin ihlali. Subagent'lar arası doğrudan iletişim gözlemlenebilirliği ve koordinatörün kontrolünü kaybettirir; ayrıca kök nedeni (örtüşen ayrıştırma) çözmez, semptomu koordine etmeye çalışır.

**Neden D yanlış:** Semptomu en sondaki bileşende maskelemeye çalışıyor. Tekrar eden araştırmanın token maliyeti zaten ödenmiş oluyor; sentez tekrarı birleştirse bile kaynak israfı devam eder. Hatayı kaynağına izle — koordinatörün ayrıştırması.
