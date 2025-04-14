# executor.py

import subprocess
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAFE_MODE = True  # keep safe mode ON

def extract_code_blocks(text):
    """Extract code blocks from the text (inside ```python ... ``` or ```...```)"""
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return code_blocks

def execute_command(command):
    """Execute a shell command safely."""
    if SAFE_MODE:
        logger.info("⚠️  Safe mode is ON. Skipping shell command execution.")
        return "Safe mode enabled. Shell command not executed."
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def execute_plan(plan):
    """Execute a plan by running extracted code blocks."""
    logger.info("🚀 Executing the plan...")

    code_blocks = extract_code_blocks(plan)

    if not code_blocks:
        logger.error("❌ No code blocks found in the plan.")
        return "No executable code found."

    final_output = ""
    for code in code_blocks:
        try:
            logger.info(f"🧩 Running extracted code:\n{code}")
            # Save code to temp file
            with open("temp_code.py", "w") as f:
                f.write(code)
            # Run the temp file
            result = subprocess.run(["python3", "temp_code.py"], capture_output=True, text=True)
            output = result.stdout + result.stderr
            logger.info(f"✅ Execution output:\n{output}")
            final_output += output
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            final_output += f"Execution failed: {e}\n"
    return final_output
