AI_KEYWORDS = [
    # 模型名稱
    "llm", "gpt", "claude", "gemini", "mistral", "llama", "phi",
    "qwen", "deepseek", "falcon", "vicuna", "alpaca",
    # 技術術語
    "transformer", "diffusion", "embedding", "inference",
    "fine-tune", "finetune", "rag", "retrieval", "attention",
    "tokenizer", "quantization", "lora", "qlora",
    # 應用場景
    "agent", "chatbot", "copilot", "assistant",
    "langchain", "llamaindex", "openai", "anthropic",
    "stable diffusion", "text-to-image", "image generation",
    # 通用詞
    "ai", "artificial intelligence", "machine learning",
    "deep learning", "neural network", "nlp",
    "multimodal", "vision model",
]


def is_ai_related(project: dict) -> bool:
    text = (project.get("description", "") + " " + project.get("name", "")).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def filter_ai(projects: list[dict]) -> list[dict]:
    return [p for p in projects if is_ai_related(p)]


if __name__ == "__main__":
    sample = [
        {"name": "ollama/ollama", "description": "Get up and running with Llama 3"},
        {"name": "torvalds/linux", "description": "Linux kernel source tree"},
        {"name": "openai/whisper", "description": "Robust speech recognition via large-scale weak supervision"},
    ]
    result = filter_ai(sample)
    print(f"過濾後剩 {len(result)} 筆：{[r['name'] for r in result]}")
