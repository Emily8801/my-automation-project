import os

def setup():
    """初始化项目运行环境"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    #创建必要的目录
    dirs = ["reports","logs","screenshots","tests"]
    for d in dirs:
        path = os.path.join(root,d)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"创建目录：{path}")
    #检查.env文件
    env_file = os.path.join(root, ".env")
    if not os.path.exists(env_file):
        print(f"警告：未找到{env_file},请创建配置文件")

    print("环境初始化完成")

if  __name__ == "__main__":
    setup()

