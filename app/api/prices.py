from typing import List
from models import Strategy

# todo: do something about the indicators
def ema():
    pass


class DoublingStrategy(Strategy):
    def __init__(
        self,
        stop_loss: int,
        take_profit: int,
        quantity: int,
        position_multiplier: float,
        series: str = "close",
    ) -> None:
        super().__init__(stop_loss, take_profit, quantity)
        self.position_multiplier = position_multiplier
        self.series_choice = {
            "open": 1,
            "close": 2,
            "low": 3,
            "high": 4,
            "volume": 5,
        }
        self.series = self.series_choice[series]

    def init_long_condition(self, price:int, ema:List[float]):
        if ema[-1]>=price and ema[-2]< price:
            return 1 # crossover
        return 0
    
    def init_short_condition(self):
        return super().init_short_condition()

    def 