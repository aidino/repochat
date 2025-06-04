# RepoChat Backend v1.0

## Tổng quan

Backend của RepoChat v1.0 - AI Code Review Assistant sử dụng kiến trúc đa agent với Orchestrator Agent làm trung tâm điều phối.

## Cấu trúc Project

```
backend/
├── src/
│   ├── orchestrator/           # Orchestrator Agent - điều phối trung tâm
│   ├── teams/                  # Các TEAM agents
│   │   ├── interaction_tasking/
│   │   ├── data_acquisition/
│   │   ├── ckg_operations/
│   │   ├── code_analysis/
│   │   ├── llm_services/
│   │   └── synthesis_reporting/
│   └── shared/                 # Shared components
│       ├── models/             # Data models
│       ├── protocols/          # Communication protocols
│       └── utils/              # Utilities
├── tests/                      # Unit tests
├── requirements.txt            # Dependencies
└── test_orchestrator.py       # Demo script
```

## Cài đặt

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

2. Chạy demo script:
```bash
python test_orchestrator.py
```

## Chạy Tests

```bash
# Chạy tất cả tests
cd tests
python -m pytest . -v

# Chạy tests cho một module cụ thể
python -m pytest test_orchestrator_agent.py -v
python -m pytest test_task_definition.py -v
```

## Tiến độ phát triển

### ✅ Task 1.1 - COMPLETED (4/6/2025)
- [x] Thiết lập cấu trúc project Python cho Orchestrator Agent
- [x] Tạo OrchestratorAgent class với logging cơ bản
- [x] Định nghĩa TaskDefinition model
- [x] Unit tests (18 tests PASS)

### 🔄 Tiếp theo: Task 1.2
- TEAM Data Acquisition - GitOperationsModule
- Clone Git repository công khai

## Kiến trúc

Hệ thống sử dụng kiến trúc đa agent với:
- **Orchestrator Agent**: Điều phối trung tâm, quản lý workflow
- **TEAM Agents**: Các team chuyên biệt xử lý các khía cạnh khác nhau
- **Shared Components**: Models, protocols, utilities dùng chung

## Công nghệ sử dụng

- **Framework**: Python, LangChain/LangGraph
- **LLM**: OpenAI API (có thể mở rộng)
- **Database**: Neo4j (cho Code Knowledge Graph)
- **Testing**: pytest
- **Models**: Pydantic

## Ghi chú

Đây là phiên bản v1.0 tập trung vào các tính năng cốt lõi:
- Xây dựng Code Knowledge Graph (CKG)
- Phân tích kiến trúc cơ bản
- Phân tích Pull Request
- Q&A về codebase
- Sinh sơ đồ lớp cơ bản 