import logging
from typing import List, Callable, Any
from PyQt5.QtCore import QThread, QTimer  # Add QTimer import

class ThreadManager:
    """Utility for managing worker threads to prevent premature garbage collection."""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Singleton pattern to ensure only one thread manager exists."""
        if cls._instance is None:
            cls._instance = ThreadManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the thread manager."""
        self.logger = logging.getLogger(__name__)
        self.active_threads = []
        
    def start_thread(self, worker: QThread, finished_callback: Callable = None) -> QThread:
        """Start a worker thread and store a reference to it.
        
        Args:
            worker: The QThread worker to start
            finished_callback: Optional callback to run when thread finishes
            
        Returns:
            The worker thread (for convenience)
        """
        # Connect finished signal to cleanup
        worker.finished.connect(lambda: self._cleanup_thread(worker))
        
        # Connect custom finished callback if provided
        if finished_callback:
            worker.finished.connect(finished_callback)
            
        # Store the thread and start it
        self.active_threads.append(worker)
        worker.start()
        
        self.logger.debug(f"Started thread {worker.__class__.__name__}. "
                          f"Active threads: {len(self.active_threads)}")
        
        return worker
    
    def _cleanup_thread(self, worker: QThread):
        """Remove thread from the tracking list when it's done."""
        if worker in self.active_threads:
            QTimer.singleShot(1000, lambda: self._finalize_thread_cleanup(worker))
            self.logger.debug(f"Thread {worker.__class__.__name__} scheduled for cleanup. "
                              f"Active threads: {len(self.active_threads)}")

    def _finalize_thread_cleanup(self, worker: QThread):
        """Complete the cleanup of a worker thread after delay."""
        if worker in self.active_threads:
            self.active_threads.remove(worker)
            self.logger.debug(f"Thread {worker.__class__.__name__} removed. "
                              f"Active threads: {len(self.active_threads)}")
            
    def cleanup_all(self):
        """Clean up all running threads (call on application exit)."""
        for worker in list(self.active_threads):
            if worker.isRunning():
                self.logger.debug(f"Terminating thread {worker.__class__.__name__}")
                worker.terminate()
                worker.wait()
            
            # Remove from list
            if worker in self.active_threads:
                self.active_threads.remove(worker)
                
        self.logger.debug("All threads cleaned up")
