# Task Statement 3.1: CLAUDE.md Hiyerarşisi

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Claude Code çalıştığında, **nasıl davranacağını** belirleyen `CLAUDE.md` adlı talimat dosyalarını arar. Kodlama standartları, isimlendirme kuralları, test gereksinimleri, projeye özgü bağlam — hepsi bu dosyalarda tanımlanır. Bunu, kod tabanın için **kalıcı bir system prompt** olarak düşün.

Kritik nokta: **Üç seviye var** ve sınav, hangi seviyenin ne işe yaradığını bilip bilmediğini sürekli test ediyor.

---

## Üç Seviye

### 1. Kullanıcı Seviyesi: `~/.claude/CLAUDE.md`

- Senin **ev dizininde** bulunur
- **Sadece SANA** uygulanır
- **Versiyon kontrol altında DEĞİL** — Git'te yok, paylaşılmaz
- Repoyu klonlayan yeni takım üyeleri bu talimatları **ALMAZ**
- **Kullanım alanı:** Kişisel tercihler, kişisel kısayollar

### 2. Proje Seviyesi: `.claude/CLAUDE.md` veya kök dizindeki `CLAUDE.md`

- **Repoda** bulunur
- **Versiyon kontrol altında** — Git ile takip edilir, paylaşılır
- Repoyu klonlayan **HERKES** bu talimatları alır
- **Kullanım alanı:** Takım genelindeki standartlar, API kuralları, isimlendirme kuralları

### 3. Dizin Seviyesi: Alt dizin içindeki `CLAUDE.md` dosyaları

- Claude Code **o dizindeki dosyalar** üzerinde çalışırken uygulanır
- **Kullanım alanı:** Pakete özgü kurallar (örneğin, frontend klasörü backend'den farklı kurallara sahip)

---

## Özet Tablo

| Seviye | Konum | Paylaşılır mı? | Git'te mi? | Kimin için? |
|---|---|---|---|---|
| Kullanıcı | `~/.claude/CLAUDE.md` | ❌ Hayır | ❌ Hayır | Sadece sen |
| Proje | `.claude/CLAUDE.md` veya kök `CLAUDE.md` | ✅ Evet | ✅ Evet | Tüm takım |
| Dizin | Alt dizindeki `CLAUDE.md` | ✅ Evet | ✅ Evet | O dizinde çalışanlar |

---

## Modüler Organizasyon

Her şeyi tek bir devasa `CLAUDE.md` dosyasına tıkmak zorunda değilsin. İki mekanizma var:

### `@import` Sözdizimi

`CLAUDE.md` içinden dış dosyaları referans edebilirsin:

```markdown
@import ./standards/api-conventions.md
@import ./standards/testing-rules.md
```

Her paket için ilgili standartları içe aktarabilirsin — temiz ve modüler.

### `.claude/rules/` Dizini

Konuya özel kural dosyalarını bu dizine koyabilirsin:

- `testing.md` — test kuralları
- `api-conventions.md` — API kuralları  
- `deployment.md` — dağıtım kuralları

Tek büyük dosya yerine organize edilmiş, konuya göre ayrılmış kurallar.

---

## Hata Ayıklama Aracı: `/memory` Komutu

Claude Code oturumlar arasında tutarsız davranıyorsa, `/memory` komutunu kullanarak **hangi bellek dosyalarının yüklü olduğunu** doğrulayabilirsin.

Bu, "bende çalışıyor ama takım arkadaşımda çalışmıyor" sorunlarını teşhis etmenin yoludur.

---

## Sınavın Favori Tuzağı — Yeni Takım Üyesi Sorunu

Bu senaryo neredeyse her sınav setinde karşına çıkacak:

> Developer A'nın Claude Code'u takımın isimlendirme kurallarını mükemmel uyguluyor. Geçen hafta katılan Developer B ise Claude Code'dan tutarsız isimler alıyor. İkisi de aynı repo üzerinde çalışıyor.

**Kök neden:** Kurallar Developer A'nın **kullanıcı seviyesi** konfigürasyonunda (`~/.claude/CLAUDE.md`). Bu dosya Git'te yok, paylaşılmıyor. Developer B bu talimatları hiç almıyor.

**Çözüm:** Talimatları `.claude/CLAUDE.md` dosyasına (proje seviyesi) taşı — versiyon kontrol altında ve paylaşılır.

> **Sınav kuralı:** "Yeni takım üyesi talimatları almıyor" → cevap neredeyse her zaman: **talimatlar kullanıcı seviyesinde, proje seviyesine taşınmalı.**

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| Kullanıcı seviyesi (`~/.claude/CLAUDE.md`) | Sadece sana uygulanır — Git'te yok, paylaşılmaz |
| Proje seviyesi (`.claude/CLAUDE.md`) | Herkese uygulanır — Git'te, paylaşılır |
| Dizin seviyesi (alt dizindeki `CLAUDE.md`) | O dizinde çalışırken uygulanır |
| `@import` sözdizimi | Dış dosyaları CLAUDE.md'den referans et — modüler organizasyon |
| `.claude/rules/` | Konuya özel kural dosyaları — tek büyük dosya yerine |
| `/memory` komutu | Hangi bellek dosyalarının yüklü olduğunu doğrula — tutarsızlık teşhisi |
| Sınav tuzağı | Yeni üye talimatları almıyor → talimatlar kullanıcı seviyesinde |

---

## Pratik Senaryo 1

> Developer A ve Developer B aynı repoyu klonlayarak çalışıyor. Developer A, Claude Code'dan mükemmel API isimlendirme kuralları alıyor. Developer B ise tutarsız isimler alıyor. İkisi de aynı branch üzerinde çalışıyor.
>
> **Kök neden nedir?**
>
> **A)** Developer B'nin Claude Code sürümü eski — güncellenmeli.
>
> **B)** API isimlendirme kuralları Developer A'nın kullanıcı seviyesi konfigürasyonunda (`~/.claude/CLAUDE.md`) — proje seviyesine (`.claude/CLAUDE.md`) taşınmalı.
>
> **C)** Developer B'nin bilgisayarında Claude Code cache'i bozulmuş — cache temizlenmeli.
>
> **D)** Her iki developer da `/memory` komutuyla belleklerini senkronize etmeli.

### Doğru Cevap: B

**Neden B doğru:** Klasik sınav tuzağı. Developer A talimatları alıyor, Developer B almıyor, aynı repo — tek fark Developer A'nın kişisel konfigürasyonu. `~/.claude/CLAUDE.md` dosyası Git'te yok, paylaşılmaz. Çözüm: `.claude/CLAUDE.md` dosyasına taşı, herkes alsın.

**Neden A yanlış:** Sürüm farkı bu tür bir davranış farkını açıklamaz. İki developer da aracı kullanabiliyor — sorun talimatların eksikliğinde.

**Neden C yanlış:** Cache sorunu talimatların tamamen eksik olmasını açıklamaz. Sorun yapısal — dosya yeri.

**Neden D yanlış:** `/memory` komutu teşhis aracıdır, senkronizasyon aracı değil. Bellek dosyalarını gösterir ama başka birinin dosyalarını kopyalamaz.

---

## Pratik Senaryo 2

> Bir takım büyük bir projede çalışıyor. Proje kök dizininde `.claude/CLAUDE.md` dosyası var ve genel kodlama standartlarını içeriyor. Ancak `frontend/` klasöründe React'e özgü kurallar, `backend/` klasöründe ise Go'ya özgü kurallar gerekiyor.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** Tüm kuralları (genel + React + Go) tek bir kök `.claude/CLAUDE.md` dosyasına yaz.
>
> **B)** `frontend/CLAUDE.md` ve `backend/CLAUDE.md` dizin seviyesi dosyaları oluştur — Claude Code o dizindeki dosyalar üzerinde çalışırken ilgili kuralları uygulasın.
>
> **C)** Her developer kendi `~/.claude/CLAUDE.md` dosyasına çalıştığı alana göre kuralları yazmalı.
>
> **D)** React ve Go kurallarını system prompt'a ekle.

### Doğru Cevap: B

**Neden B doğru:** Dizin seviyesi CLAUDE.md dosyaları tam olarak bu amaç için var — farklı alt dizinlerdeki farklı teknoloji gereksinimleri. `frontend/CLAUDE.md` React kurallarını, `backend/CLAUDE.md` Go kurallarını içerir. Her iki dosya da Git'te, paylaşılır, ve sadece ilgili dizinde çalışırken yüklenir.

**Neden A yanlış:** Tüm kuralları tek dosyaya tıkmak gereksiz token kullanımı yaratır. Backend'de çalışırken React kurallarını yüklemek anlamsız — bağlamı kirletir.

**Neden C yanlış:** Kullanıcı seviyesi konfigürasyonu paylaşılmaz. Yeni takım üyeleri bu kuralları almaz. Ayrıca kişisel tercihlere bağlı — standartlaşma sağlanamaz.

**Neden D yanlış:** System prompt farklı bir mekanizma. Dizin seviyesi CLAUDE.md dosyaları bu sorunu doğru ve temiz şekilde çözer.
