import time

# List of scripts to run sequentially
scripts = ['sceDownloadData.py', 'sceOptimv4.py', 'sceCopyData.py']

for script in scripts:
    with open(script) as f:
        code = f.read()
        try:
            exec(code)
        except Exception as e:
            print(f'Error running {script}: {e}')
            break
    if script != scripts[-1]:
        time.sleep(5)  # Pause for 5 seconds

print("All scripts have been run.")
