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
    print(f"[{base_name}] Extracting content from {len(doc)} pages...")
    
    full_text = []
    
    for i, page in enumerate(doc):
        # 1. Formatted Text Extraction (block by block)
        blocks = page.get_text("blocks")
        full_text.append(f"--- PAGE {i+1} ---")
        for b in blocks:
            text = b[4].strip()
            if text:
                full_text.append(text)
                
        # 2. Embedded Raster Image Extraction
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
            print(f"  [Raster Image] Saved: {img_filename}")
            
        # 3. Vector Drawing Extraction (Schematics, Circuits, Plots)
        drawings = page.get_drawings()
        if drawings:
            # Calculate overall bounding box or cluster of drawings
            rects = [fitz.Rect(d["rect"]) for d in drawings]
            # Merge contiguous rectangles if present
            if rects:
                union_rect = rects[0]
                for r in rects[1:]:
                    union_rect = union_rect | r
                
                # If drawing occupies significant space, extract at 300 DPI
                if union_rect.width > 30 and union_rect.height > 30:
                    pix = page.get_pixmap(dpi=300, clip=union_rect)
                    vec_filename = f"{base_name}_p{i+1}_vector.png"
                    pix.save(os.path.join(figures_dir, vec_filename))
                    print(f"  [Vector Drawing] Saved bounding box {union_rect}: {vec_filename}")
                    
    text_path = os.path.join(chapter_dir, "text.txt")
    with open(text_path, "w", encoding="utf-8") as tf:
        tf.write("\n".join(full_text))
        
    print(f"[OK] [{base_name}] Completed! Verification text saved to '{text_path}'.\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdfs = sys.argv[1:]
    else:
        pdfs = sorted(glob.glob("pdfs/*.pdf") + glob.glob("pdfs/*/*.pdf"))
        
    if not pdfs:
        print("[ERROR] No PDF found. Place PDFs inside 'pdfs/' directory or specify paths via command line.")
        sys.exit(1)
        
    for pdf in pdfs:
        extract_content(pdf)
    sys.exit(0)
