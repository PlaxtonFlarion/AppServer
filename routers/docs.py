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
      background:var(--bg); color:var(--fg);
    }}
    .sidebar {{
      width:260px; background:var(--panel); height:100vh;
      border-right:1px solid var(--border);
      padding:22px; overflow-y:auto; position:fixed;
    }}
    .content {{
      margin-left:260px; width:calc(100vw - 260px);
      padding:45px 55px;
    }}
    .logo img {{height:26px;border-radius:6px;}}
    .logo {{
      display:flex;align-items:center;gap:10px;font-weight:700;font-size:20px;
      margin-bottom:25px;
    }}

    h1 {{
      font-size:36px;
      background:linear-gradient(90deg,#00e0ff,#00ffa6);
      -webkit-background-clip:text;
      color:transparent;
      margin:0 0 4px 0;
    }}
    .sub-title {{
      opacity:.65;
      margin-bottom:28px;
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
      font-weight:700;color:var(--accent);text-transform:uppercase;font-size:11px;
      padding:1px 6px;border-radius:4px;background:rgba(0,224,255,0.1);margin-right:6px;
    }}

    details {{
      background:var(--panel);border:1px solid var(--border);
      padding:16px 20px;border-radius:8px;margin-bottom:16px;
    }}
    details summary {{
      cursor:pointer;font-weight:700;font-size:15px;margin-bottom:6px;
      display:flex;align-items:center;gap:8px;
    }}
    details summary:hover {{opacity:.9}}

    pre {{
      background:var(--code);padding:12px;border-radius:6px;font-size:13px;
      overflow:auto;color:#c7c7c7;margin-top:4px;margin-bottom:10px;
    }}

    .schema-box {{
      padding-left:12px;border-left:3px solid var(--accent);
      margin-top:8px;margin-bottom:16px;
    }}
    .schema-item {{
      margin-left:12px;font-size:13px;padding:2px 0;
    }}
    .schema-type {{
      color:var(--accent);margin-left:6px;
    }}
    .schema-required {{
      color:#ff4f4f;font-size:11px;font-weight:700;margin-left:6px;
    }}
    .schema-desc {{
      opacity:.7;margin-left:6px;font-size:12px;
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
      <div class="sub-title">✨ API Reference · Parameters · Examples · JSON Schema</div>
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
    }};
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
        html += `<h2 style='margin-top:32px;'>${{tag}}</h2>`;
        groups[tag].forEach(ep => {{
          html += renderEndpoint(ep);
        }});
      }}
      document.getElementById("api").innerHTML = html;
    }}

    function renderEndpoint(ep) {{
      const req = ep.meta.requestBody?.content?.["application/json"]?.schema;
      const res = ep.meta.responses?.["200"]?.content?.["application/json"]?.schema;
      const schemaObj = req || res;

      return `
      <details>
        <summary>
          <span class='method'>${{ep.method}}</span>
          <b>${{ep.path}}</b>
        </summary>

        <p style="opacity:.75;margin:6px 0 12px;">📄 ${{ep.meta.summary || "No description"}}</p>

        ${{ renderParams(ep.meta.parameters) }}

        ${{ req ? `<b>📥 Request Example</b><pre>${{ JSON.stringify(mockFromSchema(req), null, 2) }}</pre>` : "" }}

        ${{ res ? `<b>📤 Response Example</b><pre>${{ JSON.stringify(mockFromSchema(res), null, 2) }}</pre>` : "" }}

        <details style="margin-top:10px;">
          <summary>🧬 JSON Schema</summary>
          <div class="schema-box">
            ${{ renderSchema(schemaObj) }}
          </div>
        </details>
      </details>`;
    }}

    // ✅ 修复这里：不再嵌套反引号，也没有 x. in 这种错误
    function renderParams(params) {{
      if (!params || !params.length) return "";
      const lines = params.map(p => {{
        const type = (p.schema && p.schema.type) ? p.schema.type : "any";
        const loc = p["in"] || "query";
        return `${{p.name}} (${{loc}}) → ${{type}}`;
      }});
      return `<b>🔧 Parameters</b><pre>${{ lines.join("\\n") }}</pre>`;
    }}

    // 简单的 mock 示例生成
    function mockFromSchema(s) {{
      if (!s) return {{}};
      if (s.example) return s.example;
      if (s.properties) {{
        const obj = {{}};
        for (const k in s.properties) {{
          obj[k] = mockFromSchema(s.properties[k]);
        }}
        return obj;
      }}
      switch (s.type) {{
        case "integer": return 1;
        case "number": return 1.23;
        case "boolean": return true;
        case "array": return [mockFromSchema(s.items || {{ type: "string" }})];
        default: return "string";
      }}
    }}

    // Schema 展示（简易树）
    function renderSchema(s) {{
      if (!s || !s.properties) return "<i>No schema</i>";
      const requiredList = s.required || [];
      const parts = [];

      for (const name in s.properties) {{
        const f = s.properties[name];
        const t = f.type || "object";
        const isReq = requiredList.includes(name);
        const desc = f.description || "";

        if (f.properties) {{
          parts.push(`
            <details class="schema-item">
              <summary>
                <b>${{name}}</b>
                <span class="schema-type">${{t}}</span>
                ${{ isReq ? "<span class='schema-required'>required</span>" : "" }}
                ${{ desc ? `<span class='schema-desc'>${{desc}}</span>` : "" }}
              </summary>
              <div class="schema-box">
                ${{ renderSchema(f) }}
              </div>
            </details>
          `);
        }} else {{
          parts.push(`
            <div class="schema-item">
              • <b>${{name}}</b>
              <span class="schema-type">${{t}}</span>
              ${{ isReq ? "<span class='schema-required'>required</span>" : "" }}
              ${{ desc ? `<span class='schema-desc'>${{desc}}</span>` : "" }}
            </div>
          `);
        }}
      }}
      return parts.join("");
    }}

    function jump(path) {{
      document.querySelectorAll("details").forEach(el => {{
        if (el.innerText.includes(path)) {{
          el.open = true;
          el.scrollIntoView({{ behavior:"smooth", block:"start" }});
        }}
      }});
    }}

    document.getElementById("search").oninput = function() {{
      const key = this.value.toLowerCase();
      document.querySelectorAll(".api-item").forEach(i => {{
        i.style.display = i.innerText.toLowerCase().includes(key) ? "" : "none";
      }});
    }};
    </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


if __name__ == '__main__':
    pass
