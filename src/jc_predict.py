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
    enable_llm: bool = True,
    draw_bias: float = 0.20,
) -> list[dict[str, Any]]:
    """获取竞彩赛程并逐场预测。

    Args:
        bundle_leagues: 联赛模型 PredictorBundle
        bundle_intl: 国家队模型 PredictorBundle
        date: 日期 DDMMYY，默认当天
        api_key: LLM API key (Anthropic 格式)

    Returns:
        包含每场比赛完整信息的 dict 列表
    """
    raw_matches = fetch_jc_matches(date)

    key = api_key or os.environ.get("LLM_API_KEY")

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

        # 构建赔率元组 (用于 bundle.predict 的 odds 参数)
        odds_tuple = None
        jc_had = match_info["jc_odds"]
        if jc_had and jc_had.get("home_odds"):
            odds_tuple = (jc_had["home_odds"], jc_had["draw_odds"], jc_had["away_odds"])

        # 执行两次预测：不加赔率 vs 加赔率
        try:
            pred_base = bundle.predict(home_en, away_en, neutral=(scope == "internationals"))
            pred_boosted = bundle.predict(
                home_en, away_en, neutral=(scope == "internationals"),
                odds=odds_tuple,
            ) if odds_tuple else pred_base
        except Exception:
            results.append(match_info)
            continue

        # 赔率对比（用 boosted 预测结果 vs 竞彩去水概率）
        analysis = compare_odds(pred_boosted, jc_had)
        analysis_base = compare_odds(pred_base, jc_had) if odds_tuple else None

        match_info["prediction"] = {
            "outcome": pred_boosted["outcome"],
            "most_likely": pred_boosted["most_likely"],
            "lambda_home": pred_boosted.get("lambda_home", 0),
            "lambda_away": pred_boosted.get("lambda_away", 0),
            "top_scores": pred_boosted.get("top_scores", []),
        }
        match_info["prediction_base"] = {
            "outcome": pred_base["outcome"],
            "most_likely": pred_base["most_likely"],
            "lambda_home": pred_base.get("lambda_home", 0),
            "lambda_away": pred_base.get("lambda_away", 0),
        } if odds_tuple else None
        match_info["analysis"] = analysis
        match_info["analysis_base"] = analysis_base
        match_info["scope"] = scope
        match_info["odds_boosted"] = odds_tuple is not None

        # 伤停信息
        injuries_text = ""
        try:
            from src.injury_data import fetch_league_injuries_sync, format_injuries, get_espn_slug
            espn_slug = get_espn_slug(league_cn)
            if espn_slug:
                inj = fetch_league_injuries_sync(espn_slug)
                if inj:
                    injuries_text = format_injuries(inj)
        except Exception:
            pass

        # LLM 解读
        if enable_llm and key:
            # H2H
            h2h_key = tuple(sorted([home_en, away_en]))
            h2h_raw = bundle.last_h2h.get(h2h_key) if hasattr(bundle, "last_h2h") and bundle.last_h2h else None
            h2h_text = ""
            if h2h_raw and h2h_raw.get("n", 0) > 0:
                h2h_text = f"近{h2h_raw['n']}次交锋，主队{h2h_raw['pts_first']}分 vs 客队{h2h_raw['pts_second']}分，净胜球{h2h_raw['gd_first']:+d}"

            match_info["llm"] = interpret_match(
                home=home_en,
                away=away_en,
                league=league_cn,
                match_time=match_info["match_time"],
                model_pred=pred_boosted,
                analysis=analysis,
                injuries_text=injuries_text,
                handicap_info=match_info.get("jc_hhad"),
                h2h_text=h2h_text,
                api_key=api_key,
            )

        results.append(match_info)

    return results
