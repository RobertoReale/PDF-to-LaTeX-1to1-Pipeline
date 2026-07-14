# Protocollo Operativo e Istruzioni per l'Agente AI (Fedeltà 1:1)

> **NOTA PER L'AGENTE AI:** Questo documento costituisce il tuo vincolo comportamentale assoluto per l'intera durata del progetto. Devi rispettare ogni singola regola qui specificata senza eccezioni, abbreviazioni o iniziative personali che violino il protocollo.

---

## 1. Obiettivo e Filosofia del Progetto
Hai il compito di convertire documenti PDF (dispense universitarie, libri di testo, appunti scientifici) in **codice LaTeX puro, modulare e compilabile**, garantendo una **Fedeltà 1:1 Assoluta** rispetto al documento originale sia nella struttura che nel contenuto tipografico e matematico.

---

## 2. Le 5 Regole d'Oro della Fedeltà 1:1

### Regola 1: Divieto Assoluto di Riassumere o Paraphrasing
- **Mai riassumere, mai sintetizzare, mai elidere frasi o parole.**
- **Mai spezzare o unire elenchi puntati o paragrafi:** se nel PDF originale c'è un unico punto elenco (`\bullet`) lungo 15 righe, nel codice `.tex` deve corrispondere esattamente **un singolo `\item`** lungo 15 righe con le stesse identiche parole, virgole, parentesi e formattazioni in grassetto/corsivo. Se il testo originale è un paragrafo discorsivo, **non** trasformarlo in un elenco puntato schematico.
- Il tuo ruolo non è quello di "migliorare", "riassumere" o "riorganizzare" il pensiero dell'autore, ma di agire come un perfetto compositore tipografico (typesetter) LaTeX ad altissima precisione.

### Regola 2: Equazioni in Puro Codice LaTeX (Zero Screenshot / Zero TikZ allucinati)
- **Tutte le equazioni matematiche, i sistemi, le matrici e gli integrali** vanno digitati rigorosamente in puro codice LaTeX all'interno dei corretti ambienti matematici (`equation`, `align`, `gather`, `cases`, `multline`).
- Mantieni la numerazione coerente all'originale (es. `(11.122)`) utilizzando `\setcounter` quando necessario, oppure usando etichettature pulite con `\label{...}` e `\ref{...}`.
- **Mai inserire screenshot o immagini per rappresentare formule matematiche.**
- **Mai disperdere token o tentare di disegnare schemi geometrici complessi o circuiti in codice TikZ da zero:** i grafici vettoriali vanno estratti come immagini di precisione secondo la Regola 3.

### Regola 3: Estrazione Chirurgica dei Grafici via `get_drawings()` a 300 DPI
- Per schemi geometrici, grafici vettoriali, circuiti e illustrazioni: usa o crea uno script Python basato su `PyMuPDF (fitz)` che individui il bounding box esatto (`fitz.Rect`) del solo disegno ed estragga l'immagine ad alta risoluzione (300 DPI) salvandola nella cartella `figures/` (es. `cap_01_fig_01.png`).
- Durante il calcolo del bounding box, assicurati di **escludere rigorosamente il testo, i titoli e le formule matematiche sovrastanti o sottostanti**, che andranno invece digitate nel testo LaTeX.
- Posiziona le figure in LaTeX usando ambienti puliti come `\begin{center} ... \includegraphics[width=...]{...} \end{center}` o layout affiancati con `\begin{minipage}{0.6\textwidth} ... \end{minipage}% \begin{minipage}{0.4\textwidth} ... \end{minipage}`.

### Regola 4: Stile Accademico Sobrio (Zero Box Colorati o `tcolorbox`)
- Rispettando la tradizione accademica pulita ed evitando conflitti di paginazione o artefatti visivi, **non usare mai `tcolorbox` con cornici o sfondi colorati (verdi, blu, grigi, ecc.)**.
- Utilizza esclusivamente gli ambienti puliti definiti nel preambolo (`\begin{defbox}`, `\begin{teobox}`, `\begin{notabox}`), che formattano il titolo in grassetto (es. **Definizione 1.1.**, **Teorema.**, **Esempio.**) seguito dal testo in stile accademico sobrio.
- Evita macro instabili o comandi fragili come `\makecell` dentro tabelle `tabularx`: usa tabelle `tabular` native o `array` matematici puliti.

### Regola 5: Zero Firme AI e Meta-Dialogo
- Il codice LaTeX generato deve essere puro e professionale: **mai inserire filigrane, firme, commenti o box finali del tipo "Generato da AI", "ChatGPT", "Claude", "Gemini"**.
- Non inserire commenti di meta-dialogo all'interno dei file `.tex`.

---

## 3. Architettura Modulare e Orchestrazione a Lotti (`subfiles`)

Per prevenire il collasso della finestra di contesto (Context Window Overflow) e garantire la massima resilienza alle interruzioni della chat, il lavoro **deve essere rigorosamente organizzato a lotti sequenziali di 2-3 capitoli/lezioni alla volta**.

### Struttura Modulare:
- Ogni capitolo/lezione va salvato come file separato in `tex/` (es. `tex/Capitolo_01.tex`).
- Ogni file `.tex` deve essere formattato usando il pacchetto `subfiles`:
  ```latex
  \documentclass[../main.tex]{subfiles}

  \begin{document}
  % Contenuto del capitolo/lezione qui...
  \end{document}
  ```
- Il file master `main.tex` include le singole lezioni tramite `\subfile{tex/Capitolo_01}`.
- Il preambolo del documento va tenuto separato in `preamble.tex` e caricato dal master (`\input{preamble}`). Deve includere la ricerca multipath per le immagini:
  ```latex
  \usepackage{graphicx}
  \graphicspath{{figures/}{../figures/}{raw_extract/}{../raw_extract/}}
  ```

---

## 4. Workflow Operativo per Lotti (Da Ripetere Sequenzialmente)

Per ogni lotto di lavoro assegnato (es. Capitoli $N$ ed $N+1$):
1. **Estrazione e Taglio Asset:** Esegui lo script Python `scripts/extract_pdf_content.py` per estrarre il testo grezzo (di riscontro) e salvare chirurgicamente le figure ad alta risoluzione in `figures/`.
2. **Stesura LaTeX 1:1:** Scrivi il file `tex/Capitolo_XX.tex` applicando fedelmente le 5 Regole d'Oro.
3. **Compilazione Locale:** Compila il singolo subfile o `main.tex` con `pdflatex` dal terminale ed elimina eventuali errori di sintassi LaTeX.
4. **Verifica Incrociata QA (Diff Check):** Esegui lo script `scripts/qa_verify_fidelity.py` per confrontare programmaticamente il testo del PDF appena generato con quello grezzo della lezione originale e correggere eventuali allucinazioni, elisioni o salti di paragrafo.
5. **Aggiornamento del Master:** Decommenta il capitolo in `main.tex` e passa al lotto successivo.
