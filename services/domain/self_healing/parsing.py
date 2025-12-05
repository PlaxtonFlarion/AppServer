#  ____                _
# |  _ \ __ _ _ __ ___(_)_ __   __ _
# | |_) / _` | '__/ __| | '_ \ / _` |
# |  __/ (_| | |  \__ \ | | | | (_| |
# |_|   \__,_|_|  |___/_|_| |_|\__, |
#                              |___/
#

import re
from lxml import (
    etree, html
)
from schemas.cognitive import ElementNode


class AndroidXmlParser(object):
    """
    解析 Android UIAutomator XML Dump:
    <hierarchy>
      <node text="" resource-id="" class="" bounds="[x1,y1][x2,y2]" ... />
      ...
    </hierarchy>
    """

    @staticmethod
    def parse_bounds(bounds_str: str) -> list[int]:
        """Android bounds: "[50,1200][1030,1320]" → [50,1200,1030,1320]"""

        if not bounds_str: return []
        nums = re.findall(r"\d+", bounds_str)
        return [int(n) for n in nums] if nums else []

    @staticmethod
    def parse(xml_str: str) -> list["ElementNode"]:
        """整个页面的 XML 字符串"""

        root = etree.fromstring(xml_str.encode("utf-8"))
        tree = root.getroottree()

        nodes: list["ElementNode"] = []

        for el in root.iter("node"):
            bounds = AndroidXmlParser.parse_bounds(el.get("bounds") or "")

            node = ElementNode(
                id=el.get("resource-id") or None,
                text=el.get("text") or None,
                content_desc=el.get("content-desc") or None,
                resource_id=el.get("resource-id") or None,
                bounds=bounds,
                class_name=el.get("class") or "",
                xpath=tree.getpath(el),
            )
            node.ensure_desc()
            nodes.append(node)

        return nodes


class WebDomParser(object):
    """
    解析 Web HTML DOM：
    - 只抽取“可能可交互”的节点：a / button / input / 有 onclick / role="button" 的元素
    """

    @staticmethod
    def parse(dom_str: str) -> list["ElementNode"]:
        """页面 HTML 字符串"""

        root = html.fromstring(dom_str)
        tree = root.getroottree()

        # 选取：a / button / input / 有 onclick / role="button" 的元素
        elements = root.xpath(
            "//*[self::a or self::button or self::input or @onclick or @role='button']"
        )

        nodes: list["ElementNode"] = []

        for el in elements:
            text        = (el.text_content() or "").strip()
            resource_id = el.get("id") or None
            cls         = el.get("class") or ""
            class_name  = el.tag + (f".{cls}" if cls else "")

            node = ElementNode(
                id=resource_id,
                text=text or None,
                content_desc=el.get("title") or el.get("aria-label") or None,
                resource_id=resource_id,
                bounds=[],  # Web 暂时没有 bounds 信息
                class_name=class_name,
                xpath=tree.getpath(el),
            )
            node.ensure_desc()
            nodes.append(node)

        return nodes


if __name__ == '__main__':
    pass
