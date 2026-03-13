# Test Tool Manager

# Import necessary libraries and classes
import asyncio
import unittest

from app.agents.tool_manager import ToolManager


class TestToolManager(unittest.TestCase):

    def setUp(self):
        self.manager = ToolManager()

    def test_default_tools_registered(self):
        self.assertIn("calculator", self.manager.list_tools())

    def test_get_tool(self):
        tool = self.manager.get_tool("calculator")
        self.assertIsNotNone(tool)

    def test_execute_tool(self):
        result = asyncio.run(self.manager.execute_tool("calculator", expression="2+3"))
        self.assertIn("5", result)


if __name__ == '__main__':
    unittest.main()
