# AI Configurable MVP API

A FastAPI-based backend service for managing configurable AI workflows, fields, and prompts. This API allows you to create dynamic workflows with custom fields and AI prompts that can be executed with user input.

## 🚀 Live Demo & API Documentation

- **Live API**: [https://ai-mvp-backend-production.up.railway.app/](https://ai-mvp-backend-production.up.railway.app/)
- **Interactive API Docs**: [https://ai-mvp-backend-production.up.railway.app/docs](https://ai-mvp-backend-production.up.railway.app/docs)
- **Alternative Docs**: [https://ai-mvp-backend-production.up.railway.app/redoc](https://ai-mvp-backend-production.up.railway.app/redoc)

## 📋 Project Description

This FastAPI application provides a comprehensive API for managing AI-powered workflows. It allows users to:

- Create and manage workflows
- Add configurable fields to workflows with specific data types
- Associate AI prompts with each field
- Execute workflows by providing user input and getting AI-generated responses
- Monitor workflow execution with detailed results

The system is designed to be flexible and extensible, supporting various data types and custom AI prompt templates for different use cases.

## 🛠 Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) 0.116.1
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL)
- **AI Integration**: [OpenAI API](https://openai.com/) (GPT-3.5-turbo)
- **Language**: Python 3.13
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) 0.35.0
- **Data Validation**: [Pydantic](https://pydantic.dev/) 2.11.7
- **Environment Management**: [python-dotenv](https://pypi.org/project/python-dotenv/) 1.1.1

## 🚀 Setup Instructions

### Prerequisites

- Python 3.13 or higher
- Supabase account and project
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-configurable-mvp
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### 5. Database Setup

Run the SQL schema from `database_schema.sql` in your Supabase SQL editor to create the required tables:

- `workflows` - Stores workflow information
- `fields` - Stores field definitions for workflows
- `prompts` - Stores AI prompt templates for fields

### 6. Run the Application

```bash
# Development server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoint Documentation

### Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://ai-mvp-backend-production.up.railway.app/`

### Endpoints

#### 1. Root Endpoint
- **GET** `/`
- **Description**: Returns API information and available endpoints
- **Response**: API metadata and endpoint list

#### 2. Health Check
- **GET** `/health`
- **Description**: Health check endpoint with database connectivity status
- **Response**: Service health status

#### 3. Workflow Management

##### Create Workflow
- **POST** `/workflows/`
- **Description**: Create a new workflow
- **Request Body**:
  ```json
  {
    "name": "string"
  }
  ```
- **Response**: Created workflow with ID and timestamp

##### Get Workflow Details
- **GET** `/workflows/{workflow_id}`
- **Description**: Get a workflow with all its fields and prompts
- **Parameters**: `workflow_id` (UUID)
- **Response**: Complete workflow with nested fields and prompts

#### 4. Field Management

##### Add Field to Workflow
- **POST** `/workflows/{workflow_id}/fields`
- **Description**: Add a new field and its prompt to a workflow
- **Parameters**: `workflow_id` (UUID)
- **Request Body**:
  ```json
  {
    "workflow_id": "uuid",
    "name": "string",
    "data_type": "text|number|boolean|date|email|url|json",
    "field_id": "uuid",
    "prompt_template": "string"
  }
  ```
- **Response**: Created field with associated prompt

#### 5. Workflow Execution

##### Execute Workflow
- **POST** `/workflows/{workflow_id}/execute`
- **Description**: Execute a workflow by running all field prompts
- **Parameters**: `workflow_id` (UUID)
- **Request Body**:
  ```json
  {
    "user_input": "string"
  }
  ```
- **Response**: Detailed execution results for all fields

### Data Types

Supported field data types:
- `text` - Plain text
- `number` - Numeric values
- `boolean` - True/false values
- `date` - Date values
- `email` - Email addresses
- `url` - URLs
- `json` - JSON objects

## 🚀 Deployment Instructions

### Deploy to Railway

1. **Prepare for Deployment**
   - Ensure all environment variables are configured
   - Test the application locally
   - Commit all changes to your repository

2. **Railway Setup**
   - Go to [Railway](https://railway.app/)
   - Sign up/Login with your GitHub account
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure Environment Variables**
   - In Railway dashboard, go to your project
   - Navigate to "Variables" tab
   - Add the following environment variables:
     - `SUPABASE_URL`
     - `SUPABASE_SERVICE_KEY`
     - `OPENAI_API_KEY`

4. **Deploy**
   - Railway will automatically detect the Python application
   - The deployment will start automatically
   - Monitor the build logs for any issues

5. **Custom Domain (Optional)**
   - In Railway dashboard, go to "Settings" → "Domains"
   - Add your custom domain if desired

### Railway Configuration Files

The project includes:
- `Dockerfile` - For containerized deployment
- `app.yaml` - Railway configuration
- `requirements.txt` - Python dependencies

### Environment Variables for Production

Make sure to set these in your Railway project:

```env
SUPABASE_URL=your_production_supabase_url
SUPABASE_SERVICE_KEY=your_production_service_key
OPENAI_API_KEY=your_openai_api_key
```

## 🔧 Development

### Project Structure

```
ai-configurable-mvp/
├── main.py              # FastAPI application and endpoints
├── models.py            # Pydantic models for data validation
├── database.py          # Supabase client configuration
├── services.py          # AI service functions
├── requirements.txt     # Python dependencies
├── database_schema.sql  # Database schema
├── Dockerfile          # Container configuration
├── app.yaml            # Railway configuration
└── README.md           # This file
```

### Key Features

- **Async/Await Support**: Full async support for better performance
- **Data Validation**: Comprehensive Pydantic models with validation
- **Error Handling**: Detailed error responses and status codes
- **Database Integration**: Supabase for data persistence
- **AI Integration**: OpenAI GPT-3.5-turbo for prompt execution
- **Health Monitoring**: Health check endpoint for monitoring
- **Interactive Documentation**: Auto-generated API docs with Swagger UI

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For support and questions:
- Check the [API Documentation](https://ai-mvp-backend-production.up.railway.app/docs)
- Review the code examples in the interactive docs
- Open an issue in the repository
