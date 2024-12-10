import subprocess


commands="""
python3 -m venv venv
python3 -m pip install --upgrade pip
source venv/bin/activate
pip install -r requirements.txt
"""

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout:
        print(line.decode().strip())

def run_commands(commands):
    for command in commands.split('\n'):
        run_command(command)

if __name__ == '__main__':
    run_commands(commands)
    print("Completed setup")


