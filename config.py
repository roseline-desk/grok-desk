from datetime import datetime

DEFAULTS = {
    "scanner.min_liquidity_usd": 40000,
    "scanner.max_top10_pct": 25,
    "scanner.max_h1_change_pct": 80,
    "scanner.poll_s": 60,
    "scanner.min_pool_age_min": 10,
    "scanner.max_wait_min": 60,
    "scanner.runner_h24_pct": 300,
    "auditor.enabled": True,
    "auditor.max_dev_pct": 5,
    "auditor.max_top10_pct": 25,
    "auditor.min_lp_locked_pct": 99,
    "auditor.min_pool_age_min": 10,
    "auditor.max_bundled": 5,
    "auditor.max_delegated_accounts": 10,
    "auditor.retries": 3,
    "analyst.mode": "jev",
    "analyst.min_alive_6h": 0.70,
    "analyst.min_organic": 0.65,
    "analyst.max_chase": 0.30,
    "analyst.min_score": 70,
    "analyst.timeout_s": 10,
    "executor.stack_pct": 8,
    "executor.max_pool_pct": 2,
    "executor.min_ticket_usd": 47.50,
    "executor.below_min": "bump",
    "risk.poll_s": 15,
    "risk.stop_pct": 6,
    "risk.trail_start_pct": 20,
    "risk.trail_pct": 12,
    "risk.timeout_h": 3,
    "desk.mode": "PAPER",
    "desk.paper_start_stack": 200,
    "desk.fomo_handle": "skylinerya",
}

class Settings:
    def __init__(self):
        self.values = DEFAULTS.copy()

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value, who="system"):
        self.values[key] = value

settings = Settings()
