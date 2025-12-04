#  ____                _
# |  _ \ __ _ _ __ ___(_)_ __   __ _
# | |_) / _` | '__/ __| | '_ \ / _` |
# |  __/ (_| | |  \__ \ | | | | (_| |
# |_|   \__,_|_|  |___/_|_| |_|\__, |
#                              |___/
#

import xml.etree.ElementTree as eT
from schemas.heal import ElementNode


# ---------------- Xml dump 解析 ---------------- #
def parse_xml_dump(dump: str) -> list["ElementNode"]:

    def parse_bounds(string: str) -> list[int]:
        """
        把 Android bounds 字符串转为 [x1, y1, x2, y2]
        e.g. "[0,72][1080,552]" -> [0, 72, 1080, 552]
        """
        try:
            part = string.strip().replace(
                "][", ","
            ).replace("[", "").replace("]", "")
            nums = [
                int(x) for x in part.split(",") if x.strip().isdigit() or x.strip().lstrip("-").isdigit()
            ]
            if len(nums) == 4: return nums
        except Exception as e:
            _ = e; pass

        return []

    nodes: list["ElementNode"] = []

    try:
        root = eT.fromstring(dump)
    except eT.ParseError:
        return nodes

    for ele in root.iter():
        class_name = ele.attrib.get("class") or ele.tag
        if not class_name: continue

        text = ele.attrib.get("text") or None
        content_desc = ele.attrib.get("content-desc") or ele.attrib.get("contentDescription") or None
        resource_id = ele.attrib.get("resource-id") or ele.attrib.get("resourceId") or None
        bounds_str = ele.attrib.get("bounds") or ""
        bounds = parse_bounds(bounds_str) if bounds_str else []

        if not any([text, content_desc, resource_id]):
            # 如果想连容器节点也分析，可以删掉这段 continue
            continue

        node = ElementNode(
            id=None,
            text=text,
            content_desc=content_desc,
            resource_id=resource_id,
            class_name=class_name,
            bounds=bounds
        )
        nodes.append(node)

    return nodes


# ---------------- Dom dump 解析 ---------------- #


if __name__ == '__main__':
    pass
