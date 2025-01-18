import tweepy
from dotenv import load_dotenv
import os
import sys

def check_env_variables():
    """環境変数の存在と形式をチェック"""
    print("\n=== 環境変数チェック ===")
    load_dotenv()
    
    required_vars = [
        'CONSUMER_KEY',
        'CONSUMER_SECRET',
        'ACCESS_TOKEN',
        'ACCESS_TOKEN_SECRET'
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 値の長さと形式をチェック
            is_valid = len(value) >= 25  # Twitter APIキーは通常25文字以上
            status = "OK" if is_valid else "異常 (長さが短すぎます)"
            print(f"{var}: {value[:8]}... ({len(value)}文字) - {status}")
        else:
            print(f"{var}: 未設定")
            all_present = False
    
    return all_present

def test_v2_client():
    """Twitter API v2クライアントのテスト"""
    print("\n=== Twitter API v2 テスト ===")
    try:
        client = tweepy.Client(
            consumer_key=os.getenv('CONSUMER_KEY'),
            consumer_secret=os.getenv('CONSUMER_SECRET'),
            access_token=os.getenv('ACCESS_TOKEN'),
            access_token_secret=os.getenv('ACCESS_TOKEN_SECRET')
        )
        
        # ユーザー情報取得テスト
        me = client.get_me()
        print(f"認証成功！")
        print(f"ユーザー名: @{me.data.username}")
        return True
        
    except tweepy.errors.Unauthorized as e:
        print(f"認証エラー: {str(e)}")
        print("考えられる原因:")
        print("1. APIキーまたはトークンが間違っている")
        print("2. アプリケーションの権限が不足している")
        print("3. アカウントが制限されている")
        return False
        
    except Exception as e:
        print(f"その他のエラー: {str(e)}")
        return False

def test_v1_client():
    """Twitter API v1.1クライアントのテスト"""
    print("\n=== Twitter API v1.1 テスト ===")
    try:
        auth = tweepy.OAuth1UserHandler(
            os.getenv('CONSUMER_KEY'),
            os.getenv('CONSUMER_SECRET'),
            os.getenv('ACCESS_TOKEN'),
            os.getenv('ACCESS_TOKEN_SECRET')
        )
        
        api = tweepy.API(auth)
        user = api.verify_credentials()
        print(f"認証成功！")
        print(f"ユーザー名: @{user.screen_name}")
        print(f"アカウント作成日: {user.created_at}")
        return True
        
    except tweepy.errors.Unauthorized as e:
        print(f"認証エラー: {str(e)}")
        return False
        
    except Exception as e:
        print(f"その他のエラー: {str(e)}")
        return False

def main():
    print("Twitter API 診断を開始します...")
    
    # 環境変数チェック
    if not check_env_variables():
        print("\n環境変数の設定に問題があります。.envファイルを確認してください。")
        return
    
    # API v2テスト
    v2_success = test_v2_client()
    
    # API v1.1テスト
    v1_success = test_v1_client()
    
    # 診断結果のまとめ
    print("\n=== 診断結果 ===")
    if v2_success and v1_success:
        print("すべてのテストが成功しました！")
    else:
        print("以下の確認が必要です：")
        print("1. Developer Portalで認証情報を再確認")
        print("2. アプリケーションの権限設定を確認")
        print("3. 必要に応じて新しいキーを生成")
        print("\nDeveloper Portal: https://developer.twitter.com/en/portal/dashboard")

if __name__ == "__main__":
    main()