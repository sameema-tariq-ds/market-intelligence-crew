from crewai.tools import BaseTool
from crewai_tools import SerperDevTool

import logging
from typing import Type
from pydantic import BaseModel, Field

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from src.market_intel_crew.utils.logger import get_logger

 
logger = get_logger(__name__)

class MarketDataInput(BaseModel):
    """Input schema for market data input."""
    industry: str = Field(
        ..., description="The industry or market segment (e.g. 'AI chatbots')"
    )

class MarketDataFetcherTool(BaseTool):
    name: str = "Market Data Fetcher"
    description: str = (
        "Fetches market size, growth rate, segmentation, and trends for a given industry."
    )
    args_schema: Type[BaseModel] = MarketDataInput
    serper_api_key: str = Field(..., repr=False) #repr=False : prevents leaking secrets in log


    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError, RuntimeError)),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=before_sleep_log(logger, 30),
        reraise=True,
    )
    def _run(self, industry: str) -> str:
        """
        Fetch high-level market statistics and landscape data for the given industry.
    
        Use this tool when you need quantitative market information such as market
        size, growth rate, and major industry segments.
    
        Args:
            industry: The industry or market segment to look up (e.g. 'AI chatbots').
    
        Returns:
            A string containing market statistics and landscape information.
        """
        logger.info("Tool: MarketDataFetcherTool called | industry=%s", industry)

        try:
            serper_api_key = self.serper_api_key
            search_tool = SerperDevTool(api_key=serper_api_key)
            query = f"{industry} market size CAGR segmentation regions growth drivers 2024"
            results = search_tool.run(search_query=query)
            print(results)
            return f"Search results for {industry}:\n{results}"
        except Exception as e:
            logger.error("MarketDataFetcherTool failed", exc_info=True)
            return "Error: Unable to fetch market data at this time."
        