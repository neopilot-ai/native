from core.meta_prompting.self_reflection import self_reflect

def test_actionable():
    response = "You should refactor this function to improve readability."
    result = self_reflect(response)
    assert result["scores"]["usefulness"] == 2
    assert "Actionable" in result["comments"]["usefulness"]

def test_unprofessional_tone():
    response = "This is a dumb way to do it."
    result = self_reflect(response)
    assert result["scores"]["tone"] == 1
    assert "Unprofessional" in result["comments"]["tone"]

def test_logical_consistency():
    response = "This approach works. However, it might fail in production."
    result = self_reflect(response)
    assert result["scores"]["logical_consistency"] == 1
    assert "contradiction" in result["comments"]["logical_consistency"].lower()

def test_perfect_response():
    response = "I recommend adding tests. This will improve reliability."
    result = self_reflect(response)
    assert all(score == 2 for score in result["scores"].values())

if __name__ == "__main__":
    test_actionable()
    test_unprofessional_tone()
    test_logical_consistency()
    test_perfect_response()
    print("All self_reflection tests passed.") 