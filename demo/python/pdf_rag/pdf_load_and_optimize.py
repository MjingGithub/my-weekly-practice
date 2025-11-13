# -*- coding: utf-8 -*-
# !/usr/bin/env python3
import logging
import os
from typing import List

import pdfplumber
from llama_index.core.schema import TextNode, Document
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
import re


# PDF Loader
def format_record_line(kv_pairs_dict):
    # 将生硬的表格表头和字段的对应信息转为更流畅的自然语言表述方式：xxx年的诺贝尔化学奖获奖者是xxx,他们因为xxx而获奖
    year = kv_pairs_dict.get("年份",None)
    winner = kv_pairs_dict.get("获奖者",None)
    country = kv_pairs_dict.get("国籍",None)
    reason = kv_pairs_dict.get("获奖原因",None)
    negative_markers = ["未颁奖", "未颁发", "未授予", "空缺", "从缺"]
    formatted_text = ""
    awarded = not (winner is not None and any(marker in winner for marker in negative_markers))
    if year is not None:
        if awarded is False:
            formatted_text = f"{year}年的诺贝尔化学奖未颁发。"
        else:
            formatted_text = f"{year}年的诺贝尔化学奖获奖者是{winner}，因为{reason}而获奖。"
    return awarded,formatted_text


class NobelPdfLoader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.logger = logging.getLogger(__name__)

    def load_pdf_with_reader(self):
        """使用pdfplumber逐页解析PDF，仅解析表格：第一行作为表头，其余作为记录。返回每页一个Document。"""
        documents: list[Document] = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.logger.info(f"pdfplumber 打开PDF，共 {len(pdf.pages)} 页")
                for page_index, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables() or []

                    # 处理表格：取第一行作为表头，行到记录
                    for table_index, table in enumerate(tables, start=1):
                        # 如果 table 是空/None，或者 table 中所有行都是空的（没有一行是非空的），就进入这个 if 分支
                        if not table or not any(row for row in table):
                            continue
                        # 去除表格每一个值的前后空格，和无效表格数据
                        headers = [h.strip() if isinstance(h, str) else "" for h in (table[0] or [])]
                        headers = [h for h in headers if h is not None]
                        if not headers:
                            continue
                        for row in table[1:]:
                            if not row:
                                continue
                            cells = [c.strip() if isinstance(c, str) else "" for c in row]
                            kv_pairs_dict = {header: cells[idx].replace("\n", "") if idx < len(cells) else "" for idx, header in enumerate(headers)}
                            awarded, formatted_text = format_record_line(kv_pairs_dict)
                            documents.append(
                                Document(
                                    text=formatted_text,
                                    metadata={
                                        "page_number": page_index,
                                        "file_name": os.path.basename(self.pdf_path),
                                        "source": "pdfplumber",
                                        "year": kv_pairs_dict.get("年份", None),
                                        "winner": kv_pairs_dict.get("获奖者", None),
                                        "awarded": awarded
                                    },
                                )
                            )

                    # 只有在没有表格的情况下才提取页面文本,使用SentenceSplitter分块
                    if not tables:
                        page_text = page.extract_text() or ""
                        if page_text.strip():
                            splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
                            page_texts = splitter.split_text(page_text.strip())
                            for trunk_text in page_texts:
                                documents.append(
                                    Document(
                                        text=trunk_text.strip(),
                                        metadata={
                                            "page_number": page_index,
                                            "file_name": os.path.basename(self.pdf_path),
                                            "source": "pdfplumber"
                                        },
                                    )
                                )

                    if len(documents) % 10 == 0:
                        self.logger.info(f"PDF第{documents[-1].metadata['page_number']}页，第{len(documents)}个chunk，内容为：{documents[-1]},metadata:{documents[-1].metadata}")

            self.logger.info(f"成功加载PDF文档，共生成 {len(documents)}个chunk。 ")
            return documents
        except Exception as e:
            self.logger.error(f"pdfplumber 解析失败: {e}")
            # 回退到SimpleDirectoryReader
            return SimpleDirectoryReader(input_files=[self.pdf_path]).load_data()

