# English Practice for Armenian Beginners
### Անգլերենի վարժություններ հայ սկսնակների համար

An interactive, colorful practice app for Armenian speakers learning English with the
**English File Elementary (4th edition)** coursebook. Built with [Streamlit](https://streamlit.io).

Դասագրքին համընթաց ինտերակտիվ վարժություններ՝ հայերեն հուշումներով և բացատրություններով։
Յուրաքանչյուր պատասխան ստուգվում է անմիջապես, իսկ առաջընթացը պահպանվում է ավտոմատ։

---

## ✨ Features · Հնարավորություններ

- 👤 **Learner profiles** — each student picks an avatar and has their own saved progress
- 📚 **All 12 Files of the book** — 47 exercises and 300+ questions, each tagged with its
  lesson (English File 1A, 1B, 2A ... 12C)
- ✅ **Instant checking** — every answer is checked the moment it's entered, with praise
  or a gentle explanation in Armenian
- ✍️ **Four exercise types:**
  - *Write* — type the whole sentence (contractions like *I'm / isn't* accepted,
    missing final `.` or `?` forgiven)
  - *Choice* — tap the right answer
  - *Translate* — Armenian → English
  - 🎧 *Listen & Spell* — hear a word spelled letter by letter and type it (alphabet practice!)
- 🔊 **Text-to-speech** — every sentence can be read aloud, every word spelled out
  (works in Chrome and Safari)
- 💾 **Progress saved automatically** — switching exercises or closing the app never
  erases answers; completed exercises earn a permanent 🏆
- 🎈 Balloons for a perfect score, stars in the sidebar, and encouragement in Armenian

## 📖 How it follows the book · Դասագրքի կառուցվածքով

| File | Grammar & vocabulary practiced |
|------|-------------------------------|
| 📘 1 | verb *be* (+ – ?), days, numbers 0–100, countries & nationalities, possessives, classroom language, the alphabet |
| 📗 2 | a/an & plurals, in/on/under, this/that/these/those, adjective opposites, imperatives & feelings |
| 📙 3 | present simple (+ – ?), jobs, word order in questions |
| 📕 4 | family & possessive 's, at/in/on (time), adverbs of frequency |
| 📔 5 | can/can't, present continuous, simple vs continuous |
| 📒 6 | object pronouns, like + -ing, dates, be or do revision |
| 📘 7 | was/were, past simple regular & irregular |
| 📗 8 | past simple mixed, there is/are, there was/were, prepositions of place |
| 📙 9 | food & some/any, how much/how many, comparatives |
| 📕 10 | superlatives, be going to |
| 📔 11 | adverbs (-ly), verb + infinitive, articles |
| 📒 12 | present perfect, present perfect vs past simple, final review |

## 🚀 Run locally · Գործարկել համակարգչում

```bash
# 1. Install Python 3 (macOS usually has it), then install Streamlit:
pip3 install streamlit

# 2. Download this repository (green "Code" button → Download ZIP) or:
git clone https://github.com/Seda2/English_File_Elementary_Armenian.git
cd English_File_Elementary_Armenian

# 3. Run the app:
streamlit run english_practice_app.py
```

The app opens in your browser at `http://localhost:8501`.

When running locally, progress is stored in `english_progress.json` next to the app
and is **fully permanent**. (To reset everything, just delete that file.)

## ☁️ Live version · Առցանց տարբերակ

The app can be deployed for free on [Streamlit Community Cloud](https://share.streamlit.io).
**Note:** cloud storage is temporary — profiles and progress on the deployed version may
reset when the app restarts or updates. For long-term progress tracking, run the app
locally.

## 🗂 Project structure

```
english_practice_app.py   # the whole app: UI, answer checking, and question banks
requirements.txt          # dependencies for Streamlit Cloud
english_progress.json     # created automatically — learners' saved progress (local)
```

## 🙌 Credits

Exercises are original (generated via Claude AI) and written to align with the topics and grammar syllabus of
*English File Elementary, 4th edition* (Oxford University Press). This project is an
independent study aid and is not affiliated with or endorsed by OUP.

Made with ❤️ for Armenian English learners · Սիրով՝ հայ սովորողների համար
