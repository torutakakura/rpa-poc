#!/usr/bin/env python3
"""
RPAステップカタログをベクトルDBに投入するスクリプト
generated_step_list.jsonからデータを読み込み、OpenAI APIでembeddingを生成して
PostgreSQLのstep_embeddingsテーブルに格納する
"""
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class NumpyArrayAdapter:
    """NumPy配列をPostgreSQLのvector型に変換するアダプター"""
    def __init__(self, array):
        self.array = array

    def getquoted(self):
        # NumPy配列をPostgreSQLのvector形式 '[x,y,z,...]' に変換
        values = ','.join(str(float(x)) for x in self.array)
        return f"'[{values}]'::vector".encode('utf-8')


# NumPy配列用のアダプターを登録
register_adapter(np.ndarray, NumpyArrayAdapter)


class StepEmbeddingSeeder:
    """ステップ情報をembeddingと共にDBに投入するクラス"""
    
    def __init__(self):
        # OpenAI APIクライアントの初期化
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY環境変数が設定されていません")
        self.openai_client = OpenAI(api_key=api_key)
        
        # DB接続情報
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '55432'),
            'database': os.getenv('DB_NAME', 'rpa'),
            'user': os.getenv('DB_USER', 'rpa'),
            'password': os.getenv('DB_PASSWORD', 'rpa_password')
        }
        
        # JSONファイルパス
        self.json_path = project_root / 'generated_step_list.json'
        
    def load_step_data(self) -> List[Dict[str, Any]]:
        """generated_step_list.jsonからステップ情報を読み込む"""
        if not self.json_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('sequence', [])
    
    def create_embedding(self, text: str) -> np.ndarray:
        """OpenAI APIを使用してテキストのembeddingを生成"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = response.data[0].embedding
            return np.array(embedding)
        except Exception as e:
            print(f"Embedding生成エラー: {e}")
            raise
    
    def connect_db(self):
        """PostgreSQLに接続"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"DB接続エラー: {e}")
            raise
    
    def ensure_table_exists(self, conn):
        """step_embeddingsテーブルが存在することを確認（なければ作成）"""
        cursor = conn.cursor()
        try:
            # 拡張機能の有効化
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # テーブルの作成
            create_table_query = """
            CREATE TABLE IF NOT EXISTS step_embeddings (
                id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                step_key text NOT NULL,
                title text,
                description text,
                metadata jsonb,
                embedding vector(1536) NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now(),
                updated_at timestamptz NOT NULL DEFAULT now(),
                UNIQUE (step_key)
            )
            """
            cursor.execute(create_table_query)
            
            # インデックスの作成
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS step_embeddings_embedding_idx
                ON step_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
            """)
            
            conn.commit()
            print("✅ テーブルとインデックスの存在を確認しました")
            
        except Exception as e:
            print(f"テーブル作成エラー: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def seed_data(self):
        """ステップデータをDBに投入"""
        # ステップデータを読み込み
        steps = self.load_step_data()
        print(f"読み込んだステップ数: {len(steps)}")
        
        # DB接続
        conn = self.connect_db()
        
        # テーブルの存在を確認（なければ作成）
        self.ensure_table_exists(conn)
        
        cursor = conn.cursor()
        
        try:
            # 既存データをクリア（オプション）
            clear_existing = input("既存データをクリアしますか？ (y/n): ").lower() == 'y'
            if clear_existing:
                cursor.execute("TRUNCATE TABLE step_embeddings CASCADE")
                conn.commit()
                print("既存データをクリアしました")
            
            # 各ステップを処理
            success_count = 0
            error_count = 0
            
            for i, step in enumerate(steps, 1):
                try:
                    # ステップ情報を抽出
                    step_id = step.get('uuid')
                    step_key = step.get('cmd')
                    title = step.get('cmd-nickname', '')  # titleはcmd-nicknameを使用
                    description = step.get('description', '')
                    
                    # 必須フィールドのチェック
                    if not step_id or not step_key:
                        print(f"ステップ {i}: 必須フィールドが不足しています（スキップ）")
                        error_count += 1
                        continue
                    
                    # 既存レコードの確認
                    cursor.execute(
                        "SELECT id FROM step_embeddings WHERE step_key = %s",
                        (step_key,)
                    )
                    existing = cursor.fetchone()
                    
                    if existing and not clear_existing:
                        print(f"ステップ {i} ({step_key}): 既存レコードが存在します（スキップ）")
                        continue
                    
                    # embedding用のテキストを生成
                    embedding_text = f"{title} {description}".strip()
                    if not embedding_text:
                        embedding_text = step_key  # フォールバック
                    
                    # embeddingを生成
                    print(f"ステップ {i}/{len(steps)} ({step_key}): embedding生成中...")
                    embedding_vector = self.create_embedding(embedding_text)
                    
                    # データを挿入または更新
                    insert_query = """
                        INSERT INTO step_embeddings (
                            id, step_key, title, description, metadata, embedding
                        ) VALUES (
                            %s::uuid, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (step_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding,
                            updated_at = NOW()
                    """
                    
                    cursor.execute(insert_query, (
                        step_id,
                        step_key,
                        title,
                        description,
                        Json(step),  # metadataとしてステップ全体を保存
                        embedding_vector
                    ))
                    
                    success_count += 1
                    
                    # 定期的にコミット（メモリ効率のため）
                    if i % 10 == 0:
                        conn.commit()
                        print(f"  {i}件処理済み...")
                    
                except Exception as e:
                    print(f"ステップ {i} ({step.get('cmd', 'unknown')}): エラー - {e}")
                    error_count += 1
                    conn.rollback()  # エラー時はロールバック
            
            # 最終コミット
            conn.commit()
            
            # 結果サマリー
            print("\n=== 投入完了 ===")
            print(f"成功: {success_count}件")
            print(f"エラー: {error_count}件")
            print(f"合計: {len(steps)}件")
            
            # インデックスの更新を推奨
            print("\nインデックスを更新中...")
            cursor.execute("REINDEX INDEX step_embeddings_embedding_idx")
            conn.commit()
            print("インデックスの更新が完了しました")
            
        except Exception as e:
            print(f"処理中にエラーが発生しました: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
            print("\nDB接続を閉じました")


def main():
    """メイン処理"""
    print("=== RPAステップカタログ Embedding投入スクリプト ===\n")
    
    # 必要な環境変数の確認
    required_env = ['OPENAI_API_KEY']
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print("以下の環境変数を設定してください:")
        for env in missing_env:
            print(f"  - {env}")
        print("\n例:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  export DB_HOST='localhost'")
        print("  export DB_PORT='5432'")
        print("  export DB_NAME='postgres'")
        print("  export DB_USER='postgres'")
        print("  export DB_PASSWORD='postgres'")
        sys.exit(1)
    
    # データ投入実行
    try:
        seeder = StepEmbeddingSeeder()
        seeder.seed_data()
        print("\n✅ データ投入が正常に完了しました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()