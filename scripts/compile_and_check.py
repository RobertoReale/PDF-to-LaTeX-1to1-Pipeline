import os
import sys
import subprocess
import glob
import re

def parse_log_for_errors(log_path):
    if not os.path.exists(log_path):
        return [{"line": 0, "error": "Log file not found after compilation attempt"}]
        
    errors = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("! "):
            err_msg = line[2:]
            line_num = 0
            # Look ahead for exact line number like "l.45 \teorem..."
            for j in range(i + 1, min(i + 15, len(lines))):
                match = re.search(r'^l\.(\d+)\s*(.*)', lines[j].strip())
                if match:
                    line_num = int(match.group(1))
                    err_context = match.group(2)
                    err_msg = f"{err_msg} (Snippet: {err_context})"
                    break
            errors.append({"line": line_num, "error": err_msg})
        i += 1
    return errors

def compile_and_verify(tex_file, compiler="pdflatex"):
    print(f"=== AUTOMATED COMPILATION & QA VERIFICATION ===")
    print(f"Target TEX: '{tex_file}'")
    
    if not os.path.exists(tex_file):
        print(f"[ERROR] Target file '{tex_file}' does not exist.")
        return False
        
    base_name = os.path.splitext(os.path.basename(tex_file))[0]
    output_dir = os.path.dirname(tex_file) or "."
    
    # Run compiler
    cmd = [compiler, "-interaction=nonstopmode", f"-output-directory={output_dir}", tex_file]
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        print(f"[ERROR] Failed to launch compiler '{compiler}': {e}")
        return False
        
    log_path = os.path.join(output_dir, f"{base_name}.log")
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    if proc.returncode != 0 or not os.path.exists(pdf_path):
        print("\n[COMPILATION ERROR] pdflatex encountered errors. Extracting surgical feedback...")
        errors = parse_log_for_errors(log_path)
        print(f"\nFound {len(errors)} actionable syntax/LaTeX errors:")
        for idx, err in enumerate(errors, 1):
            line_info = f"Line {err['line']}" if err['line'] > 0 else "Unknown Line"
            print(f"  [{idx}] {line_info}: {err['error']}")
        print("\n[FAIL] Please correct the reported LaTeX errors above and run again.\n")
        return False
        
    print(f"[OK] Compilation successful! Generated PDF: '{pdf_path}'")
    
    # Auto-trigger QA verification if matching original PDF exists
    # Look up matching PDF in pdfs/
    orig_candidates = glob.glob(f"pdfs/*{base_name}*.pdf")
    if not orig_candidates:
        orig_candidates = glob.glob(f"pdfs/*.pdf")
        
    if orig_candidates:
        orig_pdf = orig_candidates[0]
        print(f"\n[AUTO-TRIGGER] Launching 1:1 QA Diff Check against '{orig_pdf}'...")
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            qa_script = os.path.join(script_dir, "qa_verify_fidelity.py")
            qa_proc = subprocess.run([sys.executable, qa_script, orig_pdf, pdf_path], text=True)
            if qa_proc.returncode == 0:
                print("[OK] Integrated compilation and 1:1 verification passed successfully!\n")
                return True
            else:
                print("[QA WARNING] Compilation succeeded, but QA fidelity check reported warnings/errors.\n")
                return False
        except Exception as e:
            print(f"[ERROR] Could not run qa_verify_fidelity.py: {e}")
            return True
    else:
        print("[INFO] No matching source PDF found in 'pdfs/' to run auto-QA. Skipping diff check.\n")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/compile_and_check.py <path/to/file.tex> [compiler]")
        sys.exit(1)
    target_tex = sys.argv[1]
    comp = sys.argv[2] if len(sys.argv) > 2 else "pdflatex"
    success = compile_and_verify(target_tex, compiler=comp)
    sys.exit(0 if success else 1)
