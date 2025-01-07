import os
import logging
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv
import asyncio
from functools import partial

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class TextProcessor:
    def __init__(self):
        """Initialize the text processor"""
        self.api_docs = self._get_api_documentation()
        logger.info("TextProcessor initialized with API documentation")
        
    async def process_question(self, question: str) -> Optional[str]:
        """Process a user question and return the best answer"""
        try:
            logger.info(f"Processing question: {question}")
            
            if not question:
                logger.warning("Empty question received")
                return "Please provide a question to answer."
                
            answer = await self._get_gemini_answer(question)
            
            if not answer:
                logger.warning("No answer generated")
                return "I apologize, but I couldn't generate an answer. Please try asking your question differently."
                
            logger.info("Answer generated successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return f"An error occurred: {str(e)}"
            
    async def _get_gemini_answer(self, question: str) -> Optional[str]:
        """Get answer from Gemini using API documentation"""
        try:
            prompt = f"""
            You are a Crustdata API expert. Answer this question using the API documentation and your knowledge.
            If you need to search the web for additional information about Crustdata, please do so.
            
            API Documentation:
            {self.api_docs}
            
            Question: {question}
            
            Requirements:
            1. If the question is about Crustdata APIs:
               - Provide specific endpoint details
               - Include code examples
               - Mention authentication and rate limits
            2. If it's a general question:
               - Provide best practices
               - Include relevant examples
            3. Always format code examples with markdown
            4. Structure your response with:
               - Answer
               - Code Example (if applicable)
               - Important Notes
            5. If you need to search the web, mention that in your response
            
            Remember to:
            1. Always provide a complete, detailed answer
            2. Include practical code examples where relevant
            3. Format code with proper markdown (```language)
            4. Mention authentication requirements
            5. Include error handling in examples
            """
            
            logger.info("Sending request to Gemini")
            
            # Create a chat session
            chat = model.start_chat(history=[])
            response = await self._run_in_executor(
                lambda: chat.send_message(prompt)
            )
            
            if not response or not response.text:
                logger.warning("Empty response from Gemini")
                return "I apologize, but I couldn't generate an answer at the moment. Please try again."
                
            logger.info("Response received from Gemini")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error getting Gemini answer: {str(e)}")
            return f"An error occurred while processing your request: {str(e)}"
            
    def _get_api_documentation(self) -> str:
        """Return the Crustdata API documentation"""
        return """
        Crustdata API Documentation:
        
        1. Discovery API:
        - Endpoint: https://api.crustdata.com/v1/discovery
        - Purpose: Find and analyze data across various sources
        - Methods: 
          * POST /search: Search for data based on keywords
            - Parameters:
              * query (required): Search query string
              * filters: Dictionary of filters
              * limit: Results per page (default: 100)
            - Returns: List of discovered datasets
          
          * POST /analyze: Analyze data structure and content
            - Parameters:
              * data (required): Data to analyze
              * options: Analysis options
            - Returns: Analysis results including schema and statistics
          
          * GET /sources: List available data sources
            - Parameters:
              * type: Filter by source type
            - Returns: List of available data sources
        
        2. Enrichment API:
        - Endpoint: https://api.crustdata.com/v1/enrichment
        - Purpose: Enrich existing data with additional information
        - Methods:
          * POST /enrich: Add metadata and context to data
            - Parameters:
              * data (required): Data to enrich
              * enrichment_types: List of enrichment types
            - Returns: Enriched data with additional context
          
          * POST /validate: Validate data quality
            - Parameters:
              * data (required): Data to validate
              * rules: Validation rules
            - Returns: Validation results and quality metrics
          
          * POST /transform: Transform data format
            - Parameters:
              * data (required): Data to transform
              * target_format: Desired output format
            - Returns: Transformed data
        
        3. Dataset API:
        - Endpoint: https://api.crustdata.com/v1/dataset
        - Purpose: Manage and query datasets
        - Methods:
          * GET /list: List available datasets
            - Parameters:
              * category: Filter by category
              * limit: Results per page
            - Returns: List of datasets
          
          * POST /query: Query specific dataset
            - Parameters:
              * dataset_id (required): ID of dataset
              * query: Query parameters
            - Returns: Query results
          
          * POST /export: Export dataset results
            - Parameters:
              * dataset_id (required): ID of dataset
              * format: Export format (json/csv)
            - Returns: Export URL or data
        
        Authentication:
        - API Key required in headers: X-API-Key: <your_api_key>
        - Rate limits: 1000 requests per minute
        - Throttling: Requests exceeding limit are queued
        
        Common Parameters:
        - format: json/csv (default: json)
        - limit: Number of results (default: 100, max: 1000)
        - offset: Pagination offset (default: 0)
        - fields: Specific fields to return
        
        Error Handling:
        - 400: Bad Request - Invalid parameters
        - 401: Unauthorized - Invalid API key
        - 403: Forbidden - Rate limit exceeded
        - 404: Not Found - Resource not found
        - 429: Too Many Requests - Rate limit exceeded
        - 500: Internal Server Error
        
        Best Practices:
        1. Always handle rate limits and implement retries
        2. Use pagination for large result sets
        3. Implement proper error handling
        4. Cache frequently accessed data
        5. Use appropriate timeout values
        6. Validate input data before sending
        7. Handle all error responses
        8. Use connection pooling for multiple requests
        9. Implement request retries with exponential backoff
        10. Monitor API usage and response times
        """
        
    async def _run_in_executor(self, func):
        """Run a blocking function in an executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func)

async def main():
    async with TextProcessor() as processor:
        # Add your test code here
        pass

if __name__ == '__main__':
    asyncio.run(main())
