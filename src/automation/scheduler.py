# scheduler.py

import time
import threading
from datetime import datetime, timedelta

class Scheduler:
    def __init__(self, interval=60):
        """
        Initializes the Scheduler with a specified interval in seconds.
        
        :param interval: Time interval in seconds for scheduling tasks.
        """
        self.interval = interval
        self.tasks = []
        self.running = False

    def add_task(self, task, run_at):
        """
        Adds a task to the scheduler with a specified run time.
        
        :param task: The function to be executed.
        :param run_at: The datetime when the task should be executed.
        """
        self.tasks.append((task, run_at))

    def start(self):
        """
        Starts the scheduler to execute tasks at their scheduled times.
        """
        self.running = True
        threading.Thread(target=self.run).start()

    def run(self):
        """
        The main loop that checks for tasks to execute at each interval.
        """
        while self.running:
            now = datetime.now()
            for task, run_at in self.tasks:
                if now >= run_at:
                    task()  # Execute the task
                    self.tasks.remove((task, run_at))  # Remove the task after execution
            time.sleep(self.interval)

    def stop(self):
        """
        Stops the scheduler from executing tasks.
        """
        self.running = False

# Example usage
if __name__ == "__main__":
    def example_task():
        print(f"Task executed at {datetime.now()}")

    scheduler = Scheduler(interval=5)  # Check every 5 seconds
    scheduler.add_task(example_task, datetime.now() + timedelta(seconds=10))  # Schedule task for 10 seconds later
    scheduler.start()

    # Let the scheduler run for a while
    time.sleep(30)
    scheduler.stop()  # Stop the scheduler after 30 seconds