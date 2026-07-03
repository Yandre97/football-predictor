"""jc_data.py — 竞彩数据获取 + 队名映射 + 赔率对比分析"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

# SportteryAPI 地址
SPORTTERY_BASE = "http://localhost:8787"

# 球队映射表
_TEAM_MAP: dict[str, str] | None = None

# 联赛名称映射（竞彩中文 → football-predictor scope）
LEAGUE_SCOPE_MAP = {
    "英超": "leagues",
    "英冠": "leagues",
    "西甲": "leagues",
    "德甲": "leagues",
    "意甲": "leagues",
    "法甲": "leagues",
    "世界杯": "internationals",
    "欧洲杯": "internationals",
    "欧国联": "internationals",
    "欧冠": "leagues",
    "欧联": "leagues",
    "欧协联": "leagues",
    "亚洲杯": "internationals",
    "非洲杯": "internationals",
    "美洲杯": "internationals",
}


def _load_team_map() -> dict[str, str]:
    global _TEAM_MAP
    if _TEAM_MAP is None:
        path = Path(__file__).resolve().parent.parent / "data" / "jc_team_map.json"
        with open(path, encoding="utf-8") as f:
            _TEAM_MAP = json.load(f)
    return _TEAM_MAP


def fetch_jc_matches(date: str | None = None) -> list[dict[str, Any]]:
    """从 SportteryAPI 获取竞彩赛程。

    Args:
        date: 可选日期筛选，格式 DDMMYY (如 "030726")

    Returns:
        比赛列表，每场包含 home/away/league/markets 等字段
    """
    params = {"pools": "had,hhad"}
    if date:
        params["date"] = date
    resp = httpx.get(f"{SPORTTERY_BASE}/api/matches", params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"SportteryAPI 返回错误: {data}")
    return data["data"]["matches"]


def map_team_name(cn_name: str) -> str | None:
    """中文队名 → 英文队名。找不到返回 None。"""
    return _load_team_map().get(cn_name)


def get_league_scope(league_cn: str) -> str:
    """根据联赛中文名判断使用哪个 scope 进行预测。"""
    return LEAGUE_SCOPE_MAP.get(league_cn, "leagues")


def extract_had_odds(match: dict) -> dict | None:
    """从比赛数据中提取胜平负赔率及去水概率。"""
    had = match.get("markets", {}).get("had")
    if not had:
        return None
    outcomes = {o["key"]: o for o in had["outcomes"]}
    return {
        "home_odds": outcomes.get("home", {}).get("odds"),
        "draw_odds": outcomes.get("draw", {}).get("odds"),
        "away_odds": outcomes.get("away", {}).get("odds"),
        "home_prob": outcomes.get("home", {}).get("noVigProb"),
        "draw_prob": outcomes.get("draw", {}).get("noVigProb"),
        "away_prob": outcomes.get("away", {}).get("noVigProb"),
        "return_rate": had.get("returnRate"),
        "margin": had.get("margin"),
        "trend_h": outcomes.get("home", {}).get("trend", "flat"),
        "trend_d": outcomes.get("draw", {}).get("trend", "flat"),
        "trend_a": outcomes.get("away", {}).get("trend", "flat"),
    }


def extract_hhad_odds(match: dict) -> dict | None:
    """提取让球胜平负数据（含让球数）。"""
    hhad = match.get("markets", {}).get("hhad")
    if not hhad:
        return None
    outcomes = {o["key"]: o for o in hhad["outcomes"]}
    return {
        "goal_line": hhad.get("goalLine"),
        "home_odds": outcomes.get("home", {}).get("odds"),
        "draw_odds": outcomes.get("draw", {}).get("odds"),
        "away_odds": outcomes.get("away", {}).get("odds"),
    }


def calibrate_draw(outcome: dict[str, float], draw_bias: float = 0.20) -> dict[str, float]:
    """平局校准：模型系统性低估平局概率，手动校正。

    Args:
        outcome: 原始 {'H': p, 'D': p, 'A': p}
        draw_bias: 平局概率提升幅度（0~0.3，默认 0.20）
                  世界杯历史平局率约 27%，模型接近 0%

    Returns:
        校准后的 {'H': p, 'D': p, 'A': p}
    """
    if draw_bias <= 0:
        return outcome
    h, d, a = outcome["H"], outcome["D"], outcome["A"]
    new_d = d + draw_bias
    # H 和 A 按比例缩放到剩下概率空间
    remaining = h + a
    if remaining > 0:
        scale = (1 - new_d) / remaining
        new_h = h * scale
        new_a = a * scale
    else:
        new_h = (1 - new_d) * 0.5
        new_a = (1 - new_d) * 0.5
    return {"H": new_h, "D": new_d, "A": new_a}


def compare_odds(model_pred: dict, jc_odds: dict | None) -> dict:
    """对比模型预测概率 vs 竞彩赔率去水概率，计算价值差。

    价值差 = 模型概率 - 赔率隐含概率(去水)
    正值表示模型认为该结果比市场隐含概率更高 → 潜在价值
    """
    if jc_odds is None or jc_odds.get("home_prob") is None:
        return {}

    model_h = model_pred["outcome"]["H"]
    model_d = model_pred["outcome"]["D"]
    model_a = model_pred["outcome"]["A"]

    return {
        "value_h": model_h - jc_odds["home_prob"],
        "value_d": model_d - jc_odds["draw_prob"],
        "value_a": model_a - jc_odds["away_prob"],
        "jc_h_prob": jc_odds["home_prob"],
        "jc_d_prob": jc_odds["draw_prob"],
        "jc_a_prob": jc_odds["away_prob"],
        "jc_h_odds": jc_odds["home_odds"],
        "jc_d_odds": jc_odds["draw_odds"],
        "jc_a_odds": jc_odds["away_odds"],
        "return_rate": jc_odds.get("return_rate"),
        "margin": jc_odds.get("margin"),
        "trend_h": jc_odds.get("trend_h", "flat"),
        "trend_d": jc_odds.get("trend_d", "flat"),
        "trend_a": jc_odds.get("trend_a", "flat"),
    }
