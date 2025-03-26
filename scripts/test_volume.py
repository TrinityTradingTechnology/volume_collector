import unittest


volumes = dict()

def get_5m_volume(symbol, hour, minute):
    """
    Returns the sum of volume for the current 5-minute window
    (where window boundaries are aligned to minutes divisible by 5)
    """
    global volumes  # Declare volumes as a global variable

    # Calculate the starting minute of the current 5-minute window
    window_start_minute = (minute // 5) * 5
    window_end_minute = window_start_minute + 4

    # Initialize sum
    sum_volume = 0

    # Iterate through each minute in the 5-minute window
    for current_min in range(window_start_minute, window_end_minute + 1):
        current_hour = hour
        
        # Handle minute overflow (if window_end_minute >= 60)
        if current_min >= 60:
            adjusted_min = current_min - 60
            adjusted_hour = current_hour + 1
            # Handle hour overflow
            if adjusted_hour >= 24:
                adjusted_hour -= 24
            sum_volume += volumes.get(symbol, {}).get(adjusted_hour, {}).get(adjusted_min, 0)
        else:
            sum_volume += volumes.get(symbol, {}).get(current_hour, {}).get(current_min, 0)

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

    def test_exact_five_minutes(self):
        global volumes
        volumes = {
            'AAPL': {
                12: {5: 100, 6: 200, 7: 300, 8: 400, 9: 500}
            }
        }

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
                13: {0: 100, 1: 200, 2: 300, 3: 400, 4: 500}
            }
        }
        
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
                0: {0: 600, 1: 200, 2: 200}
            }
        }
        
        result = get_5m_volume('AAPL', 0, 1)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 1000
        })

    def test_missing_data(self):
        global volumes
        volumes = {
            'AAPL': {}
        }
        
        result = get_5m_volume('AAPL', 12, 30)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 0
        })

    def test_invalid_symbol(self):
        global volumes
        volumes = {}
        
        result = get_5m_volume('AAPL', 12, 30)
        self.assertEqual(result, {
            "status": "success",
            "symbol": "AAPL",
            "volume": 0
        })

if __name__ == '__main__':
    unittest.main()
