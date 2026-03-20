[guidance.txt](https://github.com/user-attachments/files/26134791/guidance.txt)
本地离线RAG系统完整搭建说明（适用于Windows + Conda + 零基础用户）

一、系统目标
本项目实现以下完整离线流程：
PDF文献 → 自动转文本 → 智能分片 → 去噪过滤 → 建立索引 → 中文提问 → 本地模型翻译检索词 → 检索相关内容 → 读取可编辑Prompt模板 → 本地模型生成回答

适用场景：
1. 低空经济与城市规划文献分析
2. 屋顶起降点适宜性研究
3. 比赛辅助与论文阅读
4. 本地知识库问答

二、环境要求
必须具备：
1. Windows 系统
2. 已安装 Conda
3. 已安装 Jupyter Notebook（用于编辑和测试，不建议跑长任务）
4. 已安装 Ollama（用于本地大模型）
5. 已下载本地模型：qwen2:7b

建议说明：
1. Jupyter 主要用于编辑代码、查看文件、小范围测试
2. 长时间任务（分片、建索引、主程序运行）建议在 Anaconda Prompt 中执行
3. 不依赖 OpenAI API，可完全离线运行

三、核心环境配置
1. 创建环境
conda create -p D:\conda_envs\rag_env python=3.11 -y

2. 激活环境
conda activate D:\conda_envs\rag_env

3. 安装核心依赖（建议在 Jupyter 或当前环境中执行）
pip install sentence-transformers chromadb python-dotenv pymupdf scikit-learn requests jupyter ipykernel

4. 安装本地模型工具
先安装 Ollama（Windows 版），再执行：
ollama pull qwen2:7b

5. 测试本地模型
ollama run qwen2:7b
输入：
请只回复：本地模型正常

四、项目结构（推荐保持固定）
local-rag-project/
├── pdfs/                  # 放原始PDF文献
├── texts/                 # PDF自动提取出的文本
├── output/                # 分片结果、临时结果
├── index/                 # 检索索引文件
├── app/
│   ├── pdf_to_text.py     # PDF转文本
│   ├── split_text.py      # 文本清洗+句子级分片
│   ├── search_chunks.py   # 过滤噪声+建立索引
│   ├── rag_app.py         # 单次问答主程序
│   └── auto_rag_app.py    # 总控程序（自动化入口）
├── prompt_template.txt    # 可直接编辑的Prompt模板
└── main.ipynb             # Notebook（仅用于编辑/小测试）

五、各文件作用说明
1. pdf_to_text.py
作用：将 pdfs 文件夹中的 PDF 批量转换为 texts 文件夹中的 txt 文本

2. split_text.py
作用：
- 先清洗文本中的元数据噪声
- 再按句子切分
- 控制每段最大长度
- 保留上下文重叠
目标：避免句子被截断，提高检索质量

3. search_chunks.py
作用：
- 读取分片文件
- 过滤参考文献类噪声片段
- 使用 TF-IDF 建立本地检索索引
- 保存 vectorizer、vectors、chunks 到 index 文件夹

4. rag_app.py
作用：
- 读取索引
- 使用本地模型把中文问题翻译为英文检索关键词
- 执行相似度检索
- 读取 prompt_template.txt
- 组合 Prompt
- 调用本地 Ollama 模型生成答案

5. auto_rag_app.py
作用：
- 自动串联整个流程
- 可选择是否重建知识库
- 自动执行：PDF转文本 → 分片 → 建索引 → 问答

6. prompt_template.txt
作用：
- 放置可编辑提示词模板
- 用户只需改文本，不用改代码
- 可用于控制回答风格、结构、约束条件

六、推荐使用方式（最简单）
方法一：使用自动总入口（推荐）
在 Anaconda Prompt 中运行：

conda activate D:\conda_envs\rag_env
cd %USERPROFILE%\Desktop\local-rag-project
python app\auto_rag_app.py

然后按提示输入：
1. 是否重新处理 PDF、分片并重建索引（y/n）
2. 你的问题
3. 检索条数 top_k（建议 3-5）
4. 最小相似度 min_score（建议 0 或 0.01）

方法二：分步运行（适合调试）
1. PDF转文本
python app\pdf_to_text.py

2. 文本分片
python app\split_text.py

3. 建立索引
python app\search_chunks.py

4. 运行问答
python app\rag_app.py

七、完整自动化流程说明
自动化总流程如下：
1. 把 PDF 放入 pdfs 文件夹
2. 程序自动提取文本到 texts
3. 程序清洗元数据噪声
4. 程序按句子进行分片并保留重叠
5. 程序过滤掉参考文献、DOI、Received、Citation 等噪声片段
6. 程序建立 TF-IDF 检索索引
7. 用户输入中文问题
8. 本地模型将中文问题翻译成适合英文论文检索的关键词
9. 检索系统按相似度排序，选出 top_k 条结果
10. 程序读取 prompt_template.txt
11. 本地模型结合检索结果生成最终回答

八、关键优化点
1. 分片优化
当前采用：
- 句子级切分
- 控制 chunk 最大长度
- 保留 overlap（上下文重叠）
优点：
- 语义更完整
- 检索结果更像正文
- 减少句子被截断的问题

2. 去噪优化
系统会尽量过滤以下内容：
- Received
- Revised
- Accepted
- Published online
- DOI
- URL
- Foundation items
- Corresponding author
- E-mail
- Citation
- Copyright
- 纯编号/纯日期/过短片段

3. 检索优化
当前检索支持：
- top_k：控制返回条数
- min_score：设置最低相似度
- 按相似度分数排序
- 显示检索关键词与相似度分数

4. 中文问题优化
由于文献内容多为英文，直接用中文检索常出现相似度为 0
当前做法：
- 先用本地模型将中文问题翻译为英文检索关键词
- 再做 TF-IDF 检索
这样能显著提高匹配效果

5. Prompt 可编辑
Prompt 不写死在代码里，而是存放在：
prompt_template.txt
优点：
- 不懂代码的人也能修改
- 可以自定义回答风格
- 可以要求模型按固定结构输出

九、当前系统能力
当前已经实现：
1. 完全离线运行
2. PDF自动处理
3. 句子级分片
4. 去除参考文献类干扰
5. 中文提问
6. 本地模型辅助检索
7. 可控检索条数与相似度阈值
8. Prompt模板外置
9. 自动生成最终答案
10. 自动化总控程序

十、当前限制
1. 当前索引方式主要是 TF-IDF
优点：稳定、离线、简单
缺点：语义理解能力弱于高质量 embedding 模型

2. 如果文献格式特别杂乱，PDF提取后的文本质量可能不稳定
此时需要后续优化 pdf_to_text.py 或增加专门清洗规则

3. 本地模型生成质量取决于机器性能和所用模型能力
qwen2:7b 已可用，但仍可后续升级为更强模型

十一、常见问题与解决方式
1. 问题：相似度全是 0
原因：
- 使用中文直接检索英文文献
解决：
- 已加入“本地模型翻译检索关键词”机制

2. 问题：Jupyter 很慢、没有返回结果
原因：
- Jupyter 不适合长任务和大量输出
解决：
- 长任务改到 Anaconda Prompt 运行
- Jupyter 只做编辑和查看
- 重启 kernel，清空输出

3. 问题：Task was destroyed but it is pending!
原因：
- Jupyter 中的 input() 与子进程/模型调用冲突
解决：
- 使用脚本在终端中运行，不在 Notebook 中做交互式主程序

4. 问题：OpenAI API 连接失败
原因：
- 网络/代理/组织策略限制
解决：
- 已彻底改为本地 Ollama 模型，不依赖外部 API

5. 问题：检索结果被 DOI、Received、Citation 干扰
解决：
- 已在 split_text.py 和 search_chunks.py 中增加文本清洗与噪声过滤

6. 问题：auto_rag_app.py 报 No module named 'app'
原因：
- 导入方式不对
解决：
- 在同目录下直接 from rag_app import run_rag_once

十二、建议使用规范
1. 每次新增 PDF 后，建议重新执行：
python app\auto_rag_app.py
并在提示中选择重建知识库（y）

2. 如果只改了 Prompt，不需要重建索引
直接运行：
python app\rag_app.py

3. 如果只想调试检索质量：
- 修改 split_text.py
- 修改 search_chunks.py
- 然后重新运行分片和建索引

4. 如果只想调试回答风格：
- 只改 prompt_template.txt
- 不必改 Python 代码

最终推荐操作方式（给零基础用户）
最简单的固定流程：
1. 把 PDF 放到 pdfs 文件夹
2. 打开 Anaconda Prompt
3. 激活环境：
conda activate D:\conda_envs\rag_env
4. 进入项目目录：
cd %USERPROFILE%\Desktop\local-rag-project
5. 运行总程序：
python app\auto_rag_app.py
6. 按提示输入问题即可

这就是当前最推荐、最稳定、最适合零基础用户的使用方式。
