"""llm_interpret.py — DeepSeek API 调用，生成投注建议解读"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"

_SYSTEM_PROMPT = """你是一个专业的足球预测解读助手。
你的职责是解读统计模型的预测结果和竞彩赔率，给出投注参考建议。
解读要简洁、实用，适合竞彩玩家阅读。
你的输出必须是结构化 JSON，不要包含任何其他文字。"""

_USER_PROMPT_TEMPLATE = """分析以下竞彩比赛，给出投注建议。

【基本信息】
比赛：{home} vs {away}
联赛：{league}
比赛时间：{match_time}

【模型预测】
主胜概率：{h_prob:.1f}%
平局概率：{d_prob:.1f}%
客胜概率：{a_prob:.1f}%
预测比分：{pred_score}
预期进球：{xg_home:.2f} - {xg_away:.2f}

【竞彩胜平负赔率】
主胜 {jc_h_odds} | 平 {jc_d_odds} | 客胜 {jc_a_odds}
去水概率：主 {jc_h_prob:.1f}% / 平 {jc_d_prob:.1f}% / 客 {jc_a_prob:.1f}%

【让球胜平负】{hadicap_info}

【模型 vs 赔率对比】
主胜：模型 {h_prob:.1f}% vs 市场 {jc_h_prob:.1f}%（价值差 {value_h:+.1f}%）
平局：模型 {d_prob:.1f}% vs 市场 {jc_d_prob:.1f}%（价值差 {value_d:+.1f}%）
客胜：模型 {a_prob:.1f}% vs 市场 {jc_a_prob:.1f}%（价值差 {value_a:+.1f}%）

【伤停信息】
{injuries}

请按以下 JSON 格式输出：
{{
  "投注建议": "推荐方向，如'主胜'/'平局'/'客胜'/'观望'，并简短说明",
  "让球建议": "如果让球盘有价值，给出让球方向建议",
  "比分参考": "模型最看好的比分，以及是否有其他值得关注的比分",
  "信心评级": "高/中/低",
  "分析": "用一两句话解释推荐理由"
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
    """调用 DeepSeek API 生成比赛解读。

    Args:
        home, away: 主客队名
        league: 联赛名
        match_time: 比赛时间
        model_pred: bundle.predict() 的输出
        analysis: compare_odds() 的输出
        injuries_text: 伤停文本
        handicap_info: 让球信息
        api_key: DeepSeek API key，不传则从环境变量读取

    Returns:
        解析后的 JSON dict，或 None（失败时）
    """
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None

    h_prob = model_pred["outcome"]["H"] * 100
    d_prob = model_pred["outcome"]["D"] * 100
    a_prob = model_pred["outcome"]["A"] * 100
    hg, ag = model_pred["most_likely"]

    # 构建价值差
    value_h = (analysis.get("value_h", 0) or 0) * 100
    value_d = (analysis.get("value_d", 0) or 0) * 100
    value_a = (analysis.get("value_a", 0) or 0) * 100

    prompt = _USER_PROMPT_TEMPLATE.format(
        home=home,
        away=away,
        league=league,
        match_time=match_time,
        h_prob=h_prob,
        d_prob=d_prob,
        a_prob=a_prob,
        pred_score=f"{hg}-{ag}",
        xg_home=model_pred.get("lambda_home", 0),
        xg_away=model_pred.get("lambda_away", 0),
        jc_h_odds=analysis.get("jc_h_odds", "-"),
        jc_d_odds=analysis.get("jc_d_odds", "-"),
        jc_a_odds=analysis.get("jc_a_odds", "-"),
        jc_h_prob=(analysis.get("jc_h_prob", 0) or 0) * 100,
        jc_d_prob=(analysis.get("jc_d_prob", 0) or 0) * 100,
        jc_a_prob=(analysis.get("jc_a_prob", 0) or 0) * 100,
        value_h=value_h,
        value_d=value_d,
        value_a=value_a,
        injuries=injuries_text or "无已知伤停",
        hadicap_info=handicap_info,
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
        # 清理可能的 markdown 代码块标记
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content.strip())
    except Exception:
        return None
