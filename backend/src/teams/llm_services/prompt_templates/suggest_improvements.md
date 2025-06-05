---
template_id: suggest_improvements
name: Đề xuất Cải thiện
description: Template để đề xuất cải thiện code
category: code_optimization
version: "1.0"
required_variables:
  - code_content
optional_variables:
  - language
  - current_context
  - priority_level
default_values:
  language: python
  current_context: General code improvement
  priority_level: Medium
tags:
  - code_improvement
  - optimization
  - refactoring
  - vietnamese
---

# Template: Đề xuất Cải thiện

Hãy đề xuất các cải thiện cho đoạn code sau:

```{language}
{code_content}
```

**Current Context:** {current_context}
**Priority:** {priority_level}

Vui lòng đề xuất cải thiện trong các khía cạnh:

## 1. Refactoring Opportunities
- Code structure improvements
- Method/function extraction
- Class design optimization
- Modularization suggestions

## 2. Performance Optimizations
- Algorithm improvements
- Memory usage optimization
- Computational efficiency
- Caching strategies

## 3. Code Organization
- File/module structure
- Separation of concerns
- Dependency management
- Architecture patterns

## 4. Design Pattern Applications
- Applicable design patterns
- Architectural improvements
- SOLID principles application
- Code reusability

## 5. Error Handling Enhancements
- Exception handling improvements
- Input validation
- Fail-safe mechanisms
- Logging và monitoring

## 6. Documentation Improvements
- Code comments
- API documentation
- Usage examples
- README updates

## 7. Testing Strategy
- Unit test coverage
- Integration testing
- Test automation
- Testing best practices

Cho mỗi đề xuất, vui lòng cung cấp:
- **Description:** Mô tả chi tiết cải thiện
- **Rationale:** Lý do tại sao cần cải thiện
- **Expected Benefits:** Lợi ích dự kiến
- **Implementation Approach:** Cách thực hiện
- **Estimated Effort:** Ước tính effort (Low/Medium/High)
- **Dependencies:** Các dependency cần thiết

Trả lời bằng tiếng Việt. 