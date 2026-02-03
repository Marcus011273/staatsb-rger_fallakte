import streamlit as st
from datetime import datetime
import time
import sqlite3
from pathlib import Path

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Fallakte: Der umstrittene Schulbeschluss", page_icon="⚖️", layout="wide")

CASE_TITLE = "Fallakte: Der umstrittene Schulbeschluss"
CASE_ID = "Rosenfeld-23/26"

DB_PATH = Path("case_store.sqlite")  # in repo/app working dir


# ----------------------------
# DB LAYER (SQLite)
# ----------------------------
@st.cache_resource
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            group_name TEXT PRIMARY KEY,
            vote TEXT,
            reasoning TEXT,
            role TEXT,
            ts TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    # init solution flag if missing
    cur = conn.execute("SELECT value FROM settings WHERE key='solution_released'")
    row = cur.fetchone()
    if row is None:
        conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES('solution_released', '0')")
        conn.commit()
    return conn


def db_get_solution_released(conn) -> bool:
    row = conn.execute("SELECT value FROM settings WHERE key='solution_released'").fetchone()
    return bool(int(row[0])) if row else False


def db_set_solution_released(conn, released: bool):
    conn.execute(
        "INSERT OR REPLACE INTO settings(key, value) VALUES('solution_released', ?)",
        ("1" if released else "0",),
    )
    conn.commit()


def db_upsert_submission(conn, group_name: str, vote: str, reasoning: str, role: str, ts: str):
    conn.execute(
        """
        INSERT INTO submissions(group_name, vote, reasoning, role, ts)
        VALUES(?,?,?,?,?)
        ON CONFLICT(group_name) DO UPDATE SET
            vote=excluded.vote,
            reasoning=excluded.reasoning,
            role=excluded.role,
            ts=excluded.ts
        """,
        (group_name, vote, reasoning, role, ts),
    )
    conn.commit()


def db_get_submissions(conn):
    rows = conn.execute("SELECT group_name, vote, reasoning, role, ts FROM submissions ORDER BY lower(group_name)").fetchall()
    subs = []
    for r in rows:
        subs.append(
            {"group_name": r[0], "vote": r[1], "reasoning": r[2], "role": r[3], "timestamp": r[4]}
        )
    return subs


def db_clear_submissions(conn):
    conn.execute("DELETE FROM submissions")
    conn.commit()


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
        "is_moderator": False,
        "auto_refresh": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()
conn = get_db()

# ----------------------------
# URL PARAMS (Moderator/Group)
# ----------------------------
params = st.query_params  # Streamlit >= 1.30
mode = params.get("mode", "group")  # "group" or "moderator"
group_id = params.get("group", "")

if mode == "moderator":
    st.session_state["is_moderator"] = True
else:
    st.session_state["is_moderator"] = False
    if group_id and not st.session_state.get("group_name"):
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
    # resets only current session state, not DB
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


solution_released = db_get_solution_released(conn)

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.title("⚖️ Fallakte")
    st.caption(f"ID: {CASE_ID}")

    if st.session_state["is_moderator"]:
        st.success("Modus: Moderator/Beamer")
        st.caption("Link: ?mode=moderator")
    else:
        st.info("Modus: Gruppe")
        if group_id:
            st.caption(f"Link: ?mode=group&group={group_id}")

    st.session_state["group_name"] = st.text_input(
        "Gruppe / Name",
        st.session_state["group_name"],
        placeholder="z. B. Gruppe 2",
        disabled=st.session_state["is_moderator"],
    )

    st.session_state["role"] = st.selectbox(
        "Rolle / Perspektive",
        ["Schulaufsicht", "Verwaltungsgericht", "Fachkommission Politische Bildung", "Schulleitung"],
        index=["Schulaufsicht", "Verwaltungsgericht", "Fachkommission Politische Bildung", "Schulleitung"].index(st.session_state["role"]),
    )

    st.divider()

    steps = ["Fallakte", "Checkpoints", "Entscheidung", "Auflösung"]
    if st.session_state["is_moderator"]:
        steps = ["Live-Board"] + steps

    if st.session_state["step"] not in steps:
        st.session_state["step"] = steps[0]

    st.session_state["step"] = st.radio("Navigation", steps, index=steps.index(st.session_state["step"]))

    st.divider()
    st.caption("Moderation")
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🔄 Session-Reset", use_container_width=True):
            reset_session()

    with col_b:
        if st.session_state["is_moderator"]:
            new_flag = st.toggle("Lösung freigeben", value=solution_released)
            if new_flag != solution_released:
                db_set_solution_released(conn, new_flag)
                solution_released = new_flag
        else:
            st.toggle("Lösung freigeben", value=solution_released, disabled=True)

    if st.session_state["is_moderator"]:
        st.divider()
        st.session_state["auto_refresh"] = st.toggle("Live aktualisieren", value=st.session_state.get("auto_refresh", True))
        if st.button("🧹 Alle Abgaben löschen", use_container_width=True):
            db_clear_submissions(conn)
            st.success("Alle Abgaben gelöscht.")
            st.rerun()


# ----------------------------
# HEADER
# ----------------------------
st.title(CASE_TITLE)
badge(f"ID: {CASE_ID}")
badge(f"Perspektive: {st.session_state['role']}")
if not st.session_state["is_moderator"] and st.session_state["group_name"].strip():
    badge(f"Gruppe: {st.session_state['group_name']}")
st.caption("Ziel: urteilsbildend arbeiten (Zuständigkeit → Grundrechte → Neutralität → Verhältnismäßigkeit).")

# ----------------------------
# LIVE-BOARD (MODERATOR)
# ----------------------------
if st.session_state["step"] == "Live-Board":
    section_title("📡", "Live-Board (Moderator/Beamer)")

    subs = db_get_submissions(conn)

    left, mid, right = st.columns([0.52, 0.28, 0.20])

    with left:
        st.markdown("### Eingänge")
        if subs:
            for s in subs:
                st.markdown(f"**{s['group_name']}** — **{s['vote'] or '—'}**  \n_{s['timestamp'] or '—'}_")
                snippet = (s["reasoning"] or "").strip()
                if snippet:
                    st.caption(snippet[:220] + ("…" if len(snippet) > 220 else ""))
                st.divider()
        else:
            st.info("Noch keine Gruppenabgaben.")

    with mid:
        st.markdown("### Abstimmungsbild")
        counts = {"Ja": 0, "Nein": 0, "Teilweise": 0}
        for s in subs:
            if s["vote"] in counts:
                counts[s["vote"]] += 1
        st.write(counts)

        st.markdown("### Status")
        st.write(f"Abgaben: **{len(subs)}**")

        st.markdown("### Lösung")
        solution_released = db_get_solution_released(conn)
        st.write("Freigegeben:" + (" ✅" if solution_released else " ❌"))

    with right:
        st.markdown("### Steuerung")
        if st.button("↻ Jetzt aktualisieren", use_container_width=True):
            st.rerun()

        st.caption("Auto-Refresh (alle ~2s)")
        if st.session_state.get("auto_refresh", True):
            time.sleep(2)
            st.rerun()

    st.stop()


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
    st.markdown("### ✅ Nächster Schritt")
    st.write("Geht zu **Checkpoints**, um eure Analyse strukturiert vorzubereiten.")


# ----------------------------
# CHECKPOINTS
# ----------------------------
elif st.session_state["step"] == "Checkpoints":
    section_title("🧩", "Checkpoints (Analysefragen)")

    st.markdown("Beantwortet die Fragen. Danach bekommt ihr Rückmeldung zur Argumentationsrichtung.")
    st.caption("Hinweis: Es geht um Logik & Struktur – nicht ums Auswendiglernen.")

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

    st.session_state["mc_answers"] = st.session_state.get("mc_answers", {})

    for q in questions:
        st.session_state["mc_answers"][q["id"]] = st.radio(
            q["prompt"],
            options=list(range(len(q["options"]))),
            format_func=lambda i, opts=q["options"]: opts[i],
            index=st.session_state["mc_answers"].get(q["id"], 0),
            key=f"mc_{q['id']}",
        )
        st.write("")

    col1, col2 = st.columns([0.35, 0.65])
    with col1:
        if st.button("✅ Check auswerten", use_container_width=True):
            st.session_state["checks_done"] = True

    with col2:
        if st.session_state["checks_done"]:
            score = 0
            feedback_lines = []
            for q in questions:
                a = st.session_state["mc_answers"].get(q["id"], 0)
                if a == q["correct"]:
                    score += 1
                    feedback_lines.append(f"✅ {q['prompt']} – passt.")
                else:
                    feedback_lines.append(f"⚠️ {q['prompt']} – Hinweis: {q['explain']}")

            st.success(f"Checkpoint-Stand: {score}/{len(questions)}")
            st.markdown("\n".join(feedback_lines))
            st.info("Weiter zu **Entscheidung**." if score >= 3 else "Nochmal nachschärfen, dann zu **Entscheidung**.")


# ----------------------------
# DECISION
# ----------------------------
elif st.session_state["step"] == "Entscheidung":
    section_title("🗳️", "Entscheidung & Begründung")

    if st.session_state["is_moderator"]:
        st.info("Moderator kann mitlesen, aber nicht als Gruppe abgeben (Gruppenlink nutzen).")

    default_vote = st.session_state["vote"] if st.session_state["vote"] else "Nein"

    st.session_state["vote"] = st.radio(
        "Ist der Beschluss rechtmäßig?",
        ["Ja", "Nein", "Teilweise"],
        index=["Ja", "Nein", "Teilweise"].index(default_vote),
        disabled=st.session_state["is_moderator"],
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
        disabled=st.session_state["is_moderator"],
    )

    cols = st.columns([0.4, 0.6])
    with cols[0]:
        if st.button("📌 Entscheidung speichern", use_container_width=True, disabled=st.session_state["is_moderator"]):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["timestamp"] = ts

            gname = st.session_state["group_name"].strip() or (f"Gruppe {group_id}" if group_id else "Unbenannt")
            db_upsert_submission(conn, gname, st.session_state["vote"], st.session_state["reasoning"], st.session_state["role"], ts)
            st.success("Gespeichert (im Live-Board sichtbar).")

    with cols[1]:
        st.caption("Tipp: Nenne mind. 3 Bausteine: Zuständigkeit, Neutralität, Verhältnismäßigkeit (plus Grundrechte).")

    st.divider()
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
        st.warning("Fehlt evtl. noch: " + ", ".join(missing)) if missing else st.success("Sehr rund: Alle Kernbausteine sind drin.")
    else:
        st.info("Schreib eine kurze Begründung – dann bekommst du Struktur-Feedback.")


# ----------------------------
# SOLUTION
# ----------------------------
elif st.session_state["step"] == "Auflösung":
    section_title("✅", "Auflösung & Musterlösung")

    solution_released = db_get_solution_released(conn)
    if not solution_released:
        st.warning("Die Lösung ist noch nicht freigegeben (nur Moderator kann das in der Sidebar).")
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
    st.markdown("### 🎓 Transferfrage fürs Seminar (Chef-Moment)")
    st.markdown(
        """
**Welche Kompetenzen würden Schülerinnen und Schüler durch diesen Fall erwerben?**  
- Urteilsfähigkeit (Abwägen, Begründen)  
- Perspektivwechsel & Kontroversität  
- demokratische Teilhabe verstehen  
- Rechtsstaatsprinzip & Zuständigkeiten  
"""
    )

    st.divider()
    st.markdown("### 🧾 Eure gespeicherte Entscheidung (falls vorhanden)")
    if st.session_state.get("timestamp"):
        st.write(f"**Zeit:** {st.session_state['timestamp']}")
        st.write(f"**Entscheidung:** {st.session_state['vote']}")
        st.write("**Begründung:**")
        st.write(st.session_state["reasoning"] if st.session_state["reasoning"].strip() else "—")
    else:
        st.info("Noch nichts gespeichert – geht zu **Entscheidung** und speichert eure Begründung.")


st.caption("© Seminar-Fallakte – Cloud-tauglich mit SQLite. Tipp: Gruppenlinks per QR-Code teilen (optional).")
