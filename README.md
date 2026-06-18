# Gomoku-AI

五子棋人机对战游戏，基于 Negamax 博弈树搜索 + Alpha-Beta 剪枝实现的自适应 AI。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

## 项目背景

本项目是**数据结构与算法 B 课程期末大作业**。选题方向为"经典游戏复刻与 AI"，通过实现五子棋人机对战，将课堂所学的博弈树搜索、剪枝优化、启发式评估等理论知识应用于工程实践。

### 游戏特性

- 人机对战模式（玩家执黑先手，AI 执白后手）
- 自适应搜索深度——根据棋局阶段自动调整计算量
- 攻击优先的威胁检测——活三/活四主动进攻，五连/冲四及时封堵
- 重新开始、悔棋功能

## 核心算法

### 1. Negamax 负值极大搜索

采用 Negamax 形式的博弈树搜索，将极大层和极小层统一为单一递归函数：

```
value = -negamax(board, depth-1, -beta, -alpha)
```

通过取负号，极大化和极小化合并为一个最大化问题，代码量减半且不易出错。

### 2. Alpha-Beta 剪枝

在 Negamax 搜索中引入 α-β 窗口剪枝：当某个节点的值超出已知最优范围 [α, β] 时，立即终止该分支的搜索。候选点按启发式分值降序排列，使剪枝尽可能早发生，搜索效率提升数倍。

### 3. 启发式评估函数

基于**棋型模式匹配**的局面评分，从 15×15 棋盘的四方向提取线条，匹配预定义的 19 种棋型：

| 棋型 | 分值 | 示例 |
|------|------|------|
| 五连 | 100,000 | `11111` |
| 活四 | 10,000 | `011110` |
| 冲四 | 5,000 | `01111` |
| 活三 | 1,000 | `01110` |
| 眠三 | 500 | `1110` |
| 活二 | 100 | `0110` |

每条线采用非重叠贪婪匹配，优先检测五连，己方棋型乘 1.1 进攻偏好系数。

### 4. 轻量级位置评分（fast_score）

候选排序使用 `fast_score()` 代替完整 `evaluate()`：仅评估经过落子位置的 4 条 9 格窗口线，速度提升约 25 倍。

### 5. 智能候选生成

只选取**2 格内有邻居**的空位作为候选落子点，跳过孤立位置。棋局初期候选量从 225 降至个位数，搜索量大幅减少。

### 6. 自适应搜索策略

根据棋盘上棋子总数自动调整搜索深度和候选数量：

| 阶段 | 棋子数 | 搜索深度 | 顶层候选 | 内层候选 |
|------|--------|----------|----------|----------|
| 开局 | ≤4 | 2 | 8 | 6 |
| 中局 | 5-10 | 用户设定 | 10 | 8 |
| 中后局 | 11-16 | 用户设定+1 | 10 | 8 |
| 残局 | >16 | 用户设定+1 | 12 | 10 |

### 7. 根节点威胁优先检测

在进入搜索前，按五子棋规则优先级检测：

| 优先级 | 条件 | 动作 |
|--------|------|------|
| 1 | AI 能直接五连 | 立即获胜 |
| 2 | 对手下一步能五连 | 必须封堵 |
| 3 | 对手有活四（两端空） | 必须封堵 |
| 4 | AI 有活四 | 主动进攻 |
| 5 | 对手有冲四（一端空） | 封堵唯一胜点 |
| 6 | AI 有冲四 | 主动造杀 |
| 7 | AI 有活三 | 布局进攻 |

所有威胁检测 0 节点、0ms 完成，保证交互流畅。

### 知识点覆盖

| 课程知识点 | 本项目应用 |
|------------|-----------|
| 博弈树搜索 | Negamax 递归搜索最优落子 |
| 剪枝优化 | Alpha-Beta 剪枝减少无效搜索节点 |
| 启发式函数设计 | 棋型模式匹配与加权评估 |
| 递归与回溯 | 搜索树深度优先遍历，make/undo 操作栈 |
| 复杂度分析 | 自适应深度与候选限制控制时间复杂度 |
| 动态规划思想 | 历史移动栈保证递归中棋盘状态一致性 |
| 贪心策略 | 根节点威胁排序与优先级决策 |
| 空间换时间 | 文本预渲染缓存、候选评分缓存 |

## 运行指南

### 环境要求

- Python 3.8 或更高版本
- Pygame 2.6.0 或更高版本

### 安装与启动

```bash
# 1. 克隆项目
git clone https://github.com/des568/Gomoku-AI.git
cd Gomoku-AI

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行游戏
python src/main.py
```

## 项目结构

```
Gomoku-AI/
├── src/
│   ├── main.py           # 程序入口
│   ├── board.py          # 棋盘管理（15×15，胜负判定，悔棋）
│   ├── ai.py             # AI算法（Negamax + Alpha-Beta + 威胁检测）
│   ├── evaluation.py     # 评估函数（棋型匹配 + 轻量评分）
│   └── ui.py             # Pygame图形界面
├── docs/
│   └── screenshots/      # 演示截图
├── tests/                # 测试用例
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## 游戏说明

### 操作指南

1. **开始游戏**：运行 `python src/main.py`，点击棋盘落子
2. **执棋顺序**：玩家执黑棋先手，AI 执白棋后手
3. **重新开始**：点击绿色"重新开始"按钮重置游戏
4. **悔棋**：点击红色"悔棋"按钮撤销（撤回玩家和 AI 各一步）

## AI 工具声明

本项目使用了 AI（Claude Code）辅助开发，具体如下：

- **AI 辅助部分**：
  - Pygame 框架代码与棋盘绘制逻辑
  - UI 交互代码（按钮布局、点击处理）
  - 代码重构与性能优化（Negamax 转换、轻量评估）
  - README 文档撰写
- **参考开源项目**：
  - [gobang_AI](https://github.com/colingogogo/gobang_AI) — 邻居过滤、孤立点跳过、Negamax 架构等优化思路
- **自主设计实现部分**：
  - 启发式评估函数与棋型模式匹配
  - 根节点威胁优先级检测（五连 → 活四 → 冲四 → 活三）
  - 自适应深度策略
  - Alpha-Beta 剪枝的候选排序
  - 棋盘移动历史栈（保证递归中状态一致性）

所有核心算法逻辑均经过充分理解和验证，非简单复制粘贴。

## 参考资料

- [Minimax Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Minimax)
- [Alpha-Beta Pruning - Wikipedia](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
- [Negamax - Wikipedia](https://en.wikipedia.org/wiki/Negamax)
- [Pygame Official Documentation](https://www.pygame.org/docs/)
- [五子棋 AI 实现思路 - 简书](https://www.jianshu.com/p/46e6d7b1ba5e)（gobang_AI 作者文章）
- [gobang_AI - GitHub](https://github.com/colingogogo/gobang_AI)

## 作者

- GitHub: [des568](https://github.com/des568)
- 项目地址: https://github.com/des568/Gomoku-AI

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
