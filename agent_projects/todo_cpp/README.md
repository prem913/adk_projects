## About the Application
This is a simple command-line Todo application written in C++. It allows users to add, list, mark as complete, and delete todo items. The application now displays the todo list in a clean, tabular format.

## How to Run
```bash
g++ main.cpp -o todo && ./todo
```

## How to Test
```bash
./test_todo.sh
```

## How the Table Display Works
The 'List Todos' option (option 2) now presents your todo items in a formatted table with columns for ID, Status (marked with [x] for completed and [ ] for pending), and Description. The table dynamically adjusts its column widths for better readability.

## Remaining Tasks
*   [x] Implement table display for `listTodos` in `main.cpp`.
*   [x] Update `README.md` with application details and usage instructions.