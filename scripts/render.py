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
total_q=sum(len(d["questions"]) for d in D); total_l=sum(len(d["lessons_html"]) for d in D)
home.append('<section id="home" class="page">')
home.append(f'''<header class="hero">
<div class="hero-copy">
<p class="kicker">{bi("Çalışma rehberi","Study guide")}</p>
<h1>Claude Certified Architect<br><span>Foundations</span></h1>
<p class="lede">{bi("Sınav beş alandan (domain) oluşur. Aşağıdaki şerit her alanın sınav içindeki ağırlığını gösterir; her alanın sayfasında önce dersler, ardından cevap anahtarlı yeterlilik testi yer alır.","The exam has five domains. The bar below shows each domain's weight in the exam; every domain page has the lessons first, followed by a practice quiz with answer key.")}</p>
</div>
<div class="statcells">
<div class="statcell"><b>{len(D)}</b><small>{bi("domain","domains")}</small></div>
<div class="statcell"><b>{total_l}</b><small>{bi("ders","lessons")}</small></div>
<div class="statcell"><b>{total_q}</b><small>{bi("soru","questions")}</small></div>
</div>
</header>''')
home.append('<div class="weightbar" role="img" aria-label="Domain ağırlıkları">')
for d in D:
    home.append(f'<a href="#domain-{d["id"]}" class="seg" style="--c:{d["hue"]};flex:{d["weight"]}"><b>{bi(f"%{d['weight']}", f"{d['weight']}%")}</b><small>D{d["id"]}</small></a>')
home.append('</div>')
home.append(f'<p class="meta">{bi(f"{len(D)} domain · {total_l} task statement dersi · {total_q} pratik soru", f"{len(D)} domains · {total_l} task statement lessons · {total_q} practice questions")}</p>')
home.append('<div class="action-cards">')
home.append(f'''<a class="action-card ac-guide" href="#exam-guide"><span class="ac-t">Claude Certified Architect – Foundations Exam Guide<span class="ac-go">→</span></span><span class="ac-s">{bi("Anthropic'in resmi sınav kılavuzu.","Official exam guide from Anthropic.")}</span></a>''')
home.append(f'''<a class="action-card ac-scenarios" href="#scenarios"><span class="ac-t">{bi("Sınav senaryoları","Exam scenarios")}<span class="ac-go">→</span></span><span class="ac-s">{bi("6 senaryodan 4'ü rastgele seçilir; hangi domain hangi bağlamda sorulur?","4 of 6 are drawn at random; which domain is asked in which context?")}</span></a>''')
home.append(f'''<a class="action-card ac-practice" href="#practice"><span class="ac-t">Practice<span class="ac-go">→</span></span><span class="ac-s">{bi("Quick Mock, Full-Length Mock veya Flashcards ile çalış","Study with Quick Mock, Full-Length Mock, or Flashcards")}</span></a>''')
home.append('</div>')
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
<p class="kicker dkicker"><span class="ddot"></span>{bi(f"Domain {d['id']} · Sınavın %{d['weight']}'" + {27:"si",18:"i",20:"si",15:"i"}[d["weight"]], f"Domain {d['id']} · {d['weight']}% of the exam")}</p>
<h1>{bi(esc(d["title"]),EN_TITLE[d["id"]])}</h1>
<p class="lede">{bi(esc(d["desc"]),EN_DESC[d["id"]])}</p>
<nav class="segctl"><a href="#domain-{d["id"]}-lessons">{bi(f"Dersler · {len(d['lessons_html'])}", f"Lessons · {len(d['lessons_html'])}")}</a><a href="#domain-{d["id"]}-quiz">{bi(f"Yeterlilik testi · {len(d['questions'])}", f"Practice quiz · {len(d['questions'])}")}</a></nav>
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
<a class="practice-card" href="#quick-mock"><h2>Quick Mock<span class="ac-go">→</span></h2><p>{bi("24 soru · 2 dk/soru · ~48 dk","24 questions · 2 min/question · ~48 min")}</p></a>
<a class="practice-card primary" href="#full-length-mock"><h2>Full-Length Mock<span class="ac-go">→</span></h2><p>{bi("60 soru · 2 dk/soru · gerçek sınav koşulları","60 questions · 2 min/question · real exam conditions")}</p></a>
<a class="practice-card" href="#flashcards"><h2>Flashcards<span class="ac-go">→</span></h2><p>{bi("Domain başına kavram kartları","Concept cards per Domain")}</p></a>
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
    fc_domain_cards+=f'''<button type="button" class="fc-domain-card" data-domain="{d["id"]}" style="--c:{d["hue"]}">
<span class="fcd-top"><span class="fcd-badge">{d["id"]}</span><span class="fcd-count">{bi(f"{n} kart",f"{n} cards")}</span></span>
<span class="fcd-title">{bi(esc(d["title"]),EN_TITLE[d["id"]])}</span>
<span class="fcd-bar"></span>
</button>'''

pages.append(f'''<section id="flashcards" class="page fcpage">
<a class="back" href="#practice">{bi("← Practice","← Practice")}</a>
<p class="kicker">{bi("Practice · Flashcards","Practice · Flashcards")}</p>
<h1>Flashcards</h1>
<p class="lede">{bi("Bir domain seç; o domain'deki derslerin temel çıkarımlarını kart kart tekrar et.","Pick a Domain; review that Domain's Lessons' key takeaways one card at a time.")}</p>
<div class="fc-domains" id="fc-domain-list">{fc_domain_cards}</div>
<div class="flashcard" id="fc-card" tabindex="0" role="button">
<div class="fc-inner">
<div class="fc-face fc-front">
<span class="fc-row fc-head"><span class="fc-meta" id="fc-meta-q"></span><span class="fc-tag">{bi("SORU","QUESTION")}</span></span>
<span class="fc-body" id="fc-q"></span>
<span class="fc-row fc-foot"><span id="fc-progress"></span><span class="fc-hint">{bi("Çevirmek için dokun","Tap to flip")}</span></span>
</div>
<div class="fc-face fc-back">
<span class="fc-row fc-head"><span class="fc-meta" id="fc-meta-a"></span><span class="fc-tag">{bi("CEVAP","ANSWER")}</span></span>
<span class="fc-body" id="fc-a"></span>
<span class="fc-row fc-foot"><span id="fc-progress2"></span><span class="fc-hint">{bi("Çevirmek için dokun","Tap to flip")}</span></span>
</div>
</div>
</div>
<div class="fc-nav">
<button type="button" class="fc-btn fc-prev" id="fc-prev">← {bi("Önceki","Previous")}</button>
<button type="button" class="fc-btn fc-shuffle" id="fc-shuffle">{bi("Karıştır","Shuffle")}</button>
<button type="button" class="fc-btn fc-next" id="fc-next">{bi("Sonraki","Next")} →</button>
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

REG_URL="https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification"

eg_about_tr='''<p>Claude Certified Architect – Foundations sertifikası, pratisyenlerin Claude ile gerçek dünya
çözümleri uygularken doğru tradeoff kararları verebildiğini doğrular. Bu sınav, Claude ile production
seviyesinde uygulamalar geliştirmek için kullanılan temel teknolojiler olan Claude Code, Claude Agent
SDK, Claude API ve Model Context Protocol (MCP) genelinde temel bilgiyi test eder.</p>
<p>Sınavdaki sorular; müşteri destek için agentic sistemler kurma, çoklu agent araştırma pipeline'ları
tasarlama, Claude Code'u CI/CD iş akışlarına entegre etme, geliştirici verimlilik araçları inşa etme ve
yapılandırılmamış dokümanlardan yapılandırılmış veri çıkarma gibi gerçek müşteri kullanım
senaryolarından alınan gerçekçi senaryolara dayanır. Adaylar sadece kavramsal bilgi değil, production
ortamlarındaki mimari, konfigürasyon ve tradeoff kararlarında pratik muhakeme de göstermelidir.</p>
<p>Bu kılavuz, sınava hazırlanan adaylar için yetkili referans kaynağıdır. Sınav içeriğini açıklar, test
edilen domain ve task statement'ları listeler, örnek sorular sunar ve hazırlık stratejileri önerir. Sınavı
planlamadan önce baştan sona okuyun.</p>'''

eg_about_en='''<p>The Claude Certified Architect – Foundations certification validates that practitioners can make
informed decisions about tradeoffs when implementing real-world solutions with Claude. This exam
tests foundational knowledge across Claude Code, the Claude Agent SDK, the Claude API, and Model
Context Protocol (MCP), the core technologies used to build production-grade applications with
Claude.</p>
<p>Questions on this exam are grounded in realistic scenarios drawn from actual customer use cases,
including building agentic systems for customer support, designing multi-agent research pipelines,
integrating Claude Code into CI/CD workflows, building developer productivity tools, and extracting
structured data from unstructured documents. Candidates must demonstrate not only conceptual
knowledge but practical judgment about architecture, configuration, and tradeoffs in production
deployments.</p>
<p>This guide is the authoritative reference for candidates preparing to sit the exam. It describes the
exam content, lists the domains and task statements tested, provides sample questions, and
recommends preparation strategies. Read it in full before scheduling your exam.</p>'''

eg_audience_tr='''<p>Bu sertifika için ideal aday, Claude ile production uygulamaları tasarlayan ve uygulayan bir solution
architect'tir. Bu aday şu konularda hands-on deneyime sahiptir:</p>
<ul>
<li>Claude Agent SDK kullanarak agentic uygulamalar geliştirme; çoklu agent orkestrasyonu, subagent
delegasyonu, araç entegrasyonu ve lifecycle hook'ları dahil</li>
<li>Takım iş akışları için Claude Code'u CLAUDE.md dosyaları, Agent Skill'ler, MCP sunucu
entegrasyonları ve plan modu kullanarak konfigüre etme ve özelleştirme</li>
<li>Backend sistem entegrasyonu için Model Context Protocol (MCP) araç ve resource arayüzleri
tasarlama</li>
<li>JSON şemaları, few-shot örnekler ve extraction pattern'lerinden yararlanarak güvenilir
yapılandırılmış çıktı üreten prompt'lar mühendisleştirme</li>
<li>Uzun dokümanlar, çok turlu konuşmalar ve çoklu agent handoff'ları genelinde bağlam pencerelerini
etkili yönetme</li>
<li>Otomatik kod incelemesi, test üretimi ve pull request geri bildirimi için Claude'u CI/CD
pipeline'larına entegre etme</li>
<li>Hata yönetimi, human-in-the-loop iş akışları ve self-evaluation pattern'leri dahil sağlam eskalasyon
ve güvenilirlik kararları verme</li>
</ul>
<p>Aday tipik olarak Claude API'leri, Agent SDK, Claude Code ve MCP ile geliştirme konusunda 6+ ay
pratik deneyime sahiptir; production ortamlarında büyük dil modellerinin hem yeteneklerini hem
sınırlamalarını anlar.</p>'''

eg_audience_en='''<p>The ideal candidate for this certification is a solution architect who designs and implements
production applications with Claude. This candidate has hands-on experience with:</p>
<ul>
<li>Building agentic applications using the Claude Agent SDK, including multi-agent orchestration,
subagent delegation, tool integration, and lifecycle hooks</li>
<li>Configuring and customizing Claude Code for team workflows using CLAUDE.md files, Agent Skills,
MCP server integrations, and plan mode</li>
<li>Designing Model Context Protocol (MCP) tool and resource interfaces for backend system
integration</li>
<li>Engineering prompts that produce reliable structured output, leveraging JSON schemas, few-shot
examples, and extraction patterns</li>
<li>Managing context windows effectively across long documents, multi-turn conversations, and
multi-agent handoffs</li>
<li>Integrating Claude into CI/CD pipelines for automated code review, test generation, and pull
request feedback</li>
<li>Making sound escalation and reliability decisions, including error handling, human-in-the-loop
workflows, and self-evaluation patterns</li>
</ul>
<p>The candidate typically has 6+ months of practical experience building with Claude APIs, Agent SDK,
Claude Code, and MCP, understanding both the capabilities and limitations of large language models
in production environments.</p>'''

EG_DETAILS=[
 ("Kimlik belgesi","Credential","Claude Certified Architect – Foundations","Claude Certified Architect – Foundations"),
 ("Sınav kodu","Exam code","CCAR-F","CCAR-F"),
 ("Soru sayısı","Number of items","60","60"),
 ("Soru formatı","Item format","Çoktan seçmeli ve çoklu yanıtlı sorular; her soru kaç yanıt seçileceğini belirtir","Multiple-choice and multiple-response items; each item states how many responses to select"),
 ("Sınav yapısı","Exam structure","6 senaryoluk havuzdan seçilen 4 senaryo","4 scenarios drawn from a bank of 6"),
 ("Süre","Time limit","120 dakika","120 minutes"),
 ("Uygulama şekli","Delivery","Gözetimli: online gözetimli ve/veya test merkezi, program politikasına göre","Proctored: online proctored and/or test center, per program policy"),
 ("Geçme puanı","Passing score","100–1.000 ölçeğinde 720 skaler puan","Scaled score of 720 on a scale of 100–1,000"),
 ("Sınav ücreti","Exam fee","125 USD","$125 USD"),
 ("Geçerlilik süresi","Validity period","Sertifikanın verildiği tarihten itibaren 12 ay","12 months from the date the credential is awarded"),
 ("Sonuç raporlama","Result reporting","Skaler puanla (100–1.000) geçti/kaldı, ayrıca skor raporunda domain bazında doğru yüzdesi","Pass/fail with scaled score (100–1,000), plus percent-correct by domain on the score report"),
]
eg_details_rows=''.join(f'<tr><th>{bi(tr_l,en_l)}</th><td>{bi(tr_v,en_v)}</td></tr>' for tr_l,en_l,tr_v,en_v in EG_DETAILS)

eg_blueprint_rows=''.join(
    f'<tr><td>{d["id"]}</td><td>{bi(esc(d["title"]),EN_TITLE[d["id"]])}</td><td>%{d["weight"]}</td></tr>'
    for d in D
)

pages.append(f'''<section id="exam-guide" class="page mock">
<a class="back" href="#home">{bi("← Ana sayfa","← Home")}</a>
<p class="kicker">{bi("Sertifika kılavuzu","Certification guide")}</p>
<h1>Claude Certified Architect – Foundations</h1>
<p class="lede">{bi("Sınava kaydolmadan önce okuman gereken resmi sınav kılavuzu.","The official exam guide to read before registering.")}</p>

<details class="guide-item"><summary>{bi("1. Bu Sertifika Hakkında","1. About This Certification")}</summary>
<div class="prose l-tr">{eg_about_tr}</div><div class="prose l-en">{eg_about_en}</div></details>

<details class="guide-item"><summary>{bi("2. Hedef Kitle","2. Intended Audience")}</summary>
<div class="prose l-tr">{eg_audience_tr}</div><div class="prose l-en">{eg_audience_en}</div></details>

<details class="guide-item"><summary>{bi("3. Sınav Detayları — Genel Bakış","3. Exam Details at a Glance")}</summary>
<div class="prose"><table class="rules"><tbody>{eg_details_rows}</tbody></table></div></details>

<details class="guide-item"><summary>{bi("4. Sınav İçerik Taslağı (Blueprint)","4. Exam Content Outline (Blueprint)")}</summary>
<div class="prose"><table class="rules"><thead><tr><th>{bi("Domain","Domain")}</th><th>{bi("İçerik Alanı","Content Domain")}</th><th>{bi("Ağırlık","Weight")}</th></tr></thead>
<tbody>{eg_blueprint_rows}</tbody></table></div></details>

<a class="regcta" href="{REG_URL}" target="_blank" rel="noopener" style="margin-top:24px">{bi("Sınava register ol","Register for exam")} <span>→</span></a>
</section>''')
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
        doms_tr="".join(f'<span style="--c:{D[d-1]["hue"]}">D{d} {D[d-1]["title"]}</span>' for d in x["doms"])
        doms_en="".join(f'<span style="--c:{D[d-1]["hue"]}">D{d} {EN_TITLE[d]}</span>' for d in x["doms"])
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
nav=f'''<nav class="topnav" data-style="apple" data-palette="A">
<div class="topnav-inner">
<a class="brand" href="#home"><span class="brand-mark" aria-hidden="true"></span>CCA Foundations</a>
<div class="topnav-links" id="navlinks">
<a href="#home" data-nav="home">{bi("Domainler","Domains")}</a>
<a href="#scenarios" data-nav="scenarios">{bi("Senaryolar","Scenarios")}</a>
<a href="#practice" data-nav="practice">{bi("Practice","Practice")}</a>
<a href="#exam-guide" data-nav="exam-guide">{bi("Sınav kılavuzu","Exam guide")}</a>
</div>
<button class="langtoggle" id="langtoggle" aria-label="Dil / Language"><span data-l="tr">TR</span><span data-l="en">EN</span></button>
<button class="theme-toggle" id="themetoggle" aria-label="Theme"><span class="ti-light">☀</span><span class="ti-dark" hidden>☾</span></button>
</div>
</nav>
<nav class="tabbar" aria-label="Primary">
<div class="tabbar-inner">
<a href="#home" data-nav="home"><span class="ticon">⌂</span>{bi("Ana sayfa","Home")}</a>
<a href="#scenarios" data-nav="scenarios"><span class="ticon">◔</span>{bi("Senaryolar","Scenarios")}</a>
<a href="#practice" data-nav="practice"><span class="ticon">▤</span>{bi("Practice","Practice")}</a>
<a href="#exam-guide" data-nav="exam-guide"><span class="ticon">ⓘ</span>{bi("Kılavuz","Guide")}</a>
</div>
</nav>'''
doc=f'''<!DOCTYPE html>
<html lang="tr" data-lang="tr" data-style="apple" data-palette="A">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Claude Certified Architect (Foundations) — Çalışma Rehberi</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{nav}
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
