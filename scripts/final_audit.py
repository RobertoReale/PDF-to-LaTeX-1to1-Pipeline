import os
import glob
import re

def audit_codebase():
    print("=== AUDIT GLOBALE CODEBASE LATEX (PROTOCOL 1:1) ===")
    errors = []
    warnings = []
    
    tex_files = sorted(glob.glob("tex/*.tex"))
    print(f"[1/4] Analisi sintassi e conformità su {len(tex_files)} file TEX in 'tex/'...")
    
    forbidden_patterns = [
        (r'\\makecell', "Uso di \\makecell non supportato nativamente in alcune tabelle"),
        (r'tcolorbox.*colback=[^w]', "Tcolorbox con sfondi colorati vietati (Protocollo 1:1)"),
        (r'AI signature|Generato da AI|ChatGPT|Anthropic|Gemini', "Firme AI rilevate nel codice"),
    ]
    
    available_figures = set(os.path.basename(f) for f in glob.glob("figures/*.*"))
    
    for tf in tex_files:
        with open(tf, "r", encoding="utf-8") as f:
            content = f.read()
            
        if "\\documentclass[../main.tex]{subfiles}" not in content:
            warnings.append(f"{tf}: Manca l'intestazione \\documentclass[../main.tex]{subfiles}")
        if "\\begin{document}" not in content or "\\end{document}" not in content:
            errors.append(f"{tf}: Struttura \\begin/\\end document mancante")
            
        for pattern, msg in forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(f"{tf}: {msg}")
                
        img_matches = re.findall(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', content)
        for img in img_matches:
            img_name = os.path.basename(img)
            if img_name not in available_figures:
                errors.append(f"{tf}: Figura non trovata in 'figures/': '{img}'")
                
    print("[2/4] Controllo file master main.tex...")
    if os.path.exists("main.tex"):
        with open("main.tex", "r", encoding="utf-8") as mf:
            main_content = mf.read()
            for tf in tex_files:
                base_tf = os.path.splitext(os.path.basename(tf))[0]
                if f"\\subfile{{tex/{base_tf}}}" not in main_content:
                    warnings.append(f"Il file '{tf}' non è incluso o è commentato in main.tex")
    else:
        errors.append("File master 'main.tex' mancante nella directory radice!")
        
    print("[3/4] Controllo log di compilazione...")
    if os.path.exists("main.log"):
        with open("main.log", "r", encoding="utf-8", errors="ignore") as lf:
            log_text = lf.read()
            if "Fatal error" in log_text or "Emergency stop" in log_text:
                errors.append("Il file main.log indica un errore fatale durante l'ultima compilazione.")
                
    print("\n=== RISULTATI AUDIT ===")
    if not errors and not warnings:
        print("✔ NESSUN ERRORE RILEVATO! La codebase è al 100% integra, conforme al Protocollo 1:1 e pronta per la produzione.")
    else:
        if warnings:
            print(f"\n[AVVISI] ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")
        if errors:
            print(f"\n[ERRORI CRITICI] ({len(errors)}):")
            for e in errors:
                print(f"  - {e}")
            return False
            
    return len(errors) == 0

if __name__ == "__main__":
    success = audit_codebase()
    exit(0 if success else 1)
