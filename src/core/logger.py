from rich.console import Console


class MyLogger:
    def __init__(self):
        self.console = Console(record=True)
    
    def print(self, message: str, console_only: bool = False, report_only: bool = False):
        """
        Log a message with options:
        - console_only=True: Show only in console, do NOT save to report.
        - report_only=True: Save only to report, do NOT print in console.
        - Default: Show in console AND save to report.
        """
        if console_only:
            # Console only: print and remove from record
            self.console.print(message)
            self.console._record_buffer.pop()

        elif report_only:
            # Report only: capture silently without printing
            self.console.begin_capture()
            self.console.print(message)
            captured = self.console.end_capture()
            self.console._record_buffer.append(captured)

        else:
            # Default: console + report
            self.console.print(message)

    def save_html(self, filename):
        self.console.save_html(filename)
    
console = MyLogger()