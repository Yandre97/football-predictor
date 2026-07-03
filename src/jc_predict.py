"""jc_predict.py — 竞彩预测编排器

编排完整流程：获取赛程 → 映射队名 → 调用预测引擎 → 赔率对比 → LLM 解读
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Any

from src.jc_data import (
    compare_odds,
    extract_had_odds,
    fetch_jc_matches,
    get_league_scope,
    map_team_name,
)
from src.llm_interpret import interpret_match


def predict_jc_matches(
    bundle_leagues,
    bundle_intl,
    date: str | None = None,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """获取竞彩赛程并逐场预测。

    Args:
        bundle_leagues: 联赛模型 PredictorBundle
        bundle_intl: 国家队模型 PredictorBundle
        date: 日期 DDMMYY，默认当天
        api_key: DeepSeek API key

    Returns:
        包含每场比赛完整信息的 dict 列表
    """
    raw_matches = fetch_jc_matches(date)

    key = api_key or os.environ.get("DEEPSEEK_API_KEY")

    results = []
    for m in raw_matches:
        home_cn = m["home"]["abbName"]
        away_cn = m["away"]["abbName"]
        league_cn = m["league"]["abbName"]

        home_en = map_team_name(home_cn)
        away_en = map_team_name(away_cn)

        match_info = {
            "match_id": m.get("matchNumStr", ""),
            "home_cn": home_cn,
            "away_cn": away_cn,
            "home_en": home_en,
            "away_en": away_en,
            "league_cn": league_cn,
            "match_time": f"{m.get('matchDate', '')} {m.get('matchTime', '')}",
            "status": m.get("status", ""),
            "matched": home_en is not None and away_en is not None,
            "jc_odds": extract_had_odds(m),
            "jc_hhad": extract_had_odds(m),  # will be replaced
        }

        # 让球数据
        from src.jc_data import extract_hhad_odds

        match_info["jc_hhad"] = extract_hhad_odds(m)

        if not match_info["matched"]:
            results.append(match_info)
            continue

        # 选择模型
        scope = get_league_scope(league_cn)
        bundle = bundle_intl if scope == "internationals" else bundle_leagues
        if bundle is None:
            results.append(match_info)
            continue

        # 执行预测
        try:
            pred = bundle.predict(home_en, away_en, neutral=(scope == "internationals"))
        except Exception:
            results.append(match_info)
            continue

        # 赔率对比
        analysis = compare_odds(pred, match_info["jc_odds"])

        match_info["prediction"] = {
            "outcome": pred["outcome"],
            "most_likely": pred["most_likely"],
            "lambda_home": pred.get("lambda_home", 0),
            "lambda_away": pred.get("lambda_away", 0),
            "top_scores": pred.get("top_scores", []),
        }
        match_info["analysis"] = analysis
        match_info["scope"] = scope

        # LLM 解读（同步模式，逐场调用）
        if key and analysis:
            match_info["llm"] = interpret_match(
                home=home_en,
                away=away_en,
                league=league_cn,
                match_time=match_info["match_time"],
                model_pred=pred,
                analysis=analysis,
                injuries_text="",
                api_key=key,
            )

        results.append(match_info)

    return results
