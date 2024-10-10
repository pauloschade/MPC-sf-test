import subprocess

class CommandExecutor:
    def run_command(self, command: str) -> None:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
          return result.stdout
        else:
          return result.stderr