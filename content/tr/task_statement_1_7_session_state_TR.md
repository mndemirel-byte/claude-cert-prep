# Task Statement 1.7: Oturum Durumu ve Devam Ettirme (Session State and Resumption)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Agent'lar uzun süre çalışabilir. Bazen bir oturumu bırakıp sonra geri dönmen gerekir. Ya da agent uzun süredir çalışıyordur ve context bozulmaya başlamıştır. Bu task statement, **oturumu nasıl yönetirsin** sorusunu cevaplıyor.

---

## Üç Seçenek

### Seçenek 1: Resume (--resume <session-name>)

Belirli bir oturumu kaldığı yerden devam ettirir. Önceki tüm bağlam — tool çağrıları, sonuçlar, Claude'un reasoning'i — aynen korunur.

**Ne zaman kullanılır:** Önceki bağlam hâlâ geçerli, dosyalar önemli ölçüde değişmemiş. Örneğin, bir araştırma oturumunu yarım bıraktın ve ertesi gün devam edeceksin — veriler hâlâ güncel.

### Seçenek 2: fork_session

Paylaşılan bir analiz temelinden **bağımsız dallar** oluşturur.

**Ne zaman kullanılır:** Aynı başlangıç noktasından farklı yaklaşımları denemek istiyorsun. Örneğin, bir kod tabanı analizinden iki farklı refactoring stratejisini karşılaştırmak. Her dal birbirinden bağımsız çalışır.

### Seçenek 3: Fresh Start with Summary Injection

Yeni bir oturum başlatırsın ama önceki bulguların **yapılandırılmış bir özetini** başlangıç context'ine enjekte edersin. Sıfırdan keşif yapmaz — önceki bilgiyi özet olarak alır ve oradan devam eder.

**Ne zaman kullanılır:** Tool sonuçları bayatlamış (stale), dosyalar değişmiş, ya da uzun bir oturumda context kalitesi düşmüş.

---

## Stale Context Problemi (Sınav Tuzağı)

Bu çok önemli. Bir developer oturumu resume eder ama arada dosyaları değiştirmiştir. Agent, eski tool sonuçlarına dayanarak reasoning yapar — artık var olmayan kod hakkında tavsiye verir ya da çelişkili öneriler sunar.

**Çözüm:** Resume ediyorsan ve dosyalar değiştiyse, agent'a **hangi dosyaların değiştiğini spesifik olarak bildir** — hedefli yeniden analiz yapsın. Her şeyi sıfırdan keşfetmesini isteme.

**Ama eğer değişiklikler çok kapsamlıysa veya tool sonuçları tamamen bayatsa** → fresh start with summary injection daha güvenilir.

---

## Karar Tablosu

| Durum | Doğru Yaklaşım |
|---|---|
| Bağlam hâlâ geçerli, dosyalar değişmemiş | **Resume** |
| Aynı temelden farklı yaklaşımları denemek | **fork_session** |
| Tool sonuçları bayat, dosyalar değişmiş, context bozulmuş | **Fresh start with summary injection** |
| Resume + birkaç dosya değişmiş | Resume + **spesifik dosya değişikliklerini bildir** |

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Resume | Bağlam geçerli, dosyalar değişmemiş → kaldığı yerden devam |
| fork_session | Paylaşılan temelden bağımsız dallar — farklı yaklaşımları karşılaştırmak için |
| Fresh start with summary injection | Stale context, değişen dosyalar → yeni oturum + önceki bulguların yapılandırılmış özeti |
| Stale context problemi | Resume sonrası çelişkili tavsiyeler → agent bayat tool sonuçlarına dayanıyor |
| Spesifik dosya bildirimi | Resume + değişen dosyalar varsa → agent'a hangi dosyaların değiştiğini bildir |
| Sınav tuzağı | "Her şeyi sıfırdan keşfet" veya "daha büyük model kullan" gibi çözümler sorunu çözmez |

---

## Pratik Senaryo

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

**Neden B doğru:** Agent eski tool sonuçlarına dayanarak reasoning yapıyor — dosyalar değişmiş ama agent bunu bilmiyor. Çözüm iki katmanlı: eğer değişiklikler sınırlıysa resume edip spesifik dosya değişikliklerini bildir; eğer değişiklikler kapsamlıysa veya context tamamen bozulmuşsa fresh start with summary injection yap.

**Neden A yanlış:** Sorun context window boyutu değil, stale data. Daha büyük model de eski veriye dayanarak aynı hataları yapar.

**Neden C yanlış:** Prompt talimatı olasılıksal ve sorunu yanlış yerde çözmeye çalışıyor. Asıl mesele agent'ın context'indeki verinin bayat olması.

**Neden D yanlış:** fork_session farklı yaklaşımları karşılaştırmak için kullanılır. Buradaki sorun stale context — dallanma yapsan bile her iki dal da aynı bayat veriden başlar.
