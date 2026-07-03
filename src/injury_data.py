"""injury_data.py — ESPN API 伤停数据获取"""

from __future__ import annotations

from typing import Any

import httpx

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"

# 联赛英文名 → ESPN API slug
LEAGUE_ESPN_SLUGS: dict[str, str] = {
    "Premier League": "eng.1",
    "La Liga": "esp.1",
    "Bundesliga": "ger.1",
    "Serie A": "ita.1",
    "Ligue 1": "fra.1",
    "World Cup": "fifa.worldcup",
}

# 竞彩中文联赛名 → ESPN slug
JC_LEAGUE_TO_ESPN: dict[str, str] = {
    "英超": "eng.1",
    "西甲": "esp.1",
    "德甲": "ger.1",
    "意甲": "ita.1",
    "法甲": "fra.1",
    "世界杯": "fifa.worldcup",
    "欧冠": "uefa.champions",
    "欧联": "uefa.europa",
}


def fetch_league_injuries_sync(
    espn_slug: str, team_id: str | None = None
) -> list[dict[str, Any]]:
    """同步版：获取指定联赛的伤停报告。"""
    params: dict[str, Any] = {"limit": 50}
    if team_id:
        params["team"] = team_id
    try:
        resp = httpx.get(
            f"{ESPN_BASE}/{espn_slug}/injuries",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        # Injuries can be under 'injuries' or 'events' depending on sport
        return data.get("injuries", []) or data.get("events", [])
    except Exception:
        return []


async def fetch_league_injuries(
    espn_slug: str, team_id: str | None = None
) -> list[dict[str, Any]]:
    """获取指定联赛的伤停报告。

    Args:
        espn_slug: ESPN 联赛 slug, 如 "eng.1", "fifa.worldcup"
        team_id: 可选，按球队筛选

    Returns:
        伤停列表
    """
    params: dict[str, Any] = {"limit": 50}
    if team_id:
        params["team"] = team_id
    try:
        resp = await httpx.AsyncClient().get(
            f"{ESPN_BASE}/{espn_slug}/injuries",
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("injuries", []) or data.get("events", [])
    except Exception:
        return []


def format_injuries(injuries: list[dict]) -> str:
    """将伤停数据格式化为易读文本。"""
    if not injuries:
        return "无已知伤停"
    lines = []
    for i in injuries:
        athlete = i.get("athlete", {})
        name = athlete.get("displayName", "未知球员")
        status = i.get("status", "未知")
        comment = i.get("comment", "")
        team_name = ""
        team = athlete.get("team", i.get("team", {}))
        if isinstance(team, dict):
            team_name = team.get("displayName", "")
        parts = [name, status]
        if team_name:
            parts.append(team_name)
        if comment:
            parts.append(comment)
        lines.append(" — ".join(parts))
    return "\n".join(lines[:10])  # 最多10条


def get_espn_slug(league_cn: str) -> str | None:
    """竞彩联赛名 → ESPN slug。"""
    return JC_LEAGUE_TO_ESPN.get(league_cn)
