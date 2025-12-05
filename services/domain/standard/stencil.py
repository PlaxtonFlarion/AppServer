#   ____  _                  _ _
#  / ___|| |_ ___ _ __   ___(_) |
#  \___ \| __/ _ \ '_ \ / __| | |
#   ___) | ||  __/ | | | (__| | |
#  |____/ \__\___|_| |_|\___|_|_|
#

import json
from fastapi import HTTPException
from utils import (
    const, toolset
)


async def stencil_viewer(a: str, t: int, n: str, page: str) -> str:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    try:
        html_template = toolset.resolve_template("html", page)
        return html_template.read_text(encoding=const.CHARSET)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"文件名不存在: {page}")


async def stencil_case(a: str, t: int, n: str, case: str) -> str:
    app_name, app_desc, *_ = a.lower().strip(), a, t, n

    try:
        business_file = toolset.resolve_template("case", case)
        return json.loads(business_file.read_text(encoding=const.CHARSET))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"文件名不存在: {case}")

    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"文件格式错误: {case}")


if __name__ == '__main__':
    pass
