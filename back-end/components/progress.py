import time

class ProgressTracker:
    def __init__(self):
        self.start_time = time.time()

<<<<<<< HEAD
    def reset(self):
        self.start_time = time.time()

    def update(self, current: int, total: int):
        self.current, self.total = current, total
=======
    def get_progress(self, index: int, total: int) -> str:
        self.index = str(index)
        self.total = str(total)
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
        elapsed_time = time.time() - self.start_time
        remaining_time = elapsed_time / self.current * (self.total - self.current)

        def format_hms(seconds: float) -> str:
            m, s = divmod(max(0, int(seconds)), 60)
            h, m = divmod(m, 60)
            return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

<<<<<<< HEAD
        self.progress = f"{format_hms(elapsed_time)}:{format_hms(remaining_time)}"
=======
        return f"{format_hms(elapsed_time)}>{format_hms(remain_time)}"
>>>>>>> 33ff4f4d2a054c99c2a9203335bb290e143cdebd
