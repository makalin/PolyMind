# PolyMind - Terminal-Based Multi-AI Interpreter

import os
import openai
import requests
import json
import threading
import datetime
import difflib
from subprocess import run, PIPE

# === CONFIGURATION ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
LLAMA_API_URL = os.getenv("LLAMA_API_URL")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_AGENT_CMD = os.getenv("LOCAL_AGENT_CMD")
POLYMIND_HISTORY = os.getenv("POLYMIND_HISTORY", "polymind_history.json")
POLYMIND_ALIASES = json.loads(os.getenv("POLYMIND_ALIASES", '{}'))

# === AI CLIENTS ===
def chatgpt(prompt):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message['content'].strip()

def claude(prompt):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    json_data = {
        "model": "claude-3-opus-20240229",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=json_data)
    return response.json()['content'][0]['text']

def llama(prompt):
    if not LLAMA_API_URL:
        return "LLAMA_API_URL not set."
    json_data = {"prompt": prompt, "stream": False}
    response = requests.post(LLAMA_API_URL, json=json_data)
    result = response.json()
    return result.get("response", "No response from LLaMA")

def mistral(prompt):
    if not MISTRAL_API_URL:
        return "MISTRAL_API_URL not set."
    json_data = {"prompt": prompt, "temperature": 0.7, "stream": False}
    response = requests.post(MISTRAL_API_URL, json=json_data)
    return response.json().get("response", "No response from Mistral")

def gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    json_data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, json=json_data)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "No response from Gemini"

def local(prompt):
    if not LOCAL_AGENT_CMD:
        return "LOCAL_AGENT_CMD not configured."
    result = run([LOCAL_AGENT_CMD, prompt], stdout=PIPE, stderr=PIPE, text=True)
    return result.stdout if result.returncode == 0 else result.stderr

# === AGENT MANAGER ===
AGENTS = {
    "chatgpt": chatgpt,
    "claude": claude,
    "llama": llama,
    "mistral": mistral,
    "gemini": gemini,
    "local": local
}

def run_agent(agent, prompt):
    func = AGENTS.get(agent)
    return func(prompt) if func else f"Unknown agent: {agent}"

def log_history(entry):
    try:
        history = []
        if os.path.exists(POLYMIND_HISTORY):
            with open(POLYMIND_HISTORY, "r") as f:
                history = json.load(f)
        history.append(entry)
        with open(POLYMIND_HISTORY, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"⚠️ History log error: {e}")

def view_history(limit=5):
    try:
        if not os.path.exists(POLYMIND_HISTORY):
            print("📭 No history yet.")
            return
        with open(POLYMIND_HISTORY, "r") as f:
            history = json.load(f)[-limit:]
            for item in history:
                print(f"\n🕓 {item['timestamp']}\nAgents: {', '.join(item['agents'])}\nPrompt: {item['prompt']}\n")
                for agent, result in item['results'].items():
                    print(f"[{agent}]\n{result}\n")
    except Exception as e:
        print(f"⚠️ View error: {e}")

def clear_history():
    try:
        if os.path.exists(POLYMIND_HISTORY):
            os.remove(POLYMIND_HISTORY)
            print("🧹 History cleared.")
        else:
            print("📭 No history file to clear.")
    except Exception as e:
        print("⚠️ Could not clear history:", e)

def export_history(filepath="history_export.json"):
    try:
        if os.path.exists(POLYMIND_HISTORY):
            with open(POLYMIND_HISTORY, "r") as f:
                data = f.read()
            with open(filepath, "w") as f:
                f.write(data)
            print(f"📤 History exported to {filepath}")
        else:
            print("📭 No history to export.")
    except Exception as e:
        print("⚠️ Export failed:", e)

def generate_shell_script(agents, prompt):
    script = "#!/bin/bash\n"
    for agent in agents:
        script += f'echo "[{agent}]"\npolymind "{agent} {prompt}"\n\n'
    return script

def generate_html(results):
    html = ["<html><head><title>PolyMind Output</title></head><body>"]
    for agent, response in results.items():
        html.append(f"<h2>{agent}</h2><pre>{response}</pre>")
    html.append("</body></html>")
    return "\n".join(html)

def generate_markdown(results):
    md = ["# PolyMind Results"]
    for agent, result in results.items():
        md.append(f"\n## {agent}\n\n```\n{result}\n```")
    return "\n".join(md)

def generate_diff(results):
    keys = list(results.keys())
    if len(keys) < 2:
        return "Need at least two agents to compare."
    diff = difflib.unified_diff(
        results[keys[0]].splitlines(),
        results[keys[1]].splitlines(),
        fromfile=keys[0],
        tofile=keys[1],
        lineterm=""
    )
    return "\n".join(diff)

# === TERMINAL INTERFACE ===
def main():
    print("🧠 PolyMind CLI - Talk to multiple AIs")
    print("Commands: [agents] prompt | view | clear | export | retry | --json | --html | --markdown | --diff | --shell | --alias=NAME:AGENTS | --save=filename")

    last_prompt = None
    last_agents = None

    while True:
        user_input = input(">> ").strip()

        if user_input.lower() == "exit":
            break
        if user_input.lower() == "view":
            view_history()
            continue
        if user_input.lower() == "clear":
            clear_history()
            continue
        if user_input.lower().startswith("export"):
            parts = user_input.split()
            path = parts[1] if len(parts) > 1 else "history_export.json"
            export_history(path)
            continue
        if user_input.lower() == "retry":
            if not last_prompt or not last_agents:
                print("⛔ Nothing to retry.")
                continue
            user_input = f"{','.join(last_agents)} {last_prompt}"

        # Flags
        save_file = None
        json_output = False
        html_output = False
        markdown_output = False
        diff_output = False
        shell_output = False

        if "--json" in user_input:
            json_output = True
            user_input = user_input.replace("--json", "").strip()
        if "--html" in user_input:
            html_output = True
            user_input = user_input.replace("--html", "").strip()
        if "--markdown" in user_input:
            markdown_output = True
            user_input = user_input.replace("--markdown", "").strip()
        if "--diff" in user_input:
            diff_output = True
            user_input = user_input.replace("--diff", "").strip()
        if "--shell" in user_input:
            shell_output = True
            user_input = user_input.replace("--shell", "").strip()
        if "--save=" in user_input:
            save_file = user_input.split("--save=")[1].split()[0]
            user_input = user_input.replace(f"--save={save_file}", "").strip()
        if "--alias=" in user_input:
            alias_part = user_input.split("--alias=")[1].strip()
            if ":" in alias_part:
                name, agent_str = alias_part.split(":", 1)
                POLYMIND_ALIASES[name.strip().lower()] = agent_str.strip()
                print(f"✅ Alias added: {name.strip().lower()} = {agent_str.strip()}")
                continue

        try:
            agent_section, *prompt_parts = user_input.split()
            agents = POLYMIND_ALIASES.get(agent_section.lower(), agent_section).split(",")
            agents = [a.strip().lower() for a in agents]
            prompt = " ".join(prompt_parts)

            if shell_output:
                shell_script = generate_shell_script(agents, prompt)
                print("\n" + shell_script + "\n")
                continue

            results = {}
            threads = []

            def get_result(agent):
                try:
                    results[agent] = run_agent(agent, prompt)
                except Exception as e:
                    results[agent] = f"⚠️ Error: {str(e)}"

            for a in agents:
                t = threading.Thread(target=get_result, args=(a,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            timestamp = datetime.datetime.now().isoformat()
            entry = {"timestamp": timestamp, "agents": agents, "prompt": prompt, "results": results}
            log_history(entry)
            last_prompt = prompt
            last_agents = agents

            if html_output:
                output = generate_html(results)
            elif markdown_output:
                output = generate_markdown(results)
            elif diff_output:
                output = generate_diff(results)
            elif json_output:
                output = json.dumps(results, indent=2)
            else:
                output = "\n".join([f"[{k}]\n{v}" for k, v in results.items()])

            print("\n" + output + "\n")

            if save_file:
                with open(save_file, "w") as f:
                    f.write(output)
                print(f"📁 Output saved to {save_file}")

        except Exception as e:
            print("⚠️ Error:", e)

if __name__ == "__main__":
    main()
