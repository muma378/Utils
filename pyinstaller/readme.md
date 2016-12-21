# a demo to demonstrate how to bundle files to a app with pyinstaller

1. uses `pyi-makespec --onefile freqde.py` to create a spec file;
2. modifies freqde.spec, to add *.exe, *.dll to a.datas;
3. uses `pyinstaller freqde.spec` to bundle files to an executable file.

# noted that files are unarchived to a temp directory, therefore, the executable file shall be prefixed with an absolute path - wrapping files with function resource_path.

# besides, multiprocessing is not supported that well, some hacks are necessary to work with the module:
1. appends `multiprocessing.freeze_support() ` after `if __name__ == '__main__':`;
2. defines custom class `_Popen` and assigns `forking.Popen = _Popen` to use queue without warning;
3. not support multiprocessing.Pool