from pathlib import Path
import fitz  # PyMuPDF

project_root = Path(__file__).resolve().parent.parent
pdf_dir = project_root / "pdfs"
text_dir = project_root / "texts"

text_dir.mkdir(exist_ok=True)

pdf_files = list(pdf_dir.glob("*.pdf"))

if not pdf_files:
    print("pdfs 文件夹里没有 PDF 文件")
else:
    for pdf_file in pdf_files:
        doc = fitz.open(pdf_file)
        all_text = []

        for page in doc:
            all_text.append(page.get_text())

        output_file = text_dir / f"{pdf_file.stem}.txt"
        output_file.write_text("\n".join(all_text), encoding="utf-8")

        print(f"已转换: {pdf_file.name} -> {output_file.name}")