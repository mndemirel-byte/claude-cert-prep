# claude-cert-prep

Claude Certified Architect (Foundations) sınavı için tek dosyalık, çift dilli (TR/EN) çalışma rehberi.
Kaynak içerik Markdown; `make build` tek bir `dist/index.html` üretir — bağımlılık yok, çevrimdışı çalışır.
Vercel'de statik olarak yayında: **https://claude-cert-prep-mocha.vercel.app/**

## Özellikler

- **Ana sayfa:** 5 domain ve sınav ağırlıkları (%27 / 18 / 20 / 20 / 15), domain sayfalarına "+" ile geçiş
- **Domain sayfaları:** task statement dersleri (açılır-kapanır) + cevap anahtarlı yeterlilik testi
- **Sesli dersler (Narration):** her ders için OpenAI TTS (`gpt-4o-mini-tts`, ses `cedar`) ile önceden
  üretilmiş MP3 anlatım — EN/TR mevcut kapsamda tam (30/30 ders, her iki dilde)
- **Domain Playlist:** bir dersi çalıp bitince aynı domain içindeki bir sonraki derse otomatik geçer,
  domain sonunda durur (bir sonraki domain'e sızmaz)
- **Kaldığı yerden devam (Listening Position):** hangi dersi, hangi dilde, kaçıncı saniyede bıraktığını
  hatırlar; uygulamayı kapatıp tekrar açtığında oradan devam eder
- **Oynatıcı kontrolleri:** sürüklenebilir ilerleme çubuğu (seek), baştan başlat, sona atla,
  1x/1.25x/1.5x oynatma hızı (tercih kalıcı)
- **Kilit ekranı / Bluetooth (Media Session):** telefon kilit ekranından veya araç Bluetooth'undan
  play/pause/ileri/geri kontrol edilebilir, şu an çalan ders + domain bilgisi now-playing olarak görünür
- **Sınav senaryoları:** resmi kılavuzdaki 6 senaryo, senaryo × domain haritası, seçim mekanizması
- **Mock sınav:** 6 senaryodan rastgele 4'ü, senaryo altında gruplanmış sorular, soru başına 2 dk sayaç,
  100–1000 ölçeğinde domain ağırlıklı puan (geçme 720), domain/senaryo dökümü, açıklamalı inceleme,
  tarayıcıda saklanan deneme geçmişi
- **TR / EN geçişi:** sağ üstteki toggle tüm arayüzü, dersleri, soruları ve senaryo sayfasını çevirir

## Dizin yapısı

```
claude-cert-prep/
├── content/
│   ├── tr/            # Kaynak dersler ve yeterlilik testleri (Türkçe, Markdown)
│   └── en_lessons/    # Derslerin İngilizce sürümleri (<task>.md, ör. 3.2.md)
├── scripts/
│   ├── parse_content.py     # content/tr → build/data.json (dersler + quiz soruları)
│   ├── render.py            # data.json + src/* + ek içerik → dist/index.html
│   ├── build.py             # parse + render
│   ├── narration.py         # Ders metni → seslendirmeye hazır metin; ders/dil eşleştirme;
│   │                         #   içerik-hash tabanlı üretim planlama; playlist/resume saf fonksiyonları
│   ├── test_narration.py    # narration.py için pytest testleri
│   ├── generate_narration.py# OpenAI TTS ile gerçek MP3 üretimi (OPENAI_API_KEY / .env gerekir)
│   ├── local_server.py      # Range destekli yerel HTTP sunucu (check.py ve manuel test için)
│   ├── check.py             # Playwright duman testi + Domain Playlist/resume senaryoları
│   ├── extra_questions.py   # Mock havuzu için ek sorular + senaryo etiketleri
│   └── en_content.py        # Soruların ve senaryo sayfasının İngilizce sürümleri
├── src/
│   ├── style.css
│   ├── app.js                  # Yönlendirme, quiz, mock sınav, dil geçişi, Narration player
│   ├── narration-player.js     # Player'ın saf karar fonksiyonları (dil seçimi, playlist sırası,
│   │                             #   Listening Position parse, hız döngüsü, zaman formatlama)
│   └── test_narration_player.js# narration-player.js için Node testleri (`node --test`)
├── dist/
│   ├── index.html          # Üretilen tek dosya
│   └── audio/               # Üretilen Narration MP3'leri (en/, tr/) + manifest.json (skip-cache)
├── docs/agents/             # Agent skill'lerinin okuduğu issue-tracker / domain-docs konfigürasyonu
├── CONTEXT.md               # Proje sözlüğü (Lesson, Narration, Domain Playlist, Listening Position, ...)
├── vercel.json / .vercelignore  # Statik Vercel deploy ayarları
├── Makefile
└── requirements.txt
```

## Kurulum ve derleme

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make build          # dist/index.html üretir
make serve          # http://localhost:8080
make check          # playwright install chromium gerekir; Range destekli local_server.py kullanır
```

**Testler:**

```bash
python -m pytest scripts/test_narration.py -q   # narration.py'nin saf fonksiyonları
node --test src/test_narration_player.js        # narration-player.js'in saf fonksiyonları
```

## Sesli ders üretimi (Narration)

Ses dosyaları `dist/audio/` altında repoya commit edilmiştir — normalde tekrar üretmen gerekmez.
İçerik değiştiğinde veya yeni bir ders eklediğinde:

```bash
echo "OPENAI_API_KEY=sk-..." > .env        # .gitignore'da, asla commit edilmez
pip install openai
python scripts/generate_narration.py               # sadece değişen/eksik (ders, dil) çiftlerini üretir
python scripts/generate_narration.py --only 2.3     # tek bir dersi test etmek için
make build                                          # dist/index.html'i yeni ses dosyalarıyla günceller
```

Üretim, `dist/audio/manifest.json`'daki içerik-hash kaydına göre neyin değiştiğine karar verir; aynı
metin için tekrar API çağrısı yapmaz. Uzun dersler (~2000 token TTS limitini aşanlar) otomatik olarak
parçalara bölünüp tek MP3'te birleştirilir. Üretilen dosyalar dosya boyutunu makul tutmak için
`ffmpeg` ile 64kbps mono'ya yeniden kodlanır.

## Deploy (Vercel)

Site `vercel.json` (build/install command'sız, `outputDirectory: dist`) ve `.vercelignore`
(Python dosyalarını deploy'a dahil etmeyerek Vercel'in otomatik Python algılamasını devre dışı bırakır)
ile tamamen statik olarak servis edilir. `master`'a her push otomatik yeniden deploy tetikler — ekstra
adım gerekmez. Canlı: https://claude-cert-prep-mocha.vercel.app/

## İçerik ekleme / düzenleme

**Ders eklemek:** `content/tr/task_statement_<d>_<n>_<slug>_TR.md` dosyasını ekle, `scripts/render.py`
içindeki `DOMAINS[...]["lessons"]` listesine adını yaz. İngilizcesi için `content/en_lessons/<d>.<n>.md`
oluştur (yoksa EN modunda Türkçe metin ve bir not gösterilir). `scripts/narration.py`'deki
`discover_lessons()` dosya adından `<domain>.<n>` id'sini otomatik çıkarır — yeni dersi eklendikten
sonra `python scripts/generate_narration.py` çalıştırmak yeterli, sesi otomatik üretilir.

**Quiz sorusu eklemek:** Domain 1–3 `## Soru N (Task Statement X.Y)` + blockquote + `### Doğru Cevap: X`
formatını, Domain 4–5 `### Soru N — ...` + ayrı `## Cevap Anahtarı` formatını kullanır; `parse_content.py`
her ikisini de tanır. Yeni sorunun senaryo etiketini `extra_questions.py` içindeki `BASE_SC` sözlüğüne,
İngilizcesini `en_content.py` içindeki `Q_EN` sözlüğüne ekle.

**Mock havuzuna soru eklemek:** `extra_questions.py` → `EXTRA2` listesine `{"d","sc","ts","body","opts","ans","expl"}`
ekle; İngilizcesi `Q_EN[("extra2", index)]`.

**Senaryo metinlerini değiştirmek:** `render.py` içindeki `SCEN` (TR) ve `en_content.py` içindeki
`SCEN_EN` / `SCEN_PAGE_EN` (EN).

## Mock sınav mantığı

- Havuz: domain quizlerindeki sorular + `EXTRA` + `EXTRA2` (her biri bir senaryoya etiketli)
- Her denemede 4 senaryo çekilir; her senaryodan en fazla 15 soru alınır
- Süre = soru sayısı × 2 dk; süre dolunca otomatik teslim
- Puan = 100 + 900 × Σ(ağırlık_d × doğru_d / soru_d) / Σ ağırlık_d; geçme 720
- Şık sırası karıştırılmaz (açıklamalar harflere referans verir); soru ve senaryo sırası karıştırılır

## Lisans

İçerik kişisel çalışma amaçlıdır. Senaryo tanımları Anthropic'in resmi sınav kılavuzundan özetlenmiştir.
