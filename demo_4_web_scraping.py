"""
Demo 4: Continuous Web Scraping
Automatically search and scrape trading strategies from the internet
"""
import asyncio
import sys
sys.path.append('.')

from src.data_collection import WebSearcher, GenericWebScraper
from src.database import get_db_context, ScrapedContent
from datetime import datetime

async def main():
    print("\n" + "="*80)
    print("🌐 DEMO 4: AUTOMATED WEB SCRAPING FOR TRADING STRATEGIES")
    print("="*80)
    print("\nSearching the web for trading strategies and content...")
    
    # ========================================================================
    # STEP 1: Web Search
    # ========================================================================
    print("\n" + "-"*80)
    print("🔍 STEP 1: Searching for Trading Strategies")
    print("-"*80)
    
    searcher = WebSearcher()
    
    # Search for different types of strategies
    search_topics = [
        "RSI trading strategy",
        "momentum trading techniques",
        "algorithmic trading strategies",
        "day trading setup",
        "crypto trading strategies"
    ]
    
    all_results = []
    
    for topic in search_topics:
        print(f"\n   Searching: {topic}...")
        results = await searcher.search_strategies(topic, max_results=5)
        
        if results:
            print(f"   ✓ Found {len(results)} results")
            all_results.extend(results)
            
            # Show first result
            if results:
                first = results[0]
                print(f"      Example: {first['title'][:60]}...")
                print(f"               {first['url'][:70]}...")
        else:
            print(f"   ⚠️  No results found (search may be rate limited)")
    
    print(f"\n   Total results found: {len(all_results)}")
    
    # ========================================================================
    # STEP 2: Content Scraping (Demo)
    # ========================================================================
    print("\n" + "-"*80)
    print("🌐 STEP 2: Scraping Content from URLs")
    print("-"*80)
    print("\n   Note: Actual scraping may be rate-limited or blocked.")
    print("   In production, you would:")
    print("   • Use proper rate limiting")
    print("   • Respect robots.txt")
    print("   • Add delays between requests")
    print("   • Use proxies if needed")
    
    scraper = GenericWebScraper()
    scraped_count = 0
    
    # Try to scrape a few URLs (limited to avoid rate limiting in demo)
    urls_to_scrape = [r['url'] for r in all_results[:3]] if all_results else []
    
    for i, url in enumerate(urls_to_scrape, 1):
        print(f"\n   [{i}/{len(urls_to_scrape)}] Scraping: {url[:60]}...")
        
        try:
            content = await scraper.scrape(url)
            
            if content:
                print(f"      ✓ Scraped {content['word_count']} words")
                print(f"      ✓ Found {len(content['strategy_keywords'])} trading keywords")
                if content['strategy_keywords']:
                    print(f"      Keywords: {', '.join(content['strategy_keywords'][:5])}")
                scraped_count += 1
            else:
                print(f"      ⚠️  Could not scrape (may be blocked)")
        except Exception as e:
            print(f"      ✗ Error: {str(e)[:60]}")
        
        # Rate limiting
        await asyncio.sleep(2)
    
    # ========================================================================
    # STEP 3: Save to Database
    # ========================================================================
    print("\n" + "-"*80)
    print("💾 STEP 3: Saving to Database")
    print("-"*80)
    
    if all_results:
        print(f"\n   Saving {len(all_results)} search results to database...")
        
        with get_db_context() as db:
            saved = 0
            for result in all_results[:10]:  # Limit to 10 for demo
                # Check if already exists
                existing = db.query(ScrapedContent).filter(
                    ScrapedContent.source_url == result['url']
                ).first()
                
                if not existing:
                    content = ScrapedContent(
                        source_url=result['url'],
                        source_type='search_result',
                        title=result['title'],
                        content=result['snippet'],
                        extracted_data=result,
                        processed=False
                    )
                    db.add(content)
                    saved += 1
            
            db.commit()
            print(f"   ✓ Saved {saved} new items to database")
            
            # Show database stats
            total_scraped = db.query(ScrapedContent).count()
            unprocessed = db.query(ScrapedContent).filter(
                ScrapedContent.processed == False
            ).count()
            
            print(f"\n   Database Statistics:")
            print(f"   • Total scraped items: {total_scraped}")
            print(f"   • Unprocessed items: {unprocessed}")
            print(f"   • Ready for analysis: {total_scraped - unprocessed}")
    
    # ========================================================================
    # STEP 4: What's Next
    # ========================================================================
    print("\n" + "="*80)
    print("🤖 AUTOMATED SCRAPING WORKFLOW")
    print("="*80)
    
    print("\n   The platform can run continuously with the scheduler:")
    print("\n   1. 🔍 Search Phase (Every 60 minutes)")
    print("      • Search for new trading strategies")
    print("      • Find articles, tutorials, discussions")
    print("      • Discover new techniques and approaches")
    
    print("\n   2. 🌐 Scraping Phase")
    print("      • Extract full content from promising URLs")
    print("      • Parse strategy details and parameters")
    print("      • Store everything in database")
    
    print("\n   3. 🧠 Processing Phase")
    print("      • Analyze content with NLP")
    print("      • Extract strategy parameters")
    print("      • Identify testable strategies")
    
    print("\n   4. 🧪 Testing Phase")
    print("      • Convert strategies to code")
    print("      • Backtest automatically")
    print("      • Rank by performance")
    
    print("\n   5. 🎯 Optimization Phase")
    print("      • Optimize parameters")
    print("      • Test on multiple assets")
    print("      • Select best performers")
    
    print("\n" + "="*80)
    print("✅ Web Scraping Demo Complete!")
    print("="*80)
    
    print("\n💡 To Run Continuous Scraping:")
    print("   python -m src.scheduler.main")
    print("\n   This will:")
    print("   • Search every 60 minutes (configurable)")
    print("   • Scrape new content automatically")
    print("   • Store everything in database")
    print("   • Process and analyze content")
    
    print(f"\n📊 Results from this demo:")
    print(f"   • Search results found: {len(all_results)}")
    print(f"   • URLs scraped: {scraped_count}")
    print(f"   • Items saved to database: {saved if all_results else 0}")

if __name__ == "__main__":
    asyncio.run(main())
