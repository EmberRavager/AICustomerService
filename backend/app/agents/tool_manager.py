"""
工具管理系统 - 智能 Agent 调用工具的核心
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from loguru import logger

class ToolType(str, Enum):
    CALCULATOR = "calculator"
    WEATHER = "weather"
    KNOWLEDGE_SEARCH = "knowledge_search"
    CREATE_TICKET = "create_ticket"
    QUERY_ORDER = "query_order"
    SEND_EMAIL = "send_email"
    DATABASE = "database"
    CUSTOM = "custom"

dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None
    default: Optional[Any] = None

dataclass
class ToolSchema:
    name: str
    description: str
    parameters: List[ToolParameter]
    category: ToolType
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type,
                        "description": p.description,
                        **({"enum": p.enum} if p.enum else {}),
                        **({"default": p.default} if p.default is not None else {})
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            }
        }

class BaseTool(ABC):
    def __init__(self):
        self.schema = self._get_schema()
    
    @abstractmethod
    def _get_schema(self) -> ToolSchema:
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        return self.schema.to_dict()

class CalculatorTool(BaseTool):
    def _get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="calculator",
            description="执行数学计算，支持基本的算术运算",
            category=ToolType.CALCULATOR,
            parameters=[
                ToolParameter(
                    name="expression",
                    type="string",
                    description="数学表达式，如: 2+3, 10*5, sqrt(16)",
                    required=True
                )
            ],
            examples=[
                {"expression": "2+3", "result": "5"},
                {"expression": "sqrt(16)", "result": "4"}
            ]
        )
    
    async def execute(self, expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}}, {
                "sqrt": __import__("math").sqrt,
                "sin": __import__("math").sin,
                "cos": __import__("math").cos,
                "tan": __import__("math").tan,
                "log": __import__("math").log,
                "exp": __import__("math").exp,
            })
            return f"计算结果: {result}"
        except Exception as e:
            logger.error(f"计算错误: {e}")
            return f"计算错误: {str(e)}"

class WeatherTool(BaseTool):
    def _get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="get_weather",
            description="查询指定城市的天气信息",
            category=ToolType.WEATHER,
            parameters=[
                ToolParameter(
                    name="city",
                    type="string",
                    description="城市名称，如: 北京, 上海, 深圳",
                    required=True
                ),
                ToolParameter(
                    name="days",
                    type="number",
                    description="查询天数，默认1天，最多7天",
                    required=False,
                    default=1
                )
            ],
            examples=[
                {"city": "北京", "days": 1},
                {"city": "上海", "days": 3}
            ]
        )
    
    async def execute(self, city: str, days: int = 1) -> str:
        try:
            weather_data = {
                "城市": city,
                "天气": "晴",
                "温度": "25°C",
                "湿度": "60%",
                "风力": "3级"
            }
            return json.dumps(weather_data, ensure_ascii=False)
        except Exception as e:
            logger.error(f"天气查询错误: {e}")
            return f"天气查询失败: {str(e)}"

class KnowledgeSearchTool(BaseTool):
    def _get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="knowledge_search",
            description="在知识库中搜索相关信息",
            category=ToolType.KNOWLEDGE_SEARCH,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="搜索关键词",
                    required=True
                ),
                ToolParameter(
                    name="category",
                    type="string",
                    description="搜索分类",
                    required=False,
                    enum=["产品", "服务", "购买", "售后", "技术"]
                ),
                ToolParameter(
                    name="limit",
                    type="number",
                    description="返回结果数量，默认3",
                    required=False,
                    default=3
                )
            ]
        )
    
    async def execute(self, query: str, category: Optional[str] = None, limit: int = 3) -> str:
        try:
            results = f"找到关于 '{query}' 的信息（分类: {category or '全部'}）"
            return results
        except Exception as e:
            logger.error(f"知识库搜索错误: {e}")
            return f"知识库搜索失败: {str(e)}"

class CreateTicketTool(BaseTool):
    def _get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="create_ticket",
            description="创建客服工单或技术支持工单",
            category=ToolType.CREATE_TICKET,
            parameters=[
                ToolParameter(
                    name="title",
                    type="string",
                    description="工单标题",
                    required=True
                ),
                ToolParameter(
                    name="description",
                    type="string",
                    description="问题描述",
                    required=True
                ),
                ToolParameter(
                    name="priority",
                    type="string",
                    description="优先级",
                    required=False,
                    enum=["低", "中", "高", "紧急"],
                    default="中"
                ),
                ToolParameter(
                    name="category",
                    type="string",
                    description="工单类型",
                    required=False,
                    enum=["问题", "建议", "投诉", "其他"],
                    default="问题"
                )
            ]
        )
    
    async def execute(self, title: str, description: str, priority: str = "中", category: str = "问题") -> str:
        try:
            import uuid
            ticket_id = str(uuid.uuid4())[:8]
            return f"✅ 工单已创建！\n工单号: {ticket_id}\n标题: {title}\n优先级: {priority}"
        except Exception as e:
            logger.error(f"创建工单错误: {e}")
            return f"创建工单失败: {str(e)}"

class QueryOrderTool(BaseTool):
    def _get_schema(self) -> ToolSchema:
        return ToolSchema(
            name="query_order",
            description="查询订单状态和物流信息",
            category=ToolType.QUERY_ORDER,
            parameters=[
                ToolParameter(
                    name="order_id",
                    type="string",
                    description="订单号",
                    required=True
                )
            ]
        )
    
    async def execute(self, order_id: str) -> str:
        try:
            order_data = {
                "订单号": order_id,
                "状态": "已发货",
                "商品": "智能音箱",
                "价格": "￥299",
                "物流信息": "中通快递 已签收"
            }
            return json.dumps(order_data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"订单查询错误: {e}")
            return f"订单查询失败: {str(e)}"

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        default_tools = [
            CalculatorTool(),
            WeatherTool(),
            KnowledgeSearchTool(),
            CreateTicketTool(),
            QueryOrderTool(),
        ]
        for tool in default_tools:
            self.register(tool)
    
    def register(self, tool: BaseTool):
        self.tools[tool.schema.name] = tool
        logger.info(f"工具已注册: {tool.schema.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        return self.tools.get(tool_name)
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        tool = self.get_tool(tool_name)
        if not tool:
            return f"错误: 工具 '{tool_name}' 不存在"
        logger.info(f"执行工具: {tool_name}, 参数: {kwargs}")
        result = await tool.execute(**kwargs)
        return result
    
    def list_tools(self) -> List[str]:
        return list(self.tools.keys())

tool_manager = ToolManager()