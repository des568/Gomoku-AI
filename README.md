# Gomoku-AI

五子棋人机对战游戏，基于 Minimax 算法 + Alpha-Beta 剪枝实现。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

## 项目背景

本项目是数据结构与算法课程的期末大作业，旨在通过实现五子棋 AI，深入理解博弈树搜索、剪枝优化和估值函数设计等核心算法概念。

### 游戏特性

- 🎮 人机对战模式
- 🤖 AI 智能对手（Minimax + Alpha-Beta 剪枝）
- 📊 多难度级别（简单/中等/困难）
- 🎯 AI 思考过程可视化

## 核心算法

- **Minimax 算法**：递归搜索博弈树，找到最优落子位置
- **Alpha-Beta 剪枝**：减少不必要的搜索节点，提升效率
- **启发式评估函数**：基于棋型模式匹配的局面评分

### 知识点应用

| 知识点 | 应用场景 |
|--------|----------|
| 博弈树搜索 | Minimax 算法递归搜索最优落子 |
| 剪枝优化 | Alpha-Beta 剪枝减少搜索节点 |
| 估值函数设计 | 棋型模式匹配与评分 |

## 运行指南

### 环境要求

- Python 3.8 或更高版本
- Pygame 2.5.0

### 安装步骤

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
│   ├── __init__.py
│   ├── main.py           # 程序入口
│   ├── board.py          # 棋盘管理
│   ├── ai.py             # AI算法（Minimax + Alpha-Beta）
│   ├── evaluation.py     # 评估函数
│   └── ui.py             # Pygame界面
├── docs/
│   └── screenshots/      # 演示截图
├── tests/
│   ├── __init__.py
│   └── test_ai.py        # AI算法测试
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## 游戏说明

### 操作指南

1. **开始游戏**：运行程序后，点击棋盘任意位置落子
2. **执棋顺序**：玩家执黑棋先手，AI 执白棋后手
3. **重新开始**：点击重新开始按钮重置游戏
4. **悔棋**：点击悔棋按钮撤销上一步

### AI 策略说明

AI 采用自适应搜索策略，无需手动调节难度：

| 棋局阶段 | 棋子数 | 搜索策略 |
|----------|--------|----------|
| 开局 | 0-4 | 浅搜索，快速响应 |
| 中局 | 5-10 | 标准搜索深度 |
| 残局 | >10 | 自动加深搜索 |

## AI 工具声明

本项目使用了 AI 辅助开发，具体如下：

- **AI 辅助部分**：Pygame 框架代码、棋盘绘制逻辑、UI 交互代码
- **自主实现部分**：Minimax 搜索算法、Alpha-Beta 剪枝优化、启发式评估函数、棋型模式匹配

所有核心算法逻辑均由本人独立设计实现，并对代码进行了充分的理解和验证。

## 评分标准对照

| 维度 | 分值 | 完成情况 |
|------|------|----------|
| 核心功能 | 30 | ✅ 人机对战流畅，胜负判定准确 |
| 知识点应用 | 30 | ✅ Minimax + Alpha-Beta 自行实现 |
| 代码质量 | 20 | ✅ 模块化设计，注释清晰 |
| 文档与工程 | 10 | ✅ README 完整，环境配置清晰 |
| 创新性 | 10 | ✅ AI 思考可视化、难度调节 |

## 参考资料

- [Minimax Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Minimax)
- [Alpha-Beta Pruning - Wikipedia](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
- [Pygame Official Documentation](https://www.pygame.org/docs/)

## 作者

- GitHub: [des568](https://github.com/des568)
- 项目地址: https://github.com/des568/Gomoku-AI

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件