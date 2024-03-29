from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_ALLOW_ORIGINS'] = '*'
app.config['CORS_ALLOW_METHODS'] = ['GET', 'POST']
app.config['CORS_ALLOW_HEADERS'] = ['Content-Type', 'Authorization']


class TikTokScraper:

  def __init__(self, url):
    self.url = url

  def get_website_content(self):
    try:
      response = requests.get(self.url)
      response.raise_for_status()
      return response.text
    except requests.exceptions.RequestException as e:
      return str(e)

  def scrape(self):
    content = self.get_website_content()
    if not content.startswith("HTTP 错误") and not content.startswith(
        "连接错误") and not content.startswith("超时错误") and not content.startswith(
            "请求错误"):
      data = {}
      author_info = re.search(
          r'"author":\{"id":"(\d+)","shortId":".*?","uniqueId":".*?","nickname":"(.*?)",',
          content)
      data['uploader'] = author_info.group(2) if author_info else None

      counts_info = re.search(
          r'\{"diggCount":(\d+),"shareCount":(\d+),"commentCount":(\d+),"playCount":(\d+),"collectCount":"(\d+)"\},',
          content)
      data['likeCount'] = int(counts_info.group(1)) if counts_info else None
      data['shareCount'] = int(counts_info.group(2)) if counts_info else None
      data['commentCount'] = int(counts_info.group(3)) if counts_info else None
      data['viewCount'] = int(counts_info.group(4)) if counts_info else None
      data['collectionCount'] = int(
          counts_info.group(5)) if counts_info else None

      desc_info = re.search(r'"desc":"(.*?)","createTime":"(\d+)"', content)
      data['title'] = desc_info.group(1) if desc_info else None
      upload_time = int(desc_info.group(2)) if desc_info else None
      data['releaseTime'] = self.convert_to_timestamp(upload_time)
      data['status'] = 200

      return data
    return content

  @staticmethod
  def convert_to_timestamp(unix_time):
    cst_dt = datetime.fromtimestamp(unix_time, timezone(timedelta(hours=8)))
    return int(cst_dt.timestamp()) * 1000


@app.route('/')
def index():
  return 'Hello from Flask!'


@app.route('/tiktok', methods=['POST'])
def youtube():
  url = request.form.get('url')
  if not url:
    return jsonify({'error': 'No URL provided'}), 400
  scraper = TikTokScraper(url)

  try:
    data = scraper.scrape()
    return jsonify(data)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


app.run(host='0.0.0.0', port=81)
