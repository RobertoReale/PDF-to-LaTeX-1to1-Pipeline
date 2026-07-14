import os
import sys
import glob
import argparse
import fitz  # PyMuPDF

def prepare_batches(pdf_path=None, pages_per_batch=15, output_dir="pdfs", update_main_tex=True):
    print("=== AUTOMATED PDF BATCH PARTITIONING & MAIN.TEX SETUP ===")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("tex", exist_ok=True)
    
    if not pdf_path:
        # Auto-detect master PDF in pdfs/ or root
        candidates = sorted(glob.glob("*.pdf") + glob.glob("pdfs/*.pdf"))
        if not candidates:
            print("[ERROR] No PDF found. Please specify a master PDF path using --pdf or place it in 'pdfs/'.")
            return False
        pdf_path = candidates[0]
        
    print(f"Master PDF selected: '{pdf_path}'")
    
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[ERROR] Could not open PDF '{pdf_path}': {e}")
        return False
        
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    
    toc = doc.get_toc()
    batches = []
    
    if toc:
        print("[INFO] Table of Contents (TOC) detected. Partitioning by chapters/outline...")
        # TOC entry structure: [level, title, page_number (1-indexed)]
        # Filter top-level or chapter entries
        chapters = [entry for entry in toc if entry[0] == 1 or "Chapter" in entry[1] or "Capitolo" in entry[1] or "Lezione" in entry[1] or "Lecture" in entry[1]]
        if not chapters:
            chapters = toc
            
        for idx, entry in enumerate(chapters):
            title = entry[1].strip()
            start_page = max(1, entry[2])
            if idx + 1 < len(chapters):
                end_page = max(start_page, chapters[idx + 1][2] - 1)
            else:
                end_page = total_pages
                
            batch_num = idx + 1
            safe_title = "".join(c if c.isalnum() else "_" for c in title)[:30].strip("_")
            filename = f"Chapter_{batch_num:02d}_{safe_title}.pdf" if safe_title else f"Chapter_{batch_num:02d}.pdf"
            batches.append((filename, start_page - 1, end_page - 1, title))
    else:
        print(f"[INFO] No Table of Contents detected. Partitioning into fixed batches of {pages_per_batch} pages...")
        batch_num = 1
        for start_page in range(0, total_pages, pages_per_batch):
            end_page = min(total_pages - 1, start_page + pages_per_batch - 1)
            filename = f"Batch_{batch_num:02d}_p{start_page+1}_to_p{end_page+1}.pdf"
            batches.append((filename, start_page, end_page, f"Batch {batch_num:02d} (Pages {start_page+1}-{end_page+1})"))
            batch_num += 1
            
    print(f"Generated {len(batches)} batches/chapters:")
    
    subfile_names = []
    
    for filename, start_idx, end_idx, title in batches:
        out_path = os.path.join(output_dir, filename)
        subdoc = fitz.open()
        subdoc.insert_pdf(doc, from_page=start_idx, to_page=end_idx)
        subdoc.save(out_path)
        subdoc.close()
        
        # Determine corresponding tex subfile name
        base_name = os.path.splitext(filename)[0]
        tex_name = f"tex/{base_name}.tex"
        subfile_names.append((base_name, title))
        
        # Create skeleton subfile if not exists
        if not os.path.exists(tex_name):
            skeleton = (
                "\\documentclass[../main.tex]{subfiles}\n\n"
                "\\begin{document}\n\n"
                f"\\chapter{{{title}}}\n\n"
                "% 1:1 Fidelity typeset content for this chapter goes here...\n\n"
                "\\end{document}\n"
            )
            with open(tex_name, "w", encoding="utf-8") as tf:
                tf.write(skeleton)
                
        print(f"  [Batch Saved] '{out_path}' (Pages {start_idx+1}-{end_idx+1}) -> '{tex_name}'")
        
    if update_main_tex:
        print("\nUpdating 'main.tex' with modular subfile references...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template_main = os.path.join(script_dir, "..", "templates", "main.tex")
        template_preamble = os.path.join(script_dir, "..", "templates", "preamble.tex")
        
        main_tex_path = "main.tex" if os.path.exists("main.tex") else ("templates/main.tex" if os.path.exists("templates/main.tex") else template_main)
        
        # Ensure root preamble.tex exists when initializing root main.tex
        if not os.path.exists("preamble.tex"):
            preamble_source = "templates/preamble.tex" if os.path.exists("templates/preamble.tex") else template_preamble
            if os.path.exists(preamble_source):
                with open(preamble_source, "r", encoding="utf-8") as pf:
                    preamble_data = pf.read()
                with open("preamble.tex", "w", encoding="utf-8") as pf:
                    pf.write(preamble_data)
                print("[OK] Initialized root 'preamble.tex' from template.")
        
        if os.path.exists(main_tex_path):
            with open(main_tex_path, "r", encoding="utf-8") as mf:
                content = mf.read()
                
            if "\\mainmatter" in content:
                pre, post = content.split("\\mainmatter", 1)
                if "\\end{document}" in post:
                    body, footer = post.split("\\end{document}", 1)
                else:
                    body, footer = post, "\n\\end{document}\n"
                    
                new_subfiles = []
                for idx, (base_name, title) in enumerate(subfile_names):
                    comment = "" if idx == 0 else "% "
                    new_subfiles.append(f"{comment}\\subfile{{tex/{base_name}}}  % {title}")
                    
                subfiles_block = "\n% Uncomment chapters progressively as they are processed and verified 1:1\n" + "\n".join(new_subfiles) + "\n\n"
                new_content = pre + "\\mainmatter\n" + subfiles_block + "\\end{document}" + footer
                
                target_main = "main.tex"
                with open(target_main, "w", encoding="utf-8") as mf:
                    mf.write(new_content)
                print(f"[OK] Successfully updated '{target_main}' with {len(subfile_names)} chapter subfiles.")
        else:
            print("[WARNING] Could not find 'main.tex' or 'templates/main.tex' to update.")
            
    print("[OK] Batch preparation completed successfully.\n")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Partition PDF into chapter batches and initialize main.tex")
    parser.add_argument("--pdf", type=str, help="Path to master PDF file")
    parser.add_argument("--pages-per-batch", type=int, default=15, help="Number of pages per batch if TOC is missing")
    parser.add_argument("--output-dir", type=str, default="pdfs", help="Directory to store partitioned chapter PDFs")
    parser.add_argument("--no-update-main", action="store_true", help="Skip updating main.tex")
    
    args = parser.parse_args()
    success = prepare_batches(pdf_path=args.pdf, pages_per_batch=args.pages_per_batch, output_dir=args.output_dir, update_main_tex=not args.no_update_main)
    sys.exit(0 if success else 1)
