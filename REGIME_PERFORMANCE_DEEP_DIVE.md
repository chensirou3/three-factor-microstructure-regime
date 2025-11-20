# Regime绩效深度分析报告

**生成时间**: 2025-11-20  
**数据来源**: 36个symbol×timeframe组合的聚合分析  
**总交易数**: 96,363笔

---

## 🚨 **关键发现：Regime定义可能被反转！**

### **发现1: HIGH风险regime表现优于LOW风险regime**

| Risk Regime | 交易数 | 平均R倍数 | 中位R倍数 | 胜率% | 总盈亏 |
|------------|--------|----------|----------|-------|--------|
| **Medium** | 57,584 | **1.257** | -1.272 | 29.65% | $28,770 |
| **High** | 26,217 | **0.473** | -1.629 | **32.43%** | $4,926 |
| **Low** | 12,562 | **0.422** | -1.049 | 27.81% | $7,134 |

**关键洞察**:
- ⚠️ **HIGH风险regime的mean_R (0.473) > LOW风险regime (0.422)**
- ⚠️ **HIGH风险regime的胜率 (32.43%) > LOW风险regime (27.81%)**
- ✅ **MEDIUM风险regime表现最佳** (mean_R = 1.257)

**这意味着什么？**

有两种可能的解释：

#### **解释A: Regime定义被反转**
- 当前的"高风险"regime实际上是"低风险"
- ManipScore/OFI/VolLiqScore的高值可能代表**流动性充足、市场健康**
- 需要重新审视因子定义

#### **解释B: 高风险=高波动=高机会**
- 高风险regime虽然波动大，但也提供更好的趋势机会
- EMA策略在高波动环境下表现更好
- 这是合理的，因为趋势跟踪需要波动

---

## 📊 **按Three-Factor Box分析**

### **只有4个Box有交易**

| Box | 交易数 | 平均R | 中位R | 胜率% | 总盈亏 | 占比 |
|-----|--------|-------|-------|-------|--------|------|
| **M_low_O_low_V_low** | 61,787 | **1.237** | -1.293 | 29.01% | $34,957 | 64.1% |
| **M_low_O_high_V_low** | 5,209 | 0.993 | -1.302 | 30.36% | $968 | 5.4% |
| **M_low_O_high_V_high** | 20,944 | 0.799 | -1.660 | **32.58%** | $4,613 | 21.7% |
| **M_low_O_low_V_high** | 8,451 | 0.725 | -1.543 | 31.61% | $870 | 8.8% |

**关键洞察**:

1. **所有交易都发生在ManipScore=LOW的box中**
   - 没有任何交易在ManipScore=HIGH的box中
   - 这说明EMA策略天然避开了高操纵环境

2. **M_low_O_low_V_low是最佳box**
   - 占64.1%的交易
   - 最高mean_R (1.237)
   - 贡献了$34,957的总盈亏（占84%）

3. **所有box的mean_R都是正数**
   - 没有需要阻挡的"坏box"
   - 当前策略在所有regime下都盈利

4. **中位R都是负数**
   - 说明大部分交易亏损
   - 盈利来自少数大赢家（正偏分布）
   - 这是趋势跟踪策略的典型特征

---

## 🔍 **High Pressure分析**

| High Pressure | 交易数 | 平均R | 中位R | 胜率% | 总盈亏 |
|--------------|--------|-------|-------|-------|--------|
| **False** | 96,427 | 1.072 | -1.359 | 30.43% | $41,608 |

**关键洞察**:
- **100%的交易都在high_pressure=False时发生**
- 当前阈值设置导致没有任何交易被标记为high_pressure
- 这再次证明阈值过于保守

---

## 💡 **为什么Gating阻挡了0笔交易？**

### **原因分析**

当前gating规则：
```python
block_new_entries_in_high_pressure: true
block_new_entries_in_triple_high_box: true
```

但实际情况：
1. **high_pressure从未触发**
   - 需要RiskScore > 0.8
   - 实际上很少有bar满足这个条件

2. **triple_high_box从未出现**
   - 需要ManipScore=high AND OFI=high AND VolLiqScore=high
   - 这种极端组合在EMA入场信号时几乎不存在

### **为什么会这样？**

可能的原因：
1. **因子分布不均匀**
   - 大部分时间市场处于"正常"状态
   - 极端regime很少见

2. **EMA策略天然过滤**
   - EMA交叉本身就倾向于在"正常"市场条件下触发
   - 在极端regime下，价格可能太混乱，无法形成清晰的EMA交叉

3. **阈值校准问题**
   - 0.8的阈值可能对应99th百分位
   - 需要降低到0.6或0.5

---

## 🎯 **建议的下一步行动**

### **Action 1: 重新定义"高风险"**

**选项A: 反转定义**
```yaml
# 将当前的"low"定义为"high"
# 因为low风险regime表现更差
```

**选项B: 使用Medium作为基准**
```yaml
# Medium表现最佳 (mean_R = 1.257)
# 阻挡Low和High，只在Medium交易
```

### **Action 2: 降低Gating阈值**

**建议新阈值**:
```yaml
high_riskscore: 0.6  # 从0.8降低到0.6
low_riskscore: 0.4   # 从0.3提高到0.4
```

这样可以：
- 阻挡更多"边缘"regime的交易
- 验证gating的实际效果

### **Action 3: 基于Box的精细化Gating**

**策略**:
```yaml
# 只允许最佳box
allowed_boxes:
  - M_low_O_low_V_low  # mean_R = 1.237

# 或者阻挡最差box
blocked_boxes:
  - M_low_O_low_V_high  # mean_R = 0.725 (最低)
```

### **Action 4: 分析Regime持续性**

**目标**: 了解regime是否有预测性
- 如果high-risk regime后续表现更差 → 应该阻挡
- 如果high-risk regime只是当前状态 → 不应该阻挡

**方法**:
1. 计算每笔交易的entry regime
2. 计算该交易持有期间的平均regime
3. 分析entry regime vs holding regime的关系

---

## 📈 **统计总结**

### **整体绩效**

| 指标 | 数值 |
|------|------|
| 总交易数 | 96,363 |
| 总盈亏 | $40,830 |
| 平均R倍数 | 1.072 |
| 中位R倍数 | -1.359 |
| 整体胜率 | 30.43% |

### **Regime分布**

| Regime | 交易占比 |
|--------|---------|
| Medium | 59.8% |
| High | 27.2% |
| Low | 13.0% |

### **Box分布**

| Box | 交易占比 |
|-----|---------|
| M_low_O_low_V_low | 64.1% |
| M_low_O_high_V_high | 21.7% |
| M_low_O_low_V_high | 8.8% |
| M_low_O_high_V_low | 5.4% |

---

## 🔬 **深层问题**

### **问题1: 为什么中位R是负数但mean_R是正数？**

**答案**: 正偏分布（Right-skewed distribution）

- 大部分交易小亏（中位R = -1.359）
- 少数交易大赢（拉高mean_R到1.072）
- 这是趋势跟踪策略的典型特征：
  - 高胜率 → 中位R接近0
  - 低胜率 + 大赢家 → 中位R负，mean_R正

### **问题2: 为什么只有4个Box有交易？**

**答案**: ManipScore在EMA入场时几乎总是LOW

- EMA策略倾向于在"正常"市场条件下入场
- 高操纵环境下，价格太混乱，无法形成清晰的EMA交叉
- 这实际上是好事：策略天然避开了高风险环境

### **问题3: 为什么Medium表现最好？**

**答案**: 可能的"金发姑娘"效应（Goldilocks Effect）

- Low regime: 波动太小，趋势不明显
- High regime: 波动太大，假信号多
- Medium regime: 波动适中，趋势清晰

---

## ✅ **结论**

1. **当前Gating规则完全失效** - 需要重新校准阈值

2. **Regime定义可能有问题** - HIGH风险regime表现优于LOW

3. **所有Box都盈利** - 没有明显的"坏regime"需要阻挡

4. **Medium regime是最佳选择** - 考虑只在Medium交易

5. **策略天然避开高操纵环境** - ManipScore=high时几乎没有交易

---

**下一步**: 实施Action 1-4，重新运行回测，验证新阈值的效果

