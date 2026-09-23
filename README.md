# claude-cert-prep

Claude Certified Architect (Foundations) sınavı için tek dosyalık, çift dilli (TR/EN) çalışma rehberi.
Kaynak içerik Markdown; `make build` tek bir `dist/index.html` üretir — bağımlılık yok, çevrimdışı çalışır.

## Özellikler

- **Ana sayfa:** 5 domain ve sınav ağırlıkları (%27 / 18 / 20 / 20 / 15), domain sayfalarına "+" ile geçiş
- **Domain sayfaları:** task statement dersleri (açılır-kapanır) + cevap anahtarlı yeterlilik testi
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
│   ├── parse_content.py   # content/tr → build/data.json (dersler + quiz soruları)
│   ├── render.py          # data.json + src/* + ek içerik → dist/index.html
│   ├── build.py           # parse + render
│   ├── check.py           # Playwright ile duman testi (isteğe bağlı)
│   ├── extra_questions.py # Mock havuzu için ek sorular + senaryo etiketleri
│   └── en_content.py      # Soruların ve senaryo sayfasının İngilizce sürümleri
├── src/
│   ├── style.css
│   └── app.js             # Yönlendirme, quiz, mock sınav, dil geçişi
├── dist/index.html        # Üretilen tek dosya
├── Makefile
└── requirements.txt
```

## Kurulum ve derleme

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make build          # dist/index.html üretir
make serve          # http://localhost:8080
make check          # playwright install chromium gerekir
```

## İçerik ekleme / düzenleme

**Ders eklemek:** `content/tr/task_statement_<d>_<n>_<slug>_TR.md` dosyasını ekle, `scripts/render.py`
içindeki `DOMAINS[...]["lessons"]` listesine adını yaz. İngilizcesi için `content/en_lessons/<d>.<n>.md`
oluştur (yoksa EN modunda Türkçe metin ve bir not gösterilir).

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
