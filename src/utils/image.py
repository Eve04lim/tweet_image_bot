from PIL import Image, ImageDraw, ImageFont
import logging
from typing import Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, config):
        """
        画像生成器の初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.font = ImageFont.truetype(config.FONT_PATH, config.FONT_SIZE)
        
    def _calculate_text_layout(self, text: str) -> List[str]:
        """
        テキストを行に分割してレイアウトを計算
        
        Args:
            text: 分割するテキスト
            
        Returns:
            分割された行のリスト
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line = ' '.join(current_line)
            bbox = self.font.getbbox(line)
            if bbox[2] > (self.config.IMAGE_WIDTH - 2 * self.config.MARGIN):
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def create_tweet_image(
        self,
        tweet_text: str,
        username: str,
        created_at: datetime
    ) -> str:
        """
        ツイートの内容から画像を生成
        
        Args:
            tweet_text: ツイート本文
            username: ユーザー名
            created_at: ツイート作成日時
            
        Returns:
            生成した画像の一時ファイルパス
        """
        try:
            lines = self._calculate_text_layout(tweet_text)
            
            # 画像の高さを計算
            total_height = (
                len(lines) * (self.config.FONT_SIZE + self.config.LINE_SPACING) +
                2 * self.config.MARGIN +
                2 * self.config.FONT_SIZE  # ユーザー名と日時用の追加スペース
            )
            
            # 画像の作成
            image = Image.new(
                'RGB',
                (self.config.IMAGE_WIDTH, total_height),
                self.config.BG_COLOR
            )
            draw = ImageDraw.Draw(image)
            
            # ツイート本文の描画
            y = self.config.MARGIN
            for line in lines:
                draw.text(
                    (self.config.MARGIN, y),
                    line,
                    font=self.font,
                    fill=self.config.TEXT_COLOR
                )
                y += self.config.FONT_SIZE + self.config.LINE_SPACING
            
            # ユーザー名と投稿日時の描画
            y += self.config.LINE_SPACING
            created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
            draw.text(
                (self.config.MARGIN, y),
                f"@{username}",
                font=self.font,
                fill=self.config.TEXT_COLOR
            )
            draw.text(
                (self.config.MARGIN, y + self.config.FONT_SIZE),
                created_at_str,
                font=self.font,
                fill=self.config.TEXT_COLOR
            )
            
            # 一時ファイルとして保存
            temp_path = f'temp_tweet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            image.save(temp_path)
            return temp_path
            
        except Exception as e:
            logger.error(f"画像生成中にエラーが発生しました: {str(e)}")
            raise