"""llm_interpret.py — LLM API 调用，生成投注建议解读（Anthropic 格式）"""

from __future__ import annotations

import json
import os

import httpx

LLM_API = "https://uuapi.net/v1/messages"
LLM_MODEL = "claude-sonnet-5"
LLM_API_KEY_ENV = "LLM_API_KEY"

_SYSTEM_PROMPT = """你是一个竞彩足球投注解读助手。你的职责是根据统计模型输出的完整概率分布和竞彩赔率，给出投注方向建议。

核心原则：
1. 只做解读和建议，不做预测计算——概率和比分来自统计模型，你不能修改
2. 模型提供的是完整 H/D/A 概率分布，平局也是其中一部分，客观解读即可
3. 概率 + 赔率对比要有依据，基于你看到的数据说话
4. 不编造外部信息，不使用训练数据中的比赛知识

输出必须是结构化 JSON，不要包含任何其他文字。"""

_USER_PROMPT_WITH_ODDS = """分析以下竞彩比赛，给出投注建议。

比赛：{home} vs {away}
联赛：{league}
时间：{match_time}

模型概率：主胜 {h_prob:.0f}% / 平 {d_prob:.0f}% / 客胜 {a_prob:.0f}%
预测比分：{pred_score}（概率最高）
xG：{xg_home:.2f} - {xg_away:.2f}

竞彩赔率：主胜 {jc_h_odds} / 平 {jc_d_odds} / 客胜 {jc_a_odds}
让球{goal_line}：主胜 {hhad_h_odds} / 平 {hhad_d_odds} / 客胜 {hhad_a_odds}
赔率走势：主胜 {trend_h} / 平 {trend_d} / 客胜 {trend_a}

历史交锋：{h2h}
伤病信息：{injuries}

请按以下 JSON 格式输出：
{{
  "方向建议": "胜/平/负/让球胜/让球平/让球负/观望（选一个最明确的）",
  "信心评级": "高/中/低",
  "依据": "基于模型概率与赔率的简要分析",
  "风险提示": "本场比赛需要注意的风险因素"
}}"""

_USER_PROMPT_NO_ODDS = """分析以下比赛，给出投注建议。

比赛：{home} vs {away}
联赛：{league}
时间：{match_time}

模型概率：主胜 {h_prob:.0f}% / 平 {d_prob:.0f}% / 客胜 {a_prob:.0f}%
预测比分：{pred_score}（概率最高）
xG：{xg_home:.2f} - {xg_away:.2f}

历史交锋：{h2h}
伤病信息：{injuries}

请按以下 JSON 格式输出：
{
  "方向建议": "胜/平/负/观望（选一个最明确的）",
  "信心评级": "高/中/低",
  "依据": "基于模型概率的简要分析",
  "风险提示": "本场比赛需要注意的风险因素"
}"""


def interpret_match(
    home: str,
    away: str,
    league: str,
    match_time: str,
    model_pred: dict,
    analysis: dict,
    injuries_text: str = "无已知伤停",
    handicap_info: dict | None = None,
    h2h_text: str = "无",
    api_key: str | None = None,
) -> dict | None:
    """调用 LLM API (Anthropic 格式) 生成比赛解读。"""
    key = api_key or os.environ.get(LLM_API_KEY_ENV)
    if not key:
        return None

    h_prob = model_pred["outcome"]["H"] * 100
    d_prob = model_pred["outcome"]["D"] * 100
    a_prob = model_pred["outcome"]["A"] * 100
    hg, ag = model_pred["most_likely"]

    has_odds = bool(analysis and analysis.get("jc_h_odds"))
    h2h_text = h2h_text or "无"
    if has_odds:
        gl = handicap_info.get("goal_line", "-") if handicap_info else "-"
        hhad_h = handicap_info.get("home_odds", "-") if handicap_info else "-"
        hhad_d = handicap_info.get("draw_odds", "-") if handicap_info else "-"
        hhad_a = handicap_info.get("away_odds", "-") if handicap_info else "-"
        prompt = _USER_PROMPT_WITH_ODDS.format(
            home=home, away=away, league=league, match_time=match_time,
            h_prob=h_prob, d_prob=d_prob, a_prob=a_prob,
            pred_score=f"{hg}-{ag}",
            xg_home=model_pred.get("lambda_home", 0),
            xg_away=model_pred.get("lambda_away", 0),
            jc_h_odds=analysis["jc_h_odds"],
            jc_d_odds=analysis["jc_d_odds"],
            jc_a_odds=analysis["jc_a_odds"],
            goal_line=gl, hhad_h_odds=hhad_h,
            hhad_d_odds=hhad_d, hhad_a_odds=hhad_a,
            trend_h=analysis.get("trend_h", "flat"),
            trend_d=analysis.get("trend_d", "flat"),
            trend_a=analysis.get("trend_a", "flat"),
            h2h=h2h_text,
            injuries=injuries_text or "无已知伤停",
        )
    else:
        prompt = _USER_PROMPT_NO_ODDS.format(
            home=home, away=away, league=league, match_time=match_time,
            h_prob=h_prob, d_prob=d_prob, a_prob=a_prob,
            pred_score=f"{hg}-{ag}",
            xg_home=model_pred.get("lambda_home", 0),
            xg_away=model_pred.get("lambda_away", 0),
            h2h=h2h_text,
            injuries=injuries_text or "无已知伤停",
        )

    try:
        resp = httpx.post(
            LLM_API,
            json={
                "model": LLM_MODEL,
                "max_tokens": 1024,
                "system": _SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "User-Agent": "claude-cli/2.0.76 (external, cli)",
            },
            timeout=120,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"API {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()
        body = resp.json()
        # Find the text content block (skip thinking blocks)
        text_blocks = [c for c in body.get("content", []) if c.get("type") == "text"]
        if not text_blocks:
            return None
        content = text_blocks[0]["text"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content.strip())
    except Exception:
        return None
