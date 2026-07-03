"""llm_interpret.py — DeepSeek API 调用，生成投注建议解读"""

from __future__ import annotations

import json
import os

import httpx

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"

_SYSTEM_PROMPT = """你是一个中国体育彩票竞彩足球的投注分析助手。
你的职责是根据统计模型的预测结果和竞彩赔率，为每种竞彩玩法给出具体的投注建议。
解读要简洁、实用、有可操作性，直接告诉用户买什么。
你的输出必须是结构化 JSON，不要包含任何其他文字。"""

_USER_PROMPT_WITH_ODDS = """分析以下竞彩比赛，基于模型预测和赔率，为每种玩法给出投注建议。

【基本信息】
{home} vs {away}
联赛：{league}
时间：{match_time}

【统计模型预测数据】
- 胜平负概率：主胜 {h_prob:.1f}% / 平 {d_prob:.1f}% / 客胜 {a_prob:.1f}%
- 最可能比分：{pred_score}
- 预期进球：{xg_home:.2f} - {xg_away:.2f}

【竞彩赔率数据】
胜平负：主胜 {jc_h_odds} / 平 {jc_d_odds} / 客胜 {jc_a_odds}
（去水真实概率：主 {jc_h_prob:.1f}% / 平 {jc_d_prob:.1f}% / 客 {jc_a_prob:.1f}%）
让球胜平负：{handicap_info}

【模型 vs 市场对比】
- 主胜：模型认为 {h_prob:.1f}%，市场认为 {jc_h_prob:.1f}%，差异 {value_h:+.1f}%
- 平局：模型认为 {d_prob:.1f}%，市场认为 {jc_d_prob:.1f}%，差异 {value_d:+.1f}%
- 客胜：模型认为 {a_prob:.1f}%，市场认为 {jc_a_prob:.1f}%，差异 {value_a:+.1f}%

请针对每种竞彩玩法给出具体投注建议，严格按照以下 JSON 格式输出：
{{
  "胜平负": {{
    "推荐": "主胜/平局/客胜/不推荐",
    "sp": 赔率数值,
    "理由": "一句话理由"
  }},
  "让球胜平负": {{
    "推荐": "主胜/平局/客胜/不推荐",
    "让球数": 让球数,
    "sp": 赔率数值,
    "理由": "一句话理由"
  }},
  "总进球": {{
    "推荐": "0球/1球/2球/3球/4球/5球+/不推荐",
    "理由": "一句话理由"
  }},
  "信心评级": "高/中/低",
  "总分析": "不超过30字的总结"
}}"""

_USER_PROMPT_NO_ODDS = """分析以下比赛，基于模型预测给出投注参考。

【基本信息】
{home} vs {away}
联赛：{league}
时间：{match_time}

【模型预测数据】
- 胜平负概率：主胜 {h_prob:.1f}% / 平 {d_prob:.1f}% / 客胜 {a_prob:.1f}%
- 最可能比分：{pred_score}
- 预期进球：{xg_home:.2f} - {xg_away:.2f}

【伤停信息】
{injuries}

请按以下 JSON 格式输出：
{{
  "胜平负": {{
    "推荐": "主胜/平局/客胜/不推荐",
    "理由": "一句话理由"
  }},
  "比分参考": "模型最看好的比分",
  "信心评级": "高/中/低",
  "总分析": "不超过30字的总结"
}}"""


def interpret_match(
    home: str,
    away: str,
    league: str,
    match_time: str,
    model_pred: dict,
    analysis: dict,
    injuries_text: str = "无已知伤停",
    handicap_info: str = "无",
    api_key: str | None = None,
) -> dict | None:
    """调用 DeepSeek API 生成比赛解读。"""
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None

    h_prob = model_pred["outcome"]["H"] * 100
    d_prob = model_pred["outcome"]["D"] * 100
    a_prob = model_pred["outcome"]["A"] * 100
    hg, ag = model_pred["most_likely"]

    has_odds = bool(analysis and analysis.get("jc_h_odds"))
    if has_odds:
        value_h = (analysis.get("value_h", 0) or 0) * 100
        value_d = (analysis.get("value_d", 0) or 0) * 100
        value_a = (analysis.get("value_a", 0) or 0) * 100
        prompt = _USER_PROMPT_WITH_ODDS.format(
            home=home, away=away, league=league, match_time=match_time,
            h_prob=h_prob, d_prob=d_prob, a_prob=a_prob,
            pred_score=f"{hg}-{ag}",
            xg_home=model_pred.get("lambda_home", 0),
            xg_away=model_pred.get("lambda_away", 0),
            jc_h_odds=analysis["jc_h_odds"],
            jc_d_odds=analysis["jc_d_odds"],
            jc_a_odds=analysis["jc_a_odds"],
            jc_h_prob=analysis["jc_h_prob"] * 100,
            jc_d_prob=analysis["jc_d_prob"] * 100,
            jc_a_prob=analysis["jc_a_prob"] * 100,
            value_h=value_h, value_d=value_d, value_a=value_a,
            handicap_info=handicap_info,
            injuries=injuries_text or "无已知伤停",
        )
    else:
        prompt = _USER_PROMPT_NO_ODDS.format(
            home=home, away=away, league=league, match_time=match_time,
            h_prob=h_prob, d_prob=d_prob, a_prob=a_prob,
            pred_score=f"{hg}-{ag}",
            xg_home=model_pred.get("lambda_home", 0),
            xg_away=model_pred.get("lambda_away", 0),
            injuries=injuries_text or "无已知伤停",
        )

    try:
        resp = httpx.post(
            DEEPSEEK_API,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
            },
            headers={"Authorization": f"Bearer {key}"},
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content.strip())
    except Exception:
        return None
