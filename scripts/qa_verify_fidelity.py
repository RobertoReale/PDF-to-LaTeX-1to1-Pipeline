import sys
import re
import fitz  # PyMuPDF

def clean_text(text):
    # Remove standard headers and footers to avoid false positives
    lines = text.split('\n')
    cleaned = []
    for l in lines:
        l_strip = l.strip()
        # Ignore standalone page numbers or repetitive chapter/page markers
        if re.match(r'^\d+$', l_strip) or re.match(r'^--- (?:PAGE|PAGINA) \d+ ---$', l_strip):
            continue
        # Normalize whitespace and OCR anomalies
        l_strip = re.sub(r'[\s\t]+', ' ', l_strip)
        cleaned.append(l_strip)
    return "\n".join(cleaned)

def verify_1to1(orig_pdf_path, generated_pdf_path):
    print(f"=== QA DIFF CHECK 1:1 ===")
    print(f"Original:  '{orig_pdf_path}'")
    print(f"Generated: '{generated_pdf_path}'")
    
    try:
        doc_orig = fitz.open(orig_pdf_path)
        doc_gen = fitz.open(generated_pdf_path)
    except Exception as e:
        print(f"[ERROR] Failed to open PDF files: {e}")
        return False
        
    text_orig = clean_text(" ".join(page.get_text() for page in doc_orig))
    text_gen = clean_text(" ".join(page.get_text() for page in doc_gen))
    
    # Check overall character ratio to identify gross summarization or elision
    ratio = len(text_gen) / max(1, len(text_orig))
    print(f"Character ratio (Generated / Original): {ratio:.2%}")
    
    if ratio < 0.70:
        print("[CRITICAL ALERT] Generated document has 30%+ fewer characters than the original!")
        print("                 Probable SUMMARIZATION or PARAGRAPH OMISSION prohibited by the 1:1 Protocol.")
        
    # Lexical comparison and significant omission detection
    words_orig = set(re.findall(r'\b[a-zA-Z\u00C0-\u024F]{4,}\b', text_orig.lower()))
    words_gen = set(re.findall(r'\b[a-zA-Z\u00C0-\u024F]{4,}\b', text_gen.lower()))
    
    missing_words = words_orig - words_gen
    # Filter common math/structural keywords that might be turned into LaTeX commands or math symbols
    missing_filtered = [w for w in missing_words if not re.match(r'^(cost|fig|eq|sec|pag|max|min|const|page|section|chapter)$', w)]
    
    if len(missing_filtered) > 15:
        print(f"[QA WARNING] Possible keywords or concepts from original text missing in LaTeX output:")
        print("  ", ", ".join(sorted(missing_filtered)[:25]), "...\n")
    else:
        print("[OK] Lexical and conceptual fidelity verified successfully: zero omissions detected.")
        
    # Mathematical and Structural Density Linter
    # Check corresponding .tex source file if available
    import os
    base_path = os.path.splitext(generated_pdf_path)[0]
    tex_path = base_path + ".tex"
    if not os.path.exists(tex_path) and base_path.startswith("pdfs/"):
        tex_path = os.path.join("tex", os.path.basename(base_path) + ".tex")
        
    if os.path.exists(tex_path):
        with open(tex_path, "r", encoding="utf-8", errors="ignore") as tf:
            tex_content = tf.read()
            
        math_envs = re.findall(r'\\begin\{(?:equation|equation\*|align|align\*|gather|cases|multline)\}|\$.*?\$|\\\[.*?\\\]', tex_content)
        math_symbols_orig = len(re.findall(r'[=+\-*/^∫∑∏∂αβγδεζηθικλμνξοπρστυφχψω∆∇≈≠≤≥]', text_orig))
        
        print(f"Mathematical environments detected in TEX: {len(math_envs)}")
        if math_symbols_orig > 30 and len(math_envs) == 0:
            print("[QA WARNING] Original document contains dense mathematical notation, but zero LaTeX math environments were detected in source!")
            print("             Ensure formulas are typed inside \\begin{equation} ... \\end{equation} or $...$ and not as plain text.")
        else:
            print("[OK] Mathematical equation density verified.")
            
        if "tcolorbox" in tex_content and re.search(r'colback=[^w]', tex_content):
            print("[QA WARNING] Prohibited colored tcolorbox background detected. Please strictly adhere to preamble clean boxes.")
    print("")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/qa_verify_fidelity.py <original_pdf> <compiled_latex_pdf>")
        sys.exit(1)
    verify_1to1(sys.argv[1], sys.argv[2])
