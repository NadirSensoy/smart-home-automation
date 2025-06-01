# test_automation.py

import unittest
from src.automation.rules_engine import RulesEngine
from src.automation.scheduler import Scheduler

class TestAutomation(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.rules_engine = RulesEngine()
        self.scheduler = Scheduler()

    def test_rule_evaluation(self):
        """Test the rule evaluation logic in the RulesEngine."""
        # Example rule: If temperature > 25, turn on the AC
        self.rules_engine.add_rule("temperature > 25", "turn_on_ac")
        result = self.rules_engine.evaluate({"temperature": 30})
        self.assertTrue(result["turn_on_ac"], "AC should be turned on when temperature is above 25")

    def test_scheduler_task_execution(self):
        """Test the task execution in the Scheduler."""
        self.scheduler.schedule_task("turn_on_lights", 5)  # Schedule to turn on lights after 5 seconds
        self.scheduler.execute_tasks()  # Simulate task execution
        self.assertIn("turn_on_lights", self.scheduler.executed_tasks, "Scheduled task should be executed")

    def tearDown(self):
        """Clean up after each test."""
        self.rules_engine.clear_rules()
        self.scheduler.clear_tasks()

if __name__ == '__main__':
    unittest.main()