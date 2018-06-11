# README

## 依赖
Python 3.6
``` Shell
pip3 install websockets colorama
```

## SafeProcess.py

安全的进程类，基于 multiprocessing。能够安全地被结束，并提供非阻塞的 setAlarm 与阻塞但不影响事件响应的 delay 两种机制，此后会有更新。使用方式模仿 Arduino 和 Procesing。

### 用法：
继承 SafeProcess 类，实现 setup、loop、onMessage、onExit 等函数即可。
``` Python
class TestProcess (SafeProcess):

    def testAlarm(self, t):
        print("timer at", t)

    def setup(self):
        # 会在进程开始时运行一次
        print("setup")
        # 设一个一秒钟之后触发的 alarm，触发时调用 testAlarm
        self.setAlarm(1.0, testAlarm)

    def loop(self):
        # 会在进程运行过程中不断重复被调用
        print("loop-delay1")
        # delay 0.2 秒
        self.delay(0.2)
        print("loop-delay2")
        # delay 0.4 秒
        self.delay(0.4)

    def onMessage(self, msg):
        # 当某进程给本进程发送消息时，onMessage 会自动被调用
        print("onMessage:", msg)

    def onExit(self):
        # 当本进程即将结束时，onExit 会自动被调用
        print("onExit")
```
