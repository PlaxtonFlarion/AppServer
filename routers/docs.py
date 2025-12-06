#  ____
# |  _ \  ___   ___ ___
# | | | |/ _ \ / __/ __|
# | |_| | (_) | (__\__ \
# |____/ \___/ \___|___/
#

from fastapi import APIRouter
from fastapi.responses import (
    FileResponse, HTMLResponse
)

docs_router = APIRouter(tags=["Docs"])


@docs_router.get(path="/openapi.json", include_in_schema=False)
async def openapi_file() -> "FileResponse":
    return FileResponse(path="openapi.json", media_type="application/json")


@docs_router.get(path="/docs", include_in_schema=False)
async def docs() -> "HTMLResponse":
    openapi_url = "/openapi.json"
    title       = "AppServerX API"
    logo        = "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>

    <style>
    /* ————— CSS 和主题不变，省略头部同上 ————— */
    :root {{
      --bg:#0e0e0f; --fg:#f1f1f1; --panel:#171717; --border:#333; --code:#0e1117;
      --ok:#28d07a; --err:#ff5566;
    }}
    .light {{
      --bg:#fafafa; --fg:#000; --panel:#fff; --border:#ddd; --code:#f6f8fa;
    }}
    /* 样式同你已有版，这里省略，只添加以下新增样式 */

    .trybox {{
      background:var(--panel);border:1px solid var(--border);
      padding:14px;border-radius:8px;margin-top:16px;
    }}
    .trybox input,textarea {{
      width:100%;margin-top:8px;padding:8px;border-radius:6px;
      border:1px solid var(--border);background:var(--bg);color:var(--fg);
    }}
    .trybtn {{
      background:#00e0ff;color:#000;padding:6px 12px;border-radius:6px;
      cursor:pointer;margin-top:10px;display:inline-block;
    }}
    .resultBox {{
      background:var(--code);padding:12px;margin-top:10px;border-radius:6px;
      color:#c7c7c7;white-space:pre-wrap;overflow:auto;
    }}
    .badge{{font-size:11px;padding:1px 4px;border-radius:3px}}
    </style>
    </head>

    <body id="root">

    <div class="sidebar">
      <div class="logo"><img src="{logo}"/> {title}</div>
      <input id="search" placeholder="Search API..."/>
      <div id="menu"></div>
    </div>

    <div class="content">
      <h1>{title}</h1>
      <p style="opacity:.7;margin-top:-8px;">API Reference with Schema & Try</p>
      <div id="api"></div>
    </div>

    <div id="theme" class="btn-theme">🌙 Dark</div>

    <script>
    const URL_OPENAPI = "{openapi_url}";

    let spec = null;
    fetch(URL_OPENAPI).then(r=>r.json()).then(s=>{{spec=s; renderAPI();}});

    function renderAPI(){{
      const paths = spec.paths;
      let groups = {{}};

      Object.entries(paths).forEach(([path,methodMap]) => {{
        Object.entries(methodMap).forEach(([method,meta]) => {{
          const tag = meta.tags?meta.tags[0]:"Others";
          (groups[tag]=groups[tag]||[]).push({{path,method,meta}});
        }});
      }});

      // 左侧菜单
      let menu="";
      for(const tag in groups){{
        menu+=`<div class="section-title">${{tag}}</div>`;
        groups[tag].forEach(ep=>{{
          menu+=`<div class="api-item" onclick="scrollToAPI('${{ep.path}}')">
            <span class="method">${{ep.method}}</span> ${{ep.path}}
          </div>`;
        }});
      }}
      document.querySelector("#menu").innerHTML=menu;

      // 主文档
      let html="";
      for(const tag in groups){{
        html+=`<h2 style="margin:35px 0 15px">${{tag}}</h2>`;
        groups[tag].forEach(ep=>{{
          const req = ep.meta.requestBody?.content?.["application/json"]?.schema;
          const res = ep.meta.responses?.["200"]?.content?.["application/json"]?.schema;

          html+=`
          <details>
            <summary>${{ep.method.toUpperCase()}} <b>${{ep.path}}</b></summary>
            <p style="opacity:.7;margin:6px 0 12px">${{ep.meta.summary || "No description"}}</p>

            ${{
              req?`<b>📥 Request Body Schema</b><pre>${{formatSchema(req)}}</pre>`:""
            }}
            ${{
              res?`<b>📤 Response Schema</b><pre>${{formatSchema(res)}}</pre>`:""
            }}

            ${{
              req?`<b>📝 Request Example</b><pre>${{genExample(req)}}</pre>`:""
            }}
            ${{
              res?`<b>📦 Response Example</b><pre>${{genExample(res)}}</pre>`:""
            }}

            <div class="trybox">
              <b>⚡ Try It</b>
              <textarea id="body-${{hash(ep)}}" placeholder="JSON Body (optional)"></textarea>
              <input id="token-${{hash(ep)}}" placeholder="Authorization Bearer (optional)"/>
              <div class="trybtn" onclick="send('${{ep.method}}','${{ep.path}}','${{hash(ep)}}')">Send Request →</div>
              <pre class="resultBox" id="result-${{hash(ep)}}">waiting...</pre>
            </div>
          </details>
          `;
        }});
      }}
      document.querySelector("#api").innerHTML=html;
    }}

    // ============ UTILS ============

    // JSON example builder
    function genExample(schema){{
      if(schema.example) return JSON.stringify(schema.example,null,2);
      let obj={{}};
      if(schema.properties){{
        for(const k in schema.properties){{
          obj[k]=schema.properties[k].type||"string";
        }}
      }}
      return JSON.stringify(obj,null,2);
    }}

    // Schema text builder
    function formatSchema(s){{
      return JSON.stringify(s,null,2);
    }}

    function hash(ep){{
      return btoa(ep.path+ep.method).replace(/=/g,"");
    }}

    // Try request
    async function send(m,path,id){{
      let body=document.getElementById("body-"+id).value.trim();
      let token=document.getElementById("token-"+id).value;
      let opts={{method:m.toUpperCase(),headers:{{"Content-Type":"application/json"}}}};
      if(token) opts.headers["Authorization"]="Bearer "+token;
      if(body) opts.body=body;

      try{{
        let r=await fetch(path,opts);
        let text=await r.text();
        document.getElementById("result-"+id).innerText=`Status: ${{r.status}}
    ${{text}}`;
      }}catch(e){{
        document.getElementById("result-"+id).innerText="❌ Error: "+e;
      }}
    }}

    function scrollToAPI(path){{
      document.querySelectorAll("details").forEach(el=>{{
        if(el.innerText.includes(path)){{
          el.open=true;
          el.scrollIntoView({{behavior:"smooth"}})
        }}
      }});
    }}

    // theme toggle 省略，已包含…
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
