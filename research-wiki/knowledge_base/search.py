import json, os, sys
kb_dir = os.path.dirname(os.path.abspath(__file__))
papers_dir = os.path.join(kb_dir, "papers")

def search(query, top_k=10):
    results = []
    q = query.lower()
    query_terms = q.split()
    for fname in ["domain_overview.md", "metrics_and_baselines.md", "field_conventions.md"]:
        fpath = os.path.join(kb_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                text = f.read()
            low = text.lower()
            score = sum(low.count(t) for t in query_terms)
            if score > 0:
                idx = low.find(query_terms[0]) if query_terms else 0
                results.append({"source": fname, "score": score, "type": "domain",
                                "snippet": text[max(0,idx-200):idx+200]})
    if os.path.isdir(papers_dir):
        for fname in os.listdir(papers_dir):
            if not fname.endswith(".json"): continue
            with open(os.path.join(papers_dir, fname), encoding="utf-8") as f:
                data = json.load(f)
            text = data.get("full_text", "")
            low = text.lower()
            score = sum(low.count(t) for t in query_terms)
            if score > 0:
                idx = low.find(query_terms[0]) if query_terms else 0
                results.append({"source": data.get("slug", fname), "score": score, "type": "paper",
                                "snippet": text[max(0,idx-200):idx+200]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    for r in search(" ".join(sys.argv[1:])):
        print("\n[%s] %s (score=%d)" % (r["type"], r["source"], r["score"]))
        print("  ...%s..." % r["snippet"][:400].replace("\n", " "))
