#!/usr/bin/env python3
import json, os, re, subprocess, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "public" / "data"
DATA.mkdir(parents=True, exist_ok=True)
USER = os.getenv("GITHUB_USER", "Baozhi888")

CATEGORY_RULES = [
    ("AI / LLM", ["ai", "llm", "gpt", "chatgpt", "claude", "gemini", "ollama", "rag", "agent", "openai", "anthropic", "模型", "人工智能", "prompt", "embedding", "mcp"]),
    ("API / Proxy", ["api", "proxy", "gateway", "relay", "中转", "协议", "webhook", "serverless"]),
    ("Web / Frontend", ["vue", "react", "nextjs", "next.js", "nuxt", "frontend", "web", "website", "tailwind", "typescript", "javascript", "博客", "导航"]),
    ("Backend / Database", ["backend", "database", "mysql", "postgres", "redis", "java", "spring", "django", "flask", "fastapi", "golang", "rust"]),
    ("DevOps / Cloud", ["docker", "kubernetes", "k8s", "devops", "cloud", "nginx", "linux", "server", "部署", "运维", "terraform", "ansible"]),
    ("Automation / Crawler", ["automation", "crawler", "spider", "scraper", "workflow", "bot", "自动化", "爬虫"]),
    ("Android / Mobile", ["android", "ios", "flutter", "mobile", "kotlin", "swift", "手机"]),
    ("Media / Design", ["video", "audio", "image", "ffmpeg", "tts", "music", "design", "media", "图片", "视频", "音频"]),
    ("Data / Finance", ["data", "finance", "stock", "quant", "chart", "analytics", "数据", "股票", "金融"]),
    ("Security / Network", ["security", "network", "vpn", "wireguard", "reverse", "tunnel", "安全", "网络", "渗透"]),
    ("Tools / Productivity", ["tool", "utility", "cli", "productivity", "awesome", "collection", "工具", "效率", "file"]),
    ("Learning / Resources", ["tutorial", "course", "book", "learn", "interview", "guide", "教程", "学习", "面试", "资源"]),
]

def gh_pages(endpoint):
    out = subprocess.check_output(["gh", "api", "--paginate", endpoint], text=True)
    dec = json.JSONDecoder(); items=[]; i=0
    while i < len(out):
        while i < len(out) and out[i].isspace(): i += 1
        if i >= len(out): break
        obj, i = dec.raw_decode(out, i)
        items.extend(obj if isinstance(obj,list) else [obj])
    return items

def category(r):
    text = " ".join([r.get("name") or "", r.get("description") or "", r.get("language") or "", " ".join(r.get("topics") or [])]).lower()
    scores=[]
    for idx,(name,keys) in enumerate(CATEGORY_RULES):
        score=sum(3 if k in (r.get("topics") or []) else 1 for k in keys if k.lower() in text)
        if score: scores.append((score,-idx,name))
    return max(scores)[2] if scores else "Other"

def simplify(r, kind):
    pushed=r.get("pushed_at") or r.get("updated_at")
    return {
      "name":r.get("name"), "full_name":r.get("full_name"), "url":r.get("html_url"),
      "description":r.get("description") or "暂无描述", "language":r.get("language") or "Unknown",
      "topics":r.get("topics") or [], "stars":r.get("stargazers_count",0), "forks":r.get("forks_count",0),
      "archived":bool(r.get("archived")), "fork":bool(r.get("fork")), "private":bool(r.get("private")),
      "updated_at":r.get("updated_at"), "pushed_at":pushed, "category":category(r), "kind":kind,
      "owner":(r.get("owner") or {}).get("login","")
    }

def main():
    stars=gh_pages("user/starred?per_page=100")
    repos=gh_pages("user/repos?affiliation=owner&visibility=public&per_page=100&sort=updated")
    all_items=[simplify(x,"starred") for x in stars]+[simplify(x,"fork" if x.get("fork") else "owned") for x in repos]
    seen={};
    for x in all_items:
        key=x["full_name"].lower()
        if key in seen:
            seen[key]["kind"]="owned+starred" if not x["fork"] else "fork+starred"
        else: seen[key]=x
    items=list(seen.values())
    cats={}
    for x in items: cats[x["category"]]=cats.get(x["category"],0)+1
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"user":USER,
      "stats":{"starred":len(stars),"repos":len(repos),"forks":sum(1 for x in repos if x.get('fork')),"items":len(items),"archived":sum(1 for x in items if x['archived'])},
      "categories":dict(sorted(cats.items(), key=lambda z:(-z[1],z[0]))),"items":items}
    (DATA/"repositories.json").write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    md=[f"# {USER} · GitHub Repository Navigator","",f"> 自动整理 {len(stars)} 个 Star 与 {len(repos)} 个自有仓库。", "", "在线导航：**https://statemeta.oaicn.org**", "", "## 分类统计", ""]
    for k,v in payload["categories"].items(): md.append(f"- {k}: {v}")
    md += ["", "数据由服务器定时通过 GitHub API 更新。站点支持全文搜索、分类、语言与仓库类型筛选。"]
    (ROOT/"README.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(json.dumps(payload["stats"],ensure_ascii=False))
if __name__=="__main__": main()
