# FOFA_Extract_Fingerprint

![image-20230713103142709](https://s2.loli.net/2023/07/13/h43nW5QGd1tlfYS.png)

半自动化指纹提取。

**扩充自[Fofa-script](https://github.com/Cl0udG0d/Fofa-script)**

## 主要思想

- 给定需要提取的文档，对于含有 `metadata`的文档，将 `metadata`转化为可供 `FOFA`查询的 `FOFA`查询语句。
- 以此语句查询到的结果为**基准数量**，并获取结果的网址，称为**样例网址**。
- 利用这些网址**提取特征**，现在可以进行
  - `header`
  - 图标hash
  - 首页源码中的文件
  - 首页源码中以 `#`开头的颜色
  - 首页源码中的函数
  - 首页源码中的注释
    - `<!-- -->`
    - `//`
- 若这些特征在这些样例网址中存在比例大于给定比例，则将特征转化为FOFA查询语句，并获取结果数量。
- 若**数量与基准数量**的比值在给定指纹特征可接受的范围内，则将其视为一个**新的指纹。**

## 使用方式

### 预设置

- 修改 `config.py`中的 `cookie`，  `folder_path`，`output_path`。

  - `cookie` 设置详见该仓库 [Fofa-script](https://github.com/Cl0udG0d/Fofa-script)
  - `folder_path` 需要提取文档的路径（路径中只有待提取文档）
  - `output_path` 为输出 `json`指纹的路径
  - 以上两个路径不能相同
- `config.py`中可以根据个人需求更改变量值

  - `StartPage`：**样例网址**获取的起始页面，默认值为第一页
  - `StopPage`：**样例网址**获取的终止页面，默认值为第二页
  - `TimeSleep`：**样例网址**爬取之间的Sleep时间，默认值为5s。
  - `pro_first_lower`：若特征在样例网址中存在比例该值，即比例，则将该特征转化为 `FOFA`查询语句进一步验证，默认为0.25。
  - `pro_upper`：确定为指纹的比例区间的上界，默认为1.5。
  - `pro_lower`：确定为指纹的比例区间的下界，默认为0.9。

### 运行

```powershell
python .\FOFA_Extract_Fingerprint.py
```

### 格式规定

对于待提取文档名字 `abcd.yaml`，将输出文档格式 `abcd_fingerprint.json`

### 模式选择

共有四种模式：

```python
menu = """
1. Batch extraction (From config.folder_path).
2. Batch extraction (From config.deal_file_names).
3. Single extraction.
4. No metadata file extraction."""
```

![image-20230713101132751](https://s2.loli.net/2023/07/13/UGsEt8kLFgyJBPC.png)

分别为：

1. 批处理提取（文件名自动取自 `config.folder_path 路径下`）
   - 提取给定文件

2. 批处理提取（文件名取自 `config.deal_file_names`）

   - 提取给定的文件

   - `config.deal_file_names`：以 `python` 列表格式，内容为字符串形式的文件名

3. 单特征提取

   - **手动输入** `FOFA`查询条件，获取查询结果数，以此为指纹提取的参照。

   - 对于没有 `metadata`的文档，可以后续通过此选项，手动指定基准 `FOFA`查询条件

4. 对于没有`metadata`的文件进行批处理提取
   - 对于 `config.folder_path 路径下`的文件，判断文件内部是否有`metadata`，只对没有`metadata`进行处理，类似于模式一
   
   - 对于每个文件，需要先**手动输入**基准`FOFA`查询语句，进而开始自动化指纹提取。
   
     ![image-20230713105953988](https://s2.loli.net/2023/07/13/58d23uaCsTVA4Sh.png)

### INDEX选择

![1689130618024](image/README/1689130618024.png)

- 每次运行，都将提示每个文件的索引
- 若之前进行了提取操作但是中断了，可以通过输入索引，**手动**继续程序。

### 文件用途介绍

- `FOFA_Extract_Fingerprint.py`：提取指纹主文件
- `config.py`：用户设置的配置文件
- `Default_value.py`：指纹提取模板信息文件，用户可根据需要进行增删修改，包括：
  - `json_tmp`：输出`json`文件的模板（默认所有`level`为2）；
  - `common_header`：屏蔽的`header`信息（即对于这些`header`，默认不会视作指纹）；
  - `common_header_value`：屏蔽的`header value`：屏蔽的`header`内容；
  - `file_common_names`：屏蔽的文件名字。
- `fofa.py`：爬虫文件，修改自[Fofa-script](https://github.com/Cl0udG0d/Fofa-script)
- `Tools.py`：相关函数文件

## 批处理提取注意事项

### 从未进行过提取操作

即输出文件路径中没有待提取文档的输出文件。

- 需要用户手动输入指纹相关信息，进行**半自动**提取。

- `product_name`，`company`，`industry`

  ![image-20230713104404373](https://s2.loli.net/2023/07/13/LWeKAMoBD3p4U5V.png)

- `rules`——`icon_hash`

  ![image-20230713105120556](https://s2.loli.net/2023/07/13/M91g4XH8YFTmxuU.png)

### 已经进行过提取操作，提取的指纹在 `output_path`中

程序将根据输出文件路径中的文件，进行查询，如果输出文件中有待处理文件的输出文件（文件名按照上文格式规定进行判断）：

- **则默认用户已经进行了`product_name`，`company`，`industry`，`level`以及`rules`中的`icon_hash`的手动填写**
- 程序则跳过需要用户手动输入的`product_name`，`company`，`industry`以及`rules`中的`icon_hash`，**实现自动化提取`rules`**。

