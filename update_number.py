import os
import random
import subprocess
from datetime import datetime
import tempfile

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    with open("number.txt", "r") as f:
        return int(f.read().strip())


def write_number(num):
    with open("number.txt", "w") as f:
        f.write(str(num))


def generate_random_commit_message():
    from transformers import pipeline

    generator = pipeline(
        "text-generation",
        model="openai-community/gpt2",
    )
    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject. Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message:
    """
    generated = generator(
        prompt,
        max_new_tokens=50,
        num_return_sequences=1,
        temperature=0.9,  # Slightly higher for creativity
        top_k=50,  # Limits sampling to top 50 logits
        top_p=0.9,  # Nucleus sampling for diversity
        truncation=True,
    )
    text = generated[0]["generated_text"]

    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        raise ValueError(f"Unexpected generated text {text}")


def git_commit():
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"], check=True)
    # Create commit with current date
    if "FANCY_JOB_USE_LLM" in os.environ:
        commit_message = generate_random_commit_message()
    else:
        date = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Update number: {date}"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)


def git_push():
    # Push the committed changes to GitHub
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def update_task_scheduler():
    # Generate random hour (0-23) and minute (0-59)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)

    # Create a task in Windows Task Scheduler
    task_name = "UpdateNumberTask"
    command = f"powershell.exe -ExecutionPolicy Bypass -File {os.path.join(script_dir, 'update_number.py')}"

    # Remove any existing task with the same name
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Create a new task
    subprocess.run([
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", command,
        "/sc", "daily",
        "/st", f"{random_hour:02d}:{random_minute:02d}"
    ], check=True)

    print(f"Task Scheduler updated to run at {random_hour:02d}:{random_minute:02d} daily.")


def main():
    try:
        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)
        git_commit()
        git_push()
        update_task_scheduler()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
