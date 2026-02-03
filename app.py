import streamlit as st
from datetime import datetime
import json

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Fallakte: Der umstrittene Schulbeschluss",
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
        help="Wenn du einen Gruppenlink mit ?group=… nutzt, ist der Name fest.",
    )

    st.session_state["role"] = st.selectbox(
        "Rolle / Perspektive",
        ["Schulaufsicht", "Verwaltungsgericht", "Fachkommission Politische Bildung", "Schulleitung"],
        index=["Schulaufsicht", "Verwaltungsgericht", "Fachkommission Politische Bildung", "Schulleitung"].index(st.session_state["role"]),
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
    section_title("🗂️", "Sachverhalt & Dokumente")

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown(
            """
**Ausgangslage:**  
Die Stadt *Rosenfeld* ist Sachaufwandsträger einer Mittelschule. Der Stadtrat beschließt mehrheitlich:

> „Die Teilnahme von Schülerinnen und Schülern an politischen Demonstrationen während der Unterrichtszeit wird untersagt.  
> Lehrkräften wird es zudem verboten, im Unterricht aktuelle politische Konflikte zu thematisieren, da dies gegen das Neutralitätsgebot der Schule verstoße.“

Begründung: *Neutralität wahren* und *Unterrichtsausfall vermeiden*.

**Eskalation:**  
- SMV kritisiert den Beschluss öffentlich.  
- Eine Lehrkraft thematisiert trotzdem eine aktuelle Debatte → Ermahnung durch Schulleitung.  
- Elternbeirat legt Beschwerde bei der Schulaufsicht ein.  
- Presse berichtet: „Schule soll demokratisch erziehen – aber schweigt zu Politik?“

**Auftrag an euch:**  
Ihr seid ein unabhängiges Gremium und gebt eine begründete Empfehlung ab:
- Ist der Beschluss rechtmäßig?
- Welche Teile wären ggf. zulässig/zulässig mit Auflagen?
"""
        )
        st.info("Tipp: prüfungsnah: 1) Zuständigkeit, 2) Grundrechte, 3) Neutralität, 4) Verhältnismäßigkeit.")

    with right:
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
    st.write("Weiter mit **Checkpoints**.")

# ----------------------------
# CHECKPOINTS
# ----------------------------
elif st.session_state["step"] == "Checkpoints":
    section_title("🧩", "Checkpoints (Analysefragen)")

    st.markdown("Beantwortet die Fragen. Danach bekommt ihr Feedback zur Argumentationsrichtung.")

    questions = [
        {
            "id": "q1",
            "prompt": "1) Zuständigkeit: Darf der Stadtrat Vorgaben zu Unterrichtsinhalten erlassen?",
            "options": ["Ja, als Schulträger hat er volle Steuerung", "Nein, Unterricht/Erziehungsauftrag liegt nicht beim Schulträger", "Nur wenn Eltern zustimmen"],
            "correct": 1,
            "explain": "Schulträger = äußere Schulangelegenheiten. Unterricht/Inhalte = staatliche Schulhoheit / Schule.",
        },
        {
            "id": "q2",
            "prompt": "2) Neutralität: Was bedeutet Neutralitätsgebot im Unterricht am ehesten?",
            "options": ["Politik darf nicht vorkommen", "Kontroverse Themen ausgewogen darstellen, ohne Indoktrination", "Nur Parteien nennen, keine Bewegungen"],
            "correct": 1,
            "explain": "Neutralität schützt vor einseitiger Beeinflussung – nicht vor politischer Bildung.",
        },
        {
            "id": "q3",
            "prompt": "3) Grundrechte: Welche Aussage ist am treffendsten?",
            "options": ["Grundrechte gelten in der Schule nicht", "Grundrechte gelten, können aber verhältnismäßig eingeschränkt werden", "Nur Volljährige haben Meinungsfreiheit"],
            "correct": 1,
            "explain": "Schule ist kein grundrechtsfreier Raum. Einschränkungen nur bei legitimen Zielen & Verhältnismäßigkeit.",
        },
        {
            "id": "q4",
            "prompt": "4) Verhältnismäßigkeit: Ein pauschales Verbot aktueller politischer Konflikte im Unterricht ist…",
            "options": ["meist angemessen, weil es Ruhe schafft", "oft unverhältnismäßig, weil es den Bildungsauftrag zu stark einschränkt", "immer erforderlich"],
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
        for q in questions:
            if st.session_state["mc_answers"].get(q["id"], 0) == q["correct"]:
                score += 1

        st.success(f"Checkpoint-Stand: {score}/{len(questions)}")
        if score >= 3:
            st.info("Ihr seid auf Kurs. Weiter zu **Entscheidung**.")
        else:
            st.warning("Noch wackelig – schaut in die Fallakte und korrigiert eure Argumentationslinie.")

# ----------------------------
# DECISION
# ----------------------------
elif st.session_state["step"] == "Entscheidung":
    section_title("🗳️", "Entscheidung & Begründung")

    default_vote = st.session_state["vote"] if st.session_state["vote"] else "Nein"
    st.session_state["vote"] = st.radio(
        "Ist der Beschluss rechtmäßig?",
        ["Ja", "Nein", "Teilweise"],
        index=["Ja", "Nein", "Teilweise"].index(default_vote),
    )

    st.session_state["reasoning"] = st.text_area(
        "Begründung (3–8 Sätze):",
        value=st.session_state["reasoning"],
        height=220,
        placeholder=(
            "Struktur:\n"
            "1) Zuständigkeit\n"
            "2) Grundrechte\n"
            "3) Neutralität\n"
            "4) Verhältnismäßigkeit\n"
            "→ Ergebnis"
        ),
    )

    # Mini-Feedback (fix ohne DeltaGenerator-Ausgabe)
    st.markdown("### 🧠 Mini-Feedback (ohne KI)")
    if st.session_state["reasoning"].strip():
        text = st.session_state["reasoning"].lower()
        hits = {
            "zuständ": "Zuständigkeit",
            "grundrecht": "Grundrechte",
            "neutral": "Neutralität",
            "verhältnis": "Verhältnismäßigkeit",
            "bildungsauftrag": "Bildungsauftrag/Demokratie",
        }
        found = [label for key, label in hits.items() if key in text]
        missing = [label for label in hits.values() if label not in found]

        st.write(f"Erkannte Bausteine: **{', '.join(found) if found else '—'}**")
        if missing:
            st.warning("Fehlt evtl. noch: " + ", ".join(missing))
        else:
            st.success("Sehr rund: Alle Kernbausteine sind drin.")
    else:
        st.info("Schreib eine kurze Begründung – dann bekommst du Struktur-Feedback.")

    st.divider()

    col1, col2 = st.columns([0.45, 0.55])
    with col1:
        if st.button("📌 Abgabe speichern & Lösung freischalten", use_container_width=True):
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
            st.success("Gespeichert. Die Auflösung ist jetzt für eure Gruppe sichtbar.")

    with col2:
        st.caption("Optional: Du kannst eure Abgabe als Textblock kopieren (z. B. in ein gemeinsames Pad).")

    if st.session_state.get("saved_payload"):
        st.markdown("### 📋 Abgabe (zum Kopieren)")
        st.code(json.dumps(st.session_state["saved_payload"], ensure_ascii=False, indent=2), language="json")

# ----------------------------
# SOLUTION
# ----------------------------
elif st.session_state["step"] == "Auflösung":
    section_title("✅", "Auflösung & Musterlösung")

    if not st.session_state.get("show_solution", False):
        st.warning("Für eure Gruppe ist die Auflösung noch gesperrt. Geht zu **Entscheidung** und speichert eure Abgabe.")
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
    st.markdown("### 🎓 Transferfrage")
    st.markdown(
        """
**Welche Kompetenzen würden Schülerinnen und Schüler durch diesen Fall erwerben?**  
- Urteilsfähigkeit (Abwägen, Begründen)  
- Perspektivwechsel & Kontroversität  
- demokratische Teilhabe verstehen  
- Rechtsstaatsprinzip & Zuständigkeiten  
"""
    )

    if st.session_state.get("saved_payload"):
        st.divider()
        st.markdown("### 🧾 Eure Abgabe (Kurzcheck)")
        st.write(f"**Entscheidung:** {st.session_state['saved_payload']['vote']}")
        st.write(f"**Zeit:** {st.session_state['saved_payload']['timestamp']}")
        st.write("**Begründung:**")
        st.write(st.session_state["saved_payload"]["reasoning"] or "—")

st.caption("© Seminar-Fallakte – Gruppenlinks stabil über ?group=… | Keine Moderatoren-Synchronisation nötig.")
