#!/usr/bin/env python3
from modelcontextprotocol.sdk.server import Server
from modelcontextprotocol.sdk.server.stdio import StdioServerTransport
from modelcontextprotocol.sdk.types import (
    CallToolRequestSchema,
    ListToolsRequestSchema,
    McpError,
    ErrorCode
)
from agent import WebAgent
import os
import json
import logging
from datetime import datetime

class AdAgentServer:
    def __init__(self):
        self.server = Server(
            {
                "name": "ad-agent-server",
                "version": "0.1.0",
            },
            {
                "capabilities": {
                    "tools": {},
                }
            }
        )
        
        self.agent = None
        self.setup_logging()
        self.setup_handlers()

    def setup_logging(self):
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join(log_dir, f'mcp_server_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_handlers(self):
        self.server.setRequestHandler(ListToolsRequestSchema, self.handle_list_tools)
        self.server.setRequestHandler(CallToolRequestSchema, self.handle_call_tool)

    async def handle_list_tools(self, request):
        return {
            "tools": [
                {
                    "name": "initialize_agent",
                    "description": "Initialize the web agent with specific Chrome profile",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "profile_path": {
                                "type": "string",
                                "description": "Path to Chrome user profile directory"
                            }
                        },
                        "required": ["profile_path"]
                    }
                },
                {
                    "name": "start_training",
                    "description": "Start training mode with a specific URL",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to navigate to"
                            }
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "rate_sequence",
                    "description": "Rate current interaction sequence",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "rating": {
                                "type": "number",
                                "description": "Rating value between 0 and 1",
                                "minimum": 0,
                                "maximum": 1
                            }
                        },
                        "required": ["rating"]
                    }
                },
                {
                    "name": "predict_rating",
                    "description": "Predict rating for current page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to analyze"
                            }
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "close_agent",
                    "description": "Close the web agent",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }

    async def handle_call_tool(self, request):
        try:
            tool_name = request.params.name
            args = request.params.arguments

            if tool_name == "initialize_agent":
                return await self.initialize_agent(args.get("profile_path"))
            elif tool_name == "start_training":
                return await self.start_training(args.get("url"))
            elif tool_name == "rate_sequence":
                return await self.rate_sequence(args.get("rating"))
            elif tool_name == "predict_rating":
                return await self.predict_rating(args.get("url"))
            elif tool_name == "close_agent":
                return await self.close_agent()
            else:
                raise McpError(ErrorCode.MethodNotFound, f"Unknown tool: {tool_name}")

        except Exception as e:
            logging.error(f"Error handling tool call: {str(e)}")
            raise McpError(ErrorCode.InternalError, str(e))

    async def initialize_agent(self, profile_path):
        try:
            self.agent = WebAgent()
            options = {
                'user_data_dir': profile_path,
                'profile_directory': 'Default'
            }
            self.agent.initialize(chrome_options=options)
            return {
                "content": [{
                    "type": "text",
                    "text": "Agent initialized successfully with custom Chrome profile"
                }]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Failed to initialize agent: {str(e)}")

    async def start_training(self, url):
        if not self.agent:
            raise McpError(ErrorCode.InvalidRequest, "Agent not initialized")
        
        try:
            self.agent.start_training_sequence()
            self.agent.navigate_to(url)
            return {
                "content": [{
                    "type": "text",
                    "text": "Training sequence started"
                }]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Failed to start training: {str(e)}")

    async def rate_sequence(self, rating):
        if not self.agent:
            raise McpError(ErrorCode.InvalidRequest, "Agent not initialized")
        
        try:
            self.agent.end_training_sequence(rating)
            self.agent.start_training_sequence()  # Start new sequence
            return {
                "content": [{
                    "type": "text",
                    "text": f"Sequence rated: {rating}"
                }]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Failed to rate sequence: {str(e)}")

    async def predict_rating(self, url):
        if not self.agent:
            raise McpError(ErrorCode.InvalidRequest, "Agent not initialized")
        
        try:
            self.agent.navigate_to(url)
            ad_data = self.agent.detect_ad_content()
            prediction = self.agent.predict_rating()
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "prediction": float(prediction) if prediction is not None else None,
                        "ad_data": ad_data
                    }, indent=2)
                }]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Failed to predict rating: {str(e)}")

    async def close_agent(self):
        if self.agent:
            try:
                self.agent.close()
                self.agent = None
                return {
                    "content": [{
                        "type": "text",
                        "text": "Agent closed successfully"
                    }]
                }
            except Exception as e:
                raise McpError(ErrorCode.InternalError, f"Failed to close agent: {str(e)}")

    async def run(self):
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logging.info("Ad Agent MCP server running on stdio")

if __name__ == "__main__":
    server = AdAgentServer()
    import asyncio
    asyncio.run(server.run())
