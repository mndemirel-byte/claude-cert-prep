# Task Statement 1.2: Çoklu Agent Orkestrasyonu (Multi-Agent Orchestration)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Döngüye sahip tek bir agent güçlüdür, ancak bazı problemler tek bir agent'ın iyi başa çıkamayacağı kadar karmaşıktır. Uzmanlara ihtiyacın var. İşte **çoklu agent orkestrasyonu** tam olarak burada devreye girer.

Sınavın test ettiği mimari **hub-and-spoke** (merkez ve bağlantı) olarak adlandırılır. Bir tekerlek hayal et:

- **Merkez (hub)**, **koordinatör agent**'tır. Merkezde oturur ve işleri yönetir.
- **Bağlantılar (spoke'lar)**, **subagent'lardır** — her biri tek bir konuda uzmanlaşmış birimler (örneğin, web araması, doküman analizi, kod inceleme, sentez).

Kritik kural: **TÜM iletişim koordinatör üzerinden akar.** Subagent'lar birbirleriyle asla doğrudan iletişim kurmaz. Web arama agent'ı sentez agent'ın ihtiyaç duyduğu bir şey bulursa, bunu yandan aktarmaz — sonuçlarını koordinatöre döndürür ve koordinatör ilgili bilgiyi sentez agent'a iletir.

---

## Neden Önemli

Bu hub-and-spoke deseni sana üç şey kazandırır:

1. **Gözlemlenebilirlik (Observability)** — tüm bilgi akışı tek bir noktadan geçer, böylece her şeyi loglayabilir ve izleyebilirsin.
2. **Tutarlı hata yönetimi** — bir subagent başarısız olursa, koordinatör bunu yakalar ve ne yapılacağına karar verir.
3. **Kontrol** — koordinatör her subagent'ın hangi bağlamı göreceğine karar verir, bu da bilgi sızıntısını önler ve subagent'ların odaklanmasını sağlar.

---

## İzolasyon İlkesi (En Sık Yanlış Anlaşılan Kavram)

Bu, sınavın en çok vurguladığı kavramdır. Hafızana kazı:

> **Subagent'lar koordinatörün konuşma geçmişini otomatik olarak MİRAS ALMAZ. Subagent'lar çağrılar arasında bellek PAYLAŞMAZ. Bir subagent'ın ihtiyaç duyduğu her bilgi, prompt'una açıkça dahil edilmelidir.**

Her subagent'ı, kendisine bir görev verdiğin yepyeni bir çalışan gibi düşün. Projede neler olduğu hakkında hiçbir şey bilmiyorlar — sen brifinglerinde söylemedikçe. Bir şeyden bahsetmeyi unutursan, basitçe o bilgiden habersiz olurlar.

---

## Koordinatörün Sorumlulukları

Koordinatör aşağıdakilerin tamamını yapar:

- **Görev ayrıştırma (Task decomposition)** — karmaşık bir isteği alt görevlere böler
- **Dinamik subagent seçimi** — hangi subagent'lara ihtiyaç olduğuna karar verir (her zaman hepsine değil)
- **Bağlam aktarımı (Context passing)** — her subagent'a tam olarak ihtiyaç duyduğu bilgiyi verir
- **Sonuç birleştirme (Result aggregation)** — subagent'lardan gelen çıktıları toplar ve birleştirir
- **Yinelemeli iyileştirme (Iterative refinement)** — birleştirilmiş çıktıyı inceler, eksiklikleri tespit eder ve gerekirse yeniden görevlendirir
- **Hata yönetimi (Error handling)** — başarısızlıkları yakalar ve nasıl kurtarılacağına karar verir

---

## Dar Ayrıştırma Hatası (Sınav Tuzağı)

Bu, sınavın test ettiği belirli bir başarısızlık modudur. Şöyle çalışır:

Bir kullanıcı soruyor: *"Yapay zekanın yaratıcı endüstriler üzerindeki etkisi nedir?"*

Koordinatör bunu alt görevlere ayrıştırır, ancak yalnızca görsel sanatlar hakkında alt görevler oluşturur — dijital resim, grafik tasarım, illüstrasyon. Müzik, yazarlık, film ve oyun sektörünü tamamen atlar.

Her subagent kendisine verilen alt görevde mükemmel iş çıkarır. Sentez iyi yazılmıştır. Ama nihai rapor sadece görsel sanatları kapsar.

**Hata nerede?** Subagent'larda değil. Sentezde değil. Hata **koordinatörün görev ayrıştırmasındadır**. Problemi en baştan çok dar dilimleyerek parçalamıştır. Sınav, **hatayı kaynağına kadar izlemeni** bekler, alt bileşenleri suçlamanı değil.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Hub-and-spoke | Merkezde koordinatör, bağlantılarda subagent'lar, TÜM iletişim koordinatör üzerinden |
| İzolasyon ilkesi | Subagent'lar otomatik olarak hiçbir şey miras almaz — her bağlam parçası açıkça aktarılmalı |
| Koordinatör sorumlulukları | Ayrıştırma, seçim, bağlam aktarımı, birleştirme, iyileştirme, hata yönetimi |
| Dar ayrıştırma | Nihai çıktıda konu başlıkları tamamen eksikse, hatayı koordinatörün ayrıştırmasına kadar izle |
| Subagent'lar arası doğrudan iletişim yok | Subagent'lar birbirleriyle asla doğrudan konuşmaz — her zaman koordinatör üzerinden |

---

## Pratik Senaryo

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
