# coding:utf-8
import os


def getSubPaths(path):
    '''返回path目录下的所有子目录'''
    yield path
    stack = []
    stack.append(path)
    while len(stack) != 0:
        dirpath = stack.pop()
        try:
            filelist = os.listdir(dirpath)
        except PermissionError as err:
            print(err)
            continue
        else:
            for filename in filelist:
                fileabs = os.path.join(dirpath, filename)
                if os.path.isdir(fileabs):
                    stack.append(fileabs)
                    yield fileabs
