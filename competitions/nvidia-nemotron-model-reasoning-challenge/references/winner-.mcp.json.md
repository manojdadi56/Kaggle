# Winner solution — `.mcp.json`

- **source repo:** https://github.com/tonghuikang/nemotron (tonghuikang, Open Progress Prize, LB ~0.85)
- **file:** .mcp.json
- **chars:** 321

---

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ],
      "env": {
        "PUPPETEER_LAUNCH_OPTIONS": "{\"defaultViewport\": {\"width\": 1920, \"height\": 960}, \"args\": [\"--window-size=1920,960\"]}"
      }
    }
  }
}
```
