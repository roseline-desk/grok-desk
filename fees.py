# fees.py — FOMO fee model for PAPER PnL (STEP 11)
def fomo_fee(ticket_usd: float, ref_discount: float = 0.10) -> float:
    if ticket_usd <= 47.50:
        rate = 0.02
    elif ticket_usd <= 190:
        fee = 0.95
        return fee * (1 - ref_discount)
    else:
        rate = 0.005
    fee = ticket_usd * rate
    return fee * (1 - ref_discount)
