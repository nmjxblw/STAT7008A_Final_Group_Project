# READ ME

Main folder for the project.

### Classifier

逻辑：将Unclassified的pdf文件进行文本提取后处理（其他类型文件不会处理）
，进行文本分析和切分，分别存入/DB/common和/DB/embedding下。

若在进行文本分析时发现之前存储过该文件信息，则跳过

在全部模型相关步骤（分析，切分）完成，确认不会造成分析和切分不同步后，将分析和切分内容分别保存。