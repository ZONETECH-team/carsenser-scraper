# カーセンサー在庫スクレイピング 仕様書（Render + WordPressプラグイン連携 / 実店舗対応版）

## 🎯 目的
オートボディ菅原（カーセンサー店舗ページ: https://www.carsensor.net/shop/miyagi/326411001/stocklist/）の在庫情報を自動取得し、最新データをJSON形式で出力する。Render上で自動実行し、WordPressプラグインを通じてWebサイト上に在庫リストを自動表示する。

---

## ⚙️ 全体構成概要

| コンポーネント | 役割 |
|----------------|------|
| Python (Render) | カーセンサーから在庫情報をスクレイピングし、JSON出力。Render上で毎日自動実行。 |
| JSONファイル | 最新の在庫情報を保存するデータソース。WordPressが取得して表示に利用。 |
| WordPressプラグイン | RenderのJSONを取得し、Webサイトに在庫リストやカルーセルを生成・表示。 |

---

## 🧩 データ仕様

### 出力JSONフォーマット
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

### 各項目の説明
| キー | 内容 | 例 |
|------|------|----|
| `name` | 車名 | トヨタ カムリ |
| `year` | 年式 | 2023 (R05) |
| `mileage` | 走行距離 | 428 km |
| `engine_size` | 排気量 | 2500 CC |
| `inspection` | 車検有無 | 2026 (R08) 年10月 |
| `repair_history` | 修復歴 | なし |
| `price` | 価格 | 350万円 |
| `image_url` | 画像URL | https://～ |
| `detail_link` | 詳細ページURL | https://～ |

---

## 🏗️ Python実装仕様（Render側）

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.11以上 |
| 実行環境 | Render Web Service または Cron Job |
| ライブラリ | `requests`, `beautifulsoup4`, `lxml`, `json`, `time` |
| データ取得元 | https://www.carsensor.net/shop/miyagi/326411001/stocklist/ |
| 更新頻度 | 1日1回（cron設定: `0 9 * * *`） |
| 出力形式 | JSON（UTF-8） |
| 出力先 | `/data/carsensor_inventory.json` |
| 出力方法 | `json.dump()` を使用、インデント付き整形 |

### 処理フロー
1. カーセンサー店舗ページ（在庫リスト）から各車両詳細リンクを取得
2. 各車両ページをアクセスし、主要情報をスクレイピング
3. 必要項目を抽出・整形しリスト化
4. JSONファイル（`carsensor_inventory.json`）に書き出し
5. Renderが定期的にスクリプトを実行し、自動更新

---

## 🧱 ディレクトリ構成（Render側）
```bash
📁 /app
├── scraper.py               # メインスクリプト
├── requirements.txt         # 依存ライブラリ
├── render.yaml              # Render設定（ビルド・実行・スケジュール）
└── data/
    └── carsensor_inventory.json  # 出力ファイル
```

---

## 🔌 WordPressプラグイン仕様

| 項目 | 内容 |
|------|------|
| プラグイン名 | CarSensor Sync |
| 機能 | RenderのJSONを取得し、WordPress上に在庫を表示 |
| 表示方法 | ショートコード `[carsensor_list]` またはブロックエディタ対応 |
| 管理画面 | JSON URLとキャッシュ期間を設定できるオプションページ |
| キャッシュ | `transient` APIで12時間保持（再取得防止） |
| 出力形式 | リストまたはカルーセル（Swiper.js対応予定） |

---

## ⚖️ 非機能要件
| 区分 | 内容 |
|------|------|
| 安全性 | robots.txt遵守、アクセス間隔を2秒以上確保 |
| パフォーマンス | 100件の車両情報を2分以内に取得可能 |
| 可搬性 | ローカル・Render両方で動作可能 |
| 保守性 | BeautifulSoup構造変更時の修正が容易 |
| 拡張性 | JSON項目追加やWordPress側拡張に対応可能 |

---

## 📅 今後の拡張計画
- WordPress REST APIとの自動同期
- 在庫の差分検出（追加・削除・価格変更）
- Slack／LINE通知機能
- 管理画面から「今すぐ更新」ボタンの実装
- カルーセルUI（Swiper.js）標準搭載

---

## ✅ 成果物一覧
| ファイル | 説明 |
|-----------|------|
| `scraper.py` | スクレイピング実行スクリプト |
| `requirements.txt` | 依存ライブラリ定義 |
| `render.yaml` | Render実行設定（自動ビルド・スケジュール含む） |
| `data/carsensor_inventory.json` | 最新在庫データJSON |
| `carsensor-sync` | WordPressプラグイン（PHP）フォルダ |
| `README.md` | 手順・運用ガイド |
