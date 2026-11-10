# tests/test_links.py
import sys
sys.path.insert(0, "..")
from links import coin_url, profile_url, SIGNUP_URL

def test():
    assert "r=savipww" in coin_url("abc")
    assert "r=savipww" in profile_url("user")
    assert coin_url("x", "unknownchain") == SIGNUP_URL
    assert "/r/savipww" in SIGNUP_URL
    print("test_links: PASS")

if __name__ == "__main__":
    test()
