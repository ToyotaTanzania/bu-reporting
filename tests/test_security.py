import subprocess
import os
import tempfile


def test_env_file_gitignore():
    """Test that .env files are properly ignored by git"""
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', dir='.', delete=False) as temp_env:
        temp_env.write("TEST_SECRET=should_not_be_tracked")
        temp_env_path = temp_env.name
    
    try:
        # Check that the file is ignored
        result = subprocess.run(['git', 'status', '--porcelain', temp_env_path], 
                                capture_output=True, text=True)
        
        # If the file is properly ignored, git status should show nothing
        assert result.stdout.strip() == "", f"Temporary .env file should be ignored by git: {result.stdout}"
        
        # Also check via git check-ignore
        result = subprocess.run(['git', 'check-ignore', temp_env_path], 
                                capture_output=True, text=True)
        assert result.returncode == 0, f"File should be ignored by .gitignore: {temp_env_path}"
        
    finally:
        # Clean up
        if os.path.exists(temp_env_path):
            os.unlink(temp_env_path)


def test_env_example_tracked():
    """Test that .env.example is tracked by git"""
    # Check that .env.example is tracked
    result = subprocess.run(['git', 'ls-files', '.env.example'], 
                            capture_output=True, text=True)
    assert '.env.example' in result.stdout, ".env.example should be tracked by git"


def test_original_env_not_tracked():
    """Test that the original .env file is no longer tracked"""
    # Check that .env is not tracked
    result = subprocess.run(['git', 'ls-files', '.env'], 
                            capture_output=True, text=True)
    assert result.stdout.strip() == "", "Original .env file should not be tracked by git"