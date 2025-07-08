def run(args):
    text = "Hello"
    if args:
        for arg in enumerate(args):
            text += " " + arg[1]
    print(text + "!")