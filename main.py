import random
import time
import threading
import heapq


class Process:
    def __init__(self, id, arrival_time, exec_time, start_deadline, end_deadline, score):
        self.id = id
        self.arrival_time = arrival_time
        self.exec_time = exec_time
        self.start_deadline = start_deadline
        self.end_deadline = end_deadline
        self.score = score
        self.start_time = None
        self.finish_time = None

    def __lt__(self, other):
        if self.score == other.score:
            return self.start_deadline < other.start_deadline
        return self.score > other.score

    def __str__(self):
        return f"Process {self.id} (Score: {self.score}, Arrival: {self.arrival_time}, Exec Time: {self.exec_time})"


input_queue = []
ready_queue = []
cpu_count = 3
mutex_input_queue = threading.Lock()
mutex_ready_queue = threading.Lock()
cpu_semaphore = threading.Semaphore(cpu_count)
process_counter = 0
total_score = 0
completed_processes = []
missed_processes = []
waiting_times = []
response_times = []


def process_generator():
    global process_counter
    while process_counter < 50:
        arrival_time = time.time()
        exec_time = random.randint(1, 10)
        start_deadline = random.randint(
            int(arrival_time)+1, int(arrival_time) + 5)
        end_deadline = start_deadline + exec_time
        score = random.randint(1, 100)
        process_counter += 1
        process = Process(process_counter, arrival_time,
                          exec_time, start_deadline, end_deadline, score)

        with mutex_input_queue:
            input_queue.append(process)

        print(f"Process {process.id} generated and added to input queue.")
        time.sleep(random.uniform(0.5, 1.5))


def scheduler():
    while process_counter < 50:
        with mutex_input_queue:
            if input_queue:
                process = input_queue.pop(0)
                if process.start_deadline > time.time():
                    # if process.arrival_time + process.exec_time > process.end_deadline:
                    #     print(f"Process {process.id} will miss the deadline!")

                    # else:
                    with mutex_ready_queue:
                        if len(ready_queue) < 20:
                            heapq.heappush(ready_queue, process)
                        else:
                            if process.score > ready_queue[0].score:
                                removed_process = heapq.heappop(
                                    ready_queue)
                                print(
                                    f"Process {removed_process.id} removed from ready queue.")
                                heapq.heappush(ready_queue, process)
                                print(
                                    f"Process {process.id} added to ready queue.")
                                with mutex_input_queue:
                                    input_queue.append(removed_process)
                                    print(
                                        f"Process {removed_process.id} returned to input queue.")
                    print(f"Scheduler added {process} to ready queue.")
                else:
                    print(f"Process {process.id} will miss the deadline!")
        time.sleep(0.1)


def cpu(cpu_id):
    global total_score
    while True:
        cpu_semaphore.acquire()
        with mutex_ready_queue:
            if ready_queue:

                process = heapq.heappop(ready_queue)
                process.start_time = time.time()

                print(f"CPU {cpu_id} started executing {process}")
                time.sleep(process.exec_time)
                process.finish_time = time.time()
                total_score += process.score
                completed_processes.append(process)
                print(f"CPU {cpu_id} finished executing {
                      process}. Total score: {total_score}")
                # if process.finish_time > process.end_deadline:
                #     print(f"Process {process.id} misses the deadline.")
            else:
                print(f"CPU {cpu_id} found no process to execute.")
        cpu_semaphore.release()
        time.sleep(0.5)


def print_results():
    global total_score
    missed_processes = 0
    total_waiting_time = 0
    total_response_time = 0
    for process in completed_processes:
        if process.finish_time > process.end_deadline:
            missed_processes += 1
        total_waiting_time += process.start_time - process.arrival_time
        total_response_time += process.finish_time - process.arrival_time
    avg_waiting_time = total_waiting_time / \
        len(completed_processes) if completed_processes else 0
    avg_response_time = total_response_time / \
        len(completed_processes) if completed_processes else 0

    print(f"\nTotal score: {total_score}")
    print(f"Missed processes: {missed_processes}")
    print(f"Average waiting time: {avg_waiting_time:.2f} seconds")
    print(f"Average response time: {avg_response_time:.2f} seconds")
    print("\nCompleted processes:")
    for process in completed_processes:
        print(f"{process} started at {process.start_time} and finished at {
              process.finish_time}, Score: {process.score}")


def start_system():

    generator_thread = threading.Thread(target=process_generator)
    generator_thread.daemon = True
    generator_thread.start()
    scheduler_thread = threading.Thread(target=scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    cpu_threads = []
    for i in range(cpu_count):
        cpu_thread = threading.Thread(target=cpu, args=(i+1,))
        cpu_thread.daemon = True
        cpu_threads.append(cpu_thread)
        cpu_thread.start()
    generator_thread.join()
    scheduler_thread.join()
    print_results()


if __name__ == "__main__":
    start_system()
