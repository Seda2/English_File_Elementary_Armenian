# -*- coding: utf-8 -*-
"""
🍑 English Practice for Armenian Beginners — v4
================================================
• 👤 Learner profiles: each student has their own saved progress
• 💾 Progress is saved automatically to english_progress.json (same folder)
  — switching exercises or closing the app never erases it
• 📚 Covers ALL 12 Files of English File Elementary (4th ed.)
• Exercise types: write full sentence · multiple choice · translate HY→EN ·
  🎧 listen-to-spelling · auto-check after every answer

RUN:  streamlit run english_practice_app.py
"""

import json
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------- page setup
st.set_page_config(
    page_title="English Practice · Անգլերենի վարժություններ",
    page_icon="🍑",
    layout="wide",
)

# ---------------------------------------------------------------- styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
h1, h2, h3 { font-family: 'Fredoka', sans-serif !important; }

.hero {
    background: linear-gradient(100deg, #FF9E4F 0%, #F4636E 55%, #C0316E 100%);
    border-radius: 22px; padding: 24px 30px; color: white; margin-bottom: 6px;
}
.hero h1 { color: white !important; margin: 0; font-size: 1.9rem; }
.hero p  { margin: 6px 0 0 0; font-size: 1.02rem; opacity: .95; }
.ef-badge {
    display: inline-block; background: rgba(255,255,255,.25);
    border-radius: 999px; padding: 2px 12px; font-weight: 700; font-size: .9rem;
}

.tip-card {
    background: #FFF3E4; border: 2px dashed #FF9E4F; border-radius: 16px;
    padding: 13px 18px; margin: 10px 0 4px 0; font-size: 1.02rem;
}
.tip-card b { color: #C0316E; }

.q-card {
    background: white; border: 2px solid #FFE3C8; border-radius: 18px;
    padding: 14px 18px 6px 18px; margin: 12px 0;
    box-shadow: 0 2px 8px rgba(192,49,110,.06);
}
.q-chip {
    display: inline-block; background: #3E7CB1; color: white; border-radius: 999px;
    padding: 2px 12px; font-weight: 800; margin-right: 8px;
}
.q-text { font-size: 1.15rem; }
.hy-line { color: #8a5a86; font-size: 1.05rem; }

.ok-box   { background:#E8F8EE; border-left:6px solid #2EAD62; border-radius:10px; padding:8px 14px; margin:6px 0 10px 0; }
.err-box  { background:#FDECEE; border-left:6px solid #E3506A; border-radius:10px; padding:8px 14px; margin:6px 0 10px 0; }
.warn-box { background:#FFF6DE; border-left:6px solid #E8A93C; border-radius:10px; padding:8px 14px; margin:6px 0 10px 0; }
.hy-note  { color:#6b5b73; font-size:.95rem; }

.score-banner {
    background: #EAF3FB; border: 2px solid #3E7CB1; border-radius: 16px;
    padding: 12px 18px; font-size: 1.12rem; font-weight: 800; color: #26527c;
    margin: 10px 0;
}
.profile-card {
    background: #FFF3E4; border: 2px solid #FF9E4F; border-radius: 18px;
    padding: 16px; text-align: center; font-size: 1.1rem; font-weight: 800;
}

.stTextInput input {
    border-radius: 12px !important; border: 2px solid #FFD9B3 !important;
    font-size: 1.05rem !important;
}
.stTextInput input:focus { border-color: #F4636E !important; }
.stButton button { font-family: 'Fredoka', sans-serif; border-radius: 999px; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- checking helpers
CONTRACTION_PAIRS = [
    ("i am", "i'm"), ("you are", "you're"), ("he is", "he's"), ("she is", "she's"),
    ("it is", "it's"), ("we are", "we're"), ("they are", "they're"),
    ("is not", "isn't"), ("are not", "aren't"), ("was not", "wasn't"),
    ("were not", "weren't"), ("does not", "doesn't"), ("do not", "don't"),
    ("did not", "didn't"), ("cannot", "can't"), ("can not", "can't"),
    ("have not", "haven't"), ("has not", "hasn't"),
    ("what is", "what's"), ("where is", "where's"), ("who is", "who's"),
    ("when is", "when's"), ("how is", "how's"), ("that is", "that's"),
    ("name is", "name's"), ("today is", "today's"),
    ("i have", "i've"), ("we have", "we've"), ("they have", "they've"),
    ("you have", "you've"),
]


def normalize(text: str) -> str:
    """Lowercase, unify apostrophes, collapse spaces, ignore end punctuation."""
    t = text.strip().lower().replace("’", "'").replace("`", "'")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([?.!,])", r"\1", t)
    return t.strip(" .?!,")


def variants(sentence: str) -> set:
    """All accepted spellings: contracted AND full forms are both correct."""
    out = {normalize(sentence)}
    changed = True
    while changed:
        changed = False
        for a, b in CONTRACTION_PAIRS:
            for s in list(out):
                for x, y in ((a, b), (b, a)):
                    if x in s and s.replace(x, y) not in out:
                        out.add(s.replace(x, y))
                        changed = True
    return out


def accepted_set(q: dict) -> set:
    acc = set()
    for s in q.get("accept", [q["full"]]):
        acc |= variants(s)
    return acc


def check_full(user: str, q: dict) -> bool:
    return normalize(user) in accepted_set(q)


PRAISE = ["Ապրե՛ս! 🎉", "Կեցցե՛ս! 🌟", "Շատ լավ! 👏", "Հիանալի է! 🥳", "Բրավո! 💪", "Հրաշալի! ✨"]
ENCOURAGE = ["Փորձիր նորից 💛", "Գրեթե ստացվեց 🙂", "Մի հանձնվիր 💪", "Կարդա հուշումը 🔎"]
AVATARS = ["🦊", "🐻", "🐱", "🐶", "🦁", "🐼", "🦄", "🐸", "🐧", "🦋", "🐯", "🐨"]


def tts_buttons(sentence: str, uid: str, spell_word: str = None, listen: bool = True):
    """Browser text-to-speech: read the sentence and/or spell a word."""
    uid = re.sub(r"\W", "_", uid)
    buttons = ""
    if listen:
        buttons += f"""
          <button onclick="say_{uid}({json.dumps(sentence)}, 0.85)"
                  style="background:#3E7CB1;color:white;border:none;border-radius:999px;
                         padding:5px 13px;cursor:pointer;font-weight:700;">
            🔊 Listen · Լսել
          </button>"""
    if spell_word:
        letters = ", ".join(list(spell_word.replace("'", " apostrophe ").upper()))
        buttons += f"""
          <button onclick="say_{uid}({json.dumps(letters)}, 0.55)"
                  style="background:#C0316E;color:white;border:none;border-radius:999px;
                         padding:5px 13px;cursor:pointer;font-weight:700;">
            🔤 Spell · Հեգել
          </button>"""
    components.html(
        f"""
        <div style="display:flex; gap:8px; font-family:sans-serif;">{buttons}</div>
        <script>
          function say_{uid}(text, rate) {{
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(text);
            u.lang = 'en-US'; u.rate = rate;
            window.speechSynthesis.speak(u);
          }}
        </script>
        """,
        height=44,
    )


# ---------------------------------------------------------------- EXERCISES
# Question fields by type (topic sets a default "mode", a question can
# override it with "type"):
#  "write":     prompt, full, word, hy, why, [accept] -> type the WHOLE sentence
#  "choice":    prompt, options, word(=answer), full, hy, why -> tap to answer
#  "translate": hy, full, accept, why -> write the English sentence
#  "spell":     word, hy, why -> 🎧 listen to the spelling, type the word
LEVELS = {
    "📘 File 1 · be, թվեր, երկրներ": {
        "positive": {
            "emoji": "🌞", "title": "be (+): I am, you are...", "title_hy": "Հաստատական be",
            "ef": "English File 1A", "mode": "write",
            "tip_en": "**am / is / are**: I → **am** · he / she / it → **is** · you / we / they → **are**. ✍️ Write the WHOLE sentence!",
            "tip_hy": "Գրիր ամբողջ նախադասությունը՝ լրացնելով բացը։ Օրինակ՝ «I am a student.» Վերջակետը կարող ես չդնել։",
            "questions": [
                {"prompt": "I ___ a student.", "full": "I am a student.", "word": "am", "hy": "Ես ուսանող եմ։", "why": "I-ի հետ միշտ am է։"},
                {"prompt": "She ___ from Yerevan.", "full": "She is from Yerevan.", "word": "is", "hy": "Նա Երևանից է։", "why": "She → is (եզակի 3-րդ դեմք)։"},
                {"prompt": "Today ___ Monday.", "full": "Today is Monday.", "word": "is", "hy": "Այսօր երկուշաբթի է։", "why": "Today = it → is։"},
                {"prompt": "They ___ happy today.", "full": "They are happy today.", "word": "are", "hy": "Նրանք այսօր ուրախ են։", "why": "They → are (հոգնակի)։"},
                {"prompt": "He ___ my brother.", "full": "He is my brother.", "word": "is", "hy": "Նա իմ եղբայրն է։", "why": "He → is։"},
                {"prompt": "We ___ in class.", "full": "We are in class.", "word": "are", "hy": "Մենք դասարանում ենք։", "why": "We → are։"},
                {"prompt": "You ___ very kind.", "full": "You are very kind.", "word": "are", "hy": "Դու շատ բարի ես։", "why": "You → are։"},
                {"prompt": "My parents ___ teachers.", "full": "My parents are teachers.", "word": "are", "hy": "Իմ ծնողներն ուսուցիչներ են։", "why": "My parents = they → are։"},
            ],
        },
        "negative": {
            "emoji": "🚫", "title": "be (–): isn't, aren't", "title_hy": "Ժխտական be",
            "ef": "English File 1B", "mode": "write",
            "tip_en": "Add **not**: *is not = isn't*, *are not = aren't*, *am not*. Both long and short forms are correct!",
            "tip_hy": "Ժխտականը՝ բայ + not։ Կարող ես գրել և՛ «is not», և՛ «isn't»։ Գրիր ամբողջ նախադասությունը։",
            "questions": [
                {"prompt": "I ___ tired.", "full": "I am not tired.", "word": "am not", "hy": "Ես հոգնած չեմ։", "why": "I → am not («amn't» ձև չկա)։"},
                {"prompt": "She ___ from Italy.", "full": "She is not from Italy.", "word": "isn't", "hy": "Նա Իտալիայից չէ։", "why": "is + not = isn't։"},
                {"prompt": "We ___ from Spain.", "full": "We are not from Spain.", "word": "aren't", "hy": "Մենք Իսպանիայից չենք։", "why": "are + not = aren't։"},
                {"prompt": "It ___ Sunday today.", "full": "It is not Sunday today.", "word": "isn't", "hy": "Այսօր կիրակի չէ։", "why": "It → isn't։"},
                {"prompt": "They ___ at school.", "full": "They are not at school.", "word": "aren't", "hy": "Նրանք դպրոցում չեն։", "why": "They → aren't։"},
                {"prompt": "He ___ my teacher.", "full": "He is not my teacher.", "word": "isn't", "hy": "Նա իմ ուսուցիչը չէ։", "why": "He → isn't։"},
                {"prompt": "You ___ late.", "full": "You are not late.", "word": "aren't", "hy": "Դու չես ուշացել։", "why": "You → aren't։"},
                {"prompt": "The shop ___ open.", "full": "The shop is not open.", "word": "isn't", "hy": "Խանութը բաց չէ։", "why": "The shop = it → isn't։"},
            ],
        },
        "questions_be": {
            "emoji": "❓", "title": "be (?): Are you...? Where are...?", "title_hy": "Հարցեր be բայով",
            "ef": "English File 1B", "mode": "write",
            "tip_en": "**am / is / are** goes *before* the subject: *Are you...? Where are you from?*",
            "tip_hy": "Հարցում be բայը դրվում է ենթակայից առաջ։ Գրիր ամբողջ հարցը, «?»-ը կարող ես չդնել։",
            "questions": [
                {"prompt": "___ you a student?", "full": "Are you a student?", "word": "are", "hy": "Դու ուսանո՞ղ ես։", "why": "you → Are ...?"},
                {"prompt": "___ ___ you from?", "full": "Where are you from?", "word": "where", "hy": "Որտեղի՞ց ես դու։", "why": "Where + are you։"},
                {"prompt": "___ she from Russia?", "full": "Is she from Russia?", "word": "is", "hy": "Նա Ռուսաստանի՞ց է։", "why": "she → Is ...?"},
                {"prompt": "___ ___ your name?", "full": "What is your name?", "word": "what", "hy": "Ի՞նչ է քո անունը։", "why": "What + is։"},
                {"prompt": "___ they in class?", "full": "Are they in class?", "word": "are", "hy": "Նրանք դասարանո՞ւմ են։", "why": "they → Are ...?"},
                {"prompt": "___ ___ you today?", "full": "How are you today?", "word": "how", "hy": "Ինչպե՞ս ես այսօր։", "why": "How + are you։"},
                {"prompt": "___ I right?", "full": "Am I right?", "word": "am", "hy": "Ես ճի՞շտ եմ։", "why": "I → Am ...?"},
                {"prompt": "___ ___ your teacher from?", "full": "Where is your teacher from?", "word": "teacher", "hy": "Որտեղի՞ց է քո ուսուցիչը։", "why": "teacher → Where is ...?"},
            ],
        },
        "days": {
            "emoji": "📅", "title": "Days of the Week", "title_hy": "Շաբաթվա օրերը",
            "ef": "English File 1A", "mode": "choice",
            "tip_en": "Monday → Tuesday → Wednesday → Thursday → Friday → Saturday → Sunday. Days start with a CAPITAL letter!",
            "tip_hy": "Երկուշաբթի → ... → Կիրակի։ Անգլերենում օրերի անունները գրվում են ՄԵԾԱՏԱՌՈՎ։",
            "questions": [
                {"prompt": "Today is Monday. Tomorrow is ___.", "options": ["Tuesday", "Thursday", "Sunday"], "word": "Tuesday", "full": "Tomorrow is Tuesday.", "hy": "Վաղը երեքշաբթի է։", "why": "Monday → Tuesday (երեքշաբթի)։"},
                {"prompt": "The day after Friday is ___.", "options": ["Saturday", "Sunday", "Thursday"], "word": "Saturday", "full": "The day after Friday is Saturday.", "hy": "Ուրբաթից հետո շաբաթ օրն է։", "why": "Friday → Saturday (շաբաթ)։"},
                {"prompt": "Saturday and ___ are the weekend. 🎉", "options": ["Sunday", "Monday", "Friday"], "word": "Sunday", "full": "Saturday and Sunday are the weekend.", "hy": "Շաբաթ և կիրակի հանգստյան օրերն են։", "why": "weekend = շաբաթ + կիրակի։"},
                {"prompt": "The day before Wednesday is ___.", "options": ["Tuesday", "Thursday", "Monday"], "word": "Tuesday", "full": "The day before Wednesday is Tuesday.", "hy": "Չորեքշաբթիից առաջ երեքշաբթին է։", "why": "before = առաջ։"},
                {"prompt": "After Wednesday comes ___.", "options": ["Thursday", "Tuesday", "Saturday"], "word": "Thursday", "full": "After Wednesday comes Thursday.", "hy": "Չորեքշաբթիից հետո հինգշաբթին է։", "why": "Thursday = հինգշաբթի։"},
                {"prompt": "The first day of the working week is ___.", "options": ["Monday", "Sunday", "Friday"], "word": "Monday", "full": "The first day of the working week is Monday.", "hy": "Աշխատանքային շաբաթը սկսվում է երկուշաբթի։", "why": "Monday = երկուշաբթի։"},
                {"prompt": "The day before Saturday is ___.", "options": ["Friday", "Sunday", "Tuesday"], "word": "Friday", "full": "The day before Saturday is Friday.", "hy": "Շաբաթից առաջ ուրբաթն է։", "why": "Friday = ուրբաթ։"},
            ],
        },
        "numbers": {
            "emoji": "🔢", "title": "Numbers 0–100", "title_hy": "Թվեր 0–100",
            "ef": "English File 1A–1B", "mode": "choice",
            "tip_en": "Careful with tricky pairs: thir**teen** (13) / thir**ty** (30), fif**teen** (15) / fif**ty** (50)!",
            "tip_hy": "Ուշադիր՝ 13/30, 15/50, 17/70 զույգերը շատ նման են։ -teen՝ 13-19, -ty՝ 20-90։",
            "questions": [
                {"prompt": "13 is ___.", "options": ["thirteen", "thirty"], "word": "thirteen", "full": "Thirteen.", "hy": "13 = տասներեք։", "why": "13 → thirTEEN, 30 → THIRty։"},
                {"prompt": "50 is ___.", "options": ["fifteen", "fifty"], "word": "fifty", "full": "Fifty.", "hy": "50 = հիսուն։", "why": "50 → fifty, 15 → fifteen։"},
                {"prompt": "90 is ___.", "options": ["nineteen", "ninety"], "word": "ninety", "full": "Ninety.", "hy": "90 = իննսուն։", "why": "90 → ninety, 19 → nineteen։"},
                {"prompt": "17 is ___.", "options": ["seventy", "seventeen"], "word": "seventeen", "full": "Seventeen.", "hy": "17 = տասնյոթ։", "why": "17 → seventeen, 70 → seventy։"},
                {"type": "write", "prompt": "✍️ Write the number 12 in words.", "full": "twelve", "word": "twelve", "hy": "12 = տասներկու։", "why": "12 = twelve։"},
                {"type": "write", "prompt": "✍️ Write the number 20 in words.", "full": "twenty", "word": "twenty", "hy": "20 = քսան։", "why": "20 = twenty։"},
                {"type": "write", "prompt": "✍️ Write the number 8 in words.", "full": "eight", "word": "eight", "hy": "8 = ութ։", "why": "8 = eight (gh-ն չի կարդացվում)։"},
                {"type": "write", "prompt": "✍️ Write the number 100 in words.", "full": "one hundred", "accept": ["one hundred", "a hundred", "hundred"], "word": "hundred", "hy": "100 = հարյուր։", "why": "100 = one hundred / a hundred։"},
            ],
        },
        "countries": {
            "emoji": "🌍", "title": "Countries & Nationalities", "title_hy": "Երկրներ և ազգություններ",
            "ef": "English File 1B", "mode": "choice",
            "tip_en": "Armenia → Armenia**n** · Spain → Spani**sh** · Italy → Itali**an** · France → Fren**ch**. Capital letters!",
            "tip_hy": "Երկիր → ազգություն. Armenia → Armenian։ Ազգությունները նույնպես մեծատառով են։",
            "questions": [
                {"prompt": "I am from Armenia. I am ___.", "options": ["Armenian", "Armenia", "English"], "word": "Armenian", "full": "I am Armenian.", "hy": "Ես հայ եմ։", "why": "Armenia (երկիր) → Armenian (ազգություն)։"},
                {"prompt": "She is from Spain. She is ___.", "options": ["Spanish", "Italian", "French"], "word": "Spanish", "full": "She is Spanish.", "hy": "Նա իսպանացի է։", "why": "Spain → Spanish։"},
                {"prompt": "He is from Italy. He is ___.", "options": ["Italian", "Spanish", "Russian"], "word": "Italian", "full": "He is Italian.", "hy": "Նա իտալացի է։", "why": "Italy → Italian։"},
                {"prompt": "They are from Russia. They are ___.", "options": ["Russian", "German", "English"], "word": "Russian", "full": "They are Russian.", "hy": "Նրանք ռուս են։", "why": "Russia → Russian։"},
                {"prompt": "We are from England. We are ___.", "options": ["English", "American", "French"], "word": "English", "full": "We are English.", "hy": "Մենք անգլիացի ենք։", "why": "England → English։"},
                {"prompt": "She is from France. She is ___.", "options": ["French", "Spanish", "Italian"], "word": "French", "full": "She is French.", "hy": "Նա ֆրանսիացի է։", "why": "France → French։"},
                {"prompt": "He is from the USA. He is ___.", "options": ["American", "English", "Russian"], "word": "American", "full": "He is American.", "hy": "Նա ամերիկացի է։", "why": "the USA → American։"},
                {"prompt": "People from Georgia are ___.", "options": ["Georgian", "German", "Armenian"], "word": "Georgian", "full": "People from Georgia are Georgian.", "hy": "Վրաստանցիները վրացի են։", "why": "Georgia → Georgian։"},
            ],
        },
        "possessives": {
            "emoji": "💝", "title": "My / Your / His / Her ...", "title_hy": "Իմ / Քո / Նրա ...",
            "ef": "English File 1C", "mode": "choice",
            "tip_en": "**my**=իմ · **your**=քո · **his**=նրա(👦) · **her**=նրա(👧) · **its**=դրա · **our**=մեր · **their**=նրանց",
            "tip_hy": "Ուշադրություն՝ his՝ տղամարդու համար, her՝ կնոջ։",
            "questions": [
                {"prompt": "I have a cat. ___ cat is white.", "options": ["My", "Your", "His", "Her"], "word": "My", "full": "My cat is white.", "hy": "Իմ կատուն սպիտակ է։", "why": "I → my։"},
                {"prompt": "She has a car. ___ car is red.", "options": ["My", "His", "Her", "Their"], "word": "Her", "full": "Her car is red.", "hy": "Նրա մեքենան կարմիր է։", "why": "She → her։"},
                {"prompt": "He has a dog. ___ dog is funny.", "options": ["Her", "His", "Its", "Our"], "word": "His", "full": "His dog is funny.", "hy": "Նրա շունը զվարճալի է։", "why": "He → his։"},
                {"prompt": "We have a house. ___ house is big.", "options": ["My", "Our", "Their", "Your"], "word": "Our", "full": "Our house is big.", "hy": "Մեր տունը մեծ է։", "why": "We → our։"},
                {"prompt": "They have children. ___ children are small.", "options": ["Our", "His", "Their", "My"], "word": "Their", "full": "Their children are small.", "hy": "Նրանց երեխաները փոքր են։", "why": "They → their։"},
                {"prompt": "What is ___ name? — I'm Ani.", "options": ["your", "his", "her", "their"], "word": "your", "full": "What is your name?", "hy": "Ի՞նչ է քո անունը։", "why": "you → your։"},
            ],
        },
        "classroom": {
            "emoji": "🏫", "title": "Classroom Language", "title_hy": "Դասարանային արտահայտություններ",
            "ef": "English File 1C", "mode": "choice",
            "tip_en": "Useful phrases for your English lesson: *open your books, listen, repeat, how do you spell...?*",
            "tip_hy": "Օգտակար արտահայտություններ անգլերենի դասի համար։",
            "questions": [
                {"prompt": "___ your books, please. 📖", "options": ["Open", "Listen", "Sit"], "word": "Open", "full": "Open your books, please.", "hy": "Բացեք ձեր գրքերը։", "why": "open = բացել։"},
                {"prompt": "Please ___ down. 🪑", "options": ["sit", "stand", "open"], "word": "sit", "full": "Please sit down.", "hy": "Խնդրում եմ, նստեք։", "why": "sit down = նստել։"},
                {"prompt": "I don't understand. Can you ___ that, please?", "options": ["repeat", "close", "sit"], "word": "repeat", "full": "Can you repeat that, please?", "hy": "Կարո՞ղ եք կրկնել։", "why": "repeat = կրկնել։"},
                {"prompt": "How do you ___ 'window'? — W-I-N-D-O-W.", "options": ["spell", "open", "say"], "word": "spell", "full": "How do you spell 'window'?", "hy": "Ինչպե՞ս է հեգվում «window»-ն։", "why": "spell = հեգել։"},
                {"prompt": "___ to the audio. 🎧", "options": ["Listen", "Look", "Write"], "word": "Listen", "full": "Listen to the audio.", "hy": "Լսեք ձայնագրությունը։", "why": "listen = լսել։"},
                {"prompt": "Please turn ___ your phone. 📵", "options": ["off", "on", "up"], "word": "off", "full": "Please turn off your phone.", "hy": "Անջատեք հեռախոսը։", "why": "turn off = անջատել։"},
            ],
        },
        "alphabet": {
            "emoji": "🎧", "title": "The Alphabet: Listen & Spell", "title_hy": "Այբուբեն. լսիր և գրիր",
            "ef": "English File 1C", "mode": "spell",
            "tip_en": "Press **🔤 Spell**, listen to the letters, and type the word. Press it as many times as you need!",
            "tip_hy": "Սեղմիր «Spell» կոճակը, լսիր տառերը և գրիր բառը։ Հուշումը՝ բառի հայերեն իմաստն է։",
            "questions": [
                {"word": "book", "hy": "գիրք", "why": "B-O-O-K = book (գիրք)։"},
                {"word": "phone", "hy": "հեռախոս", "why": "P-H-O-N-E = phone։ ph = ֆ հնչյուն։"},
                {"word": "table", "hy": "սեղան", "why": "T-A-B-L-E = table։"},
                {"word": "friend", "hy": "ընկեր", "why": "F-R-I-E-N-D = friend։"},
                {"word": "window", "hy": "պատուհան", "why": "W-I-N-D-O-W = window։"},
                {"word": "Sunday", "hy": "կիրակի", "why": "S-U-N-D-A-Y = Sunday։ Օրերը մեծատառով են։"},
            ],
        },
        "translate1": {
            "emoji": "🇦🇲", "title": "Translate: About Me", "title_hy": "Թարգմանիր՝ իմ մասին",
            "ef": "English File 1A–1C", "mode": "translate",
            "tip_en": "Read the Armenian sentence and **write it in English**. Short forms (I'm, isn't...) are also correct!",
            "tip_hy": "Կարդա հայերենը և գրիր անգլերեն։ Կրճատ ձևերը նույնպես ճիշտ են։",
            "questions": [
                {"hy": "Ես Հայաստանից եմ։", "full": "I am from Armenia.", "accept": ["I am from Armenia."], "why": "I + am + from + Armenia։"},
                {"hy": "Իմ անունը Անի է։", "full": "My name is Ani.", "accept": ["My name is Ani.", "I am Ani."], "why": "My name + is + Ani։"},
                {"hy": "Ինչպե՞ս ես։", "full": "How are you?", "accept": ["How are you?"], "why": "How + are + you։"},
                {"hy": "Նա Իսպանիայից է։", "full": "She is from Spain.", "accept": ["She is from Spain.", "He is from Spain."], "why": "she/he + is + from Spain։"},
                {"hy": "Այսօր երկուշաբթի է։", "full": "Today is Monday.", "accept": ["Today is Monday.", "It is Monday today.", "It is Monday."], "why": "Today is + օր (մեծատառով)։"},
                {"hy": "Դու Իտալիայի՞ց ես։", "full": "Are you from Italy?", "accept": ["Are you from Italy?"], "why": "Հարց՝ Are-ը սկզբում։"},
                {"hy": "Մենք ուսանողներ ենք։", "full": "We are students.", "accept": ["We are students."], "why": "We + are + students (հոգնակի -s)։"},
                {"hy": "Նրանք հոգնած չեն։", "full": "They are not tired.", "accept": ["They are not tired."], "why": "Ժխտական՝ are not / aren't։"},
            ],
        },
    },
    "📗 File 2 · Իրեր, ածականներ": {
        "a_an_plural": {
            "emoji": "🔤", "title": "a / an & Plurals", "title_hy": "a / an և հոգնակի",
            "ef": "English File 2A", "mode": "choice",
            "tip_en": "**a** + consonant sound (*a book*), **an** + vowel sound (*an apple*). Plural: +**s**, or +**es** after -ch/-sh/-s/-x.",
            "tip_hy": "a՝ բաղաձայնից առաջ, an՝ ձայնավորից (a, e, i, o, u)։ Հոգնակի՝ +s / +es։",
            "questions": [
                {"prompt": "It's ___ apple. 🍎", "options": ["a", "an"], "word": "an", "full": "It's an apple.", "hy": "Սա խնձոր է։", "why": "apple → ձայնավոր → an։"},
                {"prompt": "It's ___ book. 📖", "options": ["a", "an"], "word": "a", "full": "It's a book.", "hy": "Սա գիրք է։", "why": "book → բաղաձայն → a։"},
                {"prompt": "It's ___ umbrella. ☂️", "options": ["a", "an"], "word": "an", "full": "It's an umbrella.", "hy": "Սա անձրևանոց է։", "why": "umbrella → ձայնավոր → an։"},
                {"prompt": "It's ___ pen. 🖊️", "options": ["a", "an"], "word": "a", "full": "It's a pen.", "hy": "Սա գրիչ է։", "why": "pen → բաղաձայն → a։"},
                {"type": "write", "prompt": "✍️ one book → two ___", "full": "books", "word": "books", "hy": "մեկ գիրք → երկու գիրք", "why": "book + s = books։"},
                {"type": "write", "prompt": "✍️ one watch → two ___", "full": "watches", "word": "watches", "hy": "մեկ ժամացույց → երկու ժամացույց", "why": "-ch-ից հետո → +es։"},
                {"type": "write", "prompt": "✍️ one box → three ___", "full": "boxes", "word": "boxes", "hy": "մեկ արկղ → երեք արկղ", "why": "-x-ից հետո → +es։"},
                {"type": "write", "prompt": "✍️ one key → four ___", "full": "keys", "word": "keys", "hy": "մեկ բանալի → չորս բանալի", "why": "key + s = keys։"},
            ],
        },
        "in_on_under": {
            "emoji": "📦", "title": "in / on / under", "title_hy": "Մեջ / վրա / տակ",
            "ef": "English File 2A", "mode": "choice",
            "tip_en": "**in** = մեջ (inside) · **on** = վրա (on top) · **under** = տակ (below)",
            "tip_hy": "in՝ մեջ, on՝ վրա, under՝ տակ։",
            "questions": [
                {"prompt": "The phone is ___ the bag. (👜 inside)", "options": ["in", "on", "under"], "word": "in", "full": "The phone is in the bag.", "hy": "Հեռախոսը պայուսակի մեջ է։", "why": "մեջ → in։"},
                {"prompt": "The book is ___ the table. (⬆️ on top)", "options": ["in", "on", "under"], "word": "on", "full": "The book is on the table.", "hy": "Գիրքը սեղանի վրա է։", "why": "վրա → on։"},
                {"prompt": "The cat is ___ the bed. (⬇️ below)", "options": ["in", "on", "under"], "word": "under", "full": "The cat is under the bed.", "hy": "Կատուն մահճակալի տակ է։", "why": "տակ → under։"},
                {"prompt": "The keys are ___ the box. (📦 inside)", "options": ["in", "on", "under"], "word": "in", "full": "The keys are in the box.", "hy": "Բանալիներն արկղի մեջ են։", "why": "մեջ → in։"},
                {"prompt": "The picture is ___ the wall. 🖼️", "options": ["in", "on", "under"], "word": "on", "full": "The picture is on the wall.", "hy": "Նկարը պատին է։", "why": "Պատին → on the wall։"},
                {"prompt": "The dog is ___ the chair. (⬇️)", "options": ["in", "on", "under"], "word": "under", "full": "The dog is under the chair.", "hy": "Շունը աթոռի տակ է։", "why": "տակ → under։"},
            ],
        },
        "this_these": {
            "emoji": "👉", "title": "This / That / These / Those", "title_hy": "Այս / Այն / Սրանք / Նրանք",
            "ef": "English File 2A", "mode": "choice",
            "tip_en": "**this** = այս (near, 1) · **that** = այն (far, 1) · **these** = սրանք (near, many) · **those** = նրանք (far, many)",
            "tip_hy": "this՝ մոտ, եզակի · that՝ հեռու, եզակի · these՝ մոտ, հոգնակի · those՝ հեռու, հոգնակի։",
            "questions": [
                {"prompt": "___ is my book. (📍 here)", "options": ["This", "That", "These", "Those"], "word": "This", "full": "This is my book.", "hy": "Սա իմ գիրքն է։", "why": "Մոտ + եզակի → this։"},
                {"prompt": "___ are my keys. (📍 here)", "options": ["This", "That", "These", "Those"], "word": "These", "full": "These are my keys.", "hy": "Սրանք իմ բանալիներն են։", "why": "Մոտ + հոգնակի → these։"},
                {"prompt": "___ is our school. (🔭 over there)", "options": ["This", "That", "These", "Those"], "word": "That", "full": "That is our school.", "hy": "Այն մեր դպրոցն է։", "why": "Հեռու + եզակի → that։"},
                {"prompt": "___ are mountains. (🔭 over there)", "options": ["This", "That", "These", "Those"], "word": "Those", "full": "Those are mountains.", "hy": "Այնտեղ սարեր են։", "why": "Հեռու + հոգնակի → those։"},
                {"prompt": "___ apples are sweet. (📍 in my hand)", "options": ["This", "That", "These", "Those"], "word": "These", "full": "These apples are sweet.", "hy": "Այս խնձորները քաղցր են։", "why": "Մոտ + հոգնակի → these։"},
                {"prompt": "___ car is fast. (🔭 far away)", "options": ["This", "That", "These", "Those"], "word": "That", "full": "That car is fast.", "hy": "Այն մեքենան արագ է։", "why": "Հեռու + եզակի → that։"},
            ],
        },
        "opposites": {
            "emoji": "↔️", "title": "Adjectives: Opposites", "title_hy": "Ածականներ. հականիշներ",
            "ef": "English File 2B", "mode": "choice",
            "tip_en": "big↔small · cheap↔expensive · fast↔slow · new↔old · hot↔cold · good↔bad · easy↔difficult",
            "tip_hy": "մեծ↔փոքր, էժան↔թանկ, արագ↔դանդաղ, նոր↔հին, տաք↔սառը, լավ↔վատ, հեշտ↔դժվար։",
            "questions": [
                {"prompt": "An elephant is big. A mouse is ___. 🐭", "options": ["small", "fast", "old"], "word": "small", "full": "A mouse is small.", "hy": "Մուկը փոքր է։", "why": "big ↔ small։"},
                {"prompt": "A Ferrari is expensive. A bus ticket is ___. 🎫", "options": ["cheap", "hot", "new"], "word": "cheap", "full": "A bus ticket is cheap.", "hy": "Տոմսը էժան է։", "why": "expensive ↔ cheap։"},
                {"prompt": "A tortoise is slow. A rabbit is ___. 🐇", "options": ["fast", "small", "cold"], "word": "fast", "full": "A rabbit is fast.", "hy": "Նապաստակը արագ է։", "why": "slow ↔ fast։"},
                {"prompt": "This phone is new. That phone is ___. 📞", "options": ["old", "big", "easy"], "word": "old", "full": "That phone is old.", "hy": "Այն հեռախոսը հին է։", "why": "new ↔ old։"},
                {"prompt": "Ice is cold. Fire is ___. 🔥", "options": ["hot", "slow", "cheap"], "word": "hot", "full": "Fire is hot.", "hy": "Կրակը տաք է։", "why": "cold ↔ hot։"},
                {"prompt": "The film is good. The weather is ___. 🌧️", "options": ["bad", "fast", "small"], "word": "bad", "full": "The weather is bad.", "hy": "Եղանակը վատ է։", "why": "good ↔ bad։"},
                {"prompt": "English is easy. Chinese is ___. 😅", "options": ["difficult", "cheap", "old"], "word": "difficult", "full": "Chinese is difficult.", "hy": "Չինարենը դժվար է։", "why": "easy ↔ difficult։"},
                {"prompt": "The window is open. The door is ___. 🚪", "options": ["closed", "new", "hot"], "word": "closed", "full": "The door is closed.", "hy": "Դուռը փակ է։", "why": "open ↔ closed։"},
            ],
        },
        "imperatives_feelings": {
            "emoji": "😊", "title": "Imperatives & Feelings", "title_hy": "Հրամաններ և զգացումներ",
            "ef": "English File 2C", "mode": "choice",
            "tip_en": "Imperative = verb without a subject: *Open the door! Don't worry!* Feelings: hungry, thirsty, tired, cold...",
            "tip_hy": "Հրամայականը՝ բայն առանց ենթակայի։ Ժխտականը՝ Don't + բայ։",
            "questions": [
                {"prompt": "___ the door, please. 🚪", "options": ["Open", "Opens", "Opening"], "word": "Open", "full": "Open the door, please.", "hy": "Բացիր դուռը։", "why": "Հրամայական՝ բայի հիմքը։"},
                {"prompt": "___ worry! Be happy. 😊", "options": ["Don't", "Doesn't", "Not"], "word": "Don't", "full": "Don't worry! Be happy.", "hy": "Մի անհանգստացիր։", "why": "Ժխտական հրաման՝ Don't + բայ։"},
                {"prompt": "I'm ___ — I want to eat! 🍽️", "options": ["hungry", "thirsty", "tired"], "word": "hungry", "full": "I'm hungry.", "hy": "Ես քաղցած եմ։", "why": "hungry = քաղցած։"},
                {"prompt": "She's ___ — she wants to sleep. 😴", "options": ["tired", "angry", "cold"], "word": "tired", "full": "She's tired.", "hy": "Նա հոգնած է։", "why": "tired = հոգնած։"},
                {"prompt": "I'm ___ — I want water! 🥤", "options": ["thirsty", "hungry", "happy"], "word": "thirsty", "full": "I'm thirsty.", "hy": "Ես ծարավ եմ։", "why": "thirsty = ծարավ։"},
                {"prompt": "___ quiet, please. 🤫", "options": ["Be", "Is", "Are"], "word": "Be", "full": "Be quiet, please.", "hy": "Լուռ մնացեք։", "why": "Be + ածական հրամայականում։"},
            ],
        },
        "colors_fun": {
            "emoji": "🌈", "title": "Fun: Colors & Numbers", "title_hy": "Գույներ և թվեր",
            "ef": "Fun break!", "mode": "choice",
            "tip_en": "A fun break! Pick the right color or number. 🎨",
            "tip_hy": "Զվարճալի ընդմիջում՝ ընտրիր ճիշտ գույնը կամ թիվը։",
            "questions": [
                {"prompt": "🍎 The apple is ___.", "options": ["red", "blue", "green"], "word": "red", "full": "The apple is red.", "hy": "Խնձորը կարմիր է։", "why": "red = կարմիր։"},
                {"prompt": "🌊 The sea is ___.", "options": ["yellow", "blue", "black"], "word": "blue", "full": "The sea is blue.", "hy": "Ծովը կապույտ է։", "why": "blue = կապույտ։"},
                {"prompt": "🌻 The sunflower is ___.", "options": ["yellow", "purple", "white"], "word": "yellow", "full": "The sunflower is yellow.", "hy": "Արևածաղիկը դեղին է։", "why": "yellow = դեղին։"},
                {"prompt": "🖐️ I have ___ fingers on one hand.", "options": ["three", "five", "ten"], "word": "five", "full": "I have five fingers on one hand.", "hy": "Հինգ մատ։", "why": "five = հինգ։"},
                {"prompt": "🕷️ A spider has ___ legs.", "options": ["six", "eight", "four"], "word": "eight", "full": "A spider has eight legs.", "hy": "Ութ ոտք։", "why": "eight = ութ։"},
                {"prompt": "🌳 The grass is ___.", "options": ["green", "red", "orange"], "word": "green", "full": "The grass is green.", "hy": "Խոտը կանաչ է։", "why": "green = կանաչ։"},
                {"prompt": "📅 A week has ___ days.", "options": ["five", "seven", "ten"], "word": "seven", "full": "A week has seven days.", "hy": "Յոթ օր։", "why": "seven = յոթ։"},
            ],
        },
        "translate_f2": {
            "emoji": "🎓", "title": "Translate: Things Around Me", "title_hy": "Թարգմանություն",
            "ef": "English File 2A–2B", "mode": "translate",
            "tip_en": "Everyday things and where they are. Remember **a/an**, plurals with **-s**, and *in / on / under*!",
            "tip_hy": "Հիշիր a/an հոդերը, հոգնակի -s-ը և in/on/under-ը։",
            "questions": [
                {"hy": "Սա գիրք է։", "full": "This is a book.", "accept": ["This is a book.", "It is a book."], "why": "This is + a + book։"},
                {"hy": "Հեռախոսը սեղանի վրա է։", "full": "The phone is on the table.", "accept": ["The phone is on the table."], "why": "վրա → on։"},
                {"hy": "Կատուն աթոռի տակ է։", "full": "The cat is under the chair.", "accept": ["The cat is under the chair."], "why": "տակ → under։"},
                {"hy": "Բանալիները պայուսակի մեջ են։", "full": "The keys are in the bag.", "accept": ["The keys are in the bag."], "why": "keys → հոգնակի → are։"},
                {"hy": "Սրանք իմ գրքերն են։", "full": "These are my books.", "accept": ["These are my books."], "why": "Մոտ + հոգնակի → these + are։"},
                {"hy": "Իմ մեքենան նոր չէ։", "full": "My car is not new.", "accept": ["My car is not new.", "My car is old."], "why": "Ժխտական՝ isn't / is not։"},
                {"hy": "Այս խնձորը կարմիր է։", "full": "This apple is red.", "accept": ["This apple is red."], "why": "This + գոյական + is + ածական։"},
                {"hy": "Դա էժան հեռախոս է։", "full": "It is a cheap phone.", "accept": ["It is a cheap phone.", "That is a cheap phone.", "This is a cheap phone."], "why": "Ածականը գոյականից ԱՌԱՋ է՝ a cheap phone։"},
            ],
        },
    },
    "📙 File 3 · Present Simple": {
        "pres_simple": {
            "emoji": "🏃", "title": "Present Simple (+ and –)", "title_hy": "Ներկա ժամանակ (+/–)",
            "ef": "English File 3A", "mode": "choice",
            "tip_en": "**he / she / it** → verb + **s** (*she works*). Negative: **don't / doesn't** + verb (*he doesn't like*).",
            "tip_hy": "He/she/it-ի հետ բային ավելանում է -s։ Ժխտականը՝ don't/doesn't + բայ (առանց s)։",
            "questions": [
                {"prompt": "I ___ in Yerevan.", "options": ["live", "lives"], "word": "live", "full": "I live in Yerevan.", "hy": "Ես ապրում եմ Երևանում։", "why": "I → առանց s։"},
                {"prompt": "She ___ English and Russian.", "options": ["speak", "speaks"], "word": "speaks", "full": "She speaks English and Russian.", "hy": "Նա խոսում է անգլերեն և ռուսերեն։", "why": "She → +s։"},
                {"prompt": "We ___ TV in the evening.", "options": ["watch", "watches"], "word": "watch", "full": "We watch TV in the evening.", "hy": "Երեկոյան հեռուստացույց ենք դիտում։", "why": "We → առանց s։"},
                {"prompt": "He ___ like coffee.", "options": ["doesn't", "don't"], "word": "doesn't", "full": "He doesn't like coffee.", "hy": "Նա սուրճ չի սիրում։", "why": "He → doesn't։"},
                {"prompt": "They ___ work on Sundays.", "options": ["don't", "doesn't"], "word": "don't", "full": "They don't work on Sundays.", "hy": "Կիրակի չեն աշխատում։", "why": "They → don't։"},
                {"prompt": "My father ___ in a bank.", "options": ["works", "work"], "word": "works", "full": "My father works in a bank.", "hy": "Հայրս բանկում է աշխատում։", "why": "father = he → +s։"},
            ],
        },
        "jobs_questions": {
            "emoji": "👩‍⚕️", "title": "Do/Does? & Jobs", "title_hy": "Հարցեր և մասնագիտություններ",
            "ef": "English File 3B", "mode": "choice",
            "tip_en": "Questions: **Do** + I/you/we/they · **Does** + he/she/it. Jobs: teacher, doctor, nurse, waiter...",
            "tip_hy": "Do՝ I/you/we/they, Does՝ he/she/it։ Does-ից հետո բայն ԱՌԱՆՑ s է։",
            "questions": [
                {"prompt": "___ you work in a hospital?", "options": ["Do", "Does"], "word": "Do", "full": "Do you work in a hospital?", "hy": "Դու հիվանդանոցո՞ւմ ես աշխատում։", "why": "you → Do։"},
                {"prompt": "___ she like her job?", "options": ["Does", "Do"], "word": "Does", "full": "Does she like her job?", "hy": "Նա սիրո՞ւմ է իր աշխատանքը։", "why": "she → Does։"},
                {"prompt": "A person who teaches is a ___.", "options": ["teacher", "doctor", "waiter"], "word": "teacher", "full": "A person who teaches is a teacher.", "hy": "Ուսուցիչ։", "why": "teach → teacher։"},
                {"prompt": "A ___ works in a restaurant. 🍽️", "options": ["waiter", "nurse", "driver"], "word": "waiter", "full": "A waiter works in a restaurant.", "hy": "Մատուցող։", "why": "waiter = մատուցող։"},
                {"prompt": "A ___ helps sick people in a hospital. 🏥", "options": ["nurse", "singer", "pilot"], "word": "nurse", "full": "A nurse helps sick people.", "hy": "Բուժքույր։", "why": "nurse = բուժքույր։"},
                {"prompt": "What ___ he do? — He's a doctor.", "options": ["does", "do", "is"], "word": "does", "full": "What does he do?", "hy": "Ի՞նչ գործ է անում նա։", "why": "What does he do? = Ի՞նչ մասնագիտություն ունի։"},
            ],
        },
        "question_words": {
            "emoji": "🧩", "title": "Word Order in Questions", "title_hy": "Հարցերի բառակարգ",
            "ef": "English File 3C", "mode": "choice",
            "tip_en": "Question word + do/does + subject + verb: *Where do you live?*",
            "tip_hy": "Հարցական բառ + do/does + ենթակա + բայ։",
            "questions": [
                {"prompt": "___ do you live?", "options": ["Where", "What", "Who"], "word": "Where", "full": "Where do you live?", "hy": "Որտե՞ղ ես ապրում։", "why": "Where = որտեղ։"},
                {"prompt": "___ do you get up? — At 7 o'clock.", "options": ["What time", "Where", "Who"], "word": "What time", "full": "What time do you get up?", "hy": "Ժամը քանիսի՞ն ես արթնանում։", "why": "What time = ժամը քանիսին։"},
                {"prompt": "Choose the correct question:", "options": ["Where do you live?", "Where you live?"], "word": "Where do you live?", "full": "Where do you live?", "hy": "Որտե՞ղ ես ապրում։", "why": "Հարցում պետք է do/does։"},
                {"prompt": "___ music do you like?", "options": ["What", "Who", "Where"], "word": "What", "full": "What music do you like?", "hy": "Ի՞նչ երաժշտություն ես սիրում։", "why": "What = ինչ։"},
                {"prompt": "___ do you go to the gym? — On Mondays.", "options": ["When", "Who", "What"], "word": "When", "full": "When do you go to the gym?", "hy": "Ե՞րբ ես գնում մարզասրահ։", "why": "When = երբ։"},
                {"prompt": "Choose the correct question:", "options": ["Does she work here?", "Does she works here?"], "word": "Does she work here?", "full": "Does she work here?", "hy": "Նա այստե՞ղ է աշխատում։", "why": "Does-ից հետո բայն առանց s է։"},
            ],
        },
        "translate_f3": {
            "emoji": "🇦🇲", "title": "Translate: Daily Life", "title_hy": "Թարգմանիր՝ առօրյա",
            "ef": "English File 3A–3C", "mode": "translate",
            "tip_en": "Remember: he/she/it → verb + **s**; negatives with **don't/doesn't**; questions with **do/does**.",
            "tip_hy": "Հիշիր՝ he/she/it → +s, ժխտականը՝ don't/doesn't, հարցերը՝ do/does։",
            "questions": [
                {"hy": "Ես Երևանում եմ ապրում։", "full": "I live in Yerevan.", "accept": ["I live in Yerevan."], "why": "I + live + in Yerevan։"},
                {"hy": "Նա սուրճ չի խմում։", "full": "He does not drink coffee.", "accept": ["He does not drink coffee.", "She does not drink coffee."], "why": "doesn't + drink (առանց s)։"},
                {"hy": "Դու աշխատո՞ւմ ես։", "full": "Do you work?", "accept": ["Do you work?"], "why": "Հարց՝ Do + you + work։"},
                {"hy": "Իմ քույրը դպրոցում է աշխատում։", "full": "My sister works at a school.", "accept": ["My sister works at a school.", "My sister works in a school.", "My sister works at school."], "why": "sister = she → works։"},
                {"hy": "Մենք երաժշտություն ենք սիրում։", "full": "We like music.", "accept": ["We like music.", "We love music."], "why": "We + like + music։"},
                {"hy": "Որտե՞ղ ես դու աշխատում։", "full": "Where do you work?", "accept": ["Where do you work?"], "why": "Where + do + you + work։"},
            ],
        },
    },
    "📕 File 4 · Ընտանիք, նախդիրներ": {
        "family_poss": {
            "emoji": "👨‍👩‍👧", "title": "Family & Possessive 's", "title_hy": "Ընտանիք և 's",
            "ef": "English File 4A", "mode": "choice",
            "tip_en": "Whose...? Use **'s** for possession: *Anna's car* = Աննայի մեքենան. Family: grandmother, uncle, aunt, cousin...",
            "tip_hy": "Պատկանելությունը՝ անուն + 's։ Anna's car = Աննայի մեքենան։",
            "questions": [
                {"prompt": "My mother's mother is my ___.", "options": ["grandmother", "aunt", "sister"], "word": "grandmother", "full": "My mother's mother is my grandmother.", "hy": "Տատիկ։", "why": "grandmother = տատիկ։"},
                {"prompt": "My father's brother is my ___.", "options": ["uncle", "cousin", "nephew"], "word": "uncle", "full": "My father's brother is my uncle.", "hy": "Հորեղբայր։", "why": "uncle = հորեղբայր/քեռի։"},
                {"prompt": "This is ___ car.", "options": ["Anna's", "Anna", "Annas"], "word": "Anna's", "full": "This is Anna's car.", "hy": "Սա Աննայի մեքենան է։", "why": "Պատկանելություն → 's։"},
                {"prompt": "My uncle's children are my ___.", "options": ["cousins", "brothers", "parents"], "word": "cousins", "full": "My uncle's children are my cousins.", "hy": "Զարմիկներ։", "why": "cousin = զարմիկ/զարմուհի։"},
                {"prompt": "Whose phone is this? — It's ___.", "options": ["Aram's", "Aram", "the Aram"], "word": "Aram's", "full": "It's Aram's phone.", "hy": "Սա Արամի հեռախոսն է։", "why": "Whose = ո՞ւմ → պատասխանը 's-ով։"},
                {"prompt": "My mother's sister is my ___.", "options": ["aunt", "grandmother", "cousin"], "word": "aunt", "full": "My mother's sister is my aunt.", "hy": "Մորաքույր։", "why": "aunt = մորաքույր/հորաքույր։"},
            ],
        },
        "prep_time": {
            "emoji": "⏰", "title": "at / in / on (time)", "title_hy": "Ժամանակի նախդիրներ",
            "ef": "English File 4B", "mode": "choice",
            "tip_en": "**at** + time (*at 7*), **on** + day (*on Monday*), **in** + month/part of day (*in July, in the morning*). But: *at night*!",
            "tip_hy": "at՝ ժամ, on՝ օր, in՝ ամիս/օրվա մաս։ Բացառություն՝ at night։",
            "questions": [
                {"prompt": "I get up ___ 7 o'clock.", "options": ["at", "on", "in"], "word": "at", "full": "I get up at 7 o'clock.", "hy": "Ժամը 7-ին։", "why": "ժամ → at։"},
                {"prompt": "We have English ___ Monday.", "options": ["on", "at", "in"], "word": "on", "full": "We have English on Monday.", "hy": "Երկուշաբթի օրը։", "why": "օր → on։"},
                {"prompt": "She drinks coffee ___ the morning.", "options": ["in", "at", "on"], "word": "in", "full": "She drinks coffee in the morning.", "hy": "Առավոտյան։", "why": "օրվա մաս → in։"},
                {"prompt": "My birthday is ___ July.", "options": ["in", "on", "at"], "word": "in", "full": "My birthday is in July.", "hy": "Հուլիսին։", "why": "ամիս → in։"},
                {"prompt": "I sleep ___ night.", "options": ["at", "in", "on"], "word": "at", "full": "I sleep at night.", "hy": "Գիշերը։", "why": "Բացառություն՝ at night։"},
                {"prompt": "They play football ___ the weekend.", "options": ["at", "in", "under"], "word": "at", "full": "They play football at the weekend.", "hy": "Հանգստյան օրերին։", "why": "at the weekend (բրիտ.) / on the weekend (ամեր.)։"},
            ],
        },
        "freq_adverbs": {
            "emoji": "🔁", "title": "always / usually / never", "title_hy": "Հաճախականության մակբայներ",
            "ef": "English File 4C", "mode": "choice",
            "tip_en": "always (100%) → usually → often → sometimes → never (0%). Position: BEFORE the verb, but AFTER *be*.",
            "tip_hy": "always՝ միշտ, usually՝ սովորաբար, often՝ հաճախ, sometimes՝ երբեմն, never՝ երբեք։ Դիրքը՝ բայից առաջ, be-ից հետո։",
            "questions": [
                {"prompt": "I ___ drink coffee — every day!", "options": ["always", "never", "sometimes"], "word": "always", "full": "I always drink coffee.", "hy": "Միշտ սուրճ եմ խմում։", "why": "every day → always (միշտ)։"},
                {"prompt": "He ___ eats meat — he is a vegetarian.", "options": ["never", "always", "usually"], "word": "never", "full": "He never eats meat.", "hy": "Երբեք միս չի ուտում։", "why": "vegetarian → never (երբեք)։"},
                {"prompt": "Choose the correct sentence:", "options": ["She is often late.", "She often is late."], "word": "She is often late.", "full": "She is often late.", "hy": "Նա հաճախ ուշանում է։", "why": "be-ից ՀԵՏՈ → is often։"},
                {"prompt": "We ___ go to the cinema — one time a month.", "options": ["sometimes", "always", "never"], "word": "sometimes", "full": "We sometimes go to the cinema.", "hy": "Երբեմն։", "why": "sometimes = երբեմն։"},
                {"prompt": "Choose the correct sentence:", "options": ["I am always happy.", "I always am happy."], "word": "I am always happy.", "full": "I am always happy.", "hy": "Միշտ ուրախ եմ։", "why": "be-ից հետո → am always։"},
                {"prompt": "___ do you play football? — Every Saturday.", "options": ["How often", "How much", "How many"], "word": "How often", "full": "How often do you play football?", "hy": "Որքա՞ն հաճախ։", "why": "How often = որքան հաճախ։"},
            ],
        },
    },
    "📔 File 5 · can, Present Continuous": {
        "can_cant": {
            "emoji": "💪", "title": "can / can't", "title_hy": "Կարողանալ",
            "ef": "English File 5A", "mode": "choice",
            "tip_en": "**can** + verb (no *to*, no *-s*): *She can swim.* Negative: **can't**. Questions: *Can you...?*",
            "tip_hy": "can + բայ (առանց to, առանց s)։ Ժխտականը՝ can't։ Հարցը՝ Can you...?",
            "questions": [
                {"prompt": "She ___ swim very well. 🏊", "options": ["can", "cans"], "word": "can", "full": "She can swim very well.", "hy": "Նա լավ է լողում։", "why": "can-ը երբեք s չի ստանում։"},
                {"prompt": "I ___ speak Chinese. 🙅", "options": ["can't", "don't can"], "word": "can't", "full": "I can't speak Chinese.", "hy": "Չինարեն չեմ կարողանում խոսել։", "why": "Ժխտականը՝ can't (ոչ don't can)։"},
                {"prompt": "___ you help me, please?", "options": ["Can", "Do"], "word": "Can", "full": "Can you help me, please?", "hy": "Կարո՞ղ ես օգնել։", "why": "Խնդրանք → Can you...?"},
                {"prompt": "He can ___ the guitar. 🎸", "options": ["play", "plays", "to play"], "word": "play", "full": "He can play the guitar.", "hy": "Կիթառ է նվագում։", "why": "can-ից հետո՝ բայի հիմքը։"},
                {"prompt": "___ I open the window?", "options": ["Can", "Am"], "word": "Can", "full": "Can I open the window?", "hy": "Կարո՞ղ եմ բացել պատուհանը։", "why": "Թույլտվություն → Can I...?"},
                {"prompt": "Birds ___ fly. 🐦", "options": ["can", "can't"], "word": "can", "full": "Birds can fly.", "hy": "Թռչունները կարող են թռչել։", "why": "can = կարողանալ։"},
            ],
        },
        "pres_cont": {
            "emoji": "🎬", "title": "Present Continuous", "title_hy": "Ներկա շարունակական",
            "ef": "English File 5B", "mode": "choice",
            "tip_en": "**am / is / are + verb-ing** for NOW: *I am reading. It is raining.*",
            "tip_hy": "am/is/are + բայ+ing՝ հենց հիմա կատարվող գործողության համար։",
            "questions": [
                {"prompt": "I ___ reading a book now.", "options": ["am", "is", "are"], "word": "am", "full": "I am reading a book now.", "hy": "Հիմա գիրք եմ կարդում։", "why": "I → am + -ing։"},
                {"prompt": "She is ___ TV.", "options": ["watching", "watch", "watches"], "word": "watching", "full": "She is watching TV.", "hy": "Հեռուստացույց է դիտում։", "why": "is + watching։"},
                {"prompt": "They ___ playing football now.", "options": ["are", "is", "am"], "word": "are", "full": "They are playing football now.", "hy": "Հիմա ֆուտբոլ են խաղում։", "why": "They → are։"},
                {"prompt": "Look! It ___ raining. 🌧️", "options": ["is", "are", "am"], "word": "is", "full": "It is raining.", "hy": "Անձրև է գալիս։", "why": "It → is + -ing։"},
                {"prompt": "We are ___ English now.", "options": ["studying", "study", "studies"], "word": "studying", "full": "We are studying English now.", "hy": "Հիմա անգլերեն ենք սովորում։", "why": "are + studying։"},
                {"prompt": "___ you listening to me?", "options": ["Are", "Do", "Is"], "word": "Are", "full": "Are you listening to me?", "hy": "Ինձ լսո՞ւմ ես։", "why": "Հարց՝ Are + you + -ing։"},
            ],
        },
        "simple_vs_cont": {
            "emoji": "⚖️", "title": "Simple or Continuous?", "title_hy": "Ո՞ր ժամանակը",
            "ef": "English File 5C", "mode": "choice",
            "tip_en": "**every day / usually** → Present Simple. **now / Look! / at the moment** → Present Continuous.",
            "tip_hy": "Ամեն օր/սովորաբար → Simple։ Հիմա/այս պահին → Continuous։",
            "questions": [
                {"prompt": "She ___ now. 😴", "options": ["is sleeping", "sleeps"], "word": "is sleeping", "full": "She is sleeping now.", "hy": "Հիմա քնած է։", "why": "now → Continuous։"},
                {"prompt": "I ___ coffee every morning.", "options": ["drink", "am drinking"], "word": "drink", "full": "I drink coffee every morning.", "hy": "Ամեն առավոտ։", "why": "every morning → Simple։"},
                {"prompt": "Listen! The baby ___.", "options": ["is crying", "cries"], "word": "is crying", "full": "The baby is crying.", "hy": "Երեխան լալիս է։", "why": "Listen! → հիմա → Continuous։"},
                {"prompt": "He usually ___ to work by bus.", "options": ["goes", "is going"], "word": "goes", "full": "He usually goes to work by bus.", "hy": "Սովորաբար։", "why": "usually → Simple։"},
                {"prompt": "We ___ dinner at the moment.", "options": ["are having", "have"], "word": "are having", "full": "We are having dinner at the moment.", "hy": "Այս պահին ընթրում ենք։", "why": "at the moment → Continuous։"},
                {"prompt": "On Sundays they ___ football.", "options": ["play", "are playing"], "word": "play", "full": "On Sundays they play football.", "hy": "Կիրակի օրերին։", "why": "On Sundays → սովորություն → Simple։"},
            ],
        },
    },
    "📒 File 6 · Դերանուններ, ամսաթվեր": {
        "object_pronouns": {
            "emoji": "🎯", "title": "me / him / her / them", "title_hy": "Ուղիղ խնդրի դերանուններ",
            "ef": "English File 6A", "mode": "choice",
            "tip_en": "I→**me** · you→**you** · he→**him** · she→**her** · it→**it** · we→**us** · they→**them**",
            "tip_hy": "Ես→ինձ (me), նա→նրան (him/her), մենք→մեզ (us), նրանք→նրանց (them)։",
            "questions": [
                {"prompt": "I love my mother. I love ___.", "options": ["her", "she", "him"], "word": "her", "full": "I love her.", "hy": "Սիրում եմ նրան (մայրիկիս)։", "why": "she → her։"},
                {"prompt": "This is Aram. Do you know ___?", "options": ["him", "he", "his"], "word": "him", "full": "Do you know him?", "hy": "Ճանաչո՞ւմ ես նրան։", "why": "he → him։"},
                {"prompt": "We are here! Look at ___!", "options": ["us", "we", "our"], "word": "us", "full": "Look at us!", "hy": "Նայիր մեզ։", "why": "we → us։"},
                {"prompt": "I like these songs. I listen to ___ every day.", "options": ["them", "they", "their"], "word": "them", "full": "I listen to them every day.", "hy": "Լսում եմ դրանք ամեն օր։", "why": "they → them։"},
                {"prompt": "You are my friend. I like ___.", "options": ["you", "your", "yours"], "word": "you", "full": "I like you.", "hy": "Հավանում եմ քեզ։", "why": "you → you (նույնն է)։"},
                {"prompt": "This is my dog. I play with ___.", "options": ["it", "its", "them"], "word": "it", "full": "I play with it.", "hy": "Խաղում եմ նրա հետ։", "why": "it → it։"},
            ],
        },
        "like_ing_dates": {
            "emoji": "📆", "title": "like + -ing & Dates", "title_hy": "Սիրել + -ing, ամսաթվեր",
            "ef": "English File 6B", "mode": "choice",
            "tip_en": "like / love / hate + verb**-ing**: *I like dancing.* Dates: 1st=first, 2nd=second, 3rd=third, 4th=fourth...",
            "tip_hy": "like/love/hate-ից հետո՝ բայ+ing։ Ամսաթվերը՝ դասական թվեր (first, second, third...)։",
            "questions": [
                {"prompt": "I like ___ to music. 🎵", "options": ["listening", "listen", "listens"], "word": "listening", "full": "I like listening to music.", "hy": "Սիրում եմ երաժշտություն լսել։", "why": "like + -ing։"},
                {"prompt": "She loves ___. 💃", "options": ["dancing", "dance", "dances"], "word": "dancing", "full": "She loves dancing.", "hy": "Սիրում է պարել։", "why": "love + -ing։"},
                {"prompt": "1st = ___", "options": ["first", "one", "once"], "word": "first", "full": "First.", "hy": "Առաջին։", "why": "1st = first։"},
                {"prompt": "3rd = ___", "options": ["third", "three", "thirty"], "word": "third", "full": "Third.", "hy": "Երրորդ։", "why": "3rd = third։"},
                {"prompt": "My birthday is on May the ___ (2nd).", "options": ["second", "two", "twice"], "word": "second", "full": "My birthday is on May the second.", "hy": "Մայիսի երկուսին։", "why": "Ամսաթվերում՝ դասական թիվ։"},
                {"prompt": "We hate ___ up early. 😩", "options": ["getting", "get", "gets"], "word": "getting", "full": "We hate getting up early.", "hy": "Ատում ենք շուտ արթնանալ։", "why": "hate + -ing։"},
            ],
        },
        "be_or_do": {
            "emoji": "🔀", "title": "Revision: be or do?", "title_hy": "Կրկնություն. be թե do",
            "ef": "English File 6C", "mode": "choice",
            "tip_en": "**be** for who/where/what someone IS. **do/does** for actions with other verbs.",
            "tip_hy": "be՝ երբ չկա այլ բայ, do/does՝ երբ կա գործողության բայ։",
            "questions": [
                {"prompt": "___ you like jazz?", "options": ["Do", "Are"], "word": "Do", "full": "Do you like jazz?", "hy": "Ջազ սիրո՞ւմ ես։", "why": "Կա բայ (like) → Do։"},
                {"prompt": "___ you a student?", "options": ["Are", "Do"], "word": "Are", "full": "Are you a student?", "hy": "Դու ուսանո՞ղ ես։", "why": "Չկա այլ բայ → Are։"},
                {"prompt": "Where ___ she from?", "options": ["is", "does"], "word": "is", "full": "Where is she from?", "hy": "Որտեղի՞ց է նա։", "why": "be from → is։"},
                {"prompt": "What time ___ you get up?", "options": ["do", "are"], "word": "do", "full": "What time do you get up?", "hy": "Ե՞րբ ես արթնանում։", "why": "Բայ (get up) → do։"},
                {"prompt": "___ he working now?", "options": ["Is", "Does"], "word": "Is", "full": "Is he working now?", "hy": "Հիմա աշխատո՞ւմ է։", "why": "-ing → be (Is)։"},
                {"prompt": "___ they speak English?", "options": ["Do", "Are"], "word": "Do", "full": "Do they speak English?", "hy": "Անգլերեն խոսո՞ւմ են։", "why": "Բայ (speak) → Do։"},
            ],
        },
    },
    "📘 File 7 · Անցյալ. was/were, -ed": {
        "was_were": {
            "emoji": "⏪", "title": "was / were", "title_hy": "be-ի անցյալը",
            "ef": "English File 7A", "mode": "choice",
            "tip_en": "Past of *be*: I/he/she/it → **was** · you/we/they → **were**. *I was at home yesterday.*",
            "tip_hy": "be-ի անցյալը՝ was (I/he/she/it), were (you/we/they)։",
            "questions": [
                {"prompt": "I ___ at home yesterday.", "options": ["was", "were"], "word": "was", "full": "I was at home yesterday.", "hy": "Երեկ տանն էի։", "why": "I → was։"},
                {"prompt": "They ___ at the party.", "options": ["were", "was"], "word": "were", "full": "They were at the party.", "hy": "Երեկույթին էին։", "why": "They → were։"},
                {"prompt": "She ___ tired last night.", "options": ["was", "were"], "word": "was", "full": "She was tired last night.", "hy": "Երեկ գիշեր հոգնած էր։", "why": "She → was։"},
                {"prompt": "___ you at school yesterday?", "options": ["Were", "Was"], "word": "Were", "full": "Were you at school yesterday?", "hy": "Երեկ դպրոցո՞ւմ էիր։", "why": "you → Were ...?"},
                {"prompt": "We ___ not in Yerevan last week.", "options": ["were", "was"], "word": "were", "full": "We were not in Yerevan last week.", "hy": "Անցյալ շաբաթ Երևանում չէինք։", "why": "We → were (+not = weren't)։"},
                {"prompt": "It ___ cold yesterday. 🥶", "options": ["was", "were"], "word": "was", "full": "It was cold yesterday.", "hy": "Երեկ ցուրտ էր։", "why": "It → was։"},
            ],
        },
        "past_regular": {
            "emoji": "📼", "title": "Past Simple: -ed", "title_hy": "Անցյալ՝ կանոնավոր բայեր",
            "ef": "English File 7B", "mode": "choice",
            "tip_en": "Regular verbs: + **-ed** (*played, worked*). If the verb ends in -y → **-ied** (*study → studied*).",
            "tip_hy": "Կանոնավոր բայեր՝ +ed։ y-ով վերջացողները՝ -ied (study → studied)։",
            "questions": [
                {"prompt": "I ___ football yesterday.", "options": ["played", "play"], "word": "played", "full": "I played football yesterday.", "hy": "Երեկ ֆուտբոլ խաղացի։", "why": "yesterday → անցյալ → +ed։"},
                {"prompt": "She ___ in a bank in 2020.", "options": ["worked", "works"], "word": "worked", "full": "She worked in a bank in 2020.", "hy": "2020-ին բանկում էր աշխատում։", "why": "in 2020 → անցյալ։"},
                {"type": "write", "prompt": "✍️ live → (past) ___", "full": "lived", "word": "lived", "hy": "ապրել → ապրում էր", "why": "e-ով վերջացող → +d։"},
                {"prompt": "We ___ a film last night.", "options": ["watched", "watch"], "word": "watched", "full": "We watched a film last night.", "hy": "Երեկ երեկոյան ֆիլմ դիտեցինք։", "why": "last night → անցյալ։"},
                {"type": "write", "prompt": "✍️ study → (past) ___", "full": "studied", "word": "studied", "hy": "սովորել → սովորում էր", "why": "y → ied։"},
                {"prompt": "They ___ to music two hours ago.", "options": ["listened", "listen"], "word": "listened", "full": "They listened to music two hours ago.", "hy": "Երկու ժամ առաջ երաժշտություն լսեցին։", "why": "ago → անցյալ։"},
            ],
        },
        "past_irregular": {
            "emoji": "🎲", "title": "Past Simple: go→went...", "title_hy": "Անկանոն բայեր",
            "ef": "English File 7C", "mode": "choice",
            "tip_en": "Irregular verbs change completely: go→**went**, have→**had**, get→**got**, see→**saw**.",
            "tip_hy": "Անկանոն բայերն ամբողջովին փոխվում են՝ go→went, have→had, get→got։",
            "questions": [
                {"prompt": "go → ___", "options": ["went", "goed"], "word": "went", "full": "Went.", "hy": "գնալ → գնաց", "why": "go → went (անկանոն)։"},
                {"prompt": "have → ___", "options": ["had", "haved"], "word": "had", "full": "Had.", "hy": "ունենալ → ուներ", "why": "have → had։"},
                {"prompt": "get → ___", "options": ["got", "getted"], "word": "got", "full": "Got.", "hy": "ստանալ → ստացավ", "why": "get → got։"},
                {"prompt": "see → ___", "options": ["saw", "seed"], "word": "saw", "full": "Saw.", "hy": "տեսնել → տեսավ", "why": "see → saw։"},
                {"prompt": "I ___ to Gyumri last summer.", "options": ["went", "go"], "word": "went", "full": "I went to Gyumri last summer.", "hy": "Անցյալ ամառ Գյումրի գնացի։", "why": "last summer → went։"},
                {"prompt": "She ___ a great time at the party. 🥳", "options": ["had", "has"], "word": "had", "full": "She had a great time at the party.", "hy": "Հիանալի ժամանակ անցկացրեց։", "why": "have a great time → had։"},
            ],
        },
    },
    "📗 File 8 · Անցյալ, there is/are": {
        "past_mixed": {
            "emoji": "🕵️", "title": "Past Simple: Mixed", "title_hy": "Անցյալ՝ խառը",
            "ef": "English File 8A", "mode": "choice",
            "tip_en": "Mix of regular and irregular. Remember: after **didn't** the verb is in the BASE form (*I didn't like it*).",
            "tip_hy": "Կանոնավոր և անկանոն բայեր միասին։ didn't-ից հետո բայի ՀԻՄՔՆ է։",
            "questions": [
                {"prompt": "We ___ a taxi to the airport.", "options": ["took", "taked"], "word": "took", "full": "We took a taxi to the airport.", "hy": "Տաքսի վերցրինք։", "why": "take → took։"},
                {"prompt": "She ___ me an email yesterday.", "options": ["sent", "sended"], "word": "sent", "full": "She sent me an email yesterday.", "hy": "Երեկ նամակ ուղարկեց։", "why": "send → sent։"},
                {"prompt": "I ___ TV and then went to bed.", "options": ["watched", "watch"], "word": "watched", "full": "I watched TV and then went to bed.", "hy": "Դիտեցի ու քնեցի։", "why": "watch → watched (կանոնավոր)։"},
                {"prompt": "He ___ up at 6 yesterday. ⏰", "options": ["got", "getted"], "word": "got", "full": "He got up at 6 yesterday.", "hy": "Ժամը 6-ին արթնացավ։", "why": "get up → got up։"},
                {"prompt": "They ___ a pizza last night. 🍕", "options": ["made", "maked"], "word": "made", "full": "They made a pizza last night.", "hy": "Պիցցա պատրաստեցին։", "why": "make → made։"},
                {"prompt": "I didn't ___ the film.", "options": ["like", "liked"], "word": "like", "full": "I didn't like the film.", "hy": "Ֆիլմը դուրս չեկավ։", "why": "didn't + բայի հիմքը (ոչ liked)։"},
            ],
        },
        "there_is_are": {
            "emoji": "🏠", "title": "there is / there are", "title_hy": "Կա / կան",
            "ef": "English File 8B", "mode": "choice",
            "tip_en": "**There is** + singular · **There are** + plural. some (+) / any (– and ?). House: sofa, bedroom, kitchen...",
            "tip_hy": "There is՝ եզակի (կա), There are՝ հոգնակի (կան)։ some՝ հաստատականում, any՝ ժխտականում և հարցում։",
            "questions": [
                {"prompt": "___ a sofa in the living room. 🛋️", "options": ["There is", "There are"], "word": "There is", "full": "There is a sofa in the living room.", "hy": "Հյուրասենյակում բազմոց կա։", "why": "a sofa → եզակի → is։"},
                {"prompt": "___ two bedrooms in the flat.", "options": ["There are", "There is"], "word": "There are", "full": "There are two bedrooms in the flat.", "hy": "Երկու ննջասենյակ կա։", "why": "two → հոգնակի → are։"},
                {"prompt": "___ there a garden? 🌳", "options": ["Is", "Are"], "word": "Is", "full": "Is there a garden?", "hy": "Այգի կա՞։", "why": "a garden → Is there...?"},
                {"prompt": "There aren't ___ chairs in the kitchen.", "options": ["any", "some"], "word": "any", "full": "There aren't any chairs in the kitchen.", "hy": "Աթոռներ չկան։", "why": "Ժխտական → any։"},
                {"prompt": "There are ___ pictures on the wall.", "options": ["some", "any"], "word": "some", "full": "There are some pictures on the wall.", "hy": "Պատին նկարներ կան։", "why": "Հաստատական → some։"},
                {"prompt": "___ a big window in my room.", "options": ["There is", "There are"], "word": "There is", "full": "There is a big window in my room.", "hy": "Մեծ պատուհան կա։", "why": "a window → եզակի → is։"},
            ],
        },
        "there_was_were": {
            "emoji": "🏰", "title": "there was/were & Place", "title_hy": "Կար / կային, տեղ",
            "ef": "English File 8C", "mode": "choice",
            "tip_en": "Past: **there was** (singular) / **there were** (plural). Place: next to, between, behind, in front of...",
            "tip_hy": "Անցյալում՝ there was (կար), there were (կային)։ Տեղի նախդիրներ՝ next to (կողքին), between (միջև)...",
            "questions": [
                {"prompt": "___ a hotel here in 1990.", "options": ["There was", "There were"], "word": "There was", "full": "There was a hotel here in 1990.", "hy": "1990-ին այստեղ հյուրանոց կար։", "why": "a hotel → եզակի → was։"},
                {"prompt": "___ many people at the concert.", "options": ["There were", "There was"], "word": "There were", "full": "There were many people at the concert.", "hy": "Համերգին շատ մարդ կար։", "why": "many people → հոգնակի → were։"},
                {"prompt": "___ there a TV in the room?", "options": ["Was", "Were"], "word": "Was", "full": "Was there a TV in the room?", "hy": "Հեռուստացույց կա՞ր։", "why": "a TV → Was there...?"},
                {"prompt": "There ___ any shops here 50 years ago.", "options": ["weren't", "wasn't"], "word": "weren't", "full": "There weren't any shops here 50 years ago.", "hy": "Խանութներ չկային։", "why": "shops → հոգնակի → weren't։"},
                {"prompt": "The cat is ___ the sofa and the table.", "options": ["between", "on", "at"], "word": "between", "full": "The cat is between the sofa and the table.", "hy": "Բազմոցի և սեղանի ՄԻՋԵՎ։", "why": "between = միջև։"},
                {"prompt": "The bank is ___ the supermarket.", "options": ["next to", "under", "in"], "word": "next to", "full": "The bank is next to the supermarket.", "hy": "Սուպերմարկետի ԿՈՂՔԻՆ։", "why": "next to = կողքին։"},
            ],
        },
    },
    "📙 File 9 · Ուտելիք, համեմատություն": {
        "food_some_any": {
            "emoji": "🍽️", "title": "Food: some / any", "title_hy": "Ուտելիք. some/any",
            "ef": "English File 9A", "mode": "choice",
            "tip_en": "Countable: *an apple, two eggs*. Uncountable: *milk, rice, water* (no plural!). some (+), any (– / ?).",
            "tip_hy": "Հաշվելի՝ apple, egg։ Անհաշվելի՝ milk, rice, water (հոգնակի չունեն)։ some՝ (+), any՝ (–/՞)։",
            "questions": [
                {"prompt": "There is ___ milk in the fridge. 🥛", "options": ["some", "any"], "word": "some", "full": "There is some milk in the fridge.", "hy": "Կաթ կա։", "why": "Հաստատական → some։"},
                {"prompt": "Is there ___ sugar?", "options": ["any", "some"], "word": "any", "full": "Is there any sugar?", "hy": "Շաքար կա՞։", "why": "Հարց → any։"},
                {"prompt": "I'd like ___ apple. 🍎", "options": ["an", "a", "any"], "word": "an", "full": "I'd like an apple.", "hy": "Խնձոր կուզեի։", "why": "apple → ձայնավոր → an։"},
                {"prompt": "We don't have ___ eggs. 🥚", "options": ["any", "some"], "word": "any", "full": "We don't have any eggs.", "hy": "Ձու չունենք։", "why": "Ժխտական → any։"},
                {"prompt": "Rice is ___ noun.", "options": ["an uncountable", "a countable"], "word": "an uncountable", "full": "Rice is an uncountable noun.", "hy": "Բրինձն անհաշվելի է։", "why": "rice, water, milk → անհաշվելի։"},
                {"prompt": "There are ___ tomatoes. 🍅", "options": ["some", "any"], "word": "some", "full": "There are some tomatoes.", "hy": "Լոլիկներ կան։", "why": "Հաստատական → some։"},
            ],
        },
        "much_many": {
            "emoji": "⚖️", "title": "how much / how many", "title_hy": "Որքա՞ն",
            "ef": "English File 9B", "mode": "choice",
            "tip_en": "**How many** + countable plural (*apples*) · **How much** + uncountable (*water, money, time*). a lot of = շատ.",
            "tip_hy": "How many՝ հաշվելիների հետ, How much՝ անհաշվելիների (ջուր, փող, ժամանակ)։",
            "questions": [
                {"prompt": "How ___ water do you drink? 💧", "options": ["much", "many"], "word": "much", "full": "How much water do you drink?", "hy": "Որքա՞ն ջուր ես խմում։", "why": "water → անհաշվելի → much։"},
                {"prompt": "How ___ apples are there?", "options": ["many", "much"], "word": "many", "full": "How many apples are there?", "hy": "Քանի՞ խնձոր կա։", "why": "apples → հաշվելի → many։"},
                {"prompt": "There isn't ___ time. ⏳", "options": ["much", "many"], "word": "much", "full": "There isn't much time.", "hy": "Շատ ժամանակ չկա։", "why": "time → անհաշվելի → much։"},
                {"prompt": "I have a lot ___ friends.", "options": ["of", "off", "for"], "word": "of", "full": "I have a lot of friends.", "hy": "Շատ ընկերներ ունեմ։", "why": "a lot OF = շատ։"},
                {"prompt": "How ___ money is it? 💰", "options": ["much", "many"], "word": "much", "full": "How much money is it?", "hy": "Որքա՞ն փող է։", "why": "money → անհաշվելի → much։"},
                {"prompt": "There aren't ___ people here.", "options": ["many", "much"], "word": "many", "full": "There aren't many people here.", "hy": "Շատ մարդ չկա։", "why": "people → հաշվելի → many։"},
            ],
        },
        "comparatives": {
            "emoji": "📈", "title": "Comparatives: bigger, better", "title_hy": "Համեմատական աստիճան",
            "ef": "English File 9C", "mode": "choice",
            "tip_en": "Short adjectives: +**er** (*bigger, faster*). Long adjectives: **more** + adj (*more expensive*). good→better, bad→worse!",
            "tip_hy": "Կարճ ածական՝ +er, երկար՝ more + ածական։ Անկանոն՝ good→better, bad→worse։",
            "questions": [
                {"prompt": "Yerevan is ___ than Gyumri.", "options": ["bigger", "more big"], "word": "bigger", "full": "Yerevan is bigger than Gyumri.", "hy": "Երևանն ավելի մեծ է։", "why": "big → bigger (+er, կրկնակի g)։"},
                {"prompt": "This phone is ___ than that one.", "options": ["more expensive", "expensiver"], "word": "more expensive", "full": "This phone is more expensive than that one.", "hy": "Ավելի թանկ է։", "why": "Երկար ածական → more։"},
                {"prompt": "good → ___", "options": ["better", "gooder"], "word": "better", "full": "Better.", "hy": "լավ → ավելի լավ", "why": "Անկանոն՝ good → better։"},
                {"prompt": "bad → ___", "options": ["worse", "badder"], "word": "worse", "full": "Worse.", "hy": "վատ → ավելի վատ", "why": "Անկանոն՝ bad → worse։"},
                {"type": "write", "prompt": "✍️ big → ___ (than)", "full": "bigger", "word": "bigger", "hy": "մեծ → ավելի մեծ", "why": "big → bigger (կրկնակի g)։"},
                {"prompt": "My car is ___ than your car. 🚗", "options": ["faster", "more fast"], "word": "faster", "full": "My car is faster than your car.", "hy": "Ավելի արագ է։", "why": "fast → faster։"},
            ],
        },
    },
    "📕 File 10 · Գերադրական, going to": {
        "superlatives": {
            "emoji": "🏆", "title": "Superlatives: the biggest", "title_hy": "Գերադրական աստիճան",
            "ef": "English File 10A", "mode": "choice",
            "tip_en": "**the** + adj+**est** (*the biggest*) or **the most** + long adj (*the most expensive*). good→the best, bad→the worst.",
            "tip_hy": "the + ածական+est, կամ the most + երկար ածական։ Անկանոն՝ the best, the worst։",
            "questions": [
                {"prompt": "Everest is ___ mountain in the world. 🏔️", "options": ["the highest", "the higher"], "word": "the highest", "full": "Everest is the highest mountain in the world.", "hy": "Ամենաբարձր լեռը։", "why": "Գերադրական → the + est։"},
                {"prompt": "This is ___ restaurant in the city.", "options": ["the best", "the goodest"], "word": "the best", "full": "This is the best restaurant in the city.", "hy": "Լավագույն ռեստորանը։", "why": "good → the best։"},
                {"prompt": "expensive → the ___", "options": ["most expensive", "expensivest"], "word": "most expensive", "full": "The most expensive.", "hy": "ամենաթանկը", "why": "Երկար ածական → the most։"},
                {"prompt": "It's ___ building in Yerevan.", "options": ["the oldest", "the most old"], "word": "the oldest", "full": "It's the oldest building in Yerevan.", "hy": "Ամենահին շենքը։", "why": "old → the oldest։"},
                {"prompt": "bad → the ___", "options": ["worst", "baddest"], "word": "worst", "full": "The worst.", "hy": "ամենավատը", "why": "bad → the worst։"},
                {"prompt": "She is ___ student in the class. 🌟", "options": ["the youngest", "the most young"], "word": "the youngest", "full": "She is the youngest student in the class.", "hy": "Ամենաերիտասարդ ուսանողը։", "why": "young → the youngest։"},
            ],
        },
        "going_to": {
            "emoji": "🔮", "title": "be going to (future)", "title_hy": "Ապառնի՝ going to",
            "ef": "English File 10B–10C", "mode": "choice",
            "tip_en": "Plans & predictions: **am/is/are + going to + verb**: *I am going to visit Paris.*",
            "tip_hy": "Ծրագրեր և կանխատեսումներ՝ am/is/are + going to + բայ։",
            "questions": [
                {"prompt": "I ___ going to visit Paris next year.", "options": ["am", "is", "are"], "word": "am", "full": "I am going to visit Paris next year.", "hy": "Հաջորդ տարի Փարիզ եմ գնալու։", "why": "I → am going to։"},
                {"prompt": "She is going ___ study medicine.", "options": ["to", "for", "at"], "word": "to", "full": "She is going to study medicine.", "hy": "Բժշկություն է սովորելու։", "why": "going TO + բայ։"},
                {"prompt": "They ___ going to play tennis tomorrow. 🎾", "options": ["are", "is", "am"], "word": "are", "full": "They are going to play tennis tomorrow.", "hy": "Վաղը թենիս են խաղալու։", "why": "They → are։"},
                {"prompt": "___ you going to watch the film?", "options": ["Are", "Do", "Is"], "word": "Are", "full": "Are you going to watch the film?", "hy": "Ֆիլմը դիտելո՞ւ ես։", "why": "Հարց՝ Are you going to...?"},
                {"prompt": "Look at the clouds! It is going to ___. 🌧️", "options": ["rain", "rains", "raining"], "word": "rain", "full": "It is going to rain.", "hy": "Անձրև է գալու։", "why": "going to + բայի հիմքը։"},
                {"prompt": "We aren't going ___ tonight.", "options": ["to go out", "go out"], "word": "to go out", "full": "We aren't going to go out tonight.", "hy": "Այս երեկո դուրս չենք գալու։", "why": "going + to + բայ։"},
            ],
        },
    },
    "📔 File 11 · Մակբայներ, հոդեր": {
        "adverbs_ly": {
            "emoji": "🎭", "title": "Adverbs: slowly, well...", "title_hy": "Մակբայներ",
            "ef": "English File 11A", "mode": "choice",
            "tip_en": "Adjective + **-ly** = adverb: *slow → slowly*. Irregular: good → **well**, fast → **fast**!",
            "tip_hy": "Ածական + ly = մակբայ։ Անկանոն՝ good → well, fast → fast։",
            "questions": [
                {"prompt": "She sings ___. 🎤", "options": ["beautifully", "beautiful"], "word": "beautifully", "full": "She sings beautifully.", "hy": "Գեղեցիկ է երգում։", "why": "Բայի հետ → մակբայ (-ly)։"},
                {"prompt": "He drives very ___. 🐢", "options": ["slowly", "slow"], "word": "slowly", "full": "He drives very slowly.", "hy": "Շատ դանդաղ է վարում։", "why": "slow → slowly։"},
                {"prompt": "good → ___", "options": ["well", "goodly"], "word": "well", "full": "Well.", "hy": "լավ (մակբայ)", "why": "Անկանոն՝ good → well։"},
                {"prompt": "They speak English ___.", "options": ["perfectly", "perfect"], "word": "perfectly", "full": "They speak English perfectly.", "hy": "Կատարյալ են խոսում։", "why": "perfect → perfectly։"},
                {"prompt": "Please talk ___ — the baby is sleeping. 🤫", "options": ["quietly", "quiet"], "word": "quietly", "full": "Please talk quietly.", "hy": "Խոսեք հանգիստ։", "why": "quiet → quietly։"},
                {"prompt": "fast → ___", "options": ["fast", "fastly"], "word": "fast", "full": "Fast.", "hy": "արագ (մակբայ)", "why": "Անկանոն՝ fast → fast («fastly» չկա)։"},
            ],
        },
        "verb_infinitive": {
            "emoji": "🎯", "title": "want / need / plan + to", "title_hy": "Բայ + to + բայ",
            "ef": "English File 11B", "mode": "choice",
            "tip_en": "want / need / decide / plan / learn / hope + **to** + verb: *I want to speak English well.*",
            "tip_hy": "want/need/decide/plan/learn/hope-ից հետո՝ to + բայ։",
            "questions": [
                {"prompt": "I want ___ English well.", "options": ["to speak", "speaking", "speak"], "word": "to speak", "full": "I want to speak English well.", "hy": "Ուզում եմ լավ խոսել անգլերեն։", "why": "want + to + բայ։"},
                {"prompt": "She needs ___ a new phone.", "options": ["to buy", "buying"], "word": "to buy", "full": "She needs to buy a new phone.", "hy": "Նոր հեռախոս պետք է գնի։", "why": "need + to։"},
                {"prompt": "We decided ___ to the sea. 🌊", "options": ["to go", "going"], "word": "to go", "full": "We decided to go to the sea.", "hy": "Որոշեցինք գնալ ծով։", "why": "decide + to։"},
                {"prompt": "He is learning ___ the piano. 🎹", "options": ["to play", "playing"], "word": "to play", "full": "He is learning to play the piano.", "hy": "Դաշնամուր նվագել է սովորում։", "why": "learn + to։"},
                {"prompt": "I hope ___ you soon!", "options": ["to see", "seeing"], "word": "to see", "full": "I hope to see you soon!", "hy": "Հուսով եմ շուտով կտեսնվենք։", "why": "hope + to։"},
                {"prompt": "They plan ___ a house.", "options": ["to buy", "buying"], "word": "to buy", "full": "They plan to buy a house.", "hy": "Ծրագրում են տուն գնել։", "why": "plan + to։"},
            ],
        },
        "articles": {
            "emoji": "📰", "title": "Articles: a / an / the", "title_hy": "Հոդեր",
            "ef": "English File 11C", "mode": "choice",
            "tip_en": "**a/an** = one of many (first mention) · **the** = specific/unique (*the sun*). No article: *by bus, at home, have lunch*.",
            "tip_hy": "a/an՝ առաջին հիշատակում, the՝ որոշակի/եզակի բան։ Առանց հոդի՝ by bus, at home։",
            "questions": [
                {"prompt": "I have ___ dog. 🐶", "options": ["a", "an", "the"], "word": "a", "full": "I have a dog.", "hy": "Շուն ունեմ։", "why": "Առաջին հիշատակում → a։"},
                {"prompt": "___ sun is hot. ☀️", "options": ["The", "A", "An"], "word": "The", "full": "The sun is hot.", "hy": "Արևը տաք է։", "why": "Եզակի բան աշխարհում → the։"},
                {"prompt": "She is ___ engineer.", "options": ["an", "a", "the"], "word": "an", "full": "She is an engineer.", "hy": "Նա ինժեներ է։", "why": "engineer → ձայնավոր → an։"},
                {"prompt": "Choose the correct sentence:", "options": ["I go to work by bus.", "I go to work by a bus."], "word": "I go to work by bus.", "full": "I go to work by bus.", "hy": "Ավտոբուսով եմ գնում։", "why": "by bus/car/train → առանց հոդի։"},
                {"prompt": "___ Alps are in Europe. 🏔️", "options": ["The", "A", "An"], "word": "The", "full": "The Alps are in Europe.", "hy": "Ալպերը Եվրոպայում են։", "why": "Լեռնաշղթաներ → the։"},
                {"prompt": "Choose the correct sentence:", "options": ["We have lunch at home.", "We have lunch at the home."], "word": "We have lunch at home.", "full": "We have lunch at home.", "hy": "Ճաշում ենք տանը։", "why": "at home → առանց հոդի։"},
            ],
        },
    },
    "📒 File 12 · Present Perfect": {
        "present_perfect": {
            "emoji": "✅", "title": "Present Perfect: have been", "title_hy": "Վաղակատար ներկա",
            "ef": "English File 12A", "mode": "choice",
            "tip_en": "**have/has + past participle** for life experience: *I have been to Paris. She has never eaten sushi.*",
            "tip_hy": "have/has + բայի 3-րդ ձև՝ կյանքի փորձի համար։ ever = երբևէ, never = երբեք։",
            "questions": [
                {"prompt": "I ___ been to Paris. 🗼", "options": ["have", "has"], "word": "have", "full": "I have been to Paris.", "hy": "Եղել եմ Փարիզում։", "why": "I → have։"},
                {"prompt": "She ___ never eaten sushi. 🍣", "options": ["has", "have"], "word": "has", "full": "She has never eaten sushi.", "hy": "Երբեք սուշի չի կերել։", "why": "She → has։"},
                {"prompt": "___ you ever been to Italy?", "options": ["Have", "Has"], "word": "Have", "full": "Have you ever been to Italy?", "hy": "Երբևէ եղե՞լ ես Իտալիայում։", "why": "you → Have ... ever ...?"},
                {"prompt": "We have ___ this film.", "options": ["seen", "saw"], "word": "seen", "full": "We have seen this film.", "hy": "Այս ֆիլմը տեսել ենք։", "why": "have + seen (3-րդ ձև)։"},
                {"prompt": "He has ___ his homework. 📚", "options": ["done", "did"], "word": "done", "full": "He has done his homework.", "hy": "Դասերն արել է։", "why": "has + done։"},
                {"prompt": "They ___ visited us twice.", "options": ["have", "has"], "word": "have", "full": "They have visited us twice.", "hy": "Երկու անգամ այցելել են։", "why": "They → have։"},
            ],
        },
        "perfect_vs_past": {
            "emoji": "🆚", "title": "Present Perfect or Past?", "title_hy": "Վաղակատա՞ր, թե՞ անցյալ",
            "ef": "English File 12B", "mode": "choice",
            "tip_en": "Finished time (*yesterday, in 2019, last week*) → Past Simple. Experience / no time given → Present Perfect.",
            "tip_hy": "Կոնկրետ անցյալ ժամանակ (yesterday, in 2019) → Past Simple։ Փորձ առանց ժամանակի → Present Perfect։",
            "questions": [
                {"prompt": "I ___ to London in 2019.", "options": ["went", "have been"], "word": "went", "full": "I went to London in 2019.", "hy": "2019-ին Լոնդոն գնացի։", "why": "in 2019 → Past Simple։"},
                {"prompt": "___ you ever tried Armenian food? 🇦🇲", "options": ["Have", "Did"], "word": "Have", "full": "Have you ever tried Armenian food?", "hy": "Երբևէ փորձե՞լ ես հայկական ուտեստ։", "why": "ever → Present Perfect։"},
                {"prompt": "She ___ her keys yesterday. 🔑", "options": ["lost", "has lost"], "word": "lost", "full": "She lost her keys yesterday.", "hy": "Երեկ կորցրեց բանալիները։", "why": "yesterday → Past Simple։"},
                {"prompt": "I ___ never seen snow! ❄️", "options": ["have", "did"], "word": "have", "full": "I have never seen snow!", "hy": "Երբեք ձյուն չեմ տեսել։", "why": "never (փորձ) → Present Perfect։"},
                {"prompt": "We ___ that museum last week.", "options": ["visited", "have visited"], "word": "visited", "full": "We visited that museum last week.", "hy": "Անցյալ շաբաթ այցելեցինք։", "why": "last week → Past Simple։"},
                {"prompt": "He ___ just finished work. 🎉", "options": ["has", "did"], "word": "has", "full": "He has just finished work.", "hy": "Հենց նոր ավարտեց։", "why": "just → Present Perfect։"},
            ],
        },
        "translate_final": {
            "emoji": "🎓", "title": "Final Translate: Review", "title_hy": "Ամփոփիչ թարգմանություն",
            "ef": "English File 12C · Review", "mode": "translate",
            "tip_en": "The grand final! A mix of everything you have learned. 💪",
            "tip_hy": "Մեծ եզրափակիչ՝ ամեն ինչի խառնուրդ։ Դու կկարողանաս։",
            "questions": [
                {"hy": "Ես երբեք չեմ եղել Փարիզում։", "full": "I have never been to Paris.", "accept": ["I have never been to Paris."], "why": "Փորձ → Present Perfect + never։"},
                {"hy": "Երեկ մենք ֆուտբոլ խաղացինք։", "full": "We played football yesterday.", "accept": ["We played football yesterday.", "Yesterday we played football."], "why": "yesterday → Past Simple։"},
                {"hy": "Նա ուզում է անգլերեն սովորել։", "full": "She wants to learn English.", "accept": ["She wants to learn English.", "He wants to learn English."], "why": "want + to + բայ։"},
                {"hy": "Վաղը ես դպրոց եմ գնալու։", "full": "I am going to go to school tomorrow.", "accept": ["I am going to go to school tomorrow.", "Tomorrow I am going to go to school.", "I am going to school tomorrow."], "why": "Ծրագիր → be going to։"},
                {"hy": "Երևանը Հայաստանի ամենամեծ քաղաքն է։", "full": "Yerevan is the biggest city in Armenia.", "accept": ["Yerevan is the biggest city in Armenia.", "Yerevan is the largest city in Armenia."], "why": "Գերադրական → the biggest։"},
                {"hy": "Դու կարո՞ղ ես ինձ օգնել։", "full": "Can you help me?", "accept": ["Can you help me?"], "why": "Can + you + բայ + me։"},
            ],
        },
    },
}

# ---------------------------------------------------------------- persistence
DB_PATH = Path(__file__).parent / "english_progress.json"


def load_db():
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "profiles" in data:
            return data
    except Exception:
        pass
    return {"profiles": {}}


def save_db():
    try:
        DB_PATH.write_text(
            json.dumps(st.session_state.db, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    except Exception:
        st.sidebar.warning("⚠️ Չհաջողվեց պահպանել առաջընթացը ֆայլում։")


if "db" not in st.session_state:
    st.session_state.db = load_db()
if "profile" not in st.session_state:
    st.session_state.profile = None
if "celebrated" not in st.session_state:
    st.session_state.celebrated = {}

db = st.session_state.db

# ---------------------------------------------------------------- profile page
if st.session_state.profile is None or st.session_state.profile not in db["profiles"]:
    st.markdown(
        """
        <div class="hero">
          <h1>🍑 English Practice · Անգլերենի վարժություններ</h1>
          <p>Ո՞վ է սովորում այսօր · Who is learning today?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    profiles = db["profiles"]
    if profiles:
        st.markdown("### 👤 Ընտրիր քո պրոֆիլը · Choose your profile")
        cols = st.columns(min(4, max(1, len(profiles))))
        for idx, (name, pdata) in enumerate(profiles.items()):
            n_done = len(pdata.get("completed", {}))
            with cols[idx % len(cols)]:
                st.markdown(
                    f"<div class='profile-card'>{pdata.get('avatar','🙂')}<br>{name}"
                    f"<br><span style='font-size:.85rem;'>🏆 {n_done} վարժություն</span></div>",
                    unsafe_allow_html=True,
                )
                if st.button("Մուտք · Enter", key=f"login_{name}", use_container_width=True):
                    st.session_state.profile = name
                    st.session_state.celebrated = {}
                    st.rerun()
        st.markdown("---")

    st.markdown("### ➕ Նոր սովորող · New learner")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        avatar = st.selectbox("Ընտրիր կերպար · Avatar", AVATARS)
    with c2:
        new_name = st.text_input("Անուն · Name", placeholder="Օրինակ՝ Անի")
    with c3:
        st.write("")
        st.write("")
        if st.button("🚀 Սկսել · Start", type="primary", use_container_width=True):
            name = new_name.strip()
            if not name:
                st.warning("Գրիր անունդ 🙂")
            elif name in profiles:
                st.warning("Այս անունն արդեն կա — ընտրիր վերևից կամ գրիր այլ անուն։")
            else:
                profiles[name] = {"avatar": avatar, "answers": {}, "completed": {}}
                save_db()
                st.session_state.profile = name
                st.session_state.celebrated = {}
                st.rerun()

    st.caption("💾 Յուրաքանչյուր սովորողի առաջընթացը պահպանվում է առանձին և չի կորչում "
               "ծրագիրը փակելուց հետո։")
    st.stop()

# ---------------------------------------------------------------- progress sync
profile_name = st.session_state.profile
prof = db["profiles"][profile_name]
prof.setdefault("answers", {})
prof.setdefault("completed", {})
answers = prof["answers"]


def q_key(tid, i):
    return f"{tid}_q{i}"


def sync_widgets_to_db():
    """Copy any live widget values into the persistent store."""
    dirty = False
    for ltopics in LEVELS.values():
        for tid, t in ltopics.items():
            for i in range(len(t["questions"])):
                key = q_key(tid, i)
                if key in st.session_state:
                    val = st.session_state[key]
                    if val is None:
                        continue
                    if isinstance(val, str) and not val.strip():
                        continue
                    if answers.setdefault(tid, {}).get(str(i)) != val:
                        answers[tid][str(i)] = val
                        dirty = True
    if dirty:
        save_db()


sync_widgets_to_db()


def question_status(tid, topic):
    """(n_correct, n_answered, n_total) from the persistent store."""
    correct = answered = 0
    saved = answers.get(tid, {})
    for i, q in enumerate(topic["questions"]):
        val = saved.get(str(i))
        qtype = q.get("type", topic["mode"])
        if val is None or (isinstance(val, str) and not val.strip()):
            continue
        answered += 1
        if qtype == "choice":
            if val == q["word"]:
                correct += 1
        elif qtype == "spell":
            if normalize(val) == normalize(q["word"]):
                correct += 1
        else:
            if check_full(val, q):
                correct += 1
    return correct, answered, len(topic["questions"])


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(f"## {prof.get('avatar','🙂')} {profile_name}")
    n_trophies = len(prof["completed"])
    st.caption(f"🏆 Ավարտված վարժություններ՝ {n_trophies}")
    if st.button("🔁 Փոխել պրոֆիլը · Switch profile"):
        st.session_state.profile = None
        st.rerun()
    st.markdown("---")

    level_name = st.selectbox("🎚️ Դասագրքի բաժինը · Book File", list(LEVELS.keys()))
    level = LEVELS[level_name]

    selected = st.radio(
        "📚 Վարժություն · Exercise",
        options=list(level.keys()),
        format_func=lambda tid: f"{level[tid]['emoji']} {level[tid]['title']}",
    )

    st.markdown("---")
    st.markdown("### ⭐ Այս բաժնի առաջընթացը")
    for tid, t in level.items():
        c, a, n = question_status(tid, t)
        if prof["completed"].get(tid):
            star = "🏆"
        elif c == n:
            star = "🌟"
        elif c >= n / 2:
            star = "⭐"
        elif a:
            star = "🔸"
        else:
            star = "▫️"
        st.markdown(f"{star} {t['emoji']} {t['title_hy']} — **{c}/{n}**")

    grand_correct = grand_total = 0
    for ltopics in LEVELS.values():
        for tid, t in ltopics.items():
            c, a, n = question_status(tid, t)
            grand_correct += c
            grand_total += n
    st.markdown("---")
    st.progress(grand_correct / grand_total if grand_total else 0.0)
    st.caption(f"Ընդհանուր՝ {grand_correct} / {grand_total} ճիշտ պատասխան · "
               f"💾 պահպանվում է ավտոմատ")

# ---------------------------------------------------------------- main page
topic = level[selected]
mode = topic["mode"]
c_correct, c_answered, c_total = question_status(selected, topic)

st.markdown(
    f"""
    <div class="hero">
      <h1>{topic['emoji']} {topic['title']}</h1>
      <p><span class="ef-badge">📖 {topic['ef']}</span> &nbsp; {topic['title_hy']} ·
      ✅ Ինքնաստուգում · Ճիշտ՝ {c_correct}/{c_total}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(c_correct / c_total if c_total else 0.0)

st.markdown(
    f"""
    <div class="tip-card">
      💡 {topic['tip_en']}<br>
      <span class="hy-note">🇦🇲 {topic['tip_hy']}</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

saved_topic = answers.get(selected, {})

# ---------------------------------------------------------------- questions
for i, q in enumerate(topic["questions"]):
    key = q_key(selected, i)
    qtype = q.get("type", mode)

    # restore saved answer into the widget (before the widget is created)
    saved_val = saved_topic.get(str(i))
    if key not in st.session_state and saved_val is not None:
        if qtype == "choice":
            if saved_val in q["options"]:
                st.session_state[key] = saved_val
        else:
            st.session_state[key] = saved_val

    # ---------- prompt card
    if qtype == "translate":
        st.markdown(
            f"<div class='q-card'><span class='q-chip'>{i+1}</span>"
            f"<span class='q-text hy-line'>🇦🇲 {q['hy']}</span></div>",
            unsafe_allow_html=True,
        )
    elif qtype == "spell":
        st.markdown(
            f"<div class='q-card'><span class='q-chip'>{i+1}</span>"
            f"<span class='q-text'>🎧 Լսիր հեգումը և գրիր բառը · Listen and type the word</span></div>",
            unsafe_allow_html=True,
        )
        tts_buttons(q["word"], uid=f"pre{selected}{i}", spell_word=q["word"], listen=False)
    else:
        st.markdown(
            f"<div class='q-card'><span class='q-chip'>{i+1}</span>"
            f"<span class='q-text'>{q['prompt']}</span></div>",
            unsafe_allow_html=True,
        )

    # ---------- answer widget + instant feedback
    if qtype == "choice":
        st.radio(
            "Ընտրիր · Choose:",
            options=q["options"],
            key=key,
            horizontal=True,
            index=None,
            label_visibility="collapsed",
        )
        picked = st.session_state.get(key)
        if picked is not None:
            if picked == q["word"]:
                st.markdown(
                    f"<div class='ok-box'>✅ <b>{PRAISE[i % len(PRAISE)]}</b> — {q['full']}"
                    f"<br><span class='hy-note'>🇦🇲 {q['hy']} · {q['why']}</span></div>",
                    unsafe_allow_html=True,
                )
                tts_buttons(q["full"], uid=f"{selected}{i}", spell_word=q["word"])
            else:
                st.markdown(
                    f"<div class='err-box'>❌ <b>{ENCOURAGE[i % len(ENCOURAGE)]}</b> "
                    f"Ընտրիր այլ տարբերակ։<br><span class='hy-note'>🇦🇲 {q['why']}</span></div>",
                    unsafe_allow_html=True,
                )

    elif qtype == "spell":
        with st.expander("💬 Հուշում · Hint (բառի իմաստը)"):
            st.write(f"🇦🇲 {q['hy']}")
        st.text_input("Answer", key=key, placeholder="Գրիր բառը այստեղ… (type the word)",
                      label_visibility="collapsed")
        user = st.session_state.get(key, "")
        if user.strip():
            if normalize(user) == normalize(q["word"]):
                st.markdown(
                    f"<div class='ok-box'>✅ <b>{PRAISE[i % len(PRAISE)]}</b> — {q['word']} = {q['hy']}"
                    f"<br><span class='hy-note'>🇦🇲 {q['why']}</span></div>",
                    unsafe_allow_html=True,
                )
                tts_buttons(q["word"], uid=f"{selected}{i}")
            else:
                st.markdown(
                    f"<div class='err-box'>❌ <b>{ENCOURAGE[i % len(ENCOURAGE)]}</b> "
                    f"Սեղմիր 🔤 Spell կոճակը և լսիր կրկին։</div>",
                    unsafe_allow_html=True,
                )
                with st.expander("🫣 Ցույց տալ պատասխանը · Show answer"):
                    st.write(f"**{q['word']}** — {q['hy']}։ {q['why']}")

    else:  # write / translate
        placeholder = ("Գրիր ամբողջ նախադասությունն անգլերեն… (write the full sentence)"
                       if qtype == "translate"
                       else "Գրիր պատասխանը և սեղմիր Enter…")
        if qtype != "translate":
            with st.expander("💬 Հուշում · Hint"):
                st.write(f"🇦🇲 {q['hy']}")
        st.text_input("Answer", key=key, placeholder=placeholder,
                      label_visibility="collapsed")
        user = st.session_state.get(key, "")

        if user.strip():
            if check_full(user, q):
                cap_note = ""
                if not user.strip()[0].isupper() and q["full"][0].isupper() and len(q["full"].split()) > 1:
                    cap_note = "<br>💡 Փոքր հուշում՝ նախադասությունը սկսիր մեծատառով։"
                st.markdown(
                    f"<div class='ok-box'>✅ <b>{PRAISE[i % len(PRAISE)]}</b> — {q['full']}"
                    f"{cap_note}<br><span class='hy-note'>🇦🇲 {q['why']}</span></div>",
                    unsafe_allow_html=True,
                )
                tts_buttons(q["full"], uid=f"{selected}{i}", spell_word=q.get("word"))
            elif (q.get("word") and normalize(user) == normalize(q["word"])
                  and normalize(q["word"]) != normalize(q["full"])):
                st.markdown(
                    "<div class='warn-box'>✏️ Բառը ճիշտ է, բայց գրիր <b>ամբողջ նախադասությունը</b>։</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='err-box'>❌ <b>{ENCOURAGE[i % len(ENCOURAGE)]}</b><br>"
                    f"Ճիշտ պատասխանը՝ <b>{q['full']}</b>"
                    f"<br><span class='hy-note'>🇦🇲 {q['why']}</span></div>",
                    unsafe_allow_html=True,
                )
                tts_buttons(q["full"], uid=f"{selected}{i}", spell_word=q.get("word"))

# re-sync after rendering so the sidebar/db always has the latest values
sync_widgets_to_db()
c_correct, c_answered, c_total = question_status(selected, topic)

st.markdown("---")

# ---------------------------------------------------------------- footer / score
if c_answered == c_total and c_correct == c_total:
    st.markdown(
        f"<div class='score-banner'>🏆 {c_correct}/{c_total} — Կատարյալ է! Perfect! 🎉 "
        f"Առաջընթացը պահպանված է։</div>",
        unsafe_allow_html=True,
    )
    if not prof["completed"].get(selected):
        prof["completed"][selected] = True
        save_db()
    if not st.session_state.celebrated.get(selected):
        st.balloons()
        st.session_state.celebrated[selected] = True
elif c_answered:
    st.markdown(
        f"<div class='score-banner'>Ճիշտ՝ {c_correct} / {c_total} · "
        f"Պատասխանված՝ {c_answered} / {c_total} — Շարունակիր! 💪 💾</div>",
        unsafe_allow_html=True,
    )

if st.button("🔄 Նորից սկսել այս վարժությունը · Restart this exercise"):
    for i in range(len(topic["questions"])):
        st.session_state.pop(q_key(selected, i), None)
    answers.pop(selected, None)
    save_db()
    st.session_state.celebrated[selected] = False
    st.rerun()

st.caption("💾 Պատասխանները պահպանվում են ավտոմատ՝ վարժությունից վարժություն անցնելիս և "
           "ծրագիրը փակելիս չեն կորչում։ 🏆 նշանը մնում է նույնիսկ «Նորից սկսել»-ից հետո։ "
           "✍️ Վերջակետը («.» կամ «?») կարող ես չդնել։ 🔊 Listen / 🔤 Spell՝ Chrome/Safari։")
