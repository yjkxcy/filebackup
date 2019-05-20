# coding:utf-8
import argparse
import os
import re
import glob
import sys
import time
import shutil
import hashlib
import pickle
from getsubpath import getSubPaths


class NeedFiles(object):
    def __init__(self, fileExtension=["jpg", "png"]):
        self.fileExtension = fileExtension  # 考虑是否用字典 key代表字符长度，value代表字符串

    def setFileExtension(self, *fileExtension):
        self.fileExtension = list(set(fileExtension))  # 用set做了去重处理

    def getFileExtension(self):
        return self.fileExtension

    def mergeStr(self):
        ''' 对列表中的每个字符串转换大小写，返回原列表和新列表的合并 '''
        result = []
        for s in self.fileExtension:
            result.append(s.swapcase())
        result.extend(self.fileExtension)
        return result

    def classifyByLength(self):
        ''' 根据字符串的不同长度归类 '''
        strLength = [len(s) for s in self.mergeStr()]
        minLen = min(strLength)
        maxLen = max(strLength)
        classifDict = {}
        for key in range(minLen, maxLen + 1):
            classifDict[key] = [s for s in self.mergeStr() if len(s) == key]
        return classifDict

    def getWildcard(self, fileExtensionList):
        '''根据扩展名列表生成通配符，如‘*.[JjMm][PpOo][GgV4v]’'''
        l = [''.join(set(x)) for x in zip(*fileExtensionList)]
        return ("*." + "[{}]" * len(l)).format(*l)

    def wildcardList(self):
        ''' 返回不同长度扩展名的通配符列表 '''
        result = []
        for key, value in self.classifyByLength().items():
            if value:
                result.append(self.getWildcard(value))
        return result

    def getNeedFiles(self, path):
        path = os.path.abspath(path)
        for wildcard in self.wildcardList():
            for subdir in getSubPaths(path):
                for needFile in glob.glob(os.path.join(subdir, wildcard)):
                    yield needFile


if __name__ == "__main__":
    path = "G:\\testglob"
    nf = NeedFiles()
    #nf.setFileExtension("rm", "rmvb", "thumbnail")
    nf.setFileExtension("ini")
    # print(nf.getFileExtension())
    # print(nf.mergeStr())
    # print(nf.classifyByLength())
    # print(nf.wildcardList())
    for f in nf.getNeedFiles(path):
        print(f)
