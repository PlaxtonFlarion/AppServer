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
      background:var(--bg); color:var(--fg); transition:.25s;
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

    .logo {{
      display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;
      margin-bottom:25px;
    }}
    .logo img {{height:28px;border-radius:6px;}}

    input#search {{
      width:100%;padding:8px;border-radius:6px;margin-bottom:18px;
      background:var(--bg);color:var(--fg);border:1px solid var(--border);
    }}

    .section-title {{
      opacity:.65;font-size:12px;margin-top:18px;margin-bottom:6px;font-weight:700;
    }}
    .api-item {{
      cursor:pointer;padding:7px;border-radius:6px;font-size:14px;
      display:flex;gap:8px;align-items:center;
    }}
    .api-item:hover {{ background:rgba(255,255,255,.07); }}
    .method {{
      font-weight:700;color:#00e0ff;text-transform:uppercase;font-size:12px;
    }}

    .top-right {{
      position:fixed;right:20px;top:18px;
    }}
    .btn-theme {{
      padding:6px 12px;border-radius:6px;cursor:pointer;
      background:var(--panel);border:1px solid var(--border);
    }}

    .swagger-ui .topbar {{display:none!important;}}

    pre {{
      background:var(--code);color:#c7c7c7;padding:14px;border-radius:8px;
      overflow-x:auto;margin-bottom:20px;font-size:13px;
    }}
    .block {{margin-bottom:28px;border-bottom:1px solid var(--border);padding-bottom:22px;}}

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
      <p style="opacity:.7;margin-top:-8px;">OpenAPI Reference</p>
      <div id="api"></div>
    </div>

    <div class="top-right"><div id="theme" class="btn-theme">🌙 Dark</div></div>

    <script>
    const URL_OPENAPI = "{openapi_url}";
    const root = document.getElementById("root");

    // ============ 主题切换 ============
    let mode = localStorage.getItem("theme") || "dark";
    applyTheme();

    document.getElementById("theme").onclick = () => {{
      mode = (mode === "dark" ? "light" : "dark");
      localStorage.setItem("theme", mode);
      applyTheme();
    }}

    function applyTheme() {{
      root.classList.toggle("light", mode === "light");
      document.getElementById("theme").innerText = (mode === "dark" ? "🌙 Dark" : "🌞 Light");
    }}

    // ============ 加载 OpenAPI ============
    fetch(URL_OPENAPI)
      .then(r => r.json())
      .then(renderAPI)
      .catch(() => document.getElementById("api").innerHTML = "<b style='color:red'>❌ openapi.json 加载失败</b>");

    function renderAPI(spec) {{
      const paths = spec.paths;
      const menu = document.getElementById("menu");
      const api = document.getElementById("api");

      let groups = {{}};

      Object.entries(paths).forEach(([path, methods]) => {{
        Object.entries(methods).forEach(([method, meta]) => {{
          let tag = meta.tags ? meta.tags[0] : "Others";
          (groups[tag] = groups[tag] || []).push({{ path, method, meta }});
        }});
      }});

      // ===== 左侧导航 =====
      let menuHTML = "";
      for (const tag in groups) {{
        menuHTML += `<div class='section-title'>${{tag}}</div>`;
        groups[tag].forEach(ep => {{
          menuHTML += `<div class='api-item' onclick="jump('${{ep.path}}')">
            <span class='method'>${{ep.method}}</span> ${{ep.path}}
          </div>`;
        }});
      }}
      menu.innerHTML = menuHTML;

      // ===== 文档主体 =====
      let apiHTML = "";
      for (const tag in groups) {{
        apiHTML += `<h2 style='margin-top:40px;'>${{tag}}</h2>`;
        groups[tag].forEach(ep => {{
          apiHTML += `<div class='block'>
            <h3>${{ep.method.toUpperCase()}} ${{ep.path}}</h3>
            <p>${{ep.meta.summary || ""}}</p>

            <pre>curl -X ${{ep.method.toUpperCase()}} \\
    https://api.appserverx.com${{ep.path}} \\
    -H "Authorization: Bearer <TOKEN>" \\
    -d '{{"sample":"value"}}'</pre>

          </div>`;
        }});
      }}
      api.innerHTML = apiHTML;
    }}

    // ===== 滚动定位 =====
    function jump(path) {{
      const blocks = document.querySelectorAll(".block");
      for (const b of blocks) {{
        if (b.innerText.includes(path)) {{
          b.scrollIntoView({{ behavior: "smooth" }});
          return;
        }}
      }}
    }}

    // ===== 搜索 =====
    const search = document.getElementById("search");
    search.oninput = () => {{
      const key = search.value.toLowerCase();
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
