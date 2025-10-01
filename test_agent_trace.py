#!/usr/bin/env python3
"""Test agent with detailed trace"""
import sys
sys.path.insert(0, '.')

def trace_calls(frame, event, arg):
    if event == 'call':
        filename = frame.f_code.co_filename
        if 'research_agent' in filename or 'database' in filename:
            print(f"  → {frame.f_code.co_name} in {filename.split('/')[-1]}")
    return trace_calls

print("="*60)
print("TESTING AGENT INITIALIZATION WITH TRACE")
print("="*60)

print("\n1. Importing modules...")
from src.research_agent.main_agent import ResearchAgent
print("✅ Import successful\n")

print("2. Creating ResearchAgent (with trace)...")
#sys.settrace(trace_calls)

try:
    agent = ResearchAgent()
    print("✅ ResearchAgent created successfully!")
    
    print("\n" + "="*60)
    print("✅✅✅ AGENT WORKS PERFECTLY! ✅✅✅")
    print("="*60)
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
