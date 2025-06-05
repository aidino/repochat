---
template_id: review_changes
name: Review Code Changes
description: Template để review những thay đổi code trong Pull Request
category: code_review
version: "1.0"
required_variables:
  - file_path
  - diff_content
optional_variables:
  - language
  - pr_description
  - context
default_values:
  language: python
  pr_description: No description provided
  context: Pull Request review
tags:
  - code_review
  - pull_request
  - diff_analysis
  - vietnamese
---

# Template: Review Code Changes

Hãy review những thay đổi code sau trong Pull Request:

**File:** {file_path}
**PR Description:** {pr_description}
**Context:** {context}

**Diff Content:**
```{language}
{diff_content}
```

Vui lòng review và đánh giá:

## 1. Code Quality
- Kiểm tra coding standards và best practices
- Đánh giá code readability và maintainability
- Kiểm tra naming conventions

## 2. Logic và Functionality  
- Tính đúng đắn của logic thay đổi
- Xác nhận functionality hoạt động như mong đợi
- Kiểm tra edge cases được handle

## 3. Performance và Security
- Đánh giá performance impact
- Kiểm tra potential security vulnerabilities
- Memory usage và resource efficiency

## 4. Testing và Documentation
- Đề xuất test cases cần thiết
- Kiểm tra documentation cần update
- Integration testing considerations

## 5. Recommendation
- Overall rating (Approve/Request Changes/Comment)
- Specific action items
- Priority level của các issues

Trả lời bằng tiếng Việt với format rõ ràng. 