# Video Tutorial

For a step-by-step walkthrough, watch the video [tutorial](https://drive.google.com/file/d/13kmRvU2QG0qT1YgDr80k3E65-FJK5D5i/view?usp=sharing).

# Development Setup Instructions
⚠️ **Important**:  This project only runs in a development container. It won't work if you try to run it locally without the correct setup.

## Prerequisites
- An IDE with the Dev Containers extension installed (e.g. Visual Studio Code)
- Docker Desktop installed and running

## Running the Application
1. Open the project in your IDE (preferably VS Code)
2. When prompted, click "Reopen in Container" or press `F1` and select **Dev Containers: Rebuild and Reopen in Container**
3. Once the container is built and running, open a terminal in your IDE and execute the following command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 80 --reload
   ```

## API Documentation
After the application is running, access the API documentation at:
- **Swagger UI**: [http://localhost/docs](http://localhost/docs)

