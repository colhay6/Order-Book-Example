import random

class Order(object):
    def __init__(self, type, price, quantity):
        self.type = type
        self.price = price
        self.quantity = quantity

    def __repr__(self):  
        return "{'type': '% s', 'price': % s, 'quantity': % s}" % (self.type, self.price, self.quantity)

    
class OrderBook(object):
    def __init__(self):
        self.bids = []
        self.asks = []

    def getOrderBook(self):
        return {"bids": self.bids, "asks": self.asks}
    
    def emptyOrderBook(self, order):
        if order.type == "sell":
            self.asks.append(order)
        if order.type == "buy":
            self.bids.append(order)
    
    def insert(self, order):
        is_inserted = False

        if order.type == "sell":
            for o in enumerate(self.asks):
                idx = o[0]
                curr_order = o[1]
                if order.price == curr_order.price:
                    # increase quantity
                    self.asks[idx].quantity = self.asks[idx].quantity + order.quantity
                    is_inserted = True
                    break
                if order.price < curr_order.price:
                    # insert here
                    self.asks.insert(idx, order)
                    is_inserted = True
                    break
            if not is_inserted:
                # add to end
                self.asks.append(order)

        if order.type == "buy":
            for o in enumerate(self.bids):
                idx = o[0]
                curr_order = o[1]
                if order.price == curr_order.price:
                    # increase quantity
                    self.bids[idx].quantity = self.bids[idx].quantity + order.quantity
                    is_inserted = True
                    break
                if order.price > curr_order.price:
                    # insert here
                    self.bids.insert(idx, order)
                    is_inserted = True
                    break
            if not is_inserted:
                # add to end
                self.bids.append(order)

    def transaction(self, order):
        output = []
        remaining_quantity = order.quantity

        side = self.bids if order.type == "sell" else self.asks

        while remaining_quantity > 0:
            if len(side) > 0:
                curr_order = side[0]
                is_sell_possible = order.price <= curr_order.price
                is_buy_possible = order.price >= curr_order.price
                if is_sell_possible if order.type == "sell" else is_buy_possible:
                    if remaining_quantity >= curr_order.quantity:
                        output.append([curr_order.price, curr_order.quantity])
                        removed = side.pop(0)
                        remaining_quantity = remaining_quantity - removed.quantity
                    else:
                        output.append([curr_order.price, remaining_quantity])
                        curr_order.quantity = side[0].quantity - remaining_quantity
                        remaining_quantity = 0
                else:
                    # leftover remaining, no more bids can fill, insert the order
                    order.quantity = remaining_quantity
                    remaining_quantity = 0
                    self.insert(order)
            else:
                # asks have been cleared, insert the order
                order.quantity = remaining_quantity
                remaining_quantity = 0
                self.insert(order)
        
        return output        

    def addOrder(self, order):
        order = Order(order["type"], order["price"], quantity = order["quantity"])

        output = []

        sell_min = self.asks[0].price if len(self.asks) > 0 else None
        buy_max = self.bids[0].price if len(self.bids) > 0 else None

        #if order book empty
        if sell_min == None and buy_max == None:
            self.emptyOrderBook(order)
        else:
            if (len(self.bids) == 0 and order.type == "sell") or (len(self.asks) == 0 and order.type == "buy"):
                self.insert(order)
            else:
                # possible transactions below
                if order.type == "sell":
                    if order.price > buy_max:
                        self.insert(order)
                    else:
                        output = self.transaction(order)
                if order.type == "buy":
                    if order.price < sell_min:
                        self.insert(order)
                    else:
                        output = self.transaction(order)

        if debug:
            print()
            print("------------------------------")
            print()
            print(order)
            print()
            print(output)
            print()
            print("Current OrderBook: ")
            print(self.getOrderBook())
            print()

        return output
       
      
# toggles
debug = False
test = False


start_price = 10.0
o = OrderBook()

for i in range(10):
   type = "buy" if bool(random.getrandbits(1)) else "sell"
   price = start_price+.5 if bool(random.getrandbits(1)) else start_price-.5
   quantity = round(random.uniform(0.1, 5), 1)
   newOrder = { "type": type, "price": price, "quantity": quantity }
   print()
   print(newOrder)
   print(o.addOrder(newOrder))
   start_price = price

print()
print(o.getOrderBook())


if test:
    # Test 1
    o = OrderBook()
    o.addOrder({ "type": "buy", "price": 10, "quantity": 1 })
    o.addOrder({ "type": "buy", "price": 10, "quantity": 1 })
    o.addOrder({ "type": "buy", "price": 10, "quantity": 1 })
    ob = o.getOrderBook()
    assert len(ob["bids"]) == 1 
    assert ob["bids"][0].quantity == 3

    # Test 2
    o = OrderBook()
    o.addOrder({ "type": "sell", "price": 10, "quantity": 1 })
    o.addOrder({ "type": "sell", "price": 10, "quantity": 1 })
    o.addOrder({ "type": "sell", "price": 10, "quantity": 1 })
    ob = o.getOrderBook()
    assert len(ob["asks"]) == 1 
    assert ob["asks"][0].quantity == 3

    # Test 3
    o = OrderBook()
    o.addOrder({ "type": "sell", "price": 10, "quantity": 1 })
    assert o.addOrder({ "type": "buy", "price": 10, "quantity": 1 }) == [[10, 1]]

    # Test 4
    o = OrderBook()
    o.addOrder({ "type": "buy", "price": 10, "quantity": 1 })
    assert o.addOrder({ "type": "sell", "price": 10, "quantity": 1 }) == [[10, 1]]

    # Test 5
    o = OrderBook()
    o.addOrder({ "type": "buy", "price": 10, "quantity": 1 })
    o.addOrder({ "type": "buy", "price": 9.5, "quantity": 1 })
    assert o.addOrder({ "type": "sell", "price": 10, "quantity": 2 }) == [[10, 1]]
    ob = o.getOrderBook()
    assert len(ob["asks"]) == 1
    assert len(ob["bids"]) == 1

    # Test 6
    o = OrderBook()
    o.addOrder({ "type": "sell", "price": 10, "quantity": 1 })
    o.addOrder({ "type": "sell", "price": 9.5, "quantity": 1 })
    assert o.addOrder({ "type": "buy", "price": 9.5, "quantity": 2 }) == [[9.5, 1]]
    ob = o.getOrderBook()
    assert len(ob["asks"]) == 1
    assert len(ob["bids"]) == 1

















