import os

def increment(file_name, delta=1):
    counter = 0
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            counter = int(f.read().strip())
    counter += delta
    with open(file_name, 'w') as f:
        f.write(str(counter))
    return counter
