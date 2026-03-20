from pathlib import Path
import json
import re

def clean_text_before_split(text):
    lines = text.splitlines()
    cleaned_lines = []

    skip_patterns = [
        r"^Received[:：]",
        r"^Revised[:：]",
        r"^Accepted[:：]",
        r"^Published online[:：]",
        r"^URL[:：]",
        r"^Foundation items?[:：]",
        r"^\*?\s*Corresponding author",
        r"^DOI[:：]",
        r"^E-mail[:：]",
        r"^Email[:：]",
        r"^Citation[:：]",
        r"^Copyright",
        r"^©",
        r"^Keywords?[:：]",
        r"^Key words[:：]",
    ]

    for line in lines:
        line = line.strip()
        if not line:
            cleaned_lines.append("")
            continue

        should_skip = False
        for pattern in skip_patterns:
            if re.search(pattern, line, flags=re.IGNORECASE):
                should_skip = True
                break

        # 过滤纯页码、纯年份、很短的杂项编号行
        if re.fullmatch(r"[-–—\d\s./]+", line):
            should_skip = True

        if not should_skip:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

project_root = Path(__file__).resolve().parent.parent
text_dir = project_root / "texts"
output_dir = project_root / "output"

output_dir.mkdir(exist_ok=True)

max_chunk_size = 500
overlap_sentences = 2

def split_into_sentences(text):
    # 简单中英文句子切分
    sentences = re.split(r'(?<=[。！？.!?])', text)
    return [s.strip() for s in sentences if s.strip()]

txt_files = list(text_dir.glob("*.txt"))

if not txt_files:
    print("texts 文件夹里没有 txt 文件")
else:
    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8")
        text = clean_text_before_split(text)
        sentences = split_into_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) <= max_chunk_size:
                current_chunk.append(sentence)
                current_length += len(sentence)
            else:
                chunks.append("".join(current_chunk))

                # 加 overlap（上下文连续性）
                overlap = current_chunk[-overlap_sentences:] if len(current_chunk) >= overlap_sentences else current_chunk
                current_chunk = overlap + [sentence]
                current_length = sum(len(s) for s in current_chunk)

        if current_chunk:
            chunks.append("".join(current_chunk))

        output_file = output_dir / f"{txt_file.stem}_chunks.json"
        output_file.write_text(
            json.dumps(chunks, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"{txt_file.name} 已完成，chunks={len(chunks)}")