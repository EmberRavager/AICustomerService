# Test Tool Manager

# Import necessary libraries and classes
from tool_manager import ToolManager
import unittest


class TestToolManager(unittest.TestCase):

    def setUp(self):
        self.manager = ToolManager()

    def test_add_tool(self):
        self.manager.add_tool("Hammer")
        self.assertIn("Hammer", self.manager.tools)

    def test_remove_tool(self):
        self.manager.add_tool("Hammer")
        self.manager.remove_tool("Hammer")
        self.assertNotIn("Hammer", self.manager.tools)

    def test_has_tool(self):
        self.manager.add_tool("Hammer")
        self.assertTrue(self.manager.has_tool("Hammer"))
        self.assertFalse(self.manager.has_tool("Screwdriver"))


if __name__ == '__main__':
    unittest.main()