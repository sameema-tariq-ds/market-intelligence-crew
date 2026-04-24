from crewai.tools import BaseTool
from crewai_tools import SerperDevTool

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

class MarketPriceFetcherTool(BaseTool):
    name: str = "Market Price Fetcher"
    description: str = (
        "Retrieve publicly available pricing information for a specific company."
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
        """"
        Retrieve publicly available pricing information for a specific company.
    
        Use this tool after identifying competitors to understand their pricing models,
        tiers, and positioning strategy.
    
        Args:
            industry: The name of the company to look up pricing for.
    
        Returns:
            A string describing the company's pricing model and tiers.
        """
        logger.info("Tool: MarketPriceFetcherTool called | industry=%s", industry)

        try:
            serper_api_key = self.serper_api_key
            search_tool = SerperDevTool(api_key=serper_api_key)
            query = f"{industry} understand its pricing models, tiers, and positioning strategy."
            results = search_tool.run(search_query=query)
            print('MarketPriceFetcherTool',results)
            return f"Search results for {industry}:\n{results}"
        except Exception as e:
            logger.error("MarketPriceFetcherTool failed", exc_info=True)
            return "Error: Unable to fetch market price data at this time."
        

class MarketCompetitorsFetcherTool(BaseTool):
    name: str = "Market Competitors Fetcher"
    description: str = (
        "Identify the main competitors operating in the specified industry."
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
        Identify the main competitors operating in the specified industry.
    
        Use this tool to get a list of companies, their websites, founding years,
        and brief descriptions. This is your starting point for competitive research.
    
        Args:
            industry: The industry or market segment to search (e.g. 'project management SaaS').
    
        Returns:
            A formatted string listing competitor companies with key details.
        """
        logger.info("Tool: MarketCompetitorsFetcherTool called | industry=%s", industry)

        try:
            serper_api_key = self.serper_api_key
            search_tool = SerperDevTool(api_key=serper_api_key)
            query = f"{industry} listing competitor companies with key details."
            results = search_tool.run(search_query=query)
            print('MarketCompetitorsFetcherTool',results)
            return f"Search results for {industry}:\n{results}"
        except Exception as e:
            logger.error("MarketCompetitorsFetcherTool failed", exc_info=True)
            return "Error: Unable to fetch market price data at this time."