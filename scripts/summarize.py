import os
import re
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

PROMPT_TEMPLATE = """請用繁體中文寫三句話介紹以下 GitHub 專案。只輸出三句話，不要任何其他內容。

第一句：這是什麼。
第二句：它的特色或解決什麼問題。
第三句：適合誰使用。

專案：{name}
描述：{description}
語言：{language}"""


def load_models() -> list[str]:
    """從 config.json 載入模型清單，// 開頭的項目視為已停用。"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    active = [m for m in config.get("llm_models", []) if not m.startswith("//")]
    if not active:
        raise ValueError("config.json 中沒有任何啟用的模型，請至少保留一個（移除 // 開頭）")
    print(f"[Config] 使用模型：{active}")
    return active


def extract_clean_summary(text: str) -> str:
    """從模型輸出中抽取最後一段純中文介紹，過濾掉推理過程。"""
    # 策略 1：Gemma 的 "Refining Sentence N:" 格式 — 抓最後精煉的三句
    refining = re.findall(r'Refining Sentence \d+:\s*([一-鿿][^\n(]+。)', text)
    if len(refining) >= 3:
        return ''.join(s.strip() for s in refining[:3])

    # 策略 2：找最後一個高中文比例段落（>60% 中文字、2–4 句、60–300 字）
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    for para in reversed(paragraphs):
        chinese = len(re.findall(r'[一-鿿]', para))
        total = len(para.replace(' ', '').replace('\n', ''))
        if total == 0:
            continue
        if chinese / total > 0.6 and 2 <= para.count('。') <= 4 and 60 <= len(para) <= 300:
            return para

    # 策略 3：原本邏輯（保底）
    for para in reversed(paragraphs):
        has_chinese = bool(re.search(r'[一-鿿]', para))
        is_reasoning = bool(re.search(r'^[\*\-\d]|^\s*[\*\-]', para, re.MULTILINE))
        if has_chinese and not is_reasoning and len(para) >= 30:
            return para

    return text


def build_prompt(project: dict) -> str:
    return PROMPT_TEMPLATE.format(
        name=project.get("name", ""),
        description=project.get("description", "（無描述）"),
        language=project.get("language", "未知"),
        url=project.get("url", ""),
    )


def call_gemini(model_name: str, prompt: str) -> str:
    url = f"{GEMINI_BASE}/{model_name}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload, timeout=60)

    if resp.status_code in (429, 500, 503):
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

    resp.raise_for_status()
    data = resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"回應格式異常：{e}  raw={data}")


def generate_summary(project: dict, models: list[str]) -> tuple[str, str]:
    """回傳 (summary_zh, model_used)"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY 未設定")

    prompt = build_prompt(project)

    for model_name in models:
        try:
            raw = call_gemini(model_name, prompt)
            text = extract_clean_summary(raw)
            print(f"  [OK] {model_name}")
            return text, model_name
        except Exception as e:
            print(f"  [WARN] {model_name} 失敗：{e}，嘗試下一個...")
            time.sleep(2)

    print(f"  [ERROR] 所有模型均失敗，{project['name']} 摘要留空")
    return "", "none"


def summarize_projects(projects: list[dict]) -> list[dict]:
    models = load_models()
    result = []
    for i, project in enumerate(projects):
        print(f"[{i+1}/{len(projects)}] 生成摘要：{project['name']}")
        summary, model_used = generate_summary(project, models)
        enriched = dict(project)
        enriched["summary_zh"] = summary
        enriched["model_used"] = model_used
        result.append(enriched)
        if i < len(projects) - 1:
            time.sleep(1)
    return result


if __name__ == "__main__":
    sample = [{
        "name": "ollama/ollama",
        "url": "https://github.com/ollama/ollama",
        "description": "Get up and running with Llama 3",
        "language": "Go",
        "stars_today": 523,
        "total_stars": 82400,
    }]
    out = summarize_projects(sample)
    for p in out:
        print(p.get("summary_zh"))
        print("模型：", p.get("model_used"))
