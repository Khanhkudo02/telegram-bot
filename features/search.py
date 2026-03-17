from duckduckgo_search import DDGS

def search_web(query):
    try:
        text = ""
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return "❌ Không tìm thấy."

        for r in results:
            text += f"{r['title']}\n{r['body']}\n\n"

        return text.strip()

    except:
        return "❌ Lỗi tìm kiếm."
