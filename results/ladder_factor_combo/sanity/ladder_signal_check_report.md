# Ladder Signal Check Report

## Part 1: EMA Causality Check

| symbol   | timeframe   | status   | fastU_status   | fastL_status   | slowU_status   | slowL_status   |
|:---------|:------------|:---------|:---------------|:---------------|:---------------|:---------------|
| BTCUSD   | 4h          | PASS     | PASS           | PASS           | PASS           | PASS           |
| BTCUSD   | 30min       | PASS     | PASS           | PASS           | PASS           | PASS           |
| BTCUSD   | 1h          | PASS     | PASS           | PASS           | PASS           | PASS           |

## Part 2: ret_fwd_* Usage Check

| file               |   ret_fwd_mentions | status   | message                   |
|:-------------------|-------------------:|:---------|:--------------------------|
| mtf_timing.py      |                  0 | PASS     | No ret_fwd usage detected |
| ladder_features.py |                  0 | PASS     | No ret_fwd usage detected |

## Conclusion

✅ **PASS**: All checks passed
