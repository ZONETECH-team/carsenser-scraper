#!/usr/bin/env python3
"""
カーセンサー在庫スクレイピングスクリプト (Playwright版)
オートボディ菅原の在庫情報を取得しJSON出力
"""

import json
import time
import logging
import re
import os
import subprocess
from typing import List, Dict, Optional
from urllib.parse import urljoin
from datetime import datetime

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定数（環境変数から読み込み、デフォルト値を設定）
BASE_URL = os.getenv('BASE_URL', 'https://www.carsensor.net')
SHOP_URL = os.getenv('SHOP_URL', 'https://www.carsensor.net/shop/miyagi/326411001/stocklist/')
OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'data/carsensor_inventory.json')
REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', '2'))  # リクエスト間隔（秒）
PAGE_TIMEOUT = int(os.getenv('PAGE_TIMEOUT', '30000'))  # ページ読み込みタイムアウト（ミリ秒）

# User-Agent
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


def extract_car_links(page: Page) -> List[str]:
    """
    在庫リストページから各車両の詳細ページURLを抽出

    Args:
        page: Playwrightページオブジェクト

    Returns:
        車両詳細ページURLのリスト
    """
    links = []

    try:
        # 車両リンクを抽出
        car_items = page.query_selector_all('a[href*="/usedcar/detail/"]')

        for item in car_items:
            href = item.get_attribute('href')
            if href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in links:
                    links.append(full_url)

        logger.info(f"Found {len(links)} car links")
        return links

    except Exception as e:
        logger.error(f"Failed to extract car links: {e}")
        return []


def extract_table_value(page: Page, label: str) -> str:
    """
    テーブルから特定のラベルに対応する値を抽出

    Args:
        page: Playwrightページオブジェクト
        label: 検索するラベル（例: "年式", "走行距離"）

    Returns:
        抽出された値（見つからない場合は空文字列）
    """
    try:
        # すべてのthタグを取得
        th_elements = page.query_selector_all('th.defaultTable__head')

        for th in th_elements:
            th_text = th.inner_text()
            if label in th_text:
                # 同じ行のtd要素を取得
                td = th.evaluate('el => el.parentElement?.querySelector("td.defaultTable__description")')
                if td:
                    # tdのテキストを取得
                    value = th.evaluate('el => el.parentElement?.querySelector("td.defaultTable__description")?.innerText')
                    if value:
                        return value.strip()
        return ""

    except Exception as e:
        logger.debug(f"Failed to extract table value for '{label}': {e}")
        return ""


def extract_car_details(page: Page, url: str) -> Optional[Dict[str, str]]:
    """
    車両詳細ページから情報を抽出

    Args:
        page: Playwrightページオブジェクト
        url: 車両詳細ページのURL

    Returns:
        車両情報の辞書、失敗時はNone
    """
    try:
        logger.info(f"Fetching: {url}")

        # ページにアクセス
        page.goto(url, wait_until='networkidle', timeout=PAGE_TIMEOUT)

        # ページが完全に読み込まれるまで少し待機
        page.wait_for_timeout(1000)

        # 車名を抽出
        name = "不明"
        description = ""
        try:
            h1_element = page.query_selector('h1')
            if h1_element:
                full_name = h1_element.inner_text().strip()
                # \nで分割して、最初の部分をname、残りをdescriptionに
                if '\n' in full_name:
                    parts = full_name.split('\n', 1)
                    name = parts[0].strip()
                    description = parts[1].strip() if len(parts) > 1 else ""
                else:
                    name = full_name
        except:
            pass

        # 価格を抽出
        price = ""
        try:
            price_element = page.query_selector('p.basePrice__price')
            if price_element:
                price_text = price_element.inner_text().strip()
                # 価格を整形（改行を削除して統一）
                price = re.sub(r'\s+', '', price_text)
        except:
            pass

        # テーブル情報を抽出
        year = extract_table_value(page, '年式')
        mileage = extract_table_value(page, '走行距離')
        engine_size = extract_table_value(page, '排気量')
        inspection = extract_table_value(page, '車検')
        repair_history = extract_table_value(page, '修復歴')

        # メイン画像URLを抽出
        image_url = ""
        try:
            img_element = page.query_selector('img[class*="main"]')
            if img_element:
                image_url = img_element.get_attribute('src') or ''
        except:
            pass

        car_data = {
            "name": name,
            "description": description,
            "year": year,
            "mileage": mileage,
            "engine_size": engine_size,
            "inspection": inspection,
            "repair_history": repair_history,
            "price": price,
            "image_url": image_url,
            "detail_link": url
        }

        logger.info(f"Extracted: {name} - {price}")
        return car_data

    except PlaywrightTimeout:
        logger.error(f"Timeout loading page: {url}")
        return None
    except Exception as e:
        logger.error(f"Failed to extract details from {url}: {e}")
        return None


def scrape_inventory() -> List[Dict[str, str]]:
    """
    在庫リスト全体をスクレイピング

    Returns:
        車両情報のリスト
    """
    logger.info("Starting scraping process...")
    inventory = []

    with sync_playwright() as p:
        # ブラウザを起動
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        try:
            # 在庫リストページにアクセス
            logger.info(f"Fetching shop page: {SHOP_URL}")
            page.goto(SHOP_URL, wait_until='networkidle', timeout=PAGE_TIMEOUT)
            page.wait_for_timeout(2000)

            # 車両リンクを抽出
            car_links = extract_car_links(page)
            if not car_links:
                logger.warning("No car links found")
                return []

            # 各車両の詳細を取得
            for i, link in enumerate(car_links, 1):
                logger.info(f"Processing car {i}/{len(car_links)}")

                car_data = extract_car_details(page, link)
                if car_data:
                    inventory.append(car_data)

                # サーバーに負荷をかけないよう待機
                if i < len(car_links):
                    time.sleep(REQUEST_DELAY)

            logger.info(f"Successfully scraped {len(inventory)} cars")

        except PlaywrightTimeout:
            logger.error("Timeout loading shop page")
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        finally:
            browser.close()

    return inventory


def save_to_json(data: List[Dict[str, str]], filepath: str) -> bool:
    """
    データをJSON形式で保存

    Args:
        data: 保存するデータ
        filepath: 保存先ファイルパス

    Returns:
        成功時True、失敗時False
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save data: {e}")
        return False


def git_commit_and_push() -> bool:
    """
    データファイルをGitにコミット＆プッシュ

    環境変数:
        GITHUB_TOKEN: GitHub Personal Access Token (必須)
        GITHUB_USER_NAME: Gitユーザー名 (オプション)
        GITHUB_USER_EMAIL: Gitメールアドレス (オプション)

    Returns:
        成功時True、失敗時False
    """
    try:
        # GitHub Tokenの確認
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            logger.warning("GITHUB_TOKEN not set. Skipping git push.")
            return False

        # Git設定
        git_user = os.getenv('GITHUB_USER_NAME', 'Carsensor Scraper')
        git_email = os.getenv('GITHUB_USER_EMAIL', 'scraper@example.com')

        logger.info("Configuring Git...")
        subprocess.run(['git', 'config', 'user.name', git_user], check=True)
        subprocess.run(['git', 'config', 'user.email', git_email], check=True)

        # ファイルを追加
        logger.info(f"Adding {OUTPUT_FILE}...")
        subprocess.run(['git', 'add', OUTPUT_FILE], check=True)

        # 変更があるか確認
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout.strip():
            logger.info("No changes to commit.")
            return True

        # コミット
        commit_message = f"Update inventory data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        logger.info(f"Committing: {commit_message}")
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # プッシュ（認証情報をURLに埋め込む）
        logger.info("Pushing to GitHub...")
        # リモートURLを取得
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()

        # HTTPSの場合、トークンを埋め込む
        if remote_url.startswith('https://'):
            # https://github.com/user/repo.git -> https://token@github.com/user/repo.git
            auth_url = remote_url.replace('https://', f'https://{github_token}@')
            subprocess.run(['git', 'push', auth_url, 'HEAD'], check=True)
        else:
            # SSH URLの場合はそのままプッシュ
            subprocess.run(['git', 'push'], check=True)

        logger.info("Successfully pushed to GitHub!")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to push to GitHub: {e}")
        return False


def main():
    """メイン処理"""
    start_time = time.time()

    # スクレイピング実行
    inventory = scrape_inventory()

    # JSON保存
    if inventory:
        if not save_to_json(inventory, OUTPUT_FILE):
            logger.error("Failed to save JSON file")
            return 1

        # GitHubにプッシュ（環境変数で有効化した場合のみ）
        auto_push = os.getenv('AUTO_GIT_PUSH', 'false').lower() in ('true', '1', 'yes')
        if auto_push:
            logger.info("AUTO_GIT_PUSH is enabled. Pushing to GitHub...")
            git_commit_and_push()
        else:
            logger.info("Data saved successfully. Run 'git add/commit/push' manually if needed.")

        logger.info(f"Scraping completed in {time.time() - start_time:.2f} seconds")
    else:
        logger.error("No data to save")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
