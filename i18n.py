"""Chinese (Traditional) translations for the football predictor UI."""

from __future__ import annotations

_TRANSLATIONS: dict[str, str] = {
    # ── Sidebar ──
    "WC2026 Picks": "WC2026 预测",
    "Calibrated model, refreshed daily": "校准模型 · 每日更新",
    "Feedback / feature request": "反馈 / 功能建议",
    "Spot a bug or have an idea? Drop it here.": "发现 bug 或有想法？在这里提交。",
    "Type": "类型",
    "Feature request": "功能建议",
    "Bug report": "Bug 报告",
    "Other": "其他",
    "Short title": "简短标题",
    "Details": "详细描述",
    "Create on GitHub": "在 GitHub 上创建",
    "e.g. Add Champions League": "例如：添加欧冠",
    "Describe the issue or idea...": "描述问题或想法……",
    "Click here to post on GitHub →": "点击这里在 GitHub 上提交 →",
    "Pre-fills your text. You'll need a free GitHub account "
    "to publish. Or just share the link directly.": "已预填内容。需要免费 GitHub 账号才能发布，或者直接分享链接。",
    "Please fill in both title and details first.": "请先填写标题和详细描述。",
    "Or browse [existing issues]({url}).": "或浏览[已有 Issues]({url})。",
    "Models refresh automatically every day.": "模型每天自动更新。",
    "Update now": "立即更新",
    "Re-download latest match data and retrain (~30 sec)": "重新下载最新比赛数据并重新训练（约 30 秒）",
    "Update now (~30 sec)": "立即更新（约 30 秒）",
    "Updating... please wait": "更新中……请稍候",
    "Updated. Reloading...": "已更新，重新加载中……",
    "Update failed: {msg}": "更新失败：{msg}",
    "Update timed out (>5 min)": "更新超时（超过 5 分钟）",
    "{} model: ": "{} 模型：",

    # ── Hero ──
    "World Cup 2026": "2026 世界杯",
    # Hero subtitle is in HTML - handled separately

    # ── Tabs ──
    "World Cup bracket": "世界杯赛程",
    "Quick match check": "快速查比赛",
    "More": "更多",
    "League season": "联赛赛季",
    "Live data": "实时数据",

    # ── Match tab ──
    "Scope": "范围",
    "Home team": "主队",
    "Away team": "客队",
    "Neutral venue": "中立场地",
    "Ensemble weight": "模型权重",
    "0 = pure Dixon-Coles, 1 = full stacked ensemble.": "0 = 纯 Dixon-Coles，1 = 完整集成模型。",
    "Boost with current bookmaker odds (optional)": "加入当前博彩赔率（可选）",
    "When the model has bookmaker odds, RPS drops from ~0.20 to ~0.198 - "
    "almost matching the bookmaker baseline.": "加入博彩赔率后，RPS 从 ~0.20 降至 ~0.198，几乎与博彩基线持平。",
    "Home odds (decimal)": "主胜赔率（小数）",
    "Draw odds (decimal)": "平局赔率（小数）",
    "Away odds (decimal)": "客胜赔率（小数）",
    "Both teams are at the 2026 World Cup, so this blends in the "
    "squad-strength prior and matches the tournament view.": "两支球队都参加 2026 世界杯，已融入球队实力先验，与赛事视图一致。",
    "Outcome probabilities": "胜负概率",
    "Most likely scorelines": "最可能比分",
    "Full scoreline distribution": "全比分分布",
    "Predicted score": "预测比分",
    "Expected goals": "预期进球",
    "{} win": "{} 胜",
    "Draw": "平局",
    "{} goals": "{} 进球",
    "Probability": "概率",
    "Result": "结果",
    "Model": "模型",
    "Score": "比分",

    # ── League tab ──
    "No data found for {}.": "未找到 {} 的数据。",
    "Continue from current standings": "从当前积分榜继续",
    "If on, only the remaining fixtures are simulated.": "开启后，只模拟剩余赛程。",
    "Simulations": "模拟次数",
    "{n} teams. {played}/{total} fixtures played. "
    "Simulating the remaining {remaining}.": "{n} 支球队。已赛 {played}/{total} 场。正在模拟剩余 {remaining} 场。",
    "{n} teams. Simulating a full "
    "{total} match season from scratch.": "{n} 支球队。从头模拟完整 {total} 场赛季。",
    "Current standings (real)": "当前积分榜（实际）",
    "Run season simulation": "运行赛季模拟",
    "Running {n:,} simulations...": "正在运行 {n:,} 次模拟……",
    "Done - {n:,} seasons simulated.": "完成 - 已模拟 {n:,} 个赛季。",
    "Predicted final table": "预测最终积分榜",
    "Win %": "夺冠率",
    "Top 4 %": "前四率",
    "Top 6 %": "前六率",
    "Bottom 3 %": "降级率",
    "Expected pts": "预期积分",
    "Expected pos": "预期排名",
    "Team": "球队",
    "Pts": "积分",
    "Title race": "争冠形势",
    "Relegation candidates": "降级候选",
    "League model not available. Train it first.": "联赛模型不可用，请先训练。",

    # ── Tournament tab ──
    "Internationals model not available.": "国家队模型不可用。",
    "Format": "赛事",
    "Group draw": "分组抽签",
    "Real (official draw)": "真实（官方抽签）",
    "Snake (balanced)": "蛇形（平衡）",
    "Random": "随机",
    "Pick {n} teams (default: top {n} by Elo)": "选择 {n} 支球队（默认：Elo 排名前 {n}）",
    "Need exactly {n} teams. Currently {count}.": "需要恰好 {n} 支球队，当前 {count} 支。",
    "Unrecognised teams (treated as default-strength): {unknown}": "未识别的球队（按默认实力处理）：{unknown}",
    "Using the actual official draw for **{name}**.": "使用 **{name}** 的实际官方抽签结果。",
    "Group draw preview": "分组预览",
    "Predicted fixtures": "预测赛程",
    "Mode": "模式",
    "Most-likely outcomes (deterministic)": "最可能结果（确定性）",
    "Sampled tournament (re-roll for upsets)": "采样模拟（可重新抽签看冷门）",
    "Most-likely = each fixture's score is the expected-points-maximising pick "
    "under the scoring rules below. Sampled = one random tournament drawn from "
    "the probability distribution; click Re-roll for a different one.": "最可能 = 每场比赛的比分是在下方计分规则下预期得分最高的选择。采样 = 从概率分布中抽取一个随机赛事；点击重新抽签获得不同结果。",
    "Tune scoring (advanced)": "调整计分（高级）",
    "Defaults match the most common prediction contests (3 pts exact, 1 pt result). "
    "Adjust if your contest uses different rules.": "默认值符合最常用的预测竞赛规则（猜对比分 3 分，猜对结果 1 分）。如果规则不同请自行调整。",
    "Exact score pts": "猜对比分",
    "Correct result pts": "猜对结果",
    "Correct goal-diff bonus": "猜对净胜球加分",
    "Extra points if you got the goal-difference right "
    "(e.g. predicted 2-1 and actual was 3-2). 0 if "
    "your contest doesn't use this.": "如果净胜球也猜对则加分（例如预测 2-1，实际 3-2）。如果不使用此规则则填 0。",
    "Draw bias": "平局偏置",
    "Draw bias help": "纯预期值在默认计分下几乎不会选择平局。0.35 是回测的最佳值。",
    "Picks are EV-optimal across **all** scorelines for these rules. "
    "If a pick lands in a different result region than the headline H/D/A "
    "favourite, that's correct: the alternative result's modal scoreline is "
    "concentrated enough to outweigh the lost result point.": "选择在所有比分下都是预期值最优的。如果某选择落在与标题 H/D/A 不同的结果区域，那是正确的。",
    "Group {}": "{} 组",
    "**Group {}**": "**{} 组**",
    "By stage": "按阶段",
    "Chronological": "按时间",
    "By group": "按小组",
    "Predictions organised by stage. Group cards show standings + every "
    "fixture; knockout rounds render as a bracket.": "按阶段组织的预测。小组卡片显示积分榜和所有比赛；淘汰赛轮次以对阵图形式展示。",
    "Group Stage": "小组赛",
    "Knockout Bracket": "淘汰赛对阵图",
    "Final standings:": "最终排名：",
    "Run tournament simulation": "运行赛事模拟",
    "Running {n:,} tournament simulations...": "正在运行 {n:,} 次赛事模拟……",
    "Done - {n:,} tournaments simulated.": "完成 - 已模拟 {n:,} 次赛事。",
    "Conditioned on {n} already-played match"
    "{plural} — only remaining "
    "fixtures are randomised.": "基于 {n} 场已赛结果——仅剩余赛程随机化。",
    "These are the **real title odds** — how often each team won "
    "across every simulated tournament, upsets included.": "这是**真实夺冠概率**——每支球队在每次模拟赛事中的夺冠频率，包含冷门。",
    "Stage advancement probabilities": "各阶段晋级概率",
    "Title favourites": "夺冠热门",
    "Reach the final": "进入决赛",
    "Champion: **{}**": "冠军：**{}**",
    "Champion %": "夺冠率",
    "Final %": "决赛率",
    "Semi %": "四强率",
    "Group %": "小组出线率",

    # ── Free banner / paywall ──
    "Free for the 2026 World Cup.": "2026 世界杯免费使用。",
    " Every match, the full knockout bracket, and the "
    "simulator, no payment needed.": "所有比赛、完整淘汰赛对阵图和模拟器，无需付费。",
    "Get a reminder before kickoff (optional)": "开赛前接收提醒（可选）",
    "We'll email you before the tournament starts and around the big "
    "matchdays. No spam.": "我们会在赛事开始前和重要比赛日前后发邮件提醒你，不骚扰。",
    "Email me reminders": "邮件提醒我",
    "Email": "邮箱",
    "you@email.com": "you@email.com",
    "Email me a reminder before kickoff and the big matchdays. I've read "
    "the [Privacy Policy](?page=privacy).": "开赛前和重要比赛日给我发邮件提醒。我已阅读[隐私政策](?page=privacy)。",
    "Please enter a valid email address.": "请输入有效的邮箱地址。",
    "Please tick the consent box first.": "请先勾选同意框。",
    "Done. Check your inbox.": "完成，请查收收件箱。",
    "Thanks. We'll be in touch before kickoff.": "谢谢，我们会在开赛前联系你。",

    # ── Live data tab ──
    "Could not list leagues: {e}": "无法获取联赛列表：{e}",
    "Live data cache not yet populated. The daily workflow has to run once "
    "before this tab has anything to show.": "实时数据缓存尚未填充。每日工作流需要先运行一次。",
    "Data refreshed daily by the GitHub Action. "
    "Schedules cached: {sched}  ·  "
    "Lineups cached: {lineups}": "数据由 GitHub Action 每日更新。赛程缓存：{sched} · 阵容缓存：{lineups}",
    "League": "联赛",
    "Upcoming fixtures": "即将到来的比赛",
    "Recent results": "最近赛果",
    "Standings": "积分榜",
    "Lineups": "阵容",
    "Team focus": "球队聚焦",
    "Look-ahead (days)": "前瞻天数",
    "Fetch failed: {e}": "获取失败：{e}",
    "No upcoming fixtures in this window.": "该时间段内没有即将到来的比赛。",
    "How many": "数量",
    "No completed matches found.": "未找到已完成的比赛。",
    "Copy a game_id and paste into the Lineups tab to see the starting XI.": "复制 game_id 粘贴到阵容标签页查看首发阵容。",
    "No standings yet (season hasn't started or no completed matches).": "暂无积分榜（赛季未开始或无已完成比赛）。",
    "No teams available for this league yet.": "该联赛暂无可用球队。",
    "Could not list teams: {e}": "无法获取球队列表：{e}",
    "Team": "球队",
    "Form": "近期状态",
    "Form fetch failed: {e}": "获取状态失败：{e}",
    "Predicted XI": "预测首发",
    "Predicted starting XI · {formation} · ": "预测首发阵容 · {formation} · ",
    "Show recent actual starting XIs": "显示近期实际首发阵容",
    "Lineups fetch failed: {e}": "获取阵容失败：{e}",
    "game_id (from Recent results)": "game_id（从最近赛果中获取）",
    "Something went wrong loading this section. Please refresh the "
    "page. If it keeps happening, email support@wcpicks26.app.": "加载此部分时出错。请刷新页面。如果持续出现，请发邮件至 support@wcpicks26.app。",

    # ── Footer ──
    "Terms": "条款",
    "Privacy": "隐私",
    "Refunds": "退款",
    "Contact": "联系",
    "★ View source on GitHub": "★ 在 GitHub 上查看源码",

    # ── Misc ──
    "No trained models found. Run `python train.py` first.": "未找到训练好的模型。请先运行 `python train.py`。",
    "Group": "小组",
    "Date": "日期",
    "Home": "主队",
    "Away": "客队",
    "Pts": "积分",
    "Pos": "排名",
    "Pld": "赛",
    "W": "胜",
    "D": "平",
    "L": "负",
    "W-D-L": "胜-平-负",
    "GF": "进球",
    "GA": "失球",
    "GD": "净胜球",
    "Elo": "Elo 评分",
    "Analyse": "分析",
    "Alt scores": "备选比分",
    "xG": "预期进球",
    "MD": "轮次",
    "Re-roll": "重新抽签",
    "Champion": "冠军",
    "Win": "胜",
    "Advances": "晋级",
    "best 3rds": "最佳第三名",
    "Best 3rd-place": "最佳小组第三",
    "{n_groups} groups of {per_group} = {n_teams} teams. "
    "{advance} per group{best_thirds} advance to "
    "{n_ko}-team knockout.": "{n_groups} 组，每组 {per_group} 队 = {n_teams} 支球队。每组成绩前 {advance}{best_thirds} 晋级 {n_ko} 队淘汰赛。",
    "played": "已赛",
    "H %": "主胜%",
    "D %": "平局%",
    "A %": "客胜%",

    # ── WC 2026 squad prior ──
    "WC 2026 squad-strength prior": "2026 世界杯球队实力先验",
    "Blend the model's historical-form predictions with current squad "
    "quality (Transfermarkt market values + bookmaker outright odds). "
    "0 = pure historical model, 0.3 = balanced (recommended), "
    "0.7 = mostly market view.": "将模型的历史表现预测与当前球队实力（Transfermarkt 市场价值 + 博彩夺冠赔率）融合。0 = 纯历史模型，0.3 = 平衡（推荐），0.7 = 偏向市场观点。",

    # ── Paywall teaser ──
    "Featured Matchday 1 picks": "精选第 1 轮预测",
    "All {} Matchday 1 fixtures": "全部 {} 场第 1 轮比赛",
    "Not ready to buy?": "还没准备好购买？",
    "Get the free Matchday 1 picks emailed to you, plus one reminder "
    "before the tournament starts.": "免费获取第 1 轮预测邮件，以及赛前提醒。",
    "Predicted": "预测",
    "Below: every Matchday 1 fixture. Click any row to open its full "
    "breakdown. The full tournament unlock is **£7**.": "以下为第 1 轮所有比赛。点击任意行查看完整分析。解锁完整赛事 **£7**。",

    # ── Email signup / purchase ──
    "**Thanks for your purchase.** Your unlock link is on its way to your "
    "email and usually arrives within a minute (check spam if it doesn't). "
    "Click the link in that email to open the full tournament, then you can "
    "close this tab.": "**感谢购买！**解锁链接已发送到你的邮箱，通常在一分钟内到达（如果没收到请检查垃圾邮件）。点击邮件中的链接即可打开完整赛事。",
    "Still nothing after a few minutes? Email support@wcpicks26.app and "
    "we'll sort it out.": "几分钟后还没收到？请发邮件至 support@wcpicks26.app，我们来处理。",

    # ── Tournament detail ──
    "Played at a neutral venue, with the squad-strength prior "
    "blended in. 2026 World Cup group stage.": "中立场地，已融入球队实力先验。2026 世界杯小组赛。",
    "Smartest score pick": "最优比分选择",
    "← Back to the tournament": "← 返回赛事",
    "Unknown match: {} vs {}.": "未知比赛：{} vs {}。",
    "Click the Analyse link on any row to open its full breakdown: "
    "win probabilities, the likeliest scorelines, and a heatmap.": "点击任意行的分析链接查看完整分析：胜率、最可能比分和热力图。",
    "Computing fixtures...": "正在计算赛程……",
    "✓ {n} WC 2026 match{plural} "
    "detected with real results - using those instead of predictions.": "✓ 检测到 {n} 场 2026 世界杯已赛结果——将使用实际比分而非预测。",
    "Sample #{seed} - click Re-roll for a different tournament": "样本 #{seed} - 点击重新抽签获得不同结果",
    "{played} of {total} matches played (real results); "
    "{remaining} predicted.": "已赛 {played}/{total} 场（实际结果）；{remaining} 场预测。",
    "All {total} matches predicted (tournament hasn't started yet).": "全部 {total} 场比赛均为预测（赛事尚未开始）。",
    "{} of {} knockout matches played.": "淘汰赛已赛 {}/{} 场。",
    "not yet": "尚未",
    "Last {} played": "最近 {} 场",
    "Goal diff": "净胜球",
    "Form (oldest→newest)": "状态（从旧到新）",
    "Form window (matches)": "状态窗口（场次）",
    "Lineups to base prediction on": "用于预测的阵容场次",
    "### Predicted starting XI · {formation} · "
    "confidence: {confidence}": "### 预测首发阵容 · {formation} · 置信度: {confidence}",
    "**{date} · vs {opponent} ({venue})**": "**{date} · vs {opponent}（{venue}）**",
    "FBref publishes lineups post-match. Pre-match XIs are not available here.": "FBref 仅发布赛后阵容，不提供赛前预测首发。",
    "Fetching form...": "正在获取状态……",
    "🏆 Most-likely path winner": "🏆 最可能的夺冠路径",
    "This bracket follows one path: the favourite's most-likely result in "
    "every match. A single path can't show upsets, so the winner here "
    "won't always be the team most likely to lift the trophy overall. "
    "For true title odds, run the simulation at the bottom of the page.": "此对阵图沿一条路径展开：每场比赛采用最可能的结果。单一路径无法展现冷门，因此此处冠军不一定是最有可能夺冠的球队。如需真实夺冠概率，请运行页面底部的模拟。",
    "Checkout opens Monday June 1. Bookmark this page so you can "
    "come back to it.": "结账功能将于 6 月 1 日周一开放，请收藏此页面以便稍后返回。",
    "Refunds before kickoff (Jun 11). One-time payment, no subscription. "
    "Powered by Stripe.": "开赛前（6 月 11 日）可退款。一次性付款，无需订阅。由 Stripe 提供支持。",
    "#### All {n} Matchday 1 fixtures": "#### 全部 {n} 场第 1 轮比赛",
    "#### Not ready to buy?": "#### 还没准备好购买？",
    "Get the free Matchday 1 picks emailed to you, plus one reminder "
    "before the tournament starts.": "免费获取第 1 轮预测邮件推送，以及赛前提醒。",
    "[← Back to the tournament]({url})": "[← 返回赛事]({url})",
    "### Knockout Bracket": "### 淘汰赛对阵图",
    "### Group Stage": "### 小组赛",
    # ── Hero section ──
    "WC2026 Picks title": "WC2026 预测",
    "Free predictions for your <strong style=\"color:#f59e0b\">2026 World Cup office pool</strong>. "
    "For every match it gives the score most likely to win "
    "you points, set to whatever rules your contest uses. Built on a calibrated "
    "statistical model (Dixon-Coles, Pi-rating, machine learning). The whole "
    "tournament is free to use this World Cup.": "为你的 <strong style=\"color:#f59e0b\">2026 世界杯同事竞猜</strong>"
    "免费提供预测。每场比赛按你的竞猜规则自动给出最可能得分，"
    "基于校准的统计模型（Dixon-Coles、Pi-rating、机器学习）。"
    "本届世界杯期间全部免费使用。",
    "World Cup": "世界杯",
    "For every match it gives the score most likely to win "
    "you points, set to whatever rules your contest uses. Built on a calibrated "
    "statistical model (Dixon-Coles, Pi-rating, machine learning). The whole "
    "tournament is free to use this World Cup.": "每场比赛都会给出最可能帮你赢得积分的比分，按你竞猜的规则定制。基于校准的统计模型（Dixon-Coles、Pi-rating、机器学习）。整个赛事在本届世界杯期间免费使用。",
    "Calibrated model": "校准模型",
    "Bookmaker-level accuracy": "博彩级精度",
    "Free this World Cup": "本届世界杯免费",
    "Free for the 2026 World Cup.": "2026 世界杯免费开放。",
    "Every match, the full knockout bracket, and the simulator, no payment needed.": "所有比赛、完整淘汰赛对阵图和模拟器，无需付费。",
    "Like it? Support the project": "喜欢？支持项目",
}

# Translations that are HTML-heavy or non-trivial to key-match — handled
# as raw function replacements in app.py
_HTML_TRANSLATIONS: dict[str, str] = {
    # Hero section
    "Predict every match for<br>the 2026 World Cup": "预测 2026 世界杯<br>每场比赛",
}

# Keys that are used as format strings need special handling
_FORMAT_KEYS: dict[str, str] = {}


def _(text: str) -> str:
    """Translate an English UI string to Traditional Chinese.

    Falls back to the original text when no translation exists.
    """
    return _TRANSLATIONS.get(text, text)


def translate_html(key: str) -> str:
    """Translate HTML-heavy strings by exact key match."""
    return _HTML_TRANSLATIONS.get(key, key)
