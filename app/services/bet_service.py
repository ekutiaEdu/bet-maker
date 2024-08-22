import decimal

class BetService:
    async def create_bet(self, stake: str) -> None:
        d = decimal.Decimal(stake)
        if d.as_tuple().exponent != -2 or d <= 0:
            raise ValueError()

