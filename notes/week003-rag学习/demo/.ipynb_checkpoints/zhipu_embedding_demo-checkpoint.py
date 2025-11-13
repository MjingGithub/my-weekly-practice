# from zhipuai import ZhipuAI
# import os
# def zhipu_embedding(text: str):

#     api_key = os.environ['ZHIPUAI_API_KEY']
#     client = ZhipuAI(api_key=api_key)
#     response = client.embeddings.create(
#         model="embedding-2",
#         input=text,
#     )
#     return response

# text = '要生成 embedding 的输入文本，字符串形式。'
# response = zhipu_embedding(text=text)
# print(response)
# print(f'response类型为：{type(response)}')
# print(f'embedding类型为：{response.object}')
# print(f'生成embedding的model为：{response.model}')
# print(f'生成的embedding长度为：{len(response.data[0].embedding)}')
# print(f'embedding（前10）为: {response.data[0].embedding[:10]}')

#1.数据读取
from langchain_community.document_loaders import PyMuPDFLoader

# 创建一个 PyMuPDFLoader Class 实例，输入为待加载的 pdf 文档路径
loader = PyMuPDFLoader("D:\\4px_work\\MyNote\\AI学习\\知识库文档\\pumpkin_book.pdf")

# 调用 PyMuPDFLoader Class 的函数 load 对 pdf 文件进行加载
pdf_pages = loader.load()
print(f"载入后的变量类型为：{type(pdf_pages)}，",  f"该 PDF 一共包含 {len(pdf_pages)} 页")
# pdf_page = pdf_pages[1]
# print(f"每一个元素的类型：{type(pdf_page)}.", 
#     f"该文档的描述性数据：{pdf_page.metadata}", 
#     f"查看该文档的内容:\n{pdf_page.page_content}", 
#     sep="\n------\n")

# 2.数据清洗
## 我们发现数据中还有不少的•和空格，我们的简单实用replace方法即可。
for pdf_page in pdf_pages:
    pdf_page.page_content = pdf_page.page_content.replace('•', '')
    pdf_page.page_content = pdf_page.page_content.replace(' ', '')
# print(pdf_page.page_content)
# 3.文档分割
## 
#导入文本分割器
from langchain.text_splitter import RecursiveCharacterTextSplitter
# 知识库中单段文本长度
CHUNK_SIZE = 500
# 知识库中相邻文本重合长度
OVERLAP_SIZE = 50
# 使用递归字符文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP_SIZE
)
# someSplit = text_splitter.split_text(pdf_page.page_content[0:1000])
# print(f"分割前1000文本后，someSplit={someSplit}")
split_docs = text_splitter.split_documents(pdf_pages)
print(f"切分后的文件数量：{len(split_docs)}")
print(f"切分后的字符数（可以用来大致评估 token 数）：{sum([len(doc.page_content) for doc in split_docs])}")

# 4.向量化存储（使用自己封装的zhupuAI embedding）
from  ZhipuAIEmbedding import ZhipuAIEmbeddings
## 定义embeddings
embedding = ZhipuAIEmbeddings()
from langchain_community.vectorstores import Chroma
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
existsCollections = client.list_collections()
print(f"existsCollections={existsCollections}")
for collections in existsCollections:
    client.delete_collection(collections)
existsCollections = client.list_collections()
print(f"after delete existsCollections={existsCollections}")
# client.reset()
# 定义Chroma持久化路径
# 从documents初始化
persist_directory = 'd:/4px_work/MyNote/AI学习/chroma_db'
vectordb = Chroma.from_documents(
    documents=split_docs, # 为了速度，只选择前 20 个切分的 doc 进行生成；使用千帆时因QPS限制，建议选择前 5 个doc
    embedding=embedding,
    persist_directory=persist_directory, # 允许我们将persist_directory目录保存到磁盘上
    client=client
)
# vectordb.delete_collection()
# client.reset()
print(f"向量库中存储的数量：{vectordb._collection.count()}")
# 5.向量化查询
## 相似度检索-余弦相似度
question="什么是西瓜书"
sim_docs = vectordb.similarity_search(question,k=3)
print(f"检索到的内容数：{len(sim_docs)}")
for i, sim_doc in enumerate(sim_docs):
    print(f"检索到的第{i}个内容: \n{sim_doc.page_content[:200]}", end="\n--------------\n")

## MMR检索
mmr_docs = vectordb.max_marginal_relevance_search(question,k=3)
for i, sim_doc in enumerate(mmr_docs):
    print(f"MMR 检索到的第{i}个内容: \n{sim_doc.page_content[:200]}", end="\n--------------\n")




