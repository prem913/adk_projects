#!/usr/bin/env python3
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "financial_inclusion.main:main_app",
        host="0.0.0.0",
        port=8080,
        workers=1,
    )

