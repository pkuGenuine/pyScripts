import keyboard
import os
import time

# 这个包本身对 MacOS 的支持就不好，只能凑活着用一下

'''
# 有个问题是，这个好像不会阻断其他听这个信号的东西
# command + t 在这里有输出，但有道也有反应
keyboard.add_hotkey('command+t', print, args=['triggered', 'hotkey'])

# control 在 MacOS 好像捕捉不了
# 有 command 能用其实就不错了
# keyboard.add_hotkey('control+f', print, args=['triggered', 'hotkey'])
keyboard.add_hotkey('space', print, args=['space was pressed'])

# shift 好像也不好用
# keyboard.press_and_release('shift+s, space')
# 这里要注意别递归了，不然就会一直写下去。
def myhook(key):
	keyboard.write('The quick brown fox jumps over the lazy dog.')
keyboard.on_press_key('+', myhook)
keyboard.wait()
'''


######## 输入替换
def myhook(key, string):
    def callback(received_key):
        keyboard.write(string)
        # 貌似是有迭代替换的问题，这个版本肯定还没法用
        if key in string or key == 'enter':
            time.sleep(0.5)
    keyboard.on_press_key(key, callback)
    keyboard.wait()


########   这一块主要用来记录键盘按键   #########
def log_key(event, log_file='/var/log/key_press.log', mod='a'):
    with open(log_file, mod) as f:
        # f.write("[{}]: {}\n".format(event.time, event.name))
        f.write(enter.name)
        f.close()

# 用的时候可以考虑起个线程跑，因为得等
def start_key_log(keys: list=[]): 
    # 默认记录所有按键
    if keys == []:
        keyboard.on_press(log_key)
    else:
        for key in keys:
            keyboard.on_press_key(key, log_key)
    keyboard.wait()