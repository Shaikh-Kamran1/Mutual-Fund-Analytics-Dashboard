import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Load dataset
df = pd.read_csv('mutual_funds_dataset.csv')

# Convert date columns to datetime
df['signup_date'] = pd.to_datetime(df['signup_date'])
df['fund_viewed_date'] = pd.to_datetime(df['fund_viewed_date'])
df['purchase_date'] = pd.to_datetime(df['purchase_date'])

print("=" * 70)
print("MUTUAL FUND ANALYTICS DASHBOARD - AUGUST 2026")
print("=" * 70)

# ============ METRICS ============
total_signups = len(df)
total_viewed = len(df[df['fund_viewed_date'].notna()])
total_purchased = len(df[df['purchase_date'].notna()])
active_users = len(df[df['status'] == 'Active'])
total_aum = df['purchase_amount'].sum()
avg_roi = df['roi_percent'].mean()

print(f"\n📊 KEY METRICS:")
print(f"Total Signups:          {total_signups}")
print(f"Viewed Funds:           {total_viewed} ({(total_viewed/total_signups)*100:.1f}%)")
print(f"Purchased Funds:        {total_purchased} ({(total_purchased/total_signups)*100:.1f}%)")
print(f"Active Investors:       {active_users} ({(active_users/total_signups)*100:.1f}%)")
print(f"Total AUM:              ₹{total_aum:,.0f}")
print(f"Average ROI:            {avg_roi:.2f}%")

# ============ CREATE SUBPLOTS ============
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        'User Conversion Funnel',
        'Fund Category Performance',
        'User Segmentation by Investment',
        'Retention vs Churn',
        'Top 10 Performing Funds',
        'Weekly Signup Trend'
    ),
    specs=[
        [{"type": "funnel"}, {"type": "bar"}],
        [{"type": "bar"}, {"type": "pie"}],
        [{"type": "bar"}, {"type": "scatter"}]
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.15,
    row_heights=[0.33, 0.33, 0.34]
)

# ============ SUBPLOT 1: FUNNEL ============
funnel_stages = ['Signup', 'Viewed Fund', 'Purchased', 'Active']
funnel_values = [total_signups, total_viewed, total_purchased, active_users]

fig.add_trace(
    go.Funnel(
        x=funnel_values,
        y=funnel_stages,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]},
        name="Funnel"
    ),
    row=1, col=1
)

# ============ SUBPLOT 2: FUND CATEGORY ============
category_stats = df.groupby('fund_category').agg({
    'roi_percent': 'mean'
}).round(2).sort_values('roi_percent', ascending=False)

fig.add_trace(
    go.Bar(
        x=category_stats.index,
        y=category_stats['roi_percent'],
        marker_color='#2ecc71',
        name='Avg ROI %',
        text=category_stats['roi_percent'].values,
        textposition='auto'
    ),
    row=1, col=2
)

# ============ SUBPLOT 3: SEGMENTATION ============
df['investment_segment'] = pd.cut(df['purchase_amount'], 
                                   bins=[0, 10000, 20000, 30000, 50000],
                                   labels=['Low\n(0-10K)', 'Medium\n(10-20K)', 
                                          'High\n(20-30K)', 'Very High\n(30K+)'])

segment_counts = df['investment_segment'].value_counts().sort_index()

fig.add_trace(
    go.Bar(
        x=segment_counts.index,
        y=segment_counts.values,
        marker_color='#3498db',
        name='User Count',
        text=segment_counts.values,
        textposition='auto'
    ),
    row=2, col=1
)

# ============ SUBPLOT 4: RETENTION PIE ============
active_count = (df['status'] == 'Active').sum()
inactive_count = (df['status'] == 'Inactive').sum()

fig.add_trace(
    go.Pie(
        labels=['Active', 'Churned'],
        values=[active_count, inactive_count],
        marker={"colors": ["#27ae60", "#e74c3c"]},
        name="Retention"
    ),
    row=2, col=2
)

# ============ SUBPLOT 5: TOP FUNDS ============
top_funds = df.groupby('fund_name').agg({
    'roi_percent': 'mean'
}).round(2).sort_values('roi_percent', ascending=True).tail(10)

fig.add_trace(
    go.Bar(
        y=top_funds.index,
        x=top_funds['roi_percent'],
        orientation='h',
        marker_color='#9b59b6',
        name='Avg ROI %',
        text=top_funds['roi_percent'].values,
        textposition='auto'
    ),
    row=3, col=1
)

# ============ SUBPLOT 6: SIGNUP TREND ============
df['signup_week'] = df['signup_date'].dt.to_period('W')
signup_trend = df.groupby('signup_week').size()
signup_trend_df = signup_trend.reset_index()
signup_trend_df.columns = ['Week', 'Signups']
signup_trend_df['Week'] = signup_trend_df['Week'].astype(str)

fig.add_trace(
    go.Scatter(
        x=signup_trend_df['Week'],
        y=signup_trend_df['Signups'],
        mode='lines+markers',
        line=dict(color='#e67e22', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        name='Weekly Signups'
    ),
    row=3, col=2
)

# ============ UPDATE LAYOUT ============
fig.update_xaxes(title_text="Signup Stage", row=1, col=1)
fig.update_xaxes(title_text="Fund Category", row=1, col=2)
fig.update_xaxes(title_text="Investment Segment", row=2, col=1)
fig.update_xaxes(title_text="ROI %", row=3, col=1)
fig.update_xaxes(title_text="Week", row=3, col=2)

fig.update_yaxes(title_text="Count", row=1, col=2)
fig.update_yaxes(title_text="User Count", row=2, col=1)
fig.update_yaxes(title_text="Fund Name", row=3, col=1)
fig.update_yaxes(title_text="Signups", row=3, col=2)

fig.update_layout(
    title_text="<b>Mutual Fund Analytics Dashboard - August 2026</b><br><sub>Investor Behavior | Product Metrics | Revenue Analysis</sub>",
    title_x=0.5,
    title_font_size=20,
    height=1200,
    showlegend=False,
    plot_bgcolor='rgba(240,240,240,0.5)',
    paper_bgcolor='white',
    font=dict(family="Arial, sans-serif", size=11)
)

fig.write_html('dashboard.html')
print("\n✅ Dashboard created: dashboard.html")
print("=" * 70)

# ============ INSIGHTS PRINTOUT ============
print("\n📈 KEY INSIGHTS:")
print("-" * 70)

churned_users = df[df['status'] == 'Inactive']
avg_holding_churned = churned_users['holding_days'].mean()
churn_rate = (inactive_count / len(df)) * 100

print(f"\n🔴 CHURN ANALYSIS:")
print(f"   Churn Rate: {churn_rate:.1f}%")
print(f"   Avg holding before churn: {avg_holding_churned:.1f} days")
print(f"   → RECOMMENDATION: Re-engagement at day 15-18")

best_category = category_stats.index[0]
best_roi = category_stats.iloc[0].values[0]
print(f"\n✅ BEST CATEGORY:")
print(f"   {best_category}: {best_roi:.2f}% avg ROI")
print(f"   → RECOMMENDATION: Feature in onboarding")

high_segment = df[df['investment_segment'] == 'Very High (30K+)']
if len(high_segment) > 0:
    high_retention = (high_segment['status']=='Active').sum() / len(high_segment) * 100
    print(f"\n💰 HIGH-VALUE INVESTORS:")
    print(f"   Count: {len(high_segment)} users invested 30K+")
    print(f"   Retention: {high_retention:.1f}%")
    print(f"   → RECOMMENDATION: VIP loyalty program")

print(f"\n💵 REVENUE METRICS:")
print(f"   Total AUM: ₹{total_aum:,.0f}")
print(f"   Avg Investment: ₹{df['purchase_amount'].mean():,.0f}")
print(f"   Avg ROI: {avg_roi:.2f}%")

print("\n" + "=" * 70)
print("Open dashboard.html in browser to see interactive charts!")
print("=" * 70)