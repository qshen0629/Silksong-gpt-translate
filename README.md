### 项目简介

用于从 Unity 资源文件中导出/回填 `TextAsset` 文本，以及对文本进行 AES-ECB(Base64) 加/解密的实用脚本。基于 `UnityPy` 与 `PyCryptodome`。

### 目录结构（关键）

- `assets/resources.assets`: 原始 Unity 资源文件
- `assets_unpacked/`: 由导出功能生成的文本目录
- `ZH/`: 与加/解密脚本配合使用的输入目录
- `new_ZH_encrypted/`: 与加/解密脚本配合使用的输出目录
- `new_ZH/`: 与导入功能配合使用的文本目录
- `unpack.py`: 导出/导入 Unity `TextAsset`
- `main.py`: 文本 AES-ECB(Base64) 加/解密
- `key.py`: AES 密钥（32 字节）

### 环境要求

- Python >= 3.9
- 依赖：`unitypy`, `pycryptodome`

安装方式（任选其一）：

```bash
# 使用 pip（推荐先创建虚拟环境）
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install unitypy pycryptodome
```

```bash
# 使用 uv（如已安装）
uv sync
```

### 使用方法

- 导出 Unity 文本（从 `assets/resources.assets` 到 `assets_unpacked/`）

```bash
python unpack.py --mode export --src assets/resources.assets --out-dir assets_unpacked
```

- 导入文本回资源文件（从 `new_ZH/` 读取同名 `.txt` 覆盖 `TextAsset`）

```bash
# 输出为新文件（默认文件名 resources_patched.assets）
python unpack.py --mode import --src assets/resources.assets --in-dir new_ZH --output assets/resources_patched.assets

# 或原地覆盖并在首次运行时生成 .bak 备份
python unpack.py --mode import --src assets/resources.assets --in-place --backup
```

- 文本加/解密（固定读取 `ZH/`，输出到 `new_ZH_encrypted/`）

```bash
# 解密：将 ZH/ 中的 Base64(AES-ECB, PKCS7) 文本解密为明文到 new_ZH_encrypted/
python main.py --mode decrypt

# 加密：将 ZH/ 中的明文加密为 Base64(AES-ECB, PKCS7) 到 new_ZH_encrypted/
python main.py --mode encrypt
```

### 重要说明

- `key.py` 中的 `KEY` 为 32 字节 AES-ECB 密钥，需自行确认合法来源与使用范围。
- `unpack.py` 读写文本均使用 UTF-8（含 `surrogateescape`），可最大程度保留不可解码字节。
- 使用 `--in-place` 覆盖资源文件时，强烈建议加上 `--backup` 以避免不可逆修改。

### 致谢

- UnityPy
- PyCryptodome


