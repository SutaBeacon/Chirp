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
def message(self, msg):
    if msg['src'] in self._handlers:
        self._handlers[msg['src']](msg)
    self._interactions.notify(msg)

# 从 InteractionController 内部向目的地 dest 发送一条消息 msg
def send(self, dest, msg):
    cmd = {
        "dest": dest,
        "content": json.dumps(msg)
    }
    self.commands.put(cmd)

# 将函数 handler 注册为用于处理来自 src 的消息的处理函数
def registerHandler(self, src, handler):
    self._handlers[src] = handler
```
### 1.2	InteractionQueue

```python
# 添加一个 Interaction 到队列末尾等待执行
def add(self, interaction):
    if not self._isInteraction(interaction):
        error("Item pushed onto InteractionQueue is not an Interaction!")
        return
    _id = self._assignID()
    self._interactions.append((_id, interaction))
    return _id

# 取消标号为 id 的 Interaction
def cancel(self, id):
        _id = next((x for x in self._interactions if x[0] == id), None)
        del self._interactions[_id]

# 跳过当前正在执行的 Interaction
def skip(self):
    if self._current is not None and self._current.is_alive():
        self._current.terminate()
        self._current.join()
        self._current = None
    self.running.clear()

# 清空所有队列上的 Interacton
def clear(self):
    if self._current is not None and self._current.is_alive():
        self._current.terminate()
        self._current.join()
        self._current = None
        while True:
            try:
                self._interactions.get(False)
            except Empty:
                break
    self.running.clear()

# 当前队列是否是空的
def isEmpty(self):
    return len(self._interactions) == 0

# 向当前正在执行的 Interaction 发送消息 msg
def notify(self, msg):
    if self._current is not None and self._current.is_alive():
        self._current.message(msg)
```
### 1.3	Interaction

```python
# 设一个闹钟，t 秒之后触发，触发时调用函数 f
def setAlarm(self, t, f):
        tid = self._tid
        self._tid += 1
        targetT = time() + t
        self._timers.append([tid, targetT])
        self.addCallback("timer" + str(tid), f)
        return tid

# 将函数 callback 注册为用于处理来自 src 的消息的处理函数
def registerHandler(self, src, callback):
    if src not in self._callbacks:
        self._callbacks[src] = []
    self._callbacks[src].append(callback)

# 结束这个 Interaction
def terminate(self):
    self._term.set()

# 从外部给这个 Interaction 发送一条消息
def message(self, msg):
    self._messages.put(msg)

# 从内部给目的地 dest 发送一条消息
def send(self, dest, msg):
    cmd = {
        "dest": dest,
        "content": json.dumps(msg)
    }
    self.commands.put(cmd)

# 等待 t 秒。注意！在这个期间，当前 Interaction 会被完全阻塞，无法处理任何消息
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
