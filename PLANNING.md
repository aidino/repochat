# **Kế hoạch Triển khai Dự án RepoChat v1.0**

**Tài liệu Thiết kế Tham chiếu:** repochat\_design\_updated\_v2.md

## **Tổng quan các Giai đoạn**

Dự án RepoChat v1.0 sẽ được triển khai qua các giai đoạn chính sau:

1. **Phase 1: Thiết lập Backend Cốt lõi & Thu thập Dữ liệu Cơ bản**  
2. **Phase 2: Xây dựng Code Knowledge Graph (CKG) Ban đầu**  
3. **Phase 3: Phân tích Code Cơ bản & Tích hợp LLM (Logic Cốt lõi)**  
4. **Phase 4: Tương tác Người dùng Cơ bản & Báo cáo (CLI/Web Đơn giản)**  
5. **Phase 5: Tính năng Nâng cao & Phát triển Frontend (Vue.js)**  
6. **Phase 6: Hoàn thiện, Kiểm thử Chuyên sâu & Chuẩn bị Triển khai**

## **Chi tiết các Giai đoạn**

### **Phase 1: Thiết lập Backend Cốt lõi & Thu thập Dữ liệu Cơ bản**

* **Mục tiêu:**  
  * Thiết lập kiến trúc agent cơ bản với Orchestrator.  
  * TEAM Data Acquisition có khả năng clone repository công khai và xác định ngôn ngữ lập trình chính.  
  * Xây dựng cơ chế xử lý PAT (Personal Access Token) ở mức khái niệm.  
* **Yêu cầu Giai đoạn:**  
  * Orchestrator Agent có thể khởi tạo và quản lý một luồng tác vụ đơn giản.  
  * Giao thức giao tiếp A2A cơ bản giữa Orchestrator và TEAM Data Acquisition được định hình.  
  * Hệ thống có thể clone một repository Git công khai bằng URL.  
  * Hệ thống có thể xác định các ngôn ngữ lập trình chính (Java, Kotlin, Dart, Python) trong repository đã clone.  
* **Tính năng Cần Phát triển:**  
  * **F1.1:** Khởi tạo Orchestrator Agent và thiết lập logging cơ bản.  
  * **F1.2:** TEAM Data Acquisition (GitOperationsModule): Thực hiện clone nông (git clone \--depth 1\) một Git repository công khai từ URL được cung cấp.  
  * **F1.3:** TEAM Data Acquisition (LanguageIdentifierModule): Xác định (các) ngôn ngữ lập trình chính (Java, Kotlin, Dart, Python) dựa trên phần mở rộng của file và các file cấu hình phổ biến.  
  * **F1.4:** TEAM Data Acquisition (DataPreparationModule): Đóng gói đường dẫn đến mã nguồn đã clone và danh sách ngôn ngữ đã xác định vào cấu trúc ProjectDataContext.  
  * **F1.5:** Orchestrator Agent: Có khả năng tiếp nhận một yêu cầu tác vụ cơ bản (ví dụ: URL repository) và kích hoạt TEAM Data Acquisition để xử lý.  
  * **F1.6:** TEAM Data Acquisition (PATHandlerModule): Mô phỏng quy trình yêu cầu PAT từ người dùng (ví dụ: qua CLI input) khi một repository được đánh dấu là "private" (chủ yếu là thiết kế luồng, chưa cần tích hợp API Git thực sự cho private repo ở phase này).  
* **Kịch bản Kiểm thử Thủ công (Manual Test Scenarios):**  
  * **MT1.1:** Cung cấp URL của một repository Git công khai. Xác minh hệ thống clone thành công repository đó vào một thư mục tạm thời.  
  * **MT1.2:** Với một repository đã clone chứa chủ yếu file Java, xác minh TEAM Data Acquisition nhận diện chính xác ngôn ngữ "java".  
  * **MT1.3:** Tương tự MT1.2 cho Python, Kotlin, và Dart.  
  * **MT1.4:** Kiểm tra nội dung của ProjectDataContext được tạo ra, đảm bảo chứa đường dẫn cục bộ chính xác và danh sách ngôn ngữ đúng.  
  * **MT1.5:** (Mô phỏng) Kích hoạt quy trình yêu cầu PAT cho một URL repository "private" giả định. Xác minh hệ thống hiển thị lời nhắc yêu cầu PAT.

### **Phase 2: Xây dựng Code Knowledge Graph (CKG) Ban đầu**

* **Mục tiêu:**  
  * TEAM CKG Operations có khả năng parsing mã nguồn và xây dựng một CKG cơ bản trong Neo4j.  
  * CKG lưu trữ các thực thể code chính và các mối quan hệ cơ bản.  
* **Yêu cầu Giai đoạn:**  
  * TEAM CKG Operations có thể tiếp nhận ProjectDataContext từ Orchestrator.  
  * Các parser cho Java và Python có khả năng tạo ra Abstract Syntax Trees (ASTs) cơ bản.  
  * Định nghĩa schema CKG ban đầu (files, classes, functions/methods, lời gọi hàm/method trực tiếp, kế thừa cơ bản, imports).  
  * Dữ liệu từ ASTs có thể được chuyển đổi và lưu trữ vào Neo4j.  
* **Tính năng Cần Phát triển:**  
  * **F2.1:** TEAM CKG Operations: Thiết lập kết nối đến Neo4j Community Edition.  
  * **F2.2:** TEAM CKG Operations (CodeParserCoordinatorModule): Dựa trên danh sách ngôn ngữ trong ProjectDataContext, lựa chọn và kích hoạt các parser chuyên biệt.  
  * **F2.3:** Phát triển parser cơ bản cho Java để trích xuất: files, classes, methods, và các lời gọi method trực tiếp trong cùng file/class.  
  * **F2.4:** Phát triển parser cơ bản cho Python để trích xuất: files, functions, classes, methods, và các lời gọi function/method trực tiếp trong cùng file.  
  * **F2.5:** (Tính năng mở rộng cho Phase 2 hoặc chuyển sang đầu Phase 3\) Phát triển parser cơ bản cho Kotlin và Dart với các cấu trúc tương tự.  
  * **F2.6:** TEAM CKG Operations (ASTtoCKGBuilderModule): Chuyển đổi thông tin từ ASTs (files, classes, functions/methods) thành các node trong Neo4j theo schema CKG.  
  * **F2.7:** TEAM CKG Operations (ASTtoCKGBuilderModule): Chuyển đổi các mối quan hệ lời gọi trực tiếp thành các relationship "CALLS" trong Neo4j.  
  * **F2.8:** TEAM CKG Operations (CKGQueryInterfaceModule): Triển khai một API truy vấn CKG cơ bản, ví dụ: lấy định nghĩa của một class theo tên.  
  * **F2.9:** Orchestrator Agent: Điều phối luồng tác vụ từ TEAM Data Acquisition sang TEAM CKG Operations.  
* **Kịch bản Kiểm thử Thủ công:**  
  * **MT2.1:** Cung cấp một dự án Java đơn giản. Sau khi xử lý, truy vấn Neo4j (hoặc sử dụng CKGQueryInterfaceModule qua script) để xác minh sự tồn tại của các node đại diện cho files, classes, và methods.  
  * **MT2.2:** Trong dự án Java, nếu MethodA gọi MethodB (trong cùng class hoặc file), xác minh có một relationship "CALLS" tương ứng trong CKG.  
  * **MT2.3:** Tương tự MT2.1 cho một dự án Python đơn giản.  
  * **MT2.4:** Tương tự MT2.2 cho dự án Python (function\_x gọi function\_y).  
  * **MT2.5:** Sử dụng CKGQueryInterfaceModule (ví dụ, qua một script kiểm thử) để truy vấn thông tin của một class đã biết trong dự án thử nghiệm. Xác minh thông tin trả về là chính xác.  
  * **MT2.6:** Xác minh Orchestrator chuyển thành công ProjectDataContext từ TDA sang TCKG và TCKG báo cáo trạng thái xây dựng (thành công/lỗi cơ bản).

### **Phase 3: Phân tích Code Cơ bản & Tích hợp LLM (Logic Cốt lõi)**

* **Mục tiêu:**  
  * TEAM Code Analysis thực hiện các phân tích kiến trúc cơ bản dựa trên CKG.  
  * Tích hợp TEAM LLM Services với API OpenAI cho các tác vụ LLM đơn giản.  
  * Thực hiện phân tích PR cơ bản để xác định tác động trực tiếp.  
* **Yêu cầu Giai đoạn:**  
  * TEAM Code Analysis có thể truy vấn CKG hiệu quả thông qua CKGQueryInterfaceModule.  
  * Logic phát hiện circular dependencies và public elements không sử dụng được triển khai.  
  * TEAM LLM Services có thể gửi prompt đến API OpenAI và nhận phản hồi.  
  * Lớp trừu tượng LLMProviderAbstractionLayer cho OpenAI được hoàn thiện.  
  * Orchestrator có thể định tuyến yêu cầu dịch vụ LLM.  
* **Tính năng Cần Phát triển:**  
  * **F3.1:** TEAM Code Analysis (ArchitecturalAnalyzerModule): Phát hiện circular dependencies giữa các file/module bằng cách truy vấn CKG.  
  * **F3.2:** TEAM Code Analysis (ArchitecturalAnalyzerModule): Xác định các public methods/classes có khả năng không được sử dụng trong phạm vi codebase đã phân tích (kèm cảnh báo rõ ràng về hạn chế).  
  * **F3.3:** TEAM LLM Services (LLMProviderAbstractionLayer): Hoàn thiện OpenAI provider, bao gồm xử lý API key an toàn và các tham số gọi API cơ bản.  
  * **F3.4:** TEAM LLM Services (LLMGatewayModule, PromptFormatterModule): Xây dựng prompt template cơ bản cho tác vụ "Giải thích đoạn code này".  
  * **F3.5:** TEAM Code Analysis (LLMAnalysisSupportModule): Chuẩn bị ngữ cảnh (đoạn code) và tạo LLMServiceRequest (với cấu hình LLM mặc định/hardcoded ở phase này) cho tác vụ "Giải thích đoạn code này".  
  * **F3.6:** Orchestrator Agent: Định tuyến LLMServiceRequest từ TEAM Code Analysis đến TEAM LLM Services và chuyển LLMServiceResponse trở lại TEAM Code Analysis.  
  * **F3.7:** TEAM Code Analysis: Phân tích PR cơ bản:  
    * Xác định các file đã thay đổi từ diff của PR (lấy từ ProjectDataContext).  
    * Với mỗi function/method đã thay đổi, sử dụng CKG để liệt kê các function/method gọi trực tiếp đến nó và các function/method mà nó gọi trực tiếp.  
  * **F3.8:** StaticAnalysisIntegratorModule: Tạo placeholder, chưa cần tích hợp linter thực sự.  
* **Kịch bản Kiểm thử Thủ công:**  
  * **MT3.1:** Tạo một dự án thử nghiệm có chứa circular dependency rõ ràng giữa hai file/module. Chạy phân tích. Xác minh hệ thống báo cáo đúng circular dependency đó.  
  * **MT3.2:** Trong một dự án thử nghiệm, thêm một public method không được gọi từ bất kỳ đâu trong dự án. Chạy phân tích. Xác minh method đó được gợi ý là có khả năng không sử dụng (kèm cảnh báo phù hợp).  
  * **MT3.3:** Cung cấp thủ công một đoạn code cho LLMAnalysisSupportModule. Xác minh module này tạo LLMServiceRequest, TEAM LLM Services gọi API OpenAI, và TEAM Code Analysis nhận được phản hồi dạng văn bản giải thích đoạn code (có thể kiểm tra qua log output).  
  * **MT3.4:** Mô phỏng một PR diff (danh sách file và function/method thay đổi) trong ProjectDataContext. Chạy phân tích PR. Xác minh TEAM Code Analysis sử dụng CKG để liệt kê chính xác các tác động trực tiếp (callers/callees) của các function/method đã thay đổi.  
  * **MT3.5:** Xác minh các đối tượng AnalysisFinding được tạo ra cho các vấn đề phát hiện được (circular dependency, code không sử dụng).

### **Phase 4: Tương tác Người dùng Cơ bản & Báo cáo (CLI/Web Đơn giản)**

* **Mục tiêu:**  
  * TEAM Interaction & Tasking có khả năng nhận yêu cầu từ người dùng (qua CLI hoặc giao diện web rất đơn giản).  
  * TEAM Synthesis & Reporting tổng hợp các phát hiện và kết quả LLM cơ bản thành báo cáo dạng text.  
  * Hoàn thiện luồng end-to-end cho các tác vụ "scan project" và "review PR" ở mức cơ bản.  
* **Yêu cầu Giai đoạn:**  
  * Giao diện dòng lệnh (CLI) cho phép người dùng nhập URL repository, PR ID.  
  * Hệ thống có thể tạo báo cáo dạng text tóm tắt các kết quả phân tích.  
  * Luồng Q\&A cơ bản ("Định nghĩa class X ở đâu?") hoạt động.  
* **Tính năng Cần Phát triển:**  
  * **F4.1:** TEAM Interaction & Tasking (UserIntentParserAgent, DialogManagerAgent): Xây dựng CLI cơ bản để nhận URL repository cho tác vụ "scan project".  
  * **F4.2:** TEAM Interaction & Tasking (UserIntentParserAgent, DialogManagerAgent): Mở rộng CLI để nhận URL repository và PR ID cho tác vụ "review PR".  
  * **F4.3:** TEAM Interaction & Tasking (TaskInitiationModule): Tạo TaskDefinition từ input của CLI (vẫn sử dụng cấu hình LLM mặc định/hardcoded cho TaskDefinition ở phase này).  
  * **F4.4:** TEAM Synthesis & Reporting (FindingAggregatorModule): Thu thập các đối tượng AnalysisFinding từ TEAM Code Analysis.  
  * **F4.5:** TEAM Synthesis & Reporting (ReportGeneratorModule): Tạo báo cáo dạng text đơn giản, tóm tắt các phát hiện (ví dụ: danh sách circular dependencies, code không sử dụng).  
  * **F4.6:** TEAM Synthesis & Reporting (ReportGeneratorModule): Tích hợp tóm tắt tác động PR cơ bản (từ F3.7) vào báo cáo.  
  * **F4.7:** TEAM Synthesis & Reporting (OutputFormatterModule): Tạo đối tượng FinalReviewReport (dạng text).  
  * **F4.8:** TEAM Interaction & Tasking (PresentationModule): Hiển thị FinalReviewReport dạng text trên CLI.  
  * **F4.9 (Q\&A):** TEAM Interaction & Tasking: Cho phép người dùng hỏi "Định nghĩa của class X ở đâu?" (qua CLI). TEAM Code Analysis truy vấn CKG, và TEAM Synthesis & Reporting định dạng câu trả lời để hiển thị trên CLI.  
* **Kịch bản Kiểm thử Thủ công:**  
  * **MT4.1 (Scan Project qua CLI):**  
    * Chạy RepoChat từ CLI.  
    * Nhập lệnh để scan một project và cung cấp URL repository công khai.  
    * Xác minh hệ thống thực hiện clone, xây dựng CKG, phân tích circular dependencies/code không sử dụng.  
    * Xác minh một báo cáo dạng text tóm tắt các phát hiện này được hiển thị trên CLI.  
  * **MT4.2 (Review PR qua CLI):**  
    * Chạy RepoChat từ CLI.  
    * Nhập lệnh để review một PR, cung cấp URL repository và một PR ID (có thể mô phỏng diff).  
    * Xác minh hệ thống thực hiện clone, xây dựng CKG, thực hiện phân tích tác động PR cơ bản.  
    * Xác minh một báo cáo dạng text bao gồm tóm tắt tác động này được hiển thị trên CLI.  
  * **MT4.3 (Q\&A qua CLI):**  
    * Sau khi scan một project, hỏi "Định nghĩa của class \[TênClassĐãBiết\] ở đâu?" qua CLI.  
    * Xác minh hệ thống truy vấn CKG và hiển thị đường dẫn file chứa định nghĩa class đó.  
  * **MT4.4:** Kiểm thử với URL repository yêu cầu PAT (mô phỏng). Xác minh quy trình yêu cầu PAT được kích hoạt qua CLI và tiến trình tiếp tục sau khi cung cấp PAT giả.

### **Phase 5: Tính năng Nâng cao & Phát triển Frontend (Vue.js)**

* **Mục tiêu:**  
  * Phát triển giao diện người dùng Vue.js cho các tương tác chính.  
  * Triển khai tính năng cấu hình LLM cho người dùng.  
  * Bổ sung tính năng sinh sơ đồ lớp và phân tích liên quan đến test.  
  * Nâng cao chi tiết báo cáo PR.  
* **Yêu cầu Giai đoạn:**  
  * Giao diện chat Vue.js hoạt động, có lịch sử chat và màn hình cài đặt.  
  * Người dùng có thể cấu hình model LLM cho các chức năng khác nhau.  
  * Hệ thống có thể sinh mã Mermaid/PlantUML cho sơ đồ lớp.  
  * Báo cáo PR bao gồm metadata và các nhận xét về test.  
* **Tính năng Cần Phát triển:**  
  * **F5.1 (Frontend):** Xây dựng ứng dụng Vue.js với giao diện chat cơ bản (khung nhập liệu, khu vực hiển thị tin nhắn).  
  * **F5.2 (Frontend):** Thanh bên (sidebar) với các nút "New Chat", "Settings" và khu vực hiển thị lịch sử chat (ban đầu có thể là dữ liệu giả).  
  * **F5.3 (Frontend):** Màn hình Settings UI cho phép người dùng lựa chọn model LLM cho các chức năng/TEAM khác nhau (ví dụ: NLU, Phân tích Code, Sinh Báo cáo).  
  * **F5.4 (Backend):** TEAM Interaction & Tasking (ConfigurationManagementAgent): Lưu trữ và truy xuất các lựa chọn cấu hình LLM của người dùng (ví dụ: vào database hoặc file cấu hình người dùng).  
  * **F5.5 (Tích hợp):** TaskInitiationModule sử dụng các cấu hình LLM đã lưu của người dùng khi tạo TaskDefinition. LLMServiceRequest được tạo bởi TCA và TSR sẽ bao gồm các thông tin cấu hình này.  
  * **F5.6:** TEAM Synthesis & Reporting (DiagramGeneratorModule): Sinh mã PlantUML hoặc Mermaid.js cho sơ đồ lớp của một class cụ thể, dựa trên dữ liệu từ CKG.  
  * **F5.7 (Frontend):** Hiển thị các sơ đồ PlantUML/Mermaid.js (render từ mã do backend cung cấp) trong giao diện chat.  
  * **F5.8:** TEAM Code Analysis (TestCoModificationCheckerModule): Triển khai các heuristic cơ bản để kiểm tra xem việc thay đổi code trong PR có đi kèm với thay đổi tương ứng trong code test hay không (dựa trên liên kết code-test trong CKG và diff của PR).  
  * **F5.9:** TEAM Synthesis & Reporting: Tích hợp các quan sát từ TestCoModificationCheckerModule vào FinalReviewReport.  
  * **F5.10:** TEAM Data Acquisition (PRMetadataExtractorAgent): Trích xuất title, description của PR và cố gắng tìm các liên kết đến hệ thống quản lý issue từ description.  
  * **F5.11:** TEAM Synthesis & Reporting: Tích hợp metadata của PR (title, description, issue links) vào FinalReviewReport.  
  * **F5.12 (Tính năng LLM):** TEAM Code Analysis (sử dụng LLMAnalysisSupportModule) và TEAM LLM Services: Phân tích sự thay đổi code so với mô tả của PR (sử dụng LLM) để đưa ra nhận xét cấp cao về sự phù hợp.  
  * **F5.13 (Frontend):** Triển khai luồng xác thực người dùng cơ bản (ví dụ: username/password, hoặc mock authentication cho mục đích phát triển).  
* **Kịch bản Kiểm thử Thủ công:**  
  * **MT5.1:** Mở giao diện web RepoChat. Gửi yêu cầu "scan project" với URL repository. Xác minh luồng xử lý hoàn tất và kết quả (bao gồm sơ đồ nếu được yêu cầu sau đó) được hiển thị trong giao diện chat.  
  * **MT5.2:** Truy cập màn hình Settings. Thay đổi model LLM cho chức năng "Phân tích Code". Bắt đầu một phiên scan mới. Xác minh (qua log hoặc output cụ thể) rằng lựa chọn model LLM mới được sử dụng cho các tác vụ phân tích.  
  * **MT5.3:** Sau khi scan một project, yêu cầu sinh sơ đồ lớp cho một class cụ thể. Xác minh sơ đồ PlantUML/Mermaid.js được render chính xác trong UI.  
  * **MT5.4 (Review PR Nâng cao):**  
    * Review một PR có thay đổi một function.  
    * Xác minh metadata của PR (title, description) được hiển thị trong báo cáo.  
    * Nếu có file test tương ứng nhưng không được sửa đổi, xác minh TestCoModificationCheckerModule đưa ra nhận xét về điều này.  
    * Xác minh có nhận xét (do LLM tạo) về sự phù hợp giữa code thay đổi và mô tả PR.  
  * **MT5.5:** Kiểm thử chức năng Q\&A thông qua giao diện web.  
  * **MT5.6:** Kiểm thử lịch sử chat (chức năng cơ bản: "New Chat" tạo một session mới, các session cũ được liệt kê và có thể xem lại).

### **Phase 6: Hoàn thiện, Kiểm thử Chuyên sâu & Chuẩn bị Triển khai**

* **Mục tiêu:**  
  * Tất cả các tính năng của v1.0 đã được triển khai và hoạt động ổn định.  
  * Thực hiện kiểm thử thủ công toàn diện.  
  * Xem xét các yếu tố hiệu năng cơ bản.  
  * Hoàn thiện tài liệu hướng dẫn.  
* **Yêu cầu Giai đoạn:**  
  * Hệ thống ổn định, ít lỗi.  
  * Tài liệu người dùng đầy đủ.  
  * Sẵn sàng cho việc đóng gói và triển khai thử nghiệm.  
* **Tính năng Cần Phát triển (Chủ yếu là hoàn thiện và kiểm thử):**  
  * **F6.1:** Kiểm thử end-to-end toàn diện tất cả các tính năng của v1.0 trên các ngôn ngữ được hỗ trợ.  
  * **F6.2:** Sửa lỗi và cải thiện độ ổn định dựa trên kết quả kiểm thử.  
  * **F6.3:** Cải thiện xử lý lỗi và phản hồi cho người dùng trên UI (thông báo lỗi rõ ràng, thân thiện).  
  * **F6.4:** Rà soát và tối ưu hóa các prompt sử dụng cho dịch vụ LLM để cải thiện chất lượng phản hồi.  
  * **F6.5:** Tạo tài liệu hướng dẫn người dùng (cách cài đặt, cách sử dụng các tính năng).  
  * **F6.6:** Chuẩn bị các script hoặc hướng dẫn triển khai cơ bản (ví dụ: Dockerfile nếu có).  
  * **F6.7:** Đảm bảo PAT được xử lý an toàn (không bị log, được xóa khỏi bộ nhớ ngay sau khi sử dụng).  
* **Kịch bản Kiểm thử Thủ công:**  
  * **MT6.1:** Thực thi lại tất cả các kịch bản kiểm thử từ các phase trước trên hệ thống đã tích hợp hoàn chỉnh.  
  * **MT6.2:** Kiểm thử với các dự án mã nguồn mở lớn hơn, phức tạp hơn (nhưng vẫn trong phạm vi xử lý của v1.0) cho từng ngôn ngữ được hỗ trợ.  
  * **MT6.3:** Kiểm thử các trường hợp lỗi: URL repository không hợp lệ, PR ID không hợp lệ, lỗi API của LLM (có thể mô phỏng nếu cần), lỗi trong quá trình xây dựng CKG. Xác minh hệ thống hiển thị thông báo lỗi một cách duyên dáng.  
  * **MT6.4:** Kiểm thử truy cập đồng thời của người dùng (nếu áp dụng cho mô hình triển khai, có thể mô phỏng bằng nhiều tab trình duyệt cho v1.0).  
  * **MT6.5:** Đánh giá tất cả các tương tác trên UI về tính rõ ràng và dễ sử dụng.  
  * **MT6.6:** Thực hiện theo hướng dẫn triển khai để cài đặt một instance mới của ứng dụng.