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
    }}
    .light {{
      --bg:#fafafa; --fg:#000; --panel:#fff; --border:#ddd; --code:#f6f8fa;
    }}
    body {{
      margin:0; display:flex; font-family:Inter,system-ui,sans-serif;
      background:var(--bg); color:var(--fg);
    }}
    .sidebar {{
      width:260px; background:var(--panel); height:100vh;
      border-right:1px solid var(--border);
      padding:22px; overflow-y:auto; position:fixed;
    }}
    .content {{
      margin-left:260px; width:calc(100vw - 260px);
      padding:40px 50px;
    }}
    .logo img {{height:26px;border-radius:6px;}}
    .logo {{
      display:flex;align-items:center;gap:10px;font-weight:700;font-size:19px;
      margin-bottom:25px;
    }}
    input#search {{
      width:100%;padding:8px;border-radius:6px;margin-bottom:18px;
      background:var(--bg);color:var(--fg);border:1px solid var(--border);
    }}
    .section-title {{
      opacity:.65;font-size:12px;margin-top:18px;margin-bottom:6px;font-weight:700;
    }}
    .api-item {{
      cursor:pointer;padding:7px;border-radius:6px;font-size:14px;
    }}
    .api-item:hover {{ background:rgba(255,255,255,.07); }}
    .method {{
      font-weight:700;color:#00e0ff;text-transform:uppercase;font-size:11px;
    }}

    details {{
      background:var(--panel);border:1px solid var(--border);
      padding:14px 18px;border-radius:6px;margin-bottom:14px;
    }}
    details summary {{
      cursor:pointer;font-weight:600;font-size:15px;margin-bottom:6px;
    }}
    details summary:hover {{opacity:.85}}

    pre {{
      background:var(--code);padding:12px;border-radius:6px;font-size:13px;
      overflow:auto;color:#c7c7c7;
    }}

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
      <p style="opacity:.7;margin-top:-8px;">API Reference</p>
      <div id="api"></div>
    </div>

    <div id="theme" class="btn-theme">🌙 Dark</div>

    <script>
    const URL_OPENAPI = "{openapi_url}";
    let mode = localStorage.getItem("theme") || "dark";
    applyTheme();

    document.getElementById("theme").onclick = () => {{
      mode = mode === "dark" ? "light" : "dark";
      localStorage.setItem("theme", mode);
      applyTheme();
    }}
    function applyTheme() {{
      document.body.classList.toggle("light", mode === "light");
      document.getElementById("theme").innerText = mode === "light" ? "🌞 Light" : "🌙 Dark";
    }}

    fetch(URL_OPENAPI).then(r => r.json()).then(renderAPI);

    function renderAPI(spec) {{
      const paths = spec.paths;
      let groups = {{}};

      Object.entries(paths).forEach(([path, methods]) => {{
        Object.entries(methods).forEach(([method, meta]) => {{
          const tag = meta.tags ? meta.tags[0] : "Others";
          (groups[tag] = groups[tag] || []).push({{ path, method, meta }});
        }});
      }});

      // 左侧导航
      let menuHTML = "";
      for (const tag in groups) {{
        menuHTML += `<div class='section-title'>${{tag}}</div>`;
        groups[tag].forEach(ep => {{
          menuHTML += `<div class='api-item' onclick="jump('${{ep.path}}')">
            <span class='method'>${{ep.method}}</span> ${{ep.path}}
          </div>`;
        }});
      }}
      document.getElementById("menu").innerHTML = menuHTML;

      // 主文档（折叠）
      let html = "";
      for (const tag in groups) {{
        html += `<h2 style='margin-top:40px;'>${{tag}}</h2>`;
        groups[tag].forEach(ep => {{
          html += `
          <details>
            <summary>${{ep.method.toUpperCase()}} <b>${{ep.path}}</b></summary>
            <p style="opacity:.75;margin:8px 0 12px;">${{ep.meta.summary || ""}}</p>

            ${{
              ep.meta.parameters
                ? `<b>📥 Params</b><pre>${{ep.meta.parameters.map(p => `${{p.name}}: ${{p.schema?.type || "any"}}`).join("\\n")}}</pre>`
                : ""
            }}

            ${{
              ep.meta.responses
                ? `<b>📤 Responses</b><pre>${{
                    Object.entries(ep.meta.responses).map(([code,val]) => `${{code}} → ${{val.description}}`).join("\\n")
                 }}</pre>`
                : ""
            }}
          </details>`;
        }});
      }}
      document.getElementById("api").innerHTML = html;
    }}

    function jump(path) {{
      document.querySelectorAll("details").forEach(el => {{
        if(el.innerText.includes(path)) {{
          el.open = true;
          el.scrollIntoView({{behavior:"smooth",block:"start"}});
        }}
      }});
    }}

    document.getElementById("search").oninput = function() {{
      const key = this.value.toLowerCase();
      document.querySelectorAll(".api-item").forEach(i => {{
        i.style.display = i.innerText.toLowerCase().includes(key) ? "" : "none";
      }});
    }}
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
