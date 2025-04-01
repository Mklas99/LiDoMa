import logging
from PyQt5.QtCore import QObject, pyqtSignal

class QtLogHandler(logging.Handler, QObject):
    """
    Custom logging handler that emits Qt signals for log messages.
    This allows log messages to be displayed in the UI.
    """
    log_message = pyqtSignal(str)
    
    def __init__(self, level=logging.NOTSET):
        QObject.__init__(self)
        logging.Handler.__init__(self, level)
        # Use same format as the main logger for consistency
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S'))
        self.registered = True
        
    def emit(self, record):
        """Process a log record and emit a signal with formatted message."""
        try:
            msg = self.format(record)
            self.log_message.emit(msg)
        except Exception:
            self.handleError(record)
            
    def shutdown(self):
        """Properly shutdown the handler to avoid exceptions during app exit."""
        # Prevent access during Python's atexit logging shutdown
        self.registered = False
        self.acquire()
        try:
            # Close and unregister from root logger
            self.close()
            root_logger = logging.getLogger()
            if self in root_logger.handlers:
                root_logger.removeHandler(self)
        finally:
            self.release()
