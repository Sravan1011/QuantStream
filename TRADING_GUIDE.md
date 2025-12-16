# 📈 Trading Decision Guide

## How to Use This Platform for Trading Decisions

This guide explains how to interpret the analytics dashboard and make informed trading decisions, particularly for **pairs trading** and **mean reversion** strategies.

---

## 🎯 Quick Decision Framework

### For Pairs Trading (BTC/ETH Spread)

| Z-Score | Signal | Action | Rationale |
|---------|--------|--------|-----------|
| **< -2** | 🟢 **BUY SPREAD** | Long BTC, Short ETH | Spread is 2+ std devs below mean → likely to revert up |
| **-2 to -1** | 🟡 Watch | Monitor | Spread is below mean but not extreme |
| **-1 to +1** | ⚪ Neutral | No action | Spread is within normal range |
| **+1 to +2** | 🟡 Watch | Monitor | Spread is above mean but not extreme |
| **> +2** | 🔴 **SELL SPREAD** | Short BTC, Long ETH | Spread is 2+ std devs above mean → likely to revert down |

---

## 📊 Understanding the Metrics

### 1. **Hedge Ratio (β)**

**What it shows**: How many units of ETH move with 1 unit of BTC

**Example**: β = 79.17
- When BTC moves $1, ETH moves $1/79.17 = $0.0126
- Or: 1 BTC ≈ 79 ETH in price movement

**How to use**:
- Higher β = stronger relationship
- Use β to size your positions correctly

---

### 2. **Spread**

**Formula**: `Spread = BTC_price - (β × ETH_price)`

**What it shows**: The difference between actual BTC price and "predicted" BTC price based on ETH

**Example**:
- BTC = $87,129
- ETH = $2,948
- β = 79.17
- Spread = 87,129 - (79.17 × 2,948) = -146,316

**How to use**:
- Spread itself is hard to interpret
- **Z-score** makes it actionable

---

### 3. **Z-Score** ⭐ (Most Important)

**Formula**: `Z-score = (Current_Spread - Mean_Spread) / Std_Dev`

**What it shows**: How many standard deviations the current spread is from its historical mean

**Interpretation**:

```
Z-Score Range:
  -3 ←──────── -2 ←──────── -1 ←──────── 0 ──────→ +1 ──────→ +2 ──────→ +3
  Extreme      Strong       Weak      Normal    Weak       Strong      Extreme
  Undervalued  Undervalued  Under              Over       Overvalued  Overvalued
```

**Trading Signals**:

#### 🟢 **Z-Score < -2** (Strong Buy Signal)
**Interpretation**: BTC is underpriced relative to ETH

**Action**:
```
1. BUY BTC (go long)
2. SELL ETH (go short)
3. Position size: β ratio
   - If β = 79, buy $79k BTC, sell $79k ETH
```

**Expected outcome**: Spread will revert to mean (increase)
- BTC price will rise relative to ETH
- Profit when spread normalizes

**Example**:
- Current: BTC = $85,000, ETH = $2,900, Z = -2.5
- Mean reversion: BTC rises to $87,000, ETH stays at $2,900
- Profit: $2,000 on BTC position

---

#### 🔴 **Z-Score > +2** (Strong Sell Signal)
**Interpretation**: BTC is overpriced relative to ETH

**Action**:
```
1. SELL BTC (go short)
2. BUY ETH (go long)
3. Position size: β ratio
```

**Expected outcome**: Spread will revert to mean (decrease)
- BTC price will fall relative to ETH
- Profit when spread normalizes

---

#### ⚪ **Z-Score between -1 and +1** (No Action)
**Interpretation**: Spread is within normal range

**Action**: Wait for extreme values

---

## 💡 Practical Trading Examples

### Example 1: Mean Reversion Trade

**Dashboard shows**:
- Hedge Ratio: 79.17
- Current Spread: -146,320
- Mean Spread: -146,315
- Std Dev: 1.70
- **Z-Score: -2.94** 🟢

**Analysis**:
- Z-score is < -2 → Strong buy signal
- BTC is significantly underpriced vs ETH
- High probability of mean reversion

**Trade Setup**:
```
Entry:
  - Long $10,000 BTC at $87,000
  - Short $10,000 ETH at $2,950
  
Target:
  - Z-score returns to 0 (mean)
  - Spread increases by ~5 points (3 std devs)
  
Exit:
  - Close when Z-score reaches -0.5 to 0
  - Or set profit target at +$500
  
Stop Loss:
  - If Z-score goes below -3.5
  - Or spread widens by another $10
```

**Expected Profit**:
- If spread reverts 3 std devs: ~$5.10 per spread unit
- On $10k position: ~$510 profit

---

### Example 2: Avoiding False Signals

**Dashboard shows**:
- **Z-Score: -1.2** 🟡

**Analysis**:
- Z-score is between -2 and -1
- Not extreme enough for high-confidence trade
- Could be normal volatility

**Action**: **WAIT**
- Monitor for Z-score to reach -2 or lower
- Don't trade on weak signals

---

## 🎓 Advanced Strategies

### 1. **Scaling In/Out**

Instead of one large trade, scale positions:

```
Z-Score < -2.0: Enter 33% position
Z-Score < -2.5: Add 33% (66% total)
Z-Score < -3.0: Add 34% (100% total)

Exit:
Z-Score > -1.0: Close 33%
Z-Score > -0.5: Close 33%
Z-Score > 0:    Close remaining 34%
```

---

### 2. **Correlation Check**

**Before trading**, verify correlation is strong:
- Use "View Correlation" button
- Correlation should be > 0.85
- Low correlation = unreliable spread

---

### 3. **Volatility Filter**

**Check Rolling Std Dev** in stats cards:
- High volatility = wider stops needed
- Low volatility = tighter stops possible

---

## ⚠️ Risk Management

### Position Sizing

**Never risk more than 2% of capital per trade**

Example with $100,000 capital:
```
Max risk: $2,000
Stop loss: 2 std devs = $3.40
Position size: $2,000 / $3.40 = $588 per spread unit
```

---

### Stop Loss Rules

**Set stops at**:
- Z-score moves 1 std dev against you
- Or 50% of expected profit target

Example:
- Entry: Z = -2.5
- Target: Z = 0
- Stop: Z = -3.5 (1 std dev worse)

---

### Time Limits

**Exit if**:
- Position open > 24 hours with no mean reversion
- Correlation drops below 0.7
- Major news event affects one asset

---

## 🔔 Using Alerts

### Recommended Alert Setup

**Create alerts for**:

1. **Entry Signals**:
   ```
   Alert: "BTC/ETH Z-Score < -2"
   → Notification to consider long spread
   ```

2. **Exit Signals**:
   ```
   Alert: "BTC/ETH Z-Score > -0.5"
   → Notification to close long spread
   ```

3. **Stop Loss**:
   ```
   Alert: "BTC/ETH Z-Score < -3.5"
   → Emergency exit signal
   ```

---

## 📈 Interpreting Price Charts

### BTC/ETH Price Charts

**Look for**:
- **Divergence**: BTC rising while ETH falling (or vice versa)
- **Convergence**: Prices moving together
- **Breakouts**: Sharp moves in one asset

**Trading tip**: 
- Strong divergence often precedes mean reversion
- Use price charts to confirm z-score signals

---

## 🎯 Complete Trading Checklist

Before entering a trade, verify:

- [ ] Z-score is < -2 or > +2
- [ ] Correlation is > 0.85
- [ ] Hedge ratio is stable (not changing rapidly)
- [ ] You have calculated position size
- [ ] Stop loss is set
- [ ] Profit target is defined
- [ ] Risk is < 2% of capital

---

## 📊 Performance Tracking

### Track These Metrics

1. **Win Rate**: % of profitable trades
   - Target: > 60%

2. **Risk/Reward**: Average profit / Average loss
   - Target: > 1.5:1

3. **Max Drawdown**: Largest losing streak
   - Limit: < 10% of capital

---

## 🚀 Quick Start for Beginners

### Day 1-7: Paper Trading
1. Watch z-score for 1 week
2. Note when it crosses ±2
3. Track hypothetical trades
4. Learn the patterns

### Day 8-14: Small Positions
1. Start with $100-500 positions
2. Follow the rules strictly
3. Focus on process, not profit

### Day 15+: Scale Up
1. Increase size gradually
2. Keep risk at 1-2% per trade
3. Review performance weekly

---

## 💎 Key Takeaways

1. **Z-Score is your primary signal**
   - < -2: Consider buying spread
   - \> +2: Consider selling spread

2. **Mean reversion is the core concept**
   - Extreme values tend to return to average
   - Patience is key

3. **Risk management is crucial**
   - Always use stops
   - Never risk more than 2%
   - Size positions correctly

4. **Correlation matters**
   - High correlation = reliable signals
   - Low correlation = avoid trading

5. **Be patient**
   - Wait for Z-score > ±2
   - Don't force trades
   - Quality over quantity

---

## 📚 Further Learning

### Recommended Topics

1. **Cointegration**: Statistical test for pairs trading
2. **Kalman Filters**: Dynamic hedge ratio estimation
3. **Half-life**: How fast spreads revert
4. **Ornstein-Uhlenbeck Process**: Mathematical model for mean reversion

### Resources

- "Algorithmic Trading" by Ernest Chan
- "Quantitative Trading" by Ernest Chan
- "Pairs Trading: Quantitative Methods and Analysis" by Ganapathy Vidyamurthy

---

## ⚡ Quick Reference Card

```
┌─────────────────────────────────────────┐
│  PAIRS TRADING QUICK REFERENCE          │
├─────────────────────────────────────────┤
│  Z-Score < -2  →  BUY BTC, SELL ETH    │
│  Z-Score > +2  →  SELL BTC, BUY ETH    │
│  Z-Score -1 to +1  →  NO ACTION        │
├─────────────────────────────────────────┤
│  Position Size = Risk / (2 × Std Dev)   │
│  Stop Loss = Entry Z ± 1 std dev        │
│  Target = Z-score returns to 0          │
└─────────────────────────────────────────┘
```

---

**Remember**: This platform provides the data and signals. **You** make the final trading decision based on your risk tolerance, market conditions, and trading plan.

**Trade responsibly. Never invest more than you can afford to lose.**
