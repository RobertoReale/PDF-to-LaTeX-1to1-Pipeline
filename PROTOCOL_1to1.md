# Operational Protocol and AI Agent Instructions (1:1 Fidelity)

> **MANDATORY AI BEHAVIORAL CONSTRAINT:** This document constitutes your absolute behavioral constraint for the entire duration of this project. You must strictly obey every single rule specified below without exception, abbreviation, summarization, or personal formatting initiatives that violate the protocol.

---

## 1. Project Objective and Philosophy
You are tasked with converting complex PDF documents (university lecture notes, textbooks, scientific manuscripts, and technical manuals) into **pure, modular, and compilable LaTeX code**, guaranteeing **100% 1:1 Fidelity** against the original document in both structural layout and typographical/mathematical content.

---

## 2. The 5 Golden Rules of 1:1 Fidelity

### Rule 1: Absolute Ban on Summarization, Paraphrasing, or Omissions
- **Never summarize, condense, simplify, or omit sentences, paragraphs, or words.**
- **Never split or merge bullet points or paragraphs:** if the original PDF contains a single bullet point (`\item`) spanning 15 lines of text, your `.tex` code must output **a single `\item`** exactly 15 lines long containing identical words, commas, parentheses, and bold/italic formatting. If the original text is a narrative paragraph, **do not** convert it into a schematic bulleted list.
- Your role is not to "improve", "shorten", or "re-organize" the author's reasoning, but to act as a flawless, high-precision LaTeX typesetter.

### Rule 2: Mathematical Equations in Pure LaTeX (Zero Screenshots / Zero Hallucinated TikZ)
- **All mathematical equations, systems, matrices, and integrals** must be typed strictly in pure vector LaTeX within the appropriate mathematical environments (`equation`, `align`, `gather`, `cases`, `multline`).
- Maintain exact equation numbering matching the original document (e.g., `(11.122)`) using `\setcounter` when necessary or via clean `\label{...}` and `\ref{...}` cross-referencing.
- **Never insert screenshots or raster images to represent mathematical equations or formulas.**
- **Never waste tokens or attempt to draw complex geometric diagrams, circuits, or charts from scratch in TikZ code:** vector drawings must be surgically extracted as high-resolution figures according to Rule 3.

### Rule 3: Surgical High-Resolution Figure Extraction via PyMuPDF at 300 DPI
- For geometric diagrams, vector plots, circuit schematics, and technical illustrations: use `scripts/extract_pdf_content.py` (based on `PyMuPDF` / `fitz`) to identify the precise bounding box (`fitz.Rect`) of the drawing and save it as a 300 DPI image inside the `figures/` directory (e.g., `chapter_01_fig_01.png`).
- When calculating or adjusting bounding boxes, strictly **exclude surrounding text, titles, captions, and mathematical formulas above or below the diagram**; these must be typed verbatim in LaTeX.
- Include figures inside clean environments such as `\begin{center} ... \includegraphics[width=...]{...} \end{center}` or side-by-side layouts with `\begin{minipage}{0.63\textwidth}\sloppy ... \end{minipage}\hfill \begin{minipage}{0.35\textwidth} ... \end{minipage}`.
- **Mandatory Figure Height Bound in Minipages (`keepaspectratio`):** To prevent tall figures (`500+ pt` height) from causing `Overfull \vbox` when scaled purely by width, always include `height=5.5cm, keepaspectratio` inside `\includegraphics` (e.g., `\includegraphics[width=0.85\textwidth, height=5.5cm, keepaspectratio]{...}`).
- **Minipage Content Splitting:** Minipages (`\parbox`) cannot split across pages. Never place long descriptive paragraphs, proofs, or lengthy system derivations inside the minipage alongside a figure. Only compact elements directly tied to the figure (e.g., a short `\begin{defbox}` or `itemize` list) should reside inside the minipage; longer narrative paragraphs and equation derivations must be placed outside (`before/after` the minipage) to allow natural page breaking.

### Rule 4: Sober Academic Styling & Typography Optimization
- To preserve classical academic typography and prevent pagination overflows or visual artifacts, **never use `tcolorbox` environments with colored frames or backgrounds (green, blue, gray, etc.)**.
- Use exclusively the clean environments defined in the preamble (`\begin{defbox}`, `\begin{teobox}`, `\begin{notabox}`), which typeset the title in bold (e.g., **Definition 1.1.**, **Theorem.**, **Example.**) followed by standard academic prose.
- Avoid fragile macros or unstable table syntax (such as `\makecell` inside `tabularx`). In `tabularx` tables containing complex mathematical formulas or multi-line text in `X` columns, always configure left alignment (`>{\raggedright\arraybackslash}X`) to prevent `badness 10000` horizontal stretching.
- **Math Mode Font Sizing:** Never use `\footnotesize`, `\small`, or `\Large` directly inside math mode (`equation`, `cases`, `gather`), as this causes syntax errors. Always wrap explanatory text inside `\text{...}` before applying font sizes (e.g., `\quad \text{\footnotesize (explanatory text)}`).

### Rule 5: Zero AI Signatures, Watermarks, or Meta-Commentary
- The generated LaTeX code must be pristine and professional: **never insert watermarks, signatures, comments, or concluding boxes such as "Generated by AI", "ChatGPT", "Claude", or "Gemini"**.
- Do not insert conversational meta-dialogue comments inside the `.tex` files.

---

## 3. Modular Architecture and Sequential Batch Processing (`subfiles`)

To prevent Context Window Overflow and ensure complete resilience against chat disconnections or token timeouts, the conversion project **must be organized into sequential batches of 2 to 3 chapters/lectures per batch**.

### Modular Structure:
- Each chapter/lecture must be saved as an independent file inside `tex/` (e.g., `tex/Chapter_01.tex`).
- Every `.tex` file must use the `subfiles` document class:
  ```latex
  \documentclass[../main.tex]{subfiles}

  \begin{document}
  % Chapter content here...
  \end{document}
  ```
- The master file `main.tex` includes each chapter progressively via `\subfile{tex/Chapter_01}`.
- The preamble must remain separate in `preamble.tex` and be loaded from the master (`\input{preamble}`). It includes multi-path search definitions for graphics:
  ```latex
  \usepackage{graphicx}
  \graphicspath{{figures/}{../figures/}{raw_extract/}{../raw_extract/}}
  ```

---

## 4. Operational Workflow per Batch (To Be Executed Sequentially)

For every assigned batch (e.g., Chapters $N$ and $N+1$):
1. **Extraction & Asset Cropping:** Run `python scripts/extract_pdf_content.py` to extract raw verification text and surgically save high-resolution figures into `figures/`.
2. **1:1 LaTeX Typesetting:** Write `tex/Chapter_XX.tex`, strictly adhering to the 5 Golden Rules.
3. **Local Compilation:** Compile the individual subfile or `main.tex` using `pdflatex` from the terminal and resolve any LaTeX syntax errors immediately.
4. **Automated QA Verification (Diff Check):** Execute `python scripts/qa_verify_fidelity.py <original_pdf> <compiled_pdf>` to programmatically verify lexical overlap and character ratios, correcting any hallucinated summaries or dropped paragraphs before continuing.
5. **Master Update:** Uncomment the completed chapter in `main.tex` and proceed to the next batch.
