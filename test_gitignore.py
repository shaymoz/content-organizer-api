import os

def test_gitignore_contents():
    """Test that .gitignore contains the required patterns."""
    gitignore_path = './.gitignore'

    with open(gitignore_path, 'r') as f:
        content = f.read()

    # Check for required patterns
    required_patterns = [
        '.env',
        '*.db',
        '*.sqlite3',
        '__pycache__/'
    ]

    print("Checking .gitignore contents...")
    all_found = True

    for pattern in required_patterns:
        if pattern in content:
            print("Found '" + pattern + "' in .gitignore")
        else:
            print("Missing '" + pattern + "' in .gitignore")
            all_found = False

    if all_found:
        print("\nAll required patterns found in .gitignore!")
    else:
        print("\nSome required patterns are missing from .gitignore!")

    return all_found

if __name__ == "__main__":
    test_gitignore_contents()