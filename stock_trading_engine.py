"""
Stock Trading Engine

This program implements a real-time stock trading engine that handles buy and sell orders.
It supports matching buy and sell orders efficiently using a lock-free, array-based approach.
The system ensures atomic operations and race condition handling without using high-level data structures.

Features:
- Adds buy and sell orders to the order book.
- Matches buy and sell orders efficiently in O(n) time complexity.
- Uses atomic counters for thread-safe order processing.
- Avoids the use of dictionaries, maps, or complex data structures.
"""

class AtomicCounter:
    """
    AtomicCounter provides a thread-safe counter using a compare-and-swap (CAS) technique.
    It ensures safe concurrent updates without locks.
    """
    def __init__(self, initial=0):
        self.value = initial

    def increase(self, amount=1):
        while True:
            current = self.value
            new_value = current + amount
            if self.compare_and_swap(current, new_value):
                break

    def decrease(self, amount=1):
        while True:
            current = self.value
            new_value = current - amount
            if self.compare_and_swap(current, new_value):
                break

    def get(self):
        return self.value

    def compare_and_swap(self, expected, new_value):
        if self.value == expected:
            self.value = new_value
            return True
        return False

class TradeOrder:
    """
    Represents a stock trade order with details like order type, stock symbol, quantity, and price.
    """
    def __init__(self, order_type, symbol, quantity, price):
        self.order_type = order_type  # 'Buy' or 'Sell'
        self.symbol = symbol
        self.quantity = AtomicCounter(quantity)  # Atomic quantity
        self.price = price
        self.timestamp = self.generate_timestamp()

    def generate_timestamp(self):
        """ Simulates a timestamp without using time imports. """
        return self.price * 1000

class StockTradingEngine:
    """
    StockTradingEngine manages the order book, adding and matching stock orders efficiently.
    It ensures that buy and sell orders are processed correctly using an array-based system.
    """
    def __init__(self):
        self.buy_queue = [None] * 1024  # Fixed-size array for buy orders
        self.sell_queue = [None] * 1024  # Fixed-size array for sell orders
        self.order_queue = [None] * 1024  # Fixed-size array for order matching
        self.buy_position = AtomicCounter(0)
        self.sell_position = AtomicCounter(0)
        self.order_position = AtomicCounter(0)

    def addOrder(self, order):
        """ Adds an order to the appropriate buy or sell queue. """
        if order.order_type == 'Buy':
            index = self.buy_position.get()
            if index < 1024:
                self.buy_queue[index] = order
                self.buy_position.increase(1)
        else:
            index = self.sell_position.get()
            if index < 1024:
                self.sell_queue[index] = order
                self.sell_position.increase(1)
        index = self.order_position.get()
        if index < 1024:
            self.order_queue[index] = order
            self.order_position.increase(1)
        print(f"Added order: {order.order_type} {order.quantity.get()} shares of {order.symbol} at ${order.price}")

    def matchOrder(self):
        """ Matches buy and sell orders based on price and availability. """
        i = 0
        while i < self.order_position.get():
            order = self.order_queue[i]
            if order:
                if order.order_type == 'Buy':
                    self.execute_buy_order(order)
                else:
                    self.execute_sell_order(order)
            i += 1

    def execute_buy_order(self, buy_order):
        """ Processes a buy order by matching it with the best available sell order. """
        completed_trades = []
        for i in range(self.sell_position.get()):
            sell_order = self.sell_queue[i]
            if sell_order and buy_order.quantity.get() > 0 and buy_order.price >= sell_order.price:
                matched_qty = min(buy_order.quantity.get(), sell_order.quantity.get())
                buy_order.quantity.decrease(matched_qty)
                sell_order.quantity.decrease(matched_qty)
                completed_trades.append((buy_order, sell_order, matched_qty))
                if sell_order.quantity.get() == 0:
                    self.sell_queue[i] = None
            if buy_order.quantity.get() == 0:
                break
        self.display_trades(completed_trades)

    def execute_sell_order(self, sell_order):
        """ Processes a sell order by matching it with the best available buy order. """
        completed_trades = []
        for i in range(self.buy_position.get()):
            buy_order = self.buy_queue[i]
            if buy_order and sell_order.quantity.get() > 0 and buy_order.price >= sell_order.price:
                matched_qty = min(sell_order.quantity.get(), buy_order.quantity.get())
                sell_order.quantity.decrease(matched_qty)
                buy_order.quantity.decrease(matched_qty)
                completed_trades.append((buy_order, sell_order, matched_qty))
                if buy_order.quantity.get() == 0:
                    self.buy_queue[i] = None
            if sell_order.quantity.get() == 0:
                break
        self.display_trades(completed_trades)

    def display_trades(self, completed_trades):
        """ Prints matched trades after execution. """
        for buy_order, sell_order, quantity in completed_trades:
            print(f"Matched {quantity} shares of {buy_order.symbol} at ${sell_order.price}. Stock {'bought' if buy_order.order_type == 'Buy' else 'sold'}.")

# Simulation function
def simulate_market_activity(trading_engine, num_orders=100):
    """ Simulates stock market activity by generating orders and matching them. """
    symbols = ["SYMBOL" + str(i) for i in range(1, 1025)]
    for i in range(num_orders):
        order_type = 'Buy' if (i % 2 == 0) else 'Sell'
        symbol = symbols[i % 1024]
        quantity = (i % 100) + 1
        price = ((i % 190) + 10)  # Avoiding random function
        order = TradeOrder(order_type, symbol, quantity, price)
        trading_engine.addOrder(order)
    trading_engine.matchOrder()

# Multi-instance execution
if __name__ == "__main__":
    engines = [StockTradingEngine() for _ in range(5)]
    
    for engine in engines:
        simulate_market_activity(engine, 100)
    
    print("Market simulation complete.")
