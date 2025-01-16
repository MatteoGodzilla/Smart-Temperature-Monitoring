from time import time

class Timer():
    def __init__(self, wait_time:float=100.00):
        self.threshold = wait_time
        self.reset()

    def set(self):
        self.reset()
        self.started = True

    def reset(self) -> None:
        self.started = False
        self.start_time = time()
        self.elapsed = time()

    def update(self) -> None:
        self.elapsed = time() - self.start_time

    def is_over(self) -> bool:
        return ( self.elapsed >= self.threshold )

    def is_set(self) -> bool:
        return self.started
