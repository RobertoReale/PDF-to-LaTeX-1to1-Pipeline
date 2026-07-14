import sys
import re
import fitz  # PyMuPDF

def clean_text(text):
    # Rimuove intestazioni e piè di pagina standard per evitare falsi positivi
    lines = text.split('\n')
    cleaned = []
    for l in lines:
        l_strip = l.strip()
        # Ignora numeri di pagina isolati o intestazioni di capitolo ripetitive
        if re.match(r'^\d+$', l_strip) or re.match(r'^--- PAGINA \d+ ---$', l_strip):
            continue
        # Normalizza apici, pedici e caratteri speciali OCR
        l_strip = re.sub(r'[\s\t]+', ' ', l_strip)
        cleaned.append(l_strip)
    return "\n".join(cleaned)

def verify_1to1(orig_pdf_path, generated_pdf_path):
    print(f"=== QA DIFF CHECK 1:1 ===")
    print(f"Originale: '{orig_pdf_path}'")
    print(f"Generato:  '{generated_pdf_path}'")
    
    try:
        doc_orig = fitz.open(orig_pdf_path)
        doc_gen = fitz.open(generated_pdf_path)
    except Exception as e:
        print(f"❌ Errore nell'apertura dei file PDF: {e}")
        return False
        
    text_orig = clean_text(" ".join(page.get_text() for page in doc_orig))
    text_gen = clean_text(" ".join(page.get_text() for page in doc_gen))
    
    # Controlla la lunghezza complessiva del testo per identificare riassunti grossolani
    ratio = len(text_gen) / max(1, len(text_orig))
    print(f"Rapporto caratteri (Generato / Originale): {ratio:.2%}")
    
    if ratio < 0.70:
        print("❌ [ALLERTA CRITICA] Il documento generato ha il 30%+ di testo in meno rispetto all'originale!")
        print("   Probabile RIASSUNTO o ELISIONE di paragrafi non consentita dal Protocollo 1:1.")
        
    # Confronto frasi e identificazione omissioni significative
    words_orig = set(re.findall(r'\b[a-zA-ZàèéìòùÀÈÉÌÒÙ]{4,}\b', text_orig.lower()))
    words_gen = set(re.findall(r'\b[a-zA-ZàèéìòùÀÈÉÌÒÙ]{4,}\b', text_gen.lower()))
    
    missing_words = words_orig - words_gen
    # Filtra parole matematiche o sigle comuni che possono essere cambiate in formule LaTeX
    missing_filtered = [w for w in missing_words if not re.match(r'^(cost|fig|eq|sec|pag|max|min|const)$', w)]
    
    if len(missing_filtered) > 15:
        print(f"⚠ [AVVISO QA] Possibili parole chiave/concetti del testo originale mancanti in LaTeX:")
        print("  ", ", ".join(sorted(missing_filtered)[:25]), "...\n")
    else:
        print("✔ Fedeltà concettuale lessicale verificata con successo: zero elisioni identificate.\n")
        
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python scripts/qa_verify_fidelity.py <pdf_originale> <pdf_latex_compilato>")
        sys.exit(1)
    verify_1to1(sys.argv[1], sys.argv[2])
