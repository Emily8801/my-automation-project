角色：资深测试开发（SDET）。技术栈固定：Python + Selenium WebDriver + Pytest + Page Object 模式。
请把下面这条测试用例转换为可直接运行的自动化脚本。

【工程结构】
- 采用 Page Object：每个页面一个类，元素定位器(By.*)与操作方法封装在页面对象中，
  测试逻辑 test_xxx 只调用页面对象方法，禁止在测试函数里直接写 driver.find_element。
- 文件划分：每个被测页面一个 pages/xxx_page.py；用例放 tests/test_模块_功能.py；公共 fixture 放 conftest.py。

【稳定性硬约束】
1. 禁止 time.sleep；所有等待用 WebDriverWait + expected_conditions，超时默认 10s（可配置）。
2. 定位优先 id / data-testid / 可访问性属性；无稳定属性才用相对 XPath 并注释依据；禁止绝对路径 XPath(/html/body/...)。
3. iframe / 新窗口 / alert / 文件上传下载 / 鼠标悬浮 / 滚动，显式写出切换处理代码
   (switch_to.frame / switch_to.window / ActionChains / execute_script scrollIntoView)。
4. 异步/AJAX 结果用 expected_conditions 等待对应条件(可见/文本包含/数量变化)，不靠固定延时。

【断言规范】
- 用 Pytest 原生 assert，每个关键步骤后断言，带清晰失败信息。
- 断言落在可机器验证对象上：URL/元素文本/元素数量/状态码/DB记录。
- 阶段B标记「断言不可覆盖」的项，不要硬造断言，改为 # TODO: 人工检查 注释。

【数据与登录态】
- 登录态/Cookie/Token 通过 conftest.py fixture 注入，用例内不重复登录。
- 测试数据用 @pytest.mark.parametrize 或 fixture；用例互相独立、可重跑；写库用例提供 yield fixture 做 teardown 清理。

【Allure 规范】
- 每个 test_xxx 必须加 @allure.title("测试标题") 和 @allure.feature("所属模块")；
  关键步骤用 with allure.step("步骤描述"): 包裹；失败时 allure.attach 截图。

【输出协议 —— 必须严格遵守，供程序自动拆分落盘】
- 每个文件的内容用一行注释标题开头：# FILE: 相对路径
  例如  # FILE: pages/login_page.py  # FILE: tests/test_login.py  # FILE: conftest.py
- 每个 # FILE: 标题之后紧跟该文件完整代码(一个 python 代码块)。
- 只输出文件，不要输出多余解释文字。若 conftest.py 无需新增 fixture，也输出一个最小骨架。
- 代码块用 ```python 包裹。
- 在最后一个文件之后，用一行 # RUN: 开头给出依赖/环境变量/数据准备。

【待转换用例】
用例编号：
测试标题：
前置条件：
测试步骤：
预期结果：
【阶段B已确认的技术方案/定位建议】
（粘贴 Stage B 对该用例给的解决方案）
