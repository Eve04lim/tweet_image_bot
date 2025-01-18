import tweepy
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self, config):
        """Twitter APIクライアントの初期化"""
        self.config = config
        
        # API v1.1クライアント（画像アップロード用）
        auth = tweepy.OAuth1UserHandler(
            config.CONSUMER_KEY,
            config.CONSUMER_SECRET,
            config.ACCESS_TOKEN,
            config.ACCESS_TOKEN_SECRET
        )
        self.api = tweepy.API(auth)
        
        # API v2クライアント（検索用）
        self.client = tweepy.Client(
            bearer_token=config.BEARER_TOKEN,  # Bearer Tokenを使用
            consumer_key=config.CONSUMER_KEY,
            consumer_secret=config.CONSUMER_SECRET,
            access_token=config.ACCESS_TOKEN,
            access_token_secret=config.ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        
        logger.debug("Twitter APIクライアントを初期化しました")

    def search_tweets(self, hashtag: str) -> List[dict]:
        """ハッシュタグで最新のツイートを検索"""
        try:
            query = f"{hashtag} -is:retweet lang:ja"
            logger.info(f"検索クエリ: {query}")
            
            # 検索の実行
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(10, self.config.MAX_TWEETS),
                tweet_fields=['created_at', 'author_id', 'text']
            )
            
            if not tweets or not tweets.data:
                logger.info(f"ハッシュタグ {hashtag} の新しいツイートが見つかりませんでした")
                return []
            
            # ユーザー情報の取得
            user_ids = [tweet.author_id for tweet in tweets.data]
            users = self.client.get_users(ids=user_ids)
            user_map = {user.id: user.username for user in users.data} if users.data else {}
            
            # 結果の整形
            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'username': user_map.get(tweet.author_id, 'unknown')
                })
            
            logger.info(f"ツイートを {len(results)} 件取得しました")
            return results
            
        except tweepy.errors.Unauthorized as e:
            logger.error(f"認証エラー: {str(e)}")
            logger.error("API権限を確認してください")
            raise
        except Exception as e:
            logger.error(f"ツイート検索中にエラーが発生しました: {str(e)}")
            logger.error(f"エラーの種類: {type(e).__name__}")
            raise

    def post_tweet(self, text: str, image_path: str) -> bool:
        """画像付きツイートを投稿"""
        try:
            # 画像のアップロード
            media = self.api.media_upload(image_path)
            
            # ツイートの投稿
            self.client.create_tweet(
                text=text,
                media_ids=[media.media_id]
            )
            
            logger.info("ツイートを投稿しました")
            return True
            
        except Exception as e:
            logger.error(f"ツイート投稿中にエラーが発生しました: {str(e)}")
            return False