"""
llm.py
可选大模型裁决接口（可插拔）。
不配置环境变量时 enabled() 返回 False，分类自动回落到扩展名/默认规则，保持零依赖可用。
配置 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL 后，可接入任意 OpenAI 兼容的推理 API。
"""
import os
import json


def enabled() -> bool:
    return bool(os.environ.get("LLM_API_KEY"))


def ask_classify(path, top_k: int = 5) -> str:
    """调用大模型对文件名/内容做分类，返回分类名。"""
    import urllib.request

    api_key = os.environ.get("LLM_API_KEY", "")
    base = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1")
    model = os.environ.get("LLM_MODEL", "deepseek-chat")
    categories = os.environ.get("LLM_CATEGORIES", "票据,合同,文档,图片,代码,其他")

    prompt = (
        f"这是一个文件名：{path.name}\n"
        f"请将它归入以下类别之一（只输出类别名，不要解释）：{categories}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": 10,
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()
