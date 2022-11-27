import time
import os


# Print iterations progress
def printProgressBar (iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = None, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    if length is None:
        term_width = os.get_terminal_size()[0]
        length = term_width - len(prefix) - len(suffix) - 25
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
        return False

# A List of Items
items = list(range(0, 57))
l = len(items)

# Initial call to print 0% progress
printProgressBar(0, l)
for i, item in enumerate(items):
    time.sleep(0.1)
    if i % 50 == 0: print("Log message")
    # Update Progress Bar
    printProgressBar(i + 1, l)
