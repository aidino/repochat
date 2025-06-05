---
template_id: find_issues
name: Tìm Issues trong Code
description: Template để tìm potential issues trong code
category: code_analysis
version: "1.0"
required_variables:
  - code_content
optional_variables:
  - language
  - analysis_scope
default_values:
  language: python
  analysis_scope: Full analysis
tags:
  - issue_detection
  - code_analysis
  - debugging
  - vietnamese
---

# Template: Tìm Issues trong Code

Hãy phân tích đoạn code sau để tìm potential issues:

```{language}
{code_content}
```

**Scope:** {analysis_scope}

Vui lòng tìm và phân tích:

## 1. Bugs và Logic Errors
- Lỗi logic có thể dẫn đến kết quả sai
- Off-by-one errors
- Null pointer/reference issues
- Type conversion errors

## 2. Security Vulnerabilities  
- Input validation issues
- SQL injection risks
- XSS vulnerabilities
- Authentication/authorization problems

## 3. Performance Bottlenecks
- Inefficient algorithms
- Memory leaks
- Unnecessary computations
- Database query optimization

## 4. Code Quality Issues
- Code smells và anti-patterns
- Violation of SOLID principles
- Maintainability problems
- Readability issues

## 5. Exception Handling
- Missing error handling
- Improper exception catching
- Resource cleanup issues
- Fail-safe mechanisms

## 6. Data Validation Problems
- Input sanitization
- Data type validation
- Range checking
- Format validation

Cho mỗi issue được tìm thấy, vui lòng cung cấp:
- **Severity Level:** Critical/High/Medium/Low
- **Description:** Mô tả chi tiết vấn đề
- **Impact:** Ảnh hưởng potential
- **Recommendation:** Đề xuất fix

Trả lời bằng tiếng Việt. 