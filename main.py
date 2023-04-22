import threading
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_part(start, end, url, file_name):
    headers = {'Range': 'bytes={}-{}'.format(start, end)}
    r = requests.get(url, headers=headers, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def download(url, filename):
    num_parts = 30
    response = requests.head(url)
    total_length = int(response.headers.get('content-length'))

    part_size = total_length // num_parts

    threads = []
    for i in range(num_parts):
        start = i * part_size
        end = start + part_size - 1 if i < num_parts - 1 else total_length - 1
        part_file_name = '.paths/{}_{}.mp4'.format(filename, i)
        t = threading.Thread(target=download_part, args=(start, end, url, part_file_name))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    with open(f'videos/{filename}.mp4', 'wb') as f:
        for i in range(num_parts):
            part_file_name = '.paths/{}_{}.mp4'.format(filename, i)
            with open(part_file_name, 'rb') as part_file:
                f.write(part_file.read())

            # delete the part file
            os.remove(part_file_name)


down_links = ['https://example.com/video1.mp4', 'https://example.com/video2.mp4']
File_name = ['video1', 'video2']

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for url, filename in zip(down_links, File_name):
        futures.append(executor.submit(download, url, filename))

    for future in as_completed(futures):
        result = future.result()
        print(result)
