# カーセンサー在庫スクレイピング

オートボディ菅原のカーセンサー在庫情報を自動取得し、JSON形式で出力するスクレイパー。

## 🎯 概要

- カーセンサーの店舗ページから在庫情報を自動取得
- JSON形式で出力（WordPress連携対応）
- ローカル環境で手動実行
- robots.txt遵守、適切なアクセス間隔を確保

## 📋 必要要件

- Python 3.11以上
- pip
- Playwright（Chromiumブラウザを含む）

## ⚡ クイックスタート

**初めての方は [クイックスタートガイド](QUICKSTART.md) をご覧ください！**

5分で実行できるステップバイステップガイドです。

## 🚀 セットアップと実行

### 1. 依存パッケージのインストール

```bash
# リポジトリをクローン（初回のみ）
git clone https://github.com/yourusername/carsensor-scraper.git
cd carsensor-scraper

# 依存パッケージをインストール
pip install -r requirements.txt

# Playwrightのブラウザをインストール
playwright install chromium
```

### 2. 環境変数の設定

```bash
# .envファイルを作成（初回のみ）
cp .env.example .env

# 必要に応じて編集（デフォルトのままでOK）
# vim .env または nano .env
```

### 3. 実行

```bash
python scraper.py
```

**実行後**: `data/carsensor_inventory.json` にデータが出力されます。

### 4. データの確認

```bash
# JSON形式で表示
cat data/carsensor_inventory.json | python -m json.tool

# または、ファイルを直接開く
open data/carsensor_inventory.json
```

## 📅 定期実行の設定（オプション）

### macOS/Linuxの場合（cron）

```bash
# crontabを編集
crontab -e

# 毎日18時に実行する例
0 18 * * * cd /path/to/carsenser-scraper && /usr/local/bin/python3 scraper.py >> logs/scraper.log 2>&1
```

### Windowsの場合（タスクスケジューラ）

1. 「タスクスケジューラ」を開く
2. 「基本タスクの作成」を選択
3. トリガー: 毎日、時刻を指定
4. 操作: `python.exe scraper.py` を実行

## ☁️ クラウドでの自動実行（オプション）

ローカルPCを常時起動できない場合は、Renderで自動実行できます。

**詳細な手順は [デプロイガイド](docks/DEPLOY.md) を参照してください。**

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

`.env` ファイルを編集することで、動作をカスタマイズできます。

### 主な設定項目

#### スクレイピング対象店舗の変更

他の店舗をスクレイピングする場合:

```bash
# .env
SHOP_URL=https://www.carsensor.net/shop/都道府県/店舗ID/stocklist/
```

#### リクエスト間隔の調整

サーバーへの負荷を考慮して調整:

```bash
# .env
REQUEST_DELAY=2  # 秒単位（2秒以上推奨）
```

#### 出力ファイルの変更

```bash
# .env
OUTPUT_FILE=data/my_inventory.json
```

#### 自動Git Push（オプション）

実行後に自動的にGitHubへプッシュする場合:

```bash
# .env
AUTO_GIT_PUSH=true
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_USER_NAME=Bot Name
GITHUB_USER_EMAIL=bot@example.com
```

**通常はfalse（手動）で問題ありません。**

## 🔌 データの活用

### WordPressでの使用

JSONファイルをWordPressで読み込む例:

```php
// ローカルファイルから読み込む
$json_path = '/path/to/carsensor_inventory.json';
$inventory = json_decode(file_get_contents($json_path), true);

foreach ($inventory as $car) {
    echo "<div class='car-item'>";
    echo "<h3>{$car['name']}</h3>";
    echo "<p>価格: {$car['price']}</p>";
    echo "<p>走行距離: {$car['mileage']}</p>";
    echo "</div>";
}
```

### JavaScriptでの使用

```javascript
// ローカルサーバーまたはGitHub経由
fetch('data/carsensor_inventory.json')
  .then(response => response.json())
  .then(data => {
    data.forEach(car => {
      console.log(`${car.name} - ${car.price}`);
    });
  });
```

## 📝 ログとデバッグ

スクリプト実行時に標準出力にログが出力されます。

```bash
# 通常実行
python scraper.py

# ログをファイルに保存
python scraper.py > logs/scraper_$(date +%Y%m%d).log 2>&1

# リアルタイムでログを確認しながら保存
python scraper.py 2>&1 | tee logs/scraper.log
```

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

- 2025-11-04: ローカル実行運用に変更、自動Git Pushをオプション化
- 2025-11-04: .env対応、環境変数からの設定読み込み
- 2025-11-04: Playwrightへの移行（実際のHTML構造に対応した正しいセレクタを実装）
- 2024-11-04: 初回リリース
