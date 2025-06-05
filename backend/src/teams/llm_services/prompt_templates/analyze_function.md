---
template_id: analyze_function
name: Phân tích Function
description: Template để phân tích function chi tiết
category: code_analysis
version: "1.0"
required_variables:
  - function_name
  - function_code
optional_variables:
  - language
  - context
default_values:
  language: python
  context: Function analysis
tags:
  - function_analysis
  - code_review
  - vietnamese
---

# Template: Phân tích Function

Hãy phân tích function sau một cách chi tiết:

**Function Name:** {function_name}

```{language}
{function_code}
```

Context: {context}

Vui lòng phân tích:
1. **Mục đích và chức năng:** Function này làm gì?
2. **Input parameters:** Loại và ý nghĩa của các tham số
3. **Output/Return:** Kiểu dữ liệu và ý nghĩa kết quả trả về
4. **Logic flow:** Luồng xử lý chính của function
5. **Edge cases:** Các trường hợp đặc biệt cần xử lý
6. **Complexity:** Đánh giá độ phức tạp thời gian và không gian
7. **Potential improvements:** Đề xuất cải thiện nếu có

Trả lời bằng tiếng Việt. 