class TokenContract:

    def __init__(self, name, symbol, total_supply):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.balances = {}

    def deploy(self, owner):
        self.balances[owner] = self.total_supply

    def balance_of(self, address):
        return self.balances.get(address, 0)

    def transfer(self, sender, receiver, amount):

        if self.balance_of(sender) < amount:
            return False

        self.balances[sender] -= amount
        self.balances[receiver] = self.balance_of(receiver) + amount

        return True