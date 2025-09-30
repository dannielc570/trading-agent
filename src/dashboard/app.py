"""Streamlit dashboard for monitoring"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context, Strategy, Backtest, ScrapedContent
from config import settings

st.set_page_config(
    page_title="Trading Strategy Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 2rem;
        font-weight: bold;
    }
    .status-discovered { color: #3498db; }
    .status-tested { color: #f39c12; }
    .status-optimized { color: #2ecc71; }
    .status-live { color: #e74c3c; }
</style>
""", unsafe_allow_html=True)


def load_stats():
    """Load platform statistics"""
    with get_db_context() as db:
        total_strategies = db.query(Strategy).count()
        total_backtests = db.query(Backtest).count()
        total_scraped = db.query(ScrapedContent).count()
        
        completed_backtests = db.query(Backtest).filter(
            Backtest.status == "completed"
        ).count()
        
        avg_sharpe = db.query(Backtest).filter(
            Backtest.status == "completed",
            Backtest.sharpe_ratio.isnot(None)
        ).all()
        
        avg_sharpe_value = sum(b.sharpe_ratio for b in avg_sharpe) / len(avg_sharpe) if avg_sharpe else 0
        
        return {
            "total_strategies": total_strategies,
            "total_backtests": total_backtests,
            "completed_backtests": completed_backtests,
            "total_scraped": total_scraped,
            "avg_sharpe": avg_sharpe_value
        }


def main():
    """Main dashboard"""
    st.title("📈 Trading Strategy Research Platform")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 10)
        
        st.markdown("---")
        st.header("🔍 Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("🌐 Run Web Search", use_container_width=True):
            st.info("Web search functionality - Coming soon!")
        
        if st.button("🤖 Start Scheduler", use_container_width=True):
            st.info("Scheduler functionality - Coming soon!")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💡 Strategies", "📈 Backtests", "🌐 Scraped Content"])
    
    with tab1:
        show_overview()
    
    with tab2:
        show_strategies()
    
    with tab3:
        show_backtests()
    
    with tab4:
        show_scraped_content()


def show_overview():
    """Show overview dashboard"""
    st.header("Platform Overview")
    
    # Load stats
    stats = load_stats()
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Strategies", stats["total_strategies"], delta=None)
    
    with col2:
        st.metric("Backtests", stats["total_backtests"], delta=None)
    
    with col3:
        st.metric("Completed", stats["completed_backtests"], delta=None)
    
    with col4:
        st.metric("Scraped Items", stats["total_scraped"], delta=None)
    
    with col5:
        st.metric("Avg Sharpe", f"{stats['avg_sharpe']:.2f}", delta=None)
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Strategies")
        with get_db_context() as db:
            recent_strategies = db.query(Strategy).order_by(
                Strategy.created_at.desc()
            ).limit(5).all()
            
            if recent_strategies:
                for strategy in recent_strategies:
                    with st.container():
                        st.markdown(f"**{strategy.name}**")
                        st.caption(f"Status: {strategy.status} | Created: {strategy.created_at.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.info("No strategies yet")
    
    with col2:
        st.subheader("Recent Backtests")
        with get_db_context() as db:
            recent_backtests = db.query(Backtest).order_by(
                Backtest.created_at.desc()
            ).limit(5).all()
            
            if recent_backtests:
                for backtest in recent_backtests:
                    with st.container():
                        st.markdown(f"**{backtest.symbol}** @ {backtest.timeframe}")
                        if backtest.sharpe_ratio:
                            st.caption(f"Sharpe: {backtest.sharpe_ratio:.2f} | Return: {backtest.total_return*100:.2f}%")
                        else:
                            st.caption(f"Status: {backtest.status}")
            else:
                st.info("No backtests yet")


def show_strategies():
    """Show strategies tab"""
    st.header("Trading Strategies")
    
    with get_db_context() as db:
        strategies = db.query(Strategy).all()
        
        if not strategies:
            st.info("No strategies found. Start by searching for strategies or creating a new one.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "ID": s.id,
                "Name": s.name,
                "Category": s.category or "N/A",
                "Status": s.status,
                "Created": s.created_at.strftime('%Y-%m-%d')
            }
            for s in strategies
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Details
        selected_id = st.selectbox("Select Strategy for Details", df["ID"].tolist())
        
        if selected_id:
            strategy = db.query(Strategy).filter(Strategy.id == selected_id).first()
            
            if strategy:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Details")
                    st.write(f"**Name:** {strategy.name}")
                    st.write(f"**Category:** {strategy.category or 'N/A'}")
                    st.write(f"**Status:** {strategy.status}")
                    st.write(f"**Created:** {strategy.created_at}")
                
                with col2:
                    st.subheader("Description")
                    st.write(strategy.description or "No description available")
                
                if strategy.source_url:
                    st.markdown(f"**Source:** [{strategy.source_url}]({strategy.source_url})")


def show_backtests():
    """Show backtests tab"""
    st.header("Backtest Results")
    
    with get_db_context() as db:
        backtests = db.query(Backtest).filter(
            Backtest.status == "completed"
        ).all()
        
        if not backtests:
            st.info("No completed backtests yet.")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "ID": b.id,
                "Symbol": b.symbol,
                "Timeframe": b.timeframe,
                "Total Return": f"{(b.total_return or 0) * 100:.2f}%",
                "Sharpe Ratio": f"{b.sharpe_ratio or 0:.2f}",
                "Max Drawdown": f"{(b.max_drawdown or 0) * 100:.2f}%",
                "Win Rate": f"{(b.win_rate or 0) * 100:.1f}%",
                "Trades": b.total_trades or 0,
            }
            for b in backtests
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Performance chart
        if backtests:
            st.subheader("Performance Comparison")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[f"{b.symbol} ({b.id})" for b in backtests],
                y=[b.sharpe_ratio or 0 for b in backtests],
                name="Sharpe Ratio"
            ))
            
            fig.update_layout(
                title="Sharpe Ratio by Backtest",
                xaxis_title="Backtest",
                yaxis_title="Sharpe Ratio",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)


def show_scraped_content():
    """Show scraped content tab"""
    st.header("Scraped Content")
    
    with get_db_context() as db:
        scraped = db.query(ScrapedContent).order_by(
            ScrapedContent.scraped_at.desc()
        ).limit(50).all()
        
        if not scraped:
            st.info("No scraped content yet. Start web search to collect data.")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            show_processed = st.checkbox("Show only processed", value=False)
        with col2:
            show_unprocessed = st.checkbox("Show only unprocessed", value=False)
        
        # Filter items
        filtered = scraped
        if show_processed:
            filtered = [s for s in filtered if s.processed]
        if show_unprocessed:
            filtered = [s for s in filtered if not s.processed]
        
        # Display items
        for item in filtered:
            with st.expander(f"{item.title or 'Untitled'} - {item.source_type}"):
                st.markdown(f"**URL:** [{item.source_url}]({item.source_url})")
                st.markdown(f"**Scraped:** {item.scraped_at.strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"**Processed:** {'✅' if item.processed else '❌'}")
                st.markdown(f"**Strategy Created:** {'✅' if item.strategy_created else '❌'}")
                
                if item.content:
                    st.text_area("Content Preview", item.content[:500] + "...", height=100)


if __name__ == "__main__":
    main()
