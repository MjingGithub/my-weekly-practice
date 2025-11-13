# !/usr/bin/env python3
from Chroma_index_manager import *
from LLM_manager import *
from pdf_load_and_optimize import *

from llama_index.core.evaluation import FaithfulnessEvaluator
from llama_index.core.evaluation import EvaluationResult
from llama_index.core import Response
from llama_index.core.evaluation import RelevancyEvaluator

import pandas as pd
pd.set_option("display.max_colwidth", 0)

import logging
from logging_config import setup_logging

# 初始化全局日志配置
setup_logging(log_level=logging.DEBUG, log_file="logs/pdf_rag_app.log")

import nest_asyncio
nest_asyncio.apply()

# define jupyter display function
def display_eval_df(
        eval_results: List[EvaluationResult]
) -> None:
    # 收集所有评估结果信息
    sources = []
    scores = []
    eval_results_display = []
    reasonings = []

    for i, eval_result in enumerate(eval_results):
        # 源节点文本
        sources.append(f"Source {i+1}: {eval_result.contexts[0][:300]}...")
        # 相关性分数
        scores.append(f"{eval_result.score:.4f}" if eval_result.score else "N/A")
        # 评估结果
        eval_results_display.append("Pass" if eval_result.passing else "Fail")
        # 推理原因
        reasonings.append(eval_result.feedback or "No feedback")

    # 创建包含所有信息的 DataFrame
    eval_data = {
        "Query": [eval_results[0].query] * len(sources),
        "Source": sources,
        "Score": scores,
        "Eval Result": eval_results_display,
        "Reasoning": reasonings
    }
    eval_df = pd.DataFrame(eval_data)
    # 输出格式化的表格
    print("\n" + "="*100)
    logging.info(eval_df.to_markdown(index=False))
    print("="*100 + "\n")



def main():
    """主函数"""
    logger = logging.getLogger(__name__)
    logger.info("开始执行RAG查询主程序")
    # pdf_path = "d:/4px_work/MyNote/AI学习/知识库文档/诺贝尔/诺贝尔化学奖.pdf"
    # #
    # logger.info("开始加载PDF文档...")
    # nobelPdfLoader = NobelPdfLoader(pdf_path)
    # documents = nobelPdfLoader.load_pdf_with_reader()
    # logger.info(documents[2].text)

    logger.info("加载PDF文档完成！")
    #
    # 定义全局llm
    LLMManager()
    logger.info("开始构建索引...")
    # indexManager = ChromaIndexManager(collection_name="chemical_nobel_prizes")
    # indexManager = ChromaIndexManager(collection_name="chemical_nobel_prizes_v2")
    # indexManager = ChromaIndexManager(collection_name="chemical_nobel_prizes_v3")
    indexManager = ChromaIndexManager(collection_name="chemical_nobel_prizes_v4")
    # 首次初始化-持久化保存
    # indexManager.save_nodes(documents)
    # 二次读取-读取持久化保存的节点
    index = indexManager.load_index()

    query = "2010年诺贝尔化学奖的获得者是谁？"
    response = indexManager.query(query, index)
    logger.info(f"response：{response}")

    # evaluate llm response
    # define evaluator

    # 忠诚度评估
    evaluator = FaithfulnessEvaluator(llm=LLMManager.get_llm())

    response_str = response.response
    # 使用源节点内容作为 contexts
    eval_source_result_full = [
        evaluator.evaluate(
            query=query,
            response=response_str,
            contexts=[source_node.get_content()],
        )
        for source_node in response.source_nodes
    ]
    # logger.info(f"eval_source_result_full:{eval_source_result_full}")
    display_eval_df(eval_source_result_full)


if __name__ == "__main__":
    main()


