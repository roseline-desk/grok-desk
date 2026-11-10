# config.py — settings with defaults (STEP 10), validation, change log
from pathlib import Path
import json
from datetime import datetime

DEFAULTS = {
    # scanner
    "scanner.min_liquidity_usd": 40000,
    "scanner.max_top10_pct": 25,
    "scanner.max_h1_change_pct": 80,
    "scanner.poll_s": 60,
    "scanner.min_pool_age_min": 10,
    "scanner.max_wait_min": 60,
    "scanner.runner_h24_pct": 300,
    # auditor
    "auditor.enabled": True,
    "auditor.max_dev_pct": 5,
    "auditor.max_top10_pct": 25,
    "auditor.min_lp_locked_pct": 99,
    "auditor.min_pool_age_min": 10,
    "auditor.max_bundled": 5,
    "auditor.max_delegated_accounts": 10,
    "auditor.retries": 3,
    # analyst
    "analyst.mode": "jev",
    "analyst.min_alive_6h": 0.70,
    "analyst.min_organic": 0.65,
    "analyst.max_chase": 0.30,
    "analyst.min_score": 70,
    "analyst.timeout_s": 10,
    "analyst.rules.alive_volume_h1": 25000,
    "analyst.rules.organic_buys_h1": 150,
    "analyst.rules.bundled_penalty": 0.5,
    "analyst.rules.flush_drop_m5_pct": 5,
    "analyst.rules.chase_h1_pct": 80,
    # executor
    "executor.stack_pct": 8,
    "executor.max_pool_pct": 2,
    "executor.min_ticket_usd": 47.50,
    "executor.below_min": "bump",
    "executor.recheck_liq_drop_pct": 20,
    "executor.recheck_price_up_pct": 15,
    "executor.confirm_window_min": 5,
    # risk
    "risk.poll_s": 15,
    "risk.stop_pct": 6,
    "risk.trail_start_pct": 20,
    "risk.trail_pct": 12,
    "risk.timeout_h": 3,
    "risk.timeout_min_gain_pct": 5,
    "risk.confirm_window_min": 2,
    # desk
    "desk.mode": "PAPER",
    "desk.paper_start_stack": 200,
    "desk.report_time": "08:00",
    "desk.notifier": "telegram",
    "desk.rpc_url": "https://api.mainnet-beta.solana.com",
    "desk.push_rejects": False,
    "desk.fees_ref_discount": 0.10,
    "desk.fomo_handle": "skylinerya",
}

RANGES = {
    "scanner.min_liquidity_usd": (1000, 1_000_000),
    "scanner.max_top10_pct": (5, 50),
    "risk.stop_pct": (1, 30),
    "risk.trail_pct": (5, 30),
    # add more as needed
}

class Settings:
    def __init__(self, db):
        self.db = db
        self.load()

    def load(self):
        self.values = DEFAULTS.copy()
        # load from db.settings later

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value, who="system"):
        if key in RANGES:
            lo, hi = RANGES[key]
            if not (lo <= float(value) <= hi):
                raise ValueError(f"{key} out of range {lo}-{hi}")
        old = self.values.get(key)
        self.values[key] = value
        # write to change_log
        print(f"setting {key}: {old} -> {value} by {who}")

settings = None  # init after db
