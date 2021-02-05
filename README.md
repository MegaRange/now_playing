# Now Playing
—— 一个方便您展示正在播放的音乐的OBS脚本

___

脚本原作者的帖子:
（原作者）https://obsproject.com/forum/resources/now-playing.783/
（Fork）https://obsproject.com/forum/resources/now-playing.1160/

___

## 使用方法
**注意：该脚本需要Windows Vista或者更高版本（因为要dwm.exe）**

#### 准备Python：
  1. [安装Python 3.6](https://www.python.org/downloads/)（OBS目前版本`26.1.1`似乎必须使用Python 3.6，请确认您的版本。实际上，您可以同时安装多个版本的Python，便于使用一些指定版本的脚本。）
  2. 安装pywin32：在命令提示符或PowerShell中，输入以下命令：
  `python -m pip install pywin32 -U`

#### 配置OBS：
1. 创建一个“GDI+文本”来源，并取一个名字；
2. 点击“工具”菜单，再点击“脚本”；
3. 【重要】如果您之前没用过Python脚本，您需要在“Python设置”选项卡检查OBS是不是正确配置了Python 3.6的安装路径，安装位置一般在这里：
`C:\Users\<您的用户名>\AppData\Local\Programs\Python\Python36`
4. 点击下面的加号“+”按钮，然后添加这个脚本；
5. 勾选您想要使用的播放器；
6. 在“使用的文本来源”处，选择您刚创建的“GDI+文本”来源的名字；
7. 点击“启用该脚本”；
8. 打开您的播放器并开始放歌；
9. 调整文本来源的设置。

## 小贴士:
1. 建议仅勾选您使用的播放器；
2. 记得修改文本来源的设置和滤镜效果；
3. 不要把“检查频率”设置的太快或者太慢；
4. 确认您勾选了“启用该脚本”；
5. 如果脚本出错，请检查“脚本日志”。

## 参考：
[OBS Studio Python/Lua脚本文档](https://obsproject.com/docs/scripting.html)
[OBS Studio Python Scripting Cheatsheet](https://github.com/upgradeQ/OBS-Studio-Python-Scripting-Cheatsheet-obspython-Examples-of-API)