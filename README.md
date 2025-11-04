# カーセンサー在庫スクレイピング

オートボディ菅原のカーセンサー在庫情報を自動取得し、JSON形式で出力するスクレイパー。

## 🎯 概要

- カーセンサーの店舗ページから在庫情報を自動取得
- JSON形式で出力（WordPress連携対応）
- Render上で毎日自動実行
- robots.txt遵守、適切なアクセス間隔を確保

## 📋 必要要件

- Python 3.11以上
- pip
- Playwright（Chromiumブラウザを含む）

## 🚀 ローカルでの実行

### 1. セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/carsensor-scraper.git
cd carsensor-scraper

# 依存パッケージをインストール
pip install -r requirements.txt

# Playwrightのブラウザをインストール
playwright install chromium
```

### 2. 実行

```bash
python scraper.py
```

実行後、`data/carsensor_inventory.json` にデータが出力されます。

## ☁️ Renderへのデプロイ

このプロジェクトは**完全無料**でRenderにデプロイできます。

### クイックスタート

1. GitHubリポジトリを作成・プッシュ
2. [GitHub Personal Access Token](https://github.com/settings/tokens) を作成（`repo`スコープ）
3. [Render](https://render.com)でBlueprint経由でデプロイ
4. 環境変数 `GITHUB_TOKEN` を設定

**詳細な手順は [デプロイガイド](docks/DEPLOY.md) を参照してください。**

### データの取得方法

スクレイピング結果は自動的にGitHubリポジトリにプッシュされます。
以下のURLで取得可能：

```
https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json
```

JavaScriptでの取得例：
```javascript
fetch('https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 📄 出力フォーマット

```json
[
  {
    "name": "トヨタ カムリ",
    "year": "2023 (R05)",
    "mileage": "428 km",
    "engine_size": "2500 CC",
    "inspection": "2026 (R08) 年10月",
    "repair_history": "なし",
    "price": "350万円",
    "image_url": "https://cdn.carsensor.net/...",
    "detail_link": "https://www.carsensor.net/usedcar/..."
  }
]
```

## 🔧 カスタマイズ

### スクレイピング対象の変更

`scraper.py` の以下の定数を変更:

```python
SHOP_URL = "https://www.carsensor.net/shop/miyagi/326411001/stocklist/"
```

### リクエスト間隔の調整

```python
REQUEST_DELAY = 2  # 秒単位
```

### 出力先の変更

```python
OUTPUT_FILE = "data/carsensor_inventory.json"
```

## 🔌 WordPress連携

### プラグインでの使用

WordPressプラグイン「CarSensor Sync」（別途開発予定）を使用して、
GitHub Raw URLから在庫情報を取得し、サイト上に表示できます。

### 手動での使用

```php
$json_url = 'https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json';
$inventory = json_decode(file_get_contents($json_url), true);

foreach ($inventory as $car) {
    echo "<h3>{$car['name']}</h3>";
    echo "<p>価格: {$car['price']}</p>";
    // ...
}
```

## 📝 ログ

スクリプト実行時に標準出力にログが出力されます。
Renderのダッシュボードからログを確認できます。

## ⚠️ 注意事項

- スクレイピングはカーセンサーの利用規約とrobots.txtに従って実施してください
- アクセス頻度を適切に保ち、サーバーに負荷をかけないようにしてください
- HTMLの構造が変更された場合、セレクタの調整が必要になる可能性があります

## 🛠️ トラブルシューティング

### データが取得できない場合

1. カーセンサーのHTML構造が変更されていないか確認
2. `scraper.py` のCSSセレクタを実際のHTML構造に合わせて調整
3. ログを確認してエラー内容を特定

### セレクタの確認方法

1. ブラウザで対象ページを開く
2. 開発者ツール（F12）でHTML構造を確認
3. 必要な情報の要素のクラスやIDを特定
4. `scraper.py` のセレクタを更新

## 📄 ライセンス

MIT License

## 👤 作成者

オートボディ菅原

## 📅 更新履歴

- 2025-11-04: Playwrightへの移行（実際のHTML構造に対応した正しいセレクタを実装）
- 2024-11-04: 初回リリース
