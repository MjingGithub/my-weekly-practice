# week001 - 基于gpt的excel文档解析与处理

## 1. 基本思路
1. 解析excel，展示前几行作为上下文；
2. 下达指令，让gpt生成python代码，提取代码执行；
3. 如果报错指导gpt修正代码继续执行；
4. 如果GPT理解错误，可以自己调整提示词，一步步引导gpt更准确的回答；

## 2. 代码片段
1. 解析excel以markdown格式：
   ```
   def create_system_prompt(fileContent):
    wb = load_workbook(filename = fileContent)
    system_prompt="You are working with a Workbook in Python.The name of the workbook is `wb`."
    sheet_names = wb.sheetnames
    for sheet_name in sheet_names:
        sheet = wb[sheet_name]
        header = [cell.value for cell in sheet[1]]
        max_rows = sheet.max_row
        system_prompt+=f"\nwb['{sheet_name}'] has {max_rows} rows with excel index and head(10) rows as below:\n"
        column_index=[]
        for i in range(len(header)):
            column_index.append(get_column_letter(i+1))
        data=[]
        for row in sheet.iter_rows(values_only=True):
            data.append(row)
        df = pd.DataFrame(data)
        df.columns = column_index
        system_prompt+=df.head(10).to_markdown(index=False)+"\n"

    print(system_prompt)
    return system_prompt
   ```
2. 代码生成agent:
   ```
    def code_generate_agent(user_prompt):
          context= [{'role':'system', 'content':f"{pn.state.system_prompt}，根据openpyxl库生成以下用户提问的代码，剔除加载工作簿部分，直接使用我的上下文中输入的wb工作簿,如果有返回结果，结果赋值给我的全局变量_result"}]
          context.append({'role':'user', 'content':f"{user_prompt}"})
          response = invokeAIResponseFrom_langChain(context) 
          return response
   ```
3. 代码纠正agent：
   ```
   def code_revise_agent(exec_code,error_msg):
      context= [{'role':'system', 'content':f"{pn.state.system_prompt}，你负责纠正基于以上wb表格执行出现的代码错误，请注意不要改变变量名称和代码执行意图"}]
      context.append({'role':'user', 'content':f"我执行的代码是：{exec_code}，错误信息是：{error_msg}，请帮我修正生成正确的代码"})
      response = invokeAIResponseFrom_langChain(context) 
      return response
   ```
   
## 3.更进一步
1. 标准格式转换：可以解析pdf等非标准化格式转为excel标准格式，做定制化excel映射处理；
2. 图表化处理：将excel数据按要求生成柱状图，饼图，折线图等；
3. 数据清洗：将上传的文件清洗加工后输出；