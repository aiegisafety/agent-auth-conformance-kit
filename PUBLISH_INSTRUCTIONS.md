# 发布到 GitHub（aiegisafety / agent-auth-conformance-kit, Public）

我无法直接 push 到你的 GitHub（没有连接器，且首次推送需要你本机浏览器授权）。
下面是最省事的两种方式，二选一。

## 方式 A — 一键脚本（推荐）

1. 把整个 `agent-auth-conformance-kit` 文件夹放到 `C:\Users\neuwo\Documents\AiegisWorkspace\` 下。
2. 双击 `publish_to_github.bat`。
   - 装了 GitHub CLI（`gh`）的话：脚本会自动建库 + 推送，全程无需手动建库。
   - 没装 `gh`：脚本会先让你去 https://github.com/new 建一个**空的 public 库**
     （owner=aiegisafety，name=agent-auth-conformance-kit，**不要**勾选 README/license），
     然后回车自动 commit + push。
3. 首次 push 会弹浏览器，点 **Authorize git-credential-manager**（和你 aiegis-pea 一样的流程）。

## 方式 B — 手敲命令

```bat
cd /d C:\Users\neuwo\Documents\AiegisWorkspace\agent-auth-conformance-kit
git init -b main
git add .
git commit -m "AACP v0.1: agent authorization conformance kit (L2 reference)"
git remote add origin https://github.com/aiegisafety/agent-auth-conformance-kit.git
git push -u origin main
```
（同样需要先在 github.com/new 建空的 public 库。）

## 发布后建议（5 分钟）

- 仓库 Description 填：`Runnable conformance suite for the Agent Authorization Conformance Profile (AACP v0.1).`
- Topics 加：`ai-agent` `authorization` `governance` `conformance` `ai-safety` `audit`
- 确认 Actions 标签页 `conformance` workflow 跑绿（会在 3.10/3.11/3.12 上跑 14 个测试并上传 L2 报告）。
- README 顶部可加一个 CI 徽章：
  `![conformance](https://github.com/aiegisafety/agent-auth-conformance-kit/actions/workflows/conformance.yml/badge.svg)`

## 注意

- `publish_to_github.bat` 和本说明文件已在 `.gitignore` 中，不会被提交进仓库。
- 仓库内无真名、无邮箱、无密钥（已扫描）；署名用 AIEGIS / Aron。
