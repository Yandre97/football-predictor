"""jc_ui.py — 竞彩预测标签页的 Streamlit UI"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.jc_data import fetch_jc_matches, map_team_name
from src.jc_predict import predict_jc_matches


def _render_match_card(match: dict, idx: int) -> None:
    """渲染单场比赛卡片。"""
    home_cn = match.get("home_cn", "?")
    away_cn = match.get("away_cn", "?")
    league_cn = match.get("league_cn", "?")
    match_id = match.get("match_id", "")
    match_time = match.get("match_time", "")

    with st.container(border=True):
        # 标题行
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f"**{home_cn}** vs **{away_cn}**")
        c2.markdown(f"<small>{league_cn} · {match_id}</small>", unsafe_allow_html=True)
        c3.markdown(f"<small>{match_time}</small>", unsafe_allow_html=True)

        if not match.get("matched"):
            st.warning(f"⚠️ 未匹配球队：{home_cn} / {away_cn}，无法预测")
            return

        pred = match.get("prediction")
        analysis = match.get("analysis", {})
        if not pred:
            st.info("预测失败")
            return

        # 预测结果 + 赔率对比
        pred_base = match.get("prediction_base")
        display_label = "模型预测 (含赔率)" if match.get("odds_boosted") else "模型预测"

        col_prob, col_odds = st.columns(2)

        with col_prob:
            st.caption(display_label)
            outcome = pred["outcome"]
            hg, ag = pred["most_likely"]
            fig = px.bar(
                x=["主胜", "平局", "客胜"],
                y=[outcome["H"], outcome["D"], outcome["A"]],
                text=[f"{outcome['H']*100:.1f}%", f"{outcome['D']*100:.1f}%", f"{outcome['A']*100:.1f}%"],
                color=[outcome["H"], outcome["D"], outcome["A"]],
                color_continuous_scale="Blues",
                labels={"x": "", "y": "概率"},
            )
            fig.update_layout(
                height=180, showlegend=False, margin=dict(l=0, r=0, t=0, b=0),
                yaxis_tickformat=".0%", coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"预测比分：**{hg} - {ag}**　|　预期进球：{pred['lambda_home']:.2f} - {pred['lambda_away']:.2f}")

            # 显示不加赔率的原始预测对比
            if pred_base:
                ob = pred_base["outcome"]
                bhg, bag = pred_base["most_likely"]
                st.caption(f"不含赔率: {ob['H']*100:.1f}% / {ob['D']*100:.1f}% / {ob['A']*100:.1f}%　比分 {bhg}-{bag}")

        with col_odds:
            if analysis:
                st.caption("竞彩赔率 vs 模型对比")
                jc_items = [
                    ("主胜", analysis.get("jc_h_odds", "-"), analysis.get("jc_h_prob", 0), outcome["H"], analysis.get("value_h", 0)),
                    ("平局", analysis.get("jc_d_odds", "-"), analysis.get("jc_d_prob", 0), outcome["D"], analysis.get("value_d", 0)),
                    ("客胜", analysis.get("jc_a_odds", "-"), analysis.get("jc_a_prob", 0), outcome["A"], analysis.get("value_a", 0)),
                ]
                for label, odds, jc_prob, model_prob, value in jc_items:
                    sign = "+" if value > 0 else ""
                    color = "#00c853" if value > 0.03 else "#ff9100" if value < -0.03 else "#94a3b8"
                    st.markdown(
                        f"<span style='color:{color};font-weight:600'>{label}</span> "
                        f"赔率 {odds} | "
                        f"模型 {model_prob*100:.1f}% vs 市场 {jc_prob*100:.1f}% "
                        f"(<span style='color:{color}'>{sign}{value*100:.1f}%</span>)",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("无竞彩赔率数据")

        # LLM 解读（可折叠）
        llm_result = match.get("llm")
        if llm_result:
            with st.expander("🤖 AI 投注建议", expanded=True):
                confidence = llm_result.get("信心评级", "-")
                conf_color = {"高": "#00c853", "中": "#ff9100", "低": "#ff5252"}.get(confidence, "#94a3b8")
                st.markdown(
                    f"<span style='font-size:1.1rem;font-weight:700;color:{conf_color}'>"
                    f"推荐：{llm_result.get('投注建议', '-')}</span>"
                    f"<span style='margin-left:1rem;font-size:0.9rem;color:#94a3b8'>"
                    f"信心 {confidence}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**让球建议**：{llm_result.get('让球建议', '-')}")
                st.markdown(f"**比分参考**：{llm_result.get('比分参考', '-')}")
                st.markdown(f"**分析**：{llm_result.get('分析', '-')}")


def render_jc_prediction() -> None:
    """竞彩预测标签页主渲染函数。"""
    st.markdown("## 竞彩预测")
    st.caption("中国体育彩票竞彩足球比赛预测，基于统计模型 + AI 解读")

    # 加载模型（缓存到 session_state，避免每次重新读磁盘）
    from src.predictor import PredictorBundle
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent
    if "jc_bundle_intl" not in st.session_state:
        if (ROOT / "models" / "internationals.joblib").exists():
            st.session_state["jc_bundle_intl"] = PredictorBundle.load("internationals")
        else:
            st.session_state["jc_bundle_intl"] = None
    if "jc_bundle_leagues" not in st.session_state:
        if (ROOT / "models" / "leagues.joblib").exists():
            st.session_state["jc_bundle_leagues"] = PredictorBundle.load("leagues")
        else:
            st.session_state["jc_bundle_leagues"] = None
    bundle_intl = st.session_state["jc_bundle_intl"]
    bundle_leagues = st.session_state["jc_bundle_leagues"]

    if bundle_intl is None and bundle_leagues is None:
        st.error("没有可用的预测模型，请先训练")
        return

    # DeepSeek API key 配置
    api_key = os.environ.get("DEEPSEEK_API_KEY") or st.session_state.get("jc_api_key", "")
    if not api_key:
        api_key = st.text_input("DeepSeek API Key", type="password",
                                 help="输入你的 DeepSeek API key 开启 AI 解读")
        if api_key:
            st.session_state["jc_api_key"] = api_key
            st.rerun()

    # 首次加载：不传日期，获取全部可用比赛
    all_cache_key = "jc_all_matches"
    refresh = st.button("🔄 刷新", use_container_width=True)

    if refresh or all_cache_key not in st.session_state:
        with st.spinner("获取竞彩赛程并预测中..."):
            try:
                results = predict_jc_matches(
                    bundle_leagues, bundle_intl, date=None,
                    api_key=api_key or None, enable_llm=bool(api_key),
                )
                st.session_state[all_cache_key] = results
            except Exception as e:
                st.error(f"获取数据失败: {e}")
                return

    all_results = st.session_state.get(all_cache_key, [])
    if not all_results:
        st.info("暂无竞彩比赛")
        return

    # 提取可用日期
    from collections import OrderedDict
    date_options = OrderedDict()
    for r in all_results:
        mt = r.get("match_time", "")
        d = mt.split(" ")[0] if " " in mt else ""
        if d:
            date_options[d] = date_options.get(d, 0) + 1
    if not date_options:
        date_options[datetime.now().strftime("%Y-%m-%d")] = len(all_results)

    # 日期切换
    date_list = list(date_options.keys())
    selected_date_str = st.selectbox(
        "比赛日期",
        date_list,
        index=0,
        format_func=lambda d: f"{d} ({date_options[d]}场)",
    )

    results = [r for r in all_results if r.get("match_time", "").startswith(selected_date_str)]
    if not results:
        results = all_results

    # 显示统计概览
    total = len(results)
    matched = sum(1 for r in results if r.get("matched"))
    unmatched = total - matched
    st.caption(f"共 {total} 场比赛，{matched} 场可预测，{unmatched} 场未匹配")

    # 逐场渲染
    for i, match in enumerate(results):
        _render_match_card(match, i)
