<!-- ARIS:BEGIN -->
## ARIS Skill Scope
ARIS skills installed in this project.
Update with: `bash /c/Users/w1828/repos/aris_repo/tools/install_aris.sh`
<!-- ARIS:END -->

# NV×AI Line #5 — Sensitivity-Optimal Low-SNR Ramsey Estimation (nv-research4)

**Status**: created 2026-09-12. Direction LOCKED by the user: **从低信噪比 Ramsey 数据
（重复次数少 = 光子预算低）估计出高精度磁场 B；评价指标 = 灵敏度 η（同时要求估计
不确定度 δB 小 + 所用实验数据的总积累时间 t_total 短）**。目标：**一篇创新性正结果论文**
（AI×NV 方向，物理期刊）。使用 ARIS 自动科研系统；真实 data_lab 数据必须使用，允许
按真实数据场景合成增广。

## 指标定义（论文与实验的第一性口径，全文统一）

- 灵敏度 **η = δB · √t_total**（t_total = 该估计所用实验数据的实际积累时间）。
- 低光子预算下的操作化对照：**达成目标精度 δB\* 所需的重复次数（= 总时间）**——
  在 8 级重复阶梯（5k→640k）上画 η(rep) 曲线；正结果 = 在给定总时间下 δB 更小。
- t_total 估算口径：对固定全扫描（300 τ 点）在重复级 r 下 `t_total ≈ r · Σ(τ_i + t_ovh)`；
  t_ovh（每点读出/脉冲开销）取值必须显式声明并做敏感性分析（单点列举 0.5×/1×/2× 档）。
- 所有对照：同数据、同 τ 网格、同评估协议；经典基线（LM 多重启/FFT+Rife/网格贝叶斯）
  给足调参预算。

## 与既有四条线的防重叠闸门（硬性）

| 线 | 占位 | L5 必须避开 |
|---|---|---|
| L1 `nv-research` | DC 边界区标定锚定（τ_off 物理）+ 摊销估计 + 校准 UQ（全 SNR，以边界/亚周期为叙述主线） | 不得把"标定锚定是主效应"重新讲一遍；τ_off/φ0 标定是该线的发现，L5 只能作为**已知约定引用** |
| L2 `old/ttmnv` | 已关闭（R-C），资产移交 | 不复活其声称 |
| L3 `nv_research2` | 稀疏采样设计（已归档技术报告） | 不进入"稀疏/少点 dwell 设计"领地（那属于 L3/L4 家族） |
| L4 `nv_research3` | 采样设计边界 + 混叠代价 + 验证器 | 同上；L5 固定全 τ 扫描，只调**光子预算**维度 |

**L5 的创新单元格** = "低光子预算 + 全扫描"下的**灵敏度最优化估计**：每点的重复次数
固定（sheet 级），用跨样本先验/摊销推断/校准信息在**少重复**条件下逼近高精度。Phase 0 必须：
(1) 调研该单元格的现有文献（ML-for-NV、few-shot/photon-efficient magnetometry、
sensitivity-oriented estimation）做 scoop check；(2) 用一个 pilot 实验验证"该单元格存在
真实的正结果"（见下方可行性闸门）。

## 正结果可行性闸门（G-Pos，Phase 1 末）

用户要求正结果论文——但诚实红线不放松。Phase 1 必须跑一个最小 pilot：
- 在最低两级 SNR（Sheet1-2，5k/10k）上对比：摊销估计器（可用 L1 血统的 APCE 变体 +
  校准条件化） vs 经典基线（同信息预算），指标 η 或"达标精度所需重复数"。
- **通过条件**：存在一个预注册的、可达成的正结果（如"在 X 重复次数下达到经典方法
  需要 Y 倍重复次数才能达到的 δB，p<0.01，≥3 seeds"），且与 L1 的已声称结论不重叠。
- 不通过 → 在方向内部 pivot（换预算档/换精度目标/换估计器家族）或如实降级报告；
  禁止用选择性报告制造正结果。

## 数据（强制与许可）

- **真实数据必须使用**：`C:\Users\w1828\repos\nv-research\old\ttmnv2_old\data_lab`
  （拷入本项目；DC 8 sheets × 300τ × 40 cols，B=1071.4·n nT，reps 5k–640k）。
- **合成数据允许**用于训练/增强，但必须锚定真实场景：参数分布来自真实拟合、
  噪声=散粒噪声律 σ(r)=0.207√(5000/r)、退化/漂移按真实观测建模；
  合成数据不得出现在 headline 评估里（评估一律真实数据）。
- **数字纪律**：单位（B nT、γ=2π×28e-6 rad/(µs·nT)、τ=20n ns）、高斯衰减、
  τ_off≈18.6±2.6 ns 修正约定（引用 L1 的 confirm_tau_off）——全部沿用，不得重犯单位陷阱。

## 方法与严谨性红线（继承）

- 统一 eval；audited split 冻结（无列泄漏）；不裁剪样本；报 n；配对 Wilcoxon + bootstrap CI；
  学习类方法 ≥5 seeds；失败率与 CRLB 对照；每个数字有 provenance（claim ↔ CSV ↔ figure ↔ script），
  PAPER_CLAIM_AUDIT 过闸才可 submission-ready。
- 不做：TTT、"22 nT 幻影"、退化模型上的重建损失、把训练集成绩写成泛化、速度当头条（η 才是头条，
  推理速度只在"实时估计"场景做支撑证据）。
- 多线共存注意：引用 L1/L3/L4 为同仪器 companion 工作；本线自投前跑一遍交叉重叠自查。

## 算力纪律（jindun）

- jindun 工程目录：`/data_3/repo/nv-research4`（只在此目录内工作）。
- **显卡动态检查（无静态归属）**：每次启动前 `nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory`
  + 显存查询；**有他人进程的卡一律不用（不论卡号）**；不确定归属查 `/proc/<pid>/cwd`；
  与其他线（L1 等）竞争时协商优先；跑完释放，无残留。
- 本地 RTX 5060 只跑冒烟；结果立即同步/提交 git。

## GitHub

`https://github.com/hxm2023/nv-research4`（代码 + 骨架 + 结果 JSON；**实验室原始数据与非公开材料
未经确认不上传**，按数据可用性原则"on request"处理）。

## Phase 0-1（案头，0 GPU）与时间线

1. 深调研+候选生成（≥5，≥3 非本宪法导出）+ CANDIDATE_KILL_LOG（含证伪条件）；
2. scoop check（最新 2 个月 arXiv × 每个候选单元格）；
3. 对抗审查 R1-R7（含 R7"这不就是 L1/L3/L4 吗" + G-Pos pilot）；
4. 6 维评分（闸门 ≥26/30，AI-novelty ≥4）→ PHASE0/PHASE1_DECISION 入 git。
5. 硬截止建议：Phase 0-1 两周内完成；每阶段产出 commit；与用户的决策点（方向微调/
  期刊选择/作者）先问后动。

## 合规

期刊 AI 使用政策披露；人对论文负责。

## External Review Backend (updated 2026-09-10: codex-mcp = qwen3.8-max)

- **codex MCP/CLI now serves `qwen3.8-max`** via DashScope compatible-mode (provider config in `~/.codex/config.toml`; API key persisted as env var `DASHSCOPE_API_KEY`). The previous gpt-5.4 (yansd666 relay) is disabled (config block kept commented for one-line revert).
- All `mcp__codex__codex`-based review workflows (research-review / citation-audit / experiment-audit / kill-argument / paper-claim-audit / auto-review-loop / domain-reviewer ...) transparently run on qwen3.8-max — still cross-model (non-Claude), thread semantics unchanged.
- Troubleshooting: `Missing environment variable: DASHSCOPE_API_KEY` -> restart Claude Code (env set after the current process started). `Arrearage` -> recharge the Aliyun DashScope account. Alternative text-review backend: `llm-chat` MCP (also qwen3.8-max).
