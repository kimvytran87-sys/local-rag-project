from pathlib import Path
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

project_root = Path(__file__).resolve().parent.parent
output_dir = project_root / "output"
index_dir = project_root / "index"

index_dir.mkdir(exist_ok=True)

json_files = list(output_dir.glob("*_chunks.json"))

if not json_files:
    print("没有找到分块文件")
else:
    def is_noise_chunk(text):
        noise_keywords = [
            "received", "accepted", "published", "doi", "email",
            "foundation", "corresponding author", "citation",
            "copyright", "all rights reserved", "keywords:"
        ]

        text_lower = text.lower()
        hit = sum(1 for k in noise_keywords if k in text_lower)
        if hit >= 2:
            return True
        if len(text.strip()) < 50:
            return True
        return False
    all_chunks = []
    ids = []

    for file in json_files:
        chunks = json.loads(file.read_text(encoding="utf-8"))
        for i, chunk in enumerate(chunks):
            if not is_noise_chunk(chunk):
                all_chunks.append(chunk)
                ids.append(f"{file.stem}_{i}")

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(all_chunks)

    with open(index_dir / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    with open(index_dir / "vectors.pkl", "wb") as f:
        pickle.dump(vectors, f)

    with open(index_dir / "chunks.pkl", "wb") as f:
        pickle.dump({"ids": ids, "documents": all_chunks}, f)

    print(f"索引完成，chunks={len(all_chunks)}")