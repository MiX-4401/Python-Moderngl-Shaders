import threading as thr

# Define a lock
lock = thr.Lock()
condition = thr.Condition(lock)

iterations = 10
current_thread = 1
total_threads  = 3

log = []

def concurrent_thread(name:str, thread_number:int):
    global iterations, log, condition, current_thread, total_threads

    for x in range(iterations):
        with condition:
            # Wait until it's this thread's turn
            while current_thread != thread_number:
                condition.wait()
            
            # Code
            log.append(f"{name} is doing work")
            log.append(f"{name} has released the lock")

            # Switch to the other thread
            current_thread = thread_number % total_threads + 1
            condition.notify_all()

def main_thread():
    global iterations, log, lock

    thread_1 = thr.Thread(target=concurrent_thread, daemon=True, args=("thread-1", 1))
    thread_2 = thr.Thread(target=concurrent_thread, daemon=True, args=("thread-2", 2))
    thread_3 = thr.Thread(target=concurrent_thread, daemon=True, args=("thread-3", 3))
    thread_1.start()
    thread_2.start()
    thread_3.start()

    thread_1.join()
    thread_2.join()
    thread_3.join()


# Run the main function
if __name__ == "__main__":
    main_thread()
    print("-"*5, "Log", "-"*5)
    for x in log:
        print(x)
