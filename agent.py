import os
from groq import Groq

# Initialize Groq client
client = Groq(
    api_key="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"
)

def chat_with_ai(prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content

def execute_plan(plan):
    print("\n🚀 Executing the Plan...")
    try:
        import re
        code_blocks = re.findall(r"```python(.*?)```", plan, re.DOTALL)
        if code_blocks:
            for code in code_blocks:
                print("\n🔹 Running the following code:")
                print(code.strip())
                exec(code.strip())
        else:
            print("No Python code found in the plan.")
    except Exception as e:
        print(f"❌ Error during execution: {e}")

def main():
    print("🤖 Welcome to Workik Task Agent!")
    
    while True:
        task = input("📝 Describe the task you want me to perform:\n")
        
        # Step 1: Generate plan
        plan = chat_with_ai(f"Generate a plan in markdown including the code to achieve: {task}")
        print("\n📜 Here is the generated plan:\n")
        print(plan)
        
        # Step 2: Ask for approval
        approval = input("\n✅ Do you approve this plan? (yes/no): ").strip().lower()
        if approval != 'yes':
            print("❌ Plan rejected. Let's refine it.")
            continue
        
        # Step 3: Execute the plan
        execute_plan(plan)
        
        # Step 4: Ask if successful
        success = input("\n✅ Was the task successful? (yes/no): ").strip().lower()
        if success == 'yes':
            print("🎉 Task completed successfully!")
            break
        else:
            # Step 5: Ask for reason and refine
            reason = input("❓ What went wrong? Please explain:\n")
            task = chat_with_ai(f"The previous task failed because: {reason}. Please refine the task: {task}")
            print("\n🔄 Retrying with refined task...")

if __name__ == "__main__":
    main()
