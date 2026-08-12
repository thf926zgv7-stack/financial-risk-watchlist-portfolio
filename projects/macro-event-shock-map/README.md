# Macro Event Shock Map | 宏观事件—资产冲击地图

一个可交互的事件研究小工具：将公开市场时间序列与可追溯的宏观事件日期相连，展示事件日前后五个交易日内 S&P 500、WTI 原油、VIX 与 10 年期美债收益率的变动。

在线页面可直接选择事件、查看冲击矩阵和下载 CSV；无需 API Key，也不采集任何个人或内部数据。

## 适合展示的场景

- 投研/投行支持：用事件窗口把新闻线索变成可复核的市场反应。
- 金融科技/数据分析：展示公开数据获取、清洗、事件对齐、指标口径和交互呈现。
- 风控/经营分析：作为“风险事件发生后哪些指标先看”的轻量级原型。

## 数据与边界

- 市场序列来自 [FRED](https://fred.stlouisfed.org/)（SP500、DCOILWTICO、VIXCLS、DGS10）；构建脚本下载原始 CSV，仓库仅提交可复现的聚合结果。
- 事件日期来自公开机构公告或权威新闻的日期索引，详见脚本中的事件表。
- 这是描述性事件研究，不证明因果关系，不构成投资建议；窗口收益也不能用于预测未来表现。

## 本地运行与复现

```powershell
python scripts/build_data.py
python scripts/test_data.py
python -m http.server 8000
```

浏览器访问 `http://localhost:8000`。`index.html` 是零依赖静态应用，部署到 GitHub Pages 等静态托管即可使用。

## 仓库结构

```text
index.html                         # 交互式冲击地图
scripts/build_data.py              # 从 FRED 下载并计算事件窗口
scripts/test_data.py               # 数据结构校验
data/processed/event_study_data.js # 前端使用的可复现结果
```

## 简历表述（可核验）

> 基于 FRED 公开数据搭建宏观事件—资产冲击地图，将 4 类重大事件与股票、原油、波动率及长端利率进行 ±5 个交易日事件窗口对齐，完成数据获取、口径设计、交互可视化与可下载结果输出；明确标注描述性分析边界。
