import logging
from typing import Optional
from agent import PlanGenerator
from executor import PlanExecutor
from config import Config

# Set up logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.generator = PlanGenerator()
        self.executor = PlanExecutor()
        self.attempts = 0

    def get_user_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get input from user with optional default value."""
        while True:
            user_input = input(prompt).strip()
            if user_input:
                return user_input
            if default is not None:
                return default
            print("⚠️ Please enter a valid input.")

    def run(self):
        print("👋 Welcome to AI Agent!")
        print(f"⚙️ Configuration: Model={Config.DEFAULT_MODEL}, Safe Mode={'ON' if Config.SAFE_MODE else 'OFF'}")

        while True:
            task = self.get_user_input("\n🗨️ Enter a task (or 'quit' to exit): ")
            if task.lower() in ('quit', 'exit'):
                break

            context = None
            self.attempts = 0
            success = False

            while not success and self.attempts < Config.MAX_RETRIES:
                self.attempts += 1
                print(f"\n🔍 Attempt {self.attempts} of {Config.MAX_RETRIES}")

                try:
                    plan = self.generator.generate_plan(task, context)
                    print("\n📋 Generated Plan:\n" + plan)

                    approve = self.get_user_input("\n✅ Approve this plan? (y/n/quit): ").lower()
                    if approve == 'quit':
                        return
                    if approve != 'y':
                        print("❌ Plan not approved. Please refine your task.")
                        break

                    success = self.executor.execute_plan(plan)

                    if not success:
                        context = self.get_user_input("\n❓ Why did it fail? Describe the issue (or 'quit'): ")
                        if context.lower() == 'quit':
                            return
                        context = f"Previous attempt failed. Reason: {context}. Please provide a revised plan."

                except Exception as e:
                    logger.error(f"❌ Error: {str(e)}")
                    context = f"System error occurred: {str(e)}. Please provide a revised plan."

            if success:
                print("\n🎉 Task completed successfully!")
            else:
                print("\n❌ Max attempts reached. Please try again with a different task.")

if __name__ == "__main__":
    agent = AIAgent()
    agent.run()