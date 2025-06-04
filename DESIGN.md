## **Báo cáo Thiết kế Toàn diện & Yêu cầu Nghiên cứu Chuyên sâu: Dự án RepoChat v1.0**

Ngày tạo: 4 tháng 6, 2025  
Tên dự án: RepoChat  
**Phần I: Giới thiệu, Tầm nhìn và Mục tiêu Dự án**

1\. Bối cảnh và Vấn đề Hiện tại  
Trong bối cảnh phát triển phần mềm hiện đại, quy trình review code đóng một vai trò then chốt trong việc đảm bảo chất lượng, phát hiện lỗi sớm và chia sẻ kiến thức trong đội ngũ. Tuy nhiên, quy trình này thường tốn nhiều thời gian và công sức của các nhà phát triển cấp cao, dễ bị ảnh hưởng bởi yếu tố con người, và có thể bỏ sót các vấn đề phức tạp liên quan đến kiến trúc hệ thống hoặc các tác động tiềm ẩn của thay đổi mã nguồn. Các công cụ review code tự động hiện tại phần lớn tập trung vào việc kiểm tra cú pháp, tuân thủ quy tắc định dạng (linting), hoặc phát hiện các lỗi bề mặt, chứ chưa thực sự "hiểu" được logic, ngữ nghĩa và kiến trúc tổng thể của codebase.  
2\. Tầm nhìn Giải pháp: RepoChat  
RepoChat được hình dung như một trợ lý review code AI thông minh, một "đồng đội ảo" thế hệ mới cho các nhà phát triển. Mục tiêu là vượt qua những hạn chế của các công cụ truyền thống bằng cách cung cấp khả năng phân tích sâu sắc, hiểu biết ngữ cảnh và tương tác linh hoạt. RepoChat sẽ không chỉ là một công cụ phát hiện lỗi, mà còn là một cố vấn kiến trúc, một người hướng dẫn và một nền tảng chia sẻ tri thức về codebase.  
**3\. Mục tiêu Tổng thể của RepoChat (Dài hạn)**

* Cung cấp các phân tích kiến trúc sâu sắc, tự động xác định các anti-pattern, đánh giá sự tuân thủ các nguyên tắc thiết kế.  
* Đưa ra những đánh giá tác động của Pull Request (PR) một cách toàn diện, bao gồm cả các ảnh hưởng tiềm ẩn đến các module khác hoặc các khía cạnh phi chức năng.  
* Cho phép tương tác hỏi-đáp (Q\&A) một cách tự nhiên về codebase, giúp nhà phát triển nhanh chóng hiểu rõ các phần code phức tạp hoặc tìm kiếm thông tin liên quan.  
* Hỗ trợ đa dạng ngôn ngữ lập trình phổ biến.  
* Cung cấp giao diện người dùng thân thiện, trực quan và mang tính hội thoại.  
* Liên tục học hỏi và cải thiện từ phản hồi của người dùng và các codebase mới.

4\. Mục tiêu và Phạm vi cụ thể cho RepoChat v1.0 (Yêu cầu Bắt buộc)  
Phiên bản 1.0 của RepoChat sẽ tập trung vào việc xây dựng nền tảng cốt lõi và cung cấp các tính năng thiết yếu để chứng minh giá trị của giải pháp.

* **Ngôn ngữ Lập trình Bắt buộc Hỗ trợ:**  
  * Android: Java, Kotlin  
  * Flutter: Dart  
  * Python  
* **Các Tính năng Cốt lõi của v1.0:**  
  1. **Xây dựng Code Knowledge Graph (CKG):** Tạo CKG cơ bản cho các ngôn ngữ mục tiêu, nắm bắt các cấu trúc (files, classes, functions/methods, interfaces) và mối quan hệ chính (lời gọi hàm/method trực tiếp, kế thừa, hiện thực hóa, import/dependencies).  
  2. **Phân tích Kiến trúc (Cơ bản):**  
     * Phát hiện circular dependencies ở cấp độ file/module.  
     * Gợi ý các public elements (methods, classes) có khả năng không được sử dụng trong phạm vi codebase đã phân tích (cần có cảnh báo rõ ràng về hạn chế của phân tích tĩnh trong trường hợp này, ví dụ như reflection, DI).  
  3. **Phân tích Pull Request (PR) (Cơ bản):**  
     * Phân tích diff của PR, *sử dụng CKG để xác định các thành phần code bị ảnh hưởng và* cung cấp tóm tắt bằng văn bản về các thay đổi chính và các tác động trực tiếp ở "mức độ 1" (ví dụ: function A được thay đổi, function A được gọi bởi B và gọi đến C).  
  4. **Hỏi-Đáp Tương tác (Q\&A Cơ bản):** Cho phép người dùng đặt các câu hỏi đơn giản về cấu trúc code (ví dụ: "Định nghĩa của class X ở đâu?", "Function Y gọi những hàm nào trong file này?").  
  5. **Sinh Sơ đồ Lớp (Class Diagram Cơ bản):** Tạo class diagram đơn giản theo yêu cầu cho một class hoặc module cụ thể.  
  6. **Giao diện Tương tác:** Ban đầu thông qua giao diện dòng lệnh (CLI) hoặc một giao diện web đơn giản.  
* **Chiến lược LLM cho v1.0:**  
  * Sử dụng API của OpenAI (ví dụ: các model GPT) làm LLM chính cho các tác vụ xử lý ngôn ngữ tự nhiên, tóm tắt và hỗ trợ Q\&A.  
  * Thiết kế hệ thống phải đảm bảo **khả năng mở rộng và thay thế** dễ dàng sang các nhà cung cấp LLM khác hoặc các mô hình LLM chạy local trong tương lai.  
* **Xử lý Personal Access Token (PAT):**  
  * PAT **sẽ không được lưu trữ** một cách bền vững.  
  * Khi cần thiết cho các thao tác với Git (ví dụ: clone private repo), chatbot sẽ yêu cầu người dùng cung cấp PAT.  
  * PAT chỉ được sử dụng trong session hiện tại và sẽ được xóa khỏi bộ nhớ hoạt động (và ẩn khỏi lịch sử chat nếu có thể) ngay sau khi hoàn thành tác vụ.  
* **Xử lý Repository:**  
  * Khi clone repository, chỉ lấy code ở HEAD (git clone \--depth 1 ...) để tối ưu thời gian và tài nguyên.  
* **Ưu tiên Công nghệ:** Ưu tiên sử dụng các thư viện và công cụ mã nguồn mở cho tất cả các thành phần không phải là LLM API. Ngôn ngữ phát triển chính cho backend và các agent là **Python**.

5\. Mục đích của Tài liệu này  
Tài liệu này trình bày thiết kế chi tiết cho phiên bản 1.0 của RepoChat. Đồng thời, nó cũng đóng vai trò là một bản yêu cầu nghiên cứu chuyên sâu, đặt ra các câu hỏi và lĩnh vực cần sự phân tích từ Gemini Deep Research để tối ưu hóa, xác thực và nâng cao thiết kế hiện tại, cũng như định hướng cho các phiên bản tương lai.  
**Phần II: Kiến trúc Hệ thống Tổng quan của RepoChat**

RepoChat được thiết kế dựa trên kiến trúc đa agent (Agentic Multi-Agent System). Hệ thống bao gồm một tập hợp các "TEAM" agent chuyên biệt, mỗi TEAM chịu trách nhiệm về một khía cạnh cụ thể của quy trình review code. Các TEAM này sẽ tương tác và phối hợp nhịp nhàng với nhau dưới sự điều phối của một **Orchestrator Agent** trung tâm.

**Sơ đồ Tương tác Tổng quan giữa các TEAM Agent (Đã cập nhật):**

graph TD  
    UI\[User Interface (Vue.js)\] \--\> Orchestrator;  
    Orchestrator \--\> TI\[TEAM Interaction & Tasking\];  
    TI \--\> Orchestrator;  
    Orchestrator \--\> TDA\[TEAM Data Acquisition\];  
    TDA \--\> Orchestrator;  
    Orchestrator \--\> TCKG\[TEAM CKG Operations\];  
    TCKG \--\> Orchestrator;  
    TCA\[TEAM Code Analysis\] \--\> TCKG; %% TCA queries CKG  
    Orchestrator \--\> TCA;  
    TCA \--\> Orchestrator;  
    TCA \-- Request LLM Service via Orchestrator \--\> Orchestrator;  
    Orchestrator \--\> TLLM\[TEAM LLM Services\];  
    TLLM \--\> Orchestrator;  
    Orchestrator \--\> TSR\[TEAM Synthesis & Reporting\];  
    TSR \-- Request LLM Service via Orchestrator \--\> Orchestrator;  
    TSR \--\> Orchestrator; %% TSR sends final report to Orchestrator

    subgraph RepoChat Core System  
        direction LR  
        Orchestrator;  
        subgraph UserFacingAgents  
            TI;  
        end  
        subgraph DataProcessingAgents  
            TDA;  
            TCKG;  
            TCA;  
        end  
        subgraph ServiceAgents  
            TLLM;  
        end  
        subgraph OutputAgents  
            TSR;  
        end  
    end

    style Orchestrator fill:\#daffc4,stroke:\#333,stroke-width:2px  
    style TI fill:\#c4e4ff,stroke:\#333,stroke-width:2px  
    style TDA fill:\#c4e4ff,stroke:\#333,stroke-width:2px  
    style TCKG fill:\#fff5c4,stroke:\#333,stroke-width:2px  
    style TCA fill:\#fff5c4,stroke:\#333,stroke-width:2px  
    style TLLM fill:\#ffc4c4,stroke:\#333,stroke-width:2px  
    style TSR fill:\#e6c4ff,stroke:\#333,stroke-width:2px

**Các TEAM Agent chính bao gồm:**

1. **TEAM Interaction & Tasking (Đội Tương tác & Quản lý Tác vụ)**  
2. **TEAM Data Acquisition (Đội Thu thập & Chuẩn bị Dữ liệu)**  
3. **TEAM CKG Operations (Đội Vận hành Code Knowledge Graph)**  
4. **TEAM Code Analysis (Đội Phân tích Mã nguồn)**  
5. **TEAM LLM Services (Đội Dịch vụ LLM)**  
6. **TEAM Synthesis & Reporting (Đội Tổng hợp & Báo cáo)**

**Phần II.A: Ngăn xếp Công nghệ Chủ chốt (v1.0)**

1. **Ngôn ngữ Phát triển Backend & Agent:** **Python** là ngôn ngữ chính.  
2. **Framework Phát triển Agent:** Khái niệm "Google's Agent Development Kit (ADK)" được sử dụng như một placeholder cho một framework phát triển agent phù hợp. Các thư viện như Langchain/LangGraph có thể đóng vai trò này.  
3. **Giao thức Giao tiếp giữa các Agent:** Khái niệm "Google's Agent-to-Agent Communication Protocol (A2A Protocol)" được sử dụng như một placeholder. Các giao thức cụ thể như Task Definition Protocol (TDP), Agent State Communication Protocol (ASCP), LLMServiceRequest Protocol (LSRP) sẽ định nghĩa các khía cạnh của giao tiếp này, có thể được xây dựng trên nền tảng HTTP/WebSocket hoặc message queues.  
4. **Orchestration Layer:** **Langchain/LangGraph** (xây dựng trên nền Python).  
5. **LLM (v1.0):** API của **OpenAI** (với thiết kế lớp trừu tượng để mở rộng).  
6. **Code Knowledge Graph (CKG) \- Lưu trữ:** **Neo4j Community Edition**.  
7. **Frontend:** **Vue.js**.  
8. **Công cụ Parsing (ví dụ):** javaparser (Java), Kotlin Compiler API/Detekt (Kotlin), Dart analyzer package (Dart), ast module (Python).  
9. **Tương tác Git:** gitpython.  
10. **Quản lý Session Memory (ngắn hạn):** Mem0 (hoặc tương đương).  
11. **Các thư viện khác:** Ưu tiên mã nguồn mở và tương thích với Python.

**Phần III: Thiết kế Chi tiết các TEAM Agent (Đã cập nhật với Phản hồi từ Reviewer và Lựa chọn Công nghệ)**

### **A. Orchestrator Agent (Agent Điều phối Trung tâm)**

1. Mục tiêu chung:  
   Điều phối tổng thể luồng công việc, quản lý tác vụ và đảm bảo sự tương tác trơn tru và hiệu quả giữa tất cả các TEAM agent trong hệ thống RepoChat.  
2. **Trách nhiệm chính:**  
   * Tiếp nhận yêu cầu tác vụ đã được chuẩn hóa từ TEAM Interaction & Tasking (bao gồm cả cấu hình LLM do người dùng chọn cho tác vụ đó).  
   * Kích hoạt các TEAM agent theo đúng trình tự logic của một phiên review code (ví dụ: Data Acquisition \-\> CKG Operations \-\> Code Analysis \-\> Synthesis & Reporting).  
   * Truyền tải thông tin cấu hình LLM (từ TaskDefinition) đến các TEAM liên quan (TCA, TSR) khi kích hoạt chúng.  
   * Điều phối các yêu cầu sử dụng dịch vụ LLM từ TEAM Code Analysis và TEAM Synthesis & Reporting đến TEAM LLM Services, chuyển tiếp LLMServiceRequest (đã bao gồm cấu hình LLM từ TaskDefinition) và nhận lại LLMServiceResponse.  
   * Quản lý trạng thái (pending, running, completed, failed) của tác vụ review tổng thể và của từng bước do các TEAM thực hiện.  
   * Đảm bảo dữ liệu (inputs/outputs) được chuyển giao chính xác và kịp thời giữa các TEAM.  
   * Xử lý các ngoại lệ, lỗi phát sinh từ các TEAM ở cấp độ luồng công việc và quyết định các hành động khắc phục (ví dụ: thử lại, báo lỗi cho người dùng).  
   * Quản lý ưu tiên tác vụ, cho phép thực hiện một số phân tích không critique path ở chế độ nền và thông báo khi hoàn tất để tối ưu thời gian phản hồi cho người dùng.  
3. **Input chính:**  
   * TaskDefinition object (định nghĩa tác vụ review chi tiết, bao gồm cấu hình LLM) từ TEAM Interaction & Tasking.  
   * Thông điệp cập nhật trạng thái và kết quả từ các TEAM agent khác (truyền qua A2A Protocol).  
   * LLMServiceRequest từ TCA hoặc TSR (để định tuyến đến TLLM).  
4. **Output chính:**  
   * Lệnh kích hoạt (activation commands) và dữ liệu đầu vào (bao gồm cấu hình LLM nếu có) cho các TEAM agent (truyền qua A2A Protocol).  
   * LLMServiceRequest được chuyển tiếp đến TLLM.  
   * Thông tin cập nhật về trạng thái và tiến trình của tác vụ cho TEAM Interaction & Tasking (để hiển thị cho người dùng).  
   * Thông báo lỗi hoặc kết quả cuối cùng của tác vụ (ví dụ: FinalReviewReport từ TSR được chuyển cho TI).  
5. **Thành phần/Module Nội bộ (Xây dựng bằng Python, sử dụng LangGraph làm cốt lõi):**  
   * **WorkflowEngineModule** (Cốt lõi là LangGraph)  
     * **Mục tiêu:** Thực thi các luồng công việc đã được định nghĩa.  
     * **Trách nhiệm:** Dựa trên TaskDefinition, điều phối các bước, gọi các TEAM agent tương ứng thông qua A2A Protocol.  
     * **Input:** TaskDefinition, quy tắc luồng công việc (cấu hình trong LangGraph).  
     * **Output:** Lệnh gọi các TEAM (dưới dạng thông điệp A2A).  
   * **StateManagerModule**  
     * **Mục tiêu:** Theo dõi trạng thái của toàn bộ tác vụ và các bước con.  
     * **Trách nhiệm:** Cập nhật trạng thái dựa trên thông báo (ASCP payloads qua A2A) từ các TEAM.  
     * **Input:** Thông điệp trạng thái từ các TEAM.  
     * **Output:** Trạng thái hiện tại của tác vụ (lưu trữ nội bộ, có thể truy vấn).  
   * **ErrorHandlingModule**  
     * **Mục tiêu:** Xử lý lỗi một cách nhất quán.  
     * **Trách nhiệm:** Bắt lỗi từ các TEAM, quyết định hành động (retry, abort, notify). Ghi nhận cách lỗi từ một TEAM có thể ảnh hưởng đến luồng công việc chung (ví dụ: nếu TCKG xây dựng lỗi, các bước phân tích sau đó không thể tiếp tục). LangGraph sẽ hỗ trợ quản lý trạng thái và các nhánh điều kiện này.  
     * **Input:** Thông điệp lỗi (ASCP payloads qua A2A).  
     * **Output:** Hành động xử lý lỗi, thông báo lỗi.  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển:**  
   * Task Definition Protocol (TDP): Định dạng chuẩn (payload) cho việc mô tả một tác vụ review (bao gồm trường cho cấu hình LLM).  
   * Agent State Communication Protocol (ASCP): Định dạng chuẩn (payload) cho cách các TEAM báo cáo trạng thái.  
   * Workflow Engine: Xây dựng trên **LangGraph**.  
   * Giao thức giao tiếp giữa các Agent: (Định nghĩa cụ thể dựa trên HTTP/WebSocket hoặc message queues, truyền tải TDP, ASCP, LSRP).  
7. **Cơ chế Phối hợp:**  
   * Là trung tâm điều phối, nhận yêu cầu từ TEAM Interaction & Tasking.  
   * Tuần tự hoặc song song hóa việc gọi các TEAM qua A2A Protocol.  
   * Định tuyến các yêu cầu LLMServiceRequest từ TCA và TSR đến TLLM.  
   * Nhận FinalReviewReport từ TSR và chuyển cho TEAM Interaction & Tasking.  
   * Liên tục cập nhật trạng thái cho TEAM Interaction & Tasking.  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Adaptive and Dynamic Workflow Orchestration:** Làm thế nào Orchestrator (sử dụng LangGraph) có thể tự động điều chỉnh và tối ưu hóa luồng công việc dựa trên đặc điểm của từng project (ví dụ: kích thước, ngôn ngữ, loại thay đổi trong PR) hoặc dựa trên kết quả phân tích ban đầu từ các TEAM?  
   * **Advanced Fault Tolerance and Recovery Strategies:** Phát triển các chiến lược mạnh mẽ cho Orchestrator để xử lý lỗi từ các TEAM agent (ví dụ: timeout, lỗi tài nguyên, lỗi logic của agent) và có khả năng phục hồi quy trình một cách thông minh, giảm thiểu gián đoạn cho người dùng.  
   * **Resource Management for Concurrent Tasks:** Nếu hệ thống hỗ trợ nhiều người dùng hoặc nhiều tác vụ review đồng thời, Orchestrator cần quản lý tài nguyên (CPU, memory, API rate limits cho LLM) như thế nào để đảm bảo hiệu suất và sự ổn định?  
   * **Optimizing End-to-End Latency for Critical Path PR Analysis:** Nghiên cứu các kỹ thuật để giảm thiểu độ trễ từ lúc người dùng yêu cầu review PR đến khi nhận được các kết quả phân tích cốt lõi.  
   * **Configurable Notification and Reporting Verbosity:** Làm thế nào để Orchestrator và các TEAM liên quan có thể hỗ trợ các mức độ chi tiết thông báo và báo cáo khác nhau, tùy theo cấu hình của người dùng hoặc loại review?

### **B. TEAM Interaction & Tasking (Đội Tương tác & Quản lý Tác vụ)**

1. Mục tiêu chung của TEAM:  
   Là giao diện chính và bộ não giao tiếp của RepoChat với người dùng. Đảm bảo mọi yêu cầu của người dùng được hiểu chính xác, chuyển thành các tác vụ có cấu trúc cho hệ thống, và người dùng luôn được thông báo một cách rõ ràng, kịp thời về tiến trình cũng như kết quả.  
2. **Trách nhiệm chính của TEAM:**  
   * Tiếp nhận và phân tích yêu cầu dưới dạng ngôn ngữ tự nhiên từ người dùng thông qua các kênh giao tiếp (CLI, Web UI xây dựng bằng Vue.js).  
   * Quản lý và duy trì luồng hội thoại một cách mạch lạc, đặt các câu hỏi làm rõ khi thông tin cung cấp chưa đủ hoặc mơ hồ.  
   * Thu thập các thông tin ban đầu từ người dùng, bao gồm cả link đến PR description/ticket quản lý công việc (nếu người dùng cung cấp hoặc hệ thống có thể gợi ý).  
   * Cung cấp giao diện cho người dùng để truy cập và thay đổi các **Cài đặt (Settings)**, bao gồm cả việc **chọn model LLM cho từng TEAM agent/chức năng có sử dụng LLM.**  
   * Lưu trữ và truy xuất các cấu hình LLM của người dùng.  
   * Chuyển đổi yêu cầu đã được làm rõ của người dùng thành một TaskDefinition object chuẩn hóa, **bao gồm cả các lựa chọn cấu hình LLM do người dùng thiết lập cho tác vụ đó**, sẵn sàng để Orchestrator xử lý.  
   * Tiếp nhận và hiển thị các kết quả, báo cáo, sơ đồ, và thông báo trạng thái từ hệ thống cho người dùng một cách trực quan và dễ hiểu, bao gồm cả **ngữ cảnh nghiệp vụ của PR (title, description, link ticket)**.  
   * Quản lý trạng thái của phiên tương tác người dùng.  
   * Hỗ trợ người dùng đặt câu hỏi liên quan đến các gợi ý sửa lỗi do hệ thống cung cấp.  
3. **Input chính của TEAM:**  
   * Phát ngôn (text, commands) của người dùng từ giao diện Vue.js.  
   * Thông tin trạng thái tác vụ, thông báo lỗi, và kết quả/báo cáo cuối cùng từ Orchestrator (truyền qua A2A Protocol, payload theo ASCP, FinalReviewReport Schema).  
   * Lịch sử hội thoại của phiên làm việc hiện tại.  
   * Ngữ cảnh PR/Ticket từ TEAM Data Acquisition (thông qua Orchestrator, payload theo PDCS).  
   * Lựa chọn cấu hình LLM từ người dùng (qua màn hình Settings).  
4. **Output chính của TEAM:**  
   * TaskDefinition object chuẩn hóa (payload theo TDP), **bao gồm thông tin cấu hình LLM đã chọn**, được gửi đến Orchestrator qua A2A Protocol.  
   * Các câu hỏi làm rõ, thông báo xác nhận, thông báo trạng thái gửi đến người dùng (hiển thị trên UI Vue.js).  
   * Hiển thị báo cáo review, sơ đồ kiến trúc, các câu trả lời Q\&A, và ngữ cảnh PR/Ticket cho người dùng.  
   * Cấu hình LLM được lưu trữ (ví dụ: trong user profile database, quản lý bởi ConfigurationManagementAgent).  
5. **Thành viên Agent/Module trong TEAM (Xây dựng bằng Python):**  
   * **UserIntentParserAgent** (Có thể là một agent hoặc module NLU chuyên biệt)  
     * **Mục tiêu:** Phân tích và hiểu chính xác ý định cũng như các tham số quan trọng trong yêu cầu của người dùng.  
     * **Trách nhiệm:** Sử dụng NLU để phân tích văn bản, trích xuất thực thể (loại hành động, repo, PR ID, câu hỏi (bao gồm cả các câu hỏi về logic code, yêu cầu nghiệp vụ ở mức cơ bản), tên class/module cho sơ đồ, etc.).  
     * **Input:** Phát ngôn thô của người dùng, có thể kèm theo ngữ cảnh hội thoại.  
     * **Output:** Cấu trúc dữ liệu biểu diễn ý định và tham số (payload theo Intent Schema MCP).  
   * **DialogManagerAgent** (Có thể là một agent hoặc module quản lý hội thoại)  
     * **Mục tiêu:** Duy trì một cuộc hội thoại tự nhiên, mạch lạc và hiệu quả với người dùng.  
     * **Trách nhiệm:** Quyết định hành động tiếp theo (đặt câu hỏi, xác nhận, thông báo). Quản lý ngữ cảnh hội thoại. Hỗ trợ các luồng hội thoại liên quan đến việc người dùng hỏi về cách sửa lỗi hoặc làm rõ các vấn đề được báo cáo. Quản lý luồng hội thoại liên quan đến việc giải thích và hướng dẫn người dùng cấu hình model LLM trong màn hình Settings.  
     * **Input:** Output từ UserIntentParserAgent, lịch sử hội thoại, trạng thái hệ thống (nếu cần).  
     * **Output:** Thông điệp/câu hỏi được định dạng để gửi đến người dùng qua giao diện.  
   * **TaskInitiationModule**  
     * **Mục tiêu:** Tạo ra một TaskDefinition hoàn chỉnh.  
     * **Trách nhiệm:** Tổng hợp thông tin đã xác nhận để tạo TaskDefinition object theo TDP, **bao gồm cả các lựa chọn cấu hình LLM từ ConfigurationManagementAgent**.  
     * **Input:** Toàn bộ thông tin cần thiết cho một tác vụ đã được xác nhận, cấu hình LLM hiện tại của người dùng.  
     * **Output:** TaskDefinition object.  
   * **PresentationModule**  
     * **Mục tiêu:** Hiển thị thông tin từ hệ thống cho người dùng một cách rõ ràng và hữu ích.  
     * **Trách nhiệm:** Nhận báo cáo, sơ đồ, Q\&A, ngữ cảnh PR/Ticket, thông báo lỗi từ Orchestrator và định dạng chúng để hiển thị trên UI Vue.js. Hiển thị màn hình Settings và các tùy chọn cấu hình LLM. Định dạng và hiển thị các gợi ý refactor hoặc giải thích logic từ LLM.  
     * **Input:** Dữ liệu kết quả (báo cáo, sơ đồ, text, ngữ cảnh PR/Ticket) từ Orchestrator.  
     * **Output:** Nội dung được hiển thị trên UI.  
   * **ConfigurationManagementAgent** (Có thể là một agent hoặc module chuyên biệt)  
     * **Mục tiêu:** Quản lý việc lưu trữ và truy xuất các cài đặt của người dùng, bao gồm cả cấu hình LLM.  
     * **Trách nhiệm:** Tương tác với một cơ sở dữ liệu hoặc nơi lưu trữ cấu hình để lưu các lựa chọn model LLM của người dùng. Cung cấp các cấu hình này cho TaskInitiationModule khi tạo TaskDefinition.  
     * **Input:** Lựa chọn cấu hình từ người dùng (thông qua DialogManagerAgent/PresentationModule).  
     * **Output:** Cấu hình đã được lưu. Cung cấp cấu hình khi được yêu cầu.  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển cho TEAM:**  
   * Natural Language Understanding (NLU) Service: (Tích hợp Langchain hoặc API LLM).  
   * Intent Schema & Entity Definition MCP: Định dạng chuẩn (payload) cho ý định người dùng.  
   * Dialog State Management Protocol: Giao thức theo dõi trạng thái hội thoại.  
   * User Interface Abstraction Layer: (Để PresentationModule giao tiếp với Vue.js frontend).  
   * Session Memory Access: (Sử dụng Mem0).  
   * User Configuration Storage Mechanism: Giao diện để ConfigurationManagementAgent tương tác với nơi lưu trữ cấu hình.  
   * LLM Configuration Schema: Định dạng chuẩn để lưu trữ thông tin cấu hình LLM cho từng TEAM/agent.  
   * Giao thức giao tiếp với Orchestrator (A2A).  
7. **Cơ chế Phối hợp:**  
   * Là điểm bắt đầu và kết thúc của mọi tương tác với người dùng.  
   * UserIntentParserAgent và DialogManagerAgent phối hợp chặt chẽ để làm rõ yêu cầu.  
   * Khi đủ thông tin, TaskInitiationModule tạo TaskDefinition (bao gồm cấu hình LLM) và gửi cho Orchestrator qua A2A.  
   * PresentationModule nhận dữ liệu từ Orchestrator (A2A) để hiển thị.  
   * ConfigurationManagementAgent lưu và cung cấp cấu hình LLM.  
   * Liên tục nhận cập nhật trạng thái từ Orchestrator (A2A) để thông báo cho người dùng.  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Advanced NLU for Developer Queries:** Phát triển hoặc tích hợp các kỹ thuật NLU có khả năng hiểu sâu các truy vấn phức tạp, thuật ngữ kỹ thuật đặc thù, và ngữ cảnh ngầm trong các yêu cầu của nhà phát triển liên quan đến review code.  
   * **Proactive and Context-Aware Dialog Management:** Làm thế nào DialogManagerAgent có thể chủ động đưa ra các gợi ý hữu ích, dự đoán nhu cầu tiếp theo của người dùng, hoặc đề xuất các loại phân tích phù hợp dựa trên ngữ cảnh của codebase, ngữ cảnh PR/Ticket, hoặc các tương tác trước đó?  
   * **Personalized User Experience:** Nghiên cứu cách hệ thống có thể học hỏi từ lịch sử tương tác và phản hồi của từng người dùng để cá nhân hóa giao tiếp, các loại báo cáo được ưu tiên, hoặc các thiết lập review mặc định.  
   * **Multi-modal Interaction (Future):** Nghiên cứu khả năng tích hợp các kênh tương tác khác ngoài text (ví dụ: giọng nói, hoặc tương tác trực tiếp trên sơ đồ được hiển thị) cho các phiên bản tương lai.  
   * **Interactive Exploration of Code Issues and Solutions:** Thiết kế các luồng hội thoại cho phép người dùng không chỉ xem lỗi mà còn tương tác để hiểu sâu hơn về nguyên nhân và khám phá các giải pháp tiềm năng.  
   * **Integrating User Feedback on Review Findings:** Cơ chế để người dùng dễ dàng cung cấp phản hồi về phát hiện, và hệ thống dùng phản hồi đó để cải thiện.  
   * **Secure Management and Storage of User-Specific LLM Configurations:** Các best practice để lưu trữ an toàn các cấu hình LLM do người dùng lựa chọn.

### **C. TEAM Data Acquisition (Đội Thu thập & Chuẩn bị Dữ liệu)**

1. Mục tiêu chung của TEAM:  
   Đảm bảo thu thập mã nguồn, thông tin Pull Request (bao gồm cả title, description, và các liên kết đến hệ thống quản lý công việc), và các siêu dữ liệu liên quan một cách chính xác, hiệu quả và an toàn từ các nguồn được chỉ định. Đồng thời, xác định môi trường ngôn ngữ của dự án để cung cấp đầu vào đã được chuẩn bị cho các TEAM phân tích và xây dựng CKG.  
2. **Trách nhiệm chính của TEAM:**  
   * Thực hiện shallow clone repository từ URL được cung cấp.  
   * Tải xuống chi tiết của một Pull Request cụ thể, bao gồm **title, description đầy đủ, comments, và cố gắng trích xuất các liên kết đến hệ thống quản lý công việc (Jira, Trello, etc.)** nếu có trong description.  
   * Quản lý việc yêu cầu và sử dụng Personal Access Token (PAT) một cách an toàn và tạm thời cho việc truy cập các private repositories. PAT được xóa khỏi bộ nhớ ngay sau khi hoàn thành tác vụ Git.  
   * Xác định (các) ngôn ngữ lập trình chính được sử dụng trong codebase (Java, Kotlin, Dart, Python cho v1.0) và có thể cả các framework/thư viện chủ đạo.  
   * Chuẩn bị và cấu trúc toàn bộ dữ liệu đã thu thập (đường dẫn đến mã nguồn đã clone, thông tin PR bao gồm metadata, danh sách ngôn ngữ đã xác định) theo một định dạng chuẩn ("ProjectDataContext").  
3. **Input chính của TEAM:**  
   * TaskDefinition object từ Orchestrator (payload theo TDP, nhận qua A2A Protocol), chứa URL repo, PR ID, thông tin PAT.  
4. **Output chính của TEAM:**  
   * Một ProjectDataContext object/structure chuẩn hóa (payload theo PDCS, gửi cho Orchestrator qua A2A Protocol), chứa:  
     * Đường dẫn đến mã nguồn đã clone.  
     * Dữ liệu chi tiết của PR (diffs, metadata như title, description, issue tracker links).  
     * Danh sách các ngôn ngữ lập trình và (có thể) các framework chính đã được xác định.  
     * Session ID hoặc định danh cho dữ liệu tạm thời.  
5. **Thành viên Agent/Module trong TEAM (Xây dựng bằng Python):**  
   * **GitOperationsModule**  
     * **Mục tiêu:** Thực hiện thao tác Git (clone) và với API nền tảng Git (lấy thông tin PR).  
     * **Trách nhiệm:** Thực hiện git clone \--depth 1\. Fetch thông tin PR (diffs, commits, title, description, comments) từ API nền tảng Git (sử dụng PAT nếu PATHandlerModule cung cấp).  
     * **Input:** URL Repo, PR ID, (tùy chọn) PAT, cấu hình clone.  
     * **Output:** Đường dẫn code đã clone, dữ liệu PR thô (JSON từ API).  
   * **PRMetadataExtractorModule**  
     * **Mục tiêu:** Trích xuất thông tin giá trị từ mô tả và metadata của PR.  
     * **Trách nhiệm:** Phân tích description PR để trích xuất link đến issue tracker.  
     * **Input:** Dữ liệu PR thô (đặc biệt là description).  
     * **Output:** Danh sách issue tracker links (nếu có).  
   * **PATHandlerModule**  
     * **Mục tiêu:** Quản lý việc thu thập PAT từ người dùng an toàn và chỉ khi cần.  
     * **Trách nhiệm:** Nếu cần PAT, kích hoạt quy trình (qua Orchestrator \-\> TEAM Interaction) yêu cầu PAT. Lưu trữ PAT tạm thời (Mem0), cung cấp cho GitOperationsModule. Xóa PAT ngay lập tức sau khi dùng.  
     * **Input:** Yêu cầu cần PAT.  
     * **Output:** PAT (cho GitOperationsModule), trạng thái thu thập PAT.  
   * **LanguageIdentifierModule**  
     * **Mục tiêu:** Xác định chính xác ngôn ngữ và framework trong codebase.  
     * **Trách nhiệm:** Phân tích cấu trúc thư mục, extension file, file cấu hình (pom.xml, build.gradle, pubspec.yaml, requirements.txt, etc.).  
     * **Input:** Đường dẫn code đã clone.  
     * **Output:** Danh sách ngôn ngữ và framework (ví dụ: {"languages": \["java", "python"\], "frameworks": \["spring\_boot", "flask"\]}).  
   * **DataPreparationModule**  
     * **Mục tiêu:** Đảm bảo dữ liệu đầu vào cho TEAM sau được đóng gói chuẩn hóa.  
     * **Trách nhiệm:** Tập hợp output từ các module khác trong TEAM, đóng gói thành ProjectDataContext theo PDCS.  
     * **Input:** Đường dẫn code, dữ liệu PR, issue links, danh sách ngôn ngữ/framework.  
     * **Output:** ProjectDataContext object/structure hoàn chỉnh.  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển cho TEAM:**  
   * Git Interaction Libraries: (gitpython).  
   * Git Platform API Clients: (PyGithub).  
   * PAT Request & Handling Protocol (PRHP): MCP định nghĩa cách yêu cầu và nhận PAT.  
   * Language & Framework Detection Engine: (python-linguist hoặc tùy chỉnh).  
   * Issue Tracker Link Parsing Rules/Heuristics.  
   * ProjectDataContext Schema (PDCS): Schema (payload) cho ProjectDataContext.  
   * Giao thức giao tiếp với Orchestrator (A2A).  
7. **Cơ chế Phối hợp:**  
   * Nhận TaskDefinition từ Orchestrator qua A2A.  
   * Nếu cần PAT, PATHandlerModule phối hợp với Orchestrator và TEAM Interaction & Tasking qua A2A.  
   * Các module nội bộ xử lý.  
   * DataPreparationModule gửi ProjectDataContext (PDCS payload) cho Orchestrator qua A2A.  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Advanced Language & Framework Detection:** Phát triển kỹ thuật (ML) xác định chính xác ngôn ngữ, phiên bản, framework trong project phức tạp.  
   * **Efficient Handling of Very Large Repositories (Monorepos):** Ngoài shallow clone, nghiên cứu chiến lược khác (sparse checkout, phân tích theo module) cho codebase cực lớn.  
   * **Secure and Auditable PAT Management:** Nghiên cứu giải pháp SOTA xử lý thông tin nhạy cảm như PAT, đảm bảo an toàn và có khả năng audit log.  
   * **Reliable Extraction and Linking of PRs to Issue Management Systems:** Phát triển kỹ thuật (NLU/ML) trích xuất chính xác link ticket từ mô tả PR. Nghiên cứu khả năng truy cập API hệ thống quản lý issue.  
   * **Delta Code Fetching for PR Reviews:** Nghiên cứu cách chỉ fetch file bị ảnh hưởng và lịch sử liên quan đến PR.

### **D. TEAM CKG Operations (Đội Vận hành Code Knowledge Graph)**

1. Mục tiêu chung của TEAM:  
   Xây dựng, duy trì, cập nhật và cung cấp một Code Knowledge Graph (CKG) chính xác, toàn diện và dễ truy vấn làm nền tảng tri thức trung tâm cho RepoChat. CKG là "bộ não" lưu trữ hiểu biết cấu trúc và ngữ nghĩa của mã nguồn, bao gồm cả mối liên hệ cơ bản giữa code và test.  
2. **Trách nhiệm chính của TEAM:**  
   * Tiếp nhận dữ liệu mã nguồn đã được chuẩn bị (từ TEAM Data Acquisition).  
   * Thực hiện phân tích cú pháp (parsing) mã nguồn của các ngôn ngữ được hỗ trợ (Java, Kotlin, Dart, Python cho v1.0) để tạo ra Abstract Syntax Trees (ASTs).  
   * Trích xuất các thực thể code (files, classes, functions/methods, variables, interfaces, enums, etc.) và các mối quan hệ quan trọng giữa chúng (lời gọi hàm/method, kế thừa, hiện thực hóa, import/dependencies, chứa đựng, etc.), bao gồm cả việc **cố gắng xác định và liên kết các file/class/method test với các file/class/method code tương ứng** (ở mức cơ bản cho v1.0).  
   * Xây dựng (hoặc cập nhật) CKG bằng cách lưu trữ các thực thể và mối quan hệ này vào một graph database (Neo4j Community Edition cho v1.0).  
   * Cung cấp một giao diện/API chuẩn hóa và hiệu quả cho các TEAM khác (chủ yếu là TEAM Code Analysis) để truy vấn thông tin từ CKG.  
   * (Lộ trình tương lai) Quản lý phiên bản của CKG và thực hiện cập nhật CKG một cách tăng tiến khi có thay đổi trong mã nguồn.  
3. **Input chính của TEAM:**  
   * ProjectDataContext object từ TEAM Data Acquisition (payload theo PDCS, nhận qua A2A Protocol từ Orchestrator), chứa đường dẫn code và danh sách ngôn ngữ.  
   * (Tương lai) Thông tin về các thay đổi (diffs) trong mã nguồn để thực hiện cập nhật tăng tiến.  
4. **Output chính của TEAM:**  
   * Thông báo trạng thái xây dựng CKG (thành công, thất bại, cảnh báo) gửi Orchestrator qua A2A Protocol (payload theo ASCP).  
   * Một CKG đã được xây dựng/cập nhật trong graph database, sẵn sàng để CKGQueryInterfaceModule phục vụ.  
   * CKGQueryInterfaceModule cung cấp dịch vụ truy vấn (ví dụ: qua A2A với một CKG Query Protocol).  
5. **Thành viên Agent/Module trong TEAM (Xây dựng bằng Python):**  
   * **CodeParserCoordinatorModule**  
     * **Mục tiêu:** Quản lý và điều phối hiệu quả quá trình parsing cho các ngôn ngữ khác nhau.  
     * **Trách nhiệm:** Dựa trên danh sách ngôn ngữ từ ProjectDataContext, chọn và kích hoạt các parser chuyên biệt. Thu thập kết quả ASTs.  
     * **Input:** ProjectDataContext.  
     * **Output:** Tập hợp ASTs cho các file code liên quan.  
   * **ASTtoCKGBuilderModule**  
     * **Mục tiêu:** Chuyển đổi chính xác thông tin từ ASTs thành nodes và relationships trong CKG.  
     * **Trách nhiệm:** Duyệt ASTs, trích xuất thực thể code và mối quan hệ theo CKG Schema (bao gồm liên kết test). Tạo lệnh Cypher để ghi vào Neo4j.  
     * **Input:** Tập hợp ASTs, CKG Schema.  
     * **Output:** Các thay đổi được ghi vào CKG, trạng thái ghi dữ liệu.  
   * **CKGQueryInterfaceModule**  
     * **Mục tiêu:** Cung cấp cách thức chuẩn hóa, hiệu quả để agent khác truy vấn CKG.  
     * **Trách nhiệm:** Định nghĩa và triển khai API truy vấn CKG phổ biến (ví dụ: getClassDefinition(className), getTestsForClass(className)). Tối ưu hóa truy vấn.  
     * **Input:** Yêu cầu truy vấn CKG (từ TEAM Code Analysis, payload theo CKG Query Protocol qua A2A).  
     * **Output:** Kết quả truy vấn CKG (dạng JSON, list of objects).  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển cho TEAM:**  
   * Bộ Parsers chuyên biệt: javaparser, Kotlin Compiler API/Detekt, Dart analyzer, Python ast.  
   * CKG Schema Definition (CKGSD): Tài liệu/file mô tả cấu trúc CKG (bao gồm thực thể test).  
   * AST-to-CKG Mapping Rules: Bộ quy tắc code hóa chuyển đổi AST sang CKG.  
   * Test Code Identification Heuristics: Quy tắc nhận diện thành phần test.  
   * CKG Query API Specification / CKG Query Protocol (CKGQP): Định nghĩa API và payload cho truy vấn CKG.  
   * Graph Database Client/Driver: neo4j Python driver.  
   * Giao thức giao tiếp với Orchestrator và TEAM Code Analysis (A2A).  
7. **Cơ chế Phối hợp:**  
   * Nhận ProjectDataContext từ Orchestrator (A2A).  
   * Các module nội bộ xử lý.  
   * Thông báo trạng thái xây dựng CKG cho Orchestrator (A2A).  
   * CKGQueryInterfaceModule phục vụ yêu cầu truy vấn từ TEAM Code Analysis (A2A).  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Tối ưu Schema CKG cho Phân tích Đa Ngôn ngữ và Sâu:** Nghiên cứu schema CKG hợp nhất tối ưu cho Java, Kotlin, Dart, Python, hỗ trợ truy vấn phức tạp về kiến trúc, luồng dữ liệu, và mối liên hệ code-test.  
   * **Xây dựng CKG Tăng tiến (Incremental CKG Updates) Hiệu quả:** Phát triển thuật toán và kiến trúc cập nhật CKG thông minh chỉ dựa trên diffs code.  
   * **Kỹ thuật Semantic Enrichment cho CKG:** Nghiên cứu kỹ thuật (ML/LLM, phân tích tĩnh) làm giàu CKG với thông tin ngữ nghĩa cao hơn (type inference, design pattern, liên kết code với yêu cầu).  
   * **So sánh và Đánh giá các Graph Databases Mã nguồn mở cho CKG:** Đánh giá sâu hơn Neo4j CE và các lựa chọn khác (JanusGraph, ArangoDB, etc.) về hiệu năng, mở rộng, tính năng cho RepoChat.  
   * **Version Control cho CKG:** Nghiên cứu phương pháp quản lý phiên bản CKG tương ứng với phiên bản mã nguồn.  
   * **Reliable Mapping Between Source Code and Test Code in CKG:** Phát triển thuật toán và heuristics chính xác hơn để tự động liên kết test units với code units.  
   * **Inferring Test Coverage Semantics from CKG:** Nghiên cứu cách CKG có thể được sử dụng để suy luận sâu hơn về phạm vi bao phủ của test.

### **E. TEAM Code Analysis (Đội Phân tích Mã nguồn)**

1. Mục tiêu chung của TEAM:  
   Thực hiện các phân tích chuyên sâu và đa dạng trên mã nguồn (đã được biểu diễn trong CKG), kết hợp với khả năng suy luận của LLM và ngữ cảnh từ PR/Ticket, để phát hiện các vấn đề tiềm ẩn, các điểm cần cải thiện về kiến trúc, chất lượng code, mức độ kiểm thử cơ bản, và cung cấp các hiểu biết giá trị cho người dùng.  
2. **Trách nhiệm chính của TEAM (v1.0):**  
   * Truy vấn CKG một cách hiệu quả (thông qua CKGQueryInterfaceModule của TEAM CKG Operations) để thu thập thông tin cấu trúc, mối quan hệ và siêu dữ liệu cần thiết.  
   * **Thực hiện Phân tích Kiến trúc (Cơ bản):**  
     * Phát hiện các circular dependencies ở cấp độ file/module.  
     * Đưa ra gợi ý về các public methods/classes có khả năng không được sử dụng với **độ tin cậy thấp và cảnh báo rõ ràng**, cho phép người dùng cấu hình để loại trừ các pattern/annotation cụ thể.  
   * **Thực hiện Phân tích Liên quan đến Test (Cơ bản):**  
     * Dựa trên CKG và thông tin diff của PR, đưa ra các nhận xét heuristic như: "PR thêm N hàm public mới vào Class A. File TestClassA có M hàm test mới không?" hoặc "Method M trong Class A bị thay đổi. Các test liên quan đến M trong TestClassA có được cập nhật trong PR này không?"  
   * **Tích hợp và Điều phối việc chạy các Linter/Static Analyzer:** Kích hoạt các công cụ linter/static analyzer tiêu chuẩn cho từng ngôn ngữ và thu thập, chuẩn hóa kết quả của chúng.  
   * **Chuẩn bị Ngữ cảnh cho Phân tích Logic & Q\&A bởi LLM:** Trích xuất các đoạn code liên quan, thông tin ngữ cảnh từ CKG và metadata của PR (bao gồm title, description, issue links từ ProjectDataContext và cấu hình LLM từ TaskDefinition) để tạo LLMServiceRequest gửi đến TEAM LLM Services (thông qua Orchestrator).  
3. **Input chính của TEAM:**  
   * Quyền truy cập vào CKG (thông qua CKGQueryInterfaceModule của TEAM CKG Operations, sử dụng A2A Protocol với CKGQP payload).  
   * TaskDefinition từ Orchestrator (payload theo TDP, nhận qua A2A, bao gồm cấu hình LLM).  
   * ProjectDataContext (payload theo PDCS, nhận qua A2A, chứa đường dẫn code, ngôn ngữ, và metadata của PR).  
4. **Output chính của TEAM:**  
   * Một tập hợp các "Phát hiện Phân tích" (Analysis Findings) được cấu trúc (payload theo SFF \- Standardized Finding Format, gửi cho Orchestrator qua A2A), bao gồm:  
     * Mô tả vấn đề (kiến trúc, linter, quan sát về test).  
     * Mức độ nghiêm trọng (gợi ý).  
     * Vị trí trong code (file, dòng).  
   * LLMServiceRequest object/structure (payload theo LSRP, gửi cho Orchestrator để định tuyến đến TEAM LLM Services), chứa ngữ cảnh và cấu hình LLM.  
5. **Thành viên Agent/Module trong TEAM (Xây dựng bằng Python):**  
   * **ArchitecturalAnalyzerModule**  
     * **Mục tiêu:** Phát hiện các vấn đề và rủi ro liên quan đến kiến trúc phần mềm.  
     * **Trách nhiệm (v1.0):** Truy vấn CKG phát hiện circular dependencies (file/module). Truy vấn CKG tìm public entities có thể không được sử dụng (áp dụng bộ lọc cấu hình, gắn nhãn độ tin cậy thấp).  
     * **Input:** Quyền truy cập CKG, quy tắc kiến trúc, cấu hình loại trừ "unused code".  
     * **Output:** Danh sách các vấn đề kiến trúc (payload theo SFF).  
   * **TestCoModificationCheckerModule**  
     * **Mục tiêu:** Cung cấp nhận xét cơ bản về việc code test có được cập nhật tương ứng với thay đổi code logic trong PR không.  
     * **Trách nhiệm (v1.0):** Truy vấn CKG tìm liên kết code-test. Phân tích diff PR xem code/test tương ứng có cùng thay đổi không. Tạo "Observation" heuristic.  
     * **Input:** Quyền truy cập CKG, ProjectDataContext (chứa diff PR).  
     * **Output:** Danh sách quan sát về test (payload theo SFF).  
   * **StaticAnalysisIntegratorModule**  
     * **Mục tiêu:** Tận dụng và tích hợp kết quả từ các linter/static analyzer.  
     * **Trách nhiệm:** Kích hoạt linter phù hợp dựa trên ngôn ngữ. Thu thập và chuẩn hóa output thành định dạng "Finding" chung (SFF).  
     * **Input:** ProjectDataContext (đường dẫn code, ngôn ngữ), cấu hình linter.  
     * **Output:** Danh sách "Finding" từ linter (payload theo SFF).  
   * **CKGQueryHelperModule** (Module tiện ích nội bộ)  
     * **Mục tiêu:** Cung cấp các hàm tiện ích để các module khác trong TEAM dễ dàng xây dựng và thực thi các truy vấn CKG phổ biến hoặc phức tạp.  
     * **Trách nhiệm:** Đóng gói logic truy vấn Cypher hoặc các lời gọi API của CKGQueryInterfaceModule thành các hàm dễ sử dụng.  
     * **Input:** Tham số truy vấn cụ thể.  
     * **Output:** Kết quả truy vấn CKG đã được xử lý sơ bộ (nếu cần).  
   * **LLMAnalysisSupportModule**  
     * **Mục tiêu:** Chuẩn bị dữ liệu và tạo yêu cầu để TEAM LLM Services thực hiện phân tích hoặc trả lời câu hỏi.  
     * **Trách nhiệm:** Tập hợp code liên quan, thông tin ngữ cảnh CKG, và ngữ cảnh PR (title, description, issue links từ ProjectDataContext). Tạo LLMServiceRequest (LSRP payload), **bao gồm cả thông tin cấu hình LLM từ TaskDefinition**.  
     * **Input:** Đoạn code, thông tin ngữ cảnh CKG, ngữ cảnh PR/Ticket, câu hỏi/yêu cầu phân tích, cấu hình LLM.  
     * **Output:** LLMServiceRequest object/structure.  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển cho TEAM:**  
   * CKG Query API Client (để tương tác với TEAM CKG Operations qua A2A).  
   * Linter Execution Framework.  
   * Standardized Finding Format (SFF): MCP (payload) cho "Phát hiện Phân tích".  
   * LLMServiceRequest Protocol (LSRP): MCP (payload) cho yêu cầu gửi TEAM LLM Services.  
   * Configuration for Unused Code Detection.  
   * Giao thức giao tiếp với Orchestrator và TEAM CKG Operations (A2A).  
7. **Cơ chế Phối hợp:**  
   * Nhận yêu cầu, ProjectDataContext, và TaskDefinition (chứa cấu hình LLM) từ Orchestrator (A2A).  
   * Các module nội bộ hoạt động, sử dụng CKGQueryHelperModule và truy vấn TEAM CKG Operations.  
   * LLMAnalysisSupportModule gửi LLMServiceRequest (LSRP payload, bao gồm cấu hình LLM) đến Orchestrator để định tuyến cho TEAM LLM Services.  
   * Các "Finding" (SFF payload) được gửi cho Orchestrator (A2A) để chuyển cho TEAM Synthesis & Reporting.  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Phát hiện Anti-Pattern Kiến trúc Nâng cao và Đa Ngôn ngữ:** Phát triển thuật toán/mô hình (CKG \+ ML/LLM) phát hiện anti-pattern phức tạp trên Java, Kotlin, Dart, Python.  
   * **Phân tích Luồng Dữ liệu (Data Flow Analysis) trên CKG:** Nghiên cứu biểu diễn và phân tích luồng dữ liệu trong CKG để phát hiện vấn đề (biến không dùng, null pointer, lỗ hổng bảo mật).  
   * **Đánh giá Rủi ro Thay đổi và Phân tích Tác động PR Sâu sắc:** Kỹ thuật dự đoán rủi ro của PR dựa trên CKG, lịch sử commit, test.  
   * **Tự động Gợi ý Refactoring Thông minh:** Hệ thống có thể gợi ý giải pháp refactoring và tự động tạo code refactor cơ bản không?  
   * **Đo lường và Cải thiện "Code Quality" Toàn diện:** Đánh giá các khía cạnh trừu tượng (readability, maintainability, modularity) dựa trên CKG và LLM.  
   * **Leveraging PR/Ticket Context for Deeper Code Understanding by LLMs:** Nghiên cứu cách LLM sử dụng hiệu quả thông tin từ mô tả PR/ticket để hiểu "ý định" thay đổi code.  
   * **Heuristics and LLM-based Analysis for Assessing Basic Test Co-modification and Potential Coverage Gaps:** Phát triển phương pháp đánh giá xem thay đổi code có đi kèm cập nhật test phù hợp không.  
   * **Reducing False Positives in Static & LLM-based Security Vulnerability Detection:** Cải thiện tỷ lệ signal-to-noise cho cảnh báo bảo mật.

### **F. TEAM LLM Services (Đội Dịch vụ LLM)**

1. Mục tiêu chung của TEAM:  
   Đóng vai trò là một trung tâm dịch vụ chuyên biệt và được tối ưu hóa cho tất cả các tương tác với Mô hình Ngôn ngữ Lớn (LLM). Đảm bảo việc sử dụng LLM trong RepoChat là hiệu quả, nhất quán, dễ quản lý và có khả năng mở rộng sang các nhà cung cấp LLM khác nhau trong tương lai, đồng thời tôn trọng cấu hình LLM được cung cấp trong mỗi yêu cầu.  
2. **Trách nhiệm chính của TEAM:**  
   * Tiếp nhận các LLMServiceRequest (bao gồm dữ liệu ngữ cảnh và **thông tin cấu hình LLM cụ thể cho yêu cầu đó**) từ Orchestrator.  
   * **Định tuyến Yêu cầu đến Model LLM Phù hợp:** Dựa trên **cấu hình LLM được cung cấp trong LLMServiceRequest**, chọn đúng nhà cung cấp và model LLM để thực thi yêu cầu.  
   * Quản lý **Lớp Trừu tượng LLM (LLM Abstraction Layer)**: Cung cấp interface nội bộ nhất quán, có khả năng làm việc với nhiều model/provider khác nhau.  
   * **Quản lý và Tối ưu hóa Prompt:** Xây dựng, lưu trữ, phiên bản hóa và tối ưu hóa các prompt cho từng tác vụ (bao gồm prompt phân tích code dựa trên mô tả PR, gợi ý refactor).  
   * **Quản lý Ngữ cảnh:** Nhận ngữ cảnh (code, CKG info, PR/Ticket info) từ LLMServiceRequest; xử lý, cắt tỉa, định dạng tối ưu trước khi gửi cho LLM.  
   * Thực thi các lời gọi đến API của LLM.  
   * Xử lý phản hồi từ LLM (parse output, xử lý lỗi cơ bản).  
   * Trả LLMServiceResponse về cho Orchestrator.  
   * (Tương lai) Quản lý rate limiting, retry logic, theo dõi chi phí, fine-tuning.  
3. **Input chính của TEAM:**  
   * LLMServiceRequest object/structure (payload theo LSRP, nhận từ Orchestrator qua A2A Protocol), chứa:  
     * Loại tác vụ LLM (ví dụ: EXPLAIN\_CODE, ANALYZE\_CODE\_AGAINST\_PR\_DESC, SUGGEST\_REFACTORING).  
     * Dữ liệu ngữ cảnh (code snippets, CKG data excerpts, user query, **PR title/description/issue links**).  
     * **Thông tin cấu hình LLM (model, provider, các tham số) cho yêu cầu cụ thể này.**  
     * (Có thể) ID của một prompt template cụ thể.  
4. **Output chính của TEAM:**  
   * LLMServiceResponse object/structure (payload theo LSRP, gửi cho Orchestrator qua A2A Protocol), chứa:  
     * Kết quả do LLM tạo ra.  
     * Trạng thái xử lý.  
     * (Có thể) Metadata về lời gọi LLM.  
5. **Thành viên Module/Component chuyên biệt trong TEAM (Xây dựng bằng Python):**  
   * **LLMGatewayModule**  
     * **Mục tiêu:** Là điểm vào duy nhất và được quản lý cho tất cả các yêu cầu tương tác với LLM.  
     * **Trách nhiệm:** Tiếp nhận LLMServiceRequest từ Orchestrator. **Sử dụng thông tin cấu hình LLM có sẵn trong LLMServiceRequest** để phối hợp với PromptFormatterModule và ContextProviderModule. Gọi LLM provider qua LLMProviderAbstractionLayer. Đóng gói LLMServiceResponse.  
     * **Input:** LLMServiceRequest (bao gồm cấu hình LLM).  
     * **Output:** LLMServiceResponse.  
   * **PromptFormatterModule**  
     * **Mục tiêu:** Cung cấp prompt đã được thiết kế và tối ưu hóa.  
     * **Trách nhiệm:** Lưu trữ thư viện prompt template (bao gồm template cho phân tích code dựa trên yêu cầu nghiệp vụ, gợi ý refactor). Chọn template, điền ngữ cảnh.  
     * **Input:** Loại tác vụ LLM, dữ liệu ngữ cảnh thô, ID prompt template.  
     * **Output:** Prompt hoàn chỉnh.  
   * **ContextProviderModule**  
     * **Mục tiêu:** Chuẩn bị và tối ưu hóa ngữ cảnh cho LLM.  
     * **Trách nhiệm:** Nhận dữ liệu ngữ cảnh (bao gồm thông tin từ PR/Ticket). Áp dụng kỹ thuật chọn lọc, tóm tắt, cắt tỉa. Định dạng ngữ cảnh.  
     * **Input:** Dữ liệu ngữ cảnh thô, thông tin context window LLM.  
     * **Output:** Ngữ cảnh đã xử lý.  
   * **LLMProviderAbstractionLayer (Thư viện/Interface cốt lõi)**  
     * **Mục tiêu:** Cho phép hệ thống dễ dàng chuyển đổi giữa các nhà cung cấp LLM.  
     * **Trách nhiệm:** Định nghĩa interface chung (complete(prompt, params)). Các implementation cụ thể (OpenAIProvider, AzureOpenAIProvider, LocalLlamaProvider) hiện thực hóa interface này, **hỗ trợ nhiều implementation cho các provider và model khác nhau (ví dụ: OpenAI\_GPT4oMini\_Provider, OpenAI\_GPT4Turbo\_Provider).**  
     * **Input:** Prompt, các tham số cấu hình LLM (từ LLMServiceRequest).  
     * **Output:** Phản hồi thô từ API của LLM.  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển cho TEAM:**  
   * LLMServiceRequest/Response Protocol (LSRP): MCP (payload) cho yêu cầu và phản hồi dịch vụ LLM (yêu cầu phải bao gồm cấu hình LLM).  
   * Prompt Template Library/Management System.  
   * Contextualization Engine Rules.  
   * API Clients for LLM Providers: (Thư viện openai cho Python).  
   * LLM Abstraction Interface Definition.  
   * Giao thức giao tiếp với Orchestrator (A2A).  
7. **Cơ chế Phối hợp:**  
   * Hoạt động như một TEAM dịch vụ. Nhận LLMServiceRequest (LSRP payload, bao gồm cấu hình LLM) từ Orchestrator qua A2A.  
   * LLMGatewayModule xử lý yêu cầu dựa trên cấu hình LLM được cung cấp.  
   * Trả LLMServiceResponse (LSRP payload) về cho Orchestrator qua A2A.  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Thiết kế Tối ưu và Linh hoạt cho LLM Abstraction Layer:** Nghiên cứu design pattern và kiến trúc tốt nhất cho lớp trừu tượng LLM.  
   * **Advanced Retrieval Augmented Generation (RAG) for Code Understanding:** Phát triển kiến trúc RAG tiên tiến, sử dụng CKG làm cơ sở tri thức.  
   * **Robust Prompt Engineering Framework for Code-Specific Tasks:** Xây dựng bộ khung hoặc best practices chi tiết cho prompt engineering.  
   * **Strategies for Evaluating, Monitoring, and Mitigating LLM Hallucinations in Code Context:** Phát triển phương pháp đáng tin cậy để phát hiện, đo lường và giảm thiểu "ảo giác" của LLM.  
   * **Cost-Performance Optimization for LLM Usage:** Nghiên cứu chiến lược tối ưu hóa chi phí sử dụng LLM API.  
   * **Feasibility and Roadmap for Fine-tuning/Specializing LLMs for RepoChat:** Đánh giá tính khả thi và lộ trình fine-tuning LLM mã nguồn mở.  
   * **LLM-Powered Analysis of Code Alignment with PR Descriptions and Requirements:** Phát triển kỹ thuật prompting và RAG cho phép LLM đánh giá xem code có giải quyết đúng vấn đề/yêu cầu trong PR/ticket không.  
   * **Generating Actionable Refactoring Suggestions with LLMs:** Nghiên cứu cách LLM có thể đưa ra gợi ý refactoring cụ thể, an toàn.  
   * **Dynamic LLM Model Selection and Orchestration:** Nghiên cứu kỹ thuật để RepoChat tự động chọn model LLM tối ưu cho từng tác vụ (có thể dựa trên cấu hình người dùng hoặc phân tích yêu cầu).  
   * **Performance and Cost Implications of Using Multiple LLM Models:** Phân tích chi tiết hiệu suất và chi phí khi hệ thống hỗ trợ và định tuyến giữa nhiều model LLM.

### **G. TEAM Synthesis & Reporting (Đội Tổng hợp & Báo cáo)**

1. Mục tiêu chung của TEAM:  
   Tổng hợp một cách thông minh tất cả các phát hiện, phân tích từ các TEAM khác (TEAM Code Analysis, TEAM LLM Services), tạo ra các báo cáo review code cuối cùng (dưới nhiều định dạng) một cách rõ ràng, dễ hiểu, có tính hành động cao, và hỗ trợ người dùng tương tác với kết quả thông qua việc sinh sơ đồ hoặc các hình thức trực quan hóa khác, có tích hợp ngữ cảnh PR/Ticket và các quan sát về test.  
2. **Trách nhiệm chính của TEAM (v1.0):**  
   * Thu thập và hợp nhất các "Phát hiện Phân tích" (Analysis Findings, payload theo SFF) từ TEAM Code Analysis (bao gồm output từ linter, các phân tích kiến trúc, **và các quan sát về test**), nhận từ Orchestrator.  
   * Tiếp nhận các kết quả phân tích hoặc nội dung đã được sinh bởi LLM (payload theo LSRP) từ TEAM LLM Services (thông qua Orchestrator).  
   * Sử dụng LLM (thông qua TEAM LLM Services, gửi yêu cầu qua Orchestrator, bao gồm cấu hình LLM từ TaskDefinition) để tóm tắt các phát hiện quan trọng, diễn giải các vấn đề kỹ thuật phức tạp bằng ngôn ngữ tự nhiên, dễ hiểu.  
   * Tạo ra báo cáo review code cuối cùng (ban đầu có thể là dạng text, markdown, hoặc JSON cấu trúc), **có thể bao gồm một phần tóm tắt về việc code thay đổi có vẻ khớp với mô tả PR/Ticket như thế nào** (dựa trên output từ LLM nếu có).  
   * **Sinh Sơ đồ Lớp (Class Diagram):** Dựa trên yêu cầu từ người dùng (trong TaskDefinition), truy vấn CKG để lấy dữ liệu cần thiết, sau đó sinh mã PlantUML/Mermaid.js.  
   * **Tạo Tóm tắt Tác động PR (bao gồm cả các quan sát về test liên quan đến thay đổi).**  
   * Định dạng toàn bộ output (FinalReviewReport) để gửi cho Orchestrator, sau đó Orchestrator chuyển cho TEAM Interaction & Tasking hiển thị.  
3. **Input chính của TEAM:**  
   * Tập hợp các AnalysisFinding object/structure (SFF payload) từ Orchestrator (nguồn gốc từ TEAM Code Analysis).  
   * Các LLMServiceResponse object/structure (LSRP payload) từ Orchestrator (nguồn gốc từ TEAM LLM Services).  
   * TaskDefinition (chứa yêu cầu sinh sơ đồ, loại báo cáo, và cấu hình LLM) từ Orchestrator.  
   * Quyền truy cập CKG (nếu cần, qua TEAM CKG Operations).  
   * Ngữ cảnh PR/Ticket (từ ProjectDataContext, nhận qua Orchestrator) để làm nổi bật trong báo cáo.  
4. **Output chính của TEAM:**  
   * FinalReviewReport object/structure (payload theo FinalReviewReport Schema, gửi cho Orchestrator qua A2A). Báo cáo này có thể chứa mã nguồn cho sơ đồ.  
5. **Thành viên Agent/Module trong TEAM (Xây dựng bằng Python):**  
   * **FindingAggregatorModule**  
     * **Mục tiêu:** Hợp nhất và xử lý thông minh các phát hiện từ nhiều nguồn.  
     * **Trách nhiệm:** Thu thập AnalysisFinding (bao gồm quan sát về test) và thông tin LLM. Loại bỏ trùng lặp. Ưu tiên phát hiện. Nhóm các phát hiện liên quan.  
     * **Input:** Danh sách AnalysisFinding, kết quả từ LLM.  
     * **Output:** Tập hợp phát hiện đã xử lý.  
   * **ReportGeneratorModule**  
     * **Mục tiêu:** Tạo báo cáo review code dễ đọc, dễ hiểu, mang tính hành động.  
     * **Trách nhiệm:** Sử dụng phát hiện đã tổng hợp. Yêu cầu TEAM LLM Services (thông qua Orchestrator, với cấu hình LLM từ TaskDefinition) sinh tóm tắt, giải thích, hoặc nhận xét về sự phù hợp của code với mô tả PR. Kết hợp thành báo cáo hoàn chỉnh, tích hợp quan sát về test.  
     * **Input:** Các phát hiện đã xử lý, quyền truy cập TEAM LLM Services (qua Orchestrator), ngữ cảnh PR/Ticket, cấu hình LLM.  
     * **Output:** Nội dung báo cáo review (text/markdown).  
   * **DiagramGeneratorModule**  
     * **Mục tiêu:** Tạo mã nguồn cho các sơ đồ kiến trúc theo yêu cầu.  
     * **Trách nhiệm (v1.0 \- Class Diagram):** Nhận yêu cầu sinh class diagram (từ TaskDefinition). Truy vấn CKG lấy thông tin class. Chuyển đổi thành cú pháp PlantUML/Mermaid.js.  
     * **Input:** Yêu cầu sinh sơ đồ, quyền truy cập CKG.  
     * **Output:** Chuỗi văn bản chứa mã nguồn PlantUML/Mermaid.js (để nhúng vào FinalReviewReport).  
   * **OutputFormatterModule**  
     * **Mục tiêu:** Đảm bảo tất cả thông tin trong báo cáo cuối cùng nhất quán và phù hợp.  
     * **Trách nhiệm:** Tập hợp nội dung báo cáo từ ReportGeneratorModule, mã sơ đồ từ DiagramGeneratorModule, và các thông tin khác. Đóng gói thành FinalReviewReport object/structure.  
     * **Input:** Nội dung báo cáo, mã sơ đồ, thông tin hiển thị khác.  
     * **Output:** FinalReviewReport object/structure.  
6. **Công cụ (Tools) / Giao thức Đa Ngữ cảnh (MCPs) cần phát triển cho TEAM:**  
   * FinalReviewReport Schema: MCP (payload) cho báo cáo review cuối cùng.  
   * Thư viện Sinh mã PlantUML/Mermaid.js.  
   * Template Engine (nếu cần).  
   * Giao thức giao tiếp với Orchestrator và TEAM CKG Operations (A2A).  
7. **Cơ chế Phối hợp:**  
   * Nhận dữ liệu (AnalysisFindings, LLMServiceResponse, TaskDefinition, ProjectDataContext) từ Orchestrator (A2A).  
   * Các module nội bộ phối hợp, yêu cầu dịch vụ từ TEAM LLM Services (thông qua Orchestrator, với cấu hình LLM) nếu cần.  
   * OutputFormatterModule đóng gói FinalReviewReport và gửi cho Orchestrator (A2A), Orchestrator chuyển cho TEAM Interaction & Tasking.  
8. **Chủ đề Nghiên cứu Chuyên sâu (Gemini Deep Research Topics):**  
   * **Tự động Tạo Báo cáo Review Code Thông minh và Có Tính Thuyết phục Cao:** Nghiên cứu cách LLM viết báo cáo review chuyên nghiệp, cung cấp ngữ cảnh sâu sắc, giải thích rủi ro/lợi ích, đưa ra gợi ý xây dựng.  
   * **Trực quan hóa Dữ liệu Phân tích Code Nâng cao và Tương tác:** Nghiên cứu phương pháp hiệu quả tự động sinh và trực quan hóa sơ đồ phức tạp hơn. Làm thế nào người dùng tương tác trực tiếp với sơ đồ trong chatbot?  
   * **Cá nhân hóa Báo cáo và Gợi ý:** Làm thế nào RepoChat tùy chỉnh nội dung và cách trình bày báo cáo dựa trên vai trò, kinh nghiệm người dùng?  
   * **Đo lường và Cải thiện Tính "Hành động được" (Actionability) của Báo cáo:** Phát triển metrics và phương pháp đánh giá xem báo cáo và gợi ý có thực sự giúp developer cải thiện code không.  
   * **Tích hợp Phản hồi Người dùng vào Chu trình Cải thiện Báo cáo:** Thiết kế cơ chế cho phép người dùng dễ dàng cung cấp phản hồi về tính hữu ích của từng phát hiện/gợi ý.  
   * **Presenting Test-Related Insights Effectively:** Nghiên cứu cách tốt nhất để trình bày các thông tin và quan sát liên quan đến việc kiểm thử trong báo cáo review.  
   * **Interactive Dashboards for Code Review Analytics (Future):** Khám phá khả năng tạo dashboard tương tác tổng hợp kết quả review, xu hướng chất lượng code.

**Phần IV: Luồng Hoạt động Người dùng Chi tiết (User Flows)**

Phần này mô tả chi tiết một số luồng tương tác chính của người dùng với hệ thống RepoChat, từ sau khi đăng nhập đến khi thực hiện các tác vụ review code.

**1\. Luồng Hoạt động Sau Đăng nhập và Màn hình Cài đặt (Settings)**

* **1.1. Giao diện Chính:**  
  * Sau khi người dùng đăng nhập thành công, họ sẽ được chuyển đến giao diện chính của ứng dụng RepoChat (xây dựng bằng Vue.js). Giao diện này được thiết kế theo dạng chatbot, tương tự như giao diện của Gemini (Google), với một khu vực chat trung tâm để tương tác.  
  * **Sidebar (Thanh bên):**  
    * **Lịch sử Chat (Chat History):** Hiển thị danh sách các cuộc hội thoại trước đó của người dùng với RepoChat. Người dùng có thể nhấp vào một mục lịch sử để xem lại nội dung chi tiết của cuộc hội thoại đó.  
    * **Nút "New Chat" (Tạo Chat Mới):** Cho phép người dùng bắt đầu một cuộc hội thoại/phiên làm việc mới hoàn toàn với RepoChat.  
    * **Nút "Settings" (Cài đặt):** Đưa người dùng đến màn hình Cài đặt của ứng dụng.  
  * **Khu vực Chat Chính:** Nơi người dùng nhập câu hỏi, yêu cầu và RepoChat phản hồi. Có khả năng hiển thị văn bản, code blocks, và các sơ đồ (do backend sinh mã, frontend Vue.js render).  
* **1.2. Màn hình Cài đặt (Settings Screen):**  
  * Khi người dùng nhấp vào nút "Settings", họ sẽ được chuyển đến một màn hình riêng cho phép tùy chỉnh các thiết lập của RepoChat.  
  * **Quản lý Tài khoản:** Các tùy chọn cơ bản như thay đổi mật khẩu, thông tin cá nhân.  
  * **Cấu hình Model LLM cho từng TEAM Agent/Chức năng (Tính năng quan trọng):**  
    * Giao diện sẽ liệt kê các TEAM agent (hoặc các nhóm chức năng chính) có sử dụng LLM và cho phép người dùng chọn model LLM cụ thể cho từng TEAM từ một danh sách các model được hỗ trợ (ví dụ: các phiên bản GPT của OpenAI, hoặc các model mã nguồn mở nếu được tích hợp trong tương lai).  
    * **Ví dụ:**  
      * **TEAM Interaction & Tasking (NLU và Dialog Management):** Có thể được cấu hình để sử dụng một model LLM nhỏ, nhanh và tiết kiệm chi phí (ví dụ: gpt-4o-mini).  
      * **TEAM Code Analysis (Phân tích code chuyên sâu, ví dụ qua LLMAnalysisSupportModule):** Có thể được cấu hình để sử dụng các model LLM lớn hơn, mạnh mẽ hơn và có khả năng suy luận về code tốt hơn (ví dụ: gpt-4-turbo).  
      * **TEAM Synthesis & Reporting (Tóm tắt và sinh báo cáo, ví dụ qua ReportGeneratorModule):** Có thể sử dụng model tối ưu cho việc tóm tắt và sinh văn bản mạch lạc.  
    * Hệ thống cần lưu trữ các lựa chọn này theo từng người dùng (thông qua ConfigurationManagementAgent của TEAM Interaction & Tasking).  
    * Khi người dùng khởi tạo một tác vụ mới, TaskInitiationModule sẽ lấy các cấu hình LLM này từ ConfigurationManagementAgent và đưa vào TaskDefinition.

**2\. Luồng Hoạt động Khởi tạo Tác vụ Review Code**

* **2.1. Bắt đầu Tương tác:**  
  * Tại màn hình Chat chính, RepoChat (DialogManagerAgent của TEAM Interaction & Tasking) sẽ chủ động hỏi người dùng: "Chào bạn, tôi có thể giúp gì cho bạn hôm nay? Bạn muốn thực hiện tác vụ nào? (Ví dụ: 'scan toàn bộ project' hoặc 'review PR')" hoặc người dùng có thể trực tiếp ra lệnh.  
* **2.2. Xử lý Yêu cầu "Scan Toàn bộ Project":**  
  1. **Người dùng nhập yêu cầu.**  
  2. **TEAM Interaction & Tasking (UserIntentParserAgent) phân tích:** Xác định ý định là "scan\_project".  
  3. **DialogManagerAgent phản hồi và yêu cầu thông tin:** "Tuyệt vời\! Để scan project, vui lòng cung cấp cho tôi URL của Git repository."  
  4. **Người dùng cung cấp URL.**  
  5. **DialogManagerAgent tiếp tục (nếu cần):**  
     * Nếu URL là của một private repository, agent sẽ yêu cầu: "Repository này là private. Vui lòng cung cấp Personal Access Token (PAT)...".  
     * PATHandlerModule (trong TEAM Data Acquisition, được điều phối qua Orchestrator) sẽ quản lý việc nhận và sử dụng PAT.  
  6. **Thu thập đủ thông tin:** TaskInitiationModule tạo TaskDefinition (bao gồm cấu hình LLM mặc định hoặc do người dùng chọn cho loại tác vụ này) và gửi cho Orchestrator.  
  7. **Orchestrator điều phối các TEAM** để thực hiện phân tích, truyền tải TaskDefinition (bao gồm cấu hình LLM) cho các TEAM liên quan.  
  8. **TEAM Interaction & Tasking hiển thị kết quả** (thông qua FinalReviewReport từ Orchestrator) và sẵn sàng cho Q\&A.  
* **2.3. Xử lý Yêu cầu "Review PR":**  
  * Luồng tương tự, nhưng DialogManagerAgent sẽ yêu cầu thêm Pull Request ID/URL.  
  * TEAM Data Acquisition sẽ fetch thông tin chi tiết của PR.  
  * TaskDefinition sẽ bao gồm thông tin PR và cấu hình LLM.  
* **2.4. Xử lý các Yêu cầu Không Hỗ trợ hoặc Thiếu Thông tin:**  
  * DialogManagerAgent sẽ phản hồi lịch sự và gợi ý các tính năng được hỗ trợ hoặc yêu cầu thêm thông tin.

**Phần V: Công nghệ Frontend (v1.0)**

Theo quyết định, công nghệ frontend cho RepoChat v1.0 sẽ là **Vue.js**.

1. **Lý do lựa chọn Vue.js:**  
   * **Dễ tiếp cận và học nhanh:** Phù hợp để nhanh chóng xây dựng giao diện chatbot đơn giản, đặc biệt khi trọng tâm dự án là backend.  
   * **Kiến trúc Component:** Rất thích hợp để xây dựng các thành phần UI tái sử dụng của giao diện chatbot (khung chat, bong bóng tin nhắn, ô nhập liệu, danh sách lịch sử hội thoại, khu vực hiển thị sơ đồ, màn hình Settings).  
   * **Hiệu năng tốt và nhẹ nhàng.**  
   * **Hệ sinh thái mạnh mẽ:** Có nhiều thư viện UI hỗ trợ (ví dụ: Vuetify, Element Plus, Quasar) và các giải pháp quản lý trạng thái (Vuex/Pinia) trực quan.  
   * **Tích hợp Diagram:** Dễ dàng tích hợp các thư viện render Mermaid.js (ví dụ: vue-mermaid-string) hoặc hiển thị ảnh PlantUML do backend tạo ra (thông qua mã nguồn sơ đồ trong FinalReviewReport).  
2. **Các tính năng Frontend cần hỗ trợ (v1.0):**  
   * Giao diện chat tương tác đơn giản với sidebar (lịch sử chat, nút "new chat", nút "settings").  
   * Chức năng đăng nhập/đăng ký người dùng.  
   * Quản lý và hiển thị lịch sử chat theo từng người dùng.  
   * **Màn hình Settings:** Cho phép người dùng cấu hình các model LLM cho từng TEAM agent/chức năng theo mô tả ở Phần IV.1.2.  
   * Khả năng hiển thị các đồ thị và sơ đồ (Class Diagram – được render từ mã Mermaid/PlantUML do backend cung cấp trong FinalReviewReport) bên trong giao diện chat.  
3. **Tương tác với Backend:**  
   * Frontend Vue.js sẽ tương tác với backend API của RepoChat (do các TEAM agent cung cấp và Orchestrator điều phối, có thể expose qua HTTP/WebSocket gateway) bằng các request HTTP (sử dụng axios hoặc fetch API).  
   * Xử lý token xác thực (ví dụ: JWT) để bảo mật các request.  
   * Gửi các lựa chọn cấu hình LLM của người dùng về backend để lưu trữ (thông qua API tương ứng của TEAM Interaction & Tasking).  
   * Nhận và hiển thị FinalReviewReport (bao gồm văn bản, mã sơ đồ) từ backend.