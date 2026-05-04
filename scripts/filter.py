import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


def load_keywords() -> list[str]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    keywords = []
    for category_words in config["ai_keywords"].values():
        keywords.extend(category_words)
    return keywords


def is_ai_related(project: dict, keywords: list[str]) -> bool:
    text = (project.get("description", "") + " " + project.get("name", "")).lower()
    return any(kw in text for kw in keywords)


def filter_ai(projects: list[dict]) -> list[dict]:
    keywords = load_keywords()
    return [p for p in projects if is_ai_related(p, keywords)]


if __name__ == "__main__":
    keywords = load_keywords()
    print(f"載入 {len(keywords)} 個關鍵字")

    sample = [
        {"name": "ollama/ollama", "description": "Get up and running with Llama 3"},
        {"name": "torvalds/linux", "description": "Linux kernel source tree"},
        {"name": "openai/whisper", "description": "Robust speech recognition via large-scale weak supervision"},
    ]
    result = filter_ai(sample)
    print(f"過濾後剩 {len(result)} 筆：{[r['name'] for r in result]}")
