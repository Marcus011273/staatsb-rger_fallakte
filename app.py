import streamlit as st
from datetime import datetime
import json

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Fallakte: Der umstrittene Schulbeschluss - Seminar 45.2",
    page_icon="⚖️",
    layout="wide",
)

CASE_TITLE = "Fallakte: Der umstrittene Schulbeschluss"
CASE_ID = "Rosenfeld-23/26"

# ----------------------------
# URL PARAMS (Group)
# ----------------------------
params = st.query_params  # Streamlit >= 1.30
group_id = params.get("group", "")

# ----------------------------
# STATE INIT
# ----------------------------
def init_state():
    defaults = {
        "step": "Fallakte",
        "group_name": "",
        "role": "Schulaufsicht",
        "checks_done": False,
        "mc_answers": {},
        "vote": None,
        "reasoning": "",
        "timestamp": None,
        "saved_payload": None,
        "show_solution": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# Prefill group name from URL, and lock it (stable links)
if group_id and not st.session_state["group_name"]:
    st.session_state["group_name"] = f"Gruppe {group_id}"

# ----------------------------
# ROLE-SPECIFIC ADDITIONAL TASKS (Sie-Form)
# ----------------------------
ROLE_TASKS = {
    "Schulaufsicht": {
        "title": "🏛️ Perspektive: Schulaufsicht",
        "intro": "Sie betrachten den Fall aus der Sicht der staatlichen Schulaufsicht.",
        "questions": [
            "Welche Zuständigkeiten haben Schulträger, Schule und staatliche Schulaufsicht?",
            "Überschreitet der Stadtrat mit seinem Beschluss seine Kompetenzen?",
            "Welche Konsequenzen oder Empfehlungen ergeben sich aus aufsichtsrechtlicher Sicht?",
        ],
    },
    "Schulleitung": {
        "title": "🏫 Perspektive: Schulleitung",
        "intro": "Sie betrachten den Fall aus der Sicht der Schulleitung einer betroffenen Schule.",
        "questions": [
            "Welche Auswirkungen hat der Beschluss auf den Schulalltag und das Kollegium?",
            "Welche pädagogischen und organisatorischen Konflikte könnten entstehen?",
            "Wie kann die Schule rechtssicher und zugleich pädagogisch verantwortungsvoll handeln?",
        ],
    },
    "Verwaltungsgericht": {
        "title": "⚖️ Perspektive: Verwaltungsgericht",
        "intro": "Sie betrachten den Fall aus der Sicht eines Verwaltungsgerichts.",
        "questions": [
            "Welche Grundrechte der Schülerinnen und Schüler sind betroffen?",
            "Wie ist das Neutralitätsgebot rechtlich zu verstehen?",
            "Ist der Beschluss verhältnismäßig oder stellt er einen unzulässigen Eingriff dar?",
        ],
    },
    "Fachkommission Politische Bildung": {
        "title": "📘 Perspektive: Fachkommission für Politische Bildung",
        "intro": "Sie betrachten den Fall aus der Sicht einer fachlichen Kommission für politische Bildung.",
        "questions": [
            "Welchen Auftrag hat Schule in einer demokratischen Gesellschaft?",
            "Steht politische Bildung im Widerspruch zum Neutralitätsgebot?",
            "Welche langfristigen Folgen hätte ein solcher Beschluss für demokratische Bildung?",
        ],
    },
}

# ----------------------------
# HELPERS
# ----------------------------
def badge(text: str):
    st.markdown(
        f"""
        <div style="display:inline-block;padding:4px 10px;border-radius:999px;
        border:1px solid rgba(0,0,0,.15);font-size:0.9rem;margin-right:6px;">
        {text}
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_title(icon, title):
    st.markdown(f"## {icon} {title}")

def reset_session():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

def render_role_task(role: str):
    data = ROLE_TASKS.get(role)
    if not data:
        return
    st.markdown(f"### {data['title']}")
    st.write(data["intro"])
    st.markdown("**Leitfragen:**")
    for q in data["questions"]:
        st.markdown(f"- {q}")

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.title("⚖️ Fallakte")
    st.caption(f"ID: {CASE_ID}")

    # Group name: locked if group param exists
    st.session_state["group_name"] = st.text_input(
        "Gruppe / Name",
        st.session_state["group_name"],
        placeholder="z. B. Gruppe 2",
        disabled=bool(group_id),
        help="Wenn Sie einen Gruppenlink mit ?group=… nutzen, ist der Name fest.",
    )

    st.session_state["role"] = st.selectbox(
        "Institutionelle Perspektive",
        ["Schulaufsicht", "Verwaltungsgericht", "Fachkommission Politische Bildung", "Schulleitung"],
        index=["Schulaufsicht", "Verwaltungsgericht", "Fachkommission Politische Bildung", "Schulleitung"].index(st.session_state["role"]),
        help="Bitte bearbeiten Sie den Fall mit besonderem Fokus auf die Leitfragen Ihrer Perspektive.",
    )

    st.divider()

    st.session_state["step"] = st.radio(
        "Navigation",
        ["Fallakte", "Checkpoints", "Entscheidung", "Auflösung"],
        index=["Fallakte", "Checkpoints", "Entscheidung", "Auflösung"].index(st.session_state["step"]),
    )

    st.divider()
    if st.button("🔄 Alles zurücksetzen", use_container_width=True):
        reset_session()

# ----------------------------
# HEADER
# ----------------------------
st.title(CASE_TITLE)
badge(f"ID: {CASE_ID}")
if st.session_state["group_name"].strip():
    badge(f"Gruppe: {st.session_state['group_name']}")
badge(f"Perspektive: {st.session_state['role']}")
st.caption("Ziel: urteilsbildend arbeiten (Zuständigkeit → Grundrechte → Neutralität → Verhältnismäßigkeit).")

# ----------------------------
# FALLAKTE
# ----------------------------
if st.session_state["step"] == "Fallakte":
    section_title("🗂️", "Fallakte")

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown(
            """
### Sachverhalt

Die Stadt **Rosenfeld** ist Sachaufwandsträger einer Mittelschule. Der Stadtrat beschließt mehrheitlich:

> „Die Teilnahme von Schülerinnen und Schülern an politischen Demonstrationen während der Unterrichtszeit wird untersagt.  
> Lehrkräften wird es zudem verboten, im Unterricht aktuelle politische Konflikte zu thematisieren, da dies gegen das Neutralitätsgebot der Schule verstoße.“

Begründung: **Neutralität wahren** und **Unterrichtsausfall vermeiden**.

**Eskalation:**  
- Die SMV kritisiert den Beschluss öffentlich.  
- Eine Lehrkraft thematisiert trotzdem eine aktuelle Debatte → Ermahnung durch die Schulleitung.  
- Der Elternbeirat legt Beschwerde bei der Schulaufsicht ein.  
- Presse berichtet: „Schule soll demokratisch erziehen – aber schweigt zu Politik?“

---
### Übergeordneter Arbeitsauftrag

**Sie arbeiten als unabhängiges Prüfgremium.**  
Ihre Aufgabe ist es, den Beschluss des Stadtrats **fachlich fundiert, begründet und nachvollziehbar** zu beurteilen.

Dabei analysieren Sie den Fall **aus einer zugewiesenen institutionellen Perspektive** und kommen zu einer begründeten Empfehlung.

**Hinweis zur Arbeitsweise:**  
Auch wenn Sie aus einer bestimmten institutionellen Perspektive argumentieren, treffen Sie Ihre Entscheidung **unabhängig, sachlich und auf Grundlage demokratischer und rechtsstaatlicher Prinzipien**.

---
### Verbindliche Fragestellung

**Ist der Beschluss des Stadtrats rechtmäßig?**  
☐ Ja  ☐ Nein  ☐ Teilweise

Begründen Sie Ihre Entscheidung fachlich und strukturiert.

**Empfohlene Struktur:**  
1. Zuständigkeit  
2. Grundrechte  
3. Neutralitätsgebot  
4. Verhältnismäßigkeit
"""
        )

        st.info("Bitte beachten Sie zusätzlich die Leitfragen Ihrer gewählten Perspektive (rechts).")

    with right:
        st.markdown("### Ihre Perspektive (Zusatzauftrag)")
        render_role_task(st.session_state["role"])

        st.divider()
        st.markdown("### 📎 Dokumente (simuliert)")
        tab1, tab2, tab3, tab4 = st.tabs(["Stadtratsbeschluss", "Elternbeschwerde", "Schulleitung", "Presseauszug"])

        with tab1:
            st.markdown(
                """
**Beschlussvorlage (Auszug)**  
- Ziel: Neutralitätsgebot sichern  
- Unterrichtszeit schützen  
- Keine „politische Stimmungsmache“ an Schulen

**Beschluss:**  
1) Teilnahme an politischen Demonstrationen während Unterrichtszeit untersagt.  
2) Behandlung aktueller politischer Konflikte im Unterricht untersagt.
"""
            )

        with tab2:
            st.markdown(
                """
**Beschwerde Elternbeirat (Auszug)**  
- Schule hat demokratischen Erziehungsauftrag  
- Politische Bildung ist verpflichtend  
- Pauschalverbot verletzt Grundrechte  
- Bitte rechtliche Prüfung und Aufhebung
"""
            )

        with tab3:
            st.markdown(
                """
**Notiz der Schulleitung (intern)**  
- Sorge um Konflikte im Kollegium  
- Eltern könnten „Parteinahme“ unterstellen  
- Wunsch nach klaren Vorgaben „von oben“
"""
            )

        with tab4:
            st.markdown(
                """
**Presseauszug (fiktiv)**  
„Darf Schule Politik ausklammern? Kritiker sprechen von einem Angriff auf Demokratiebildung.“
"""
            )

    st.divider()
    st.write("Weiter mit **Checkpoints**, um Ihre Argumentation zu strukturieren.")

# ----------------------------
# CHECKPOINTS
# ----------------------------
elif st.session_state["step"] == "Checkpoints":
    section_title("🧩", "Checkpoints (Analysefragen)")

    st.markdown("Bitte beantworten Sie die Fragen. Anschließend erhalten Sie eine kurze Rückmeldung zur Argumentationsrichtung.")
    st.caption("Hinweis: Es geht um Struktur und Begründungslogik – nicht ums Auswendiglernen.")

    questions = [
        {
            "id": "q1",
            "prompt": "1) Zuständigkeit: Darf der Stadtrat Vorgaben zu Unterrichtsinhalten erlassen?",
            "options": [
                "Ja, als Schulträger hat er volle Steuerung",
                "Nein, Unterricht und Bildungsauftrag liegen nicht beim Schulträger",
                "Nur wenn Eltern zustimmen",
            ],
            "correct": 1,
            "explain": "Schulträger = äußere Schulangelegenheiten. Unterricht/Inhalte = staatliche Schulhoheit / Schule.",
        },
        {
            "id": "q2",
            "prompt": "2) Neutralität: Was bedeutet Neutralitätsgebot im Unterricht am ehesten?",
            "options": [
                "Politik darf nicht vorkommen",
                "Kontroverse Themen ausgewogen darstellen, ohne Indoktrination",
                "Nur Parteien nennen, keine Bewegungen",
            ],
            "correct": 1,
            "explain": "Neutralität schützt vor einseitiger Beeinflussung – nicht vor politischer Bildung.",
        },
        {
            "id": "q3",
            "prompt": "3) Grundrechte: Welche Aussage ist am treffendsten?",
            "options": [
                "Grundrechte gelten in der Schule nicht",
                "Grundrechte gelten, können aber verhältnismäßig eingeschränkt werden",
                "Nur Volljährige haben Meinungsfreiheit",
            ],
            "correct": 1,
            "explain": "Schule ist kein grundrechtsfreier Raum. Einschränkungen nur bei legitimen Zielen & Verhältnismäßigkeit.",
        },
        {
            "id": "q4",
            "prompt": "4) Verhältnismäßigkeit: Ein pauschales Verbot aktueller politischer Konflikte im Unterricht ist …",
            "options": [
                "meist angemessen, weil es Ruhe schafft",
                "oft unverhältnismäßig, weil es den Bildungsauftrag zu stark einschränkt",
                "immer erforderlich",
            ],
            "correct": 1,
            "explain": "Pauschalverbote sind regelmäßig zu weit. Mildere Mittel existieren (Leitlinien, Mehrperspektivität, Absprachen).",
        },
    ]

    for q in questions:
        st.session_state["mc_answers"][q["id"]] = st.radio(
            q["prompt"],
            options=list(range(len(q["options"]))),
            format_func=lambda i, opts=q["options"]: opts[i],
            index=st.session_state["mc_answers"].get(q["id"], 0),
            key=f"mc_{q['id']}",
        )
        st.write("")

    if st.button("✅ Check auswerten", use_container_width=True):
        st.session_state["checks_done"] = True

    if st.session_state["checks_done"]:
        score = 0
        feedback_lines = []
        for q in questions:
            if st.session_state["mc_answers"].get(q["id"], 0) == q["correct"]:
                score += 1
                feedback_lines.append(f"✅ {q['prompt']} – passt.")
            else:
                feedback_lines.append(f"⚠️ {q['prompt']} – Hinweis: {q['explain']}")

        st.success(f"Checkpoint-Stand: {score}/{len(questions)}")
        st.markdown("\n".join(feedback_lines))

        if score >= 3:
            st.info("Sie sind argumentativ auf Kurs. Bitte wechseln Sie zu **Entscheidung**.")
        else:
            st.warning("Bitte schärfen Sie Ihre Argumentationslinie und wechseln Sie anschließend zu **Entscheidung**.")

# ----------------------------
# DECISION
# ----------------------------
elif st.session_state["step"] == "Entscheidung":
    section_title("🗳️", "Entscheidung & Begründung")

    st.markdown("Bitte treffen Sie eine Entscheidung und begründen Sie diese fachlich und strukturiert.")
    st.info("Berücksichtigen Sie zusätzlich die Leitfragen Ihrer Perspektive (siehe Fallakte).")

    default_vote = st.session_state["vote"] if st.session_state["vote"] else "Nein"
    st.session_state["vote"] = st.radio(
        "Ist der Beschluss rechtmäßig?",
        ["Ja", "Nein", "Teilweise"],
        index=["Ja", "Nein", "Teilweise"].index(default_vote),
    )

    st.session_state["reasoning"] = st.text_area(
        "Begründung (3–10 Sätze):",
        value=st.session_state["reasoning"],
        height=240,
        placeholder=(
            "Empfohlene Struktur:\n"
            "1) Zuständigkeit\n"
            "2) Grundrechte\n"
            "3) Neutralitätsgebot\n"
            "4) Verhältnismäßigkeit\n"
            "→ Ergebnis\n\n"
            "Bitte ergänzen Sie Aspekte aus Ihrer Perspektive."
        ),
    )

    # Role task reminder (compact)
    with st.expander("📌 Leitfragen Ihrer Perspektive anzeigen", expanded=False):
        render_role_task(st.session_state["role"])

    # Mini-Feedback (without DeltaGenerator output)
    st.markdown("### 🧠 Mini-Feedback (ohne KI)")
    if st.session_state["reasoning"].strip():
        text = st.session_state["reasoning"].lower()
        hits = {
            "zuständ": "Zuständigkeit",
            "grundrecht": "Grundrechte",
            "neutral": "Neutralitätsgebot",
            "verhältnis": "Verhältnismäßigkeit",
            "bildungsauftrag": "Bildungsauftrag/Demokratie",
        }
        found = [label for key, label in hits.items() if key in text]
        missing = [label for label in hits.values() if label not in found]

        st.write(f"Erkannte Bausteine: **{', '.join(found) if found else '—'}**")
        if missing:
            st.warning("Fehlt evtl. noch: " + ", ".join(missing))
        else:
            st.success("Sehr rund: Alle Kernbausteine sind enthalten.")
    else:
        st.info("Bitte verfassen Sie eine kurze Begründung, um ein Struktur-Feedback zu erhalten.")

    st.divider()

    col1, col2 = st.columns([0.45, 0.55])
    with col1:
        if st.button("📌 Abgabe speichern & Auflösung freischalten", use_container_width=True):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["timestamp"] = ts

            payload = {
                "case_id": CASE_ID,
                "group": st.session_state["group_name"].strip() or (f"Gruppe {group_id}" if group_id else "Unbenannt"),
                "role": st.session_state["role"],
                "vote": st.session_state["vote"],
                "reasoning": st.session_state["reasoning"],
                "timestamp": ts,
            }
            st.session_state["saved_payload"] = payload
            st.session_state["show_solution"] = True
            st.success("Ihre Abgabe wurde gespeichert. Die Auflösung ist nun für Ihre Gruppe sichtbar.")

    with col2:
        st.caption("Optional: Sie können Ihre Abgabe als Textblock kopieren (z. B. in ein gemeinsames Dokument).")

    if st.session_state.get("saved_payload"):
        st.markdown("### 📋 Abgabe (zum Kopieren)")
        st.code(json.dumps(st.session_state["saved_payload"], ensure_ascii=False, indent=2), language="json")

# ----------------------------
# SOLUTION
# ----------------------------
elif st.session_state["step"] == "Auflösung":
    section_title("✅", "Auflösung & Musterlösung")

    if not st.session_state.get("show_solution", False):
        st.warning("Für Ihre Gruppe ist die Auflösung noch gesperrt. Bitte speichern Sie zunächst Ihre Abgabe unter **Entscheidung**.")
        st.stop()

    st.success("**Ergebnis:** Der Beschluss ist **rechtswidrig** (mindestens in wesentlichen Teilen).")

    st.markdown(
        """
### Musterbegründung (prüfungsnah)

**1) Zuständigkeit:**  
Der Stadtrat (Schulträger) ist primär für *äußere Schulangelegenheiten* zuständig.  
Vorgaben zu **Unterrichtsinhalten** und zum **pädagogischen Auftrag** fallen nicht in seine Kompetenz.  
→ Der Beschluss ist bereits deshalb angreifbar.

**2) Grundrechte:**  
Schülerinnen und Schüler behalten ihre Grundrechte auch in der Schule. Einschränkungen sind möglich, müssen aber legitim begründet und **verhältnismäßig** sein.  
Ein pauschales Verbot politischer Themen greift zu stark ein.

**3) Neutralitätsgebot:**  
Neutralität bedeutet nicht „Politik vermeiden“, sondern **kontroverse Themen ausgewogen behandeln** und **Indoktrination vermeiden**.  
Ein Unterrichtsverbot aktueller Konflikte beruht auf einem Fehlverständnis.

**4) Verhältnismäßigkeit:**  
Pauschalverbote sind regelmäßig nicht erforderlich und nicht angemessen. Mildere Mittel wären z. B. didaktische Leitlinien, Transparenz, Mehrperspektivität, schulinterne Absprachen.

**Fazit:**  
Der Beschluss ist rechtswidrig; zulässig wären allenfalls eng begrenzte organisatorische Regelungen (z. B. Umgang mit Unterrichtsversäumnissen), aber kein generelles Themenverbot.
"""
    )

    st.divider()
    st.markdown("### 🎓 Reflexionsfrage (optional)")
    st.markdown(
        """
*Warum ist es für eine Demokratie wichtig, dass unterschiedliche Institutionen denselben Sachverhalt unterschiedlich gewichten, aber dennoch auf einer gemeinsamen rechtlichen Grundlage entscheiden?*
"""
    )

    if st.session_state.get("saved_payload"):
        st.divider()
        st.markdown("### 🧾 Ihre Abgabe (Kurzcheck)")
        st.write(f"**Entscheidung:** {st.session_state['saved_payload']['vote']}")
        st.write(f"**Zeit:** {st.session_state['saved_payload']['timestamp']}")
        st.write("**Begründung:**")
        st.write(st.session_state["saved_payload"]["reasoning"] or "—")

st.caption("© Seminar-Fallakte – Gruppenlinks stabil über ?group=… | Perspektivaufträge in Sie-Form integriert.")
