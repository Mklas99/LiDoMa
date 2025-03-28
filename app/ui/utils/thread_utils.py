"""Thread utilities for the Docker Manager application."""
import sys
import traceback
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    started = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    log = pyqtSignal(str)

class ThreadWorker(QThread):
    """Worker thread base class for Docker operations."""
    
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.setObjectName(f"{fn.__name__}_worker")
        
    def run(self):
        """Execute the function on the worker thread."""
        self.is_running = True
        self.signals.started.emit()
        thread_id = int(QThread.currentThreadId())
        
        # Log thread start
        msg = f"Starting worker thread {self.objectName()} (ID: {thread_id})"
        self.signals.log.emit(msg)
        logger.info(msg)
        
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            # Print the error to console for debugging
            logger.error(f"Error in worker thread {self.objectName()}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Emit the error signal with exception info
            exctype, value, tb = sys.exc_info()
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.is_running = False
            self.signals.finished.emit()
            msg = f"Finished worker thread {self.objectName()} (ID: {thread_id})"
            self.signals.log.emit(msg)
            logger.info(msg)

def run_in_thread(parent: QObject, 
                  callback: Callable, 
                  fn: Callable, 
                  *args, 
                  error_callback: Optional[Callable] = None,
                  finished_callback: Optional[Callable] = None,
                  log_callback: Optional[Callable] = None,
                  **kwargs) -> ThreadWorker:
    """
    Run a function in a separate thread and connect its signals.
    
    Args:
        parent: The parent object to ensure thread cleanup
        callback: Function to call with the result
        fn: Function to run in the thread
        *args: Arguments to pass to the function
        error_callback: Optional function to call if an error occurs
        finished_callback: Optional function to call when thread is done
        log_callback: Optional function to receive log messages
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The worker thread instance
    """
    # Create worker
    worker = ThreadWorker(fn, *args, **kwargs)
    
    # Connect signals
    worker.signals.result.connect(callback)
    
    if error_callback:
        worker.signals.error.connect(error_callback)
        
    if finished_callback:
        worker.signals.finished.connect(finished_callback)
        
    if log_callback:
        worker.signals.log.connect(log_callback)
    
    # Make sure the thread gets cleaned up when parent is destroyed
    worker.setParent(parent)
    
    # Start the thread
    worker.start()
    
    return worker
