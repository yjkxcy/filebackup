# coding:utf-8
import os
from needfiles import NeedFiles


def getFileType():
    return ("thm", "ctg", "ini", "thumbnail","db")


def rmEmptyDir(path):
    if os.path.isdir(path):
        for dir in os.listdir(path):
            rmEmptyDir(os.path.join(path, dir))
    if not os.path.isfile(path) and not os.listdir(path):
        os.rmdir(path)
        print("{}  目录已删除".format(path))


def rmUselessFile(path):
    nf = NeedFiles()
    nf.setFileExtension(*getFileType())
    for file in nf.getNeedFiles(path):
        os.remove(file)
        print("{} 文件已删除".format(file))


if __name__ == "__main__":
    path = "g:\\temp"
    rmUselessFile(path)
    rmEmptyDir(path)
