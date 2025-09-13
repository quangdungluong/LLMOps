# LLMOps - Enterprise AI Operations Platform

LLMOps is a comprehensive enterprise platform for managing Large Language Model operations, featuring advanced RAG (Retrieval Augmented Generation) capabilities, document processing, knowledge management, and full observability stack. Built with modern microservices architecture, it provides everything needed to deploy, monitor, and scale AI applications in production.

## Core AI Features

### Intelligent Document Processing

- **Multi-format Support**: Process PDFs, Word documents, text files, and more with automatic content extraction
- **Smart Chunking**: Advanced text splitting with configurable chunk sizes and overlap for optimal retrieval
- **OCR Capabilities**: Extract text from scanned documents and images
- **Background Processing**: Asynchronous document processing with real-time status updates
- **Duplicate Detection**: Automatic file deduplication using SHA256 hashing

### Advanced RAG System

- **Contextual Retrieval**: History-aware document retrieval that understands conversation context
- **Multi-knowledge Base Support**: Query across multiple knowledge bases simultaneously
- **Citation Tracking**: Automatic source citation with reference numbers
- **Conversational Memory**: Maintains chat history for coherent multi-turn conversations
- **Semantic Search**: Vector-based similarity search for accurate document retrieval

### LLM Integration & Management

- **Multi-Provider Support**: Seamless integration with Google Gemini models (2.5 Pro, 2.5 Flash, 2.0 Flash)
- **LiteLLM Gateway**: Unified API gateway for multiple LLM providers with load balancing
- **Model Routing**: Intelligent model selection based on workload and performance requirements
- **Rate Limiting**: Built-in request throttling and budget controls
- **Response Streaming**: Real-time response generation with streaming support

### Vector Store & Embeddings

- **Milvus Integration**: High-performance vector database for scalable similarity search
- **Multiple Embedding Models**: Support for Ollama and vLLM embedding providers
- **Collection Management**: Organized vector collections per knowledge base
- **Similarity Search**: Configurable top-k retrieval with score thresholds
- **Batch Operations**: Efficient bulk document embedding and storage

### AI Safety & Guardrails

- **NeMo Guardrails**: Integrated safety framework for content filtering and response validation
- **Prompt Management**: Centralized prompt templates with version control
- **Response Validation**: Automatic content moderation and safety checks
- **Custom Rules**: Configurable guardrails for domain-specific requirements

## Platform Architecture

### Backend Services

- **FastAPI Application**: High-performance async Python backend with automatic API documentation
- **PostgreSQL Database**: Robust relational database for metadata and user management
- **Redis Caching**: In-memory caching for improved response times and LLM response caching
- **Background Tasks**: Celery-based task queue for document processing and other async operations

### Frontend Interface

- **Next.js Application**: Modern React-based web interface with TypeScript
- **Real-time Chat**: Interactive chat interface with streaming responses
- **Knowledge Base Management**: Intuitive document upload and management interface
- **Dashboard Analytics**: Comprehensive metrics and usage analytics
- **Responsive Design**: Mobile-friendly interface built with Tailwind CSS

### Data Pipeline

- **Apache Airflow**: Orchestrated data ingestion and processing workflows
- **MinIO Storage**: S3-compatible object storage for documents and media files
- **Document Loaders**: Specialized loaders for different file formats
- **Chunk Processing**: Automated text splitting and embedding generation
- **Batch Operations**: Scheduled processing for large document collections

### Observability Stack

- **Langfuse Integration**: Comprehensive LLM observability and tracing
- **Prometheus Monitoring**: Metrics collection and alerting
- **Grafana Dashboards**: Visual monitoring and analytics
- **Container Monitoring**: Docker container performance tracking with cAdvisor
- **Distributed Tracing**: End-to-end request tracing across services

## Deployment Options

### Docker Compose Setup

The platform supports multiple deployment configurations:

- **Standard Deployment**: Core services with PostgreSQL and Milvus
- **LiteLLM Gateway**: Enhanced LLM routing and management
- **vLLM Integration**: Self-hosted LLM inference server
- **Monitoring Stack**: Full observability with Prometheus and Grafana

### Infrastructure Components

- **Nginx Reverse Proxy**: Load balancing and SSL termination
- **PostgreSQL**: Primary database with health checks
- **Milvus Vector Database**: High-performance vector storage
- **Redis**: Caching and session management
- **MinIO**: Object storage for documents and media
- **ClickHouse**: Analytics database for Langfuse
- **Etcd**: Service discovery and configuration management

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- Node.js 18+ (for frontend development)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/quangdungluong/LLMOps
cd LLMOps

# Start all services
make run

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost/api/v1
# Langfuse: http://localhost:3001
# Milvus Attu: http://localhost:3003
```

## API Documentation

The platform provides comprehensive API documentation:

- **Interactive Docs**: Available at `/docs` endpoint
- **OpenAPI Specification**: Standard REST API with full schema definitions
- **Authentication**: JWT-based user authentication
- **Rate Limiting**: Built-in request throttling
- **Error Handling**: Detailed error responses with proper HTTP status codes

## Key Features

### Knowledge Management

- Create and manage multiple knowledge bases
- Upload documents in various formats
- Automatic document processing and indexing
- Search and retrieval across knowledge bases
- Document versioning and metadata tracking

### Chat Interface

- Real-time conversational AI
- Context-aware responses with citations
- Multi-knowledge base querying
- Chat history persistence
- Streaming response generation

### User Management

- User registration and authentication
- Role-based access control
- Session management
- User activity tracking

### Monitoring & Analytics

- Real-time performance metrics
- LLM usage analytics
- Cost tracking and budgeting
- Error monitoring and alerting
- Custom dashboard creation

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

## Roadmap

- Enhanced multi-modal support (images, audio)
- Advanced prompt engineering tools
- Custom model fine-tuning capabilities
- Enterprise SSO integration
- Advanced analytics and reporting
- Multi-tenant architecture support
