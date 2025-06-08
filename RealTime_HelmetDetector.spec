# -*- mode: python ; coding: utf-8 -*-



import sys
import os

block_cipher = None

a = Analysis(
    ['RealTime_HelmetDetectorV3.py'],
    pathex=['D:\\code\\workspace\\python\\yolo\\yolov11'],  
    binaries=[],
    datas=[
        ('warning-alarm-991.wav', '.'),   # 音频放根目录
        ('best.pt', '.'),                 # 模型也放根目录
        ('icon.ico', '.'),                # 图标若在程序里引用，也建议加进去
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RealTime_HelmetDetector',             # 最终生成的程序名
    icon='icon.ico',                             # 图标路径
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False                                # 不显示命令行窗口
)
