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
async def swagger_docs() -> "HTMLResponse":
    title = "AppServerX API Console"

    loud_theme = "https://unpkg.com/swagger-ui-themes/themes/3.x/theme-material.css"
    dark_theme = "https://unpkg.com/swagger-ui-themes/themes/3.x/theme-monokai.css"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"/>
        <title>{title}</title>

        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>

        <link id="swagger-theme" rel="stylesheet" href="{dark_theme}"/>

        <style>
            body {{ margin:0; font-family: 'Inter', ui-sans-serif; }}

            .topbar {{
                background:#111!important;
                padding:8px 16px;
                display:flex;justify-content:space-between;align-items:center;
            }}

            .brand {{ color:#eee; font-size:18px;font-weight:600; }}

            #theme-btn {{
                background:#222; color:#eee; padding:4px 10px; border-radius:6px;
                cursor:pointer; border:1px solid #444; font-size:13px; transition:.25s;
            }}

            #theme-btn:hover {{ background:#555; }}
        </style>
    </head>

    <body>

    <div class="topbar">
        <div class="brand">{title}</div>
        <div id="theme-btn">🌙 Dark</div>
    </div>

    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>

    <script>
        const themeBtn = document.getElementById("theme-btn");
        const theme = document.getElementById("swagger-theme");

        const DARK = "{dark_theme}";
        const LOUD = "{loud_theme}";

        function setTheme(mode) {{
            if(mode === "loud") {{
                theme.href = LOUD;
                themeBtn.textContent = "🌞 Loud";
                themeBtn.style.background = "#f0f0f0";
                themeBtn.style.color = "#333";
            }} else {{
                theme.href = DARK;
                themeBtn.textContent = "🌙 Dark";
                themeBtn.style.background = "#222";
                themeBtn.style.color = "#eee";
            }}
            localStorage.setItem("swagger-theme", mode);
        }}

        let saved = localStorage.getItem("swagger-theme") || "dark";
        setTheme(saved);

        themeBtn.onclick = ()=>{{
            saved = (saved === "dark" ? "loud" : "dark");
            setTheme(saved);
        }}

        // Swagger Init
        SwaggerUIBundle({{
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            deepLinking: true,
            displayRequestDuration:true,
            tryItOutEnabled:true,
            persistAuthorization:true,
            docExpansion:"none"
        }});
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


@docs_router.get(path="/custom-docs", include_in_schema=False)
async def custom_docs() -> "HTMLResponse":

    openapi_url = "/openapi.json"
    logo = "https://fastapi.tiangolo.com/img/icon-white.svg"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title>AppServerX Developer Console</title>

    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>
    <link id="theme-css" rel="stylesheet" href="https://unpkg.com/swagger-ui-themes/themes/3.x/theme-material.css">

    <style>

    body {{
      margin:0;
      display:flex;
      font-family: Inter, sans-serif;
      background: var(--bg);
      color: var(--fg);
      transition:.25s ease;
    }}

    :root {{
      --bg:#0e0e0f;
      --fg:#fff;
      --panel:#161616;
      --border:#333;
    }}

    .loud {{
      --bg:#fafafa;
      --fg:#000;
      --panel:#ffffff;
      --border:#ddd;
    }}

    .sidebar {{
      width:250px;
      background:var(--panel);
      border-right:1px solid var(--border);
      height:100vh;
      padding:20px;
      overflow-y:auto;
      position:fixed;
    }}

    .logo {{
      display:flex;
      align-items:center;
      font-size:20px;
      gap:8px;
      font-weight:700;
      margin-bottom:24px;
    }}

    .logo img {{ width:28px; border-radius:6px; }}

    .section-title {{
      opacity:.7;
      font-size:12px;
      margin-top:24px;
      margin-bottom:6px;
      font-weight:600;
    }}

    .api-item {{
      cursor:pointer;
      padding:6px 4px;
      border-radius:6px;
      font-size:14px;
      margin-bottom:4px;
    }}

    .api-item:hover {{
      background:rgba(255,255,255,0.06);
    }}

    .content {{
      margin-left:250px;
      width:calc(100vw - 250px);
      padding:20px 40px;
    }}

    .top-right {{
      position:fixed; right:20px; top:20px;
      display:flex; gap:12px;
    }}

    .btn {{
      padding:6px 12px;
      border-radius:6px;
      cursor:pointer;
      font-size:13px;
      background:var(--panel);
      border:1px solid var(--border);
    }}

    .swagger-ui .opblock-summary-method {{
      border-radius:6px;
    }}

    .swagger-ui .topbar {{ display:none !important; }}

    </style>

    </head>
    <body id="root" class="dark">

    <div class="sidebar">
      <div class="logo">
        <img src="{logo}"/> AppServerX
      </div>

      <div class="section-title">API Endpoints</div>
      <div id="menu"></div>
    </div>

    <div class="top-right">
      <div id="theme-toggle" class="btn">🌙 Dark</div>
    </div>

    <div class="content">
      <div id="swagger-ui"></div>
    </div>

    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>

    <script>

    const ui = SwaggerUIBundle({{
        url: "{openapi_url}",
        dom_id: '#swagger-ui',
        deepLinking: true,
        layout: "BaseLayout",
        persistAuthorization:true,
        tryItOutEnabled:true,
    }});

    // build sidebar menu tree from schema
    ui.getSystem().events.on('loaded', () => {{
        const paths = ui.getSystem().specSelectors.paths();

        let menuHTML="";
        Object.keys(paths.toJS()).forEach(p => {{
            menuHTML += `<div class='api-item' onclick="scrollToEndpoint('${{p}}')">${{p}}</div>`;
        }});
        document.querySelector("#menu").innerHTML = menuHTML;
    }});

    function scrollToEndpoint(path) {{
        const el = document.querySelector(`div.opblock-summary[data-path="${{path}}"]`);
        if(el) el.scrollIntoView({{ behavior:'smooth', block:'start' }});
    }}

    // theme switch
    const root = document.getElementById("root")
    const toggle = document.getElementById("theme-toggle")
    let mode = localStorage.getItem("mode") || "dark";

    function applyTheme() {{
        if(mode==="loud") {{
            root.classList.add("loud");
            toggle.textContent="🌞 Loud";
        }} else {{
            root.classList.remove("loud");
            toggle.textContent="🌙 Dark";
        }}
        localStorage.setItem("mode",mode);
    }}

    applyTheme();

    toggle.onclick=()=>{{
        mode = (mode==="dark"?"loud":"dark");
        applyTheme();
    }}

    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
