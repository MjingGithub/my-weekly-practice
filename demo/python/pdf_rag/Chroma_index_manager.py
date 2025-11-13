# -*- coding: utf-8 -*-
# !/usr/bin/env python3
import logging
import chromadb
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine


# 全局变量（可改为配置）
CHROMA_DB_DIR = "d:/4px_work/MyNote/AI学习/chroma_db"  # 本地持久化路径


class ChromaIndexManager:
    def __init__(self, collection_name):
       self.collection_name = collection_name
       self.logger = logging.getLogger(__name__)  # 使用模块级日志记录器

    def save_nodes(self, documents):
        """
        首次初始化
        :param documents:
        :return:
        """
        self.logger.info(f"开始保存文档到集合: {self.collection_name}")
        db = chromadb.PersistentClient(CHROMA_DB_DIR)
        chroma_collection = db.get_or_create_collection(self.collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        VectorStoreIndex(documents, storage_context=storage_context, show_progress=True)  # 自动持久化
        self.logger.info("文档保存完成")

    def load_index(self):
        """
        加载索引
        :return:
        """
        self.logger.info(f"开始加载索引: {self.collection_name}")
        try:
            db = chromadb.PersistentClient(CHROMA_DB_DIR)
            chroma_collection = db.get_or_create_collection(self.collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            index= VectorStoreIndex.from_vector_store(vector_store)
            self.logger.info("索引加载完成")
            return index
        except Exception as e:
            self.logger.error(f"加载索引时出错: {e}")
            raise

    def query(self, question, index):
        """
        查询：先提取年份，用 metadata 过滤，再语义检索
        """
        # 假设你有这个函数来提取年份
        def _extract_year_from_question(question: str) -> int:
            import re
            # 匹配 1800~2099 之间的年份
            match = re.search(r'(18|19|20)\d{2}', question)
            return int(match.group()) if match else None

        # year = _extract_year_from_question(question)
        year = None
        self.logger.debug(f"提取年份: {year}")
        postprocessor = SimilarityPostprocessor(similarity_cutoff=0.6)

        if year is not None:
            self.logger.info(f" Filtering by year: {year}")
            filters = MetadataFilters(
                filters=[ExactMatchFilter(key="year", value=str(year))]
            )
            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=3,
                filters=filters
            )
        else:
            self.logger.info("No year found, searching across all years")
            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=3
            )
        # nodes = retriever.retrieve(question)
        # self.logger.info(f"检索到的节点数量:{len(nodes)}" )
        # for n in nodes:
        #     self.logger.info(f"Node text:{n.text}")
        #     self.logger.info(f"Node score:{n.score}")  # 看相似度分数

        engine = RetrieverQueryEngine(
            retriever=retriever,
            node_postprocessors=[postprocessor]
        )
        response = engine.query(question)
        # 如果需要查看检索到的节点，可以通过 response 获取
        source_nodes = response.source_nodes
        self.logger.info(f"检索到的节点数量: {len(source_nodes)}")
        for n in source_nodes:
            self.logger.info(f"Node text:{n.text}")
            self.logger.info(f"Node score:{n.score}")  # 看相似度分数

        return response
