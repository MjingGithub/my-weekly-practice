from typing import Dict
from table_locator import TableLocator
from sql_generator import SQLGenerator
from ddl_manager import DDLManager
import os
from dotenv import load_dotenv

load_dotenv()

class SQLAgent:
    def __init__(self, ddl_dir: str = "ddl_files"):
        """
        初始化SQL Agent
        :param ddl_dir: DDL文件存储目录
        """
        self.table_locator = TableLocator()
        self.sql_generator = SQLGenerator()
        self.ddl_manager = DDLManager(ddl_dir)
        
    def initialize(self):
        """初始化agent，加载表DDL信息"""
        # 加载所有DDL信息
        table_ddls = self.ddl_manager.load_all_ddls()
        self.table_locator.load_table_metadata(table_ddls)
        
    def generate_sql_from_query(self, user_query: str) -> str:
        """根据用户查询生成SQL"""
        # 1. 定位相关表
        tables = self.table_locator.locate_tables(user_query)
        
        # 2. 生成SQL
        sql = self.sql_generator.generate_sql(user_query, tables)
        
        return sql

def main():
    # 示例使用
    agent = SQLAgent()
    
    # 初始化agent（会自动加载ddl_files目录下的所有DDL文件）
    agent.initialize()
    
    # 示例查询
    user_query = "请帮我输出多多[2024年10月][美国][广东一仓]的所有对账差异明细"
    
    # 生成SQL
    sql = agent.generate_sql_from_query(user_query)
    print("生成的SQL：")
    print(sql)

if __name__ == "__main__":
    main() 