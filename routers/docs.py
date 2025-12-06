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
    :root {{
      --bg:#0e0e0f; --fg:#f1f1f1; --panel:#171717; --border:#333; --code:#0e1117;
      --accent:#00e0ff; --sub:#9c9c9c;
    }}
    .light {{
      --bg:#fafafa; --fg:#000; --panel:#fff; --border:#ddd; --code:#f6f8fa;
    }}

    body {{
      margin:0; display:flex; font-family:Inter,system-ui,sans-serif;
      background:var(--bg); color:var(--fg); transition:.2s;
    }}

    .sidebar {{
      width:260px; background:var(--panel); height:100vh;
      border-right:1px solid var(--border); padding:22px; overflow-y:auto; position:fixed;
    }}
    .logo img {{height:26px;border-radius:6px;}}
    .logo {{display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;margin-bottom:25px;}}

    input#search {{
      width:100%;padding:8px;border-radius:6px;margin-bottom:18px;
      background:var(--bg);color:var(--fg);border:1px solid var(--border);
    }}

    .section-title {{opacity:.65;font-size:12px;margin-top:20px;margin-bottom:6px;font-weight:700;letter-spacing:.5px}}
    .api-item {{cursor:pointer;padding:7px;border-radius:6px;font-size:14px;}}
    .api-item:hover {{ background:rgba(255,255,255,.10); }}
    .method {{
      font-weight:700;color:var(--accent);text-transform:uppercase;font-size:11px;margin-right:6px;
    }}

    .content {{
      margin-left:260px;width:calc(100vw - 260px);
      padding:45px 55px;
    }}
    h1 {{
      font-size:36px;
      background:linear-gradient(to right,#00e0ff,#00ffa6);
      -webkit-background-clip:text;
      color:transparent;font-weight:900;margin-top:0;
    }}
    .sub-title {{opacity:.65;margin-top:-10px;font-size:15px;margin-bottom:30px;}}

    details {{
      background:var(--panel);border:1px solid var(--border);
      padding:18px 22px;border-radius:8px;margin-bottom:18px;
    }}
    details summary {{cursor:pointer;font-weight:700;font-size:16px;margin-bottom:8px;display:flex;align-items:center;gap:8px}}
    details summary:hover {{opacity:.85}}

    pre {{
      background:var(--code);padding:12px;border-radius:6px;font-size:13px;
      overflow:auto;color:#bfbfbf;margin-bottom:12px;
    }}

    .schema-box{{padding-left:12px;border-left:3px solid var(--accent);margin-top:10px;margin-bottom:18px;}}
    .schema-item {{margin-left:12px;font-size:13px;padding:2px 0}}
    .schema-type {{color:var(--accent);margin-left:6px}}
    .schema-required {{color:#ff4f4f;font-weight:700;margin-left:6px;font-size:11px}}
    .schema-desc{{opacity:.7;margin-left:8px}}

    .btn-theme {{
      position:fixed;right:20px;top:18px;padding:6px 12px;border-radius:6px;
      cursor:pointer;background:var(--panel);border:1px solid var(--border);
    }}
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
      <div class="sub-title">🔗 API Reference · Schemas · Examples</div>
      <div id="api"></div>
    </div>

    <div id="theme" class="btn-theme">🌙 Dark</div>

    <script>
    const URL = "{openapi_url}";
    let theme = localStorage.theme || "dark";
    applyTheme();
    document.getElementById("theme").onclick = () => {{theme=theme==="dark"?"light":"dark";localStorage.theme=theme;applyTheme();}};
    function applyTheme(){{document.body.classList.toggle("light",theme==="light");document.getElementById("theme").innerText=theme==="light"?"🌞 Light":"🌙 Dark";}}

    fetch(URL).then(r=>r.json()).then(render);

    function render(spec){{
      let groups={{}};
      Object.entries(spec.paths).forEach(([path,methods])=>{{
        Object.entries(methods).forEach(([method,meta])=>{{
          const tag=meta.tags?meta.tags[0]:"Others";
          (groups[tag]=groups[tag]||[]).push({{path,method,meta}});
        }});
      }});

      let menu="";for(const tag in groups){{menu+=`<div class='section-title'>${{tag}}</div>`;groups[tag].forEach(ep=>{{menu+=`<div class='api-item' onclick="jump('${{ep.path}}')"><span class='method'>${{ep.method}}</span>${{ep.path}}</div>`}});}}
      document.getElementById("menu").innerHTML=menu;

      let html="";
      for(const tag in groups){{
        html+=`<h2 style='margin:35px 0 15px;font-size:22px;'>${{tag}}</h2>`;
        groups[tag].forEach(ep=>{{html+=renderAPI(ep);}});
      }}
      document.getElementById("api").innerHTML=html;
    }}

    function renderAPI(ep){{
      const req=ep.meta.requestBody?.content?.["application/json"]?.schema;
      const res=ep.meta.responses?.["200"]?.content?.["application/json"]?.schema;

    return `
    <details>
      <summary><span class='method'>${{ep.method}}</span> <b>${{ep.path}}</b></summary>
      <p style="opacity:.75;margin:5px 0 15px;">📄 ${{ep.meta.summary||"No description"}}</p>

      ${{renderParams(ep.meta.parameters) | | ""}}
      ${{req?("<b>📥 Request Example</b>"+example(req)):""}}
      ${{res?("<b>📤 Response Example</b>"+example(res)):""}}

      <details style='margin-top:14px;'>
        <summary>🧬 JSON Schema Structure</summary>
        <div class='schema-box'>${{schema(req | | res)}}</div>
      </details>
    </details>`;
    }}

    function renderParams(p){{
      if(!p) return "";
      return `<b>🔧 Parameters</b>
      <pre>${{p.map(x=>`${{x.name}} (${{x. in}}) : ${{x.schema?.type}}`).join("\\n")}}</pre>`;
    }}

    function example(schema){{
      return `<pre>${{JSON.stringify(mock(schema),null,2)}}</pre>`;
    }}

    function mock(s){{
      if(s.example) return s.example;
      if(s.properties){{
        let o={{}};for(const k in s.properties)o[k]=mock(s.properties[k]);
        return o;
      }}
      switch(s.type){{
        case "integer":return 1;
        case "number":return 3.14;
        case "boolean":return true;
        case "array":return [mock(s.items||{{type:"string"}})];
        default:return "string";
      }}
    }}

    function schema(s){{
      if(!s||!s.properties) return "<i>No schema</i>";
      return Object.keys(s.properties).map(k=>{{
        const v=s.properties[k];
        const req=(s.required||[]).includes(k);
        return v.properties
          ? `<details class='schema-item'><summary><b>${{k}}</b><span class='schema-type'>${{v.type||"object"}}</span>${{req?"<span class='schema-required'>required</span>":""}}</summary><div>${{schema(v)}}</div></details>`
          : `<div class='schema-item'>• <b>${{k}}</b><span class='schema-type'>${{v.type||"object"}}</span>${{req?"<span class='schema-required'>required</span>":""}}${{v.description?`<span class='schema-desc'>${{v.description}}</span>`:""}}</div>`;
      }}).join("");
    }}

    function jump(path){{document.querySelectorAll("details").forEach(el=>{{if(el.innerText.includes(path)){{el.open=true;el.scrollIntoView({{behavior:"smooth"}})}}}});}}

    document.getElementById("search").oninput=function(){{
      const k=this.value.toLowerCase();
      document.querySelectorAll(".api-item").forEach(i=>i.style.display=i.innerText.toLowerCase().includes(k)?"":"none");
    }};
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
