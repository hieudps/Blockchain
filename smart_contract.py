class TokenContract:
    """Smart Contract mo phong token theo mo hinh account-based."""

    def __init__(self, name, symbol, total_supply, balances=None):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.balances = balances or {}

    def deploy(self, owner):
        if owner not in self.balances:
            self.balances[owner] = self.total_supply

    def balance_of(self, address):
        return float(self.balances.get(address, 0))

    def credit(self, address, amount):
        self.balances[address] = self.balance_of(address) + float(amount)

    def debit(self, address, amount):
        amount = float(amount)
        if self.balance_of(address) < amount:
            return False

        self.balances[address] = self.balance_of(address) - amount
        return True

    def transfer(self, sender, receiver, amount):
        amount = float(amount)
        if not self.debit(sender, amount):
            return False

        self.credit(receiver, amount)
        return True
