# Handover: 竞彩预测集成

## 项目结构

```
football-predictor/
├── app.py                      # Streamlit 主入口（加了"竞彩预测"Tab）
├── i18n.py                     # 中文 UI 翻译
├── requirements.txt            # pip 依赖
├── data/
│   ├── jc_team_map.json        # 竞彩中文队名 → 模型英文队名映射（250+国家队+五大联赛）
│   └── processed/              # 模型训练数据 parquet
├── models/
│   ├── internationals.joblib   # 国家队模型（321 支球队）
│   └── leagues.joblib          # 联赛模型（186 支球队）
├── src/
│   ├── jc_data.py              # 竞彩数据获取、队名映射、赔率提取、平局校准
│   ├── jc_predict.py           # 编排器：赛程→映射→预测→赔率对比→LLM
│   ├── jc_ui.py                # 竞彩预测标签页的 Streamlit UI
│   ├── llm_interpret.py        # LLM API 调用（Anthropic 格式）
│   ├── injury_data.py          # ESPN API 伤停数据
│   └── ...                     # 其他预测引擎模块（未改动）
├── sporttery-api/              # SportteryAPI（独立 Node.js 项目）
└── backtest_report.html        # 世界杯 2026 回测报告（82 场，65.9% 准确率）
```

## 当前状态

| 模块 | 状态 | 说明 |
|---|---|---|
| SportteryAPI | ✅ 运行中 | localhost:8787，提供竞彩赔率+赛程 |
| 队名映射 | ✅ 完成 | `jc_team_map.json` 覆盖所有国家队 + 五大联赛 |
| 竞彩数据获取 | ✅ 完成 | `jc_data.py`: 拉取赛程、赔率提取、价值差计算 |
| 预测编排 | ✅ 完成 | `jc_predict.py`: 完整链路（预测+赔率对比+伤停+H2H+LLM） |
| LLM 解读 | ⚠️ 间歇性 | `claude-sonnet-5` via uuapi.net，有时 API 400 错误 |
| 伤病数据 | ✅ 完成 | ESPN API 伤停信息传给 LLM |
| UI 标签页 | ✅ 完成 | "竞彩预测"为默认 Tab |
| 缓存机制 | ✅ 完成 | 模型+预测结果都缓存在 session_state，仅刷新按钮重新生成 |
| 世界杯回测 | ✅ 完成 | 82 场，65.9% 胜负准确率，RPS 0.0956 |

## 启动方式

```bash
# 1. 启动 SportteryAPI（Node.js）
cd sporttery-api && npm run dev

# 2. 启动 Streamlit App
cd football-predictor
streamlit run app.py
```

环境变量：
- `LLM_API_KEY` — 必填，uuapi.net 的 API key
- `WC_ONLY=0` — 同时加载联赛+国家队模型（竞彩需要）
- `FREE_MODE=1` — 免费模式
- `IS_HOSTED=0` — 本地模式

## 数据流

```
SportteryAPI (localhost:8787)
    → jc_data.fetch_jc_matches()     → 14 场竞彩比赛
    → map_team_name()                → 中文→英文队名映射
    → bundle.predict(odds=...)        → 模型预测（含赔率特征）
    → compare_odds()                  → 模型概率 vs 赔率去水概率
    → fetch_injuries() [ESPN API]     → 伤停信息
    → interpret_match() [LLM]         → DeepSeek/Claude 投注建议
    → jc_ui.py [Streamlit]            → 展示
```

## 已知问题

1. **LLM API 间歇性 400** — claude-sonnet-5 通过 uuapi.net 代理调用，有时返回 Invalid Request，原因未明确。代码内已包 try/except 不会崩页面，但部分比赛会缺失 AI 解读。
2. **模型从不预测平局** — Dixon-Coles 框架固有问题，不改模型前提下靠 LLM 在解读时补足。
3. **队名匹配不到的部分比赛** — K 联赛等亚洲联赛不在模型覆盖范围内，会标记"未匹配"。
4. **ESPN 伤病接口不保证世界杯数据** — 联赛数据较全，世界杯期间数据可能缺失。

## 待办/可改进

- [ ] 赔率走势（trend up/down）已传到 LLM prompt，但 H2H 数据偶尔触发错误
- [ ] 比分玩法（crs）和总进球（ttg）数据已从 SportteryAPI 获取但未传给 LLM
- [ ] 串关计算器（parlay）功能未实现
- [ ] `claude-fable-5` 换 `claude-sonnet-5` — 已改但未充分测试
- [ ] 本地部署稳定后可考虑 Docker 化
- [ ] GitHub Action 每天自动训练模型，注意数据文件冲突
