from tqdm import tqdm
from time import sleep

def iterate():
    for i in range(5000): yield i

total_files = 3000
pbar = tqdm(total=total_files)
for i in range(3000):
    sleep(0.1)
    pbar.update(1)
