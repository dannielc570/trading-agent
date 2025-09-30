"""Strategy parameter optimization using Optuna"""
from typing import Dict, Any, Callable, List
import optuna
from optuna.samplers import TPESampler
from loguru import logger
import pandas as pd


class StrategyOptimizer:
    """Optimize strategy parameters using Bayesian optimization"""
    
    def __init__(
        self,
        n_trials: int = 100,
        n_jobs: int = 1,
        optimization_metric: str = "sharpe_ratio"
    ):
        """
        Initialize optimizer
        
        Args:
            n_trials: Number of optimization trials
            n_jobs: Number of parallel jobs
            optimization_metric: Metric to optimize
        """
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.optimization_metric = optimization_metric
        self.study = None
    
    def optimize(
        self,
        objective_func: Callable,
        parameter_space: Dict[str, Any],
        direction: str = "maximize"
    ) -> Dict[str, Any]:
        """
        Run optimization
        
        Args:
            objective_func: Function to optimize (takes trial, returns metric)
            parameter_space: Dictionary defining parameter ranges
            direction: 'maximize' or 'minimize'
            
        Returns:
            Dictionary with best parameters and score
        """
        try:
            logger.info(f"Starting optimization with {self.n_trials} trials")
            
            # Create study
            self.study = optuna.create_study(
                direction=direction,
                sampler=TPESampler(seed=42)
            )
            
            # Run optimization
            self.study.optimize(
                objective_func,
                n_trials=self.n_trials,
                n_jobs=self.n_jobs,
                show_progress_bar=True
            )
            
            # Get results
            best_params = self.study.best_params
            best_value = self.study.best_value
            
            # Get trial history
            trials_data = []
            for trial in self.study.trials:
                trials_data.append({
                    'trial_number': trial.number,
                    'params': trial.params,
                    'value': trial.value,
                    'state': trial.state.name
                })
            
            results = {
                'best_parameters': best_params,
                'best_score': best_value,
                'n_trials': len(self.study.trials),
                'trials': trials_data
            }
            
            logger.info(f"Optimization complete. Best score: {best_value:.4f}")
            logger.info(f"Best parameters: {best_params}")
            
            return results
            
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return {'error': str(e)}
    
    def suggest_parameters(
        self,
        trial: optuna.Trial,
        parameter_space: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest parameters for a trial
        
        Args:
            trial: Optuna trial object
            parameter_space: Parameter definitions
            
        Returns:
            Dictionary of suggested parameters
        """
        params = {}
        
        for param_name, param_config in parameter_space.items():
            param_type = param_config.get('type', 'int')
            
            if param_type == 'int':
                params[param_name] = trial.suggest_int(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    step=param_config.get('step', 1)
                )
            elif param_type == 'float':
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    step=param_config.get('step', None),
                    log=param_config.get('log', False)
                )
            elif param_type == 'categorical':
                params[param_name] = trial.suggest_categorical(
                    param_name,
                    param_config['choices']
                )
        
        return params
    
    def get_optimization_history(self) -> pd.DataFrame:
        """Get optimization history as DataFrame"""
        if not self.study:
            return pd.DataFrame()
        
        trials_df = self.study.trials_dataframe()
        return trials_df
    
    def plot_optimization_history(self):
        """Plot optimization history"""
        if not self.study:
            logger.warning("No study available to plot")
            return None
        
        try:
            from optuna.visualization import plot_optimization_history, plot_param_importances
            
            fig1 = plot_optimization_history(self.study)
            fig2 = plot_param_importances(self.study)
            
            return {'history': fig1, 'importances': fig2}
        except ImportError:
            logger.warning("Optuna visualization not available")
            return None


class GridSearchOptimizer:
    """Simple grid search optimizer"""
    
    def __init__(self):
        """Initialize grid search optimizer"""
        pass
    
    def optimize(
        self,
        objective_func: Callable,
        parameter_grid: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """
        Run grid search optimization
        
        Args:
            objective_func: Function that takes params dict and returns score
            parameter_grid: Dictionary of parameter lists to try
            
        Returns:
            Best parameters and results
        """
        try:
            from itertools import product
            
            # Generate all parameter combinations
            param_names = list(parameter_grid.keys())
            param_values = list(parameter_grid.values())
            
            all_combinations = list(product(*param_values))
            
            logger.info(f"Testing {len(all_combinations)} parameter combinations")
            
            best_score = float('-inf')
            best_params = None
            all_results = []
            
            for i, combination in enumerate(all_combinations):
                params = dict(zip(param_names, combination))
                
                try:
                    score = objective_func(params)
                    all_results.append({'params': params, 'score': score})
                    
                    if score > best_score:
                        best_score = score
                        best_params = params
                        
                except Exception as e:
                    logger.warning(f"Error evaluating params {params}: {e}")
                    continue
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Completed {i + 1}/{len(all_combinations)} combinations")
            
            logger.info(f"Grid search complete. Best score: {best_score:.4f}")
            logger.info(f"Best parameters: {best_params}")
            
            return {
                'best_parameters': best_params,
                'best_score': best_score,
                'n_trials': len(all_combinations),
                'all_results': all_results
            }
            
        except Exception as e:
            logger.error(f"Grid search error: {e}")
            return {'error': str(e)}
