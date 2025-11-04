# クイックスタートガイド 🚀

このガイドに従えば、5分でスクレイパーを実行できます！

## ステップ1: 依存関係のインストール

```bash
# 依存パッケージをインストール
pip install -r requirements.txt

# Playwrightのブラウザをインストール（初回のみ）
playwright install chromium
```

## ステップ2: 環境設定（初回のみ）

```bash
# .envファイルを作成
cp .env.example .env
```

**注意**: デフォルト設定のままで動作します。カスタマイズ不要です。

## ステップ3: 実行

```bash
python scraper.py
```

実行すると、以下のように進行します:

```
2025-11-04 18:00:00 - INFO - Starting scraping process...
2025-11-04 18:00:00 - INFO - Fetching shop page: https://www.carsensor.net/...
2025-11-04 18:00:02 - INFO - Found 10 car links
2025-11-04 18:00:02 - INFO - Processing car 1/10
2025-11-04 18:00:03 - INFO - Extracted: トヨタ カムリ - 350万円
...
2025-11-04 18:00:30 - INFO - Successfully scraped 10 cars
2025-11-04 18:00:30 - INFO - Data saved to data/carsensor_inventory.json
2025-11-04 18:00:30 - INFO - Data saved successfully. Run 'git add/commit/push' manually if needed.
2025-11-04 18:00:30 - INFO - Scraping completed in 28.45 seconds
```

## ステップ4: 結果の確認

```bash
# JSONファイルを確認
cat data/carsensor_inventory.json | python -m json.tool
```

## 完了！ 🎉

`data/carsensor_inventory.json` に在庫データが保存されました。

---

## 次のステップ

### データの活用

- **WordPressで使う**: JSONファイルをアップロードして`file_get_contents()`で読み込み
- **Webサイトで使う**: JavaScriptの`fetch()`でJSONを読み込み
- **Excelで分析**: JSONをCSVに変換して分析

### 定期実行の設定

毎日自動で実行したい場合:

**macOS/Linux:**
```bash
crontab -e
# 毎日18時に実行
0 18 * * * cd /path/to/carsenser-scraper && python3 scraper.py
```

**Windows:**
タスクスケジューラで設定

### 設定のカスタマイズ

`.env`ファイルを編集:

```bash
# 対象店舗を変更
SHOP_URL=https://www.carsensor.net/shop/都道府県/店舗ID/stocklist/

# リクエスト間隔を変更（秒単位）
REQUEST_DELAY=3

# 出力ファイル名を変更
OUTPUT_FILE=data/my_inventory.json
```

---

## トラブルシューティング

### Playwrightのエラー

```bash
playwright install chromium
```

### Pythonのバージョン

Python 3.11以上が必要です:

```bash
python --version
```

### その他の問題

詳細は [README.md](README.md) を参照してください。

---

## よくある質問

**Q: GitHubトークンは必要？**
A: ローカル実行では不要です。データは`data/`フォルダに保存されます。

**Q: 無料で使える？**
A: はい、完全無料です。

**Q: 商用利用できる？**
A: カーセンサーの利用規約を確認してください。個人利用を推奨します。

**Q: 他の店舗をスクレイピングしたい**
A: `.env`ファイルの`SHOP_URL`を変更してください。

**Q: クラウドで自動実行したい**
A: [DEPLOY.md](docks/DEPLOY.md) を参照してください（オプション）。

