import os
import sys
import zipfile
import glob

def package_for_overleaf(zip_filename="Overleaf_Project_1to1.zip"):
    print(f"=== OVERLEAF PROJECT PACKAGING ===")
    
    files_to_include = []
    arcname_map = {}
    
    # Check root configuration and legal/dependency files
    for root_file in ["PROTOCOL_1to1.md", "README.md", "PROMPT_TEMPLATE.txt", "LICENSE", "requirements.txt"]:
        if os.path.exists(root_file):
            files_to_include.append(root_file)
            arcname_map[root_file] = root_file
            
    # Include main.tex and preamble.tex (fallback to templates/ if not in root)
    for core_tex in ["main.tex", "preamble.tex"]:
        if os.path.exists(core_tex):
            files_to_include.append(core_tex)
            arcname_map[core_tex] = core_tex
        elif os.path.exists(os.path.join("templates", core_tex)):
            template_path = os.path.join("templates", core_tex)
            files_to_include.append(template_path)
            arcname_map[template_path] = core_tex
            
    tex_files = sorted(glob.glob("tex/*.tex"))
    for tf in tex_files:
        files_to_include.append(tf)
        arcname_map[tf] = tf
        
    fig_files = sorted(glob.glob("figures/*.*"))
    for ff in fig_files:
        files_to_include.append(ff)
        arcname_map[ff] = ff
        
    print(f"Files selected for Overleaf: {len(files_to_include)} files "
          f"({len(tex_files)} TEX chapters, {len(fig_files)} figures, + core configuration/templates).")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath in files_to_include:
            zipf.write(filepath, arcname=arcname_map[filepath])
            
    if os.path.exists(zip_filename):
        size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
        print(f"[OK] Archive successfully created: '{zip_filename}' ({size_mb:.2f} MB)")
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            bad_file = zipf.testzip()
            if bad_file:
                print(f"[ERROR] ZIP archive integrity error: {bad_file}")
                return False
            else:
                print("[OK] Integrity verification 100% passed. Ready for upload to Overleaf!")
        return True
    return False

if __name__ == "__main__":
    success = package_for_overleaf()
    sys.exit(0 if success else 1)
