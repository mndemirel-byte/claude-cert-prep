import re, json, html, os
import markdown
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"content","tr")+os.sep
MD=lambda s: markdown.markdown(s, extensions=['fenced_code','tables','sane_lists'])

DOMAINS = [
 {"id":1,"title":"Agentic Mimari ve Orkestrasyon","weight":27,"hue":"#0F6E6E",
  "desc":"Agentic döngüler, çoklu agent orkestrasyonu, subagent çağırma ve bağlam aktarımı, iş akışı zorlaması ve hook'lar, görev ayrıştırma, oturum durumu.",
  "lessons":["task_statement_1_1_agentic_loops_TR.md","task_statement_1_2_multi_agent_orchestration_TR.md","task_statement_1_3_subagent_invocation.md","task_statement_1_4_workflow_enforcement.md","task_statement_1_5_agent_sdk_hooks.md","task_statement_1_6_task_decomposition.md","task_statement_1_7_session_state.md"],
  "quiz":"domain_1_practice_exam.md","fmt":"A"},
 {"id":2,"title":"Araç Tasarımı ve MCP Entegrasyonu","weight":18,"hue":"#8A4B08",
  "desc":"Araç arayüzü tasarımı, yapılandırılmış hata yanıtları, araç dağılımı ve tool_choice, MCP sunucu entegrasyonu, yerleşik araçlar.",
  "lessons":["task_statement_2_1_tool_interface_design_TR.md","task_statement_2_2_structured_error_responses_TR.md","task_statement_2_3_tool_distribution_TR.md","task_statement_2_4_mcp_server_integration_TR.md","task_statement_2_5_builtin_tools_TR.md"],
  "quiz":"domain_2_practice_exam_TR.md","fmt":"A"},
 {"id":3,"title":"Claude Code Konfigürasyonu ve İş Akışları","weight":20,"hue":"#3B4F9A",
  "desc":"CLAUDE.md hiyerarşisi, özel slash komutları ve skill'ler, yol-bazlı kurallar, plan modu vs doğrudan çalıştırma, yinelemeli iyileştirme, CI/CD entegrasyonu.",
  "lessons":["task_statement_3_1_claude_md_hierarchy_TR.md","task_statement_3_2_custom_commands_skills_TR.md","task_statement_3_3_path_specific_rules_TR.md","task_statement_3_4_plan_mode_vs_direct_TR.md","task_statement_3_5_iterative_refinement_TR.md","task_statement_3_6_cicd_integration_TR.md"],
  "quiz":"domain_3_practice_exam_TR.md","fmt":"A"},
 {"id":4,"title":"Prompt Engineering ve Yapılandırılmış Çıktı","weight":20,"hue":"#7A2E5C",
  "desc":"Açık kriterler, few-shot prompting, tool_use ile yapılandırılmış çıktı, validation-retry döngüleri, toplu işleme, çok örnekli inceleme.",
  "lessons":["task_statement_4_1_explicit_criteria_TR.md","task_statement_4_2_few_shot_prompting_TR.md","task_statement_4_3_structured_output_tool_use_TR.md","task_statement_4_4_validation_retry_loops_TR.md","task_statement_4_5_batch_processing_TR.md","task_statement_4_6_multi_instance_review_TR.md"],
  "quiz":"domain_4_yeterlilik_testi_TR.md","fmt":"B"},
 {"id":5,"title":"Bağlam Yönetimi ve Güvenilirlik","weight":15,"hue":"#4E6B2A",
  "desc":"Bağlam koruma, eskalasyon ve belirsizlik çözümü, hata yayılımı, kod tabanı keşfi, insan incelemesi ve güven kalibrasyonu, bilgi kaynağı takibi.",
  "lessons":["task_statement_5_1_context_preservation_TR.md","task_statement_5_2_escalation_ambiguity_TR.md","task_statement_5_3_error_propagation_TR.md","task_statement_5_4_codebase_exploration_TR.md","task_statement_5_5_human_review_confidence_TR.md","task_statement_5_6_information_provenance_TR.md"],
  "quiz":"domain_5_yeterlilik_testi_TR.md","fmt":"B"},
]

def read(f): return open(P+f,encoding="utf-8").read()

def lesson(f):
    t=read(f)
    m=re.search(r'^# (.+)$',t,re.M); title=m.group(1)
    title=re.sub(r'^Task Statement\s+','',title)
    body=t[m.end():]
    # drop the domain subtitle line
    body=re.sub(r'^\s*## Domain \d.*$','',body,count=1,flags=re.M)
    body=re.sub(r'^\s*---\s*$','',body,count=1,flags=re.M)
    return title, MD(body)

OPT=re.compile(r'^\*\*([A-D])\)\*\*\s*(.*?)\s*$')
def split_q(block):
    lines=block.split('\n'); body=[]; opts={}
    for l in lines:
        m=OPT.match(l.strip())
        if m: opts[m.group(1)]=m.group(2)
        else: body.append(l)
    return MD('\n'.join(body).strip()), opts

def parse_A(t):
    qs=[]
    parts=re.split(r'^## (?:Question|Soru) (\d+) \((.*?)\)\s*$',t,flags=re.M)
    for i in range(1,len(parts),3):
        n,ts,rest=parts[i],parts[i+1],parts[i+2]
        m=re.search(r'^### (?:Correct Answer|Doğru Cevap):\s*([A-D])\s*$',rest,re.M)
        qtext=rest[:m.start()]; expl=rest[m.end():]
        expl=re.split(r'^---\s*$',expl,flags=re.M)[0]
        qtext='\n'.join(re.sub(r'^> ?','',l) for l in qtext.strip().split('\n'))
        body,opts=split_q(qtext)
        # bold "Why X" -> rows
        qs.append({"n":int(n),"ts":ts,"body":body,"opts":opts,"ans":m.group(1),"expl":MD(expl.strip())})
    return qs

def parse_B(t):
    qsec,ksec=re.split(r'^## Cevap Anahtarı.*$',t,flags=re.M)
    qs={}
    parts=re.split(r'^### Soru (\d+) — (.*?)\s*$',qsec,flags=re.M)
    for i in range(1,len(parts),3):
        n,ts,rest=parts[i],parts[i+1],parts[i+2]
        rest=re.split(r'^---\s*$',rest,flags=re.M)[0]
        body,opts=split_q(rest.strip())
        qs[int(n)]={"n":int(n),"ts":ts,"body":body,"opts":opts}
    kp=re.split(r'^### Soru (\d+) → \*\*([A-D])\*\*\s*$',ksec,flags=re.M)
    for i in range(1,len(kp),3):
        n,a,rest=int(kp[i]),kp[i+1],kp[i+2]
        rest=re.split(r'^---\s*$',rest,flags=re.M)[0]
        qs[n]["ans"]=a; qs[n]["expl"]=MD(rest.strip())
    return [qs[k] for k in sorted(qs)]

out=[]
for d in DOMAINS:
    d["lessons_html"]=[lesson(f) for f in d["lessons"]]
    t=read(d["quiz"])
    d["questions"]=parse_A(t) if d["fmt"]=="A" else parse_B(t)
    for q in d["questions"]:
        assert len(q["opts"])==4 and q.get("ans"), (d["id"],q["n"],q["opts"].keys())
    print(d["id"],len(d["lessons_html"]),"lessons",len(d["questions"]),"questions")
os.makedirs(os.path.join(ROOT,"build"),exist_ok=True)
json.dump(DOMAINS,open(os.path.join(ROOT,"build","data.json"),"w"),ensure_ascii=False)
