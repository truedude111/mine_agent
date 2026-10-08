# 矿权日报 Agent 运行说明

数据全链路默认 `MINING_DATA=fixture`，不需要模型 API key，也不需要外网。

## 1. Docker（主流程审查）

```powershell
docker compose up --build
```

终端会打印一份 Markdown 简报，包含新闻摘要、储量数据、价格走势、风险提示和来源链接。

更换查询句子时临时加环境变量，不要改默认 compose：

```powershell
docker compose run --rm -e BRIEF_QUERY="给我生成一份关于 Pilbara 锂矿的今日简报" brief
```

不要把中文查询写进命令行参数。

## 2. 本机虚拟环境与 MCP 接入

在仓库根执行：

```powershell
powershell -File scripts/setup.ps1
```

脚本会：

1. 创建或复用 `.venv` 并安装 `requirements.txt`
2. 按本机绝对路径生成 `mcp-config.json` 与 `.cursor/mcp.json`

本地直接出简报：

```powershell
.venv\Scripts\python.exe -m agent
```

### Cursor

打开本仓库并重载窗口后，应看到三个服务已连接：

- `mining-news-mcp`
- `mineral-pdf-mcp`
- `lme-price-mcp`

桌面端里的模型只用于点工具。可分别调用 `search`、`extract_resources`、`get_price`，返回 JSON。

`extract_resources` 的 `pdf_url` 使用仓库内文件，例如：

`fixtures/pilbara-lithium.pdf`

或该文件的绝对路径。

### Claude Desktop

不要让脚本改 Claude Desktop 的用户配置。把生成的 `mcp-config.json` 里的 `mcpServers` 合并进本机 Claude Desktop 配置后重启即可。

## 3. 测试

```powershell
.venv\Scripts\python.exe -m pytest
```

pytest 同样走 fixture，不访问外网。
