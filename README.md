# FOFA_Extract_Fingerprint

半自动化指纹提取。

**扩充自[Fofa-script](https://github.com/Cl0udG0d/Fofa-script)**

## 使用方式

### 预设置

- 修改 `config.py`中的 `cookie`，  `folder_path`，`output_path`。
  - `cookie` 设置详见该仓库 [Fofa-script](https://github.com/Cl0udG0d/Fofa-script)
  - `folder_path` 需要提取文档的路径（路径中只有待提取文档）
  - `output_path` 为输出 `json`指纹的路径
  - 以上两个路径不能相同

### 运行

```powershell
python .\FOFA_Extract_Fingerprint.py
```


### 格式规定

对于待提取文档名字 `abcd.yaml`，将输出文档格式 `abcd_fingerprint.json`


### 模式选择

共有三种模式：

```python
menu = """
1. Batch extraction (From config.folder_path).
2. Batch extraction (From config.deal_file_names).
3. Single extraction."""
```

分别为：

- 批处理提取
- 批处理提取
  - 提取给定文件名，以 `python` 
- 单特征提取
  - 手动输入基准 `FOFA`查询条件，以此为指纹提取的参照。


## 半自动注意事项

### 已经进行过提取操作，之前提取的指纹都在 `output_path`中

- 程序将根据


### 从未进行过提取操作
