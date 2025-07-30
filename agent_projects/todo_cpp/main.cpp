#include <iostream>
#include <vector>
#include <string>
#include <limits>
#include <iomanip> // Required for std::setw and std::left

struct TodoItem {
    std::string description;
    bool completed;
};

void displayMenu() {
    std::cout << "\n--- Todo Application Menu ---\n";
    std::cout << "1. Add Todo\n";
    std::cout << "2. List Todos\n";
    std::cout << "3. Mark Todo as Complete\n";
    std::cout << "4. Delete Todo\n";
    std::cout << "5. Quit\n";
    std::cout << "Enter your choice: ";
}

void addTodo(std::vector<TodoItem>& todos) {
    std::string description;
    std::cout << "Enter todo description: ";
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Clear buffer
    std::getline(std::cin, description);
    todos.push_back({description, false});
    std::cout << "Todo added successfully!\n";
}

void listTodos(const std::vector<TodoItem>& todos) {
    if (todos.empty()) {
        std::cout << "No todo items yet.\n";
        return;
    }
    std::cout << "\n--- Your Todo List ---\n";
    // Define column widths
    const int idWidth = 5;
    const int statusWidth = 10;
    const int descriptionWidth = 30; // Increased width for description

    // Print table header
    std::cout << std::left << std::setw(idWidth) << "ID"
              << std::left << std::setw(statusWidth) << "Status"
              << std::left << std::setw(descriptionWidth) << "Description\n";
    std::cout << std::string(idWidth + statusWidth + descriptionWidth, '-') << "\n"; // Dynamic separator

    for (size_t i = 0; i < todos.size(); ++i) {
        std::cout << std::left << std::setw(idWidth) << i + 1
                  << std::left << std::setw(statusWidth) << (todos[i].completed ? "[x]" : "[ ]")
                  << std::left << std::setw(descriptionWidth) << todos[i].description << "\n";
    }
}

void markTodoComplete(std::vector<TodoItem>& todos) {
    listTodos(todos);
    if (todos.empty()) {
        return;
    }
    int index;
    std::cout << "Enter the number of the todo to mark as complete: ";
    std::cin >> index;
    if (std::cin.fail() || index < 1 || index > static_cast<int>(todos.size())) {
        std::cin.clear(); // Clear error flags
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Discard invalid input
        std::cout << "Invalid todo number.\n";
        return;
    }
    todos[index - 1].completed = true;
    std::cout << "Todo marked as complete!\n";
}

void deleteTodo(std::vector<TodoItem>& todos) {
    listTodos(todos);
    if (todos.empty()) {
        return;
    }
    int index;
    std::cout << "Enter the number of the todo to delete: ";
    std::cin >> index;
    if (std::cin.fail() || index < 1 || index > static_cast<int>(todos.size())) {
        std::cin.clear(); // Clear error flags
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n'); // Discard invalid input
        std::cout << "Invalid todo number.\n";
        return;
    }
    todos.erase(todos.begin() + index - 1);
    std::cout << "Todo deleted successfully!\n";
}

int main() {
    std::vector<TodoItem> todos;
    int choice;

    do {
        displayMenu();
        std::cin >> choice;

        switch (choice) {
            case 1:
                addTodo(todos);
                break;
            case 2:
                listTodos(todos);
                break;
            case 3:
                markTodoComplete(todos);
                break;
            case 4:
                deleteTodo(todos);
                break;
            case 5:
                std::cout << "Exiting application. Goodbye!\n";
                break;
            default:
                std::cout << "Invalid choice. Please try again.\n";
                break;
        }
    } while (choice != 5);

    return 0;
}