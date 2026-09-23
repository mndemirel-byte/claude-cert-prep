# Task Statement 1.1: Agentic Döngüler (Agentic Loops)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Normalde Claude'u kullandığınızda tek bir alışveriş gerçekleşir: bir mesaj gönderirsin, bir yanıt alırsın, biter. **Agentic döngü**, Claude'u *harekete geçebilen* bir şeye dönüştürür — araçları çağırabilir, sonuçlara bakabilir, tekrar düşünebilir, daha fazla araç çağırabilir ve iş bitene kadar devam edebilir.

Bunu bir araştırma asistanı tutmak gibi düşün. Ona sadece bir soru sorup tek bir cevap almazsın. Gider araştırır, bulduklarıyla geri gelir, daha fazla bilgiye ihtiyacı olduğuna karar verir, başka bir şey daha araştırır ve sonunda eksiksiz bir cevapla geri döner. İşte agentic döngü budur.

---

## Yaşam Döngüsü — Adım Adım

Kodda tam olarak nasıl çalıştığını görelim:

**Adım 1:** Messages API üzerinden Claude'a bir istek gönderirsin. Bu istek bir system prompt (agent'ın talimatları) ve konuşma geçmişini içerir.

**Adım 2:** Claude yanıt verir. Her yanıtta `stop_reason` adında bir alan bulunur. Bu, agentic sistemlerdeki en önemli tek alandır. Claude'un *neden üretmeyi durdurduğunu* söyler.

**Adım 3:** `stop_reason` alanını kontrol edersin:

- Eğer `"tool_use"` ise → Claude bir araç kullanmak istiyor. "Sana nihai bir cevap vermeden önce bir şey yapmam gerekiyor" demektir. Aracı çalıştırırsın, sonucu alırsın, **konuşma geçmişine eklersin** ve her şeyi tekrar Claude'a gönderirsin. Adım 2'ye geri dön.
- Eğer `"end_turn"` ise → Claude işini bitirmiştir. Yanıtı kullanıcıya sun. Döngüden çık.

Hepsi bu. Agentic döngünün tamamı şudur: **gönder → stop_reason'ı kontrol et → ya araçları çalıştır ve döngüye devam et, ya da bitir.**

Kritik detay: Tool sonuçlarını aldığında, sadece sonuçları tek başına geri göndermezsin. Onları tam konuşma geçmişine eklersin. Claude şimdiye kadar olan her şeyi görmek zorundadır — kendi önceki akıl yürütmesini, yaptığı tool çağrılarını ve şimdi sonuçları — böylece bir sonraki adımda ne yapacağına karar verebilir.

---

## Üç Anti-Pattern (Sınav Tuzakları)

Sınav, bu döngüyü kontrol etmenin **yanlış** yollarını bilip bilmediğini test eder. Üç tane var ve cevap seçeneklerinde gördüğünde anında reddetmen gerekiyor.

### Anti-pattern 1: Tamamlanmaya Karar Vermek İçin Doğal Dili Ayrıştırma

Claude'un yanıtında "İşim bitti" veya "İşte nihai cevabım" ifadesinin olup olmadığını kontrol etmek. Bu güvenilmezdir çünkü doğal dil belirsizdir — Claude "Aramayı bitirdim" diyebilir ama hâlâ sonuçları sentezlemesi gerekebilir. `stop_reason` alanı tam olarak metinden tahmin yapmak zorunda kalmaman için var.

### Anti-pattern 2: Birincil Durdurma Mekanizması Olarak Keyfi İterasyon Sınırları

Örneğin, "ne olursa olsun 10 döngüden sonra dur." Bu yanlıştır çünkü ya faydalı çalışmayı keser (ya 11. döngü önemli olandıysa?) ya da gereksiz iterasyonlar çalıştırarak zaman harcar. Claude, `stop_reason` aracılığıyla ne zaman bitirdiğini bildirir. İterasyon sınırları bir *güvenlik ağı* olabilir, ama asla birincil kontrol mekanizması olmamalıdır.

### Anti-pattern 3: Tamamlanma Sinyali Olarak Metin İçeriğini Kontrol Etme

Örneğin: `if response.content[0].type == "text": bittik`. Bu bir tuzaktır çünkü **Claude aynı yanıtta hem metin hem de tool çağrıları döndürebilir.** "Bazı ilk sonuçları buldum, şimdi veritabanını kontrol edeyim" diyebilir — bu yanıtta hem metin *hem de* bir tool_use bloğu vardır. Metin gördüğün için durursan, döngüyü erken sonlandırmış olursun.

---

## Model Güdümlü vs Önceden Yapılandırılmış Karar Alma

Bir agentic döngüde, bağlama göre hangi aracı çağıracağına ve ne zaman çağıracağına **Claude karar verir**. "Önce A aracını çağır, sonra B aracını, sonra C aracını" diyen bir betik yazmazsın. Claude'a araçlara erişim verirsin ve hangilerine ihtiyacı olduğunu düşünmesine izin verirsin.

Sınav, esneklik açısından bu model güdümlü yaklaşımı tercih eder. Ancak — kritik iş kuralları söz konusu olduğunda (örneğin "iade yapmadan önce her zaman kimliği doğrula"), bunları Claude'un hatırlamasını umarak değil, programatik olarak zorlarsın. (Task Statement 1.4'te ayrıntılı olarak ele alınmaktadır.)

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `stop_reason` | Agentic döngü için **tek** güvenilir sonlandırma sinyali |
| `"tool_use"` | Aracı çalıştır, sonucu geçmişe ekle, Claude'a geri gönder |
| `"end_turn"` | Agent işini bitirdi — nihai yanıtı sun |
| Konuşma geçmişi | Tool sonuçları tam geçmişe **eklenmeli**, tek başına gönderilmemeli |
| Anti-pattern'lar | Birincil durdurma mekanizması olarak asla doğal dil ayrıştırma, iterasyon sınırları veya içerik türü kontrolleri kullanma |

---

## Pratik Senaryo

> Bir geliştirici, kullanıcıların konu araştırmasına yardımcı olan bir agent oluşturmuş. Agent'ın web arama aracına erişimi var. Geliştiricinin döngü mantığı, agent'ın ne zaman bitirdiğini belirlemek için `response.content[0].type == "text"` kontrolü yapıyor — metin bulursa döngüden çıkıyor ve yanıtı kullanıcıya sunuyor.
>
> Kullanıcılar, agent'ın sık sık eksik yanıtlar verdiğini bildiriyor — daha fazla araştırma yapması gerekirken genellikle tek bir aramadan sonra duruyor.
>
> **Hata nedir ve nasıl düzeltilmelidir?**

### Doğru Cevap

**Kök Neden:** Claude aynı yanıtta hem metin hem de `tool_use` blokları döndürebilir. Geliştiricinin mantığı `content[0].type == "text"` kontrolü yapıyor ve bunu bir tamamlanma sinyali olarak değerlendiriyor. Ancak Claude sıklıkla bir metin bloğu (örneğin, "Bazı ilk sonuçları buldum, daha fazla ayrıntı için arama yapayım") döndürürken *aynı anda* bir `tool_use` bloğu da döndürüyor. Döngü metni görüyor, agent'ın bitirdiğini varsayıyor ve erken çıkıyor — Claude hâlâ görevin ortasındayken bile.

**Düzeltme:**

`stop_reason` yanıt metninin içinde değildir. Yanıt nesnesinin üzerinde ayrı bir alandır. Yanıtı iki farklı parçası olan bir yapı olarak düşün:

- `response.content` → asıl içerik (metin blokları, tool_use blokları veya her ikisi)
- `response.stop_reason` → Claude'un *neden üretmeyi durdurduğunu* söyleyen yapılandırılmış bir alan

Düzeltme, içerik türü kontrolünü `stop_reason` kontrolüyle değiştirmektir:

- `stop_reason == "tool_use"` → Claude araçları kullanması gerekiyor. Çalıştır, sonuçları ekle, tekrar döngüye gir.
- `stop_reason == "end_turn"` → Claude gerçekten bitirdi. Döngüden çık.

```python
# YANLIŞ — güvenilmez, erken sonlandırmaya neden olur
if response.content[0].type == "text":
    return response

# DOĞRU — stop_reason tek güvenilir sinyaldir
if response.stop_reason == "end_turn":
    return response
elif response.stop_reason == "tool_use":
    # istenen aracı/araçları çalıştır
    # tool sonuçlarını konuşma geçmişine ekle
    # güncellenmiş konuşmayı Claude'a geri gönder
```

**Temel İlke:** `stop_reason`, yanıt metninin bir parçası değil, **yanıt nesnesi üzerindeki yapılandırılmış bir alandır**. Agentic döngünün devam edip etmeyeceğini veya sonlanıp sonlanmayacağını belirlemek için tek güvenilir mekanizmadır.
