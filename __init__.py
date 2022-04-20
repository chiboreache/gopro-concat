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
    print(f'#concat DONE: {src.parent} => {status}')


def concatination(dst_root):
    start = datetime.now()
    gl = Path('/tmp/gopro-concat/').glob('**/*.txt')
    with Pool() as pool:
        dst_ls = list()
        res_ls = list()
        for i, txt in enumerate(gl):
            dst = f'{dst_root}{txt.parts[3]}.mp4'
            dst_ls.append(dst)
            print('#concatination: ', dst)
            res = pool.apply_async(
                concat,
                (
                    i,
                    txt,
                    dst,
                ),
            )
            res_ls.append(res)
        [res.get() for res in res_ls]
    print('\n### concatination DONE!')

    end = datetime.now()
    time_taken = end - start
    print('### time: ', time_taken)
    print()

    return dst_ls


def clear_processed_files(clear_list):
    for i in clear_list:
        subprocess.run(f'rm -rf {i}', shell=True)


if __name__ == '__main__':

    user_name = 'chibo'

    src = f'/run/media/{user_name}/7000-8000/DCIM/100GOPRO/'

    tmp = '/tmp/gopro-concat/'
    dst = f'/home/{user_name}/GOPRO/'

    create_file_list(src)
    cc_result = concatination(dst)
    files_existance = [Path(i).exists() for i in cc_result]

    print('cc_result: ', cc_result)
    print('files_existance: ', files_existance)

    if all(files_existance):
        clear_processed_files([tmp, src])

    print('#DONE')
