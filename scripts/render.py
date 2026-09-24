import json, re, html, os, markdown
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD=lambda s: markdown.markdown(s, extensions=['fenced_code','tables'])
D=json.load(open(os.path.join(ROOT,"build","data.json"),encoding="utf-8"))
import sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from narration import narration_filename, discover_lessons
from flashcards import extract_flashcards
def narration_attrs(idx):
    attrs=[]
    fname=narration_filename(idx)
    for lang in ("en","tr"):
        if os.path.exists(os.path.join(ROOT,"dist","audio",lang,fname)):
            attrs.append(f'data-narration-{lang}="audio/{lang}/{fname}"')
    return (" "+" ".join(attrs)) if attrs else ""
EN_TITLE={1:"Agentic Architecture & Orchestration",2:"Tool Design & MCP Integration",3:"Claude Code Configuration & Workflows",4:"Prompt Engineering & Structured Output",5:"Context Management & Reliability"}
EN_DESC={1:"Agentic loops, multi-agent orchestration, subagent invocation and context passing, workflow enforcement and hooks, task decomposition, session state.",
2:"Tool interface design, structured error responses, tool distribution and tool_choice, MCP server integration, built-in tools.",
3:"CLAUDE.md hierarchy, custom slash commands and skills, path-specific rules, plan mode vs direct execution, iterative refinement, CI/CD integration.",
4:"Explicit criteria, few-shot prompting, structured output with tool_use, validation-retry loops, batch processing, multi-instance review.",
5:"Context preservation, escalation and ambiguity resolution, error propagation, codebase exploration, human review and confidence calibration, information provenance."}
EN_LTITLE={"1.3":"Subagent Invocation and Context Passing","1.4":"Workflow Enforcement and Handoff","1.5":"Agent SDK Hooks","1.6":"Task Decomposition Strategies","1.7":"Session State and Resumption","3.1":"CLAUDE.md Hierarchy","3.2":"Custom Slash Commands & Skills","3.6":"CI/CD Integration","4.2":"Few-Shot Prompting","4.3":"Structured Output with Tool_use","4.4":"Validation-Retry Loops"}
EN_LESSON_FILES={"1.1":"task_statement_1_1_agentic_loops.md","1.2":"task_statement_1_2_multi_agent_orchestration.md"}
NOTE_EN='<p class="langnote">English version of this section is not available yet — showing the Turkish text.</p>'
def en_title(tr_title):
    idx=tr_title.split(":")[0].strip()
    if idx in EN_LTITLE: return EN_LTITLE[idx]
    m=re.search(r'\(([^)]+)\)\s*$',tr_title)
    if m: return m.group(1)
    return tr_title.split(":",1)[1].strip()
import os
def en_lesson_body(idx,f_tr,tr_body):
    src=EN_LESSON_FILES.get(idx)
    if src is None and not f_tr.endswith("_TR.md"): return tr_body  # already English
    lp=os.path.join(ROOT,"content","en_lessons",f"{idx}.md")
    if src is None and os.path.exists(lp): return MD(open(lp,encoding="utf-8").read())
    if src is None: return NOTE_EN+tr_body
    t=open(P+src,encoding="utf-8").read()
    m=re.search(r'^# (.+)$',t,re.M); body=t[m.end():]
    body=re.sub(r'^\s*## Domain \d.*$','',body,count=1,flags=re.M)
    body=re.sub(r'^\s*---\s*$','',body,count=1,flags=re.M)
    return MD(body)
def bi(tr,en): return f'<span class="l-tr">{tr}</span><span class="l-en">{en}</span>'

P=os.path.join(ROOT,"content","tr")+os.sep
def intro(d):
    t=open(P+d["quiz"],encoding="utf-8").read()
    if d["fmt"]=="A":
        m=re.search(r'^## .*\n(.*?)^## (?:Question|Soru) 1',t,re.S|re.M); s=m.group(1)
    else:
        m=re.search(r'^## Genel Bilgiler\n(.*?)^## Sorular',t,re.S|re.M); s=m.group(1)
    s=re.sub(r'^---\s*$','',s,flags=re.M)
    return MD(s.strip())

def esc(s): return html.escape(s)
from en_content import SCEN_EN, SCEN_PAGE_EN, Q_EN
def en_q(key):
    e=Q_EN.get(key)
    if not e: return None
    return {"body":MD(e["body"]),"opts":{k:MD(v)[3:-4] for k,v in e["opts"].items()},"expl":MD(e["expl"])}
def bidiv(tr,en,cls=""):
    en_html = en if en is not None else NOTE_EN+tr
    return f'<div class="l-tr {cls}">{tr}</div><div class="l-en {cls}">{en_html}</div>'
def biopt(tr,en):
    return f'<span class="l-tr">{tr}</span><span class="l-en">{en if en is not None else tr}</span>'

for d in D:
    for q in d["questions"]:
        q["en"]=en_q(("base",d["id"],q["n"]))

QUESTION_POOL=json.load(open(os.path.join(ROOT,"content","question_pool.json"),encoding="utf-8"))
def qp_en(q):
    if not q["body_en"]: return None
    return {"body":MD(q["body_en"]),"opts":{k:MD(v)[3:-4] for k,v in q["opts_en"].items()},"expl":MD(q["expl_en"])}
POOL=[{"d":q["d"],"sc":q["sc"],"ts":q["ts"],"body":MD(q["body_tr"]),
       "opts":{k:MD(v)[3:-4] for k,v in q["opts_tr"].items()},"ans":q["ans"],
       "expl":MD(q["expl_tr"]),"en":qp_en(q)} for q in QUESTION_POOL]
POOL_JSON=json.dumps(POOL,ensure_ascii=False).replace("</script>","<\\/script>")

def _md1(s):
    return MD(s)[3:-4] if s else None
FLASHCARDS={}
for lesson in discover_lessons(os.path.join(ROOT,"content","en_lessons"),os.path.join(ROOT,"content","tr")):
    domain=int(lesson.id.split('.')[0])
    en_cards=extract_flashcards(open(lesson.en_path,encoding="utf-8").read()) if lesson.en_path else []
    tr_cards=extract_flashcards(open(lesson.tr_path,encoding="utf-8").read()) if lesson.tr_path else []
    deck=FLASHCARDS.setdefault(domain,[])
    for i in range(max(len(en_cards),len(tr_cards))):
        e=en_cards[i] if i<len(en_cards) else {}
        t=tr_cards[i] if i<len(tr_cards) else {}
        deck.append({"concept_tr":_md1(t.get("concept")),"remember_tr":_md1(t.get("remember")),
                     "concept_en":_md1(e.get("concept")),"remember_en":_md1(e.get("remember"))})
FLASHCARDS_JSON=json.dumps(FLASHCARDS,ensure_ascii=False).replace("</script>","<\\/script>")

SCEN=[
 {"id":1,"tr":"Customer Support Resolution Agent","en":"Customer Support Resolution Agent","doms":[1,2,5],
  "ctx":"Claude Agent SDK ile bir müşteri destek çözüm agent'ı kuruyorsun. Agent iade, fatura itirazı ve hesap sorunları gibi belirsizliği yüksek talepleri ele alıyor. Backend sistemlere özel MCP araçlarıyla erişiyor: <code>get_customer</code>, <code>lookup_order</code>, <code>process_refund</code>, <code>escalate_to_human</code>. Hedef: ne zaman eskalasyon yapılacağını bilerek %80+ ilk temasta çözüm.",
  "sig":[("1.1 Agentic loop","Döngü <code>stop_reason</code> ile yönetilir; \"final answer\" metni aramak, iterasyon tavanı ya da text-block kontrolü tuzaktır."),
         ("1.4 / 1.5 Zorlama ve hook'lar","Kimlik doğrulaması olmadan iade → prompt talimatı değil, programatik prerequisite gate. 500$ üzeri iade → tool call interception hook ile engelle ve insana yönlendir. Farklı MCP araçlarından gelen tarih/status formatları → PostToolUse hook ile normalize et."),
         ("2.1 / 2.2 Araç tasarımı","\"Hesap bilgilerini getirir\" gibi minimal açıklamalar misrouting yaratır → ilk adım açıklamayı zenginleştirmek. Hatalar <code>isError</code> + <code>errorCategory</code> + <code>isRetryable</code> ile yapılandırılır; iş kuralı hatası retry edilmez."),
         ("5.1 Bağlam koruma","Özetleme sırasında sipariş no/tutar/tarih kaybolur → kalıcı <em>case facts</em> bloğu; 45 alanlı araç sonuçlarını ilgili 5 alana kırp."),
         ("5.2 Eskalasyon","Geçerli tetikleyiciler: müşteri insan istiyor, politika boşluğu, ilerleme imkânsız. Duygu analizi ve öz-bildirilen güven skoru güvenilir değildir. Birden fazla müşteri eşleşmesi → ek tanımlayıcı iste, sezgisel seçme."),
         ("5.3 Boş sonuç vs erişim hatası","<code>status: success, results: []</code> geçerli bir cevaptır; retry gerekmez.")],
  "traps":["\"System prompt'a talimatı 3 kez yaz\" / \"daha büyük model\" — finansal riskte asla doğru cevap değil","Kızgın müşteriyi otomatik eskale etmek — duygu ≠ karmaşıklık","Handoff özetini transcript'e dayandırmak — insan temsilci transcript'i göremez, özet self-contained olmalı"]},
 {"id":2,"tr":"Code Generation with Claude Code","en":"Code Generation with Claude Code","doms":[3,5],
  "ctx":"Yazılım geliştirmeyi hızlandırmak için Claude Code kullanıyorsun. Takım onu kod üretimi, refactoring, debugging ve dokümantasyon için kullanıyor. Özel slash komutları, CLAUDE.md konfigürasyonları ile iş akışına entegre etmen ve plan modu ile doğrudan çalıştırma arasında ne zaman geçileceğini bilmen gerekiyor.",
  "sig":[("3.1 CLAUDE.md hiyerarşisi","Yeni takım üyesi kuralları almıyor → kural <code>~/.claude/CLAUDE.md</code>'de (kullanıcı seviyesi, paylaşılmaz); proje seviyesine taşı. Büyüyen dosya → <code>@import</code> veya <code>.claude/rules/</code>; <code>/memory</code> ile hangi dosyaların yüklendiğini doğrula."),
         ("3.2 Komutlar ve skill'ler","Takımla paylaşılacak komut → <code>.claude/commands/</code> (repo'da). Gürültülü çıktı üreten skill → <code>context: fork</code>; yıkıcı aksiyonları önlemek → <code>allowed-tools</code>; parametre isteme → <code>argument-hint</code>. Skill = isteğe bağlı iş akışı, CLAUDE.md = her zaman yüklü standart."),
         ("3.3 Yol-bazlı kurallar","Dağınık test dosyaları → <code>.claude/rules/</code> + <code>paths: [\"**/*.test.tsx\"]</code>; dizin CLAUDE.md tek dizine bağlıdır."),
         ("3.4 Plan modu","Mimari karar, çok dosyalı değişiklik, birden fazla geçerli yaklaşım → plan modu. Net stack trace'li tek dosya düzeltmesi → doğrudan çalıştırma. Gürültülü keşif → Explore subagent."),
         ("3.5 Yinelemeli iyileştirme","Düzyazı tutarsız yorumlanıyor → 2-3 somut before/after örneği. Test güdümlü iterasyon, mülakat deseni. Etkileşen sorunlar tek mesajda, bağımsız sorunlar sırayla."),
         ("1.7 / 5.4 Oturum yönetimi","Aynı temelden iki yaklaşım → <code>fork_session</code>; dosyalar değişmemişse resume; bayat bağlam → özet enjeksiyonlu yeni oturum; uzun keşifte scratchpad ve <code>/compact</code>.")],
  "traps":["Her şeyi kök CLAUDE.md'ye yığmak — token israfı ve tutarsızlık","Kişisel (<code>~/.claude</code>) konfigürasyonun takımla paylaşıldığını sanmak","Karmaşıklığı baştan belli olan işte \"önce doğrudan başla, gerekirse plana geç\""]},
 {"id":3,"tr":"Multi-Agent Research System","en":"Multi-Agent Research System","doms":[1,2,5],
  "ctx":"Claude Agent SDK ile çok agent'lı bir araştırma sistemi kuruyorsun. Bir coordinator agent, uzmanlaşmış subagent'lara delege ediyor: biri web'de arıyor, biri dokümanları analiz ediyor, biri bulguları sentezliyor, biri rapor üretiyor. Sistem konuları araştırıp kapsamlı, atıflı raporlar üretiyor.",
  "sig":[("1.2 Koordinasyon","Rapor bazı alt konuları hiç kapsamıyor ve subagent'lar tek başına iyi çalışıyor → coordinator'ın dar decomposition'ı. Hub-and-spoke: tüm iletişim coordinator üzerinden. Sentez çıktısındaki boşluklar için yinelemeli iyileştirme döngüsü."),
         ("1.3 Bağlam aktarımı","Subagent'lar coordinator'ın geçmişini miras almaz; bulgular prompt'a açıkça verilir. Atıf kaybını önlemek için içerik ve metadata (URL, doküman, sayfa) yapılandırılmış ayrılır. Paralel subagent = tek yanıtta birden fazla Task çağrısı; <code>allowedTools</code> \"Task\" içermeli."),
         ("2.3 Araç dağılımı","Agent başına 4-5 araç; 18 araç seçim güvenilirliğini düşürür. Sentez agent'ına tam web araması değil, kapsamlı <code>verify_fact</code> gibi kapsamlı-dar bir araç; karmaşık doğrulama coordinator üzerinden."),
         ("5.3 Hata yayılımı","Timeout → yapılandırılmış hata bağlamı (tür, denenen sorgu, kısmi sonuç, alternatif). Sessiz bastırma da tüm akışı durdurmak da anti-pattern. Transient hatalar subagent'ta yerel olarak çözülür."),
         ("5.1 / 5.6 Bağlam ve kaynak","Verbose subagent çıktısı sentez bütçesini tüketiyor → upstream agent'ı yapılandırılmış veri döndürecek şekilde değiştir. Çelişen istatistikler → ikisini de kaynak ve tarihle sun; zamansal fark çelişki değildir. Claim-source eşleştirmeleri sentezde korunur; kapsam boşlukları raporda açıkça belirtilir.")],
  "traps":["Downstream agent'ı suçlamak (sentez \"filtreledi\") — hatayı kaynağına izle","Subagent'lara tam konuşma geçmişi vermek — izolasyon ilkesini bozar","Çelişen veride \"en güncel olanı seç\" ya da \"ortalamasını al\""]},
 {"id":4,"tr":"Developer Productivity with Claude","en":"Developer Productivity with Claude","doms":[2,3,1],
  "ctx":"Claude Agent SDK ile geliştirici üretkenlik araçları kuruyorsun. Agent, mühendislerin tanımadıkları kod tabanlarını keşfetmesine, legacy sistemleri anlamasına, boilerplate üretmesine ve tekrarlayan işleri otomatikleştirmesine yardım ediyor. Yerleşik araçları (Read, Write, Bash, Grep, Glob) kullanıyor ve MCP sunucularıyla entegre.",
  "sig":[("2.5 Yerleşik araçlar","Grep = dosya <em>içeriği</em> (fonksiyon çağrıları, hata mesajları, importlar); Glob = dosya <em>yolları</em> (<code>**/*.test.tsx</code>). Edit benzersiz eşleşme ister; başarısızsa Read + Write. Kod tabanı artımlı keşfedilir: Grep ile giriş noktası, Read ile import takibi — hepsini önden okumak değil."),
         ("2.4 MCP entegrasyonu","Paylaşılan sunucu → <code>.mcp.json</code> + <code>${TOKEN}</code>; kişisel/deneysel → <code>~/.claude.json</code>. Keşif çağrılarını azaltmak için içerik katalogları MCP <em>resource</em> olarak sunulur. Agent yerleşik Grep'i MCP aracına tercih ediyorsa → MCP açıklamasını zenginleştir. Standart entegrasyon (Jira) için topluluk sunucusu, özel iş akışı için özel sunucu."),
         ("1.6 / 1.7 Ayrıştırma ve oturum","Açık uçlu görev (\"legacy koda test ekle\") → önce yapıyı haritala, yüksek etkili alanları bul, bağımlılıklar keşfedildikçe uyarlanan plan. Değişen dosyalarla resume → değişiklikleri bildir; kapsamlı değişiklik → özet enjeksiyonlu yeni oturum."),
         ("3.4 / 5.4 Keşif ve bağlam","Gürültülü keşif → Explore subagent. Uzun oturumda \"tipik desenler\"e kayma = bağlam bozulması → scratchpad, subagent delegasyonu, manifest ile çökme kurtarma.")],
  "traps":["Fonksiyon çağrılarını Glob ile aramak","Sabit prompt chaining'i açık uçlu araştırma görevine uygulamak","\"Daha büyük context window\" ile bağlam bozulmasını çözmeye çalışmak"]},
 {"id":5,"tr":"Claude Code for Continuous Integration","en":"Claude Code for Continuous Integration","doms":[3,4],
  "ctx":"Claude Code'u CI/CD pipeline'ına entegre ediyorsun. Sistem otomatik kod incelemesi yapıyor, test senaryoları üretiyor ve pull request'lere geri bildirim veriyor. Uygulanabilir geri bildirim üreten ve yanlış pozitifleri en aza indiren prompt'lar tasarlaman gerekiyor.",
  "sig":[("3.6 CI entegrasyonu","Pipeline askıda kalıyor → <code>-p</code> / <code>--print</code>. Makine-okunabilir bulgu → <code>--output-format json</code> + <code>--json-schema</code>. Yeniden çalıştırmada önceki bulguları ver, yalnızca yeni/açık sorunları raporlat. Mevcut test dosyalarını context'e ver; test standartlarını ve fixture'ları CLAUDE.md'de belgele."),
         ("4.1 Açık kriterler","\"Yorumlar doğru mu?\" değil, \"yorum, kodun davranışıyla çelişiyorsa işaretle\". \"Muhafazakâr ol\" işe yaramaz. Yüksek yanlış pozitifli kategori güveni zehirliyorsa geçici olarak kapat. Ciddiyet seviyeleri kod örnekleriyle tanımlanır."),
         ("4.2 Few-shot","Belirsiz durumlar için (eski yorum mu, yanlış yorum mu?) gerekçeli 2-4 örnek; format (konum, sorun, ciddiyet, öneri) örnekle gösterilir."),
         ("4.6 / 1.6 Çok geçişli inceleme","14+ dosyalık tek geçiş tutarsız → dosya başına geçiş + çapraz dosya bütünleştirme geçişi. Kodu üreten oturum kendi kodunu iyi inceleyemez → bağımsız inceleme instance'ı."),
         ("4.5 Batch API","Pre-merge kontrol bloklayıcı → senkron; gece/haftalık raporlar → batch (%50 tasarruf, 24 saat, SLA yok).")],
  "traps":["Yanlış pozitif için \"güven eşiğini yükselt\" — sorun kriter belirsizliği","Büyük PR'ı büyük context window'la tek geçişte incelemeye devam etmek","Bloklayıcı akışı batch'e taşımak"]},
 {"id":6,"tr":"Structured Data Extraction","en":"Structured Data Extraction","doms":[4,5],
  "ctx":"Claude ile yapılandırılmış veri çıkarım sistemi kuruyorsun. Sistem, yapılandırılmamış dokümanlardan bilgi çıkarıyor, çıktıyı JSON şemalarıyla doğruluyor ve yüksek doğruluk sağlıyor. Edge case'leri zarifçe ele almalı ve downstream sistemlerle entegre olmalı.",
  "sig":[("4.3 tool_use ile yapılandırılmış çıktı","Garantili şema uyumu için tool_use + JSON şema; sözdizimi hatası biter ama semantik hata (toplamlar tutmuyor) bitmez. Bilinmeyen belge türü, çoklu şema → <code>tool_choice: \"any\"</code>; belirli araç önce → isimli zorlama. Belgede olmayabilen alan → nullable (uydurmayı önler); genişletilebilir kategori → enum + <code>\"other\"</code> + detay."),
         ("4.4 Validation-retry","Retry'a belge + başarısız çıktı + spesifik hata eklenir. Format hataları retry ile düzelir; bilgi belgede yoksa retry işe yaramaz. <code>calculated_total</code> vs <code>stated_total</code>, <code>conflict_detected</code> ile öz-doğrulama."),
         ("4.2 Few-shot","Tablo / düz metin / iç içe liste gibi farklı düzenlerde boş çıkarım → düzen çeşitliliğini gösteren örnekler."),
         ("4.5 Batch","Büyük hacim, gecikmeye toleranslı → batch; başarısızları <code>custom_id</code> ile ayıkla, boyut aşanları parçala; büyük gönderim öncesi örnek sette prompt'u rafine et."),
         ("5.5 İnsan incelemesi","%96 genel doğruluk belge türü bazında zayıflığı gizleyebilir → tabakalı analiz. Güven eşikleri etiketli doğrulama setiyle kalibre edilir; yüksek güvenli çıktılar tabakalı rastgele örneklemeyle sürekli denetlenir. Düşük güven ve çelişkili kaynak → insan incelemesi.")],
  "traps":["Zorunlu alan + eksik bilgi → halüsinasyon; çözüm retry değil nullable alan","\"JSON geçerli, demek ki çıkarım doğru\" — semantik doğrulama ayrı","Sezgisel güven eşiği; etiketli veri olmadan otomasyona geçmek"]},
]
SCEN_JSON=json.dumps([{"id":x["id"],"tr":x["tr"],"en":x["en"],"doms":x["doms"],"ctx":x["ctx"]} for x in SCEN],ensure_ascii=False).replace("</script>","<\\/script>")
META_JSON=json.dumps({"weights":{d["id"]:d["weight"] for d in D},"hues":{d["id"]:d["hue"] for d in D},"titles_tr":{d["id"]:d["title"] for d in D},"titles_en":EN_TITLE},ensure_ascii=False)


home=[]
home.append('<section id="home" class="page">')
home.append(f'''<header class="hero">
<p class="kicker">{bi("Çalışma rehberi","Study guide")}</p>
<h1>Claude Certified Architect<br><span>Foundations</span></h1>
<p class="lede">{bi("Sınav beş alandan (domain) oluşur. Aşağıdaki şerit her alanın sınav içindeki ağırlığını gösterir; her alanın sayfasında önce dersler, ardından cevap anahtarlı yeterlilik testi yer alır.","The exam has five domains. The bar below shows each domain's weight in the exam; every domain page has the lessons first, followed by a practice quiz with answer key.")}</p>
</header>''')
home.append('<div class="weightbar" role="img" aria-label="Domain ağırlıkları">')
for d in D:
    home.append(f'<a href="#domain-{d["id"]}" class="seg" style="--c:{d["hue"]};flex:{d["weight"]}"><b>{bi(f"%{d['weight']}", f"{d['weight']}%")}</b><small>D{d["id"]}</small></a>')
home.append('</div>')
total_q=sum(len(d["questions"]) for d in D); total_l=sum(len(d["lessons_html"]) for d in D)
home.append(f'<p class="meta">{bi(f"{len(D)} domain · {total_l} task statement dersi · {total_q} pratik soru", f"{len(D)} domains · {total_l} task statement lessons · {total_q} practice questions")}</p>')
home.append(f'''<a class="scencta" href="#scenarios"><span class="scencta-t">{bi("Sınav senaryoları","Exam scenarios")}</span><span class="scencta-s">{bi("6 senaryodan 4'ü rastgele seçilir; hangi domain hangi bağlamda sorulur?","4 of 6 are drawn at random; which domain is asked in which context?")}</span><span class="scencta-go">→</span></a>''')
home.append(f'''<a class="mockcta" href="#practice">
<span class="mockcta-t">{bi("Practice","Practice")}</span>
<span class="mockcta-s">{bi("Quick Mock, Full-Length Mock veya Flashcards ile çalış","Study with Quick Mock, Full-Length Mock, or Flashcards")}</span>
<span class="mockcta-go">→</span></a>''')
home.append(f'''<a class="regcta" href="https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification" target="_blank" rel="noopener">{bi("Sınava register olmak için","Register for the exam")} <span>→</span></a>''')
home.append('<ol class="domains">')
for d in D:
    home.append(f'''<li class="drow" style="--c:{d["hue"]}">
<div class="dnum">{d["id"]}</div>
<div class="dbody">
 <h2><a href="#domain-{d["id"]}">{bi(esc(d["title"]),EN_TITLE[d["id"]])}</a></h2>
 <p>{bi(esc(d["desc"]),EN_DESC[d["id"]])}</p>
 <p class="dfacts">{bi(f'Ağırlık %{d["weight"]} · {len(d["lessons_html"])} ders · {len(d["questions"])} soru', f'Weight {d["weight"]}% · {len(d["lessons_html"])} lessons · {len(d["questions"])} questions')}</p>
</div>
<a class="plus" href="#domain-{d["id"]}" aria-label="Domain {d["id"]} sayfasına git">+</a>
</li>''')
home.append('</ol></section>')

pages=[]
for d in D:
    p=[f'<section id="domain-{d["id"]}" class="page domain" style="--c:{d["hue"]}">']
    p.append(f'''<header class="dhead">
<a class="back" href="#home">{bi("← Tüm alanlar","← All domains")}</a>
<p class="kicker">{bi(f"Domain {d['id']} · Sınavın %{d['weight']}'" + {27:"si",18:"i",20:"si",15:"i"}[d["weight"]], f"Domain {d['id']} · {d['weight']}% of the exam")}</p>
<h1>{bi(esc(d["title"]),EN_TITLE[d["id"]])}</h1>
<p class="lede">{bi(esc(d["desc"]),EN_DESC[d["id"]])}</p>
<nav class="jump"><a href="#domain-{d["id"]}-lessons">{bi("Dersler","Lessons")}</a><a href="#domain-{d["id"]}-quiz">{bi("Yeterlilik testi","Practice quiz")}</a></nav>
</header>''')
    p.append(f'<h2 class="secttl" id="domain-{d["id"]}-lessons">{bi("Dersler","Lessons")}</h2>')
    p.append('<div class="lessons">')
    for i,(title,body) in enumerate(d["lessons_html"]):
        idx=title.split(":")[0].strip(); f_tr=d["lessons"][i]
        tr_t=esc(title.split(":",1)[1].strip()) if ":" in title else esc(title)
        en_b=en_lesson_body(idx,f_tr,body)
        p.append(f'<details class="lesson" data-lesson-id="{idx}"{narration_attrs(idx)}><summary><span class="lidx">{idx}</span><span class="ltitle">{bi(tr_t,esc(en_title(title)))}</span></summary><div class="narration-controls" hidden><button type="button" class="nc-restart" aria-label="Restart">⏮</button><span class="nc-time nc-current">0:00</span><input type="range" class="nc-seek" min="0" max="0" step="1" value="0"><span class="nc-time nc-duration">0:00</span><button type="button" class="nc-end" aria-label="Skip to end">⏭</button><button type="button" class="nc-speed" aria-label="Playback speed">1x</button></div><div class="prose l-tr">{body}</div><div class="prose l-en">{en_b}</div></details>')
    p.append('</div>')
    p.append(f'<h2 class="secttl" id="domain-{d["id"]}-quiz">{bi("Yeterlilik testi","Practice quiz")}</h2>')
    allen=all(q.get("en") for q in d["questions"])
    p.append(f'<div class="prose qintro">{"" if allen else f"<div class=\"l-en\">{NOTE_EN}</div>"}{intro(d)}</div>')
    p.append(f'<div class="quiz" data-domain="{d["id"]}">')
    for q in d["questions"]:
        e=q.get("en")
        p.append(f'<article class="q" data-ans="{q["ans"]}"><div class="qhead"><span class="qn">{bi(f"Soru {q['n']}",f"Question {q['n']}")}</span><span class="qts">{esc(q["ts"])}</span></div><div class="prose qbody">{bidiv(q["body"], e["body"] if e else None)}</div><div class="opts">')
        for k in "ABCD":
            p.append(f'<button class="opt" data-k="{k}"><span class="k">{k}</span><span class="t">{biopt(MD(q["opts"][k])[3:-4], e["opts"][k] if e else None)}</span></button>')
        p.append(f'</div><div class="verdict"></div><div class="expl prose"><div class="explhd">{bi("Doğru cevap","Correct answer")}: <b>{q["ans"]}</b></div>{bidiv(q["expl"], e["expl"] if e else None)}</div></article>')
    p.append(f'<div class="score"><span class="scoretxt"></span><button class="reset">{bi("Testi sıfırla","Reset quiz")}</button></div>')
    p.append('</div>')
    p.append(f'<p class="pagenav"><a href="#home">{bi("← Tüm alanlar","← All domains")}</a>' + (f'<a href="#domain-{d["id"]+1}">Domain {d["id"]+1} →</a>' if d["id"]<5 else '') + '</p>')
    p.append('</section>')
    pages.append('\n'.join(p))

practice=f'''<section id="practice" class="page practice">
<a class="back" href="#home">{bi("← Ana sayfa","← Home")}</a>
<p class="kicker">{bi("Çalışma","Study")}</p>
<h1>Practice</h1>
<p class="lede">{bi("Zamana göre bir çalışma modu seç: hızlı bir kontrol, gerçek sınav koşullarında tam deneme, ya da kavramları hızlı tekrar için flashcard'lar.","Pick a study mode that fits your time: a quick check, a full-length attempt under real exam conditions, or flashcards for fast concept review.")}</p>
<div class="practice-cards">
<a class="practice-card" href="#quick-mock"><h2>Quick Mock</h2><p>{bi("24 soru · 2 dk/soru · ~48 dk","24 questions · 2 min/question · ~48 min")}</p></a>
<a class="practice-card" href="#full-length-mock"><h2>Full-Length Mock</h2><p>{bi("60 soru · 2 dk/soru · gerçek sınav koşulları","60 questions · 2 min/question · real exam conditions")}</p></a>
<a class="practice-card" href="#flashcards"><h2>Flashcards</h2><p>{bi("Domain başına kavram kartları","Concept cards per Domain")}</p></a>
</div>
</section>'''
pages.append(practice)

quickmock=f'''<section id="quick-mock" class="page mock">
<a class="back" href="#practice">{bi("← Practice","← Practice")}</a>
<p class="kicker">{bi("Hızlı kontrol","Quick check")}</p>
<h1>Quick Mock</h1>
<p class="lede">{bi("Gerçek sınavdaki gibi 6 senaryodan 4'ü rastgele seçilir, sorular senaryo altında gruplanır. Kısa süreli, hedefli bir ilerleme kontrolü için.","Just like the real exam, 4 of 6 Scenarios are drawn at random and questions are grouped by Scenario. A short, focused progress check.")}</p>
<table class="rules"><tbody>
<tr><th>{bi("Senaryolar","Scenarios")}</th><td>{bi("6 senaryodan rastgele 4'ü; her senaryonun soruları birlikte sunulur","4 of 6 drawn at random; each scenario's questions are presented together")}</td></tr>
<tr><th>{bi("Soru sayısı","Questions")}</th><td>{bi("24 soru, domain ağırlığına göre dağıtılır (yaklaşık 7/4/5/5/3)","24 questions, distributed by domain weight (roughly 7/4/5/5/3)")}</td></tr>
<tr><th>{bi("Süre","Time limit")}</th><td>{bi("Soru başına 2 dakika — toplam ~48 dakika; süre dolunca otomatik teslim","2 minutes per question — ~48 minutes total; auto-submits when time is up")}</td></tr>
<tr><th>{bi("Puanlama","Scoring")}</th><td>{bi("Domain ağırlıklı, 100–1000 ölçeği; geçme 720","Domain-weighted, 100–1000 scale; pass at 720")}</td></tr>
<tr><th>{bi("Sıra","Order")}</th><td>{bi("Soru sırası ve her sorunun şık sırası her denemede karışır","Question order and each question's answer-option order are shuffled every attempt")}</td></tr>
</tbody></table>
<button class="bigbtn" id="quick-start">{bi("Sınava başla","Start exam")}</button>
<div id="quick-history"></div>
</section>'''
pages.append(quickmock)

fullmock=f'''<section id="full-length-mock" class="page mock">
<a class="back" href="#practice">{bi("← Practice","← Practice")}</a>
<p class="kicker">{bi("Gerçek sınav koşulları","Real exam conditions")}</p>
<h1>Full-Length Mock</h1>
<p class="lede">{bi("Gerçek sınav formatı: 6 senaryodan 4'ü rastgele seçilir, sorular senaryo altında gruplanır, puan domain ağırlıklı. Tam süreli, gerçek sınav simülasyonu.","Real exam format: 4 of 6 Scenarios are drawn at random and questions are grouped by Scenario, scoring is domain-weighted. A full-length, real exam simulation.")}</p>
<table class="rules"><tbody>
<tr><th>{bi("Senaryolar","Scenarios")}</th><td>{bi("6 senaryodan rastgele 4'ü; her senaryonun soruları birlikte sunulur","4 of 6 drawn at random; each scenario's questions are presented together")}</td></tr>
<tr><th>{bi("Soru sayısı","Questions")}</th><td>{bi("60 soru, domain ağırlığına göre dağıtılır (yaklaşık 16/11/12/12/9)","60 questions, distributed by domain weight (roughly 16/11/12/12/9)")}</td></tr>
<tr><th>{bi("Süre","Time limit")}</th><td>{bi("Soru başına 2 dakika — toplam ~120 dakika; süre dolunca otomatik teslim","2 minutes per question — ~120 minutes total; auto-submits when time is up")}</td></tr>
<tr><th>{bi("Puanlama","Scoring")}</th><td>{bi("Domain ağırlıklı, 100–1000 ölçeği; geçme 720","Domain-weighted, 100–1000 scale; pass at 720")}</td></tr>
<tr><th>{bi("Sıra","Order")}</th><td>{bi("Soru sırası ve her sorunun şık sırası her denemede karışır","Question order and each question's answer-option order are shuffled every attempt")}</td></tr>
</tbody></table>
<button class="bigbtn" id="full-start">{bi("Sınava başla","Start exam")}</button>
<div id="full-history"></div>
</section>'''
pages.append(fullmock)

fc_domain_cards=''
for d in D:
    n=len(FLASHCARDS.get(d["id"],[]))
    fc_domain_cards+=f'''<button type="button" class="practice-card fc-domain-card" data-domain="{d["id"]}" style="--c:{d["hue"]}">
<h2>{bi(f'Domain {d["id"]}',f'Domain {d["id"]}')} — {bi(esc(d["title"]),EN_TITLE[d["id"]])}</h2>
<p>{bi(f"{n} kart",f"{n} cards")}</p>
</button>'''

pages.append(f'''<section id="flashcards" class="page">
<a class="back" href="#practice">{bi("← Practice","← Practice")}</a>
<div id="fc-picker">
<p class="kicker">{bi("Hızlı tekrar","Quick review")}</p>
<h1>Flashcards</h1>
<p class="lede">{bi("Bir domain seç; o domain'deki derslerin temel çıkarımlarını kart kart tekrar et.","Pick a Domain; review that Domain's Lessons' key takeaways one card at a time.")}</p>
<div class="practice-cards" id="fc-domain-list">{fc_domain_cards}</div>
</div>
<div id="fc-deck" hidden>
<button type="button" class="back" id="fc-back">{bi("← Flashcards","← Flashcards")}</button>
<p class="kicker" id="fc-domain-title"></p>
<div class="flashcard" id="fc-card" tabindex="0" role="button">
<div class="fc-inner">
<div class="fc-face fc-front"></div>
<div class="fc-face fc-back"></div>
</div>
</div>
<p class="fc-hint">{bi("Çevirmek için karta dokun","Tap the card to flip it")}</p>
<div class="fc-nav">
<button type="button" class="reset" id="fc-prev">←</button>
<span id="fc-progress"></span>
<button type="button" class="reset" id="fc-next">→</button>
</div>
</div>
</section>''')

examrunner=f'''<section id="practice-exam" class="page mock">
<div id="mock-exam">
<div class="exambar"><span id="mock-progress"></span><span id="mock-timer"></span><button class="reset" id="mock-finish">{bi("Sınavı bitir","Finish exam")}</button></div>
<details class="scenbox" id="mock-scen"><summary></summary><p></p></details>
<div id="mock-q"></div>
<div class="examnav"><button class="reset" id="mock-prev">←</button><button class="reset" id="mock-flag"></button><button class="reset" id="mock-next">→</button></div>
<div class="palette" id="mock-palette"></div>
</div>
<div id="mock-result" hidden></div>
</section>'''
pages.append(examrunner)
SEL_TR='''<p>Resmi kılavuzun tanımı şu: sınav senaryo tabanlı sorular kullanır; her senaryo, bir dizi soruyu çerçeveleyen gerçekçi bir üretim bağlamı sunar ve sınav sırasında <strong>6 senaryoluk havuzdan rastgele 4'ü</strong> sunulur. Yani:</p>
<ul>
<li>Sorular bağımsız birer bilgi sorusu değildir; "şu sistemi kuruyorsun" diye başlayan bir senaryo metninin altında gelir ve o senaryonun araç adları, hedef metrikleri ve kısıtları soru gövdesine gömülüdür.</li>
<li>60 soru 4 senaryoya dağılır (senaryo başına yaklaşık 15 soru). Hangi 4 senaryonun geleceği önceden bilinemez; altısına da hazır olmak gerekir.</li>
<li>Domain ağırlıkları (%27 / 18 / 20 / 20 / 15) sabittir; her sınav formunda korunur. Değişen şey, aynı domain'in <em>hangi bağlamda</em> sorulduğudur.</li>
<li>Puan 100–1000 ölçeğinde ve domain ağırlıklı hesaplanır; geçme 720. Ölçekli puanlama, farklı zorluktaki formları eşitlemek içindir — senaryo karışımı formdan forma değişse de eşik aynıdır.</li>
</ul>'''
MAPNOTES_TR='''<p>Haritadan çıkan pratik sonuçlar:</p><ul>
<li><strong>Domain 5</strong> dört senaryoda birincil; hangi 4 senaryo gelirse gelsin geniş bağlam çeşitliliğiyle sorulur.</li>
<li><strong>Domain 4</strong> yalnızca senaryo 5 ve 6'da birincil. Senaryo 6 gelmezse Domain 4'ün 12 sorusu ağırlıkla CI/CD bağlamından (inceleme kriterleri, yanlış pozitif, çok geçişli inceleme, batch) gelir; Senaryo 5 gelmezse çıkarım bağlamından (nullable alan, validation-retry, doküman çeşitliliği için few-shot).</li>
<li><strong>Domain 1</strong>'in 16 sorusu senaryo 1, 3 ve 4'ten; <strong>Domain 3</strong>'ün 12 sorusu senaryo 2, 4 ve 5'ten; <strong>Domain 2</strong>'nin 11 sorusu senaryo 1, 3 ve 4'ten gelir.</li>
<li>Senaryo 4 (Developer Productivity) üç domain'e birden köprü kurar — yerleşik araçlar, MCP ve oturum yönetimi aynı senaryoda iç içe sorulur.</li>
</ul>'''
IMPACT_TR='''<p><strong>1. Her senaryonun "imza" karar kalıpları vardır.</strong> Aynı task statement farklı senaryolarda farklı yüzle gelir. Örneğin 1.4 (zorlama) müşteri destek senaryosunda "kimlik doğrulaması olmadan iade" olarak, CI senaryosunda ise "agent merge yapmaya çalışıyor" olarak karşına çıkar; cevap ilkesi aynı (deterministik zorlama), yüzeyi farklı.</p>
<p><strong>2. Soru kalıbı senaryodan beslenir.</strong> Kılavuzdaki örnek soruların tipik yapısı: <em>"Üretim logları/verisi şunu gösteriyor … en etkili ilk adım / kök neden hangisi?"</em> Dört seçenek de o senaryonun içinden gelir ve hepsi "işe yarayabilir" görünür. Doğru olan, kök nedeni hedefleyen ve <em>orantılı</em> olandır: açıklamayı düzeltmek classifier eklemekten, nullable alan retry döngüsünden, prerequisite gate prompt talimatından önce gelir.</p>
<p><strong>3. Çeldiriciler de senaryoya özgüdür.</strong> Yüksek riskli senaryolarda (finans, compliance, üretim veritabanı) "prompt'a talimat ekle", "daha büyük model", "daha büyük context window", "classifier ekle", "her şeyi insana yönlendir" seçenekleri neredeyse her zaman tuzaktır. Kılavuz bunu açıkça söyler: prompt tabanlı uyum olasılıksaldır, finansal sonuç varsa yetmez.</p>
<p><strong>4. Bir senaryonun soruları birbirini besler.</strong> Aynı senaryo altında art arda gelen sorular aynı araç setini ve aynı hedef metriği paylaşır. Senaryo metnini bir kez dikkatle okumak (hangi araçlar var, hedef ne, hangi kısıt var) sonraki 15 sorunun her birinde zaman kazandırır — soru gövdesinde tekrar edilmeyen bilgi senaryo metnindedir.</p>
<p><strong>5. Hazırlık stratejisi:</strong> Domain bazlı çalışmayı senaryo bazlı tekrarla tamamla. Her senaryo için araç setini, hedef metriği, tipik arıza modlarını ve bunlara karşılık gelen doğru mimari kararı bir sayfada toparla; aşağıdaki kartlar bu amaçla hazırlandı. Sınav gününde senaryoyu tanıdığın an, hangi task statement'ların geleceğini büyük ölçüde öngörebilirsin.</p>'''
def scen_page():
    E=SCEN_PAGE_EN
    counts={x["id"]:{} for x in SCEN}
    for q in POOL: counts[q["sc"]][q["d"]]=counts[q["sc"]].get(q["d"],0)+1
    p=[f'''<section id="scenarios" class="page scen">
<a class="back" href="#home">{bi("← Ana sayfa","← Home")}</a>
<p class="kicker">{bi("Resmi sınav kılavuzuna göre","According to the official exam guide")}</p>
<h1>{bi("Sınav senaryoları","Exam scenarios")}</h1>
<p class="lede">{bi("Sınavdaki her soru, gerçek bir müşteri kullanım örneğinden türetilmiş bir senaryonun altında sorulur. Altı senaryo vardır; her sınav oturumunda bunlardan dördü rastgele seçilir.","Every exam question sits under a scenario derived from a real customer use case. There are six scenarios; each sitting draws four of them at random.")}</p>
<h2 class="secttl">{bi("Senaryo seçimi nasıl yapılır?",E["h_sel"])}</h2>
<div class="prose scenprose">{bidiv(SEL_TR,E["sel"])}</div>
<h2 class="secttl">{bi("Senaryo × domain haritası",E["h_map"])}</h2>
<div class="prose">{bidiv("<p>Her senaryonun kılavuzda belirtilen <strong>birincil domain&#39;leri</strong> (●) ve bu rehberdeki mock havuzunda o senaryoya bağlı soru sayıları:</p>",E["map_intro"])}</div>
<div class="matrixwrap"><table class="matrix"><thead><tr><th>{bi("Senaryo","Scenario")}</th>''']
    for d in D: p.append(f'<th style="--c:{d["hue"]}"><span>D{d["id"]}</span><small>{bi("%"+str(d["weight"]),str(d["weight"])+"%")}</small></th>')
    p.append(f'<th>{bi("Toplam","Total")}</th></tr></thead><tbody>')
    for x in SCEN:
        p.append(f'<tr><th><a href="#scen-{x["id"]}">{x["id"]}. {x["tr"]}</a></th>')
        for d in D:
            n=counts[x["id"]].get(d["id"],0); prim=d["id"] in x["doms"]
            p.append(f'<td class="{"prim" if prim else ""}" style="--c:{d["hue"]}">{"●" if prim else ""}{(" "+str(n)) if n else ""}</td>')
        p.append(f'<td><b>{sum(counts[x["id"]].values())}</b></td></tr>')
    p.append('</tbody></table></div>')
    p.append(f'<div class="prose scenprose">{bidiv(MAPNOTES_TR,E["map_notes"])}</div>')
    p.append(f'<h2 class="secttl">{bi("Bu durum soruları nasıl etkiler?",E["h_impact"])}</h2>')
    p.append(f'<div class="prose scenprose">{bidiv(IMPACT_TR,E["impact"])}</div>')
    p.append(f'<h2 class="secttl">{bi("Altı senaryo",E["h_six"])}</h2>')
    for x in SCEN:
        n=sum(counts[x["id"]].values()); xe=SCEN_EN[x["id"]]
        doms_tr=" · ".join(f'<span style="--c:{D[d-1]["hue"]}">D{d} {D[d-1]["title"]}</span>' for d in x["doms"])
        doms_en=" · ".join(f'<span style="--c:{D[d-1]["hue"]}">D{d} {EN_TITLE[d]}</span>' for d in x["doms"])
        p.append(f'<article class="scard" id="scen-{x["id"]}"><div class="shead"><span class="snum">{x["id"]}</span><div><h3>{x["tr"]}</h3><p class="sdoms">{bi("Birincil domain&#39;ler: "+doms_tr, E["prim"]+": "+doms_en)}</p></div></div>')
        def card(ctx,sig,traps,lbl,hs,ht,pool):
            return (f'<p class="sctx"><strong>{lbl}</strong> {ctx}</p><h4>{hs}</h4><dl class="sig">'+"".join(f'<dt>{a}</dt><dd>{b}</dd>' for a,b in sig)+f'</dl><h4>{ht}</h4><ul>'+"".join(f'<li>{t}</li>' for t in traps)+f'</ul><p class="sfacts">{pool}</p>')
        tr_card=card(x["ctx"],x["sig"],x["traps"],"Bağlam (kılavuzdan):","Bu senaryoda tipik olarak sınanan kararlar","Sık düşülen tuzaklar",f"Mock havuzunda bu senaryoya bağlı {n} soru var.")
        en_card=card(xe["ctx"],xe["sig"],xe["traps"],E["ctx_lbl"],E["h_sig"],E["h_traps"],E["pool"].format(n=n))
        p.append(f'<div class="prose">{bidiv(tr_card,en_card)}</div></article>')
    p.append(f'<p class="pagenav"><a href="#home">{bi("← Ana sayfa","← Home")}</a><a href="#practice">{bi("Practice →","Practice →")}</a></p></section>')
    return "\n".join(p)
pages.append(scen_page())
css=open(os.path.join(ROOT,"src","style.css"),encoding="utf-8").read(); js=open(os.path.join(ROOT,"src","app.js"),encoding="utf-8").read()
narration_js=open(os.path.join(ROOT,"src","narration-player.js"),encoding="utf-8").read()
mock_builder_js=open(os.path.join(ROOT,"src","mock-builder.js"),encoding="utf-8").read()
doc=f'''<!DOCTYPE html>
<html lang="tr" data-lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Claude Certified Architect (Foundations) — Çalışma Rehberi</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<button class="langtoggle" id="langtoggle" aria-label="Dil / Language"><span data-l="tr">TR</span><span data-l="en">EN</span></button>
<div class="wrap">
{''.join(home)}
{''.join(pages)}
<footer class="foot">{bi(f"Claude Certified Architect (Foundations) çalışma notları · {len(D)} domain · {total_q} soru", f"Claude Certified Architect (Foundations) study notes · {len(D)} domains · {total_q} questions")}</footer>
</div>
<script>var MOCK_POOL={POOL_JSON};var MOCK_META={META_JSON};var MOCK_SCEN={SCEN_JSON};var FLASHCARDS={FLASHCARDS_JSON};</script>\n<script>{narration_js}</script>\n<script>{mock_builder_js}</script>\n<script>{js}</script>
</body></html>'''
OUT=os.path.join(ROOT,"dist","index.html")
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,"w",encoding="utf-8").write(doc)
print("written",OUT)
print(len(doc)//1024,"KB")
