import tomllib

# 读取 pyproject.toml 里的依赖
with open("pyproject.toml", "rb") as f:
    deps = tomllib.load(f)["project"]["dependencies"]

# 写入 requirements.txt（含镜像源命令）
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("# 一键安装命令：\n")
    f.write(
        "# pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple\n\n"
    )
    f.write("\n".join(deps) + "\n")
