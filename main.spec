# specfile.spec

block_cipher = None

added_files = [
    ('src/app', 'src'),  # Beispiel: ('src', 'src') wenn src im aktuellen Verzeichnis liegt
    ('src/joystickhandler', 'src'),  # Kopiert config.ini ins Hauptverzeichnis des gebauten Pakets
    ('src/naobackend', 'src')  # Kopiert das Verzeichnis images in ein Unterverzeichnis 'images'
]


a = Analysis(['main.py'],
             pathex=['C:\\Users\\peter\\PycharmProjects\\naoChallange'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               added_files,
               [],
               upx=True,
               name='main')
