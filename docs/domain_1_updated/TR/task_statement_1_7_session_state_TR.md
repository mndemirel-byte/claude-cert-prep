# Task Statement 1.7: Oturum Durumu ve Devam Ettirme (Session State and Resumption)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Agent'lar uzun süre çalışabilir. Bazen bir oturumu bırakıp sonra geri dönmen gerekir. Ya da agent uzun süredir çalışıyordur ve context bozulmaya başlamıştır. Bu task statement, **oturumu nasıl yönetirsin** sorusunu cevaplıyor.

Bir oturum (session), Claude Code'un diskte tuttuğu tam konuşma geçmişidir: kullanıcı mesajları, Claude'un yanıtları, tüm tool çağrıları ve sonuçları. Bu kayıt sayesinde oturumu sonra devam ettirebilir, dallandırabilir ya da özetleyip yeni bir oturuma taşıyabilirsin.

---

## Üç Seçenek

### Seçenek 1: Resume (`--resume <session-name>`)

Belirli bir oturumu kaldığı yerden devam ettirir. Önceki tüm bağlam — tool çağrıları, sonuçlar, Claude'un reasoning'i — aynen korunur.

**Ne zaman kullanılır:** Önceki bağlam hâlâ geçerli, dosyalar önemli ölçüde değişmemiş. Örneğin, bir araştırma oturumunu yarım bıraktın ve ertesi gün devam edeceksin — veriler hâlâ güncel.

### Seçenek 2: fork_session

Mevcut bir oturumun geçmişini kopyalayarak paylaşılan bir analiz temelinden **bağımsız dallar** oluşturur. Orijinal oturum değişmez; her dal yeni bir session ID alır.

**Ne zaman kullanılır:** Aynı başlangıç noktasından farklı yaklaşımları denemek istiyorsun. Örneğin, bir kod tabanı analizinden iki farklı refactoring stratejisini karşılaştırmak. Her dal birbirinden bağımsız çalışır; analizi bir kez yapıp iki kez kullanırsın.

**Mekanizma:** `fork_session` tek başına çalışmaz — her zaman `resume` ile birliktedir. `resume` hangi oturumun kopyalanacağını söyler, `fork_session` ise "üzerine yazma, dallan" der (ayrıntı 1.3'te).

### Seçenek 3: Fresh Start with Summary Injection

Yeni bir oturum başlatırsın ama önceki bulguların **yapılandırılmış bir özetini** başlangıç context'ine enjekte edersin. Sıfırdan keşif yapmaz — önceki bilgiyi özet olarak alır ve oradan devam eder.

**Ne zaman kullanılır:** Tool sonuçları bayatlamış (stale), dosyalar kapsamlı değişmiş, ya da uzun bir oturumda context kalitesi düşmüş.

**Nasıl yapılır:** Özet, yeni oturumun ilk prompt'una ya da `--append-system-prompt` ile system prompt'a verilir; proje genelinde kalıcı olması gerekiyorsa CLAUDE.md'ye yazılır. İyi bir özet serbest metin değil, sabit alanlardan oluşur:

```markdown
## Önceki oturum özeti (2026-09-24)
- Bulgular: auth modülü JWT doğrulamasını `verify_token()` içinde yapıyor; 3 endpoint bunu atlıyor (liste: ...)
- Alınan kararlar: middleware yaklaşımı seçildi, decorator yaklaşımı reddedildi (neden: ...)
- Tamamlanan işler: `auth/middleware.py` yazıldı, testleri geçiyor
- Kalan işler: 3 endpoint'i middleware'e bağla, eski decorator'ı kaldır
- O zamandan beri değişen dosyalar: `routes/api.py` (yeniden yazıldı), `models/user.py` (alan eklendi)
```

Kritik: özette **ne bilindiği** kadar **neyin artık geçerli olmayabileceği** de yazılmalı — agent bayat varsayımlarla değil, "şunları yeniden kontrol et" bilgisiyle başlar.

---

## Mekanizma Tablosu — CLI ve SDK

Sınav mekanizmayı isimleriyle sorabilir. Karşılıkları:

| İşlem | Claude Code CLI | Agent SDK seçeneği |
|---|---|---|
| Son oturumu devam ettir | `claude --continue` (`-c`) | `continue_conversation=True` |
| Belirli oturumu devam ettir | `claude --resume <ad veya ID>` (`-r`) | `resume="<session_id>"` |
| Oturum seçici aç | `claude --resume` (argümansız) | — |
| Oturuma ad ver | `claude --name <ad>` (başlangıçta) / `/rename <ad>` (oturum içinde) | — |
| Dallandır | `--fork-session` ile resume / `/branch` (oturum içinde) | `resume="<id>", fork_session=True` |
| Belirli mesaja kadar devam ettir | — | `resume_session_at="<message_uuid>"` |
| Özel oturum ID'si kullan | — | `session_id="<uuid>"` |

`--continue` ile `--resume` farkı: `--continue` bulunduğun dizindeki **en son** oturumu açar, hangisi olduğunu seçmezsin; `--resume` belirli bir oturumu ad ya da ID ile seçer. Uzun süreli projelerde oturumlara ad vermek (`--name`, `/rename`) ID ezberlemekten kurtarır — exam guide'ın "named session resumption" dediği budur.

---

## Stale Context Problemi (Sınav Tuzağı)

Bu çok önemli. Bir developer oturumu resume eder ama arada dosyaları değiştirmiştir. Agent'ın context'inde hâlâ eski tool sonuçları (eski dosya içerikleri, eski grep çıktıları) vardır. Agent bunlara dayanarak reasoning yapar — artık var olmayan kod hakkında tavsiye verir ya da çelişkili öneriler sunar.

Agent'ın "dosya değişmiş olabilir" diye kendiliğinden şüphelenmesini bekleme: context'indeki tool sonucu onun için gerçektir. Bayatlığı **sen** bildirmelisin.

**Çözüm:** Resume ediyorsan ve dosyalar değiştiyse, agent'a **hangi dosyaların değiştiğini spesifik olarak bildir** — hedefli yeniden analiz yapsın. Her şeyi sıfırdan keşfetmesini isteme.

> "Oturumdan bu yana `routes/api.py` ve `models/user.py` değişti. Önceki analizindeki bu dosyalara ait bulguları geçersiz say ve bu iki dosyayı yeniden oku. Diğer dosyalar aynı."

**Ama eğer değişiklikler çok kapsamlıysa veya tool sonuçları tamamen bayatsa** → fresh start with summary injection daha güvenilir. Ölçüt: değişen dosyaları tek tek sayabiliyorsan resume + bildirim; sayamıyorsan ya da yapının kendisi değiştiyse (modüller silinmiş, API yeniden tasarlanmış) fresh start.

---

## Dördüncü Seçenek: Context Compaction

"Uzun oturumda context kalitesi düştü" sorununun fresh start dışında bir cevabı daha var: **compaction**. Claude Code, context dolmaya yaklaştığında konuşmayı otomatik olarak özetler; `/compact` komutuyla bunu istediğin anda ve isteğe bağlı bir odakla ("test bulgularını koru") tetikleyebilirsin.

Compaction ile fresh start farkı:

| | Compaction | Fresh start with summary injection |
|---|---|---|
| Kim özetler | Claude, otomatik | Sen (ya da önceki oturumdaki Claude, senin yönlendirmenle) |
| Oturum | Aynı oturum devam eder | Yeni oturum |
| Kontrol | Düşük — neyin korunacağına model karar verir | Yüksek — özetin içeriğini sen belirlersin |
| Bayat tool sonuçları | Özetlenir ama "bayat" olduğu bilinmez | Özette açıkça işaretlenir |
| Uygun olduğu yer | Context doldu, dosyalar değişmedi | Dosyalar değişti ve/veya kontrollü yeni başlangıç isteniyor |

`PreCompact` hook'u (1.5), sıkıştırma öncesinde kritik bilgiyi dosyaya yazmak için kullanılır — compaction'ın kaybettirebileceği ayrıntılar için güvenlik ağı.

---

## Karar Tablosu

| Durum | Doğru Yaklaşım |
|---|---|
| Bağlam hâlâ geçerli, dosyalar değişmemiş | **Resume** |
| Aynı temelden farklı yaklaşımları denemek | **fork_session** (resume + fork) |
| Resume + birkaç dosya değişmiş | Resume + **spesifik dosya değişikliklerini bildir** |
| Tool sonuçları bayat, dosyalar kapsamlı değişmiş, yapı değişmiş | **Fresh start with summary injection** |
| Context doldu ama dosyalar değişmedi | **Compaction** (`/compact`) |

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Resume | Bağlam geçerli, dosyalar değişmemiş → kaldığı yerden devam; `--continue` son oturum, `--resume` seçilen oturum |
| Oturum adlandırma | `--name` / `/rename` → `--resume <ad>`; exam guide'ın "named session resumption"ı |
| fork_session | Her zaman `resume` ile; paylaşılan temelden bağımsız dallar, orijinal değişmez |
| Fresh start with summary injection | Stale context, kapsamlı değişiklik → yeni oturum + yapılandırılmış özet (bulgular, kararlar, kalan işler, **değişen dosyalar**) |
| Stale context problemi | Resume sonrası çelişkili tavsiyeler → agent bayat tool sonuçlarına dayanıyor; kendiliğinden fark etmez |
| Spesifik dosya bildirimi | Resume + değişen dosyalar → hangi dosyaların değiştiğini söyle, hedefli yeniden analiz |
| Compaction | Context doldu, dosyalar değişmedi → `/compact`; `PreCompact` hook ile kritik bilgiyi koru |
| Exam trap | "Her şeyi sıfırdan keşfet", "daha büyük model kullan", "fork'la ve en iyisini seç" — sorunu çözmez |

---

## Pratik Senaryo 1

> Bir developer, bir kod tabanı üzerinde çalışan agent oturumunu resume ediyor. Arada 3 dosyada önemli değişiklikler yapmış. Agent, bu dosyalar hakkında çelişkili tavsiyeler veriyor — bir yerde "bu fonksiyonu refactor et" diyor ama fonksiyon zaten değiştirilmiş.
>
> **Sorun nedir ve doğru yaklaşım hangisidir?**
>
> **A)** Agent'ın context window'u yetersiz — daha büyük model kullanılmalı.
>
> **B)** Agent stale tool sonuçlarına dayanarak reasoning yapıyor — oturum resume edilirken değişen dosyalar spesifik olarak bildirilmeli, ya da tool sonuçları tamamen bayatsa fresh start with summary injection yapılmalı.
>
> **C)** Agent'ın system prompt'una "dosyaları tekrar kontrol et" talimatı eklenmeli.
>
> **D)** fork_session ile iki dal oluşturulup en iyi sonuç seçilmeli.

### Doğru Cevap: B

**Neden B doğru:** Agent eski tool sonuçlarına dayanarak reasoning yapıyor — dosyalar değişmiş ama agent bunu bilmiyor ve bilemez. Çözüm iki katmanlı: değişiklikler sınırlıysa (3 dosya, sayılabilir) resume edip spesifik dosya değişikliklerini bildir; değişiklikler kapsamlıysa veya context tamamen bozulmuşsa fresh start with summary injection yap.

**Neden A yanlış:** Sorun context window boyutu değil, stale data. Daha büyük model de eski veriye dayanarak aynı hataları yapar.

**Neden C yanlış:** Prompt talimatı olasılıksal ve hedefsiz — "dosyaları tekrar kontrol et" hangi dosyaların değiştiğini söylemez; agent ya hepsini yeniden okur (israf) ya da yine bayat veriye güvenir. Spesifik bildirim gerekir.

**Neden D yanlış:** fork_session farklı yaklaşımları karşılaştırmak için kullanılır. Buradaki sorun stale context — dallanma yapsan bile her iki dal da aynı bayat veriden başlar.

---

## Pratik Senaryo 2

> Bir ekip, büyük bir monorepo'da bağımlılık analizi yapan uzun bir Claude Code oturumu yürütüyor. Analiz 40 dakika sürdü ve tamamlandı. Şimdi ekip, aynı analiz temelinden iki farklı migration stratejisini (a) modül modül kademeli geçiş, (b) tek seferde toplu geçiş — ayrı ayrı denemek ve sonuçlarını karşılaştırmak istiyor. Kod tabanı analizden bu yana değişmedi.
>
> **En verimli yaklaşım hangisidir?**
>
> **A)** İki yeni oturum başlat ve her birinde analizi baştan yaptır — böylece her strateji temiz bir context'te çalışır.
>
> **B)** Aynı oturumda önce (a)'yı dene, sonra "şimdi (b)'yi dene" de — Claude ikisini karşılaştırsın.
>
> **C)** Analiz oturumunu `resume` + `fork_session` ile iki kez dallandır; her dalda bir stratejiyi çalıştır. Analiz bir kez yapılır, iki dal da onu miras alır, birbirini etkilemez.
>
> **D)** Analiz oturumunu `/compact` ile özetle, sonra iki stratejiyi aynı oturumda sırayla dene.

### Doğru Cevap: C

**Neden C doğru:** fork_session'ın tam kullanım senaryosu — paylaşılan analiz temelinden bağımsız dallar. 40 dakikalık analiz bir kez yapılır; her dal geçmişi fork noktasına kadar miras alır ve kendi stratejisini bağımsız çalıştırır. Dallar birbirinin context'ini kirletmez, orijinal analiz oturumu bozulmadan kalır ve karşılaştırma için temiz iki sonuç elde edilir.

**Neden A yanlış:** 40 dakikalık analizi iki kez tekrarlamak israf. Kod değişmediği için analiz bayat değil — yeniden yapmanın gerekçesi yok.

**Neden B yanlış:** Aynı oturumda sırayla denemek, (b) stratejisinin (a)'nın çıktıları ve kararlarıyla kirlenmiş bir context'te çalışması demek. Karşılaştırma adil olmaz; ayrıca (a) sırasında yapılan dosya değişiklikleri (b)'yi etkiler.

**Neden D yanlış:** Compaction context'i küçültür ama izolasyon sağlamaz — B'deki kirlenme sorunu aynen devam eder. Burada context dolma sorunu da yok; sorun iki bağımsız deney ihtiyacı.
