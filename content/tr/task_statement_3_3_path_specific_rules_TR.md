# Task Statement 3.3: Yol-Bazlı Kurallar (Path-Specific Rules)

## Domain 3 — Claude Code Konfigürasyonu ve İş Akışları (Sınavın %20'si)

---

## Temel Fikir

Bazen kuralların belirli **dosya türlerine** uygulanması gerekir — tüm test dosyaları, tüm API dosyaları, tüm Terraform dosyaları gibi. Bu dosyalar kod tabanının her yerine dağılmış olabilir. Dizin seviyesi CLAUDE.md dosyaları bu durumda yetersiz kalır çünkü tek bir dizine bağlıdır. İşte yol-bazlı kurallar (path-specific rules) tam olarak bu sorunu çözer.

---

## `.claude/rules/` Dosyaları ve YAML Frontmatter

`.claude/rules/` dizinine kural dosyaları koyarsın. Her dosyanın başında YAML frontmatter ile **glob pattern** belirtirsin:

```yaml
---
paths: ["terraform/**/*"]
---

Tüm Terraform dosyalarında:
- Her kaynak (resource) için açıklayıcı isim kullan
- Modülleri ayrı dizinlerde organize et
- State dosyasını remote backend'de tut
```

```yaml
---
paths: ["**/*.test.tsx"]
---

Tüm test dosyalarında:
- describe/it yapısı kullan
- Her test tek bir davranışı test etmeli
- Mock'ları dosya başında tanımla
- Test isimleri "should" ile başlamalı
```

**Kurallar sadece glob pattern'a uyan dosyalar düzenlenirken yüklenir.** Terraform dosyasına dokunmuyorsan, Terraform kuralları yüklenmez.

---

## Dizin Seviyesi CLAUDE.md vs Yol-Bazlı Kurallar

Bu ayrım sınavın favori sorusudur. Kesin olarak öğren:

| Özellik | Dizin Seviyesi CLAUDE.md | Yol-Bazlı Kurallar (`.claude/rules/`) |
|---|---|---|
| Kapsam | **Tek bir dizin** | **Tüm kod tabanı** (glob pattern ile) |
| Eşleştirme | Dosyanın bulunduğu dizin | Dosya yolu pattern'ı |
| Test dosyaları | Her dizine CLAUDE.md koymalısın | `**/*.test.tsx` ile hepsini yakalar |
| Token verimliliği | O dizindeyken her zaman yüklü | Sadece eşleşen dosyalarda yüklü |

### Kritik Fark

**Glob pattern'lar tüm kod tabanındaki dosyaları eşleştirir.** `**/*.test.tsx` pattern'ı hangi dizinde olursa olsun TÜM test dosyalarını yakalar.

**Dizin seviyesi CLAUDE.md sadece o tek dizindeki dosyalara uygulanır.** Test dosyaları 50 farklı dizine dağılmışsa, 50 tane CLAUDE.md dosyası oluşturman gerekir — bakımı imkansız.

---

## Token Verimliliği

Yol-bazlı kuralların önemli bir avantajı: **sadece eşleşen dosyalar düzenlenirken yüklenir.**

- Terraform dosyasına dokunmuyorsan → Terraform kuralları yüklenmez
- Test dosyası düzenlemiyorsan → test kuralları yüklenmez
- Her zaman yüklenen CLAUDE.md'ye kıyasla **daha az gereksiz bağlam, daha az token tüketimi**

---

## Kullanım Senaryoları

### Test Kuralları
```yaml
---
paths: ["**/*.test.tsx", "**/*.test.ts", "**/*.spec.ts"]
---
```
Tüm test dosyalarına uygulanan kurallar — dizin fark etmez.

### API Kuralları
```yaml
---
paths: ["src/api/**/*", "src/routes/**/*"]
---
```
API ve route dosyalarına özgü kurallar.

### Altyapı Kuralları
```yaml
---
paths: ["terraform/**/*", "infrastructure/**/*"]
---
```
Altyapı konfigürasyon dosyalarına özgü kurallar.

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `.claude/rules/` + YAML frontmatter | Glob pattern ile yol-bazlı kurallar tanımla |
| Glob pattern | `**/*.test.tsx` — tüm kod tabanındaki test dosyalarını yakalar |
| Dizin CLAUDE.md sınırlaması | Sadece tek bir dizine uygulanır — dağınık dosyalar için yetersiz |
| Token verimliliği | Sadece eşleşen dosyalar düzenlenirken yüklenir — gereksiz bağlam azalır |
| Sınav tuzağı | "50 dizindeki test dosyalarına kural uygula" → yol-bazlı kurallar, dizin CLAUDE.md değil |

---

## Pratik Senaryo 1

> Bir kod tabanında test dosyaları kaynak dosyalarla aynı dizinde bulunuyor (co-located). 50'den fazla dizinde test dosyaları var. Takım tüm testlerin aynı kuralları izlemesini istiyor: describe/it yapısı, tek davranış testi, mock'lar dosya başında.
>
> **Doğru yaklaşım hangisidir?**
>
> **A)** `.claude/rules/` dizininde `paths: ["**/*.test.tsx"]` glob pattern'ı ile yol-bazlı kural dosyası oluştur.
>
> **B)** Her 50 dizine ayrı `CLAUDE.md` dosyası koy — her birine test kurallarını yaz.
>
> **C)** Tek bir kök `CLAUDE.md` dosyasına tüm test kurallarını yaz — her zaman yüklü olsun.
>
> **D)** Bir `/test-rules` skill'i oluştur — her test yazarken çağrılsın.

### Doğru Cevap: A

**Neden A doğru:** `**/*.test.tsx` glob pattern'ı tüm kod tabanındaki test dosyalarını yakalar — hangi dizinde olursa olsun. Tek bir kural dosyası, 50+ dizindeki tüm test dosyalarına uygulanır. Bakımı kolay, token verimli (sadece test dosyası düzenlenirken yüklenir).

**Neden B yanlış:** 50 dizine 50 ayrı CLAUDE.md dosyası koymak bakım kabusudur. Bir kuralı değiştirmek istediğinde 50 dosyayı güncellemelisin. Yol-bazlı kuralların tam olarak çözdüğü sorun bu.

**Neden C yanlış:** Kök CLAUDE.md her zaman yüklenir — test dosyası düzenlemesen bile test kuralları bağlamda yer kaplar. Token israfı ve bağlam kirliliği. Ayrıca test dışı dosyalarda gereksiz bilgi.

**Neden D yanlış:** Skill'ler isteğe bağlı çağrılır — her test yazımında çağırmayı hatırlamak gerekir. Unutulabilir. Yol-bazlı kurallar otomatik yüklenir — eşleşen dosya düzenlendiğinde kendiliğinden devreye girer.

---

## Pratik Senaryo 2

> Bir takımın Terraform konfigürasyon dosyaları `infrastructure/terraform/` dizininde. Ayrıca `modules/` dizininde de Terraform modülleri var. Takım tüm Terraform dosyalarında aynı isimlendirme ve organizasyon kurallarını uygulamak istiyor.
>
> **Hangi yaklaşım en uygun?**
>
> **A)** `infrastructure/terraform/CLAUDE.md` dizin seviyesi dosyası oluştur.
>
> **B)** `.claude/rules/terraform.md` dosyası oluştur — `paths: ["**/*.tf", "**/*.tfvars"]` frontmatter ile.
>
> **C)** Kök CLAUDE.md dosyasına Terraform kurallarını ekle.
>
> **D)** Her Terraform dosyasının başına yorum olarak kuralları yaz.

### Doğru Cevap: B

**Neden B doğru:** Terraform dosyaları iki farklı dizinde (`infrastructure/terraform/` ve `modules/`). Glob pattern `**/*.tf` her iki dizindeki dosyaları da yakalar. Tek bir kural dosyası, tüm Terraform dosyalarına uygulanır. Token verimli — sadece `.tf` dosyası düzenlenirken yüklenir.

**Neden A yanlış:** Dizin seviyesi CLAUDE.md sadece `infrastructure/terraform/` dizinindeki dosyalara uygulanır. `modules/` dizinindeki Terraform dosyaları bu kuralları almaz. İkinci bir CLAUDE.md oluşturmak gerekir — yol-bazlı kurallar bunu tek dosyayla çözer.

**Neden C yanlış:** Kök CLAUDE.md her zaman yüklenir. Python dosyası düzenlerken bile Terraform kuralları bağlamda olur — token israfı.

**Neden D yanlış:** Dosya içi yorumlar Claude Code'un konfigürasyon mekanizması değil. Bakımı zor, standartlaşma sağlanamaz.
