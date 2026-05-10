"""
Locust load testing script for 1MR Financial API
Targets: 17,000 requests per second
Endpoint: POST /read/balance
"""

import random
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser


class FinancialApiUser(FastHttpUser):
    """Load test user simulating balance read requests"""

    wait_time = between(0.001, 0.01)  # Minimal wait between requests

    def on_start(self):
        """Initialize user with valid credentials from database"""
        self.user_num = random.randint(1, 10000)
        self.user_id = f"USER-{self.user_num:04d}"
        self.pin_code = f"{self.user_num % 1000000:06d}"

    @task
    def read_balance(self):
        """Simulate a balance read request"""
        payload = {
            "user_unique_id": self.user_id,
            "PINCode": self.pin_code
        }

        with self.client.post(
            "/read/balance",
            json=payload,
            catch_response=True
        ) as response:
            # Handle both success (200) and auth failures (401)
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class HighConcurrencyUser(FastHttpUser):
    """Alternative user class for ultra-high concurrency testing"""

    wait_time = between(0, 0.001)  # Minimal to zero wait

    def on_start(self):
        self.user_num = random.randint(1, 10000)
        self.user_id = f"USER-{self.user_num:04d}"
        self.pin_code = f"{self.user_num % 1000000:06d}"

    @task
    def read_balance(self):
        payload = {
            "user_unique_id": self.user_id,
            "PINCode": self.pin_code
        }

        with self.client.post(
            "/read/balance",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test start information"""
    print("\n" + "="*60)
    print("STARTING LOAD TEST FOR FINANCIAL API")
    print(f"Target: 17,000 RPS")
    print(f"Endpoint: POST /read/balance")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary statistics"""
    print("\n" + "="*60)
    print("LOAD TEST COMPLETED")
    print("="*60 + "\n")
