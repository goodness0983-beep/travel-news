import feedparser, re, time
from datetime import datetime, timezone
from pathlib import Path

SOURCES = [
    {"cat":"swiss",  "url":"https://news.google.com/rss/search?q=瑞士+旅遊&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"},
    {"cat":"swiss",  "url":"https://news.google.com/rss/search?q=Switzerland+travel+2026&hl=en-US&gl=US&ceid=US:en"},
    {"cat":"italy",  "url":"https://news.google.com/rss/search?q=義大利+旅遊&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"},
    {"cat":"italy",  "url":"https://news.google.com/rss/search?q=Italy+travel+news+2026&hl=en-US&gl=US&ceid=US:en"},
    {"cat":"europe", "url":"https://news.google.com/rss/search?q=歐洲+旅遊+新知&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"},
    {"cat":"europe", "url":"https://news.google.com/rss/search?q=Europe+travel+news+2026&hl=en-US&gl=US&ceid=US:en"},
    {"cat":"europe", "url":"https://www.euronews.com/rss?level=theme&name=travel"},
    {"cat":"flight", "url":"https://news.google.com/rss/search?q=台灣+歐洲+機票&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"},
    {"cat":"flight", "url":"https://news.google.com/rss/search?q=歐洲+航班+促銷&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"},
    {"cat":"flight", "url":"https://news.google.com/rss/search?q=Europe+flight+deals+Asia&hl=en-US&gl=US&ceid=US:en"},
]

CATS = {
    "swiss":  {"label":"瑞士",   "color":"#1B3B6F", "bg":"#EBF0FA"},
    "italy":  {"label":"義大利", "color":"#8C1A1A", "bg":"#FAF0F0"},
    "europe": {"label":"歐洲",   "color":"#2A5C45", "bg":"#EAF2EE"},
    "flight": {"label":"機票",   "color":"#7A4D00", "bg":"#FDF5E6"},
}

def clean(t):
    t = re.sub(r"<[^>]+>","",t or "")
    return re.sub(r"\s+"," ",t).strip()

def trunc(t, n=200):
    t = clean(t)
    return t[:n].rsplit(" ",1)[0]+"…" if len(t)>n else t

def fmt_date(e):
    for a in ("published_parsed","updated_parsed"):
        v = getattr(e,a,None)
        if v:
            try: return datetime(*v[:6]).strftime("%Y/%m/%d")
            except: pass
    return ""

def fetch():
    by_cat = {k:[] for k in CATS}
    seen   = {k:set() for k in CATS}
    for s in SOURCES:
        try:
            feed = feedparser.parse(s["url"])
            for e in feed.entries[:6]:
                t = clean(e.get("title",""))
                if not t: continue
                key = re.sub(r"\s+","",t.lower())[:25]
                if key in seen[s["cat"]]: continue
                seen[s["cat"]].add(key)
                by_cat[s["cat"]].append({
                    "title":   t,
                    "summary": trunc(e.get("summary",e.get("description",""))),
                    "url":     e.get("link",""),
                    "source":  e.get("source",{}).get("title",""),
                    "date":    fmt_date(e),
                })
            time.sleep(1)
        except Exception as ex:
            print(f"  skip: {ex}")
    for k in by_cat:
        by_cat[k] = by_cat[k][:8]
    return by_cat

def card(a, cat):
    m = CATS[cat]
    date_h = f'<span class="c-date">{a["date"]}</span>' if a["date"] else ""
    link_h = f'<a class="c-link" href="{a["url"]}" target="_blank" rel="noopener">閱讀全文 →</a>' if a["url"] else ""
    src_h  = f'<span class="c-src">{a["source"]}</span>' if a["source"] else ""
    return f"""<article class="card" data-cat="{cat}">
  <div class="c-top"><span class="badge" style="background:{m['bg']};color:{m['color']}">{m['label']}</span>{date_h}</div>
  <h2 class="c-title">{a['title']}</h2>
  <p class="c-body">{a['summary']}</p>
  <div class="c-foot">{src_h}{link_h}</div>
</article>"""

def build(by_cat):
    now   = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    total = sum(len(v) for v in by_cat.values())
    cards = "\n".join(card(a,cat) for cat,arts in by_cat.items() for a in arts)
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>歐洲旅遊情報</title>
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#F8F5F0;--sur:#FFF;--ink:#1A1714;--ink2:#5C554D;--ink3:#A09488;--rule:rgba(26,23,20,.08);--acc:#2A5C45}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--ink);min-height:100vh}}
header{{background:var(--ink);color:#F8F5F0;padding:28px 36px;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:12px}}
header h1{{font-family:'Lora',serif;font-size:26px;font-weight:600;color:#F8F5F0}}
header p{{font-size:11px;letter-spacing:1.8px;text-transform:uppercase;color:#6B635A;margin-top:6px}}
.meta{{font-size:11px;color:#4A4540;text-align:right;line-height:1.7}}
nav{{background:var(--sur);border-bottom:1px solid var(--rule);padding:0 36px;display:flex;overflow-x:auto}}
.nb{{font-family:'DM Sans',sans-serif;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;font-weight:500;padding:13px 16px;border:none;background:none;cursor:pointer;color:var(--ink3);border-bottom:2px solid transparent;margin-bottom:-1px;transition:all .15s;white-space:nowrap}}
.nb:hover{{color:var(--ink)}}.nb.on{{color:var(--acc);border-bottom-color:var(--acc)}}
.wrap{{max-width:1140px;margin:0 auto;padding:32px 36px 60px}}
.lbl{{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--ink3);margin-bottom:18px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:2px;overflow:hidden}}
.card{{background:var(--sur);padding:20px 22px;display:flex;flex-direction:column;gap:11px;transition:background .15s}}
.card:hover{{background:#FDFAF6}}.card.hidden{{display:none}}
.c-top{{display:flex;align-items:center;justify-content:space-between;gap:8px}}
.badge{{font-size:10px;font-weight:500;letter-spacing:.8px;text-transform:uppercase;padding:3px 9px;border-radius:2px}}
.c-date{{font-size:11px;color:var(--ink3)}}
.c-title{{font-family:'Lora',serif;font-size:15.5px;line-height:1.5;color:var(--ink)}}
.c-body{{font-size:13px;color:var(--ink2);line-height:1.7;flex:1}}
.c-foot{{border-top:1px solid var(--rule);padding-top:10px;display:flex;align-items:center;justify-content:space-between;gap:8px}}
.c-src{{font-size:11px;color:var(--ink3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:60%}}
.c-link{{font-size:11px;font-weight:500;color:var(--acc);text-decoration:none;white-space:nowrap}}
.c-link:hover{{text-decoration:underline}}
.empty{{grid-column:1/-1;padding:60px;text-align:center;font-family:'Lora',serif;font-style:italic;color:var(--ink3);font-size:16px}}
@media(max-width:600px){{header,nav,.wrap{{padding-left:18px;padding-right:18px}}.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<header>
  <div><h1>歐洲旅遊情報</h1><p>Switzerland · Italy · Europe · Flights</p></div>
  <div class="meta">更新時間<br>{now}<br>共 {total} 則</div>
</header>
<nav>
  <button class="nb on" data-f="all">全部（{total}）</button>
  <button class="nb" data-f="swiss">🇨🇭 瑞士</button>
  <button class="nb" data-f="italy">🇮🇹 義大利</button>
  <button class="nb" data-f="europe">🌍 歐洲</button>
  <button class="nb" data-f="flight">✈ 機票</button>
</nav>
<div class="wrap">
  <p class="lbl" id="lbl">共 {total} 則最新資訊</p>
  <div class="grid" id="grid">
    {cards}
    <div class="empty hidden" id="empty">此分類目前沒有資料</div>
  </div>
</div>
<script>
const btns=document.querySelectorAll('.nb'),cards=document.querySelectorAll('.card'),lbl=document.getElementById('lbl'),empty=document.getElementById('empty');
btns.forEach(b=>b.addEventListener('click',()=>{{
  btns.forEach(x=>x.classList.remove('on'));b.classList.add('on');
  const f=b.dataset.f;let n=0;
  cards.forEach(c=>{{const s=f==='all'||c.dataset.cat===f;c.classList.toggle('hidden',!s);if(s)n++;}});
  lbl.textContent='共 '+n+' 則最新資訊';
  empty.classList.toggle('hidden',n>0);
}}));
</script></body></html>"""

if __name__ == "__main__":
    print("抓取新聞中...")
    data = fetch()
    for k,v in data.items(): print(f"  {k}: {len(v)} 則")
    html = build(data)
    Path("index.html").write_text(html, encoding="utf-8")
    print("完成 → index.html")
