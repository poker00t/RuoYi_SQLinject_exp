# RuoYi_SQLinject_exp

## Product Information
- **Product**: RuoYi
- **Version**: 4.8.1
 
## POC
 
### Execution Steps
1. **Log in to RuoYi backend system**
2. **Select "System Tools"(系统工具) -> "Code Generation"(代码生成) -> "Create"(创建) and submit the payload: "CREATE TABLE abc_test AS SELECT(IF(1=1,BENCHMARK(30000000,MD5(1)),0)) AS RESULT;" (although the last prompt to create the table structure exception, in fact, the payload successfully executed)**
   <img width="2390" height="1454" alt="image" src="https://github.com/user-attachments/assets/91b365a0-ff4f-4a2a-8fee-3d1607342470" />
3. **The SQL statement is executed successfully, the response is delayed and a new table named “abc_test” is added to the database, proving the existence of SQL injection vulnerability.**
   <img width="2514" height="1532" alt="image" src="https://github.com/user-attachments/assets/54d84022-f933-46f3-b0ac-14aa2625f83e" />
   <img width="1668" height="426" alt="image" src="https://github.com/user-attachments/assets/0c009a15-ee13-48f9-a5e0-aa89b817c893" />

## EXP
**The python exploit script will automate a time-based SQL blind injection on the vulnerable site, eventually obtaining the "login_name" and "password" of the database table "sys_user".**

## Vulnerability Analysis
**When accessing the URL path "/tool/gen/createTable", enter the function of class GenController "public AjaxResult create(String sql)" 
[RuoYi\ruoyi-generator\src\main\java\com\ruoyi\generator\controller\GenController.java]**
<img width="1656" height="886" alt="image" src="https://github.com/user-attachments/assets/817e9ccf-e564-4db9-9f01-5707c36ac449" />

**Within the create function, the code first invokes SqlUtil.filterKeyword(sql) to perform keyword filtering on our injected SQL statement, with the explicit purpose of preventing SQL injection attacks. Let's examine the implementation of the filterKeyword method.
[RuoYi\ruoyi-common\src\main\java\com\ruoyi\common\utils\sql\SqlUtil.java]**
<img width="1650" height="836" alt="image" src="https://github.com/user-attachments/assets/2a14fdb4-3b97-4c13-b51d-f32478023429" />

**The filterKeyword function implements SQL filtering primarily through StringUtils.split(SQL_REGEX, "\\|"). Notably, there exists a keyword blacklist named SQL_REGEX that we examined. While this blacklist does filter numerous keywords, our payload:"CREATE TABLE abc_test AS SELECT(IF(1=1,BENCHMARK(30000000,MD5(1)),0)) AS RESULT;" successfully bypasses detection because the patterns SELECT[space] and SELECT( do not match the regular expression rules in SQL_REGEX.**
<img width="1562" height="374" alt="image" src="https://github.com/user-attachments/assets/276734b0-76c0-4018-a165-f35efcacfcdc" />

**Upon completion of SqlUtil.filterKeyword(sql) execution, the subsequent if statement checks whether our SQL statement conforms to the MySqlCreateTableStatement type. This condition mandates the use of CREATE TABLE syntax in our payload, which explains why our exploit must begin with**
<img width="1536" height="452" alt="image" src="https://github.com/user-attachments/assets/358ff866-ca8e-4d39-b2c7-0a04d063abbe" />

**The filtered SQL statement ultimately gets executed through genTableService.createTable(createTableStatement.toString()). Let's examine the implementation of this critical method**
<img width="1022" height="232" alt="image" src="https://github.com/user-attachments/assets/ff38435d-5dc7-442c-a6f4-56f4ad5a5bcc" />

**The SQL statement execution path was traced to the genTableMapper component. Upon further investigation:
    We located the corresponding MyBatis XML mapper file at:
    [RuoYi/ruoyi-generator/src/main/resources/mapper/generator/GenTableMapper.xml]**
<img width="1232" height="366" alt="image" src="https://github.com/user-attachments/assets/46868677-d780-499f-b27d-9889099e8686" />

**Analysis revealed:
        SQL statements are dynamically concatenated
        No parameterized queries or prepared statements are used
        Input validation relies solely on the previously analyzed filterKeyword method
This combination of dynamic SQL concatenation and insufficient input sanitization creates the perfect conditions for SQL injection, as demonstrated by our payload's successful execution despite keyword filtering.**


