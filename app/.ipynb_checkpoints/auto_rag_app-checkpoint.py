from pathlib import Path
from rag_app import run_rag_once
import subprocess
import sys
import importlib


project_root = Path(__file__).resolve().parent.parent
app_dir = project_root / "app"


def run_step(script_name, step_name):
    script_path = app_dir / script_name
    print(f"\n=== 开始：{step_name} ===")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=project_root,
        text=True
    )

    if result.returncode != 0:
        print(f"\n❌ {step_name} 失败，请先检查：{script_name}")
        sys.exit(1)

    print(f"✅ {step_name} 完成")


def main():
    print("=== 本地离线 RAG 自动化系统 ===")

    rebuild = input("是否重新处理 PDF、分片并重建索引？(y/n，默认 y)：").strip().lower() or "y"

    if rebuild == "y":
        run_step("pdf_to_text.py", "PDF 转文本")
        run_step("split_text.py", "文本分片")
        run_step("search_chunks.py", "建立索引")
    else:
        print("跳过知识库重建，直接进入问答")

    print("\n=== 加载问答模块 ===")
    query = input("请输入你的问题：").strip()
    top_k = int(input("检索条数（默认5）：") or 5)
    min_score = float(input("最小相似度（默认0）：") or 0.0)

    run_rag_once(
        query=query,
        top_k=top_k,
        min_score=min_score,
        model="qwen2:7b"
    )


if __name__ == "__main__":
    main()
    import os
    sys.path.append(os.path.dirname(__file__))