#Ollama 응답
import ollama

def generate_response(prompt: str) -> str:
    try:
        response = ollama.chat(model="gemma:2b", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        return f"[ERROR] Ollama 응답 실패: {e}"
