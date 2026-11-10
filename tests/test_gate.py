# tests/test_gate.py
def test_gate(alive, organic, chase, score, expect_pass):
    passed = alive >= 0.70 and organic >= 0.65 and chase <= 0.30 and score >= 70
    assert passed == expect_pass, f"expected {expect_pass} got {passed}"

def test():
    test_gate(0.69, 0.70, 0.20, 80, False)
    test_gate(0.70, 0.64, 0.20, 80, False)
    test_gate(0.70, 0.65, 0.31, 80, False)
    test_gate(0.70, 0.65, 0.20, 69, False)
    test_gate(0.70, 0.65, 0.30, 70, True)
    print("test_gate: PASS")

if __name__ == "__main__":
    test()
