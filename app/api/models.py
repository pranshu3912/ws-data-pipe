from abc import ABC, abstractmethod

class Strategy:
    def __init__(self, stop_loss:int, take_profit:int, quantity:int) -> None:
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.quantity = quantity
        self.open_trades = 0

    @abstractmethod
    def init_long_condition(self):
        pass


    @abstractmethod
    def init_short_condition(self):
        pass


    #todo: design a better class
    @abstractmethod
    def entry(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def long_condition(self):
        pass


    @abstractmethod
    def short_condition(self):
        pass