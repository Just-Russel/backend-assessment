# Junior developer assessment

# Project Overview

This is a simple FastAPI project using a SQLite database for persistence. It includes:

- A basic setup with an `author` entity
- Endpoints to create and read authors
- Project scaffolding with requirements.txt and pyproject.toml

Your task is to build on this foundation by adding new features and improvements.

# Getting started

1. Get started by setting up the project virtual environment and installing the dependencies.
    You can choose whatever method you prefer, both a `requirements.txt` file and a `pyproject.toml` file are provided.
2. You can start the server by running the `src` package as a module.
3. After running the server, you can browse the existing endpoints at `http://localhost:8000/docs` or `http://localhost:8000/redoc`.
4. I recommend taking a look at the project structure and the existing code to understand how it works.

# Main objective

+ Add a Book entity:
    - Implement create and read endpoints
    - Each Book should be associated with one Author
    - An Author can have many Books

+ Add a new endpoint to list all books by a specific author

+ Add a new endpoint to update an author or book

+ Implement authentication for all endpoints:
    - You may use any method you prefer (e.g. API Key, JWT, OAuth2)
    - Make sure endpoints are secured appropriately

+ Write tests for your new features
    - Use `pytest`, `unittest`, or any test framework you're comfortable with

## Bonus Points

- Use type annotations and ensure your code is type-safe
- Organize your code following clean architecture or well-structured modular design
- Add meaningful tests
- Implement role-based access control or different user roles
- Meaningful commit messages

## Final Notes

- Focus on clean, readable, and maintainable code.
- Don't hesitate to refactor existing code if needed.

**Good luck! If you have any questions, feel free to ask.**