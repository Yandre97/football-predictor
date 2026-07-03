"""jc_ui.py — 竞彩预测标签页的 Streamlit UI"""

from __future__ import annotations

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
        cache_key = f"jc_llm_{idx}"
        if llm_result:
            with st.expander("🤖 AI 解读", expanded=False):
                cols = st.columns(5)
                confidence = llm_result.get("信心评级", "-")
                conf_color = {"高": "#00c853", "中": "#ff9100", "低": "#ff5252"}.get(confidence, "#94a3b8")
                cols[0].metric("信心", confidence, border=False)
                cols[1].metric("比分建议", llm_result.get("比分建议", "-")[:6], border=False)

                st.markdown(f"**胜平负分析**：{llm_result.get('胜平负分析', '-')}")
                st.markdown(f"**风险提示**：{llm_result.get('风险提示', '-')}")
                if llm_result.get("信心理由"):
                    st.caption(f"理由：{llm_result['信心理由']}")
        elif analysis:
            # 仅在需要时才渲染按钮，但不需要每次都显示
            pass


def render_jc_prediction() -> None:
    """竞彩预测标签页主渲染函数。"""
    st.markdown("## 竞彩预测")
    st.caption("中国体育彩票竞彩足球比赛预测，基于统计模型 + AI 解读")

    # 日期选择 + 刷新
    col_date, col_btn, _ = st.columns([2, 1, 3])
    today = datetime.now()
    default_date = today.strftime("%Y-%m-%d")
    selected_date = col_date.date_input("比赛日期", today, max_value=today + timedelta(days=7))
    refresh = col_btn.button("🔄 刷新", use_container_width=True)

    # 从 session_state 获取 bundle
    from src.predictor import PredictorBundle
    from pathlib import Path

    ROOT = Path(__file__).resolve().parent.parent
    bundle_leagues = None
    bundle_intl = None

    if (ROOT / "models" / "internationals.joblib").exists():
        bundle_intl = PredictorBundle.load("internationals")
    if (ROOT / "models" / "leagues.joblib").exists():
        bundle_leagues = PredictorBundle.load("leagues")

    if bundle_intl is None and bundle_leagues is None:
        st.error("没有可用的预测模型，请先训练")
        return

    # 缓存 key
    cache_key = f"jc_results_{selected_date}"
    if refresh or cache_key not in st.session_state:
        with st.spinner("获取竞彩赛程并预测中..."):
            try:
                date_str = selected_date.strftime("%d%m%y")
                results = predict_jc_matches(bundle_leagues, bundle_intl, date=date_str)
                st.session_state[cache_key] = results
            except Exception as e:
                st.error(f"获取数据失败: {e}")
                return

    results = st.session_state.get(cache_key, [])

    if not results:
        st.info("该日期没有竞彩比赛")
        return

    # 显示统计概览
    total = len(results)
    matched = sum(1 for r in results if r.get("matched"))
    unmatched = total - matched
    st.caption(f"共 {total} 场比赛，{matched} 场可预测，{unmatched} 场未匹配")

    # 逐场渲染
    for i, match in enumerate(results):
        _render_match_card(match, i)
        st.divider() if i < len(results) - 1 else None
