import os
import logging
from typing import Optional
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

from config import Config
from utils.twitter import TwitterClient
from utils.image import ImageGenerator

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,  # より詳細なログを出力
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.get_log_path()),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TweetImageBot:
    def __init__(self, config: Config):
        self.config = config
        self.twitter = TwitterClient(config)
        self.image_generator = ImageGenerator(config)
        
    def run(self) -> None:
        """メインの実行ループ"""
        try:
            # 設定されているハッシュタグごとに処理
            for hashtag in self.config.SEARCH_HASHTAGS:
                logger.info(f"ハッシュタグ {hashtag} の処理を開始")
                tweets = self.twitter.search_tweets(hashtag)
                
                if not tweets:
                    continue
                    
                # 最新のツイートを処理
                tweet = tweets[0]
                logger.debug(f"処理するツイート: {tweet}")
                
                # 画像生成
                image_path = self.image_generator.create_tweet_image(
                    tweet['text'],
                    tweet['username'],
                    tweet['created_at']
                )
                
                if image_path:
                    # ツイート投稿
                    tweet_text = (
                        f"元ツイート: https://twitter.com/user/status/{tweet['id']}\n"
                        f"{hashtag} #自動生成"
                    )
                    self.twitter.post_tweet(tweet_text, image_path)
                    
                    # クリーンアップ
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        logger.error(f"一時ファイルの削除に失敗: {e}")
                    
        except Exception as e:
            logger.error(f"実行中にエラーが発生しました: {str(e)}", exc_info=True)
            raise

def main():
    try:
        # 設定の検証
        Config.validate()
        
        # ボットの初期化
        bot = TweetImageBot(Config)
        
        # スケジューラーの設定
        interval_minutes = int(os.getenv('SEARCH_INTERVAL', '15'))  # 環境変数から直接取得
        
        scheduler = BlockingScheduler()
        scheduler.add_job(
            bot.run,
            'interval',
            minutes=interval_minutes,
            next_run_time=datetime.now()  # 即時実行
        )
        
        logger.info(f"ボットを開始します（実行間隔: {interval_minutes}分）")
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("ボットを終了します")
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()