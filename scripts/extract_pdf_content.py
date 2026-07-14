import os
import sys
import glob
import fitz  # PyMuPDF

def extract_content(pdf_path, output_dir="raw_extract", figures_dir="figures"):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    chapter_dir = os.path.join(output_dir, base_name)
    os.makedirs(chapter_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    print(f"[{base_name}] Estrazione da {len(doc)} pagine in corso...")
    
    full_text = []
    
    for i, page in enumerate(doc):
        # 1. Estrazione Testo Formattato (a blocchi)
        blocks = page.get_text("blocks")
        full_text.append(f"--- PAGINA {i+1} ---")
        for b in blocks:
            text = b[4].strip()
            if text:
                full_text.append(text)
                
        # 2. Estrazione Immagini Raster Incorporate
        images = page.get_images(full=True)
        for img_idx, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            img_filename = f"{base_name}_p{i+1}_img_{img_idx+1}.{image_ext}"
            img_path = os.path.join(figures_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(image_bytes)
            print(f"  [Immagine Raster] Salvata: {img_filename}")
            
        # 3. Estrazione Disegni Vettoriali (Schemi, Circuiti, Grafici)
        drawings = page.get_drawings()
        if drawings:
            # Calcola il bounding box complessivo o di cluster dei disegni
            rects = [fitz.Rect(d["rect"]) for d in drawings]
            # Unisci i rettangoli contigui se presenti
            if rects:
                union_rect = rects[0]
                for r in rects[1:]:
                    union_rect = union_rect | r
                
                # Se il disegno occupa uno spazio significativo, estrailo come immagine vettoriale a 300 DPI
                if union_rect.width > 30 and union_rect.height > 30:
                    pix = page.get_pixmap(dpi=300, clip=union_rect)
                    vec_filename = f"{base_name}_p{i+1}_vector.png"
                    pix.save(os.path.join(figures_dir, vec_filename))
                    print(f"  [Schema Vettoriale] Salvato bounding box {union_rect}: {vec_filename}")
                    
    text_path = os.path.join(chapter_dir, "text.txt")
    with open(text_path, "w", encoding="utf-8") as tf:
        tf.write("\n".join(full_text))
        
    print(f"✔ [{base_name}] Completato! Testo di riscontro salvato in '{text_path}'.\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = sorted(glob.glob("pdfs/*.pdf") + glob.glob("pdfs/*/*.pdf"))
        
    if not pdfs:
        print("❌ Nessun PDF trovato. Inserisci i PDF in pdfs/ o specifica il percorso via riga di comando.")
        sys.exit(1)
        
    for pdf in pdfs:
        extract_content(pdf)
