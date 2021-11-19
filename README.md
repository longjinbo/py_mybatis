# py_mybatis

dushitaoyuan/py_mybatis 基础上新增new feature

## mybatis 语法支持

### 标签修改
- foreach标签支持嵌套其他标签，如if
### 动态语法支持
- #{table,pythonType=raw} 支持动态表名
### sql 参数支持
- in语句数组结构的参数
- 支持对象参数
### 结果映射
暂不支持,查询结果参见pymysql,pymysql.cursors.DictCursor
### 数据库支持
- mysql
**理论上可支持所有sql类型数据库**
## 使用示例

### 基本示例

