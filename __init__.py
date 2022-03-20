import subprocess
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path


def create_file_list(gopro_src):
    gl = Path(gopro_src).glob('**/*.MP4')
    ls = list()
    for i in gl:
        print(i)
        n = i.stem
        _, chapter, file = n[0:2], n[2:4], n[4:]  # encoding
        ls.append(dict(path=str(i.resolve()), file=file, chapter=chapter))
    groupby = dict()
    for item in sorted(ls, key=lambda k: k['chapter']):
        groupby.setdefault(item['file'], []).append(item)
    for filenum, dls in groupby.items():
        file_list_dst = f'/tmp/gopro-concat/{filenum}'
        Path(file_list_dst).mkdir(exist_ok=True, parents=True)
        with open(f'{file_list_dst}/concat_me.txt', 'w') as file:
            for i in dls:
                s = f'file {i["path"]}\n'
                file.write(s)
    print('\n### create_file_list DONE!\n\n')


def concat(i, txt, dst):
    src = txt.resolve()
    command = f'ffmpeg -f concat -safe 0 -i {src} -c copy {dst}'
    status, _ = subprocess.getstatusoutput(command)  # output
    print(f'#: {i:03}, path: {src.parent}, status: {status}')


def concatination(dst_root):
    start = datetime.now()
    gl = Path('/tmp/gopro-concat/').glob('**/*.txt')
    with Pool() as pool:
        resls = list()
        for i, txt in enumerate(gl):
            dst = f'{dst_root}{txt.parts[3]}.mp4'
            res = pool.apply_async(
                concat,
                (
                    i,
                    txt,
                    dst,
                ),
            )
            resls.append(res)
        print('res: ', [res.get() for res in resls])
    print('\n### concatination DONE!\n\n')

    end = datetime.now()
    time_taken = end - start
    print('Time: ', time_taken)


def clear_data(tmp=False, src=False):
    if tmp:
        subprocess.run(f'rm -rf {tmp}', shell=True)
    if src:
        subprocess.run(f'rm -rf {src}', shell=True)


if __name__ == '__main__':
    src = '/run/media/chibo/7000-8000/DCIM/100GOPRO/'
    tmp = '/tmp/gopro-concat/'
    dst = '/home/chibo/GOPRO/'

    create_file_list(src)
    concatination(dst)

    clear_data(
        tmp=tmp,
        # src=src,
    )

    print('#DONE')
