## 0.  依赖
0. Python 3.3+
1. websockets
2. colorama
3. pygame
4. textdistance
## 1.  基础功能

### 1.1	InteractionController

```python
# 从外部向 InteractionController 发送一条消息 msg
# 用例：interactionController.message(msg)
def message(self, msg):
    if msg['src'] in self._handlers:
        self._handlers[msg['src']](msg)
    self.interactionsQueue.notify(msg)

# 从 InteractionController 内部向目的地 dest 发送一条消息 msg
# 用例：self.send('face', msg)
def send(self, dest, msg):
    cmd = {
        "dest": dest,
        "content": json.dumps(msg)
    }
    self.commands.put(cmd)

# 将函数 handler 注册为用于处理来自 src 的消息的处理函数
# 用例：self.registerHandler('midi', self.onMidi)
def registerHandler(self, src, handler):
    self._handlers[src] = handler
```
### 1.2	InteractionQueue

```python
# 添加一个 Interaction 到队列末尾等待执行
# 返回值是添加成功的 Interaction 的 id，可以留作以后取消用
# 注意：interaction 应当是一个类，不要提前把它实例化！
# 用例：id = interactionQueue.add(SomeInteraction)
def add(self, interaction):
    if not self._isInteraction(interaction):
        error("Item pushed onto InteractionQueue is not an Interaction!")
        return
    _id = self._assignID()
    self.interactionsQueue.append((_id, interaction))
    return _id

# 取消标号为 id 的 Interaction
# 用例：interactionQueue.cancel(12)
def cancel(self, id):
        _id = next((x for x in self.interactionsQueue if x[0] == id), None)
        del self.interactionsQueue[_id]

# 跳过当前正在执行的 Interaction
# 用例：interactionQueue.skip()
def skip(self):
    if self._current is not None and self._current.is_alive():
        self._current.terminate()
        self._current.join()
        self._current = None
    self.running.clear()

# 清空所有队列上的 Interacton
# 用例：interactionQueue.clear()
def clear(self):
    if self._current is not None and self._current.is_alive():
        self._current.terminate()
        self._current.join()
        self._current = None
        while True:
            try:
                self.interactionsQueue.get(False)
            except Empty:
                break
    self.running.clear()

# 当前队列是否是空的
# 用例：if interactionQueue.isEmpty():
def isEmpty(self):
    return len(self.interactionsQueue) == 0

# 向当前正在执行的 Interaction 发送消息 msg
# 用例：interactionQueue.notify(msg)
def notify(self, msg):
    if self._current is not None and self._current.is_alive():
        self._current.message(msg)
```
### 1.3	Interaction

```python
# 做一个表情。完成时会发送 websocket 消息，cmd = 'face-finish'
# 用例：self.makeFace("Happy.json")
#
# def onWebSocket(self, msg):
#     if msg['cmd'] == 'face-finish':
#         print("Face animation finished:", msg['id'])
def makeFace(self, name):
    self.send("face", {
        "cmd": "face-change",
        "id": name
    })

# 设定乐器
# 用例：self.setInstrument(73)
def setInstrument(self, instrument=73):
    self.send("midi", {
        "cmd": "instrument",
        "id": instrument
    })

# 唱一个音符 note，时长为 length，音量 velocity。并在结束时调用 callback 函数
def makeNote(self, note, length, velocity=127, callback=None):
    def cb(t):
        self.send("midi", {
            "cmd": "note-off",
            "note": note
        })
        if callback:
            callback()

    self.send("midi", {
        "cmd": "note-on",
        "note": note,
        "velocity": velocity
    })

    self.setAlarm(length, cb)

# 设一个闹钟，t 秒之后触发，触发时调用函数 f
# 用例：self.setAlarm(1.0, self.onAlarm)
def setAlarm(self, t, f):
        tid = self._tid
        self._tid += 1
        targetT = time() + t
        self._timers.append([tid, targetT])
        self.addCallback("timer" + str(tid), f)
        return tid

# 将函数 callback 注册为用于处理来自 src 的消息的处理函数
# 用例：self.registerHandler('midi', self.onMidi)
def registerHandler(self, src, callback):
    if src not in self._callbacks:
        self._callbacks[src] = []
    self._callbacks[src].append(callback)

# 结束这个 Interaction
# 用例：self.terminate() 或者 interaction.terminate()
def terminate(self):
    self._term.set()

# 从外部给这个 Interaction 发送一条消息
# 用例：interaction.message(msg)
def message(self, msg):
    self._messages.put(msg)

# 从内部给目的地 dest 发送一条消息
# 用例：self.send('face', msg)
def send(self, dest, msg):
    cmd = {
        "dest": dest,
        "content": json.dumps(msg)
    }
    self.commands.put(cmd)

# 等待 t 秒。注意！在这个期间，当前 Interaction 会被完全阻塞，无法处理任何消息
# 用例：self.delay(1.0)
def delay(self, t):
    targetTime = time() + t
    while time() < targetTime:
        pass

# 写在这里的代码会在 Interaction 开始时被调用一遍
def setup(self):
    pass

# 写在这里的代码会在 Interaction 开始后一遍遍被调用
def loop(self):
    pass

# 写在这里的代码会在 Interaction 结束时调用
def onExit(self):
    pass
```
### 1.4	MusicAnalyzer

```python
# 测量两个乐句 phrase1 和 phrase2 的相似程度。
# 乐句是一个包含任意多个 int 的 list，如 [64, 56, 78, 66]
# 返回值 0～1，表示完全不相似～完全一样
def similarity(phrase1, phrase2):
    s1 = ""
    s2 = ""
    for note in phrase1:
        s1 += chr(note)
    for note in phrase2:
        s2 += chr(note)
    return jaccard(s1, s2)

# 给定一个乐句 phrase，猜测最有可能的语料库乐句
# 返回一个 tuple，第一个元素是最可能的乐句，第二个是可能性。如：
# (["Play Game", [72, 79, 72, 79, 72, 84, 72]], 0.67777)
def predict(phrase):
    ph = Phrases[:]
    ph.sort(key=lambda x: similarity(x[1], phrase))
    return (ph[-1], similarity(ph[-1][1], phrase))
```

### 1.5	ConsoleLog

```python
# 白色字
def normal(*args, **kwargs):

# 红色字
def error(*args, **kwargs):

# 绿色字
def success(*args, **kwargs):

# 黄色字
def warning(*args, **kwargs):

# 青色字
def notice(*args, **kwargs):
```



## 2.  接收事件消息
### 2.1 基础结构
```json
evt = {
    "src": "事件来源，如 'midi', 'serial', 'websocket' 等",
    "cmd": "指令码，根据来源不同指令码会有不同",
    "...": "根据指令码不同，每个事件消息包会附带更多补充信息"
}
```
### 2.2 MIDI 事件
#### 音符
```json
midi_evt = {
    "src": "midi",
    "cmd": "note-on",
    "note": 64,
    "velocity": 127,
    "time": 1239
}
```
```json
midi_evt = {
    "src": "midi",
    "cmd": "note-off",
    "note": 64,
    "velocity": 127,
    "time": 1240
}
```
```json
midi_evt = {
    "src": "midi",
    "cmd": "note-hold",
    "note": 0,
    "velocity": 0,
    "time": 0
}
```
#### 乐句
```json
midi_evt = {
    "src": "midi",
    "cmd": "phrase",
    "notes": [64, 128, 70, 46]
}
```
```json
midi_evt = {
    "src": "midi",
    "cmd": "phrase-end",
    "notes": [64, 128, 70, 46],
    "start": 1239,
    "end": 1240
}
```

## 3.  发送命令
### 3.1 基础结构
```json
cmd = {
    "dest": "命令目的地，如 'face', 'controller'",
    "cmd": "指令码，根据来源不同指令码会有不同",
    "...": "根据指令码不同，每个事件消息包会附带更多补充信息"
}
```
### 3.2 脸部动画命令
```json
cmd = {
    "dest": "face",
    "cmd": "face-change",
    "id": 1
}
```
```json
cmd = {
    "cmd": "face-load",
    "filenames": ["Happy.json", "Grumpy.json", "..."]
}
```
### 3.3 MIDI播放命令
```json
cmd = {
    "dest": "midi",
    "cmd": "note-on",
    "note": "音符",
    "velocity": "音量"
}
```
```json
cmd = {
    "dest": "midi",
    "cmd": "note-off",
    "note": "音符"
}
```
