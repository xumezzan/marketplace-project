import sys
print("SYS PATH:", sys.path)
try:
    import telegram
    print("TELEGRAM FILE:", telegram.__file__)
except ImportError as e:
    print("IMPORT ERROR:", e)
