# 主要参考资料
 [Awesome-LLM-RAG-Application](https://github.com/lizhe2004/Awesome-LLM-RAG-Application?tab=readme-ov-file)

# 什么是RAG?
 [rag定义](https://www.promptingguide.ai/zh/research/rag#rag%E7%AE%80%E4%BB%8B)
 
# RAG工具介绍
1. langchain
[langchain](https://python.langchain.com/docs/tutorials/rag/#setup)

# 从0-1搭建知识库
[词向量及向量知识库介绍](https://datawhalechina.github.io/llm-universe/#/C3/1.%E8%AF%8D%E5%90%91%E9%87%8F%E5%8F%8A%E5%90%91%E9%87%8F%E7%9F%A5%E8%AF%86%E5%BA%93%E4%BB%8B%E7%BB%8D)

## 本地安装部署chroma向量库
[chroma官网](https://www.trychroma.com/)

**python安装：**
```
pip install chromadb 
```
**server启动**
```
chroma run --path /db_path
chroma run --path d:/4px_work/MyNote/AI学习/chroma_db
```
**client连接**
1. 阻塞式http连接
```
import chromadb
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
```
2. 非阻塞式（异步）httpclient
```
import asyncio
import chromadb

async def main():
    client = await chromadb.AsyncHttpClient()

    collection = await client.create_collection(name="my_collection")
    await collection.add(
        documents=["hello world"],
        ids=["id1"]
    )

asyncio.run(main())
```

## 使用Embedding API
```
def zhipu_embedding(text: str):

    api_key = os.environ['ZHIPUAI_API_KEY']
    client = ZhipuAI(api_key=api_key)
    response = client.embeddings.create(
        model="embedding-2",
        input=text,
    )
    return response
```
## 数据处理
1. 数据读取
*pdf文档读取**
 langChain 的 PyMuPDFLoader
```
from langchain.document_loaders.pdf import PyMuPDFLoader
loader = PyMuPDFLoader("D:\\4px_work\\MyNote\\AI学习\\知识库文档\\pumpkin_book.pdf")
pdf_pages = loader.load()
```
*md文档读取**
langchain的 UnstructuredMarkdownLoader
```
from langchain.document_loaders.markdown import UnstructuredMarkdownLoader
loader = UnstructuredMarkdownLoader("../../data_base/knowledge_db/prompt_engineering/1. 简介 Introduction.md")
md_pages = loader.load()
```
2. 数据清洗
   我们期望知识库的数据尽量是有序的、优质的、精简的，因此我们要删除低质量的、甚至影响理解的文本数据。
   部分空格，换行符，.等可以删除
   ```
   ## 我们发现数据中还有不少的•和空格，我们的简单实用replace方法即可。
    pdf_page.page_content = pdf_page.page_content.replace('•', '')
    pdf_page.page_content = pdf_page.page_content.replace(' ', '')
   ```
3. 文档分割
   由于单个文档的长度往往会超过模型支持的上下文，导致检索得到的知识太长超出模型的处理能力，因此，在构建向量知识库的过程中，我们往往需要对文档进行分割，将单个文档按长度或者按固定的规则分割成若干个 chunk，然后将每个 chunk 转化为词向量，存储到向量数据库中。

在检索时，我们会以 chunk 作为检索的元单位，也就是每一次检索到 k 个 chunk 作为模型可以参考来回答用户问题的知识，这个 k 是我们可以自由设定的。

Langchain 中文本分割器都根据 chunk_size (块大小)和 chunk_overlap (块与块之间的重叠大小)进行分割。

- chunk_size： 指每个块包含的字符或 Token （如单词、句子等）的数量
- chunk_overlap： 指两个块之间共享的字符数量，用于保持上下文的连贯性，避免分割丢失上下文信息
![text_splitter](/assets/text_splitter.png)

注：如何对文档进行分割，其实是数据处理中最核心的一步，其往往决定了检索系统的下限。但是，如何选择分割方式，往往具有很强的业务相关性——针对不同的业务、不同的源数据，往往需要设定个性化的文档分割方式。因此，在本章，我们仅简单根据 chunk_size 对文档进行分割。对于有兴趣进一步探索的读者，欢迎阅读我们第三部分的项目示例来参考已有的项目是如何进行文档分割的。

4. 向量化存储
[chroma langchain vectorstore](https://python.langchain.com/docs/integrations/vectorstores/chroma/#basic-initialization)
这里使用的zhupu ai封装的embedding ,向量库使用chroma,并持久化保存
```
rom  ZhipuAIEmbedding import ZhipuAIEmbeddings
## 定义embeddings
embedding = ZhipuAIEmbeddings()
from langchain.vectorstores import Chroma
import chromadb
# client = chromadb.HttpClient(host='localhost', port=8000)
# 定义Chroma持久化路径
persist_directory = 'd:/4px_work/MyNote/AI学习/chroma_db'
vectordb = Chroma.from_documents(
    documents=split_docs[:20], # 为了速度，只选择前 20 个切分的 doc 进行生成；使用千帆时因QPS限制，建议选择前 5 个doc
    embedding=embedding,
    persist_directory=persist_directory # 允许我们将persist_directory目录保存到磁盘上
    # client=client
)
# vectordb.delete_collection()
print(f"向量库中存储的数量：{vectordb._collection.count()}")
```
5. 向量化查询
*相似度检索-余弦相似度**
```
question="什么是西瓜书"
sim_docs = vectordb.similarity_search(question,k=3)
print(f"检索到的内容数：{len(sim_docs)}")
for i, sim_doc in enumerate(sim_docs):
    print(f"检索到的第{i}个内容: \n{sim_doc.page_content[:200]}", end="\n--------------\n")
```
*MMR检索**
果只考虑检索出内容的相关性会导致内容过于单一，可能丢失重要信息。

最大边际相关性 (MMR, Maximum marginal relevance) 可以帮助我们在保持相关性的同时，增加内容的丰富度。

核心思想是在已经选择了一个相关性高的文档之后，再选择一个与已选文档相关性较低但是信息丰富的文档。这样可以在保持相关性的同时，增加内容的多样性，避免过于单一的结果。
```
mmr_docs = vectordb.max_marginal_relevance_search(question,k=3)
for i, sim_doc in enumerate(mmr_docs):
    print(f"MMR 检索到的第{i}个内容: \n{sim_doc.page_content[:200]}", end="\n--------------\n")
```
# 如何与chat_sql结合应用？