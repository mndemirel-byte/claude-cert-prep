# Task Statement 1.6: Task Decomposition Strategies

## Domain 1 — Agentic Architecture & Orchestration (27% of Exam)

---

## The Core Idea

Büyük görevleri nasıl parçalara ayırırsın? İki temel pattern var ve her birinin ne zaman doğru olduğunu bilmen gerekiyor.

---

## Pattern 1: Fixed Sequential Pipelines (Prompt Chaining)

İşi önceden belirlenmiş sıralı adımlara bölersin. Her adımın çıktısı bir sonraki adımın girdisi olur.

Örnek — kod inceleme:

1. Her dosyayı tek tek analiz et
2. Sonra tüm dosyalar arası bağımlılıkları kontrol eden bir entegrasyon geçişi yap

**Ne zaman kullanılır:** Tahmin edilebilir, yapılandırılmış görevler — kod inceleme, doküman işleme, veri dönüştürme.

**Avantajı:** Tutarlı ve güvenilir.

**Sınırlaması:** Beklenmedik bulgulara uyum sağlayamaz.

---

## Pattern 2: Dynamic Adaptive Decomposition

Alt görevleri her adımda keşfedilen bilgiye göre dinamik olarak üretirsin.

Örnek — "legacy bir kod tabanına test ekle":

- Önce yapıyı haritalarsın
- Yüksek etkili alanları belirlersin
- Bağımlılıklar ortaya çıktıkça önceliklendirilmiş bir plan oluşturursun

**Ne zaman kullanılır:** Açık uçlu araştırma görevleri, keşif gerektiren problemler.

**Avantajı:** Probleme uyum sağlar.

**Sınırlaması:** Daha az öngörülebilir.

---

## Attention Dilution Problemi (Sınav Tuzağı)

Bu çok önemli. Tek bir geçişte çok fazla dosyayı veya veriyi işlersen, Claude'un dikkati dağılır. Sonuç: bazı dosyalara detaylı geri bildirim verir, diğerlerindeki bariz hataları kaçırır. Daha da kötüsü — **aynı pattern'ı bir dosyada sorunlu olarak işaretlerken, başka bir dosyada aynı kodu onaylar**. Bu tutarsızlık attention dilution'ın belirtisidir.

**Çözüm: Multi-pass architecture.**

- **Pass 1 — Per-file local analysis:** Her dosyayı ayrı ayrı incele. Yerel sorunları yakala.
- **Pass 2 — Cross-file integration:** Dosyalar arası veri akışı, bağımlılık ve tutarsızlıkları kontrol et.

Per-file geçişleri yerel sorunları tutarlı şekilde yakalar; entegrasyon geçişi dosyalar arası sorunları yakalar.

---

## Key Exam Takeaways

| Concept | Remember |
|---|---|
| Fixed sequential pipelines | Önceden belirlenmiş sıralı adımlar — tahmin edilebilir görevler için |
| Dynamic adaptive decomposition | Keşfedilen bilgiye göre dinamik alt görevler — açık uçlu araştırma için |
| Attention dilution | Tek geçişte çok fazla veri → tutarsız derinlik ve çelişkili değerlendirmeler |
| Multi-pass architecture | Per-file local analysis + cross-file integration — attention dilution'ın çözümü |
| Exam trap | "Prompt'a eşit dikkat göster yaz" gibi çözümler yapısal sorunu çözmez — reddet |

---

## Practice Scenario

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

### Correct Answer: B

**Why B is correct:** 14 dosyayı tek geçişte işlemek Claude'un dikkatini dağıtıyor. Tutarsız derinlik ve aynı pattern'a farklı tepkiler vermesi bunun klasik belirtisi. Multi-pass mimari — önce her dosyayı ayrı ayrı analiz et, sonra dosyalar arası entegrasyon geçişi yap — her iki sorunu da çözer.

**Why A is wrong:** Sorun context window boyutu değil, dikkat dağılımı. Daha büyük model aynı sorunu yaşar çünkü tek geçişte 14 dosyaya odaklanmaya çalışmak yapısal bir problem.

**Why C is wrong:** Prompt talimatı olasılıksal. "Eşit dikkat göster" demek attention dilution'ı çözmez — bu yapısal bir mimari sorunu, prompt sorunu değil.

**Why D is wrong:** Sıralama değişikliği hangi dosyaların ihmal edildiğini değiştirir ama sorunu çözmez. Hâlâ tek geçiş, hâlâ dikkat dağılımı.
