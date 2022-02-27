import sys
import os
import argparse

"""
局限：
    1. remove, replace 后必须跟代码
    2. 依赖 black 去规范代码格式。不确定带括号和逗号的多行写法会不会出问题，全部整到一行去处理。
    3. 不建议使用多行注释与多行字符串
    4. path 虽然写了参数但还没实现
"""


class Patcher(object):
    """docstring for Patcher"""

    def __init__(self, black=True, removeComments=False, removeBlankline=False, removePrint=False, path=""):
        super(Patcher, self).__init__()
        self.black = black
        self.removeComments = removeComments
        self.removeBlankline = removeBlankline
        self.removePrint = removePrint
        if path != "":
            self.path = path.split(":").append(os.getcwd())
        else:
            self.path = [os.getcwd()]

    def patch(self, file):
        if self.black and os.system(f"black -l 10000 {file}") != 0:
            raise NotImplementedError(f'Failed to "black" the file {file}')
        contents = open(file)
        outfile = open(f"{file}~", "w")
        try:
            line = next(contents)
            while True:
                line = self.processLine(line, contents, outfile)
        except StopIteration:
            outfile.close()
            os.system(f"rm -f {file}; mv {file}~ {file}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def processLine(self, line, contents, outfile):
        stripped = line.strip()
        if stripped.startswith("# @@! "):
            directive = stripped[6:].split()
            op = directive[0].lower()
            # nextline = next(contents)
            if op == "remove":

                nextline = next(contents)
                while(nextline.strip() == ""):
                    nextline = next(contents)

                # 这个地方还是不好的，更好的做法是忽略空格和注释？
                if nextline.startswith("#") or nextline.startswith("'''") or nextline.startswith('"""'):
                    raise NotImplementedError("Invalid sytax. Comments or blank line below directive is not allowed.")

                if len(directive) == 1 or directive[1].lower() == "line":
                    pass
                elif directive[1].lower() == "block":
                    blockIndentation = len(nextline) - len(nextline.strip(" "))
                    assert blockIndentation % 4 == 0
                    while True:
                        nextline = next(contents)
                        if len(nextline) - len(nextline.strip(" ")) == blockIndentation:
                            return nextline
                else:
                    raise NotImplementedError(f"{directive[1].lower()} is not valid for remove.")

            elif op == "add":
                indentation = len(line) - len(line.strip(" "))
                assert indentation % 4 == 0
                outfile.write(" " * indentation + " ".join(directive[1:]) + "\n")
                return next(contents)

            elif op == "replace":

                nextline = next(contents)
                while(nextline.strip() == ""):
                    nextline = next(contents)

                if nextline.startswith("#") or nextline.startswith("'''") or nextline.startswith('"""'):
                    raise NotImplementedError("Invalid sytax. Comments or blank line below directive is not allowed.")

                if directive[1].lower() == "line":
                    indentation = len(line) - len(line.strip(" "))
                    if directive[2].startswith("file:"):
                        self.includeFile(indentation, " ".join(directive[2:])[5:], outfile)
                    else:
                        outfile.write(" " * indentation + " ".join(directive[2:]) + "\n")
                elif directive[1].lower() == "block":
                    blockIndentation = len(nextline) - len(nextline.strip(" "))
                    assert blockIndentation % 4 == 0
                    while True:
                        nextline = next(contents)
                        if len(nextline) - len(nextline.strip(" ")) == blockIndentation:
                            if directive[2].startswith("file:"):
                                indentation = len(line) - len(line.strip(" "))
                                self.includeFile(indentation, " ".join(directive[2:])[5:], outfile)
                            else:
                                outfile.write(" " * indentation + " ".join(directive[2:]))
                            return nextline
                else:
                    raise NotImplementedError(f"{directive[1].lower()} is not valid for replace.")
            # 包含进来的文件和 directive 缩进一致
            elif op == "include":
                indentation = len(line) - len(line.strip(" "))
                self.includeFile(indentation, " ".join(directive[1:]), outfile)
                return next(contents)
            else:
                raise NotImplementedError(f"{op} is not implemented.")

        elif stripped.startswith("#"):
            if not self.removeComments:
                outfile.write(line)
        elif stripped == "":
            if not self.removeBlankline:
                outfile.write("\n")
        elif stripped.startswith("print("):
            if not self.removeComments:
                outfile.write(line)
            else:
                indentation = len(line) - len(line.strip(" "))
                outfile.write(indentation * " " + "pass")
        # 块注释，要求要么一行结束，要么结束时独占一行
        elif stripped.startswith("'''") or stripped.startswith('"""'):
            if not self.removeComments:
                outfile.write(line)
            if not (len(stripped) >= 6 and stripped[:3] == stripped[-3:]):
                while True:
                    nextline = next(contents)
                    if not self.removeComments:
                        outfile.write(nextline)
                    if nextline.strip() == stripped[:3]:
                        break
        else:
            outfile.write(line)
        return next(contents)

    def includeFile(self, indentation, file, outfile):
        if self.black and os.system(f"black -l 10000 {file}") != 0:
            raise NotImplementedError(f'Failed to "black" the file {file}')
        # black 默认第一行必须没缩进，所以这里也认为第一行没有缩进
        # file 默认不为空
        f = open(file)
        try:
            line = " " * indentation + next(f)
            while True:
                line = " " * indentation + self.processLine(line, f, outfile)
        except StopIteration:
            f.close()
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=str, nargs="+", help="List of files to be patched.")
    parser.add_argument("--nocomm", dest="removeComments", default=False, action="store_true", help="Remove comments in codes.")
    parser.add_argument("--noblank", dest="removeBlankline", default=False, action="store_true", help="Remove blank lines in codes.")
    parser.add_argument("--noprint", dest="removePrint", default=False, action="store_true", help="Remove prints in codes.")
    parser.add_argument("-p", "--path", default="", help="Not Implemented.")
    parser.add_argument("--noblack", default=False, action="store_true", help="Do not black the codes.")
    args = parser.parse_args()
    d = {"black": not args.noblack, "removeComments": args.removeComments, "removeBlankline": args.removeBlankline, "removePrint": args.removePrint, "path": args.path}
    patcher = Patcher(**d)
    for file in args.files:
        patcher.patch(file)
