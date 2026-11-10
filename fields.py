# fields.py — raw key mapping from STEP 2
# Agents read only through this mapping. Never guess a key.

def map_pumpportal(msg: dict) -> dict:
    return {
        "mint": msg.get("mint"),
        "pool": msg.get("pool") or msg.get("bondingCurve") or msg.get("pair"),
        "signature": msg.get("signature"),
        "creator": msg.get("creator") or msg.get("user"),
    }

def map_dex(pair: dict) -> dict:
    return {
        "pairAddress": pair.get("pairAddress"),
        "priceUsd": pair.get("priceUsd"),
        "liquidityUsd": (pair.get("liquidity") or {}).get("usd"),
        "marketCap": pair.get("marketCap"),
        "volume": pair.get("volume"),
        "txns": pair.get("txns"),
        "priceChange": pair.get("priceChange"),
        "pairCreatedAt": pair.get("pairCreatedAt"),
        "name": (pair.get("baseToken") or {}).get("name"),
        "symbol": (pair.get("baseToken") or {}).get("symbol"),
    }

def map_rugcheck_report(report: dict) -> dict:
    return {
        "creator": report.get("creator"),
        "creatorBalance": report.get("creatorBalance"),
        "mintAuthority": (report.get("token") or {}).get("mintAuthority"),
        "freezeAuthority": (report.get("token") or {}).get("freezeAuthority"),
        "topHolders": report.get("topHolders"),
        "markets": report.get("markets"),
    }

def map_rugcheck_graph(graph) -> dict:
    # graph is list or dict with nodes/edges
    return {"raw": graph}
