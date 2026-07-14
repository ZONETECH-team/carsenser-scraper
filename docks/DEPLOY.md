# Renderへのデプロイ手順（オプション）

> ⚠️ **注意**: このドキュメントはオプションです。
> 
> **ローカルで手動実行する場合は、このデプロイ作業は不要です。**
> 
> Renderでのクラウド自動実行が必要な場合のみ、以下の手順を実施してください。

このガイドでは、カーセンサースクレイパーをRenderのCron Jobとして無料でデプロイする方法を説明します。

## 📌 ローカル実行との違い

| 項目 | ローカル実行 | Render実行 |
|------|------------|-----------|
| 実行方法 | 手動で`python scraper.py` | 自動（スケジュール実行） |
| PC稼働 | 実行時のみ必要 | 不要 |
| データ保存 | ローカルファイル | GitHubに自動プッシュ |
| コスト | 無料 | 無料 |
| セットアップ | 簡単 | やや複雑 |

**推奨**: まずはローカル実行で動作確認してから、必要に応じてRenderへ移行してください。

## 前提条件

- GitHubアカウント
- Renderアカウント（無料）
- このリポジトリがGitHubにプッシュされていること
- ローカル実行で動作確認済みであること

## アーキテクチャ

```
Render Cron Job (毎日実行)
    ↓
スクレイピング実行
    ↓
data/carsensor_inventory.json に保存
    ↓
GitHubにコミット＆プッシュ
    ↓
GitHub Pages または Raw URL で公開
```

## 手順

### 1. GitHub Personal Access Token (PAT) の作成

Render上のスクリプトがGitHubにプッシュできるようにトークンを作成します。

1. GitHubにログイン
2. 右上のプロフィールアイコン → **Settings**
3. 左サイドバー最下部の **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**
6. トークンの設定：
   - **Note**: `Render Carsensor Scraper`
   - **Expiration**: `No expiration` または適切な期限
   - **Select scopes**:
     - ✅ `repo` (フルアクセス)
7. **Generate token** をクリック
8. **トークンをコピーして安全な場所に保存**（二度と表示されません）

### 2. Renderへのデプロイ

#### Option A: Blueprint経由（推奨）

1. [Render Dashboard](https://dashboard.render.com/) にログイン
2. **New +** → **Blueprint**
3. GitHubリポジトリを接続（初回のみ）
   - **Connect account** をクリック
   - GitHubで認証
   - このリポジトリ（`ZONETECH-team/carsenser-scraper`）へのアクセスを許可
4. リポジトリを選択
5. **render.yaml** が自動検出される
6. **Apply** をクリック

#### Option B: 手動作成

1. [Render Dashboard](https://dashboard.render.com/) にログイン
2. **New +** → **Cron Job**
3. GitHubリポジトリを接続・選択
4. 設定：
   - **Name**: `carsensor-scraper`
   - **Environment**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Command**: `python scraper.py`
   - **Schedule**: `0 9 * * *` (毎日9時UTC = 日本時間18時)

### 3. 環境変数の設定

Renderのダッシュボードで環境変数を設定します。

1. デプロイした Cron Job を開く
2. **Environment** タブをクリック
3. 以下の環境変数を追加：

#### 必須の環境変数

| Key | Value | 説明 |
|-----|-------|------|
| `GITHUB_TOKEN` | `ghp_xxxxx...` | 手順1で作成したPAT |
| `PYTHON_VERSION` | `3.11.0` | Python バージョン |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/render/.cache/ms-playwright` | Playwright キャッシュパス |
| `AUTO_GIT_PUSH` | `true` | 自動Git Pushを有効化 |

#### GitHub関連の環境変数（オプション）

| Key | Value | デフォルト値 |
|-----|-------|-------------|
| `GITHUB_USER_NAME` | `Carsensor Scraper Bot` | `Carsensor Scraper` |
| `GITHUB_USER_EMAIL` | `bot@example.com` | `scraper@example.com` |

#### スクレイピング設定の環境変数（オプション）

| Key | Value | デフォルト値 |
|-----|-------|-------------|
| `BASE_URL` | `https://www.carsensor.net` | `https://www.carsensor.net` |
| `SHOP_URL` | 店舗ページURL | `https://www.carsensor.net/shop/miyagi/326411001/stocklist/` |
| `OUTPUT_FILE` | `data/carsensor_inventory.json` | `data/carsensor_inventory.json` |
| `REQUEST_DELAY` | `2` | `2` |
| `PAGE_TIMEOUT` | `30000` | `30000` |
| `USER_AGENT` | カスタムUA | デフォルトのChrome UA |

**注**: 
- `AUTO_GIT_PUSH=true` を設定することで、実行後に自動的にGitHubへプッシュします
- デフォルト値で問題ない場合は、オプションの環境変数は設定不要です

4. **Save Changes** をクリック

### 4. 初回デプロイの確認

1. **Manual Jobs** → **Trigger Job** で手動実行して動作確認
2. ログを確認してエラーがないかチェック
3. GitHubリポジトリに `data/carsensor_inventory.json` がプッシュされているか確認

## データの取得方法

スクレイピングしたデータは以下のURLで取得できます：

### GitHub Raw URL（推奨）

```
https://raw.githubusercontent.com/ZONETECH-team/carsenser-scraper/refs/heads/main/data/carsensor_inventory.json
```

フロントエンドアプリケーションから直接このURLをfetchできます：

```javascript
fetch('https://raw.githubusercontent.com/ZONETECH-team/carsenser-scraper/refs/heads/main/data/carsensor_inventory.json')
  .then(response => response.json())
  .then(data => {
    console.log('在庫データ:', data);
  });
```

### GitHub Pages（オプション）

より高速なアクセスが必要な場合、GitHub Pagesを有効化できます：

1. GitHubリポジトリの **Settings** → **Pages**
2. **Source**: `main` ブランチ
3. **Folder**: `/`（root）
4. **Save**
5. データURL: `https://zonehisa.github.io/carsenser-scraper/data/carsensor_inventory.json`

## 実行スケジュール

- **Cron式**: `0 9 * * *`
- **UTC時刻**: 毎日 09:00
- **日本時刻**: 毎日 18:00

スケジュールを変更したい場合は、`render.yaml` の `schedule` フィールドを編集してください。

## トラブルシューティング

### Playwrightがブラウザを起動できない

ログに以下のようなエラーが表示される場合：
```
Error: browserType.launch: Executable doesn't exist
```

**解決策**: Build Commandに `playwright install-deps chromium` が含まれているか確認

### GitHubへのプッシュが失敗する

ログに以下のようなエラーが表示される場合：
```
Git command failed: Permission denied
```

**解決策**:
1. `GITHUB_TOKEN` が正しく設定されているか確認
2. トークンに `repo` スコープが付与されているか確認
3. トークンが期限切れでないか確認

### データが更新されない

**確認項目**:
1. Render上でCron Jobが正常に実行されているか（Logsタブで確認）
2. GitHubリポジトリの最終コミット日時を確認
3. ブラウザのキャッシュをクリアして再読み込み

### Cron Jobが実行されない

**確認項目**:
1. Renderの無料プランでは、Cron Jobの実行が遅延することがあります
2. **Manual Jobs** タブから手動で実行して動作確認
3. スケジュール設定が正しいか確認

## コスト

このセットアップは**完全無料**です：

- ✅ Render Free Plan: Cron Jobは無料
- ✅ GitHub: リポジトリとPages無料
- ✅ Playwright: オープンソース

## セキュリティ注意事項

1. **GitHub Token を公開しない**
   - `.env` ファイルは `.gitignore` に追加済み
   - Render環境変数は暗号化されて保存されます

2. **スクレイピングのマナー**
   - リクエスト間隔は2秒に設定済み
   - 過度なアクセスはサーバーに負荷をかけます

3. **利用規約の遵守**
   - カーセンサーの利用規約を確認してください
   - 個人利用の範囲で使用することを推奨

## 参考リンク

- [Render Cron Jobs ドキュメント](https://render.com/docs/cronjobs)
- [GitHub Personal Access Tokens](https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [Playwright ドキュメント](https://playwright.dev/python/)
