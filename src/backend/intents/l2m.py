from backend.intents.l2m_utils import get_server_id_by_name
from backend.intents.l2m_api import get_item_price_info
# from backend.common.response import generate_response  # 임시로 주석 처리

PROMPT_TEMPLATE = """
    
    다음은 리니지2M '{server}' 서버의 '{item}' 아이템 시세 정보입니다:
    최저가: {min_price} 다이아
    평균가: {avg_price} 다이아
    최고가: {max_price} 다이아
"""
SUMMARY_TEMPLATE = """
'{item}'에 대한 전체 서버 시세입니다 (상위 {count}개):

{lines}
"""

def merge_entities_by_type(entities, target_type):
    merged = []
    buffer = []
    for e in entities:
        if e.type == target_type:
            buffer.append(e.value)
        else:
            if buffer:
                merged.append(" ".join(buffer))
                buffer = []
    if buffer:
        merged.append(" ".join(buffer))
    return merged

def handle(query: str, entities: list) -> str:
    print(f"[DEBUG] 원본 엔티티: {[{'type': e.type, 'value': e.value} for e in entities]}")

    server_entities = merge_entities_by_type(entities, "SERVER")
    item_entities = merge_entities_by_type(entities, "ITEM")

    server = "".join(server_entities) if server_entities else None
    item = " ".join(item_entities) if item_entities else None

    print(f"[DEBUG] 병합된 서버명: {server}")
    print(f"[DEBUG] 병합된 아이템명: {item}")

    if not item:
        return "[BOT] 아이템명을 정확히 입력해주세요."

    server_id = None
    server_name = ""
    if server:
        server_name = server.replace("서버", "")
        server_id = get_server_id_by_name(server_name)
        if not server_id:
            return f"[BOT] 서버 '{server}' 를 찾을 수 없습니다."

    response = get_item_price_info(item, server_id)
    print(f"[DEBUG] API 응답: {response}")

    items = response.get("contents", [])
    if not items:
        return f"[BOT] '{item}'에 대한 시세 정보를 찾을 수 없습니다."

    if server_id:
        matched_items = [i for i in items if i.get("server_id") == server_id]
        if not matched_items:
            return f"[BOT] '{item}'에 대한 시세 정보를 찾을 수 없습니다."
        item_info = matched_items[0]
        min_price = item_info.get("now_min_unit_price", "N/A")
        avg_price = item_info.get("avg_unit_price", "N/A")
        max_price = item_info.get("max_unit_price", "N/A")
        prompt = PROMPT_TEMPLATE.format(
            server=server,
            item=item,
            min_price=min_price,
            avg_price=avg_price,
            max_price=max_price if max_price != "N/A" else "데이터 없음"
        )
        # generate_response 대신 바로 리턴 (디버그용)
        return prompt.strip()
    else:
        summary_lines = []
        for i in items[:10]:
            server_name = i.get("server_name", "알 수 없음")
            min_p = i.get("now_min_unit_price", "N/A")
            avg_p = i.get("avg_unit_price", "N/A")
            summary_lines.append(f"{server_name} -  최저가: {min_p} /  평균가: {avg_p}")

        if not summary_lines:
            return f"[BOT] '{item}'에 대한 전체 서버 시세 정보를 찾을 수 없습니다."

        summary = SUMMARY_TEMPLATE.format(
            item=item,
            count=len(summary_lines),
            lines="\n".join(summary_lines)
        )
        # generate_response 대신 바로 리턴 (디버그용)
        return summary.strip()
