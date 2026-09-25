# Task Statement 1.1: Agentic Döngüler (Agentic Loops)

## Domain 1 — Agentic Mimari ve Orkestrasyon (Sınavın %27'si)

---

## Temel Fikir

Normalde Claude'u kullandığınızda tek bir alışveriş gerçekleşir: bir mesaj gönderirsin, bir yanıt alırsın, biter. **Agentic döngü**, Claude'u *harekete geçebilen* bir şeye dönüştürür — araçları çağırabilir, sonuçlara bakabilir, tekrar düşünebilir, daha fazla araç çağırabilir ve iş bitene kadar devam edebilir.

Bunu bir araştırma asistanı tutmak gibi düşün. Ona sadece bir soru sorup tek bir cevap almazsın. Gider araştırır, bulduklarıyla geri gelir, daha fazla bilgiye ihtiyacı olduğuna karar verir, başka bir şey daha araştırır ve sonunda eksiksiz bir cevapla geri döner. İşte agentic döngü budur.

---

## Yaşam Döngüsü — Adım Adım

Kodda tam olarak nasıl çalıştığını görelim:

**Adım 1:** Messages API üzerinden Claude'a bir istek gönderirsin. Bu istek bir system prompt (agent'ın talimatları), tool tanımları (`tools` parametresi) ve konuşma geçmişini (`messages`) içerir.

**Adım 2:** Claude yanıt verir. Her yanıtta `stop_reason` adında bir alan bulunur. Bu, agentic sistemlerdeki en önemli tek alandır. Claude'un *neden üretmeyi durdurduğunu* söyler.

**Adım 3:** `stop_reason` alanını kontrol edersin:

- Eğer `"tool_use"` ise → Claude bir araç kullanmak istiyor. "Sana nihai bir cevap vermeden önce bir şey yapmam gerekiyor" demektir. Aracı çalıştırırsın, sonucu alırsın, **konuşma geçmişine eklersin** ve her şeyi tekrar Claude'a gönderirsin. Adım 2'ye geri dön.
- Eğer `"end_turn"` ise → Claude işini bitirmiştir. Yanıtı kullanıcıya sun. Döngüden çık.

Sınavın çekirdeği bu iki değerdir. Agentic döngünün özü şudur: **gönder → stop_reason'ı kontrol et → ya araçları çalıştır ve döngüye devam et, ya da bitir.**

Kritik detay: Tool sonuçlarını aldığında, sadece sonuçları tek başına geri göndermezsin. Onları tam konuşma geçmişine eklersin. Claude şimdiye kadar olan her şeyi görmek zorundadır — kendi önceki akıl yürütmesini, yaptığı tool çağrılarını ve şimdi sonuçları — böylece bir sonraki adımda ne yapacağına karar verebilir.

---

## Tool Sonucu Nasıl Geri Gönderilir? — `tool_result` Bloğu

"Sonucu geçmişe ekle" demek yetmez; sınav *nasıl* eklendiğini de bilmeni bekler. Yapı şöyledir:

1. Claude'un yanıtı (`role: "assistant"`) olduğu gibi geçmişe eklenir — içindeki `tool_use` bloğu dahil. Her `tool_use` bloğunun bir `id`'si vardır.
2. Ardından **`role: "user"`** olan yeni bir mesaj eklenir. İçeriği metin değil, **`type: "tool_result"`** bloklarıdır. Her blok, hangi tool çağrısına ait olduğunu `tool_use_id` alanıyla belirtir.
3. Tool hata verdiyse sonucu yine `tool_result` olarak gönderirsin — ama `is_error: true` ile. Döngüyü kırmazsın; Claude hatayı görüp başka bir yol dener.

```python
# Claude'un yanıtı: content içinde tool_use bloğu var, stop_reason == "tool_use"
messages.append({"role": "assistant", "content": response.content})

tool_results = []
for block in response.content:
    if block.type == "tool_use":
        try:
            output = run_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(output),
            })
        except Exception as e:
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": f"Tool hatası: {e}",
                "is_error": True,          # hatayı Claude'a bildir, döngüyü kırma
            })

messages.append({"role": "user", "content": tool_results})
```

Sık yapılan hatalar: `tool_result`'ı `assistant` rolüyle göndermek, `tool_use_id`'yi atlamak, tool sonucunu düz metin olarak user mesajına yazmak. Hepsi API hatası ya da Claude'un sonucu bir tool çıktısı olarak tanımaması ile sonuçlanır.

---

## Paralel Tool Çağrıları — `content[0]` Tuzağı

Claude **tek bir yanıtta birden fazla `tool_use` bloğu** döndürebilir (örneğin aynı anda üç şehrin hava durumunu sorgulamak). Bu durumda kural nettir:

> Assistant yanıtındaki **her** `tool_use` bloğu için, hemen sonraki **tek bir** `user` mesajında karşılık gelen bir `tool_result` bloğu bulunmalıdır.

Yanlış: her tool sonucunu ayrı bir user mesajı olarak göndermek. Doğru: tüm `tool_result` bloklarını tek user mesajının `content` listesinde toplamak (yukarıdaki kod tam olarak bunu yapıyor).

Bu yüzden `response.content[0]` üzerinden akıl yürüten her kod şüphelidir — ilk blok metin olabilir, ikinci ve üçüncü bloklar tool çağrısı olabilir. Her zaman `response.content` listesinin **tamamını** dolaş.

Paralel çağrıyı kapatmak istersen: `tool_choice={"type": "auto", "disable_parallel_tool_use": True}`. Bu durumda Claude yanıt başına en fazla bir tool çağırır. Sıralı bağımlılık gerektiren (A'nın çıktısı B'nin girdisi) tool setlerinde kullanılır; aksi halde paralel çağrı latency açısından tercih edilir.

---

## `stop_reason`'ın Tüm Değerleri

Sınavın çekirdeği `tool_use` ve `end_turn` olsa da, sağlam bir agentic döngü **tüm** değerleri ele almalıdır. Aksi halde döngü sessizce yarım yanıt döndürür ya da sonsuz döngüye girer.

| `stop_reason` | Anlamı | Döngü ne yapmalı |
|---|---|---|
| `end_turn` | Claude doğal olarak bitirdi | Yanıtı sun, döngüden çık |
| `tool_use` | Claude tool çağırmak istiyor | Tool'ları çalıştır, `tool_result` ekle, devam et |
| `max_tokens` | Çıktı `max_tokens` sınırına takıldı — yanıt **kesik** | `max_tokens`'ı artırıp tekrar dene ya da "devam et" iste; **asla bitmiş sayma** |
| `pause_turn` | Sunucu taraflı tool (ör. web search) iterasyon limitine geldi | Yanıtı olduğu gibi geçmişe ekleyip tekrar gönder — Claude kaldığı yerden devam eder |
| `stop_sequence` | Senin tanımladığın bir stop sequence üretildi | `stop_sequence` alanına bakıp kendi mantığına göre işle |
| `refusal` | Claude güvenlik nedeniyle yanıt vermeyi reddetti | Logla, kullanıcıya bildir; aynı isteği körlemesine tekrarlama |
| `model_context_window_exceeded` | Context window doldu | Çıktıyı kesik kabul et; geçmişi özetle/kısalt ve yeniden başlat |

Sınav tuzağı: "Agent bazen cümlenin ortasında duruyor ve döngü bunu nihai cevap olarak sunuyor" → bu `max_tokens` durumudur ve döngünün yalnızca `end_turn`/`tool_use` kontrol etmesinden kaynaklanır.

---

## Üç Anti-Pattern (Sınav Tuzakları)

Sınav, bu döngüyü kontrol etmenin **yanlış** yollarını bilip bilmediğini test eder. Üç tane var ve cevap seçeneklerinde gördüğünde anında reddetmen gerekiyor.

### Anti-pattern 1: Tamamlanmaya Karar Vermek İçin Doğal Dili Ayrıştırma

Claude'un yanıtında "İşim bitti" veya "İşte nihai cevabım" ifadesinin olup olmadığını kontrol etmek. Bu güvenilmezdir çünkü doğal dil belirsizdir — Claude "Aramayı bitirdim" diyebilir ama hâlâ sonuçları sentezlemesi gerekebilir. `stop_reason` alanı tam olarak metinden tahmin yapmak zorunda kalmaman için var.

### Anti-pattern 2: Birincil Durdurma Mekanizması Olarak Keyfi İterasyon Sınırları

Örneğin, "ne olursa olsun 10 döngüden sonra dur." Bu yanlıştır çünkü ya faydalı çalışmayı keser (ya 11. döngü önemli olandıysa?) ya da gereksiz iterasyonlar çalıştırarak zaman harcar. Claude, `stop_reason` aracılığıyla ne zaman bitirdiğini bildirir.

Nüans: İterasyon sınırı bir **güvenlik ağı** olarak meşrudur — bir tool sürekli hata verirse ya da Claude aynı çağrıyı tekrarlarsa maliyeti sınırlar. Yanlış olan, bunu *birincil* kontrol mekanizması yapmaktır. Sınıra ulaşıldığında da sessizce durmak yerine bunu açıkça loglamalı ve kullanıcıya bildirmelisin.

### Anti-pattern 3: Tamamlanma Sinyali Olarak Metin İçeriğini Kontrol Etme

Örneğin: `if response.content[0].type == "text": bittik`. Bu bir tuzaktır çünkü **Claude aynı yanıtta hem metin hem de tool çağrıları döndürebilir.** "Bazı ilk sonuçları buldum, şimdi veritabanını kontrol edeyim" diyebilir — bu yanıtta hem metin *hem de* bir tool_use bloğu vardır. Metin gördüğün için durursan, döngüyü erken sonlandırmış olursun.

---

## Tam Döngü İskeleti

Yukarıdaki her şeyi bir araya getiren referans implementasyon:

```python
MAX_ITERATIONS = 50   # güvenlik ağı — birincil mekanizma DEĞİL

def run_agent(client, system, tools, messages):
    for i in range(MAX_ITERATIONS):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=system,
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        match response.stop_reason:
            case "end_turn":
                return response                      # bitti

            case "tool_use":
                tool_results = []
                for block in response.content:       # content[0] değil — tüm liste
                    if block.type == "tool_use":
                        tool_results.append(execute_and_wrap(block))  # is_error dahil
                messages.append({"role": "user", "content": tool_results})
                continue

            case "pause_turn":
                continue                             # aynı geçmişle tekrar gönder

            case "max_tokens":
                messages.append({"role": "user",
                                 "content": "Yanıt kesildi, kaldığın yerden devam et."})
                continue

            case "refusal" | "model_context_window_exceeded":
                log_and_notify(response.stop_reason)
                return response

    raise RuntimeError(f"{MAX_ITERATIONS} iterasyonda tamamlanamadı")  # sessizce dönme
```

---

## Model Güdümlü vs Önceden Yapılandırılmış Karar Alma

Bir agentic döngüde, bağlama göre hangi aracı çağıracağına ve ne zaman çağıracağına **Claude karar verir**. "Önce A aracını çağır, sonra B aracını, sonra C aracını" diyen bir betik yazmazsın. Claude'a araçlara erişim verirsin ve hangilerine ihtiyacı olduğunu düşünmesine izin verirsin.

Sınav, esneklik açısından bu model güdümlü yaklaşımı tercih eder. Ancak — kritik iş kuralları söz konusu olduğunda (örneğin "iade yapmadan önce her zaman kimliği doğrula"), bunları Claude'un hatırlamasını umarak değil, programatik olarak zorlarsın. (Task Statement 1.4 ve 1.5'te ayrıntılı olarak ele alınmaktadır.)

---

## Sınav İçin Temel Çıkarımlar

| Kavram | Hatırla |
|---|---|
| `stop_reason` | Agentic döngü için **birincil** sonlandırma sinyali — metinden çıkarım yapma |
| `"tool_use"` | Tool'ları çalıştır, `tool_result` bloklarını tek user mesajında geçmişe ekle, Claude'a geri gönder |
| `"end_turn"` | Agent işini bitirdi — nihai yanıtı sun |
| `"max_tokens"` | Yanıt kesik — bitmiş sayma, devam ettir |
| `"pause_turn"` | Sunucu taraflı tool döngüsü duraklatıldı — aynı geçmişle tekrar gönder |
| `tool_result` bloğu | `role: "user"` mesajında, `tool_use_id` ile eşleşmiş; hata için `is_error: true` |
| Paralel tool çağrıları | Tek yanıtta birden fazla `tool_use` olabilir → hepsinin sonucu **tek** user mesajında; `content[0]`'a güvenme |
| Konuşma geçmişi | Assistant yanıtı + tool sonuçları tam geçmişe **eklenmeli**, tek başına gönderilmemeli |
| Anti-pattern'lar | Doğal dil ayrıştırma, keyfi iterasyon sınırı (birincil olarak), içerik türü kontrolü |
| İterasyon sınırı | Yalnızca güvenlik ağı — ulaşıldığında sessizce dönme, logla ve bildir |

---

## Pratik Senaryo 1

> Bir geliştirici, kullanıcıların konu araştırmasına yardımcı olan bir agent oluşturmuş. Agent'ın web arama aracına erişimi var. Geliştiricinin döngü mantığı, agent'ın ne zaman bitirdiğini belirlemek için `response.content[0].type == "text"` kontrolü yapıyor — metin bulursa döngüden çıkıyor ve yanıtı kullanıcıya sunuyor.
>
> Kullanıcılar, agent'ın sık sık eksik yanıtlar verdiğini bildiriyor — daha fazla araştırma yapması gerekirken genellikle tek bir aramadan sonra duruyor.
>
> **Hata nedir ve nasıl düzeltilmelidir?**

### Doğru Cevap

**Kök Neden:** Claude aynı yanıtta hem metin hem de `tool_use` blokları döndürebilir. Geliştiricinin mantığı `content[0].type == "text"` kontrolü yapıyor ve bunu bir tamamlanma sinyali olarak değerlendiriyor. Ancak Claude sıklıkla bir metin bloğu (örneğin, "Bazı ilk sonuçları buldum, daha fazla ayrıntı için arama yapayım") döndürürken *aynı anda* bir `tool_use` bloğu da döndürüyor. Döngü metni görüyor, agent'ın bitirdiğini varsayıyor ve erken çıkıyor — Claude hâlâ görevin ortasındayken bile.

**Düzeltme:**

`stop_reason` yanıt metninin içinde değildir. Yanıt nesnesinin üzerinde ayrı bir alandır:

- `response.content` → asıl içerik (metin blokları, tool_use blokları veya her ikisi — bir liste)
- `response.stop_reason` → Claude'un *neden üretmeyi durdurduğunu* söyleyen yapılandırılmış bir alan

```python
# YANLIŞ — güvenilmez, erken sonlandırmaya neden olur
if response.content[0].type == "text":
    return response

# DOĞRU — stop_reason birincil sinyaldir
if response.stop_reason == "end_turn":
    return response
elif response.stop_reason == "tool_use":
    # content listesinin TAMAMINDAKİ tool_use bloklarını çalıştır
    # tool_result bloklarını tek bir user mesajında geçmişe ekle
    # güncellenmiş konuşmayı Claude'a geri gönder
```

**Temel İlke:** `stop_reason`, yanıt metninin bir parçası değil, **yanıt nesnesi üzerindeki yapılandırılmış bir alandır**. Döngünün devam edip etmeyeceğini belirlemek için birincil mekanizmadır.

---

## Pratik Senaryo 2

> Bir agent, üç farklı bölgenin satış verisini karşılaştırmak için `query_sales` tool'unu kullanıyor. Claude tek bir yanıtta üç ayrı `tool_use` bloğu döndürüyor (her bölge için bir tane). Geliştiricinin kodu her tool sonucunu ayrı bir `{"role": "user", "content": [tool_result]}` mesajı olarak geçmişe ekliyor.
>
> API, ikinci istekte hata döndürüyor.
>
> **Sorun nedir?**
>
> **A)** Claude aynı anda yalnızca bir tool çağırabilir; `disable_parallel_tool_use` açık olmalıydı.
>
> **B)** Bir assistant yanıtındaki tüm `tool_use` bloklarının sonuçları, hemen sonraki **tek bir** user mesajında `tool_result` blokları olarak gönderilmelidir; ayrı mesajlara bölmek geçersiz bir konuşma yapısı oluşturur.
>
> **C)** `tool_result` blokları `assistant` rolüyle gönderilmeliydi.
>
> **D)** Üç sorgu sıralı yapılmalı; paralel tool çağrısı Messages API'de desteklenmez.

### Doğru Cevap: B

**Neden B doğru:** Kural açık — assistant turundaki her `tool_use` bloğu, bir sonraki user mesajında karşılık gelen `tool_result` bloğunu bulmalıdır. İlk user mesajı yalnızca bir sonucu içerdiğinden diğer iki `tool_use` bloğu karşılıksız kalır ve API isteği reddeder. Çözüm: üç `tool_result` bloğunu tek user mesajının `content` listesinde toplamak.

**Neden A yanlış:** Claude paralel tool çağrısı yapabilir; bu bir hata değil, özelliktir. `disable_parallel_tool_use` bunu kapatmak için var, ama buradaki sorun döngünün paralel çağrıyı yanlış işlemesi.

**Neden C yanlış:** `tool_result` blokları her zaman `user` rolüyle gönderilir. Rol doğru, mesaj yapısı yanlış.

**Neden D yanlış:** Paralel tool çağrısı Messages API'nin standart bir özelliğidir ve latency'yi azaltır. Sorunu çözmek için özelliği kapatmak değil, döngüyü doğru yazmak gerekir.
