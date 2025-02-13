#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.services.scrapers.data_collector import run_collector
from app.core.logger import logger

async def main():
    """Run the data collector service"""
    logger.info("Starting data collector service...")
    try:
        await run_collector()
    except KeyboardInterrupt:
        logger.info("Data collector service stopped by user")
    except Exception as e:
        logger.error(f"Data collector service error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 