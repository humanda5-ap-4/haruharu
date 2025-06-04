#Ollama 응답
import ollama

def generate_response(prompt: str) -> str:
    try:
        response = ollama.chat(model="mistral:7b-instruct", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        return f"[ERROR] Ollama 응답 실패: {e}"
