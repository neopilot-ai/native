from core.thought_engine.feedback_loop import multi_agent_feedback


def test_multi_agent_feedback():
    thinklets = [
        "Add input validation.",
        "Optimize the loop.",
        "Check for null values.",
    ]
    feedback = multi_agent_feedback(thinklets)
    assert len(feedback) == 3
    for f, t in zip(feedback, thinklets):
        assert f["original"] == t
        assert f["critic"].startswith("[Critic]")
        assert f["optimizer"].startswith("[Optimizer]")
        assert f["verifier"].startswith("[Verifier]")


if __name__ == "__main__":
    test_multi_agent_feedback()
    print("All feedback_loop tests passed.")
