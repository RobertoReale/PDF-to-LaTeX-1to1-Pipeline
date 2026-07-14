import os
import zipfile
import glob

def package_for_overleaf(zip_filename="Progetto_Overleaf_1to1.zip"):
    print(f"=== PACCHETTIZZAZIONE PROGETTO PER OVERLEAF ===")
    
    files_to_include = []
    
    for root_file in ["main.tex", "preamble.tex", "PROTOCOL_1to1.md", "README.md"]:
        if os.path.exists(root_file):
            files_to_include.append(root_file)
            
    tex_files = sorted(glob.glob("tex/*.tex"))
    files_to_include.extend(tex_files)
    
    fig_files = sorted(glob.glob("figures/*.*"))
    files_to_include.extend(fig_files)
    
    print(f"File selezionati per Overleaf: {len(files_to_include)} file "
          f"({len(tex_files)} lezioni TEX, {len(fig_files)} figure, + file di configurazione).")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath in files_to_include:
            zipf.write(filepath, arcname=filepath)
            
    if os.path.exists(zip_filename):
        size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
        print(f"✔ Archivio creato con successo: '{zip_filename}' ({size_mb:.2f} MB)")
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            bad_file = zipf.testzip()
            if bad_file:
                print(f"❌ Errore di integrità del file compresso: {bad_file}")
                return False
            else:
                print("✔ Verifica di integrità completata all'100%. Pronto per il caricamento su Overleaf!")
        return True
    return False

if __name__ == "__main__":
    success = package_for_overleaf()
    exit(0 if success else 1)
