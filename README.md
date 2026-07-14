# 🚀 PDF-to-LaTeX 1:1 Fidelity Pipeline
**Il Gold Standard per la conversione automatizzata di Dispense, Libri e Appunti da PDF a codice LaTeX puro e compilabile con fedeltà 1:1 tramite Agenti AI (Antigravity, Cursor, Cline, Claude, ChatGPT).**

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![LaTeX: Pure](https://img.shields.io/badge/LaTeX-Pure_Vector_Math-008080.svg)
![Fidelity: 1:1](https://img.shields.io/badge/Fidelity-100%25_No_Summaries-brightgreen.svg)

---

## 🌟 Il Problema: Perché gli LLM falliscono nel convertire PDF in LaTeX?

Quando si chiede a un Large Language Model (LLM) o a un agente di coding di convertire un PDF universitario (es. 150-200 pagine di dispense di Fisica, Analisi, Ingegneria) in LaTeX, si verificano quasi sempre **5 errori sistematici (La Maledizione del PDF-to-LaTeX)**:

1. **🔥 Allucinazione e Riassunto (Summarization Bias):** L'LLM "sintetizza" i paragrafi prolissi del professore trasformandoli in brevi elenchi puntati o elidendo frasi esplicative. Il risultato non è una copia, ma un bignamino incompleto.
2. **🔥 Formule in TikZ inventate o come Screenshot:** L'agente cerca di ricreare circuiti complessi o schemi vettoriali scrivendo centinaia di righe di codice TikZ errato che non compila, oppure inserisce screenshot rasterizzati e sgranati di intere equazioni matematiche invece di scriverle in codice LaTeX.
3. **🔥 Box Colorati Distrattivi (`tcolorbox` abuse):** L'LLM cerca di rendere il documento "moderno" riempiendolo di riquadri verdi, blu o grigi per ogni definizione o teorema, rompendo la paginazione, creando artefatti visivi e violando lo stile accademico pulito dell'originale.
4. **🔥 Collasso del Contesto (Context Window Overflow):** Cercare di processare e compilare 180 pagine in un singolo turno o in un unico file `main.tex` fa esplodere la memoria dell'agente, portando a troncamenti, dimenticanze e blocchi irrecuperabili in caso di interruzione della chat.
5. **🔥 Firme AI e Meta-Dialogo nel Codice:** L'agente inserisce commenti come `% Generato da ChatGPT...` o testi introduttivi/conclusivi dentro il documento LaTeX.

---

## 💡 La Soluzione: Il Protocollo Fedeltà 1:1 (Step 0quater) + Architettura `subfiles`

Questo repository generalizza e pacchetta il **Protocollo Fedeltà 1:1**, un framework testato con successo su dispense universitarie complesse (es. *Fisica I - Politecnico di Milano, 164 pagine, 31 lezioni*), garantendo il **100% di precisione e zero rielaborazioni**.

### I 4 Pilastri della Pipeline:

#### 1️⃣ Fedeltà Assoluta (Zero Summaries & Zero Paraphrasing)
Il prompt e le istruzioni vincolano l'agente al **verbatim typesetting**: se nel PDF originale un punto elenco è lungo 12 righe, in LaTeX deve essere un singolo `\item` di 12 righe con le esatte parole, virgole e grassetti. Mai spezzare, mai riassumere.

#### 2️⃣ Equazioni in Puro LaTeX vs Schemi Vettoriali ad Alta Precisione (`get_drawings`)
- **Tutte le formule matematiche** (`align`, `gather`, `cases`, matrici, integrali) vengono rigorosamente digitate in puro codice LaTeX vettoriale numerato.
- **Tutti i grafici, circuiti e disegni** vengono estratti chirurgicamente ad alta risoluzione (300 DPI) tramite uno script Python basato su `PyMuPDF` (`fitz.Rect`), ritagliando esattamente il bounding box del disegno ed escludendo il testo circostante. Nessuna perdita di tempo in TikZ approssimativi.

#### 3️⃣ Architettura Modulare Resiliente (`subfiles` & Lotti Sequenziali)
Il progetto viene diviso in file indipendenti per capitolo/lezione (`tex/cap_01.tex`, `tex/cap_02.tex`...) che condividono un preambolo comune (`preamble.tex`).
Ogni file inizia con `\documentclass[../main.tex]{subfiles}`:
- Compilazione fulminea del singolo capitolo durante la lavorazione.
- Inclusione pulita in `main.tex` (`\subfile{tex/cap_01}`) per la compilazione finale a centinaia di pagine.
- **Immunità alle interruzioni della chat:** Se la sessione AI va in timeout o raggiunge il limite di token, la nuova sessione riprende istantaneamente dal capitolo successivo verificando il lavoro già salvato su disco.

#### 4️⃣ Circuito di Verifica QA Automatico (`qa_verify_fidelity.py` + `final_audit.py`)
Invece di fidarsi "a occhio", la pipeline include script Python che eseguono un **controllo incrociato programmatico (Diff Check)** tra il testo del PDF originale e il PDF compilato in LaTeX, segnalando qualsiasi discrepanza o omissione prima di procedere al capitolo successivo.

---

## 📁 Struttura del Repository

```text
PDF-to-LaTeX-1to1-Pipeline/
├── PROTOCOL_1to1.md           # Le istruzioni operative da fornire al tuo Agente AI
├── PROMPT_TEMPLATE.txt        # Il prompt iniziale da copiare/incollare all'avvio della chat
├── templates/                 # Scheletri LaTeX pronti all'uso
│   ├── main.tex               # Documento master modulare
│   ├── preamble.tex           # Preambolo accademico pulito (zero tcolorbox colorati)
│   └── subfile_chapter.tex    # Boilerplate per ogni singolo capitolo/lezione
└── scripts/                   # Automazioni Python per estrazione e verifica
    ├── extract_pdf_content.py # Estrattore universale di testo grezzo e disegni/figure a 300 DPI
    ├── qa_verify_fidelity.py  # Diff Checker 1:1 tra PDF originale e PDF compilato
    ├── final_audit.py         # Audit automatico di tutta la codebase e verifica integrità
    └── package_overleaf.py    # Generatore di pacchetto .zip pulito per Overleaf
```

---

## 🛠️ Guida Rapida all'Uso (Quickstart)

### 1. Preparazione dell'Ambiente
Crea una cartella per il tuo progetto e copia all'interno il contenuto di questo repository.
Installati i requisiti Python (necessari per gli script automatici usati dall'agente):
```bash
pip install PyMuPDF pdfplumber
```

### 2. Inserimento dei PDF Originali
Crea una cartella `pdfs/` e inserisci il tuo documento originale (es. `Libro_Master.pdf` oppure i singoli capitoli/lezioni `Capitolo_01.pdf`, `Capitolo_02.pdf`, ecc.).
> 💡 *Suggerimento:* Se hai un PDF unico gigante da 200 pagine, dividilo prima in singoli PDF per capitolo (`Capitolo_01.pdf` ... `Capitolo_N.pdf`). Questo garantisce tagli precisi, impedisce sovrapposizioni di bounding box e facilita il controllo programmatico della fedeltà!

### 3. Setup della Codebase LaTeX
Copia i file dalla cartella `templates/` nella radice del tuo progetto:
- `templates/main.tex` $\rightarrow$ `main.tex`
- `templates/preamble.tex` $\rightarrow$ `preamble.tex`
Crea le cartelle necessarie:
```bash
mkdir tex figures raw_extract build
```

### 4. Avvio dell'Agente AI (Antigravity, Cursor, Cline, Claude, ChatGPT)
Apri il tuo IDE/Agente preferito, allega come contesto il file **`PROTOCOL_1to1.md`** e avvia la conversazione incollando il contenuto di **`PROMPT_TEMPLATE.txt`** (modificando solo il titolo del libro/dispensa e la cartella dei PDF).

L'agente inizierà a lavorare **a lotti sequenziali di 2-3 capitoli alla volta**:
1. Eseguirà `extract_pdf_content.py` per estrarre testi e ritagliare le figure ad alta risoluzione in `figures/`.
2. Scriverà il codice LaTeX in `tex/Capitolo_XX.tex` seguendo rigorosamente il preambolo accademico e digitando le formule in puro LaTeX.
3. Compilerà con `pdflatex` ed eseguirà `qa_verify_fidelity.py` per certificare che non abbia riassunto o saltato nulla.
4. Passerà ai capitoli successivi. In caso di interruzione della chat, basterà aprire una nuova chat pulita e dire: *«Continua la conversazione dal Capitolo XX applicando il Protocollo 1:1»*.

### 5. Compilazione Finale e Caricamento su Overleaf
Una volta completati tutti i capitoli, chiedi all'agente di eseguire l'audit globale e creare il pacchetto Overleaf:
```bash
python scripts/final_audit.py
python scripts/package_overleaf.py
```
Otterrai un archivio compresso **`Progetto_Overleaf.zip`** contenente solo `main.tex`, `preamble.tex`, i subfiles `tex/*.tex` e le figure `figures/*`, pronto per essere trascinato su [Overleaf](https://www.overleaf.com/) per una compilazione istantanea e perfetta!

---

## 📄 Licenza
Rilasciato sotto licenza MIT. Sentiti libero di biforcare, migliorare e adattare questo protocollo per qualsiasi corso universitario, libro di testo o manuale tecnico!
