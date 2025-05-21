import os
import httpx
import asyncio
import random
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv
from common import const

fake = Faker()


# 判断运行环境并加载环境变量
if Path("/etc/secrets").exists():
    url_path = "/etc/secrets/CRON_JOB_URL"
    key_path = "/etc/secrets/CRON_JOB_KEY"
    CRON_URL = Path(url_path).read_text().strip()
    CRON_KEY = Path(key_path).read_text().strip()
else:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    CRON_URL = os.getenv("CRON_JOB_URL")
    CRON_KEY = os.getenv("CRON_JOB_KEY")

HEADERS = {"Authorization": f"Bearer {CRON_KEY}"}

async def create_keep_alive_jobs():
    cron_expressions = ["*/5 * * * *"] * 2 + ["*/10 * * * *"] * 2 + ["*/15 * * * *"]
    tasks = []

    for cron in cron_expressions:
        headers = {
            "User-Agent": fake.user_agent()
        }
        job = {
            "url": "https://license-server-s68o.onrender.com/keep-render-alive",
            "method": "GET",
            "headers": headers,
            "schedule": cron,
            "enabled": True
        }
        tasks.append(httpx.post(f"{CRON_URL}/jobs", headers=HEADERS, json=job))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return all(isinstance(res, httpx.Response) and res.status_code == 201 for res in results)

async def delete_all_jobs():
    try:
        resp = httpx.get(f"{CRON_URL}/jobs", headers=HEADERS, timeout=10)
        resp.raise_for_status()
        jobs = resp.json()
        for job in jobs:
            job_id = job.get("id")
            if job_id:
                await httpx.delete(f"{CRON_URL}/jobs/{job_id}", headers=HEADERS)
        return True
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False

async def create_keep_alive_jobs():
    intervals = [5, 5, 10, 10, 15]
    tasks = []

    for interval in intervals:
        headers = {
            "User-Agent": fake.user_agent()
        }
        cron = cron_expr(interval)
        job = {
            "url": "https://your-service.onrender.com/ping",
            "method": "GET",
            "headers": headers,
            "schedule": cron,
            "enabled": True
        }
        tasks.append(httpx.post(f"{CRON_URL}/jobs", headers=HEADERS, json=job))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return all(isinstance(res, httpx.Response) and res.status_code == 201 for res in results)

async def reset_cron_jobs():
    print("[cron] Resetting jobs ...")
    if await delete_all_jobs():
        print("[cron] Creating keep-alive jobs ...")
        await create_keep_alive_jobs()
    else:
        print("[cron] Skip creation due to delete failure")
