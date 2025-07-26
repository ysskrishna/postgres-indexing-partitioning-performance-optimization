import time
from typing import Tuple, List, Any


class SimpleBenchmark:
    def time_query(self, db, query: str, params=None) -> Tuple[List[Tuple], float]:
        """Time a query execution and return results with timing."""
        start_time = time.time()
        results = db.execute_query(query, params)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        output ={
            'query': query,
            'time': execution_time,
            'row_count': len(results)
        }
        
        return execution_time, output