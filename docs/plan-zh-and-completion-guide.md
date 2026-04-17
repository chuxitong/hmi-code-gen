# 《Чжан Сычэн.docx》计划文档：中文全文与项目内完成方式

本文档对应仓库根目录上级目录中的 `Чжан Сычэн.docx`（英文撰写的毕设工作计划），已译为中文，并与本仓库 `figma-hmi-plugin` 中**已实现内容**逐周对照，说明**如何完成、产物在何处、如何复现**。

---

## 一、论文题目

| 语言 | 题目 |
|------|------|
| 俄文 | Разработка интеллектуального программного модуля генерации и итеративной корректировки кода человеко-машинных интерфейсов по графическим макетам |
| 英文 | Development of an Intelligent Software Module for the Generation and Iterative Refinement of Human-Machine Interface Code from Graphical Mockups |
| 中文（意译） | 基于图形化人机界面（HMI）草图，开发用于生成与迭代修正界面代码的智能软件模块 |

---

## 二、总体目标（概述）

目标是开发一个**面向工业 HMI**（操作站、监控大屏、报警页、设备状态、监督控制界面等）的 **Figma 智能插件原型**。系统**不应**被描述成「一键完美转代码」，而应帮助用户：

- 得到工业界面的**第一版可运行代码**（HTML/CSS）；
- 对照参考草图**迭代改进**，使渲染结果更接近设计；
- 用**自然语言指令**做局部修改。

技术路线是可行的：Figma 插件可用 `exportAsync` 导出节点为图、用 `figma.variables` 读设计变量、用 `getCSSAsync` 拿类似 Inspect 的 CSS 提示，并通过 `figma.ui.postMessage` / `parent.postMessage` 在沙箱与 iframe UI 之间传数据。

基线模型选用 **UI2Code^N**（公开论文与仓库，支持生成、编辑、润色）。系统应定位为**工业界面开发中的智能工程助手**，而非全自动完美设计转代码。

**实践价值包括：**减少早期手工量、给出可用初版代码、支持相对草图迭代、支持自然语言点改、展示如何将智能能力嵌入工业 HMI 工程流程。

---

## 三、插件目标功能（三项）

**功能 1：生成代码（Generate Code）**  
选中画板 → 导出 → 发往本地服务 → 得到 HTML/CSS → 在插件内展示代码、渲染预览小图、支持复制。

**功能 2：更接近草图（Make It Closer to the Mockup）**  
对比 Figma 导出图与当前代码渲染图，请求模型改进代码，可 **1～3 轮**迭代润色。

**功能 3：按指令编辑（Edit by Request）**  
用户输入自然语言，例如：把按钮改为次要样式、放大标题、减小趋势图上方间距、让报警区更醒目等；系统改代码并刷新预览。

以上与 UI2Code^N 的生成 / 编辑 / 润色模式一致。

**本仓库对应实现：** `figma-plugin/src/code.ts` + `ui.html` 调用 `local-service/app.py` 的 `/generate`、`/refine`、`/edit`；预览通过 `/render` 或响应中的 `preview_base64`。

---

## 四、通用每周提交格式（导师要求）

- **第 1 周** 创建 **一个** GitHub 或 GitLab 仓库，把链接发给导师（见根目录 `REPOSITORY.txt`）。
- **之后每周** 提交：同一仓库的更新链接、短周报（`reports/week-N.md` 或 PDF）、截图或短视频、问题与下周计划简述。
- 每周须有**可核查的具体结果**；导师按**莫斯科时间每周五 20:00**检查。

---

## 五、逐周要求：中文翻译 + 本仓库完成方式

下列「完成方式」均相对于项目根目录 **`figma-hmi-plugin/`**。

### 第 1 周：熟悉 Figma 插件流程并建立仓库

**原文要求（摘要）：** 理解如何获取当前选中画板、查看结构、导出 PNG、访问变量、CSS 提示、插件与 UI 消息通信。

**交付：** 带初始结构与 README 的仓库链接；一篇短文说明哪些数据**必选**、哪些**可选**、如何传给外部服务；最小 PoC（导出 PNG **或** 插件与 UI 测试消息）。

**本仓库完成方式：**

| 事项 | 位置 / 做法 |
|------|----------------|
| README | `README.md` |
| 必选/可选数据说明 | `docs/figma-data-extraction.md` |
| PoC（导出 + postMessage + 后续 HTTP） | `figma-plugin/src/code.ts`、`src/ui.html` |
| 仓库链接 | `REPOSITORY.txt` |
| 周报 | `reports/week-1.md` |

**本地验证：** 安装依赖后 `npx tsc`（在 `figma-plugin/`）生成 `dist/code.js`；Figma Desktop → Plugins → Development → Import plugin from manifest → 选 `figma-plugin/manifest.json`。

---

### 第 2 周：准备工业 HMI 草图集

**原文要求：** 2～3 个可编辑仪表盘模板 + 2～4 个工业 HMI/SCADA 视觉参考 → 在 Figma 中做出 **5～8** 个改编工业风界面；建议 2 简单、2 中等、1～2 较难；类型可含设备状态、报警、趋势、操作站、产线总览、机台卡片等。

**交付：** Figma 文件或分享链接；仓库内各画板 **PNG**；简短表格（屏名、场景、复杂度、入选原因）。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| Figma 链接与说明 | `mockups/mockup-index.md` 文内链接与段落说明 |
| 8 张 PNG 导出 | `mockups/png/01-…` ～ `08-…` |
| 周报 | `reports/week-2.md` |

**说明：** 模板与参考来源（Themesberg、Sneat、Siemens、Ignition 等）在 `mockup-index.md` 中以文字说明，不要求在仓库内包含第三方源文件。

---

### 第 3 周：启动并验证基线模型 UI2Code^N

**原文要求：** 本地安装运行；验证能否从截图生成代码、按文本编辑、用视觉反馈迭代改进。

**交付：** 安装与环境说明；**2～3** 个基线测试；短文总结优势与典型错误；基线输出**截图**。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 环境与部署说明 | `DEPLOYMENT.md`、`local-service/model_wrapper.py`、`local-service/verify_model_install.py` |
| 基线脚本（默认规则模型可复现） | `baseline-tests/run_baseline_tests.py` |
| 输出：HTML/PNG、日志、prompts | `baseline-tests/outputs/`（如 `test1-generated.png` 等） |
| 周报 | `reports/week-3.md` |

**复现命令：** 在仓库根目录执行  
`py baseline-tests/run_baseline_tests.py`  
若使用真实 UI2Code^N：设置环境变量 `USE_REAL_MODEL=1` 并先按 `DEPLOYMENT.md` 准备权重（笔记本 GPU 显存不足时可能极慢，可用规则模型完成课程/实验交付）。

---

### 第 4 周：将模型封装为本地 HTTP 服务

**原文要求：** 插件内不直接跑模型；HTTP 服务接收 PNG、任务描述、可选当前代码、变量、CSS 提示；返回 HTML/CSS 等；可用多路由或统一接口。

**交付：** 可运行的服务代码；API 说明与请求/响应示例；报告中附 **一条**演示请求与响应。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| FastAPI 服务 | `local-service/app.py`（`/generate`、`/refine`、`/edit`、`/render`、`/health`） |
| API 文档与 curl 示例 | `docs/api-reference.md` |
| 周报 | `reports/week-4.md` |

**启动：** `cd local-service` 后按 `README.md` 用 `uvicorn app:app --port 8000`（若使用项目内 venv 则按 README 中的解释器路径）。

---

### 第 5 周：代码渲染 + 插件外壳

**原文要求：** 无头浏览器将 HTML/CSS 渲染为截图；插件面板含：生成、更接近草图、编辑输入框、应用编辑、代码区、预览区、日志区；交付可工作的渲染模块、能与本地服务通信的最小面板、**短视频或 GIF** 证明壳可用。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 渲染模块 | `local-service/renderer.py`（Playwright） |
| 插件 UI | `figma-plugin/src/ui.html` |
| 演示截图与 GIF（自动化生成） | `reports/screenshots/week05_plugin_panel.png`、`week05_pipeline_demo.gif` |
| 生成脚本 | `baseline-tests/build_report_screenshots.py` |
| 周报 | `reports/week-5.md` |

**复现 GIF/截图：** `py baseline-tests/build_report_screenshots.py`（依赖已安装 Playwright 与 Pillow）。

---

### 第 6 周：实现生成 + 基础润色（端到端）

**原文要求：** 单选画板、导出 PNG、可选变量/CSS、调服务、展示代码与预览、复制；润色：保存原图、渲染当前代码、把参考图+渲染图+代码送服务、展示更新；交付至少在 **3** 个工业草图上演示生成、在 **≥2** 个草图上演示润色、**润色前后截图**。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 全量 8 套 mockup 流水线 | `baseline-tests/run_full_evaluation.py` |
| 每套：generate、refine×2、edit 的 HTML+PNG | `baseline-tests/outputs/full-eval/<m1…m8>/` |
| 润色前后对比拼图（示例） | `reports/screenshots/week06_m1_reference_generate_refine2.png`、`week06_m4_reference_generate_refine2.png` |
| 周报 | `reports/week-6.md` |

---

### 第 7 周：按请求编辑 + 变量/CSS 开关

**原文要求：** 自然语言编辑；开关：设计变量、CSS 提示；**≥3** 条编辑示例带截图；**≥1** 组对比：仅图 vs 图+变量+CSS。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 编辑示例（5 条）与 PNG | `baseline-tests/outputs/week7-edits/`、`edits.json` |
| A/B/C 上下文对比 | `baseline-tests/outputs/week7-context/`（`A_image_only`、`B_image_variables`、`C_image_variables_css`） |
| 插件内开关 | `figma-plugin/src/ui.html` 中复选框 + `code.ts` 传参 |
| 周报 | `reports/week-7.md` |

**复现：** `py baseline-tests/run_edit_and_context.py`

---

### 第 8 周：实验评估原型

**原文要求：** 结构化实验；测量首版耗时、可接受结果耗时、润色轮数、错误类型、变量/CSS 影响等；描述常见失败模式；交付实验节草稿、评估流程说明、简短结论页。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 指标 JSON/CSV、俄语汇总 | `baseline-tests/outputs/full-eval/metrics.json`、`metrics.csv`、`summary.md` |
| 实验与结论叙述 | `reports/week-8.md`、`thesis/chapter-3-materials.md`（与实验挂钩） |

**复现：** `py baseline-tests/run_full_evaluation.py`

---

### 第 9 周：改进基线并冻结原型

**原文要求：** 在可行范围内改进（提示词、请求格式、变量/CSS、后处理、润色逻辑、工业界面适配等）；交付 baseline vs 改进版对比、仓库最终版、改进说明、**带标签的 release 或冻结提交**。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 对比脚本与结果 | `baseline-tests/run_week9_comparison.py` → `baseline-tests/outputs/week9-comparison/` |
| 冻结说明与 Git 标签说明 | `release-notes.md`；标签名 `v2026.04.17-prototype-freeze` |
| 周报 | `reports/week-9.md` |

---

### 第 10 周：文献与论文写作

**原文要求：** 不写新大功能；准备文献综述；按学校格式组装论文；完成初稿并提交导师；文献可从 UI2Code^N 相关工作扩展到 Design2Code、WebSight、Web2Code 等。

**本仓库完成方式：**

| 事项 | 位置 |
|------|------|
| 第 1～2 章与第 3 章材料、参考文献草稿 | `thesis/chapter-1.md`、`chapter-2.md`、`chapter-3-materials.md`、`references.md` |
| 致导师说明信草稿 | `thesis/cover-letter.md` |
| 周报 | `reports/week-10.md` |

---

## 六、一键复现与交付自检

在 **`figma-hmi-plugin`** 根目录：

```bash
py baseline-tests/run_all_experiments.py
py baseline-tests/verify_deliverables.py
```

第二条命令退出码为 `0` 表示当前检查清单中的文件与实验产物齐全。

---

*译文与路径对照基于 `Чжан Сычэн.docx` 与仓库当前结构。*
