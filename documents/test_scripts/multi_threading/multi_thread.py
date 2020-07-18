# Import Python modules
import time
import os
import multiprocessing
import psutil
from random import randint
import math

# Main task function
def main_process(item_queue, args_array):
    # Go through each link in the array passed in.
    while not item_queue.empty():
        # Get the next item in the queue
        item = item_queue.get()
        # Create a random number to simulate threads that
        # are not all going to be the same
        randomizer = randint(100, 100000)
        for i in range(randomizer):
            algo_seed = math.sqrt(math.sqrt(i * randomizer) % randomizer)
        # Check if the thread should continue based on current load balance
        if spool_down_load_balance():
            print("Process " + str(os.getpid()) + " saying goodnight...")
            break

# This function will build a queue and
def start_thread_process(queue_pile, args_array):
    # Create a Queue to hold link pile and share between threads
    item_queue = multiprocessing.Queue()
    # Put all the initial items into the queue
    for item in queue_pile:
        item_queue.put(item)
    # Append the load balancer thread to the loop
    load_balance_process = multiprocessing.Process(target=spool_up_load_balance, args=(item_queue, args_array))
    # Loop through and start all processes
    load_balance_process.start()
    # This .join() function prevents the script from progressing further.
    load_balance_process.join()

# Spool down the thread balance when load is too high
def spool_down_load_balance():
    # Get the count of CPU cores
    core_count = psutil.cpu_count()
    # Calulate the short term load average of past minute
    one_minute_load_average = os.getloadavg()[0] / core_count
    # If load balance above the max return True to kill the process
    if one_minute_load_average > args_array['cpu_target']:
        print("-Unacceptable load balance detected. Killing process " + str(os.getpid()) + "...")
        return True

# Load balancer thread function
def spool_up_load_balance(item_queue, args_array):

    print("[Starting load balancer...]")
    # Get the count of CPU cores
    core_count = psutil.cpu_count()
    # While there is still links in queue
    while not item_queue.empty():
        print("[Calculating load balance...]")
        # Check the 1 minute average CPU load balance
        # returns 1,5,15 minute load averages
        one_minute_load_average = os.getloadavg()[0] / core_count
        # If the load average much less than target, start a group of new threads
        if one_minute_load_average < args_array['cpu_target'] / 2:
            # Print message and log that load balancer is starting another thread
            print("Starting another thread group due to low CPU load balance of: " + str(one_minute_load_average * 100) + "%")
            time.sleep(5)
            # Start another group of threads
            for i in range(3):
                start_new_thread = multiprocessing.Process(target=main_process,args=(item_queue, args_array))
                start_new_thread.start()
            # Allow the added threads to have an impact on the CPU balance
            # before checking the one minute average again
            time.sleep(20)

        # If load average less than target start single thread
        elif one_minute_load_average < args_array['cpu_target']:
            # Print message and log that load balancer is starting another thread
            print("Starting another single thread due to low CPU load balance of: " + str(one_minute_load_average * 100) + "%")
            # Start another thread
            start_new_thread = multiprocessing.Process(target=main_process,args=(item_queue, args_array))
            start_new_thread.start()
            # Allow the added threads to have an impact on the CPU balance
            # before checking the one minute average again
            time.sleep(20)

        else:
            # Print CPU load balance
            print("Reporting stable CPU load balance: " + str(one_minute_load_average * 100) + "%")
            # Sleep for another minute while
            time.sleep(20)

if __name__=="__main__":

    # Set the queue size
    queue_size = 10000
    # Define an arguments array to pass around all the values
    args_array = {
        # Set some initial CPU load values as a CPU usage goal
        "cpu_target" : 0.60,
        # When CPU load is significantly low, start this number
        # of threads
        "thread_group_size" : 3
    }

    # Create an array of fixed length to act as queue
    queue_pile = list(range(queue_size))
    # Set main process start time
    start_time = time.time()
    # Start the main process
    start_thread_process(queue_pile, args_array)
    print('[Finished processing the entire queue! Time consuming:{0} Time Finished: {1}]'.format(time.time() - start_time, time.strftime("%c")))
