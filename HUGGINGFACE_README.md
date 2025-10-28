# AIstylist - 軽量版の説明

## 🎯 Hugging Face Spaces用の最適化されたバージョン

このバージョンは、Hugging Face Spacesの容量制限に合わせて最適化されています。

### 主な特徴

1. **APIベースのアプローチ**: モデルファイルは一切含まれません
   - すべての機能は**OpenAI API**への呼び出しで実現
   - GPT-4o (画像分析)、gpt-3.5-turbo (チャット)、DALL-E 3 (画像生成)

2. **容量削減対策**:
   - `venv/` ディレクトリ除外（Hugging Faceが自動的に作成）
   - データファイル（画像など）は最小限
   - キャッシュファイル除外

3. **必要なファイルのみ**:
   ```
   ├── app_hf.py              # Hugging Face用のメインアプリ
   ├── requirements_hf.txt     # 依存関係（軽量化版）
   ├── Dockerfile             # Docker設定
   ├── README_HF.md           # このREADME
   ├── templates/             # HTMLテンプレート
   ├── src/                   # ソースコード
   ├── database.py            # データベース管理
   ├── chat_service.py        # チャット機能
   ├── weather_service.py     # 天気API
   └── static/                # 静的ファイル（画像など）
   ```

### ストレージ制限について

- **Hugging Face Spaces無料版**: 50GB
- **このアプリ**: 約5-10GB（依存関係込み）
- **余裕あり**: 十分な容量

### 環境変数の設定

Hugging Face Spacesの環境変数設定で以下を追加：

```
OPENAI_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### 使い方

1. **このリポジトリをクローン**
2. **新しいHugging Face Spaceを作成**
   - SDK: Docker
   - Visibility: Public
3. **ファイルをアップロード**
4. **環境変数を設定**
5. **デプロイ完了！**

### 容量をさらに削減したい場合

1. **不要な画像ファイルを削除**
   - `data/clothes/input/` からテスト用画像を削除
   - `output/` から生成された画像を削除
   - `static/images/` から不要な画像を削除

2. **Git履歴の圧縮**
   ```bash
   git gc --aggressive
   ```

3. **依存関係の最適化**
   - `requirements_hf.txt` で必要なものだけをインストール

### デプロイ時の注意

- 初回デプロイに5-10分かかる場合があります
- 依存関係のインストールに時間がかかります
- 環境変数の設定を忘れずに！

### トラブルシューティング

**Q: デプロイに失敗する**
- ログを確認して、依存関係の問題をチェック
- 環境変数が正しく設定されているか確認

**Q: 容量が足りない**
- `docker gc` を実行してイメージをクリーンアップ
- 不要なファイルを削除

**Q: APIエラーが発生する**
- OPENAI_API_KEYが正しく設定されているか確認
- APIのクォータをチェック
