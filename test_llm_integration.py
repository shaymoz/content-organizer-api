import os
import sys
sys.path.append('/c/ClaudeCodeShay/content_organizer')

from app.main import classify_content_with_llm

def test_llm_function_structure():
    """Test that the LLM function is properly structured."""
    # Check that the function exists
    assert callable(classify_content_with_llm)

    # Check that we can import the OpenAI client setup
    from app.main import get_openai_client
    assert callable(get_openai_client)

    print("LLM integration structure test passed!")

if __name__ == "__main__":
    test_llm_function_structure()