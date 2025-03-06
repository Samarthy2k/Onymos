Stock Trading Engine

This program implements a real-time stock trading engine that handles buy and sell orders.
It supports matching buy and sell orders efficiently using a lock-free, array-based approach.
The system ensures atomic operations and race condition handling without using high-level data structures.

Features:
- Adds buy and sell orders to the order book.
- Matches buy and sell orders efficiently in O(n) time complexity.
- Uses atomic counters for thread-safe order processing.
- Avoids the use of dictionaries, maps, or complex data structures.
