#!/bin/bash

# Compile the C++ application
g++ main.cpp -o todo

# Check if compilation was successful
if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

echo "Running automated tests..."

# Test sequence: Add, List, Complete, List, Delete, List, Quit
{
  echo "1" # Add todo
  echo "Buy groceries"
  echo "2" # List todos
  echo "3" # Mark complete
  echo "1" # Complete item 1
  echo "2" # List todos
  echo "4" # Delete todo
  echo "1" # Delete item 1
  echo "2" # List todos
  echo "5" # Quit
} | ./todo

echo "Automated tests finished."