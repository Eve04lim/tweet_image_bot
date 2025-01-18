import os
from dotenv import load_dotenv

# プロジェクトルートディレクトリのパスを取得
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# .envファイルの読み込み
load_dotenv(os.path.join(ROOT_DIR, '.env'))

class Config:
    # Twitter API設定
    CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
    BEARER_TOKEN = os.getenv('BEARER_TOKEN')

    # フォント設定
    _font_path = os.getenv('FONT_PATH', 'fonts/NotoSansJP-Regular.otf')
    FONT_PATH = os.path.join(ROOT_DIR, _font_path)
    FONT_SIZE = int(os.getenv('FONT_SIZE', '30'))
    
    # 画像生成設定
    MARGIN = int(os.getenv('MARGIN', '20'))
    LINE_SPACING = int(os.getenv('LINE_SPACING', '10'))
    IMAGE_WIDTH = int(os.getenv('IMAGE_WIDTH', '1000'))
    BG_COLOR = tuple(map(int, os.getenv('BG_COLOR', '255,255,255').split(',')))
    TEXT_COLOR = tuple(map(int, os.getenv('TEXT_COLOR', '0,0,0').split(',')))

    # レートリミット設定
    RATE_LIMIT_WINDOW = 15 * 60  # 15分
    RATE_LIMIT_MAX_REQUESTS = 180  # 15分あたりの最大リクエスト数
    
    # 検索設定
    SEARCH_HASHTAGS = os.getenv('SEARCH_HASHTAG', '#Python').split(',')
    SEARCH_INTERVAL = int(os.getenv('SEARCH_INTERVAL', '60'))  # デフォルト60分
    MAX_TWEETS = int(os.getenv('MAX_TWEETS', '5'))  # デフォルト5件

    @classmethod
    def validate(cls):
        """設定値の検証"""
        required_vars = [
            'CONSUMER_KEY',
            'CONSUMER_SECRET',
            'ACCESS_TOKEN',
            'ACCESS_TOKEN_SECRET'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        if not os.path.exists(cls.FONT_PATH):
            raise FileNotFoundError(
                f"Font file not found: {cls.FONT_PATH}\n"
                f"Please ensure the font file exists in the fonts directory"
            )

    @classmethod
    def get_log_path(cls):
        """ログファイルのパスを取得"""
        log_dir = os.path.join(ROOT_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, 'bot.log')