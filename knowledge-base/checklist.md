AWS Glue Job – Peer Review Checklist


## 1. Code Structure & Readability
- Is the code modular and function-based? Common functions being used for any repetitive code?
- Are variable, methods, classes and function names meaningful?
- Are all method and function names in lowercase with words separated by underscore eg. calculate_salary,verify_address?
- Are Python's built-in classes named in lowercase?
- Does class name follows UpperCamelCase convention?
- Is unnecessary commented code removed?
- Do all except clause end with error?
- Are all Instance variable names in lowercase with words separated by underscore eg. abc_def?
- Redundant comments, print, count and show statements have been removed?


## 2. Error Handling & Logging
- Does Transformation script start with comments helpful for reader to understand?
- Does the above comment has meaningful comments helpful for readers to understand.
- Each module,class/method has comments in form of Docstring wherein purpose,input/output should be clearly mentioned?
- Are try-except blocks used where required?
- Are errors logged with meaningful messages?
- Is logging level appropriate (INFO / WARN / ERROR)?


## 3. Security & Compliance
- Are there no hardcoded credentials or secrets?
- Are IAM roles used instead of keys?


## 4. Configuration & Maintainability
- Are configs externalized (S3 / parameters)?
- Are comments and docstrings present?
- Is the job easy to modify and extend?


## 5. AWS Glue Best Practices
- Correct use of DynamicFrames / DataFrames?
- Proper use of Spark context and Glue context?


## 6. Imports
- All imports should occur at the top of the module, after any module docstring


## 7. Job name
- Input job name should be all lower case and separated by only underscore. Example : abc, abc_def
