from loguru import logger
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from services.infrastructure.storage import r2_storage

docs_router = APIRouter(tags=["Docs"])


@docs_router.get(path="/docs", include_in_schema=False)
async def swagger_docs() -> "HTMLResponse":
    title = "AppServerX API Console"
    logo  = "https://your-cdn/logo.png"

    light_theme = "https://unpkg.com/swagger-ui-themes/themes/3.x/theme-material.css"
    dark_theme  = "https://unpkg.com/swagger-ui-themes/themes/3.x/theme-monokai.css"

    r2_swagger_key = "docs/swagger/latest.json"
    doc_url        = f"{r2_storage.r2_bucket_url}/{r2_swagger_key}"

    logger.info(f"{title} - {doc_url}")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"/>
        <title>{title}</title>
        <link id="swagger-theme" rel="stylesheet" href="{dark_theme}"/>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css"/>

        <style>
            body {{ margin:0; font-family: 'Inter', ui-sans-serif; }}

            /* 顶栏样式 */
            .topbar {{ background:#111!important; padding:8px 16px; display:flex;justify-content:space-between;align-items:center; }}
            .brand {{ display:flex;align-items:center;gap:8px;color:#eee;font-size:18px;font-weight:600; }}
            .brand img {{ height:26px;border-radius:4px; }}

            /* 主题切换按钮 */
            #theme-btn {{
                background:#222;
                color:#eee;
                padding:4px 10px;
                border-radius:6px;
                cursor:pointer;
                border:1px solid #444;
                font-size:13px;
                transition:.25s;
            }}
            #theme-btn:hover {{
                background:#555;
            }}
        </style>
    </head>
    <body>

    <div class="topbar">
        <div class="brand">
            <img src="{logo}">
            {title}
        </div>
        <div id="theme-btn">🌙 Dark</div>
    </div>

    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>

    <script>
    const themeBtn = document.getElementById("theme-btn");
    const theme = document.getElementById("swagger-theme");

    function setTheme(mode) {{
        if (mode === "light") {{
            theme.href = "{light_theme}";
            themeBtn.textContent = "🌞 Light";
            themeBtn.style.background = "#f0f0f0";
            themeBtn.style.color = "#333";
        }} else {{
            theme.href = "{dark_theme}";
            themeBtn.textContent = "🌙 Dark";
            themeBtn.style.background = "#222";
            themeBtn.style.color = "#eee";
        }}
        localStorage.setItem("swagger-theme", mode);
    }}

    //===== init =====
    let saved = localStorage.getItem("swagger-theme") || "dark";
    setTheme(saved);

    themeBtn.onclick = () => {{
        saved = (saved === "dark" ? "light" : "dark");
        setTheme(saved);
    }};

    //===== Swagger Init =====
    SwaggerUIBundle({{
        url: "{doc_url}",
        dom_id: '#swagger-ui',
        deepLinking: true,
        displayRequestDuration:true,
        tryItOutEnabled:true,
        persistAuthorization:true,
        docExpansion:"none"
    }});
    </script>

    </body>
    </html>"""

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
