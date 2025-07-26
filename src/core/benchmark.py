import time
from dataclasses import dataclass, field
from contextlib import contextmanager
from datetime import datetime
from typing import Optional


@dataclass
class BenchmarkResult:
    """Represents the result of a single benchmark run."""
    name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    row_count: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    

class SimpleBenchmark:
    
    @contextmanager
    def measure_performance(self, name: str):
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = self.process.cpu_percent()
        
        result = BenchmarkResult(name=name)
        
        try:
            yield result
            
            # Measure end metrics
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            end_cpu = self.process.cpu_percent()
            
            result.execution_time = end_time - start_time
            result.memory_usage = end_memory - start_memory
            result.cpu_usage = (start_cpu + end_cpu) / 2
            
        except Exception as e:
            result.error = str(e)
            raise
        
    
    def benchmark_query(self, db, query: str, params=None) -> BenchmarkResult:
        """Time a query execution and return results with timing."""
        
        with self.measure_performance(name="time_query") as result:
            start_time = time.time()
            results = db.execute_query(query, params)
            
            execution_time = time.time() - start_time
            
            result.execution_time = execution_time
            result.row_count = len(results)
        
        return result
    
    @staticmethod
    def timed(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        return time.time() - start, result