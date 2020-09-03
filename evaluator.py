"""
Evaluator calculates indicators for an alpha to evaluate alpha performance.
"""

from multiprocessing import Array, Process, Queue
import ctypes
import pickle
import numpy as np

DATES = 'dates'
PNLS = 'pnls'
POSITIONS = 'positions'
indicators_all = {}
indicators_default = []

class Evaluator:
    """
    Evaluator to run alpha evaluation indicators.
    """
    def __init__(self, indicator_names=None):
        """
        indicators: indicators to calculate.
            If indicators=None, default indicators will be calculated.
        """
        if indicator_names is None:
            self.indicators = indicators_default
        else:
            self.set_indicators(indicator_names)

    def get_indicators(self):
        """
        Return a list of current assigned indicator names.
        """
        return [indicator.__name__ for indicator in self.indicators]

    def set_indicators(self, indicator_names):
        """
        Set to-run indicators to be the given indicators.
        """
        self.indicators = []
        for indicator_name in indicator_names:
            indicator = indicators_all.get(indicator_name)
            if indicator is None:
                raise AttributeError(
                    'Indicator not found: %s' % indicator_name)
            self.indicators.append(indicator)

    def run(self, data):
        """
        Run all specified evaluation functions and return their results.

        data: a Data with fields 'pnls' and 'positions'.
                pnls: a list-like objects of floats.
                positions: a list-like of dict-like objects.
        """
        dates = [item.date for item in data]
        pnls = np.array([item.pnl for item in data])
        positions = [item.position for item in data]
        serialized = (
            lambda var: Array(ctypes.c_char, pickle.dumps(var), lock=False))
        packed = {
            DATES: serialized(dates),
            PNLS: serialized(pnls),
            POSITIONS: serialized(positions)
        }
        processes = []
        results_queue = Queue()
        for indicator in self.indicators:
            process = Process(
                target=evaluate,
                args=(results_queue, indicator),
                kwargs=packed)
            process.start()
            processes.append(process)
        for process in processes:
            process.join()
        results = {}
        while not results_queue.empty():
            indicator_name, result = results_queue.get()
            results[indicator_name] = result
        return results

def evaluate(results, indicator, **serialized):
    """
    Decode all shared variables into evalution function inputs, and return
    their results by results (a multiprocess.Queue).
    """
    results.put((indicator.__name__, indicator(**serialized)))

def get_all_indicators():
    """
    Return a list of all available built-in indicators.
    """
    return list(indicators_all.keys())

def default(func):
    """
    Set func to be a default indicators.
    """
    indicators_default.append(func)
    return func

def inputs(*needed_fields):
    """
    Decorator for eval_functions to extract their inputs from encoded data.
    Only fields in needed_fields will be decoded to improve the performance.

    All and only functions decorated by this will be considered as indicators.
    They will be registered into indicator_list for lookup.
    """
    def middle(func):
        def final(**available_fileds):
            return func(*(
                pickle.loads(available_fileds[field])
                for field in needed_fields))
        final.__name__ = func.__name__
        # register the function into indicators_all
        indicators_all[final.__name__] = final
        return final
    return middle

@default
@inputs(PNLS)
def returns(pnls):
    """
    Average annual returns
    """
    return np.mean(pnls) * 252

@default
@inputs(PNLS)
def sharpe(pnls):
    """
    Sharpe ratio
    """
    return np.mean(pnls) / np.std(pnls)

@default
@inputs(POSITIONS)
def turnover(positions):
    """
    Turnover rate
    """
    d_turnover = [] # daily turnover rate
    for position_1st, position_2nd in zip(positions[:-1], positions[1:]):
        diff2_1 = {m: position_2nd[m] for m in set(position_2nd) - set(position_1st)}
        diff1_2 = {m: position_1st[m] for m in set(position_1st) - set(position_2nd)}
        d_change = {m: abs(position_2nd[m] - position_1st[m]) for m in position_1st if m in position_2nd}
        d_change.update(diff2_1)
        d_change.update(diff1_2)
        d_turnover.append(sum(d_change.values()) / 2)
    return {'Mean': np.mean(d_turnover), 'Std': np.std(d_turnover)}
