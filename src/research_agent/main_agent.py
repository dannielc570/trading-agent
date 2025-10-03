"""Main Research Agent - The orchestrator brain

This is the main autonomous agent that:
- Sets and tracks goals
- Makes decisions on what to do next
- Coordinates all sub-modules
- Learns from results
- Continuously improves the platform 24/7
"""

from typing import Dict, Any, List
from datetime import datetime
from loguru import logger

from .knowledge_base import KnowledgeBase
from .strategy_discoverer import StrategyDiscoverer
from .improvement_engine import ImprovementEngine


class ResearchAgent:
    """The main autonomous research agent"""
    
    def __init__(self):
        print("[ResearchAgent] Initializing knowledge base...", flush=True)
        self.knowledge = KnowledgeBase()
        print("[ResearchAgent] ✅ Knowledge base OK", flush=True)
        
        print("[ResearchAgent] Initializing discoverer...", flush=True)
        self.discoverer = StrategyDiscoverer()
        print("[ResearchAgent] ✅ Discoverer OK", flush=True)
        
        print("[ResearchAgent] Initializing improver...", flush=True)
        self.improver = ImprovementEngine()
        print("[ResearchAgent] ✅ Improver OK", flush=True)
        
        # Agent goals and config
        self.goals = {
            'target_strategies': 50,  # Aim for 50+ strategies
            'target_assets': 30,      # Test across 30+ assets
            'target_sharpe': 2.0,     # Find strategies with Sharpe > 2.0
            'min_tests_per_strategy': 5,  # Test each strategy on 5+ assets
        }
        
        self.config = {
            'discovery_frequency': 'every_cycle',  # How often to search for new strategies
            'optimization_threshold': 0.5,  # Optimize if Sharpe < 0.5
            'max_actions_per_cycle': 10,  # Maximum actions in one cycle
        }
        
        self.state = {
            'cycles_run': 0,
            'total_strategies_added': 0,
            'total_tests_run': 0,
            'total_optimizations': 0,
            'best_sharpe_found': 0.0,
            'last_run': None
        }
        
        logger.info("🤖 Research Agent initialized")
    
    def save_strategy(self, strategy_data: Dict[str, Any]) -> int:
        """Save a discovered strategy to the database"""
        from ..database import get_db_context, Strategy
        
        try:
            with get_db_context() as db:
                # Check if strategy already exists
                existing = db.query(Strategy).filter(
                    Strategy.name == strategy_data['name']
                ).first()
                
                if existing:
                    logger.info(f"Strategy '{strategy_data['name']}' already exists (ID: {existing.id})")
                    return existing.id
                
                # Create new strategy
                strategy = Strategy(
                    name=strategy_data['name'],
                    description=strategy_data.get('description', '')[:500],  # Limit description
                    category=strategy_data.get('category', 'discovered'),
                    code=strategy_data.get('code', '# Strategy code'),
                    parameters=strategy_data.get('parameters', {}),
                    source_url=strategy_data.get('source_url'),
                    status='discovered'
                )
                
                db.add(strategy)
                db.commit()
                db.refresh(strategy)
                
                logger.success(f"✅ Saved NEW strategy: {strategy.name} (ID: {strategy.id})")
                return strategy.id
        except Exception as e:
            logger.error(f"❌ Failed to save strategy '{strategy_data.get('name', 'unknown')}': {e}")
            return 0
    
    def evaluate_current_state(self) -> Dict[str, Any]:
        """Evaluate current platform state against goals"""
        logger.info("📊 Evaluating current state...")
        
        performance = self.knowledge.get_performance_summary()
        best_strategies = self.knowledge.get_best_strategies(limit=10)
        best_assets = self.knowledge.get_best_assets(limit=10)
        
        evaluation = {
            'performance': performance,
            'best_strategies': best_strategies,
            'best_assets': best_assets,
            'goal_progress': {
                'strategies': {
                    'current': performance['total_strategies'],
                    'target': self.goals['target_strategies'],
                    'progress': (performance['total_strategies'] / self.goals['target_strategies']) * 100
                },
                'sharpe': {
                    'current_best': performance['max_sharpe'],
                    'target': self.goals['target_sharpe'],
                    'achieved': performance['max_sharpe'] >= self.goals['target_sharpe']
                },
                'tests': {
                    'total_backtests': performance['total_backtests']
                }
            }
        }
        
        logger.info(f"📈 Progress: {evaluation['goal_progress']['strategies']['progress']:.1f}% of strategy goal")
        logger.info(f"🎯 Best Sharpe: {performance['max_sharpe']:.2f} (target: {self.goals['target_sharpe']})")
        
        return evaluation
    
    def decide_next_actions(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decide what actions to take next based on current state"""
        logger.info("🧠 Deciding next actions...")
        
        actions = []
        performance = evaluation['performance']
        progress = evaluation['goal_progress']
        
        # Priority 1: If we're far from strategy goal, focus on discovery
        if progress['strategies']['progress'] < 50:
            actions.append({
                'type': 'discovery',
                'priority': 'high',
                'reason': 'Need more strategies to reach goal'
            })
        
        # Priority 2: If best Sharpe is below target, focus on optimization
        if not progress['sharpe']['achieved']:
            actions.append({
                'type': 'optimization',
                'priority': 'high',
                'reason': f"Best Sharpe ({performance['max_sharpe']:.2f}) below target ({self.goals['target_sharpe']})"
            })
        
        # Priority 3: If we have strategies but few tests, expand testing
        if performance['total_strategies'] > 0 and performance['total_backtests'] < (performance['total_strategies'] * 3):
            actions.append({
                'type': 'testing',
                'priority': 'high',
                'reason': 'Need more tests across different assets'
            })
        
        # Priority 4: Always do some discovery for continuous improvement
        actions.append({
            'type': 'discovery',
            'priority': 'medium',
            'reason': 'Continuous knowledge expansion'
        })
        
        # Priority 5: Periodic optimization of existing strategies
        actions.append({
            'type': 'improvement',
            'priority': 'medium',
            'reason': 'Optimize existing strategies'
        })
        
        logger.info(f"📋 Planned {len(actions)} actions")
        return actions
    
    async def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action with timeout handling"""
        action_type = action['type']
        logger.info(f"⚡ Executing action: {action_type} ({action['priority']} priority)")
        
        result = {'action': action_type, 'success': False}
        
        # Timeout for actions (5 minutes max)
        action_timeout = 300
        
        try:
            # Wrap action execution with timeout
            result_data = await asyncio.wait_for(
                self._execute_action_internal(action),
                timeout=action_timeout
            )
            result.update(result_data)
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Action {action_type} timed out after {action_timeout}s")
            result['error'] = f'timeout after {action_timeout}s'
            result['success'] = False
        except Exception as e:
            logger.error(f"❌ Action {action_type} failed: {e}")
            result['error'] = str(e)
        
        return result
    
    async def _execute_action_internal(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Internal action execution (called with timeout)"""
        action_type = action['type']
        result = {'action': action_type, 'success': False}
        
        try:
            if action_type == 'discovery':
                # Use discover_strategies (async) instead of run_discovery_cycle (sync)
                new_strategies = await self.discoverer.discover_strategies(max_results=10)
                
                # Save discovered strategies to database
                strategies_created = 0
                for strategy_data in new_strategies:
                    strategy_id = self.save_strategy(strategy_data)
                    if strategy_id:
                        strategies_created += 1
                
                result['success'] = True
                result['details'] = {'strategies_created': strategies_created, 'total_found': len(new_strategies)}
                self.state['total_strategies_added'] += strategies_created
                
                logger.info(f"✅ Discovery: Created {strategies_created} strategies from {len(new_strategies)} found")
            
            elif action_type == 'optimization' or action_type == 'improvement':
                improvement_result = await self.improver.run_improvement_cycle()
                result['success'] = True
                result['details'] = improvement_result
                self.state['total_optimizations'] += improvement_result.get('optimizations_run', 0)
                self.state['total_tests_run'] += improvement_result.get('new_tests', 0)
            
            elif action_type == 'testing':
                # Get untested combinations and test them on ALL TIMEFRAMES
                untested = self.knowledge.get_untested_combinations()
                tests_run = 0
                
                for combo in untested[:3]:  # Test up to 3 assets (each across 8 timeframes = 24 tests)
                    multi_tf_result = await self.improver.test_on_multiple_timeframes(
                        strategy_id=combo['strategy_id'],
                        asset=combo['asset']
                    )
                    tests_run += multi_tf_result['tests_completed']
                
                result['success'] = True
                result['details'] = {'tests_run': tests_run}
                self.state['total_tests_run'] += tests_run
            
            logger.info(f"✅ Action {action_type} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Action {action_type} failed: {e}")
            result['error'] = str(e)
        
        return result
    
    async def run_cycle(self) -> Dict[str, Any]:
        """Run one complete research cycle"""
        cycle_start = datetime.utcnow()
        self.state['cycles_run'] += 1
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🤖 RESEARCH AGENT CYCLE #{self.state['cycles_run']} STARTED")
        logger.info(f"{'='*70}\n")
        
        cycle_results = {
            'cycle_number': self.state['cycles_run'],
            'started_at': cycle_start,
            'actions_executed': [],
            'insights': [],
            'errors': []
        }
        
        try:
            # Step 1: Evaluate current state
            evaluation = self.evaluate_current_state()
            cycle_results['evaluation'] = evaluation
            
            # Step 2: Decide what to do
            actions = self.decide_next_actions(evaluation)
            cycle_results['planned_actions'] = actions
            
            # Step 3: Execute actions
            for action in actions[:self.config['max_actions_per_cycle']]:
                result = await self.execute_action(action)
                cycle_results['actions_executed'].append(result)
                
                if not result['success']:
                    cycle_results['errors'].append(result.get('error', 'Unknown error'))
            
            # Step 4: Generate insights
            insights = self._generate_insights(evaluation, cycle_results)
            cycle_results['insights'] = insights
            
            # Step 5: Update best results
            if evaluation['performance']['max_sharpe'] > self.state['best_sharpe_found']:
                self.state['best_sharpe_found'] = evaluation['performance']['max_sharpe']
                self.knowledge.log_insight(
                    f"New best Sharpe ratio found: {self.state['best_sharpe_found']:.2f}",
                    category='achievement'
                )
            
            # Update state
            self.state['last_run'] = datetime.utcnow()
            cycle_results['completed_at'] = self.state['last_run']
            cycle_results['duration_seconds'] = (self.state['last_run'] - cycle_start).total_seconds()
            
            logger.info(f"\n{'='*70}")
            logger.info(f"✅ RESEARCH AGENT CYCLE #{self.state['cycles_run']} COMPLETED")
            logger.info(f"Duration: {cycle_results['duration_seconds']:.1f}s")
            logger.info(f"Actions: {len(cycle_results['actions_executed'])}")
            logger.info(f"Insights: {len(insights)}")
            logger.info(f"{'='*70}\n")
            
        except Exception as e:
            logger.error(f"❌ Cycle failed: {e}")
            cycle_results['errors'].append(str(e))
        
        return cycle_results
    
    def _generate_insights(self, evaluation: Dict[str, Any], 
                          cycle_results: Dict[str, Any]) -> List[str]:
        """Generate insights from the cycle results"""
        insights = []
        
        performance = evaluation['performance']
        
        # Insight 1: Progress towards goals
        progress = evaluation['goal_progress']['strategies']['progress']
        if progress < 25:
            insights.append(f"⚠️  Low strategy count ({performance['total_strategies']}). Increasing discovery efforts.")
        elif progress > 75:
            insights.append(f"✅ Good strategy diversity ({performance['total_strategies']} strategies).")
        
        # Insight 2: Performance quality
        if performance['avg_sharpe'] > 1.0:
            insights.append(f"🎯 Strong average performance (Sharpe: {performance['avg_sharpe']:.2f})")
        elif performance['avg_sharpe'] < 0.3:
            insights.append(f"⚠️  Low average Sharpe ({performance['avg_sharpe']:.2f}). More optimization needed.")
        
        # Insight 3: Best performers
        best_strats = evaluation.get('best_strategies', [])
        if best_strats:
            top = best_strats[0]
            insights.append(f"🏆 Top strategy: {top['name']} (Sharpe: {top['avg_sharpe']:.2f})")
        
        # Insight 4: Asset performance
        best_assets = evaluation.get('best_assets', [])
        if best_assets:
            top_asset = best_assets[0]
            insights.append(f"💎 Best asset: {top_asset['symbol']} (Sharpe: {top_asset['avg_sharpe']:.2f})")
        
        # Insight 5: Actions summary
        actions_count = len(cycle_results['actions_executed'])
        insights.append(f"📊 Executed {actions_count} improvement actions this cycle")
        
        # Log all insights
        for insight in insights:
            self.knowledge.log_insight(insight)
        
        return insights
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get a comprehensive status report"""
        evaluation = self.evaluate_current_state()
        
        return {
            'agent_state': self.state,
            'goals': self.goals,
            'current_evaluation': evaluation,
            'next_actions': self.decide_next_actions(evaluation)
        }
    
    async def run_forever(self, interval_seconds: int = 3600):
        """Run the agent continuously (for production)"""
        import asyncio
        
        logger.info(f"🚀 Starting continuous operation (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.run_cycle()
                logger.info(f"😴 Sleeping for {interval_seconds}s...")
                await asyncio.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("🛑 Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Cycle error: {e}")
                logger.info(f"⏳ Waiting {interval_seconds}s before retry...")
                await asyncio.sleep(interval_seconds)
