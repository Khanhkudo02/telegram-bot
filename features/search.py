from duckduckgo_search import DDGS

def search_web(q):
    try:
        with DDGS() as d:
            r = list(d.text(q, max_results=5))
        return "\n\n".join([i["title"] for i in r])
    except:
        return "❌ lỗi search"