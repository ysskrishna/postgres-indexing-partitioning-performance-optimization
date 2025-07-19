import time
from typing import Tuple, List, Any


class SimpleBenchmark:
    """Simple benchmarking for query performance comparison."""
    
    def __init__(self):
        self.results = []
    
    def time_query(self, db, query: str, params=None, description: str = "") -> Tuple[List[Tuple], float]:
        """Time a query execution and return results with timing."""
        start_time = time.time()
        results = db.execute_query(query, params)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Store result for comparison
        self.results.append({
            'description': description,
            'query': query,
            'time': execution_time,
            'row_count': len(results)
        })
        
        return results, execution_time
    
    def compare_results(self) -> None:
        """Compare and display benchmark results."""
        if len(self.results) < 2:
            print("Need at least 2 results to compare")
            return
        
        print("\n📊 Performance Comparison:")
        print("=" * 50)
        
        for i, result in enumerate(self.results, 1):
            print(f"{i}. {result['description']}")
            print(f"   Time: {result['time']:.4f} seconds")
            print(f"   Rows: {result['row_count']}")
            print()
        
        # Calculate improvement
        if len(self.results) == 2:
            time1, time2 = self.results[0]['time'], self.results[1]['time']
            improvement = time1 / time2 if time2 > 0 else float('inf')
            
            if improvement > 1:
                print(f"✨ Improvement: {improvement:.1f}x faster!")
            elif improvement < 1:
                print(f"⚠️  Slower by: {1/improvement:.1f}x")
            else:
                print("⚖️  No significant difference")
    
    def clear_results(self) -> None:
        """Clear stored results."""
        self.results = []
    
    def get_query_plan(self, db, query: str, params=None) -> str:
        """Get and display query execution plan."""
        plan = db.get_query_plan(query, params)
        print("\n🔍 Query Execution Plan:")
        print("=" * 30)
        print(plan)
        return plan 