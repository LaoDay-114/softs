import sys
import os
import zipfile
import json
import shutil
from pathlib import Path

#-----------配置区
NNSV = "NeoU"
SV = "1.0.0-Beta"

UTF = "UpdateTemp"

CT = "[neou.py] 创建缓存"
TT = "[neou.py] 缓存存在"
EUP = "[neou.py] 释放了文件"
DFM = "[neou.py] 根据更新包要求,删除了文件"
CFM = "[neou.py] 应用了更新"
DUTF = "[neou.py] 清理了更新缓存"

MFJ = "manifest.json"
#-----------

def sv() -> None:
    print(f"{NNSV} Version {SV}\n")

def unzip(zip_file, path):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(path=path)


def main():
    sv()

    if len(sys.argv) < 2:
        print("如何使用?")
        print("neou 更新包")
        print("对！就是这么简单，快去试试吧！")
        return 1


    if not os.path.exists(UTF):
        os.mkdir(UTF)
        print(CT)
    else:
        print(TT)
    unzip(sys.argv[1], UTF)
    print(EUP)
    with open(f"{UTF}/{MFJ}", 'r', encoding='utf-8') as f:
        data = json.load(f)
    delfe_list = data.get("delfe", [])
    for item in delfe_list:
        print(f"{DFM} {item}")
        p = Path(item)
        if p.exists():
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    value = data["data"]
    shutil.copytree(
        src=f"{UTF}/{value}",
        dst=Path.cwd(),
        dirs_exist_ok=True,
        symlinks=True,
        ignore=shutil.ignore_patterns("*.tmp", "__pycache__", ".git"),
        copy_function=shutil.copy2,
    )
    print(CFM)
    p = Path(UTF)
    if p.exists():
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    print(DUTF)


if __name__ == "__main__":
    main()
