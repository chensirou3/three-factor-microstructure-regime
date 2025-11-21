"""
Generate comprehensive Ladder vs EMA comparison report.
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def main():
    root = Path(__file__).resolve().parents[3]
    
    # Load Ladder results
    ladder_file = root / "results/strategy/ladder_phase/ladder_vs_ema_summary.csv"
    ladder_df = pd.read_csv(ladder_file)
    
    # Filter only Ladder results
    ladder_only = ladder_df[ladder_df['trend_engine'] == 'Ladder'].copy()
    
    # Load EMA Phase 3 aggregated results
    ema_agg_file = root / "results/strategy/phase3/all_experiments_summary.csv"
    
    if ema_agg_file.exists():
        ema_df = pd.read_csv(ema_agg_file)
        ema_df['trend_engine'] = 'EMA'
        ema_df['base_variant'] = ema_df['variant_id']
        
        # Combine
        combined = pd.concat([ladder_only, ema_df], ignore_index=True)
    else:
        print("EMA aggregated file not found, using Ladder only")
        combined = ladder_only
    
    # Save combined
    output_file = root / "results/strategy/ladder_phase/ladder_vs_ema_full_comparison.csv"
    combined.to_csv(output_file, index=False)
    print(f"✓ Saved: {output_file}")
    
    # Generate summary report
    report_file = root / "LADDER_VS_EMA_FINAL_REPORT.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🎯 Ladder vs EMA: Final Comparison Report\n\n")
        f.write("**Stage L2 Complete**: Comprehensive comparison of Ladder and EMA trend engines under three-factor regime framework\n\n")
        f.write("---\n\n")
        
        # Overall stats
        f.write("## 📊 Overall Performance\n\n")
        
        by_engine = combined.groupby('trend_engine').agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown_pct': 'mean',
            'n_trades': 'sum',
            'win_rate_pct': 'mean'
        }).round(4)
        
        f.write("| Trend Engine | Avg Return % | Avg Sharpe | Avg Max DD % | Total Trades | Avg Win Rate % |\n")
        f.write("|--------------|--------------|------------|--------------|--------------|----------------|\n")
        for engine, row in by_engine.iterrows():
            f.write(f"| **{engine}** | {row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | "
                   f"{row['max_drawdown_pct']:.2f} | {row['n_trades']:.0f} | {row['win_rate_pct']:.2f} |\n")
        f.write("\n")
        
        # By variant
        f.write("## 🔬 Performance by Variant\n\n")
        
        by_variant = combined.groupby(['base_variant', 'trend_engine']).agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'n_trades': 'sum'
        }).round(4)
        
        f.write("| Variant | Engine | Avg Return % | Avg Sharpe | Total Trades |\n")
        f.write("|---------|--------|--------------|------------|-------------|\n")
        for (variant, engine), row in by_variant.iterrows():
            f.write(f"| {variant} | **{engine}** | {row['total_return_pct']:.2f} | "
                   f"{row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        # Top performers (Ladder only)
        f.write("## 🏆 Top 10 Ladder Performers (by Return)\n\n")
        
        ladder_top = ladder_only.nlargest(10, 'total_return_pct')[
            ['symbol', 'timeframe', 'base_variant', 'total_return_pct', 'sharpe_ratio', 'n_trades']
        ]
        
        f.write("| Rank | Symbol | Timeframe | Variant | Return % | Sharpe | Trades |\n")
        f.write("|------|--------|-----------|---------|----------|--------|--------|\n")
        for i, (_, row) in enumerate(ladder_top.iterrows(), 1):
            f.write(f"| {i} | {row['symbol']} | {row['timeframe']} | {row['base_variant']} | "
                   f"{row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        # Worst performers
        f.write("## ⚠️ Bottom 10 Ladder Performers (by Return)\n\n")
        
        ladder_bottom = ladder_only.nsmallest(10, 'total_return_pct')[
            ['symbol', 'timeframe', 'base_variant', 'total_return_pct', 'sharpe_ratio', 'n_trades']
        ]
        
        f.write("| Rank | Symbol | Timeframe | Variant | Return % | Sharpe | Trades |\n")
        f.write("|------|--------|-----------|---------|----------|--------|--------|\n")
        for i, (_, row) in enumerate(ladder_bottom.iterrows(), 1):
            f.write(f"| {i} | {row['symbol']} | {row['timeframe']} | {row['base_variant']} | "
                   f"{row['total_return_pct']:.2f} | {row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        # By symbol
        f.write("## 📈 Performance by Symbol (Ladder)\n\n")
        
        by_symbol = ladder_only.groupby('symbol').agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'n_trades': 'sum'
        }).round(4).sort_values('total_return_pct', ascending=False)
        
        f.write("| Symbol | Avg Return % | Avg Sharpe | Total Trades |\n")
        f.write("|--------|--------------|------------|-------------|\n")
        for symbol, row in by_symbol.iterrows():
            f.write(f"| **{symbol}** | {row['total_return_pct']:.2f} | "
                   f"{row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        # By timeframe
        f.write("## ⏰ Performance by Timeframe (Ladder)\n\n")
        
        by_tf = ladder_only.groupby('timeframe').agg({
            'total_return_pct': 'mean',
            'sharpe_ratio': 'mean',
            'n_trades': 'sum'
        }).round(4).sort_values('sharpe_ratio', ascending=False)
        
        f.write("| Timeframe | Avg Return % | Avg Sharpe | Total Trades |\n")
        f.write("|-----------|--------------|------------|-------------|\n")
        for tf, row in by_tf.iterrows():
            f.write(f"| **{tf}** | {row['total_return_pct']:.2f} | "
                   f"{row['sharpe_ratio']:.4f} | {row['n_trades']:.0f} |\n")
        f.write("\n")
        
        f.write("---\n\n")
        f.write("**Data**: See `ladder_vs_ema_full_comparison.csv` for complete results\n")
    
    print(f"✓ Saved: {report_file}")
    print("\n✅ Stage L2 analysis complete!")

if __name__ == "__main__":
    main()

