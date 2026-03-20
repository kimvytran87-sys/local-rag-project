from pathlib import Path
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity


project_root = Path(__file__).resolve().parent.parent
index_dir = project_root / "index"
prompt_file = project_root / "prompt_template.txt"


with open(index_dir / "vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open(index_dir / "vectors.pkl", "rb") as f:
    vectors = pickle.load(f)

with open(index_dir / "chunks.pkl", "rb") as f:
    data = pickle.load(f)


def ask_local_llm(prompt, model="qwen2:7b"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    result = response.json()
    return result["response"]


def translate_query_local(query, model="qwen2:7b"):
    prompt = f"""请将下面的中文问题翻译成适合学术检索的英文关键词。
要求：
1. 只输出英文关键词
2. 不要写完整句子
3. 用空格分隔
4. 保留核心主题词、方法词、指标词

中文问题：
{query}

英文关键词："""
    result = ask_local_llm(prompt, model=model)
    return result.strip()


def search_local_knowledge(query, top_k=5, min_score=0.0, model="qwen2:7b"):
    query_en = translate_query_local(query, model=model)
    print("检索关键词：", query_en)

    query_vector = vectorizer.transform([query_en])
    scores = cosine_similarity(query_vector, vectors)[0]

    results = []
    for idx, score in enumerate(scores):
        if score >= min_score:
            results.append({
                "id": data["ids"][idx],
                "score": float(score),
                "text": data["documents"][idx]
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def build_prompt(query, top_k=5, min_score=0.0, model="qwen2:7b"):
    results = search_local_knowledge(query, top_k=top_k, min_score=min_score, model=model)
    context = "\n\n".join([r["text"] for r in results])

    template = prompt_file.read_text(encoding="utf-8")
    prompt = template.format(context=context, query=query)
    return prompt, results


def run_rag_once(query, top_k=5, min_score=0.0, model="qwen2:7b"):
    print("=== 本地RAG系统 ===")
    print("问题：", query)
    print("检索条数：", top_k)
    print("最小相似度：", min_score)

    prompt, results = build_prompt(query, top_k=top_k, min_score=min_score, model=model)

    print("\n=== 检索结果（前3条）===")
    for i, r in enumerate(results[:3], 1):
        print(f"\n[{i}] ID: {r['id']}")
        print(f"相似度: {round(r['score'], 4)}")
        print(r["text"][:300])

    print("\n=== 正在生成回答 ===")
    answer = ask_local_llm(prompt, model=model)

    print("\n=== 最终回答 ===\n")
    print(answer)

    return {
        "query": query,
        "results": results,
        "prompt": prompt,
        "answer": answer
    }


if __name__ == "__main__":
    query = input("请输入你的问题：")
    top_k = int(input("检索条数（默认5）：") or 5)
    min_score = float(input("最小相似度（默认0）：") or 0.0)

    run_rag_once(
        query=query,
        top_k=top_k,
        min_score=min_score,
        model="qwen2:7b"
    )