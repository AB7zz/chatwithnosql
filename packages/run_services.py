import subprocess
import os
import sys
import signal
import time
from threading import Thread

def run_command(command, cwd=None, use_conda=False):
    try:
        if use_conda:
            # Modify the command to run in the conda environment
            if sys.platform == 'win32':
                # For Windows
                command = f'conda activate chatwithnosql && {command}'
            else:
                # For Unix-like systems
                command = f'conda run -n chatwithnosql {command}'
        
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        def print_output(stream, prefix):
            for line in stream:
                print(f"{prefix} | {line}", end='')
                
        Thread(target=print_output, args=(process.stdout, command)).start()
        Thread(target=print_output, args=(process.stderr, command)).start()
        
        return process
    except Exception as e:
        print(f"Error starting {command}: {e}")
        return None

def main():
    # Get the absolute path to the packages directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(base_path, 'frontend')
    backend_path = os.path.join(base_path, 'backend')
    
    # Commands to run
    commands = [
        ('npm run dev', frontend_path, False),  # (command, path, use_conda)
        ('python cosine/app.py', backend_path, True),
        ('python data-lake/app.py', backend_path, True),
        ('python embeddings/app.py', backend_path, True),
        ('python gemini/app.py', backend_path, True),
        ('python pinecone/app.py', backend_path, True),
    ]
    
    # Start all processes
    processes = []
    for cmd, cwd, use_conda in commands:
        print(f"Starting {cmd} in {cwd}")
        process = run_command(cmd, cwd, use_conda)
        if process:
            processes.append(process)
        time.sleep(2)  # Add a small delay between starting services
    
    def signal_handler(signum, frame):
        print("\nShutting down all services...")
        for process in processes:
            if process.poll() is None:  # If process is still running
                if sys.platform == 'win32':
                    process.terminate()
                else:
                    process.send_signal(signal.SIGTERM)
        sys.exit(0)
    
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Wait for all processes to complete
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()