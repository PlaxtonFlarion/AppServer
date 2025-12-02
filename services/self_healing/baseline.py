#  ____                 _ _
# | __ )  __ _ ___  ___| (_)_ __   ___
# |  _ \ / _` / __|/ _ \ | | '_ \ / _ \
# | |_) | (_| \__ \  __/ | | | | |  __/
# |____/ \__,_|___/\___|_|_|_| |_|\___|
#

import time
import typing
from loguru import logger
from schemas import heal
from services.redis_cache import RedisCache


class BaselineStore(object):
    """
    Baseline 仓库：

    - 按 app_id + page_id 维度存储页面上的“关键元素基线”
    - 每条基线记录一个逻辑元素 -> 当前有效 locator
    - 目前实现基于 Redis，将来可以挂 DB / Supabase 再同步一层
    """

    def __init__(self, cache: typing.Optional["RedisCache"] = None, ttl_seconds: int = 7 * 24 * 3600):
        self.cache = cache or RedisCache()
        self.ttl   = ttl_seconds

    # ======== 内部工具 ========

    @staticmethod
    def _logical_key(app_id: str, page_id: str, old_locator: "heal.Locator") -> str:
        """
        定义一个 “逻辑元素 ID”，将来可以换成更复杂的规则：
        - 例如加上业务 ID、用例 ID 等
        """
        return f"{app_id}:{page_id}:{old_locator.by}:{old_locator.value}"

    @staticmethod
    def _redis_key(app_id: str, page_id: str) -> str:
        return f"baseline:{app_id}:{page_id}"

    # ======== 对外 API ========

    async def get_page_baseline(self, app_id: str, page_id: str) -> list[dict[str, typing.Any]]:
        """
        获取某个页面的全部基线记录。

        返回格式（list[dict]）：
            [
                {
                    "logical_key": "...",
                    "locator": {"by": "...", "value": "..."},
                    "meta": {...}
                }
            ]
        """

        key       = self._redis_key(app_id, page_id)
        baselines = await self.cache.redis_get(key) or []

        # 确保是 list
        if not isinstance(baselines, list):
            logger.warning(f"[Baseline] Unexpected type in redis: {type(baselines)}")
            return []
        return baselines

    async def find_baseline_for(
        self,
        app_id: str,
        page_id: str,
        old_locator: "heal.Locator"
    ) -> typing.Optional[dict[str, typing.Any]]:
        """
        查找某个逻辑元素对应的当前基线 locator。
        """

        logical_key = self._logical_key(app_id, page_id, old_locator)
        baselines   = await self.get_page_baseline(app_id, page_id)

        for item in baselines:
            if item.get("logical_key") == logical_key:
                return item

        return None

    async def update_baseline(
        self,
        app_id: str,
        page_id: str,
        old_locator: "heal.Locator",
        new_locator: dict[str, typing.Any],
        extra_meta: typing.Optional[dict[str, typing.Any]] = None,
    ) -> dict[str, typing.Any]:
        """
        将某次自愈结果写入基线：
        - 如果已存在，则更新 locator + 更新时间 + 版本号+1
        - 如果不存在，则新增一条基线
        """

        cache_key   = self._redis_key(app_id, page_id)
        logical_key = self._logical_key(app_id, page_id, old_locator)

        now = int(time.time())

        baselines = await self.get_page_baseline(app_id, page_id)

        target = None

        for item in baselines:
            if item.get("logical_key") == logical_key:
                target = item
                break

        if target:
            # 更新已有基线
            meta    = target.get("meta") or {}
            version = int(meta.get("version", 1)) + 1

            target["locator"] = new_locator
            target["meta"]    = {
                **meta,
                "version"    : version,
                "updated_at" : now,
                "extra"      : {**(meta.get("extra") or {}), **(extra_meta or {})},
            }

            logger.info(
                f"[Baseline] Update baseline {logical_key} v{version} -> locator={new_locator}"
            )

        else:
            # 新增基线
            target = {
                "logical_key" : logical_key,
                "locator"     : new_locator,
                "meta"        : {
                    "version"    : 1,
                    "created_at" : now,
                    "updated_at" : now,
                    "extra"      : extra_meta or {},
                },
            }
            baselines.append(target)

            logger.info(
                f"[Baseline] New baseline {logical_key} locator={new_locator}"
            )

        # 回写 Redis
        await self.cache.redis_set(cache_key, baselines, ex=self.ttl)

        return target


if __name__ == '__main__':
    pass
