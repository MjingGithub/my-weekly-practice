# 1. 首先探讨odps使用python导出切割文件，参考：
 [pyodps](https://pyodps.readthedocs.io/zh-cn/stable/)

# 2. 结合ai chat输入，生成sql语句，替换后能自动导出数据

# 3. 聊天框输入某个表，希望按用户输入分析产出图表

# 提示词示例：
''' 
## 你是一个odps语法专家，请根据用户的提问，预判应使用哪个表生成用户需要的sql语句。
## 已知有这些表，我已经给他们做了打标：
1. dwd_css_settlement_fee：结算表
2. dwd_css_pengding_fee：待结表
3. dsf_ods.o_ironforge_billing_billing_info： 计费表
4. temu_recon_source_data_recently_v5： 多多账单原表
## 请按下面的步骤逐步分析得到最终的sql语句：
1. 根据已知表打标预判要使用的表tablea
2. 使用 df = DataFrame(o.get_table('tablea')) , df.head(10)查看前10行数据
3. 根据用户的需求分析得出最终的sql语句并输出
## 用户的输入{}
'''

# 实现自动生成sql
1. 定位表agent
2. 解析表，根据表结构确定sql agent

# 挑战：
1. 如何让gpt知道表分区，选择正确的分区(对于全量分区表，查询最大分区值使用。否则使用日期范围查询往前后1天)
2. 如何知道表字段注释（投喂建表语句，或自住查询表schema）
# 结果：
最终使用cursor快速生成了一版，但是准确性不够理想，对输入也比较依赖。

# 思考
参考市面上已有的db-gpt等工具，了解他们的生成思路后，再进一步优化。

# 参考链接：
 [LLM-RAG-Application](https://github.com/lizhe2004/Awesome-LLM-RAG-Application?tab=readme-ov-file)