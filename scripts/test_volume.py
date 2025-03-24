import unittest


volumes = dict()


# Function to test
def get_5m_volume(symbol, hour, minute):
    """
    Returns the sum of volume for the last five minutes
    """
    global volumes  # Declare volumes as a global variable

    # Convert time to minutes since midnight
    current_minutes = hour * 60 + minute

    # Calculate start time (5 minutes ago)
    start_minutes = current_minutes - 5

    # Initialize sum
    sum_volume = 0

    # Handle both normal case and midnight wrap-around
    if start_minutes >= 0:
        # Normal case - no midnight crossing
        for m in range(start_minutes, current_minutes):
            h = m // 60
            min = m % 60
            sum_volume += volumes.get(symbol, {}).get(h, {}).get(min, 0)
    else:
        # Midnight crossing - handle two segments
        # First segment: from start_minutes (negative) to midnight (1440 minutes)
        for m in range(start_minutes + 1440, 1440):
            h = m // 60
            min = m % 60
            sum_volume += volumes.get(symbol, {}).get(h, {}).get(min, 0)
        # Second segment: from midnight (0) to current_minutes
        for m in range(0, current_minutes):
            h = m // 60
            min = m % 60
            sum_volume += volumes.get(symbol, {}).get(h, {}).get(min, 0)

    return {
        "status": "success",
        "symbol": symbol,
        "volume": sum_volume
    }

# Unit tests
class TestGet5mVolume(unittest.TestCase):
    def setUp(self):
        global volumes
        volumes = {}  # Reset volumes before each test

    def print_minutes_range(self, hour, minute):
        current_minutes = hour * 60 + minute
        start_minutes = current_minutes - 5
        
        if start_minutes < 0:
            start_minutes += 24 * 60
        
        print(f"\nTesting time: {hour:02d}:{minute:02d}")
        print("Minutes range being checked:")
        for m in range(start_minutes, current_minutes):
            h = m // 60 % 24
            min = m % 60
            print(f"  {h:02d}:{min:02d}")

    def test_exact_five_minutes(self):
        global volumes
        volumes = {
            'AAPL': {
                12: {0: 100, 1: 200, 2: 300, 3: 400, 4: 500}
            }
        }

        self.print_minutes_range(12, 5)
        result = get_5m_volume('AAPL', 12, 5)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 1500
        })

    def test_partial_minutes(self):
        global volumes
        volumes = {
            'AAPL': {
                12: {55: 100, 56: 200, 57: 300, 58: 400, 59: 500}
            }
        }
        
        self.print_minutes_range(13, 0)
        result = get_5m_volume('AAPL', 13, 0)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 1500
        })

    def test_midnight_transition(self):
        global volumes
        volumes = {
            'AAPL': {
                23: {55: 100, 56: 200, 57: 300, 58: 400, 59: 500},
                0: {0: 600}
            }
        }
        
        self.print_minutes_range(0, 1)
        result = get_5m_volume('AAPL', 0, 1)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 2000
        })

    def test_missing_data(self):
        global volumes
        volumes = {
            'AAPL': {}
        }
        
        self.print_minutes_range(12, 30)
        result = get_5m_volume('AAPL', 12, 30)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 0
        })

    def test_invalid_symbol(self):
        global volumes
        volumes = {}
        
        self.print_minutes_range(12, 30)
        result = get_5m_volume('AAPL', 12, 30)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 0
        })

if __name__ == '__main__':
    unittest.main()
