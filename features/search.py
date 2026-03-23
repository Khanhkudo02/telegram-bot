from duckduckgo_search import DDGS

def search_web(q):
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(q, max_results=6)]
        if not results:
            return "❌ Không tìm thấy kết quả phù hợp."

        formatted = []
        for r in results:
            title = r.get("title", "No title")
            body = r.get("body", "")[:180]
            href = r.get("href", "")
            formatted.append(f"🔗 {title}\n{body}\n{href}\n")

        return "\n".join(formatted)
    except Exception as e:
        print(f"SEARCH ERROR: {e}")
        return "❌ Lỗi khi tìm kiếm. Thử lại sau."