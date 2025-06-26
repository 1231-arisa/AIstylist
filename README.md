# AIstylist - AI-Powered Fashion Coordination

AIstylistは、AIを使用してファッションコーディネーションを自動生成するプロジェクトです。OpenAIのGPT-4oとDALL-Eを使用して、アバターに服を着せたスタイリッシュなイラストを生成します。

## 機能

- **服の分析**: GPT-4oを使用して服の画像を詳細に分析
- **スタイル選択**: 天候やシーンに応じた服の組み合わせを自動選択
- **画像生成**: DALL-Eを使用してスタイリッシュなファッションイラストを生成
- **Webアプリケーション**: 直感的なUIで簡単に操作可能

## 環境設定

### 前提条件
- Python 3.11以上
- OpenAI API キー

### セットアップ

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd AIstylist
```

2. **仮想環境の作成とアクティベート**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate   # Linux/Mac
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **環境変数の設定**
`.env`ファイルを作成し、OpenAI APIキーを設定：
```
OPENAI_API_KEY=your_api_key_here
```

## 使用方法

### Webアプリケーション（推奨）

1. **アプリケーションの起動**
```bash
python app.py
```

2. **ブラウザでアクセス**
```
http://127.0.0.1:5000
```

3. **機能の使用**
   - **服のアップロード**: 「Upload Clothing」ボタンで服の画像をアップロード
   - **アウトフィット生成**: 「Generate Outfit」ボタンで天候とシーンを選択してアウトフィットを生成
   - **クローゼット管理**: アップロードした服の一覧を確認

### コマンドライン（従来の方法）

1. **服の画像を準備**
   - `data/clothes/input/`ディレクトリに服の画像を配置

2. **パイプラインの実行**
```bash
python run_full_pipeline.py
```

### 個別の機能

- **服の分析**: `python src/generate_item.py <image_path>`
- **スタイル選択**: `python src/style_agent.py`
- **画像生成**: `python src/generate_visualisation.py <avatar.txt> <clothing1.txt> <clothing2.txt>`

## プロジェクト構造

```
AIstylist/
├── app.py                    # メインのWebアプリケーション
├── data/
│   ├── avatar.txt            # アバターの説明
│   └── clothes/input/        # 服の画像
├── src/
│   ├── generate_item.py      # 服の分析
│   ├── style_agent.py        # スタイル選択
│   └── generate_visualisation.py  # 画像生成
├── templates/                # HTMLテンプレート
├── static/                   # CSS、JS、画像ファイル
├── output/                   # 生成された画像
├── requirements.txt          # メインの依存関係
└── run_full_pipeline.py      # コマンドラインパイプライン
```

## API エンドポイント

### POST /upload
服の画像をアップロードして分析
- **Content-Type**: multipart/form-data
- **Parameters**: file (画像ファイル)
- **Response**: JSON形式の分析結果

### POST /generate-outfit
天候とシーンに基づいてアウトフィットを生成
- **Content-Type**: application/json
- **Parameters**: weather, occasion
- **Response**: 生成された画像のURL

### GET /closet
クローゼットの内容を取得
- **Response**: アップロードされた服の一覧

## 依存関係

### メイン環境
- Flask==3.0.0 - Webフレームワーク
- openai==1.92.2 - OpenAI API
- Pillow==11.2.1 - 画像処理
- numpy==1.26.4 - 数値計算

## 注意事項

- OpenAI APIキーが必要です
- 画像生成にはAPIクレジットが消費されます
- 生成される画像はOpenAIのコンテンツポリシーに従います
- アップロード可能な画像サイズは16MBまでです

## トラブルシューティング

### よくある問題

1. **APIキーエラー**
   - `.env`ファイルに正しいAPIキーが設定されているか確認
   - APIキーに十分なクレジットがあるか確認

2. **画像生成エラー**
   - 服の説明が適切に生成されているか確認
   - OpenAIのコンテンツポリシーに違反していないか確認

3. **アプリケーションが起動しない**
   - 仮想環境がアクティベートされているか確認
   - 依存関係が正しくインストールされているか確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## ✨ Features

- 👗 **Personalized Outfit Suggestions**  
  Get AI-powered recommendations tailored to your preferences, body type, and occasion.

- 🛍️ **Virtual Wardrobe**  
  Upload your wardrobe and let AIstylist create new looks from your own clothes.

- 🎨 **Style Inspiration**  
  Discover trending styles and get inspired by curated looks.

- 📸 **Image-Based Recommendations**  
  Upload a photo and receive suggestions to enhance or complement your style.

- 🗣️ **Conversational Interface**  
  Chat with your AI stylist for instant advice and tips.

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AIstylist.git
   cd AIstylist
   ```

2. **Install dependencies**
   ```bash
   # Example for Node.js
   npm install
   ```

3. **Run the application**
   ```bash
   npm start
   ```

## 🖼️ Screenshots

<!-- Add screenshots or GIFs here to showcase the app -->

## 🤖 Technologies Used

- Artificial Intelligence / Machine Learning
- Node.js / Python (adapt as appropriate)
- React / Vue / Angular (adapt as appropriate)
- Cloud Storage

## 📄 License

This project is licensed under the MIT License.

## 🙌 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

## 📬 Contact

For questions or feedback, please contact [your.email@example.com](mailto:your.email@example.com).

---
AIstylist — Your personal AI-powered fashion assistant.
