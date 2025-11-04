# WordPress連携ガイド

GitHubに公開されたJSONデータをWordPress側でfetchして表示する方法を説明します。

## 🌐 JSONデータのURL

スクレイパーを実行してGitHubにプッシュすると、以下のURLでデータが公開されます：

```
https://raw.githubusercontent.com/あなたのユーザー名/carsenser-scraper/main/data/carsensor_inventory.json
```

**例:**
```
https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json
```

## 📝 WordPress実装方法

### 方法1: ショートコード（推奨）

テーマの`functions.php`に追加:

```php
<?php
/**
 * カーセンサー在庫表示ショートコード
 * 使い方: [carsensor_inventory]
 */
function carsensor_inventory_shortcode($atts) {
    // 属性のデフォルト値
    $atts = shortcode_atts(array(
        'limit' => 10,  // 表示件数
        'cache' => 3600,  // キャッシュ時間（秒）
    ), $atts);
    
    // JSONデータのURL（自分のリポジトリに変更）
    $json_url = 'https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json';
    
    // キャッシュキー
    $cache_key = 'carsensor_inventory_' . md5($json_url);
    
    // キャッシュから取得を試みる
    $inventory = get_transient($cache_key);
    
    if (false === $inventory) {
        // キャッシュがない場合、JSONを取得
        $response = wp_remote_get($json_url, array(
            'timeout' => 15,
            'sslverify' => true,
        ));
        
        if (is_wp_error($response)) {
            return '<p class="error">在庫情報の取得に失敗しました。</p>';
        }
        
        $body = wp_remote_retrieve_body($response);
        $inventory = json_decode($body, true);
        
        if (empty($inventory)) {
            return '<p class="error">在庫データが見つかりません。</p>';
        }
        
        // キャッシュに保存
        set_transient($cache_key, $inventory, $atts['cache']);
    }
    
    // 表示件数を制限
    $inventory = array_slice($inventory, 0, $atts['limit']);
    
    // HTML出力を開始
    ob_start();
    ?>
    
    <div class="carsensor-inventory">
        <?php foreach ($inventory as $car): ?>
            <div class="car-item">
                <?php if (!empty($car['image_url'])): ?>
                    <div class="car-image">
                        <a href="<?php echo esc_url($car['detail_link']); ?>" target="_blank">
                            <img src="<?php echo esc_url($car['image_url']); ?>" 
                                 alt="<?php echo esc_attr($car['name']); ?>"
                                 loading="lazy">
                        </a>
                    </div>
                <?php endif; ?>
                
                <div class="car-details">
                    <h3 class="car-name">
                        <a href="<?php echo esc_url($car['detail_link']); ?>" target="_blank">
                            <?php echo esc_html($car['name']); ?>
                        </a>
                    </h3>
                    
                    <div class="car-specs">
                        <?php if (!empty($car['year'])): ?>
                            <span class="spec-item">
                                <strong>年式:</strong> <?php echo esc_html($car['year']); ?>
                            </span>
                        <?php endif; ?>
                        
                        <?php if (!empty($car['mileage'])): ?>
                            <span class="spec-item">
                                <strong>走行距離:</strong> <?php echo esc_html($car['mileage']); ?>
                            </span>
                        <?php endif; ?>
                        
                        <?php if (!empty($car['engine_size'])): ?>
                            <span class="spec-item">
                                <strong>排気量:</strong> <?php echo esc_html($car['engine_size']); ?>
                            </span>
                        <?php endif; ?>
                        
                        <?php if (!empty($car['inspection'])): ?>
                            <span class="spec-item">
                                <strong>車検:</strong> <?php echo esc_html($car['inspection']); ?>
                            </span>
                        <?php endif; ?>
                        
                        <?php if (!empty($car['repair_history'])): ?>
                            <span class="spec-item">
                                <strong>修復歴:</strong> <?php echo esc_html($car['repair_history']); ?>
                            </span>
                        <?php endif; ?>
                    </div>
                    
                    <?php if (!empty($car['price'])): ?>
                        <div class="car-price">
                            <?php echo esc_html($car['price']); ?>
                        </div>
                    <?php endif; ?>
                    
                    <div class="car-link">
                        <a href="<?php echo esc_url($car['detail_link']); ?>" 
                           target="_blank" 
                           rel="noopener"
                           class="btn-detail">
                            詳細を見る
                        </a>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>
    
    <style>
        .carsensor-inventory {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .car-item {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            transition: box-shadow 0.3s;
        }
        
        .car-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .car-image img {
            width: 100%;
            height: 200px;
            object-fit: cover;
        }
        
        .car-details {
            padding: 15px;
        }
        
        .car-name {
            margin: 0 0 10px 0;
            font-size: 18px;
        }
        
        .car-name a {
            color: #333;
            text-decoration: none;
        }
        
        .car-name a:hover {
            color: #007bff;
        }
        
        .car-specs {
            display: flex;
            flex-direction: column;
            gap: 5px;
            margin-bottom: 15px;
            font-size: 14px;
            color: #666;
        }
        
        .spec-item {
            display: block;
        }
        
        .car-price {
            font-size: 24px;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 15px;
        }
        
        .btn-detail {
            display: inline-block;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background 0.3s;
        }
        
        .btn-detail:hover {
            background: #0056b3;
            color: white;
        }
        
        .error {
            padding: 15px;
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
        }
    </style>
    
    <?php
    return ob_get_clean();
}
add_shortcode('carsensor_inventory', 'carsensor_inventory_shortcode');
```

#### 使い方

固定ページや投稿に以下のショートコードを追加:

```
[carsensor_inventory]
```

オプション付き:
```
[carsensor_inventory limit="20" cache="7200"]
```

- `limit`: 表示件数（デフォルト: 10）
- `cache`: キャッシュ時間（秒、デフォルト: 3600 = 1時間）

---

### 方法2: テンプレートファイルに直接記述

`page-inventory.php`などのテンプレートファイルを作成:

```php
<?php
/*
Template Name: 在庫一覧
*/

get_header();

// JSONデータのURL（自分のリポジトリに変更）
$json_url = 'https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json';

// キャッシュから取得
$cache_key = 'carsensor_inventory_data';
$inventory = get_transient($cache_key);

if (false === $inventory) {
    $response = wp_remote_get($json_url);
    
    if (!is_wp_error($response)) {
        $body = wp_remote_retrieve_body($response);
        $inventory = json_decode($body, true);
        
        // 1時間キャッシュ
        set_transient($cache_key, $inventory, 3600);
    }
}
?>

<div class="inventory-page">
    <h1>在庫車両一覧</h1>
    
    <?php if (!empty($inventory)): ?>
        <div class="car-grid">
            <?php foreach ($inventory as $car): ?>
                <div class="car-card">
                    <img src="<?php echo esc_url($car['image_url']); ?>" 
                         alt="<?php echo esc_attr($car['name']); ?>">
                    <h2><?php echo esc_html($car['name']); ?></h2>
                    <p class="price"><?php echo esc_html($car['price']); ?></p>
                    <a href="<?php echo esc_url($car['detail_link']); ?>" 
                       target="_blank">詳細を見る</a>
                </div>
            <?php endforeach; ?>
        </div>
    <?php else: ?>
        <p>在庫情報が見つかりません。</p>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
```

---

### 方法3: JavaScript（Ajax）で動的読み込み

```html
<!-- HTMLに配置 -->
<div id="car-inventory"></div>

<script>
// GitHub Raw URLからJSONを取得
fetch('https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json')
  .then(response => response.json())
  .then(inventory => {
    const container = document.getElementById('car-inventory');
    
    inventory.forEach(car => {
      const carElement = `
        <div class="car-item">
          <img src="${car.image_url}" alt="${car.name}">
          <h3>${car.name}</h3>
          <p class="price">${car.price}</p>
          <p>年式: ${car.year}</p>
          <p>走行距離: ${car.mileage}</p>
          <a href="${car.detail_link}" target="_blank">詳細を見る</a>
        </div>
      `;
      container.innerHTML += carElement;
    });
  })
  .catch(error => {
    console.error('在庫データの取得に失敗:', error);
    document.getElementById('car-inventory').innerHTML = 
      '<p>在庫情報の取得に失敗しました。</p>';
  });
</script>
```

---

## 🔄 キャッシュのクリア

データを更新した後、WordPressのキャッシュをクリアする方法:

### 方法1: プラグイン

WP-CLIを使用:
```bash
wp transient delete carsensor_inventory_data
```

### 方法2: functions.phpに追加

管理画面からキャッシュクリアボタンを追加:

```php
<?php
// 管理画面にキャッシュクリアボタンを追加
add_action('admin_bar_menu', 'add_clear_cache_button', 100);
function add_clear_cache_button($wp_admin_bar) {
    if (!current_user_can('manage_options')) {
        return;
    }
    
    $wp_admin_bar->add_node(array(
        'id' => 'clear_car_cache',
        'title' => 'キャッシュクリア',
        'href' => admin_url('admin-post.php?action=clear_car_cache'),
    ));
}

add_action('admin_post_clear_car_cache', 'clear_car_cache');
function clear_car_cache() {
    delete_transient('carsensor_inventory_' . md5('https://raw.githubusercontent.com/zonehisa/carsenser-scraper/main/data/carsensor_inventory.json'));
    
    wp_redirect(wp_get_referer());
    exit;
}
```

---

## 🚀 運用フロー

1. **ローカルでスクレイピング実行**
   ```bash
   python scraper.py
   ```

2. **GitHubに自動プッシュ**
   - `AUTO_GIT_PUSH=true`の場合、自動的にGitHubにプッシュされます

3. **WordPress側で自動更新**
   - キャッシュ時間が経過すると自動的に新しいデータを取得

---

## 💡 Tips

### パフォーマンス最適化

- キャッシュ時間を長めに設定（3600秒 = 1時間以上）
- 画像の遅延読み込み（`loading="lazy"`）を使用
- CDNを利用する場合、GitHub Pagesも検討

### セキュリティ

- `esc_html()`, `esc_url()`, `esc_attr()`を使用してXSS対策
- `wp_remote_get()`でSSL検証を有効化

### デバッグ

JSONが取得できない場合:
```php
$response = wp_remote_get($json_url);
error_log(print_r($response, true));
```

---

## 📌 チェックリスト

- [ ] GitHubトークンを`.env`に設定
- [ ] `AUTO_GIT_PUSH=true`に設定
- [ ] スクレイパーを実行してGitHubにプッシュ
- [ ] GitHub上でJSONファイルを確認
- [ ] WordPressにコードを実装
- [ ] ショートコードをページに追加
- [ ] 表示を確認

これで完成です！🎉

