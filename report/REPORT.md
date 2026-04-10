# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Quách Gia Được  
**MSSV:** 2A202600423  
**Nhóm:** E3-C401  
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**  
Theo cách em hiểu, high cosine similarity nghĩa là hai đoạn text có vector gần cùng hướng, nên nội dung ngữ nghĩa khá giống nhau. Điểm càng gần 1 thì mức tương đồng càng cao.

**Ví dụ HIGH similarity:**
- Sentence A: "Talk about their life instead of your idea."
- Sentence B: "Ask about specifics in the past instead of generics or opinions about the future."
- Tại sao tương đồng: Cả hai cùng nói về nguyên tắc hỏi đúng trong The Mom Test, chỉ khác cách diễn đạt.

**Ví dụ LOW similarity:**
- Sentence A: "Commitment can be cash, but does not have to be."
- Sentence B: "A product designer sold many 3D-printed tripod prototypes."
- Tại sao khác: Hai câu thuộc hai ngữ cảnh hoàn toàn khác nhau, gần như không có giao nhau về ý nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Với embedding, độ lớn vector có thể bị ảnh hưởng bởi nhiều yếu tố kỹ thuật, nên so sánh hướng vector sẽ ổn định và hợp lý hơn khi đánh giá nghĩa. Vì vậy cosine similarity thường phản ánh semantic relevance tốt hơn Euclidean distance.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

**Trình bày phép tính:**  
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))  
= ceil((10000 - 50) / (500 - 50))  
= ceil(9950 / 450)  
= ceil(22.11)

**Đáp án:** 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**  
Khi overlap tăng, bước nhảy giảm nên số chunk tăng. Đổi lại, overlap giúp giữ ngữ cảnh liên tục giữa các chunk, đặc biệt hữu ích khi ý chính nằm sát ranh giới chunk.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Customer discovery / startup interview với sách The Mom Test

**Tại sao nhóm chọn domain này?**  
Nhóm em chọn The Mom Test vì nội dung tập trung vào các nguyên tắc interview khách hàng rất rõ ràng (compliments, fluff, commitment, advancement). Tài liệu có tính thực tiễn cao, dễ tạo benchmark query và dễ đánh giá đúng/sai theo ngữ cảnh cụ thể.

Ngoài ra, dù chỉ dùng một nguồn chính, file sách đủ dài và có cấu trúc chương/phần rõ, nên vẫn phù hợp để thử nhiều strategy chunking khác nhau.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | the_mom_test_part1_foundations.md | Tách từ The Mom Test.md | 28517 | chapter, source, language, domain, content_type |
| 2 | the_mom_test_part2_bad_data.md | Tách từ The Mom Test.md | 29944 | chapter, source, language, domain, content_type |
| 3 | the_mom_test_part3_advancement.md | Tách từ The Mom Test.md | 49201 | chapter, source, language, domain, content_type |
| 4 | the_mom_test_part4_process.md | Tách từ The Mom Test.md | 49294 | chapter, source, language, domain, content_type |
| 5 | the_mom_test_part5_recap.md | Tách từ The Mom Test.md | 23062 | chapter, source, language, domain, content_type |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| chapter | string | the_mom_test_part3_advancement | Lọc theo phạm vi chương |
| content_type | string | rule, compliment, fluff, pitching, advancement | Lọc theo intent của câu hỏi |
| source | string | data/the_mom_test_part2_bad_data.md | Truy vết nguồn chunk |
| language | string | en | Đồng bộ ngôn ngữ dữ liệu |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| the_mom_test_part1_foundations.md | FixedSizeChunker (`fixed_size`) | 27 | 1171.74 | Trung bình, đôi lúc cắt giữa ý |
| the_mom_test_part1_foundations.md | SentenceChunker (`by_sentences`) | 114 | 248.24 | Thấp, dễ vỡ ngữ cảnh dài |
| the_mom_test_part1_foundations.md | RecursiveChunker (`recursive`) | 30 | 948.67 | Tốt, giữ đoạn mạch lạc |
| the_mom_test_part2_bad_data.md | FixedSizeChunker (`fixed_size`) | 28 | 1185.14 | Trung bình |
| the_mom_test_part2_bad_data.md | SentenceChunker (`by_sentences`) | 112 | 265.54 | Thấp |
| the_mom_test_part2_bad_data.md | RecursiveChunker (`recursive`) | 29 | 1030.59 | Tốt |
| the_mom_test_part3_advancement.md | FixedSizeChunker (`fixed_size`) | 46 | 1186.98 | Trung bình |
| the_mom_test_part3_advancement.md | SentenceChunker (`by_sentences`) | 174 | 280.89 | Thấp |
| the_mom_test_part3_advancement.md | RecursiveChunker (`recursive`) | 51 | 962.78 | Tốt |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**  
Em triển khai strategy theo hướng structural: ưu tiên tách theo các separator tự nhiên (đoạn, dòng, câu) trước khi fallback về cắt cứng. Cách này giúp chunk giữ trọn ý hơn so với fixed-size thuần, đặc biệt khi tài liệu có heading và đoạn diễn giải dài. Em dùng `chunk_size=1200` để giảm vỡ ngữ cảnh ở các phần định nghĩa và nguyên tắc.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Domain The Mom Test có pattern nội dung dạng chương/phần, trong đó mỗi ý chính thường trải dài nhiều câu liên tiếp. RecursiveChunker khai thác tốt pattern này vì giữ được coherence theo đoạn, giúp agent trả lời các câu hỏi khái niệm mạch lạc hơn.

**Code snippet (nếu custom):**
```python
from src import RecursiveChunker

chunker = RecursiveChunker(chunk_size=1200)
chunks = chunker.chunk(text)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| The Mom Test (5 files) | best baseline (FixedSize medium) | 46 (trên part3) | 1186.98 | Trung bình |
| The Mom Test (5 files) | của tôi (RecursiveChunker) | 182 (toàn bộ corpus) | 987.16 | 4/5 query có relevant chunk trong top-3 |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Kim Trí Thành | FixedSizeChunker (300, 10%) | 8/10 (4/5 relevant) | Ổn định, làm đối chứng tốt | Có thể cắt giữa rule |
| Phạm Quốc Dũng | SentenceChunker (granular, 1 câu/chunk) | 8/10 | Match tốt các câu ngắn chứa tín hiệu rõ | Context mỏng khi cần tổng hợp nhiều câu |
| Quách Gia Được | RecursiveChunker (structural, chunk ~1200) | 8/10 (quy đổi từ 4/5 relevant) | Chunk mạch lạc, giữ ý theo đoạn/chương | Score tuyệt đối chưa cao nếu ép threshold 0.7 |
| Đặng Đinh Tú Anh | FixedSizeChunker (1000, overlap=0) | 7/10 | Mỗi chunk chứa nhiều context, thuận lợi cho câu hỏi tổng quát | Chunk quá lớn làm nhiễu chủ đề, query mơ hồ dễ trượt |
| Thành Nam | RecursiveChunker + Metadata Filter (member5 run) | 2/10 (quy đổi từ 1/5 relevant) | Có cơ chế lọc theo content_type trước khi search | Metadata chưa đủ chính xác nên filter chưa cải thiện kết quả |

**Strategy nào tốt nhất cho domain này? Tại sao?**  
Theo dữ liệu hiện có của nhóm, hai strategy cho kết quả ổn định nhất là baseline FixedSize 300+10% của anh Trí Thành và RecursiveChunker của em (đều đạt 4/5 relevant ở bộ query nhóm, tương ứng 8/10). Strategy sentence-level của bạn Dũng cũng cho kết quả tốt với câu hỏi cần bằng chứng ngắn. Với member5 metadata-filter, kết quả hiện tại mới 1/5 relevant (2/10) nên chưa thể kết luận filter mạnh hơn; nhóm cần tinh chỉnh lại metadata schema trước khi đánh giá tiếp.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**SentenceChunker.chunk — approach:**  
Em dùng regex tách theo ranh giới câu (`(?<=[.!?])(?:\s+|\n+)`) để giữ dấu câu và giảm gãy nghĩa. Sau đó gom theo `max_sentences_per_chunk` và loại bỏ phần tử rỗng/whitespace. Edge cases như text rỗng hoặc chỉ có khoảng trắng đều trả về danh sách rỗng.

**RecursiveChunker.chunk / _split — approach:**  
Algorithm thử tách theo thứ tự separator ưu tiên; nếu đoạn còn dài hơn `chunk_size` thì đệ quy với separator nhỏ hơn. Base case là đoạn đã <= `chunk_size` hoặc hết separator, khi đó fallback sang FixedSize không overlap. Cách này tối đa hóa giữ cấu trúc tự nhiên trước khi cắt cứng.

### EmbeddingStore

**add_documents + search — approach:**  
Em chuẩn hóa mỗi document thành record gồm id, content, metadata, embedding và lưu vào in-memory store (đồng thời thử sync Chroma nếu khả dụng). Khi search, em embed query, tính score bằng dot product với từng record, rồi sort giảm dần và lấy top-k.

**search_with_filter + delete_document — approach:**  
`search_with_filter` filter theo metadata trước rồi mới chạy similarity search trên tập đã lọc để tránh nhiễu. `delete_document` xóa toàn bộ record theo `doc_id`, trả True/False theo kết quả xóa, và sync delete sang Chroma nếu backend đang bật.

### KnowledgeBaseAgent

**answer — approach:**  
Agent retrieve top-k chunks, đánh số context blocks và inject vào prompt theo format use-only-context. Prompt có nhánh fallback nếu không có context để tránh hallucination. Sau cùng gọi `llm_fn` và trả về chuỗi answer.

### Test Results

```text
pytest tests/ -v
...
============================= 42 passed in 0.03s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Talk about their life instead of your idea. | Ask about specifics in the past instead of generics or opinions about the future. | high | 0.4904 | Đúng |
| 2 | Compliments are the fool's gold of customer learning. | Opinions are worthless. | high | 0.3259 | Đúng một phần |
| 3 | If you slip into pitch mode, just apologise. | Can we jump back to what you were just saying? | high | 0.2869 | Sai |
| 4 | A meeting has succeeded when it ends with a commitment to advance to the next step. | If you do not know what happens next after a meeting, the meeting was pointless. | high | 0.4960 | Đúng |
| 5 | Talk less and listen more. | You cannot learn anything useful unless you spend a few minutes shutting up. | high | 0.4746 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**  
Cặp #3 thấp hơn kỳ vọng dù cùng chủ đề pitching-recovery. Điều này cho thấy embedding vẫn nhạy với cách diễn đạt cụ thể, nên similarity score là tín hiệu quan trọng nhưng không thay thế hoàn toàn việc đọc ngữ cảnh theo đoạn.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. 5 queries trùng với các thành viên cùng nhóm.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Quy tắc cốt lõi của The Mom Test để tránh nhận lời nói dối là gì? | Nói về cuộc đời họ, hỏi sự kiện quá khứ cụ thể, nói ít và lắng nghe nhiều |
| 2 | Tại sao compliments là “vàng giả”? | Vì là lời khen xã giao, không phải dữ liệu hành vi đáng tin |
| 3 | Neo giữ thông tin mơ hồ bằng cách nào? | Hỏi ví dụ cụ thể trong quá khứ, không chấp nhận câu chung chung |
| 4 | Dấu hiệu cuộc gặp thành công (Advancement)? | Có commitment: bước tiếp theo, giới thiệu, thời gian, tiền |
| 5 | Nên làm gì khi lỡ pitch quá sớm? | Dừng lại, xin lỗi, quay về khai thác vấn đề của khách hàng |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|----------------------------------|-------|-----------|--------------------------|
| 1 | Core rule tránh lời nói dối | Trúng đoạn định nghĩa The Mom Test rules | 0.4484 | Có | Trả lời đúng ý chính |
| 2 | Compliments là vàng giả | Trúng chương nói về compliments/fibs | 0.4059 | Có | Trả lời đúng nguyên nhân |
| 3 | Neo giữ fluff | Top-3 chưa trúng rõ phần last-time/specific | 0.3574 | Không | Trả lời còn chung chung |
| 4 | Dấu hiệu advancement | Trúng đoạn commitment/advancement | 0.4644 | Có | Trả lời đúng tiêu chí |
| 5 | Lỡ pitch quá sớm xử lý sao | Trúng đoạn khuyên dừng pitch và xin lỗi | 0.3855 | Có | Trả lời đúng hướng |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 4 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Từ anh Hoàng Kim Trí Thành, em học được cách dùng baseline đối chứng rõ ràng trước khi kết luận strategy nào tốt hơn. Từ bạn Phạm Quốc Dũng và Tú Anh, em thấy rõ trade-off giữa chunk nhỏ và chunk lớn theo từng loại query. Từ Thành Nam, em rút ra rằng metadata-filter chỉ mạnh khi schema metadata được gán chính xác và nhất quán.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**  
Điểm em học được là không nên dùng cứng một ngưỡng score cho mọi query, mà cần nhìn cả mức độ relevant thực tế trong top-3. Cách nhìn này hợp lý với kết quả nhóm em vì có query score chưa cao nhưng chunk vẫn đúng ý.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Em sẽ chuẩn hóa metadata ở cấp chunk ngay từ đầu theo schema chung của nhóm (chapter, content_type, source, language) và kiểm tra chất lượng metadata trước benchmark. Ngoài ra em sẽ chuẩn hóa cặp query VI/EN tương đương để giảm mismatch ngôn ngữ khi dữ liệu gốc là tiếng Anh.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 8 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **83 / 100** |