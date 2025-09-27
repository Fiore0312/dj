"""
Threading Utilities for DJ GUI
Safe threading utilities for GUI updates and background operations.
"""

import threading
import time
import tkinter as tk
from typing import Callable, Any, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, Future
import logging
import queue
from functools import wraps

logger = logging.getLogger(__name__)


class GUIUpdater:
    """
    Thread-safe GUI updater that ensures all GUI updates happen on the main thread.
    Uses tkinter's after() method to schedule updates from background threads.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._update_queue = queue.Queue()
        self._running = True
        self._start_processor()

    def _start_processor(self):
        """Start the update processor on the main thread."""
        self._process_updates()

    def _process_updates(self):
        """Process queued GUI updates."""
        if not self._running:
            return

        try:
            # Process all queued updates
            while not self._update_queue.empty():
                try:
                    update_func, args, kwargs = self._update_queue.get_nowait()
                    update_func(*args, **kwargs)
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error processing GUI update: {e}")

        except Exception as e:
            logger.error(f"Error in update processor: {e}")

        # Schedule next processing cycle
        if self._running:
            self.root.after(16, self._process_updates)  # ~60 FPS

    def schedule_update(self, func: Callable, *args, **kwargs):
        """
        Schedule a GUI update to be executed on the main thread.

        Args:
            func: Function to execute on main thread
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        """
        if self._running:
            try:
                self._update_queue.put((func, args, kwargs), timeout=1.0)
            except queue.Full:
                logger.warning("GUI update queue is full, dropping update")

    def shutdown(self):
        """Shutdown the GUI updater."""
        self._running = False


class BackgroundWorker:
    """
    Manages background threads for non-GUI operations.
    Provides controlled execution and proper cleanup.
    """

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="DJ_Worker")
        self._active_tasks: Dict[str, Future] = {}
        self._shutdown = False

    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        """
        Submit a task for background execution.

        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Future object representing the task
        """
        if self._shutdown:
            raise RuntimeError("BackgroundWorker is shut down")

        # Cancel existing task with same ID if running
        if task_id in self._active_tasks:
            self._active_tasks[task_id].cancel()

        future = self.executor.submit(func, *args, **kwargs)
        self._active_tasks[task_id] = future

        # Clean up completed tasks
        def cleanup_task(fut):
            if task_id in self._active_tasks and self._active_tasks[task_id] is fut:
                del self._active_tasks[task_id]

        future.add_done_callback(cleanup_task)
        return future

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task."""
        if task_id in self._active_tasks:
            return self._active_tasks[task_id].cancel()
        return False

    def is_task_running(self, task_id: str) -> bool:
        """Check if a task is currently running."""
        if task_id in self._active_tasks:
            return not self._active_tasks[task_id].done()
        return False

    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Get result of a completed task."""
        if task_id in self._active_tasks:
            return self._active_tasks[task_id].result(timeout=timeout)
        raise KeyError(f"Task {task_id} not found")

    def shutdown(self, wait: bool = True):
        """Shutdown the background worker."""
        self._shutdown = True
        self.executor.shutdown(wait=wait)


class PeriodicTask:
    """
    Manages periodic tasks that run in the background.
    Useful for regular updates like audio level monitoring.
    """

    def __init__(self, interval: float, func: Callable, *args, **kwargs):
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def start(self):
        """Start the periodic task."""
        if self._running:
            logger.warning("Periodic task already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._running = True
        logger.debug(f"Started periodic task with {self.interval}s interval")

    def stop(self):
        """Stop the periodic task."""
        if not self._running:
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._running = False
        logger.debug("Stopped periodic task")

    def _run(self):
        """Internal task runner."""
        while not self._stop_event.is_set():
            try:
                start_time = time.time()
                self.func(*self.args, **self.kwargs)

                # Calculate sleep time to maintain consistent interval
                execution_time = time.time() - start_time
                sleep_time = max(0, self.interval - execution_time)

                if self._stop_event.wait(sleep_time):
                    break

            except Exception as e:
                logger.error(f"Error in periodic task: {e}")
                if self._stop_event.wait(1.0):  # Wait before retry
                    break

    @property
    def is_running(self) -> bool:
        """Check if the task is currently running."""
        return self._running


def thread_safe_gui_update(gui_updater: GUIUpdater):
    """
    Decorator to ensure GUI updates happen on the main thread.

    Args:
        gui_updater: GUIUpdater instance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if threading.current_thread() is threading.main_thread():
                # Already on main thread, execute directly
                return func(*args, **kwargs)
            else:
                # Schedule update on main thread
                gui_updater.schedule_update(func, *args, **kwargs)
        return wrapper
    return decorator


def background_task(worker: BackgroundWorker, task_id: Optional[str] = None):
    """
    Decorator to run a function as a background task.

    Args:
        worker: BackgroundWorker instance
        task_id: Optional task ID (defaults to function name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tid = task_id or func.__name__
            return worker.submit_task(tid, func, *args, **kwargs)
        return wrapper
    return decorator


class ThreadSafeCounter:
    """Thread-safe counter for tracking operations."""

    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        """Increment counter and return new value."""
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        """Decrement counter and return new value."""
        with self._lock:
            self._value -= amount
            return self._value

    def reset(self) -> int:
        """Reset counter to zero and return old value."""
        with self._lock:
            old_value = self._value
            self._value = 0
            return old_value

    @property
    def value(self) -> int:
        """Get current counter value."""
        with self._lock:
            return self._value


class RateLimiter:
    """Rate limiter for controlling update frequency."""

    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self._calls = []
        self._lock = threading.Lock()

    def can_proceed(self) -> bool:
        """Check if a call can proceed within rate limits."""
        with self._lock:
            now = time.time()
            # Remove old calls outside the time window
            self._calls = [call_time for call_time in self._calls if now - call_time < self.time_window]

            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False

    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        while not self.can_proceed():
            time.sleep(0.01)  # Small sleep to avoid busy waiting


class TaskManager:
    """
    High-level task manager combining all threading utilities.
    Provides a unified interface for GUI applications.
    """

    def __init__(self, root: tk.Tk, max_workers: int = 4):
        self.gui_updater = GUIUpdater(root)
        self.background_worker = BackgroundWorker(max_workers)
        self.periodic_tasks: Dict[str, PeriodicTask] = {}
        self._shutdown = False

    def schedule_gui_update(self, func: Callable, *args, **kwargs):
        """Schedule a GUI update."""
        self.gui_updater.schedule_update(func, *args, **kwargs)

    def submit_background_task(self, task_id: str, func: Callable, *args, **kwargs) -> Future:
        """Submit a background task."""
        return self.background_worker.submit_task(task_id, func, *args, **kwargs)

    def start_periodic_task(self, task_id: str, interval: float, func: Callable, *args, **kwargs):
        """Start a periodic task."""
        if task_id in self.periodic_tasks:
            self.periodic_tasks[task_id].stop()

        task = PeriodicTask(interval, func, *args, **kwargs)
        task.start()
        self.periodic_tasks[task_id] = task
        logger.info(f"Started periodic task '{task_id}' with {interval}s interval")

    def stop_periodic_task(self, task_id: str):
        """Stop a periodic task."""
        if task_id in self.periodic_tasks:
            self.periodic_tasks[task_id].stop()
            del self.periodic_tasks[task_id]
            logger.info(f"Stopped periodic task '{task_id}'")

    def shutdown(self):
        """Shutdown all managed tasks and workers."""
        if self._shutdown:
            return

        self._shutdown = True
        logger.info("Shutting down task manager...")

        # Stop all periodic tasks
        for task_id in list(self.periodic_tasks.keys()):
            self.stop_periodic_task(task_id)

        # Shutdown background worker
        self.background_worker.shutdown(wait=True)

        # Shutdown GUI updater
        self.gui_updater.shutdown()

        logger.info("Task manager shutdown complete")


# Export main classes and utilities
__all__ = [
    'GUIUpdater', 'BackgroundWorker', 'PeriodicTask', 'TaskManager',
    'ThreadSafeCounter', 'RateLimiter',
    'thread_safe_gui_update', 'background_task'
]