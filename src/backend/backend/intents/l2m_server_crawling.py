import os
import re
import json

def extract_server_map_from_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    match = re.search(r'var _serverNameMap = (\[.*?\]);', html, re.DOTALL)
    if not match:
        print("[❌] 서버 리스트를 찾을 수 없습니다.")
        return

    json_text = match.group(1)
    server_list = json.loads(json_text)
    server_map = {entry["serverName"]: int(entry["serverId"]) for entry in server_list}

    # 📌 현재 파일 위치 기준으로 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "server_map.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(server_map, f, indent=2, ensure_ascii=False)

    print(f"[✅] 서버 {len(server_map)}개 저장 완료 → {output_path}")

if __name__ == "__main__":
    extract_server_map_from_html("page_debug.html")
