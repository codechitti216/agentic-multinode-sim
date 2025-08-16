import requests, json
from config import LMSTUDIO_BASE_URL, LMSTUDIO_API_KEY

def call_llm_simple(incident_text: str, model: str = None, timeout=8):
    url = f"{LMSTUDIO_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LMSTUDIO_API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "You are a concise planner. Produce a JSON `plan` array of steps. Each step: {step_id, title, agent_type, params, depends_on}"},
        {"role": "user", "content": incident_text}
    ]
    body = {"model": model or "MaziyarPanahi/Qwen2.5-7B-Instruct-GGUF", "messages": messages, "temperature": 0.0}
    try:
        r = requests.post(url, json=body, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        # try standard OpenAI-like response
        if isinstance(data, dict) and "choices" in data:
            choice = data["choices"][0]
            # LM Studio may return .message.content
            content = (choice.get("message") or {}).get("content") or choice.get("text")
            return content
        return None
    except Exception:
        return None
