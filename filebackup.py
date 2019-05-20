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
from needfiles import NeedFiles

try:
    import exifread
except ImportError:
    print("导入EXIFREAD模块错误，请运行pip install exifread安装，或访问https://pypi.org/project/ExifRead/获得帮助")
    exit()

if sys.version[0] == "3":
    raw_input = input


# elif sys.getdefaultencoding() != "utf-8":
# reload(sys)
# sys.setdefaultencoding("utf-8")

def getFileMd5(filename):
    '''生成文件的MD5码'''

    def read_chunks(fh):
        fh.seek(0)
        chunk = fh.read(8096)
        while chunk:
            yield chunk
            chunk = fh.read(8096)
        else:
            fh.seek(0)

    m = hashlib.md5()
    with open(filename, 'rb') as fh:
        for chunk in read_chunks(fh):
            m.update(chunk)
    return m.hexdigest()


def getDateTimeOriginal(file):
    '''返回EXIF信息的拍摄日期'''
    with open(file, 'rb') as f:
        tags = exifread.process_file(f, details=False, stop_tag='EXIF DateTimeOriginal', strict=True)
    return str(tags['EXIF DateTimeOriginal'])[:19]  # 截去上午或下午字段


def renameFile(file, index):
    '''依照样式（filename_1.jpg）重命名文件，后缀为index'''
    path, filename = os.path.split(file)
    name, ext = os.path.splitext(filename)
    if index == 1:
        name = name + '_' + str(index)
    else:
        name = re.sub(r"_%s$" % (index - 1), "_%s" % index, name)
    newfilename = name + ext
    if newfilename == filename:
        raise Exception('file not rename')
    return os.path.join(path, newfilename)


class FileInfo(object):
    def __init__(self, file):
        self.file = os.path.abspath(file)
        self.fileName = os.path.basename(self.file)
        self.fileExtension = os.path.splitext(self.fileName)[-1]
        self.fileMd5 = getFileMd5(self.file)
        self.fileSubDir = self.creatFileSubDir()

    def getFile(self):
        return self.file

    def getFileName(self):
        return self.fileName

    def getFileExtension(self):
        return self.fileExtension

    def getFileMd5(self):
        return self.fileMd5

    def getSubDir(self):
        return self.fileSubDir

    def creatFileSubDir(self):
        timeTmp = None
        if self.fileExtension in (".jpg", ".jpeg"):
            try:
                timeTmp = time.strptime(getDateTimeOriginal(self.file), '%Y:%m:%d %H:%M:%S')
            except KeyError:
                timeTmp = time.localtime(os.stat(self.file).st_mtime)
        else:
            timeTmp = time.localtime(os.stat(self.file).st_mtime)
        return time.strftime('%Y-%m', timeTmp)

    def getFileInfo(self):
        keys = ("file", "fileName", "fileExt", "fileMd5", "subDir")
        return dict(zip(keys, (self.file, self.fileName, self.fileExtension, self.fileMd5, self.getSubDir())))

    def rmFile(self):
        os.remove(self.file)
        print("{}删除成功".format(self.file))


class BackupPath(object):
    def __init__(self, path):
        self.backupPath = os.path.abspath(path)
        self.pickleFile = os.path.join(self.backupPath, "filesmd5db.pickle")
        self.fileMd5Dict = self.createFileMd5Dict()

    def getFileMd5Dict(self):
        return self.fileMd5Dict

    def createFileMd5Dict(self):
        latestMd5 = {}
        try:
            with open(self.pickleFile, 'rb') as f:
                latestMd5 = pickle.load(f)
        except FileNotFoundError:  # "filesmd5db.pickle"文件不存在，则新建
            with open(self.pickleFile, 'wb') as f:
                pickle.dump(latestMd5, f)
        return latestMd5

    def saveFileMd5Dict(self):
        with open(self.pickleFile, 'wb') as f:
            pickle.dump(self.fileMd5Dict, f)

    def renewFileMd5Dict(self):
        '''刷新MD5字典，保持最新的文件MD5'''
        pass

    def copyFile(self, fileInfo):
        desFile = os.path.join(self.backupPath, fileInfo.getSubDir(), fileInfo.getFileName().upper())
        index = 0  # 重命名时的参考编号
        while os.path.isfile(desFile):
            index += 1
            if fileInfo.getFileMd5() == getFileMd5(desFile):
                print("文件已存在2")
                result = False  # 文件已存在,没有进行复制步骤，返回False
                break
            else:
                desFile = renameFile(desFile, index)  # 文件名相同但内容不同，重新命名文件
        else:
            print("开始复制文件")
            shutil.copy2(fileInfo.getFile(), desFile)
            result = True  # 文件复制成功，返回True
        self.fileMd5Dict[fileInfo.getSubDir()].add(fileInfo.getFileMd5())  # 把MD5加入字典中
        return result

    def backupFile(self, file):
        fInfo = FileInfo(file)
        if fInfo.getSubDir() in self.fileMd5Dict.keys():  # 判断子目录是否存在
            md5s = self.fileMd5Dict[fInfo.getSubDir()]
            if fInfo.getFileMd5() in md5s:  # 判断文件是否存在
                print("文件已存在1")
                result = False  # 文件已经存在，返回False
            else:
                result = self.copyFile(fInfo)
        else:
            subDir = os.path.join(self.backupPath, fInfo.getSubDir())  # 第一次碰到子目录处理步骤
            if not os.path.isdir(subDir):
                os.mkdir(subDir)
            self.fileMd5Dict[fInfo.getSubDir()] = set()
            result = self.copyFile(fInfo)
        fInfo.rmFile()
        return result


def filetest():
    file = "img.jpg"
    fInfo = FileInfo(file)
    print(fInfo.getFile())
    print(fInfo.getFileName())
    print(fInfo.getFileExtension())
    print(fInfo.getFileMd5())
    print(fInfo.getSubDir())


def bkptest():
    file = "img2.jpg"
    path = "d:\\backup"
    bkp = BackupPath(path)
    print(bkp.backupFile(file))
    bkp.saveFileMd5Dict()
    print(bkp.getFileMd5Dict())


if __name__ == "__main__":
    # filetest()
    # bkptest()
    srcpath = "g:\\temp"
    bkpath = BackupPath("g:\\backup")
    # bkpath.renewFileMd5Dict()
    # for key in bkpath.getFileMd5Dict():
    #     print(key)
    nf = NeedFiles()
    #nf.setFileExtension("mov", "jpeg")
    #nf.setFileExtension("MP4", "DAT")
    nf.setFileExtension("3gp", "avi", "mpg", "mov", "jpeg", "MP4", "DAT", "jpg", "png")
    i = 0
    for file in nf.getNeedFiles(srcpath):
        if bkpath.backupFile(file):
            i += 1
    print(i)
    bkpath.saveFileMd5Dict()
