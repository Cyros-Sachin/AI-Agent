import subprocess
import os
import logging
import re
import tempfile
from typing import List, Tuple, Optional
from config import Config

# Set up logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

class PlanExecutor:
    def __init__(self):
        self.supported_languages = {
            'python': {'extension': 'py', 'command': 'python'},
            'javascript': {'extension': 'js', 'command': 'node'},
            'bash': {'extension': 'sh', 'command': 'bash'},
            'ruby': {'extension': 'rb', 'command': 'ruby'}
        }

    def _extract_code_blocks(self, plan: str) -> List[Tuple[str, str]]:
        """
        Extract only proper code blocks, ignoring command examples
        """
        pattern = r'```(?:(\w+)\n)?([\s\S]+?)```'
        matches = re.findall(pattern, plan)
        # Filter out blocks that look like commands
        return [
            (lang.lower().strip(), code.strip()) 
            for lang, code in matches 
            if code.strip() and not code.strip().startswith(('python ', 'node ', 'bash ', 'ruby '))
        ]

    def _parse_commands(self, plan: str) -> List[str]:
        """
        Parse both explicit commands and code block execution commands
        """
        commands = []
        
        # First find all command-like lines
        for line in plan.split('\n'):
            line = line.strip()
            if not line or line.startswith(('#', '//', '**', '*', 'Example', 'Explanation')):
                continue
            if line.startswith('```') and line.endswith('```'):
                continue
            
            # Add lines that look like commands
            if line.startswith(('python ', 'node ', 'bash ', 'ruby ')) or \
               (not any(line.startswith(f"{lang} ") )
                        for lang in self.supported_languages) and not re.match(r'^\w+\.\w+$', line):  # Skip things that look like file.ext
                            commands.append(line)
        
        return commands

    def _execute_code_block(self, language: str, code: str) -> bool:
        """
        Execute a code block with proper input handling
        """
        if not language:  # Default to python if no language specified
            language = 'python'
        elif language not in self.supported_languages:
            logger.error(f"Unsupported language: {language}")
            return False

        lang_config = self.supported_languages[language]
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f'.{lang_config["extension"]}',
            mode='w+',
            delete=False
        ) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        try:
            logger.info(f"🔧 Running {language} script: {temp_path}")
            
            # For Python scripts that need input
            if language == 'python' and ('input(' in code or 'sys.stdin' in code):
                inputs = ['5', '3']  # Default test inputs
                process = subprocess.Popen(
                    [lang_config['command'], temp_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate('\n'.join(inputs))
            else:
                # Regular execution
                process = subprocess.run(
                    [lang_config['command'], temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                stdout, stderr = process.stdout, process.stderr

            if process.returncode != 0:
                logger.error(f"❌ Error executing {language} script:\n{stderr}")
                return False
            
            logger.info(f"✅ {language} script output:\n{stdout}")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Script execution timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to execute {language} code: {str(e)}")
            return False
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass

    def execute_plan(self, plan: str) -> bool:
        """
        Execute the provided plan with proper command/code separation
        """
        logger.info("🚀 Executing plan...")
        
        # First handle code blocks (actual code to execute)
        code_blocks = self._extract_code_blocks(plan)
        for language, code in code_blocks:
            if not self._execute_code_block(language, code):
                return False

        # Then handle commands (like "python file.py")
        commands = self._parse_commands(plan)
        for cmd in commands:
            if not cmd:
                continue
                
            if Config.SAFE_MODE and any(word in cmd.lower() for word in ['rm', 'delete', 'format', 'dd']):
                logger.warning(f"⚠️ Skipping potentially dangerous command in safe mode: {cmd}")
                continue

            logger.info(f"🔧 Running command: {cmd}")
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode != 0:
                    logger.error(f"❌ Error executing command:\n{result.stderr}")
                    return False
                
                logger.info(f"✅ Command output:\n{result.stdout}")
                
            except subprocess.TimeoutExpired:
                logger.error("❌ Command timed out")
                return False
            except Exception as e:
                logger.error(f"❌ Failed to execute command: {str(e)}")
                return False

        return True