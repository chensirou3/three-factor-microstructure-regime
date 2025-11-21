# Ladder D3 Strategy Sanity Check Report

**Generated**: 2025-11-21 16:20:47

---

## Check 1: Multi-timeframe Alignment (No Look-ahead Bias)

| symbol   | high_tf   | low_tf   | status   |   violations | message                     |
|:---------|:----------|:---------|:---------|-------------:|:----------------------------|
| BTCUSD   | 4h        | 30min    | PASS     |            0 | No look-ahead bias detected |
| BTCUSD   | 4h        | 1h       | PASS     |            0 | No look-ahead bias detected |

✅ **PASS**: No look-ahead violations detected in multi-timeframe alignment

---

## Check 2: Ladder Signal Computation

### Summary

✅ **PASS**: Ladder EMA computation is causal, no ret_fwd_* usage in signal generation

See full report: `ladder_signal_check_report.md`

---

## Check 3: Time-split Out-of-Sample Test

### BTCUSD_4h_1h

| segment       | start_date   | end_date   |   n_trades |   total_return |   annualized_return |   max_drawdown |   sharpe_like |   win_rate |   avg_trade_return |
|:--------------|:-------------|:-----------|-----------:|---------------:|--------------------:|---------------:|--------------:|-----------:|-------------------:|
| IS_2010_2018  | 2017-05-07   | 2018-12-31 |         79 |        68.4568 |             37.2198 |       -2.75172 |       7.35023 |     68.75  |           0.672504 |
| OOS_2019_2025 | 2019-01-01   | 2025-10-08 |        561 |       453.716  |             28.786  |       -2.16405 |       7.81076 |     69.395 |           0.307474 |

✅ **STABLE**: OOS performance acceptable (Sharpe=7.811, DD=-2.16%)

### BTCUSD_4h_30min

| segment       | start_date   | end_date   |   n_trades |   total_return |   annualized_return |   max_drawdown |   sharpe_like |   win_rate |   avg_trade_return |
|:--------------|:-------------|:-----------|-----------:|---------------:|--------------------:|---------------:|--------------:|-----------:|-------------------:|
| IS_2010_2018  | 2017-05-07   | 2018-12-31 |         79 |        27.3171 |             15.7811 |       -1.50069 |       8.03739 |    73.4177 |           0.311969 |
| OOS_2019_2025 | 2019-01-01   | 2025-10-08 |        561 |       202.572  |             17.7805 |       -2.14413 |       4.16422 |    63.879  |           0.200312 |

✅ **STABLE**: OOS performance acceptable (Sharpe=4.164, DD=-2.14%)

---

## Check 4: Cost Sensitivity Analysis

### BTCUSD_4h_1h

| account_id   |   cost_per_side_pct |   n_trades |   total_return_gross |   total_return_net |   annualized_return_net |   max_drawdown_net |   sharpe_like_net |   win_rate |   avg_trade_return_net |
|:-------------|--------------------:|-----------:|---------------------:|-------------------:|------------------------:|-------------------:|------------------:|-----------:|-----------------------:|
| low_cost     |               0.003 |        639 |              615.549 |            613.972 |                 26.2992 |           -1.245   |          0.399261 |    83.7246 |                3.24071 |
| high_cost    |               0.07  |        639 |              615.549 |            578.757 |                 25.5427 |           -1.33492 |          0.38237  |    79.0297 |                3.24071 |

✅ **ROBUST**: Strategy remains profitable under high cost (degradation: 0.76%)

### BTCUSD_4h_30min

| account_id   |   cost_per_side_pct |   n_trades |   total_return_gross |   total_return_net |   annualized_return_net |   max_drawdown_net |   sharpe_like_net |   win_rate |   avg_trade_return_net |
|:-------------|--------------------:|-----------:|---------------------:|-------------------:|------------------------:|-------------------:|------------------:|-----------:|-----------------------:|
| low_cost     |               0.003 |        639 |              696.427 |            694.853 |                 27.9194 |          -0.241326 |          0.420326 |    92.0188 |                3.63337 |
| high_cost    |               0.07  |        639 |              696.427 |            659.695 |                 27.2339 |          -0.253701 |          0.404259 |    88.5759 |                3.63337 |

✅ **ROBUST**: Strategy remains profitable under high cost (degradation: 0.69%)

---

## Overall Conclusion

### ✅ All Checks Complete

All four sanity checks have been executed. Review the results above to determine if the D3 strategy is ready for production consideration.

**Next Steps**:
1. Review any warnings or failures above
2. If all checks pass, proceed to production code review
3. Set up small capital testing environment
4. Implement monitoring and alerting

---

**Report generated**: 2025-11-21 16:20:47