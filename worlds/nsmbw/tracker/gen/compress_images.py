# This python script can be used to compress your images using zopfli
# Make sure to install the required packages from requirements.txt
import time
from tqdm import tqdm
from multiprocessing import Pool

from zopfli.png import optimize
import os


def main():
    start = time.time()
    found_files = []
    all_bytes = 0
    all_new_bytes = 0
    for root, dirs, files in os.walk('../images'):
        print(root, dirs, files)
        for file in files:
            filename, extension = os.path.splitext(file)
            if extension.lower() == '.png':
                path = os.path.abspath(os.path.join(root, file))
                found_files.append(path)
                print(f'found file: {path}')
    print(f'found {len(found_files)} files')
    found_files.sort(key=lambda x: os.path.getsize(x), reverse=True)
    print('files sorted')
    with Pool() as p:
        for res in tqdm(p.imap_unordered(optimize_file, found_files, chunksize=1), total=len(found_files),
                        unit="files"):
            all_bytes += res[0]
            all_new_bytes += res[1]
    end = time.time()
    format_saved(all_bytes, all_new_bytes, end - start)


def optimize_file(path):
    start = time.time()
    with open(path, 'rb') as f:
        bytes = f.read()
        new_bytes = optimize(bytes)
    if len(new_bytes) < len(bytes):
        with open(path, 'wb') as f:
            f.seek(0)
            f.write(new_bytes)
            f.flush()
    end = time.time()
    format_saved(len(bytes), len(new_bytes), end - start, os.path.basename(path))
    return len(bytes), len(new_bytes)


def format_saved(bytes, new_bytes, time, filename="overall"):
    saved = bytes - new_bytes
    percent = (saved / bytes) * 100
    print(
        f'{filename}: {format_bytes(bytes)}->{format_bytes(new_bytes)}, saved {format_bytes(saved)} ({percent:.2f}%), took {time:.3f}s')


def format_bytes(bytes):
    labels = {0: '', 1: 'k', 2: 'M', 3: 'G', 4: 'T', 5: 'P', 6: 'E'}
    n = 0
    while bytes > 1024:
        bytes = bytes / 1024
        n += 1
    return f'{bytes:.1f}{labels[n]}B'


if __name__ == '__main__':
    main()
