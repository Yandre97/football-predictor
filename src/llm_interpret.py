"""llm_interpret.py — DeepSeek API 调用，生成投注建议解读"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"

_SYSTEM_PROMPT = """你是一个专业的足球预测解读助手。
你的职责是解读统计模型的预测结果，而不是自己做预测。
你的输出必须是结构化的 JSON，不要包含任何其他文字。"""

_USER_PROMPT_TEMPLATE = """分析以下比赛，给出投注建议解读。

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

【竞彩赔率（不含让球）】
主胜赔率：{jc_h_odds}
平局赔率：{jc_d_odds}
客胜赔率：{jc_a_odds}
竞彩去水主胜概率：{jc_h_prob:.1f}%
竞彩去水平局概率：{jc_d_prob:.1f}%
竞彩去水客胜概率：{jc_a_prob:.1f}%

【模型 vs 赔率对比】
主胜价值差：{value_h:+.1f}% {"（模型看高）" if value_h > 0 else "（市场看高）"}
平局价值差：{value_d:+.1f}% {"（模型看高）" if value_d > 0 else "（市场看高）"}
客胜价值差：{value_a:+.1f}% {"（模型看高）" if value_a > 0 else "（市场看高）"}

【伤停信息】
{injuries}

请按以下 JSON 格式输出，不要包含任何其他内容：
{{
  "胜平负分析": "分析模型概率与赔率隐含概率的差异，指出是否存在价值投注机会",
  "比分建议": "对预测比分的合理性做简短评价",
  "信心评级": "高/中/低",
  "信心理由": "一句话说明信心评级的依据",
  "风险提示": "风险提示"
}}"""


def interpret_match(
    home: str,
    away: str,
    league: str,
    match_time: str,
    model_pred: dict,
    analysis: dict,
    injuries_text: str = "无已知伤停",
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
