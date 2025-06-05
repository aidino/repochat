---
template_id: explain_code
name: Giải thích Code
description: Template để giải thích chức năng của đoạn code
category: code_analysis
version: "1.0"
required_variables:
  - code_snippet
optional_variables:
  - language
  - context
default_values:
  language: python
  context: General code analysis
tags:
  - explanation
  - code_analysis
  - vietnamese
---

# Template: Giải thích Code

Hãy giải thích chức năng của đoạn code sau một cách chi tiết và dễ hiểu:

```{language}
{code_snippet}
```

Context: {context}

Vui lòng:
1. Mô tả chức năng chính của code
2. Giải thích từng bước logic quan trọng
3. Chỉ ra các pattern hoặc technique được sử dụng
4. Đề cập đến potential issues nếu có
5. Đánh giá độ phức tạp và performance

Trả lời bằng tiếng Việt một cách rõ ràng và dễ hiểu. 