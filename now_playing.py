#!/usr/bin/env python
# 标题        : now_playing.py
# 说明        : Now Playing是一个OBS实用性脚本，当您使用指定的播放器播放音乐时，
#             : 这个脚本会自动为您更新您选择的“文本来源”。仅支持Windows。
# 作者        : Etuldan(原作者)
#             : Creepercdn(Fork)
#             : MegaRange(Fork of fork)
# 更新日期    : 2021 02 05
# 版本        : 0.2a
# 前置需求    : - Python 3.6 (https://www.python.org/)
#             :   - pywin32 (https://github.com/mhammond/pywin32/releases)
#             : - Windows Vista或更高版本
# 使用方法    : 请按照以下方法安装和设置Now Playing：
#             : Python:
#             :   1. 安装Python（目前版本的OBS必须使用Python 3.6，请确认您的版本。
#             :      实际上，您可以同时安装多个版本的Python，便于使用一些指定版本的脚本。）
#             :   2. 安装pywin32：在命令提示符或PowerShell中，输入以下命令：
#             ：     python -m pip install pywin32 -U
#             : OBS:
#             :   1. 创建一个“GDI+文本”来源，并取一个名字；
#             :   2. 点击“工具”菜单，再点击“脚本”；
#             :   2.5. （重要）如果您之前没用过Python脚本，您需要在“Python设置”选项卡
#             :        检查OBS是不是正确配置了Python 3.6的安装路径，安装位置一般在这里：
#             :        C:\Users\<您的用户名>\AppData\Local\Programs\Python\Python36
#             :   3. 点击下面的加号“+”按钮，然后添加这个脚本；
#             :   4. 勾选您想要使用的播放器；
#             :   6. 在“使用的文本来源”处，选择您刚创建的“GDI+文本”来源的名字；
#             :   7. 点击“启用该脚本”。
#  
# ==============================================================================

import ctypes
import ctypes.wintypes
import site

import win32api
import win32con
import win32gui
import win32process

import obspython as obs

site.main()

enabled = True
check_frequency = 1000  # ms
display_text = '%artist - %title'
debug_mode = True

source_name = ''

customset = {'spotify': True, 'vlc': True, 'yt_firefox': True, 'yt_chrome': True,
             'foobar2000': True, 'necloud': True, 'aimp': True, }


def IsWindowVisibleOnScreen(hwnd):
    def IsWindowCloaked(hwnd):
        DWMWA_CLOAKED = 14
        cloaked = ctypes.wintypes.DWORD()
        ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, ctypes.wintypes.DWORD(
            DWMWA_CLOAKED), ctypes.byref(cloaked), ctypes.sizeof(cloaked))
        return cloaked.value
    return ctypes.windll.user32.IsWindowVisible(hwnd) and (not IsWindowCloaked(hwnd))


def script_defaults(settings):
    if debug_mode:
        print("Calling defaults")

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_int(settings, "check_frequency", check_frequency)
    obs.obs_data_set_default_string(settings, "display_text", display_text)
    obs.obs_data_set_default_string(settings, "source_name", source_name)
    obs.obs_data_set_default_bool(settings, "spotify", customset['spotify'])
    obs.obs_data_set_default_bool(settings, "vlc", customset['vlc'])
    obs.obs_data_set_default_bool(
        settings, "yt_firefox", customset['yt_firefox'])
    obs.obs_data_set_default_bool(
        settings, "yt_chrome", customset['yt_chrome'])
    obs.obs_data_set_default_bool(
        settings, "foobar2000", customset['foobar2000'])
    obs.obs_data_set_default_bool(settings, "necloud", customset['necloud'])
    obs.obs_data_set_default_bool(settings, "aimp", customset['aimp'])


def script_description():
    if debug_mode:
        print("Calling description")

    return "<b>正在播放</b>" + \
        "<hr>" + \
        "本脚本将自动显示您正在播放的音乐。" + \
        "<br/>" + \
        "可以使用的通配字符串：" + \
        "<br/>" + \
        "<code>%artist</code>, <code>%title</code>" + \
        "<hr>"


def script_load(_):
    if debug_mode:
        print("[CS] 脚本已加载。")


def script_properties():
    if debug_mode:
        print("[CS] 配置已加载。")

    props = obs.obs_properties_create()
    obs.obs_properties_add_bool(props, "enabled", "启用该脚本")
    obs.obs_properties_add_bool(props, "debug_mode", "调试模式")
    obs.obs_properties_add_int(
        props, "check_frequency", "检查频率（毫秒）", 150, 10000, 100)
    obs.obs_properties_add_text(
        props, "display_text", "显示文本", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_bool(props, "spotify", "Spotify")
    obs.obs_properties_add_bool(props, "vlc", "VLC")
    obs.obs_properties_add_bool(props, "yt_firefox", "Youtube for Firefox")
    obs.obs_properties_add_bool(props, "yt_chrome", "Youtube for Chrome")
    obs.obs_properties_add_bool(props, "foobar2000", "Foobar2000")
    obs.obs_properties_add_bool(props, "necloud", "网易云音乐")
    obs.obs_properties_add_bool(props, 'aimp', 'AIMP')

    p = obs.obs_properties_add_list(
        props, "source_name", "使用文本框",
        obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    sources = obs.obs_enum_sources()
    if sources:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id in ("text_gdiplus", "text_ft2_source"):
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)
    obs.source_list_release(sources)

    return props


def script_save(settings):
    if debug_mode:
        print("[CS] 已保存配置。")

    script_update(settings)


def script_unload():
    if debug_mode:
        print("[CS] 已停用脚本")

    obs.timer_remove(get_song_info)


def script_update(settings):
    global enabled
    global display_text
    global check_frequency
    global source_name
    global debug_mode
    if debug_mode:
        print("[CS] 设置已更新。")

    if obs.obs_data_get_bool(settings, "enabled") is True:
        if not enabled:
            if debug_mode:
                print("[CS] Enabled song timer.")

        enabled = True
        obs.timer_add(get_song_info, check_frequency)
    else:
        if enabled:
            if debug_mode:
                print("[CS] Disabled song timer.")

        enabled = False
        obs.timer_remove(get_song_info)

    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    display_text = obs.obs_data_get_string(settings, "display_text")
    source_name = obs.obs_data_get_string(settings, "source_name")
    check_frequency = obs.obs_data_get_int(settings, "check_frequency")
    customset['spotify'] = obs.obs_data_get_bool(settings, "spotify")
    customset['vlc'] = obs.obs_data_get_bool(settings, "vlc")
    customset['yt_firefox'] = obs.obs_data_get_bool(settings, "yt_firefox")
    customset['yt_chrome'] = obs.obs_data_get_bool(settings, "yt_chrome")
    customset['foobar2000'] = obs.obs_data_get_bool(settings, "foobar2000")
    customset['necloud'] = obs.obs_data_get_bool(settings, "necloud")
    customset['aimp'] = obs.obs_data_get_bool(settings, "aimp")


def update_song(artist="", song=""):

#    now_playing = "无音乐"
    now_playing = ""
    if(artist != "" or song != ""):
        now_playing = display_text.replace(
            '%artist', artist).replace('%title', song)

    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", now_playing)
    source = obs.obs_get_source_by_name(source_name)
    obs.obs_source_update(source, settings)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)
    if debug_mode:
        print("[CS] 正在播放： " + artist + " / " + song)


def get_song_info():

    def enumHandler(hwnd, result):

        _, procpid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            if not IsWindowVisibleOnScreen(hwnd):
                return
            mypyproc = win32api.OpenProcess(
                win32con.PROCESS_ALL_ACCESS, False, procpid)
            exe = win32process.GetModuleFileNameEx(mypyproc, 0)
            if customset['spotify'] and exe.endswith("Spotify.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "-" in title:
                    artist = title[0:title.find("-")-1]
                    song = title[title.find("-")+2:]
                    result.append([artist, song])
                    return
            if customset['vlc'] and exe.endswith("vlc.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "-" in title:
                    artist = title[0:title.find("-")-1]
                    song = title[title.find("-")+2:title.rfind("-")-1]
                    result.append([artist, song])
                    return
            if customset['yt_firefox'] and exe.endswith("firefox.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "- YouTube" in title:
                    artist = title[0:title.find("-")-1]
                    song = title[title.find("-")+2:title.rfind("-")-1]
                    result.append([artist, song])
                    return
            if customset['yt_chrome'] and exe.endswith("chrome.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "- YouTube" in title:
                    artist = title[0:title.find("-")-1]
                    song = title[title.find("-")+2:title.rfind("-")-1]
                    result.append([artist, song])
                    return
            if customset['foobar2000'] and exe.endswith("foobar2000.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "-" in title:
                    artist = title[0:title.find("-")-1]
                    song = title[title.find("]") +
                                 2:title.rfind(" [foobar2000]")-1]
                    result.append([artist, song])
                    return
            if customset['necloud'] and exe.endswith("cloudmusic.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "-" in title:
                    song = title[0:title.find("-")-1]
                    artist = title[title.find("-")+2:]
                    result.append([artist, song])
                    return
            if customset['necloud'] and exe.endswith("cloudmusic.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "-" in title:
                    song = title[0:title.find("-")-1]
                    artist = title[title.find("-")+2:]
                    result.append([artist, song])
                    return
            if customset['aimp'] and exe.endswith("AIMP.exe"):
                title = win32gui.GetWindowText(hwnd)
                if "-" in title:
                    artist = title[0:title.find("-")-1]
                    song = title[title.find("-")+2:]
                    result.append([artist, song])
                    return

        except:
            return
        return

    result = []
    win32gui.EnumWindows(enumHandler, result)
    try:
        update_song(result[0][0], result[0][1])
    except:
        update_song()
