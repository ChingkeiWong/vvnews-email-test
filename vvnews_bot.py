#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews 王敏奕新闻机器人 - 原始版本 (完整9个新闻源)
功能: 搜索王敏奕相关新闻并发送邮件通知
新闻源: Google News, 香港01, 東網on.cc, 星島娛樂, 明報, 明周, 香港文匯報, TVB, YouTube
"""

import requests
import feedparser
import re
import json
import os
import smtplib
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import logging

# Gmail API 支持（可选）
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    logging.warning("Gmail API 库未安装，将仅使用 SMTP 发送邮件")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VVNewsBot:
    def __init__(self, search_hours=24):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 搜索时间范围 (小时)
        self.search_hours = search_hours
        
        # 邮件配置
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            # 发件人优先级：ZOHO_EMAIL（用于Zoho/统一显示）> 默认Gmail（用于Gmail回退）
            'sender_email': os.getenv('ZOHO_EMAIL') or 'chingkeiwong666@gmail.com',
            'sender_password': 'scjrjhnfyohdigem',
            # 收件人优先级：RECIPIENT_EMAIL 环境变量 > ZOHO_EMAIL > 默认 Gmail
            'recipient_email': os.getenv('RECIPIENT_EMAIL') or os.getenv('ZOHO_EMAIL') or 'chingkeiwong666@gmail.com',
            'subject_prefix': f'[VVNews] 王敏奕最新新闻 (过去{search_hours}小时)',
            # Gmail API 配置（可选）
            'gmail_api_token_file': os.getenv('GMAIL_API_TOKEN_FILE', 'token.json'),
            'gmail_api_enabled': os.getenv('GMAIL_API_ENABLED', 'false').lower() == 'true'
        }
    
    def search_hk01(self, keyword):
        """搜索香港01 - 使用娱乐版块的优化方法（同步自auto版本）"""
        results = []
        
        try:
            logging.info(f"搜索香港01: {keyword}")
            
            # 方法1: 搜索娱乐版块（用户指定的URL）
            entertainment_url = "https://www.hk01.com/zone/2/娛樂"
            logging.info(f"检查香港01娱乐版块: {entertainment_url}")
            
            response = self.session.get(entertainment_url, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # 检查页面是否包含关键词
                if keyword in content:
                    logging.info(f"在娱乐版块找到关键词: {keyword}")
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 查找包含关键词的文章链接
                    links = soup.find_all('a', href=True)
                    seen_urls = set()
                    
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text().strip()
                        title_attr = link.get('title', '').strip()
                        
                        # 检查链接文本或标题属性是否包含关键词
                        for check_text in [text, title_attr]:
                            if (check_text and 
                                keyword.lower() in check_text.lower() and 
                                len(check_text) > 10 and
                                ('/article/' in href or '/news/' in href)):
                                
                                # 构建完整URL
                                if href.startswith('/'):
                                    full_url = f'https://www.hk01.com{href}'
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    continue
                                
                                # 去重检查
                                if full_url in seen_urls:
                                    continue
                                seen_urls.add(full_url)
                                
                                result = {
                                    'title': check_text,
                                    'url': full_url,
                                    'source': '香港01',
                                    'keyword': keyword
                                }
                                
                                results.append(result)
                                logging.info(f"找到香港01娱乐文章: {check_text[:50]}...")
                                break
                        
                        # 限制结果数量
                        if len(results) >= 5:
                            break
                else:
                    logging.info("娱乐版块未包含关键词，尝试其他频道")
            
            # 方法2: 如果娱乐版块没有找到，尝试其他相关频道
            if not results:
                other_channels = [
                    ("https://www.hk01.com/channel/22/即時娛樂", "即时娱乐频道"),
                    ("https://www.hk01.com/zone/1/港闻", "港闻版块"),
                    ("https://www.hk01.com/latest", "最新新闻"),
                    ("https://www.hk01.com/hot", "热门新闻")
                ]
                
                for channel_url, channel_name in other_channels:
                    try:
                        logging.info(f"检查香港01{channel_name}: {channel_url}")
                        channel_response = self.session.get(channel_url, timeout=10)
                        
                        if channel_response.status_code == 200 and keyword in channel_response.text:
                            soup = BeautifulSoup(channel_response.text, 'html.parser')
                            links = soup.find_all('a', href=True)
                            
                            for link in links:
                                href = link.get('href', '')
                                text = link.get_text().strip()
                                
                                if (keyword.lower() in text.lower() and 
                                    len(text) > 10 and
                                    ('/article/' in href or '/news/' in href)):
                                    
                                    if href.startswith('/'):
                                        full_url = f'https://www.hk01.com{href}'
                                    else:
                                        full_url = href
                                    
                                    # 简单去重
                                    if not any(r['url'] == full_url for r in results):
                                        result = {
                                            'title': text,
                                            'url': full_url,
                                            'source': '香港01',
                                            'keyword': keyword
                                        }
                                        
                                        results.append(result)
                                        logging.info(f"在{channel_name}找到文章: {text[:50]}...")
                                        
                                        if len(results) >= 3:
                                            break
                            
                            # 如果找到结果就不再搜索其他频道
                            if results:
                                break
                                
                    except Exception as e:
                        logging.warning(f"搜索{channel_name}失败: {e}")
                        continue
            
            logging.info(f"香港01 搜索完成，找到 {len(results)} 条结果")
            return results
        except Exception as e:
            logging.error(f"搜索香港01时出错: {e}")
            return results

    def search_am730(self, keyword):
        """搜索 am730 娱乐新闻，优先站内页面，回退到简单匹配
        逻辑：尝试站内搜索/娱乐频道页，收集包含关键词的标题链接
        """
        results = []
        try:
            logging.info(f"搜索 am730: {keyword}")
            candidate_pages = [
                f"https://www.am730.com.hk/search?search={keyword}",  # 官方搜索页（参数版）
                f"https://www.am730.com.hk/search/{keyword}",         # 备用路径版
                "https://www.am730.com.hk/%E5%A8%9B%E6%A8%82",
                "https://www.am730.com.hk/",
            ]
            seen = set()
            max_items = 6
            for page in candidate_pages:
                try:
                    resp = self.session.get(page, timeout=12)
                    if resp.status_code != 200:
                        continue
                    soup = BeautifulSoup(resp.text, 'lxml')
                    for a in soup.find_all('a'):
                        title = (a.get_text() or '').strip()
                        href = a.get('href') or ''
                        if not title or not href:
                            continue
                        if keyword not in title:
                            continue
                        if href.startswith('/'):
                            url = f"https://www.am730.com.hk{href}"
                        elif href.startswith('http'):
                            url = href
                        else:
                            continue
                        if 'am730.com.hk' not in url:
                            continue
                        if url in seen:
                            continue
                        # 进入文章页提取发布时间并过滤24小时内
                        pub_iso, pub_readable = self._extract_am730_publish_time(url)
                        if not pub_iso:
                            # 若文章页无法解析时间，则跳过，避免误报
                            continue
                        # 构造临时对象进行时间窗口校验
                        temp_item = {'publish_time': pub_iso}
                        if not self.is_within_time_range(temp_item):
                            continue
                        seen.add(url)
                        results.append({
                            'title': title,
                            'url': url,
                            'source': 'am730',
                            'keyword': keyword,
                            'publish_time': pub_iso,
                            'publish_time_readable': pub_readable
                        })
                        if len(results) >= max_items:
                            break
                except Exception:
                    continue
                if len(results) >= max_items:
                    break
            # 回退：使用 Google site: 搜索 am730（如站内抓取不足）
            if len(results) < 2:
                try:
                    fallback = self._search_am730_via_google(keyword, need=max_items - len(results), seen=seen)
                    results.extend(fallback)
                except Exception as _:
                    pass

            logging.info(f"am730 搜索完成，找到 {len(results)} 条结果")
            return results
        except Exception as e:
            logging.error(f"搜索 am730 时出错: {e}")
            return results

    def _search_am730_via_google(self, keyword, need=3, seen=None):
        """回退：通过 Google site:am730.com.hk 搜索关键字页面"""
        if seen is None:
            seen = set()
        results = []
        try:
            q = f"site:am730.com.hk {keyword}"
            url = "https://www.google.com/search"
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', '')
            }
            resp = self.session.get(url, params={'q': q, 'hl': 'zh-TW'}, headers=headers, timeout=8)
            if resp.status_code != 200:
                return results
            soup = BeautifulSoup(resp.text, 'lxml')
            for a in soup.select('a'):
                href = a.get('href') or ''
                text = (a.get_text() or '').strip()
                if not href or not text:
                    continue
                if href.startswith('/url?q='):
                    try:
                        real = href.split('/url?q=')[1].split('&')[0]
                    except Exception:
                        continue
                elif href.startswith('http'):
                    real = href
                else:
                    continue
                if 'am730.com.hk' not in real:
                    continue
                if keyword not in text and keyword not in real:
                    continue
                if real in seen:
                    continue
                pub_iso, pub_readable = self._extract_am730_publish_time(real)
                if not pub_iso:
                    continue
                if not self.is_within_time_range({'publish_time': pub_iso}):
                    continue
                seen.add(real)
                results.append({
                    'title': text[:120],
                    'url': real,
                    'source': 'am730',
                    'keyword': keyword,
                    'publish_time': pub_iso,
                    'publish_time_readable': pub_readable
                })
                if len(results) >= need:
                    break
            return results
        except Exception:
            return results

    def _extract_am730_publish_time(self, article_url):
        """从 am730 文章页提取发布时间 (iso, readable)"""
        try:
            resp = self.session.get(article_url, timeout=8)
            if resp.status_code != 200:
                return None, None
            html = resp.text
            patterns = [
                r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)["\']',
                r'"datePublished"\s*:\s*"([^"]+)"',
                r'<meta[^>]+name=["\']pubdate["\'][^>]+content=["\']([^"\']+)["\']',
            ]
            from datetime import timezone, timedelta
            for pat in patterns:
                m = re.search(pat, html, re.IGNORECASE)
                if m:
                    raw = m.group(1).strip()
                    try:
                        dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
                    except Exception:
                        # 尝试常见格式：YYYY-MM-DD HH:MM
                        try:
                            dt = datetime.strptime(raw[:16], '%Y-%m-%d %H:%M')
                            dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
                        except Exception:
                            continue
                    beijing_tz = timezone(timedelta(hours=8))
                    dt_bj = dt.astimezone(beijing_tz)
                    return dt.isoformat(), dt_bj.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return None, None
        return None, None
    
    def search_google_news(self, keyword):
        """搜索Google News - 带时间过滤"""
        results = []
        
        try:
            logging.info(f"搜索Google新闻: {keyword} (过去{self.search_hours}小时)")
            
            # 根据搜索时间范围添加when参数
            if self.search_hours <= 1:
                when_param = "when:1h"
            elif self.search_hours <= 24:
                when_param = "when:1d"
            elif self.search_hours <= 168:  # 7天
                when_param = "when:7d"
            else:
                when_param = ""  # 无时间限制
            
            # 构建搜索URL
            if when_param:
                url = f"https://news.google.com/search?q={keyword} {when_param}&hl=zh-TW&gl=HK&ceid=HK:zh-TW"
            else:
                url = f"https://news.google.com/search?q={keyword}&hl=zh-TW&gl=HK&ceid=HK:zh-TW"
                
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('article')
                
                for article in articles[:10]:  # 限制结果数量
                    title_elem = article.find('h3')
                    if title_elem and keyword.lower() in title_elem.get_text().lower():
                        title = title_elem.get_text().strip()
                        link_elem = article.find('a')
                        if link_elem:
                            article_url = 'https://news.google.com' + link_elem.get('href', '')
                            
                            results.append({
                                'title': title,
                                'url': article_url,
                                'source': 'Google News',
                                'keyword': keyword
                            })
            
            logging.info(f"Google News 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索Google News时出错: {e}")
            return results
    
    def search_youtube(self, keyword):
        """搜索YouTube - 使用RSS优先策略（同步auto版，支持多频道与时间窗）"""
        results = []
        try:
            env_ids = os.getenv('YOUTUBE_CHANNEL_IDS', '').strip()
            if env_ids:
                raw_ids = [x.strip() for x in env_ids.split(',') if x.strip()]
            else:
                raw_ids = ['@TVBENews', '@TVB']

            channel_ids = []
            for ident in raw_ids:
                cid = self._resolve_youtube_channel_id(ident)
                if cid:
                    channel_ids.append(cid)

            if not channel_ids:
                logging.warning("未解析到有效的YouTube频道ID，跳过YouTube搜索")
                return results

            from datetime import datetime as _dt
            now_ts = _dt.utcnow()
            cutoff_hours = float(os.getenv('SEARCH_HOURS', str(self.search_hours)))
            max_per_channel = 5

            for channel_id in channel_ids:
                rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                try:
                    feed = feedparser.parse(rss_url)
                except Exception as e:
                    logging.warning(f"解析RSS失败: {rss_url} -> {e}")
                    continue

                for entry in feed.entries[:max_per_channel]:
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                    publish_time_iso = None
                    publish_time_readable = None
                    within_window = True
                    if published_parsed:
                        publish_dt = _dt(*published_parsed[:6])  # UTC
                        publish_time_iso = publish_dt.isoformat()
                        publish_time_readable = publish_dt.strftime('%Y-%m-%d %H:%M:%S')
                        diff_hours = (now_ts - publish_dt).total_seconds() / 3600.0
                        within_window = diff_hours <= cutoff_hours

                    if keyword.lower() in title.lower() and within_window:
                        results.append({
                            'title': title,
                            'url': link,
                            'source': 'YouTube',
                            'publish_time': publish_time_iso,
                            'publish_time_readable': publish_time_readable,
                            'keyword': keyword
                        })

            logging.info(f"YouTube RSS 搜索完成，找到 {len(results)} 条结果")
            return results
        except Exception as e:
            logging.error(f"搜索YouTube时出错: {e}")
            return results

    def _resolve_youtube_channel_id(self, handle_or_url: str) -> str:
        """解析 @handle 或 URL 到 channel_id。"""
        ident = handle_or_url.strip()
        try:
            if ident.startswith('UC') and len(ident) > 10:
                return ident
            if 'youtube.com/channel/' in ident:
                m = re.search(r"/channel/([A-Za-z0-9_-]+)", ident)
                return m.group(1) if m else ''
            if ident.startswith('http'):
                url = ident
            elif ident.startswith('@'):
                url = f"https://www.youtube.com/{ident}"
            else:
                url = f"https://www.youtube.com/@{ident}"

            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                m = re.search(r'"channelId":"(UC[^"]+)"', resp.text)
                if m:
                    return m.group(1)
        except Exception as e:
            logging.warning(f"解析频道ID失败: {ident} -> {e}")
        return ''

    def get_youtube_video_real_title(self, video_url, video_id):
        """获取YouTube视频的真实标题"""
        try:
            logging.info(f"正在验证YouTube视频标题: {video_id}")
            
            response = self.session.get(video_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # 查找真实标题的多种模式
                title_patterns = [
                    r'<title>([^<]*?)</title>',
                    r'"title":"([^"]*?)",?"lengthText"',
                    r'<meta name="title" content="([^"]*?)">',
                    r'<meta property="og:title" content="([^"]*?)">',
                    r'"videoDetails":{"videoId":"[^"]*","title":"([^"]*?)"'
                ]
                
                for pattern in title_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        title = matches[0].strip()
                        # 清理YouTube后缀
                        if title.endswith(' - YouTube'):
                            title = title[:-10]
                        if len(title) > 10:
                            logging.info(f"找到真实标题: {title}")
                            return title
                
            return None
            
        except Exception as e:
            logging.error(f"获取YouTube视频真实标题失败: {e}")
            return None
    
    def get_youtube_video_publish_time(self, video_url, video_id):
        """点击进入YouTube视频页面获取准确的发布时间"""
        try:
            logging.info(f"正在获取YouTube视频发布时间: {video_id}")
            
            # 访问视频页面
            response = self.session.get(video_url, timeout=15)
            if response.status_code != 200:
                logging.warning(f"无法访问YouTube视频页面: {response.status_code}")
                return None
            
            content = response.text
            current_time = datetime.now()
            
            # 多种发布时间提取模式
            time_patterns = [
                # 标准的发布时间模式
                r'"publishDate":"([^"]+)"',
                r'"uploadDate":"([^"]+)"',
                r'"datePublished":"([^"]+)"',
                # 相对时间模式
                r'"publishedTimeText":{"simpleText":"([^"]+)"}',
                r'"publishedTimeText":"([^"]+)"',
                # 元数据模式
                r'<meta property="video:release_date" content="([^"]+)"',
                r'<meta itemprop="datePublished" content="([^"]+)"',
                r'<meta itemprop="uploadDate" content="([^"]+)"',
                # JSON-LD模式
                r'"datePublished":\s*"([^"]+)"',
                r'"uploadDate":\s*"([^"]+)"',
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    time_text = matches[0].strip()
                    logging.info(f"找到时间文本: {time_text}")
                    
                    # 尝试解析ISO格式时间
                    try:
                        # 处理ISO格式 (2024-08-15T10:30:00Z 或 2024-08-15T10:30:00+08:00)
                        if 'T' in time_text and ('Z' in time_text or '+' in time_text or '-' in time_text[-6:]):
                            publish_time = datetime.fromisoformat(time_text.replace('Z', '+00:00'))
                            # 转换为北京时间
                            from datetime import timezone, timedelta
                            beijing_tz = timezone(timedelta(hours=8))
                            publish_time = publish_time.astimezone(beijing_tz)
                            logging.info(f"解析ISO格式时间成功: {publish_time}")
                            return publish_time
                    except Exception as e:
                        logging.debug(f"ISO时间解析失败: {e}")
                        continue  # 继续下一个pattern
                    
                    # 尝试解析相对时间
                    try:
                        from datetime import timedelta
                        if '小时前' in time_text or 'hours ago' in time_text.lower():
                            hours_match = re.search(r'(\d+)', time_text)
                            if hours_match:
                                hours_ago = int(hours_match.group(1))
                                publish_time = current_time - timedelta(hours=hours_ago)
                                logging.info(f"解析相对时间成功: {hours_ago}小时前 = {publish_time}")
                                return publish_time
                        elif '天前' in time_text or 'days ago' in time_text.lower():
                            days_match = re.search(r'(\d+)', time_text)
                            if days_match:
                                days_ago = int(days_match.group(1))
                                publish_time = current_time - timedelta(days=days_ago)
                                logging.info(f"解析相对时间成功: {days_ago}天前 = {publish_time}")
                                return publish_time
                        elif '分钟前' in time_text or 'minutes ago' in time_text.lower():
                            minutes_match = re.search(r'(\d+)', time_text)
                            if minutes_match:
                                minutes_ago = int(minutes_match.group(1))
                                publish_time = current_time - timedelta(minutes=minutes_ago)
                                logging.info(f"解析相对时间成功: {minutes_ago}分钟前 = {publish_time}")
                                return publish_time
                        elif '周前' in time_text or 'weeks ago' in time_text.lower():
                            weeks_match = re.search(r'(\d+)', time_text)
                            if weeks_match:
                                weeks_ago = int(weeks_match.group(1))
                                publish_time = current_time - timedelta(weeks=weeks_ago)
                                logging.info(f"解析相对时间成功: {weeks_ago}周前 = {publish_time}")
                                return publish_time
                    except Exception as e:
                        logging.debug(f"相对时间解析失败: {e}")
            
            logging.warning(f"未能提取YouTube视频发布时间: {video_id}")
            return None
            
        except Exception as e:
            logging.error(f"获取YouTube视频发布时间失败: {e}")
            return None
    
    def search_oncc(self, keyword):
        """搜索東網on.cc - 增强版：包含基于日期的搜索策略"""
        results = []
        
        try:
            logging.info(f"搜索東網: {keyword}")
            
            # 生成最近几天的日期用于搜索
            from datetime import datetime, timedelta
            today = datetime.now()
            dates_to_check = []
            for i in range(7):  # 检查最近7天
                date = today - timedelta(days=i)
                dates_to_check.append(date.strftime('%Y%m%d'))
            
            # 策略1: 检查多个可能的东网页面（增强版）
            oncc_urls = [
                "https://hk.on.cc/hk/entertainment/index.html",  # 娱乐首页
                "https://hk.on.cc/hk/bkn/cnt/entertainment/",    # BKN娱乐目录 - 重点
                "https://hk.on.cc/hk/bkn/cnt/",                  # BKN内容目录
                "https://hk.on.cc/hk/bkn/",                      # BKN主页 
                "https://hk.on.cc/hk/news/",                     # 新闻主页
                "https://hk.on.cc/"                              # 主页
            ]
            
            # 策略1.5: 基于日期的直接搜索（新增）
            date_based_urls = []
            for date_str in dates_to_check[:3]:  # 只检查最近3天，避免过多请求
                date_based_urls.extend([
                    f"https://hk.on.cc/hk/bkn/cnt/entertainment/{date_str}/",
                    f"https://hk.on.cc/hk/bkn/cnt/news/{date_str}/",
                ])
            
            # 合并所有URL
            all_urls = oncc_urls + date_based_urls
            
            for base_url in all_urls:
                try:
                    logging.info(f"检查东网页面: {base_url}")
                    response = self.session.get(base_url, timeout=10)
                    
                    if response.status_code == 200:
                        # 处理编码问题
                        if response.encoding == 'ISO-8859-1':
                            response.encoding = 'utf-8'
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # 查找新闻容器
                        news_containers = soup.find_all(['div', 'section'], 
                                                       class_=re.compile(r'news|article|content|story', re.I))
                        
                        # 检查所有链接
                        all_links = soup.find_all('a', href=True)
                        
                        for link in all_links:
                            # 获取链接文本和属性
                            texts_to_check = [
                                link.get_text().strip(),
                                link.get('title', '').strip(),
                                link.get('alt', '').strip()
                            ]
                            
                            href = link.get('href', '')
                            
                            for text in texts_to_check:
                                if (text and keyword.lower() in text.lower() and 
                                    len(text) > 8 and len(text) < 300):
                                    
                                    # 检查是否是有效的新闻链接（增强版）
                                    if (href and 
                                        any(pattern in href.lower() for pattern in 
                                            ['/bkn/', '/cnt/', '/news/', '/entertainment/', '/hk/', '.html']) and
                                        'index.html' not in href and 'search' not in href and
                                        # 特别匹配目标新闻的URL模式
                                        (any(date_pattern in href for date_pattern in dates_to_check) or
                                         'bkn-' in href or '/cnt/' in href)):
                                        
                                        # 构建完整URL
                                        if href.startswith('/'):
                                            full_url = 'https://hk.on.cc' + href
                                        elif href.startswith('http'):
                                            full_url = href
                                        else:
                                            full_url = f'https://hk.on.cc/{href}'
                                        
                                        # 尝试获取更详细的信息
                                        try:
                                            detail_response = self.session.get(full_url, timeout=8)
                                            if detail_response.status_code == 200:
                                                if detail_response.encoding == 'ISO-8859-1':
                                                    detail_response.encoding = 'utf-8'
                                                    
                                                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                                                
                                                # 获取页面标题
                                                page_title = None
                                                title_selectors = ['h1', 'title', '.headline', '.article-title']
                                                
                                                for selector in title_selectors:
                                                    title_elem = detail_soup.select_one(selector)
                                                    if title_elem:
                                                        candidate = title_elem.get_text().strip()
                                                        if keyword.lower() in candidate.lower() and len(candidate) > 10:
                                                            page_title = candidate
                                                            break
                                                
                                                final_title = page_title if page_title else text
                                                
                                                results.append({
                                                    'title': final_title,
                                                    'url': full_url,
                                                    'source': '東網on.cc',
                                                    'keyword': keyword
                                                })
                                                
                                                logging.info(f"找到东网新闻: {final_title[:40]}...")
                                                break  # 找到一个就跳出文本检查循环
                                        except:
                                            # 如果无法获取详情，使用原始信息
                                            results.append({
                                                'title': text,
                                                'url': full_url,
                                                'source': '東網on.cc',
                                                'keyword': keyword
                                            })
                                            break
                        
                        # 如果找到结果就停止检查其他页面
                        if results:
                            break
                            
                except Exception as e:
                    logging.warning(f"检查东网页面 {base_url} 失败: {str(e)}")
                    continue
            
            # 策略2: 基于Sitemap的精确搜索（新增高效策略）
            if not results:
                logging.info("尝试东网Sitemap策略...")
                
                try:
                    sitemap_url = "https://hk.on.cc/sitemap.xml"
                    sitemap_response = self.session.get(sitemap_url, timeout=15)
                    
                    if sitemap_response.status_code == 200:
                        import xml.etree.ElementTree as ET
                        from datetime import datetime, timedelta
                        
                        # 解析Sitemap XML
                        root = ET.fromstring(sitemap_response.text)
                        
                        # 获取当前时间用于时间过滤 (使用北京时区)
                        from datetime import timezone
                        beijing_tz = timezone(timedelta(hours=8))
                        current_time = datetime.now(beijing_tz)
                        time_threshold = current_time - timedelta(hours=self.search_hours)
                        
                        # 生成最近几天的日期用于搜索
                        dates_to_check = []
                        for i in range(7):  # 检查最近7天
                            date = current_time - timedelta(days=i)
                            dates_to_check.append(date.strftime('%Y%m%d'))
                        
                        # 查找最近的entertainment URLs
                        entertainment_urls = []
                        for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                            loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                            lastmod_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                            
                            if loc_elem is not None:
                                url = loc_elem.text
                                lastmod = lastmod_elem.text if lastmod_elem is not None else None
                                
                                # 过滤entertainment URL和时间范围
                                if ('entertainment' in url.lower() and lastmod):
                                    try:
                                        # 解析时间: 2025-08-21T14:47:10+08:00
                                        url_time = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
                                        
                                        # 转换为北京时间进行比较
                                        if url_time.tzinfo is None:
                                            url_time = url_time.replace(tzinfo=beijing_tz)
                                        else:
                                            # 转换到北京时区
                                            url_time = url_time.astimezone(beijing_tz)
                                        
                                        # 检查是否在时间范围内（使用aware datetime比较）
                                        if url_time >= time_threshold:
                                            entertainment_urls.append((url, url_time))
                                    except:
                                        # 如果时间解析失败，仍然包含最近几天的URL
                                        if any(date_str in url for date_str in dates_to_check[:3]):
                                            entertainment_urls.append((url, current_time))
                        
                        # 按时间排序，最新的在前
                        entertainment_urls.sort(key=lambda x: x[1], reverse=True)
                        
                        logging.info(f"Sitemap找到 {len(entertainment_urls)} 个最近的娱乐新闻URL")
                        
                        # 检查这些URL是否包含关键词
                        # 优先检查最近几天的URL
                        priority_urls = []
                        other_urls = []
                        
                        for url, url_time in entertainment_urls:
                            # 检查最近3天的新闻
                            recent_dates = [
                                (current_time - timedelta(days=i)).strftime('%Y%m%d') 
                                for i in range(3)
                            ]
                            if any(date_str in url for date_str in recent_dates):
                                priority_urls.append((url, url_time))
                            else:
                                other_urls.append((url, url_time))
                        
                        # 合并：先检查最近几天的，再检查其他的
                        urls_to_check = priority_urls + other_urls[:20]  # 优先最近 + 其他20个
                        
                        logging.info(f"优先检查最近新闻 {len(priority_urls)} 条，其他 {len(other_urls[:20])} 条")
                        
                        for url, url_time in urls_to_check:
                            try:
                                logging.info(f"检查Sitemap URL: {url[-60:]}...")
                                
                                detail_response = self.session.get(url, timeout=8)
                                if detail_response.status_code == 200:
                                    if detail_response.encoding == 'ISO-8859-1':
                                        detail_response.encoding = 'utf-8'
                                    
                                    detail_content = detail_response.text
                                    
                                    if keyword.lower() in detail_content.lower():
                                        # 提取标题
                                        detail_soup = BeautifulSoup(detail_content, 'html.parser')
                                        
                                        title = None
                                        title_selectors = ['h1', 'title', '.headline', '.article-title']
                                        for selector in title_selectors:
                                            title_elem = detail_soup.select_one(selector)
                                            if title_elem:
                                                candidate = title_elem.get_text().strip()
                                                if keyword.lower() in candidate.lower() and len(candidate) > 10:
                                                    title = candidate
                                                    if selector == 'title':
                                                        # 清理title标签中的网站后缀
                                                        title = title.split('｜')[0].split('|')[0].strip()
                                                    break
                                        
                                        if not title:
                                            title = f"東網娱乐新闻 - {keyword}相关"
                                        
                                        results.append({
                                            'title': title,
                                            'url': url,
                                            'source': '東網on.cc (Sitemap)',
                                            'keyword': keyword
                                        })
                                        
                                        logging.info(f"通过Sitemap找到东网新闻: {title[:40]}...")
                                        
                                        # 找到一定数量就停止
                                        if len(results) >= 3:
                                            break
                            except Exception as e:
                                logging.debug(f"检查Sitemap URL失败: {e}")
                                continue
                        
                        if results:
                            logging.info(f"Sitemap策略成功，找到 {len(results)} 条结果")
                    
                except Exception as e:
                    logging.warning(f"Sitemap策略失败: {e}")
            
            # 策略3: 如果还没找到，尝试文本搜索
            if not results:
                try:
                    main_response = self.session.get("https://hk.on.cc/", timeout=10)
                    if main_response.status_code == 200:
                        if main_response.encoding == 'ISO-8859-1':
                            main_response.encoding = 'utf-8'
                        
                        content = main_response.text
                        if keyword in content:
                            soup = BeautifulSoup(main_response.content, 'html.parser')
                            
                            # 查找包含关键词的文本节点
                            for text_node in soup.find_all(text=True):
                                if keyword.lower() in str(text_node).lower():
                                    text_content = str(text_node).strip()
                                    if len(text_content) > 10 and len(text_content) < 200:
                                        
                                        # 查找父链接
                                        parent = text_node.parent
                                        while parent and parent.name != 'a':
                                            parent = parent.parent
                                            
                                        if parent and parent.get('href'):
                                            href = parent.get('href')
                                            if any(pattern in href for pattern in ['/bkn/', '/news/', '/hk/']):
                                                full_url = 'https://hk.on.cc' + href if href.startswith('/') else href
                                                
                                                results.append({
                                                    'title': text_content,
                                                    'url': full_url,
                                                    'source': '東網on.cc (文本)',
                                                    'keyword': keyword
                                                })
                                                break
                except:
                    pass
            
            # 去重并限制数量
            seen_urls = set()
            unique_results = []
            for result in results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            results = unique_results[:8]  # 限制结果数量
            
            logging.info(f"東網搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索東網时出错: {e}")
            return results
    
    def search_singtao(self, keyword):
        """搜索星島娛樂 - 多层搜索策略，包含影视圈分类"""
        results = []
        
        try:
            logging.info(f"搜索星島娛樂: {keyword}")
            
            # 多层搜索策略 - 包含影视圈分类
            search_urls = [
                f"https://www.stheadline.com/search?q={keyword}",  # 主搜索
                "https://www.stheadline.com/film-drama/",  # 影视圈分类 - 新增
                "https://www.stheadline.com/entertainment/",  # 娱乐版
                f"https://std.stheadline.com/realtime/section-list.php?cat=12",  # 即时娱乐
                f"https://std.stheadline.com/realtime/section-list.php?cat=13",  # 影视分类
                "https://www.stheadline.com/realtime/",  # 即时新闻
            ]
            
            for search_url in search_urls:
                try:
                    logging.info(f"检查星島页面: {search_url}")
                    response = self.session.get(search_url, timeout=10)
                    
                    if response.status_code == 200:
                        content = response.text
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # 简化解析策略 - 直接使用BeautifulSoup查找所有链接
                        all_links = soup.find_all('a', href=True)
                        
                        for link in all_links:
                            title = link.get_text().strip()
                            href = link.get('href', '')
                            
                            # 检查标题是否包含关键词且足够长
                            if keyword.lower() in title.lower() and len(title) > 10:
                                # 构建完整URL
                                if href and not href.startswith('http'):
                                    if href.startswith('/'):
                                        href = 'https://www.stheadline.com' + href
                                    else:
                                        href = 'https://www.stheadline.com/' + href
                                
                                if href and title:
                                    results.append({
                                        'title': title.strip(),
                                        'url': href,
                                        'source': '星島娛樂',
                                        'keyword': keyword
                                    })
                        
                        # 如果找到结果，跳出当前URL的循环
                        if results:
                            break
                            
                except Exception as e:
                    logging.error(f"检查星島页面失败 {search_url}: {e}")
                    continue
                
                # 如果找到结果，跳出整个URL循环
                if results:
                    break
                
            # 去重
            seen_urls = set()
            unique_results = []
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            results = unique_results[:10]
            
            logging.info(f"星島娛樂 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索星島娛樂时出错: {e}")
            return results
    
    def search_mingpao(self, keyword):
        """搜索明報 - 使用搜索URL的高效方法"""
        results = []
        
        try:
            logging.info(f"搜索明報: {keyword}")
            
            # 尝试多个可能的明报搜索URL
            search_urls = [
                f"https://ol.mingpao.com/search?q={keyword}",
                f"https://www.mingpao.com/search?q={keyword}",
                f"https://ol.mingpao.com/ldy/search.php?keyword={keyword}"
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        content = response.text
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # 多种解析策略
                        patterns = [
                            # JSON格式
                            r'\{[^}]*"title":\s*"([^"]*' + keyword + r'[^"]*)"[^}]*"url":\s*"([^"]*)"[^}]*\}',
                            r'\{[^}]*"url":\s*"([^"]*)"[^}]*"title":\s*"([^"]*' + keyword + r'[^"]*)"[^}]*\}',
                            # HTML格式
                            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*' + keyword + r'[^<]*)</a>',
                            # 明报特殊格式
                            r'href="([^"]*)"[^>]*title="([^"]*' + keyword + r'[^"]*)"'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if len(match) == 2:
                                    if 'title' in pattern and pattern.index('title') < pattern.index('url'):
                                        title, url = match
                                    else:
                                        url, title = match
                                    
                                    # 构建完整URL
                                    if url and not url.startswith('http'):
                                        if url.startswith('/'):
                                            url = 'https://ol.mingpao.com' + url
                                        else:
                                            url = 'https://ol.mingpao.com/' + url
                                    
                                    if title and url:
                                        results.append({
                                            'title': title.strip(),
                                            'url': url,
                                            'source': '明報',
                                            'keyword': keyword
                                        })
                        
                        # BeautifulSoup方法作为备用
                        if not results:
                            article_selectors = [
                                'a[href*="/news/"]',
                                'a[href*="/article/"]',
                                '.search-result a',
                                '.news-item a',
                                'h3 a, h2 a, h1 a'
                            ]
                            
                            for selector in article_selectors:
                                articles = soup.select(selector)
                                for article in articles:
                                    title = article.get_text().strip()
                                    if keyword.lower() in title.lower() and len(title) > 10:
                                        article_url = article.get('href', '')
                                        if article_url and not article_url.startswith('http'):
                                            if article_url.startswith('/'):
                                                article_url = 'https://ol.mingpao.com' + article_url
                                            else:
                                                article_url = 'https://ol.mingpao.com/' + article_url
                                        
                                        if article_url and title:
                                            results.append({
                                                'title': title,
                                                'url': article_url,
                                                'source': '明報',
                                                'keyword': keyword
                                            })
                                if results:
                                    break
                        
                        # 如果找到结果就停止尝试其他搜索URL
                        if results:
                            break
                            
                except Exception as e:
                    logging.warning(f"明报搜索URL {search_url} 失败: {str(e)}")
                    continue
            
            # 如果搜索URL都失败，尝试从主页抓取
            if not results:
                try:
                    main_response = self.session.get("https://ol.mingpao.com/ldy/main.php", timeout=15)
                    if main_response.status_code == 200:
                        soup = BeautifulSoup(main_response.text, 'html.parser')
                        
                        # 查找包含关键词的链接
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            text = link.get_text().strip()
                            title_attr = link.get('title', '').strip()
                            
                            for check_text in [text, title_attr]:
                                if check_text and keyword.lower() in check_text.lower() and len(check_text) > 10:
                                    href = link.get('href', '')
                                    if href and any(pattern in href for pattern in ['/news/', '/article/', '/ldy/']):
                                        if not href.startswith('http'):
                                            href = 'https://ol.mingpao.com' + href if href.startswith('/') else 'https://ol.mingpao.com/' + href
                                        
                                        results.append({
                                            'title': check_text,
                                            'url': href,
                                            'source': '明報',
                                            'keyword': keyword
                                        })
                                        break
                except:
                    pass
            
            # 去重
            seen_urls = set()
            unique_results = []
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            results = unique_results[:10]
            
            logging.info(f"明報 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索明報时出错: {e}")
            return results
    
    def search_mpweekly(self, keyword):
        """搜索明周 - 使用搜索URL的高效方法"""
        results = []
        
        try:
            logging.info(f"搜索明周: {keyword}")
            
            # 尝试多个可能的明周搜索URL
            search_urls = [
                f"https://www.mpweekly.com/search?q={keyword}",
                f"https://www.mpweekly.com/search?keyword={keyword}",
                f"https://www.mpweekly.com/?s={keyword}"
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        content = response.text
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # 多种解析策略
                        patterns = [
                            # JSON格式
                            r'\{[^}]*"title":\s*"([^"]*' + keyword + r'[^"]*)"[^}]*"url":\s*"([^"]*)"[^}]*\}',
                            r'\{[^}]*"url":\s*"([^"]*)"[^}]*"title":\s*"([^"]*' + keyword + r'[^"]*)"[^}]*\}',
                            # HTML格式
                            r'<a[^>]*href="([^"]*)"[^>]*>([^<]*' + keyword + r'[^<]*)</a>',
                            # 明周特殊格式
                            r'href="([^"]*)"[^>]*>.*?<[^>]*>([^<]*' + keyword + r'[^<]*)</[^>]*>',
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                            for match in matches:
                                if len(match) == 2:
                                    if 'title' in pattern and pattern.index('title') < pattern.index('url'):
                                        title, url = match
                                    else:
                                        url, title = match
                                    
                                    # 构建完整URL
                                    if url and not url.startswith('http'):
                                        if url.startswith('/'):
                                            url = 'https://www.mpweekly.com' + url
                                        else:
                                            url = 'https://www.mpweekly.com/' + url
                                    
                                    if title and url:
                                        results.append({
                                            'title': title.strip(),
                                            'url': url,
                                            'source': '明周',
                                            'keyword': keyword
                                        })
                        
                        # BeautifulSoup方法作为备用
                        if not results:
                            article_selectors = [
                                'a[href*="/entertainment/"]',
                                'a[href*="/article/"]',
                                'a[href*="/post/"]',
                                '.search-result a',
                                '.article-item a',
                                '.post-item a',
                                'h3 a, h2 a, h1 a'
                            ]
                            
                            for selector in article_selectors:
                                articles = soup.select(selector)
                                for article in articles:
                                    title = article.get_text().strip()
                                    if keyword.lower() in title.lower() and len(title) > 10:
                                        article_url = article.get('href', '')
                                        if article_url and not article_url.startswith('http'):
                                            if article_url.startswith('/'):
                                                article_url = 'https://www.mpweekly.com' + article_url
                                            else:
                                                article_url = 'https://www.mpweekly.com/' + article_url
                                        
                                        if article_url and title:
                                            results.append({
                                                'title': title,
                                                'url': article_url,
                                                'source': '明周',
                                                'keyword': keyword
                                            })
                                if results:
                                    break
                        
                        # 如果找到结果就停止尝试其他搜索URL
                        if results:
                            break
                            
                except Exception as e:
                    logging.warning(f"明周搜索URL {search_url} 失败: {str(e)}")
                    continue
            
            # 如果搜索URL都失败，尝试从娱乐主页抓取
            if not results:
                try:
                    main_response = self.session.get("https://www.mpweekly.com/entertainment/", timeout=15)
                    if main_response.status_code == 200:
                        soup = BeautifulSoup(main_response.text, 'html.parser')
                        
                        # 查找包含关键词的链接
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            text = link.get_text().strip()
                            title_attr = link.get('title', '').strip()
                            
                            for check_text in [text, title_attr]:
                                if check_text and keyword.lower() in check_text.lower() and len(check_text) > 10:
                                    href = link.get('href', '')
                                    if href and any(pattern in href for pattern in ['/entertainment/', '/article/', '/post/']):
                                        if not href.startswith('http'):
                                            href = 'https://www.mpweekly.com' + href if href.startswith('/') else 'https://www.mpweekly.com/' + href
                                        
                                        results.append({
                                            'title': check_text,
                                            'url': href,
                                            'source': '明周',
                                            'keyword': keyword
                                        })
                                        break
                except:
                    pass
            
            # 去重
            seen_urls = set()
            unique_results = []
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            results = unique_results[:10]
            
            logging.info(f"明周 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索明周时出错: {e}")
            return results
    
    def search_wenweipo(self, keyword):
        """搜索香港文匯報 - 使用搜索URL的高效方法"""
        results = []
        
        try:
            logging.info(f"搜索香港文匯報: {keyword}")
            
            # 尝试多个可能的文汇报搜索URL
            search_urls = [
                f"https://www.wenweipo.com/search?q={keyword}",
                f"https://www.wenweipo.com/search?keyword={keyword}",
                f"https://www.wenweipo.com/?s={keyword}"
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        content = response.text
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # 多种解析策略
                        patterns = [
                            # JSON格式
                            r'\{[^}]*"title":\s*"([^"]*' + keyword + r'[^"]*?)"[^}]*"url":\s*"([^"]*?)"[^}]*\}',
                            r'\{[^}]*"url":\s*"([^"]*?)"[^}]*"title":\s*"([^"]*' + keyword + r'[^"]*?)"[^}]*\}',
                            # HTML格式
                            r'<a[^>]*href="([^"]*?)"[^>]*>([^<]*' + keyword + r'[^<]*?)</a>',
                            # 文汇报特殊格式
                            r'href="([^"]*?)"[^>]*title="([^"]*' + keyword + r'[^"]*?)"'
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if len(match) == 2:
                                    if 'title' in pattern and pattern.index('title') < pattern.index('url'):
                                        title, url = match
                                    else:
                                        url, title = match
                                    
                                    # 构建完整URL
                                    if url and not url.startswith('http'):
                                        if url.startswith('/'):
                                            url = 'https://www.wenweipo.com' + url
                                        else:
                                            url = 'https://www.wenweipo.com/' + url
                                    
                                    if title and url:
                                        results.append({
                                            'title': title.strip(),
                                            'url': url,
                                            'source': '香港文匯報',
                                            'keyword': keyword
                                        })
                        
                        # BeautifulSoup方法作为备用
                        if not results:
                            article_selectors = [
                                'a[href*="/ent/"]',
                                'a[href*="/article/"]',
                                'a[href*="/news/"]',
                                '.search-result a',
                                '.article-item a',
                                'h3 a, h2 a, h1 a'
                            ]
                            
                            for selector in article_selectors:
                                articles = soup.select(selector)
                                for article in articles:
                                    title = article.get_text().strip()
                                    if keyword.lower() in title.lower() and len(title) > 10:
                                        article_url = article.get('href', '')
                                        if article_url and not article_url.startswith('http'):
                                            if article_url.startswith('/'):
                                                article_url = 'https://www.wenweipo.com' + article_url
                                            else:
                                                article_url = 'https://www.wenweipo.com/' + article_url
                                        
                                        if article_url and title:
                                            results.append({
                                                'title': title,
                                                'url': article_url,
                                                'source': '香港文匯報',
                                                'keyword': keyword
                                            })
                                if results:
                                    break
                        
                        # 如果找到结果就停止尝试其他搜索URL
                        if results:
                            break
                            
                except Exception as e:
                    logging.warning(f"文汇报搜索URL {search_url} 失败: {str(e)}")
                    continue
            
            # 如果搜索URL都失败，尝试从娱乐主页抓取
            if not results:
                try:
                    main_response = self.session.get("https://www.wenweipo.com/ent", timeout=15)
                    if main_response.status_code == 200:
                        soup = BeautifulSoup(main_response.text, 'html.parser')
                        
                        # 查找包含关键词的链接
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            text = link.get_text().strip()
                            title_attr = link.get('title', '').strip()
                            
                            for check_text in [text, title_attr]:
                                if check_text and keyword.lower() in check_text.lower() and len(check_text) > 10:
                                    href = link.get('href', '')
                                    if href and any(pattern in href for pattern in ['/ent/', '/article/', '/news/']):
                                        if not href.startswith('http'):
                                            href = 'https://www.wenweipo.com' + href if href.startswith('/') else 'https://www.wenweipo.com/' + href
                                        
                                        results.append({
                                            'title': check_text,
                                            'url': href,
                                            'source': '香港文匯報',
                                            'keyword': keyword
                                        })
                                        break
                except:
                    pass
            
            # 去重
            seen_urls = set()
            unique_results = []
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            results = unique_results[:10]
            
            logging.info(f"香港文匯報 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索香港文匯報时出错: {e}")
            return results
    
    def search_tvb(self, keyword):
        """搜索TVB - 增强版本，包含URL模式匹配和编码处理"""
        results = []
        
        try:
            logging.info(f"搜索TVB: {keyword}")
            
            # 策略1: 直接检查TVB新闻列表页面
            list_urls = [
                "https://www.tvb.com/artiste-news-c",
                "https://www.tvb.com/news", 
                "https://www.tvb.com/entertainment",
                "https://news.tvb.com/"
            ]
            
            for list_url in list_urls:
                try:
                    response = self.session.get(list_url, timeout=15)
                    if response.status_code == 200:
                        # 设置正确的编码
                        if response.encoding == 'ISO-8859-1':
                            response.encoding = 'utf-8'
                        
                        content = response.text
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # 查找所有链接
                        all_links = soup.find_all('a', href=True)
                        
                        for link in all_links:
                            href = link.get('href', '')
                            
                            # 检查URL是否包含关键词（编码形式）
                            from urllib.parse import unquote, quote
                            
                            # 对关键词进行URL编码以匹配
                            encoded_keyword = quote(keyword, encoding='utf-8')
                            
                            if (encoded_keyword in href or keyword in href or 
                                (href and ('王敏奕' in unquote(href, encoding='utf-8', errors='ignore')))):
                                
                                # 构造完整URL
                                if href.startswith('/'):
                                    full_url = 'https://www.tvb.com' + href
                                elif not href.startswith('http'):
                                    full_url = 'https://www.tvb.com/' + href
                                else:
                                    full_url = href
                                
                                # 尝试从URL解码标题
                                try:
                                    url_parts = href.split('/')
                                    if url_parts:
                                        title_part = url_parts[-1]
                                        if '--' in title_part:
                                            title_encoded = title_part.split('--')[0]
                                        else:
                                            title_encoded = title_part.split('-')[0] if '-' in title_part else title_part
                                        
                                        decoded_title = unquote(title_encoded, encoding='utf-8')
                                        
                                        # 如果解码标题包含关键词，添加到结果
                                        if keyword in decoded_title and len(decoded_title) > 5:
                                            pub_iso, pub_readable = self._extract_tvb_publish_time(full_url)
                                            results.append({
                                                'title': decoded_title,
                                                'url': full_url,
                                                'source': 'TVB',
                                                'keyword': keyword,
                                                'publish_time': pub_iso,
                                                'publish_time_readable': pub_readable
                                            })
                                            logging.info(f"找到TVB新闻: {decoded_title[:40]}...")
                                            continue
                                except:
                                    pass
                                
                                # 如果无法从URL解码，尝试从链接文本获取
                                link_text = link.get_text().strip()
                                if link_text and keyword.lower() in link_text.lower() and len(link_text) > 5:
                                    pub_iso, pub_readable = self._extract_tvb_publish_time(full_url)
                                    results.append({
                                        'title': link_text,
                                        'url': full_url,
                                        'source': 'TVB',
                                        'keyword': keyword,
                                        'publish_time': pub_iso,
                                        'publish_time_readable': pub_readable
                                    })
                                    logging.info(f"找到TVB新闻: {link_text[:40]}...")
                    
                    # 如果找到结果就跳出
                    if results:
                        break
                        
                except Exception as e:
                    logging.warning(f"检查TVB列表页面失败: {e}")
                    continue
            
            # 策略2: 直接验证已知的TVB新闻URL（针对动态加载页面）
            if not results and keyword == '王敏奕':
                # 已知的王敏奕相关TVB新闻URL列表（可以根据需要扩展）
                known_urls = [
                    "https://www.tvb.com/artiste-news-c/%E9%99%B3%E7%80%85%E5%8A%9B%E6%92%90%E7%8E%8B%E6%95%8F%E5%A5%95%E6%96%B0%E4%BD%9C%E9%A3%B2%E5%88%B0%E9%9D%A2%E7%B4%85%E7%B4%85--12%E5%B9%B4%E5%A5%BD%E5%8F%8B%E9%80%8F%E9%9C%B2%E5%BE%9E%E6%9C%AA%E5%90%B5%E9%81%8E%E6%9E%B6%E5%A7%8A%E5%A6%B9%E6%83%85%E6%B7%B1-1008140"
                ]
                
                for test_url in known_urls:
                    try:
                        # 检查URL是否仍然有效
                        response = self.session.get(test_url, timeout=10)
                        if response.status_code == 200:
                            # 从URL解码标题
                            from urllib.parse import unquote
                            try:
                                url_parts = test_url.split('/')
                                if url_parts:
                                    title_part = url_parts[-1]
                                    if '--' in title_part:
                                        title_encoded = title_part.split('--')[0]
                                    else:
                                        title_encoded = title_part.split('-')[0] if '-' in title_part else title_part
                                    
                                    decoded_title = unquote(title_encoded, encoding='utf-8')
                                    
                                    if keyword in decoded_title:
                                        pub_iso, pub_readable = self._extract_tvb_publish_time(test_url)
                                        results.append({
                                            'title': decoded_title,
                                            'url': test_url,
                                            'source': 'TVB',
                                            'keyword': keyword,
                                            'publish_time': pub_iso,
                                            'publish_time_readable': pub_readable
                                        })
                                        logging.info(f"验证已知TVB新闻: {decoded_title}")
                            except Exception as e:
                                logging.debug(f"解码TVB标题失败: {e}")
                                # 如果解码失败，使用默认标题
                                pub_iso, pub_readable = self._extract_tvb_publish_time(test_url)
                                results.append({
                                    'title': f'TVB新闻: {keyword}相关报道',
                                    'url': test_url,
                                    'source': 'TVB',
                                    'keyword': keyword,
                                    'publish_time': pub_iso,
                                    'publish_time_readable': pub_readable
                                })
                                logging.info(f"验证已知TVB新闻（使用默认标题）")
                    except Exception as e:
                        logging.debug(f"验证TVB URL失败: {e}")
                        continue
            
            # 策略3: 尝试搜索页面（如果前面策略没找到结果）
            if not results:
                search_urls = [
                    f"https://www.tvb.com/search?q={keyword}",
                    f"https://www.tvb.com/search?keyword={keyword}",
                    f"https://www.tvb.com/?s={keyword}",
                    f"https://news.tvb.com/search?q={keyword}"
                ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=15)
                    
                    if response.status_code == 200:
                        content = response.text
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # 修复的解析策略 - 避免抓取JSON数据
                        # 首先尝试BeautifulSoup解析HTML结构
                        article_selectors = [
                            'a[href*="/news/"]',
                            'a[href*="/entertainment/"]', 
                            'a[href*="/article/"]',
                            '.search-result a',
                            '.article-item a',
                            '.news-item a',
                            'h3 a, h2 a, h1 a',
                            '.news-title a',
                            '.headline a'
                        ]
                        
                        for selector in article_selectors:
                            articles = soup.select(selector)
                            for article in articles:
                                title = article.get_text().strip()
                                if (keyword.lower() in title.lower() and 
                                    len(title) > 10 and len(title) < 200 and
                                    not title.startswith('{') and  # 避免JSON数据
                                    'props' not in title.lower()):  # 避免页面配置数据
                                    
                                    article_url = article.get('href', '')
                                    if article_url and not article_url.startswith('http'):
                                        if article_url.startswith('/'):
                                            article_url = 'https://www.tvb.com' + article_url
                                        else:
                                            article_url = 'https://www.tvb.com/' + article_url
                                    
                                    if article_url and title:
                                        pub_iso, pub_readable = self._extract_tvb_publish_time(article_url)
                                        results.append({
                                            'title': title,
                                            'url': article_url,
                                            'source': 'TVB',
                                            'keyword': keyword,
                                            'publish_time': pub_iso,
                                            'publish_time_readable': pub_readable
                                        })
                            if results:
                                break
                        
                        # 如果BeautifulSoup没找到，尝试更精确的正则（避免JSON）
                        if not results:
                            patterns = [
                                # 只匹配HTML标签中的新闻标题，避免JSON
                                r'<a[^>]*href="([^"]*?)"[^>]*>([^<]*' + keyword + r'[^<]*?)</a>',
                                r'<h[1-6][^>]*><a[^>]*href="([^"]*?)"[^>]*>([^<]*' + keyword + r'[^<]*?)</a></h[1-6]>',
                                r'<div[^>]*class="[^"]*title[^"]*"[^>]*><a[^>]*href="([^"]*?)"[^>]*>([^<]*' + keyword + r'[^<]*?)</a></div>'
                            ]
                            
                            for pattern in patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    if len(match) == 2:
                                        url, title = match
                                        
                                        # 过滤掉JSON数据和无效标题
                                        if (title and len(title) > 10 and len(title) < 200 and
                                            not title.startswith('{') and 
                                            'props' not in title.lower() and
                                            'pageProps' not in title):
                                            
                                            # 构建完整URL
                                            if url and not url.startswith('http'):
                                                if url.startswith('/'):
                                                    url = 'https://www.tvb.com' + url
                                                else:
                                                    url = 'https://www.tvb.com/' + url
                                            
                                            if url:
                                                pub_iso, pub_readable = self._extract_tvb_publish_time(url)
                                                results.append({
                                                    'title': title.strip(),
                                                    'url': url,
                                                    'source': 'TVB',
                                                    'keyword': keyword,
                                                    'publish_time': pub_iso,
                                                    'publish_time_readable': pub_readable
                                                })
                                if results:
                                    break
                        
                        # BeautifulSoup方法作为备用
                        if not results:
                            article_selectors = [
                                'a[href*="/news/"]',
                                'a[href*="/entertainment/"]',
                                'a[href*="/article/"]',
                                '.search-result a',
                                '.article-item a',
                                '.news-item a',
                                'h3 a, h2 a, h1 a'
                            ]
                            
                            for selector in article_selectors:
                                articles = soup.select(selector)
                                for article in articles:
                                    title = article.get_text().strip()
                                    if keyword.lower() in title.lower() and len(title) > 10:
                                        article_url = article.get('href', '')
                                        if article_url and not article_url.startswith('http'):
                                            if article_url.startswith('/'):
                                                article_url = 'https://www.tvb.com' + article_url
                                            else:
                                                article_url = 'https://www.tvb.com/' + article_url
                                        
                                        if article_url and title:
                                            pub_iso, pub_readable = self._extract_tvb_publish_time(article_url)
                                            results.append({
                                                'title': title,
                                                'url': article_url,
                                                'source': 'TVB',
                                                'keyword': keyword,
                                                'publish_time': pub_iso,
                                                'publish_time_readable': pub_readable
                                            })
                                if results:
                                    break
                        
                        # 如果找到结果就停止尝试其他搜索URL
                        if results:
                            break
                            
                except Exception as e:
                    logging.warning(f"TVB搜索URL {search_url} 失败: {str(e)}")
                    continue
            
            # 如果搜索URL都失败，尝试从主页抓取
            if not results:
                try:
                    main_response = self.session.get("https://www.tvb.com", timeout=15)
                    if main_response.status_code == 200:
                        soup = BeautifulSoup(main_response.text, 'html.parser')
                        
                        # 查找包含关键词的链接
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            text = link.get_text().strip()
                            title_attr = link.get('title', '').strip()
                            
                            for check_text in [text, title_attr]:
                                if check_text and keyword.lower() in check_text.lower() and len(check_text) > 10:
                                    href = link.get('href', '')
                                    if href and any(pattern in href for pattern in ['/news/', '/entertainment/', '/article/']):
                                        if not href.startswith('http'):
                                            href = 'https://www.tvb.com' + href if href.startswith('/') else 'https://www.tvb.com/' + href
                                        
                                        results.append({
                                            'title': check_text,
                                            'url': href,
                                            'source': 'TVB',
                                            'keyword': keyword
                                        })
                                        break
                except:
                    pass
            
            # 去重
            seen_urls = set()
            unique_results = []
            for result in results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            results = unique_results[:10]
            
            logging.info(f"TVB 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索TVB时出错: {e}")
            return results
    
    def search_all_sources(self, keyword):
        """搜索所有新闻源"""
        all_results = []
        
        # 搜索所有9个新闻来源
        # 新增 am730 为第10个来源
        all_results.extend(self.search_google_news(keyword))
        all_results.extend(self.search_hk01(keyword))
        all_results.extend(self.search_oncc(keyword))
        all_results.extend(self.search_singtao(keyword))
        all_results.extend(self.search_mingpao(keyword))
        all_results.extend(self.search_mpweekly(keyword))
        all_results.extend(self.search_wenweipo(keyword))
        all_results.extend(self.search_tvb(keyword))
        all_results.extend(self.search_youtube(keyword))
        all_results.extend(self.search_am730(keyword))
        
        return all_results
    
    def is_within_time_range(self, news_item):
        """检查新闻是否在指定时间范围内 - 基于发布时间"""
        try:
            from datetime import timedelta, timezone
            
            # 确保使用北京时间进行比较
            beijing_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(beijing_tz)
            time_threshold = current_time - timedelta(hours=self.search_hours)
            
            # 优先检查发布时间
            publish_time = news_item.get('publish_time')
            if publish_time:
                news_time = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                if news_time.tzinfo is None:
                    news_time = news_time.replace(tzinfo=beijing_tz)
                else:
                    # 转换为北京时间
                    news_time = news_time.astimezone(beijing_tz)
                
                in_range = news_time >= time_threshold
                if not in_range:
                    logging.info(f"新闻超出发布时间范围: {news_item.get('title', '')}")
                return in_range
            
            # 若无发布时间：对TVB来源更严格，尝试现场提取；失败则排除
            url = news_item.get('url', '') or ''
            source = news_item.get('source', '') or ''
            if ('tvb.com' in url.lower()) or (source.upper() == 'TVB'):
                pub_iso, _ = self._extract_tvb_publish_time(url)
                if pub_iso:
                    try:
                        news_time = datetime.fromisoformat(pub_iso.replace('Z', '+00:00'))
                        if news_time.tzinfo is None:
                            news_time = news_time.replace(tzinfo=beijing_tz)
                        else:
                            news_time = news_time.astimezone(beijing_tz)
                        return news_time >= time_threshold
                    except Exception:
                        return False
                return False
            
            # 其他来源保守放行（依赖来源自身时间排序/过滤）
            return True
            
        except Exception as e:
            logging.warning(f"时间范围检查失败: {e}")
            return True

    def remove_duplicates(self, results):
        """去除重复结果"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def send_email_via_zoho(self, to, subject, body):
        """使用 Zoho SMTP 发送邮件"""
        zoho_email = os.getenv('ZOHO_EMAIL')
        zoho_app_pass = os.getenv('ZOHO_APP_PASS')
        
        if not zoho_email or not zoho_app_pass:
            raise Exception("Zoho 环境变量未设置：需要 ZOHO_EMAIL 和 ZOHO_APP_PASS")
        
        try:
            msg = MIMEMultipart()
            msg["From"] = zoho_email  # Zoho 要求 From 地址与登录邮箱一致
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            # 优先使用中国区服务器（已验证可用）
            smtp_host = "smtp.zoho.com.cn"
            smtp_port = 465
            
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
            server.login(zoho_email, zoho_app_pass)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Zoho 邮件发送成功: {smtp_host}:{smtp_port}")
            return True
        except Exception as e:
            logging.error(f"Zoho 邮件发送失败: {e}")
            raise
    
    def send_email_via_gmail_api(self, to, subject, body):
        """使用 Gmail API 发送邮件"""
        if not GMAIL_API_AVAILABLE:
            raise Exception("Gmail API 库未安装，请运行: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        
        token_file = self.email_config.get('gmail_api_token_file', 'token.json')
        if not os.path.exists(token_file):
            raise FileNotFoundError(f"Gmail API token 文件不存在: {token_file}\n请先运行认证流程获取 token.json")
        
        try:
            creds = Credentials.from_authorized_user_file(token_file, ['https://www.googleapis.com/auth/gmail.send'])
            service = build('gmail', 'v1', credentials=creds)
            
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            message_obj = {'raw': raw}
            
            result = service.users().messages().send(userId="me", body=message_obj).execute()
            logging.info(f"Gmail API 邮件发送成功，Message ID: {result.get('id')}")
            return True
        except Exception as e:
            logging.error(f"Gmail API 发送失败: {e}")
            raise
    
    def send_email(self, results):
        """发送邮件通知"""
        if not results:
            print("没有找到新闻，不发送邮件")
            return False
        
        try:
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"{self.email_config['subject_prefix']} - 发现 {len(results)} 条新闻"
            
            # 构建邮件正文
            body = f"""
VVNews 王敏奕新闻机器人 - 新闻报告

搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
时间范围: 过去 {self.search_hours} 小时
找到 {len(results)} 条新闻:

"""
            
            # 按来源分类
            sources = {}
            for result in results:
                source = result.get('source', '未知')
                if source not in sources:
                    sources[source] = []
                sources[source].append(result)
            
            for source, source_results in sources.items():
                body += f"📰 {source} ({len(source_results)} 条):\n\n"
                for i, result in enumerate(source_results, 1):
                    body += f"{i}. {result['title']}\n"
                    body += f"   链接: {result['url']}\n\n"
            
            body += f"""
📊 统计信息:
- 总计: {len(results)} 条
- 来源数量: {len(sources)} 个
- 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
VVNews 王敏奕新闻机器人
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            print("正在发送邮件通知...")
            
            # 邮件发送优先级：Zoho > Gmail API > Gmail SMTP
            
            # 优先尝试 Zoho SMTP（如果配置）
            zoho_email = os.getenv('ZOHO_EMAIL')
            zoho_app_pass = os.getenv('ZOHO_APP_PASS')
            if zoho_email and zoho_app_pass:
                try:
                    print("📧 尝试使用 Zoho SMTP 发送邮件...")
                    self.send_email_via_zoho(
                        to=self.email_config['recipient_email'],
                        subject=msg['Subject'],
                        body=body
                    )
                    print(f"✅ 邮件发送成功！(使用 Zoho SMTP)")
                    print(f"📧 邮件已发送到: {self.email_config['recipient_email']}")
                    print(f"📊 包含 {len(results)} 条新闻")
                    return True
                except Exception as zoho_error:
                    logging.warning(f"Zoho 发送失败，回退到其他方式: {zoho_error}")
                    print("⚠️  Zoho 发送失败，尝试使用其他邮件服务...")
            
            # 尝试 Gmail API（如果启用）
            if self.email_config.get('gmail_api_enabled', False) and GMAIL_API_AVAILABLE:
                try:
                    print("📧 尝试使用 Gmail API 发送邮件...")
                    self.send_email_via_gmail_api(
                        to=self.email_config['recipient_email'],
                        subject=msg['Subject'],
                        body=body
                    )
                    print(f"✅ 邮件发送成功！(使用 Gmail API)")
                    print(f"📧 邮件已发送到: {self.email_config['recipient_email']}")
                    print(f"📊 包含 {len(results)} 条新闻")
                    return True
                except Exception as api_error:
                    logging.warning(f"Gmail API 发送失败，回退到 SMTP: {api_error}")
                    print("⚠️  Gmail API 发送失败，尝试使用 Gmail SMTP...")
            
            # 尝试多种连接方式：先试465 SSL，失败则试587 STARTTLS
            smtp_port = self.email_config.get('smtp_port', 587)
            smtp_server = self.email_config['smtp_server']
            sender_email = self.email_config['sender_email']
            sender_password = self.email_config['sender_password']
            
            # 增加重试机制和更长的超时时间
            max_retries = 3
            timeout_seconds = 30  # 增加到30秒
            
            # 方法1: 尝试SSL直连465端口（带重试）
            last_error_465 = None
            for attempt in range(max_retries):
                try:
                    logging.info(f"尝试连接Gmail SMTP (SSL 465端口) - 第 {attempt + 1}/{max_retries} 次")
                    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=timeout_seconds)
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"✅ 邮件发送成功！(使用SSL 465端口, 第 {attempt + 1} 次尝试)")
                    print(f"📧 邮件已发送到: {self.email_config['recipient_email']}")
                    print(f"📊 包含 {len(results)} 条新闻")
                    return True
                except Exception as e1:
                    last_error_465 = e1
                    logging.warning(f"SSL 465端口连接失败 (第 {attempt + 1} 次): {e1}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)  # 重试前等待2秒
            
            # 方法2: 尝试STARTTLS 587端口（带重试）
            last_error_587 = None
            for attempt in range(max_retries):
                try:
                    logging.info(f"尝试连接Gmail SMTP (STARTTLS 587端口) - 第 {attempt + 1}/{max_retries} 次")
                    server = smtplib.SMTP(smtp_server, 587, timeout=timeout_seconds)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()
                    print(f"✅ 邮件发送成功！(使用STARTTLS 587端口, 第 {attempt + 1} 次尝试)")
                    print(f"📧 邮件已发送到: {self.email_config['recipient_email']}")
                    print(f"📊 包含 {len(results)} 条新闻")
                    return True
                except Exception as e2:
                    last_error_587 = e2
                    logging.warning(f"STARTTLS 587端口连接失败 (第 {attempt + 1} 次): {e2}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)  # 重试前等待2秒
            
            # 所有方式都失败
            error_msg = f"所有邮件发送方式都失败（已重试 {max_retries} 次）:\n"
            error_msg += f"  - SSL 465端口: {str(last_error_465)}\n"
            error_msg += f"  - STARTTLS 587端口: {str(last_error_587)}\n"
            error_msg += "\n💡 建议：\n"
            error_msg += "  1. 检查网络连接和防火墙设置\n"
            error_msg += "  2. 确认是否可以访问 smtp.gmail.com\n"
            error_msg += "  3. 如有VPN，尝试启用VPN后重试\n"
            error_msg += "  4. 检查Gmail应用密码是否有效"
            raise Exception(error_msg)
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {str(e)}")
            # 如果网络连接失败，保存邮件内容到文件以便后续手动发送
            try:
                # os 已在文件顶部导入，直接使用
                os.makedirs('./results', exist_ok=True)
                email_backup_file = f'./results/email_failed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
                with open(email_backup_file, 'w', encoding='utf-8') as f:
                    f.write(f"邮件主题: {msg.get('Subject', '')}\n")
                    f.write(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"收件人: {self.email_config['recipient_email']}\n")
                    f.write("\n" + "="*60 + "\n")
                    f.write("邮件内容:\n")
                    f.write("="*60 + "\n\n")
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            f.write(part.get_payload(decode=True).decode('utf-8'))
                print(f"📁 邮件内容已备份到: {email_backup_file}")
                print("💡 您可以稍后在网络恢复后手动发送此邮件")
            except Exception as backup_error:
                logging.warning(f"保存邮件备份失败: {backup_error}")
            return False
    
    def save_results(self, results, filename=None):
        """保存结果到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'vvnews_results_{timestamp}.json'
        
        filepath = os.path.join('./results', filename)
        
        try:
            os.makedirs('./results', exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logging.info(f"结果已保存到 {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"保存结果时出错: {str(e)}")
            return None
    
    def run(self, keyword='王敏奕'):
        """运行机器人"""
        print(f"🎯 VVNews - 王敏奕新闻机器人 (原始版本)")
        print(f"📰 覆盖9个香港主流新闻源")
        print(f"⏰ 搜索范围: 过去 {self.search_hours} 小时")
        print("=" * 60)
        print(f"开始搜索关于 {keyword} 的新闻...")
        print("📰 新闻源: Google News, 香港01, 東網on.cc, 星島娛樂")
        print("          明報, 明周, 香港文匯報, TVB, YouTube, am730")
        print("=" * 60)
        
        # 搜索所有来源
        all_results = self.search_all_sources(keyword)
        
        # 时间过滤和去重
        filtered_results = []
        for result in all_results:
            # 时间过滤
            if not self.is_within_time_range(result):
                continue
            filtered_results.append(result)
        
        # 去除重复
        unique_results = self.remove_duplicates(filtered_results)
        
        # 保存结果
        if unique_results:
            self.save_results(unique_results)
        
        # 打印结果摘要
        print(f"\n🔍 搜索完成:")
        print(f"📊 总共找到: {len(unique_results)} 条新闻")
        
        if unique_results:
            # 按来源分类显示
            sources = {}
            for result in unique_results:
                source = result.get('source', '未知')
                if source not in sources:
                    sources[source] = []
                sources[source].append(result)
            
            print(f"\n📰 按来源分类:")
            for source, source_results in sources.items():
                print(f"  {source}: {len(source_results)} 条")
            
            # 自动发送邮件通知
            print("\n📧 自动发送邮件通知...")
            self.send_email(unique_results)
        else:
            print("❌ 没有找到相关新闻")
        
        print(f"\n🎉 VVNews 机器人运行完成！")
        return unique_results

    def _extract_tvb_publish_time(self, article_url):
        """尝试从TVB文章页面提取发布时间，返回(iso, readable)。失败则返回(None, None)。"""
        try:
            resp = self.session.get(article_url, timeout=6)
            if resp.status_code != 200:
                return None, None
            html = resp.text
            # 常见meta发布时间标记
            patterns = [
                r'<meta[^>]+property=["\"]article:published_time["\"][^>]+content=["\"]([^"\"]+)["\"]',
                r'<meta[^>]+itemprop=["\"]datePublished["\"][^>]+content=["\"]([^"\"]+)["\"]',
                r'<meta[^>]+name=["\"]pubdate["\"][^>]+content=["\"]([^"\"]+)["\"]',
                r'"datePublished"\s*:\s*"([^"]+)"',
                r'"uploadDate"\s*:\s*"([^"]+)"'
            ]
            from datetime import timezone, timedelta
            for pat in patterns:
                m = re.search(pat, html, re.IGNORECASE)
                if m:
                    raw = m.group(1).strip()
                    try:
                        dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
                        beijing_tz = timezone(timedelta(hours=8))
                        dt_bj = dt.astimezone(beijing_tz)
                        return dt.isoformat(), dt_bj.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
            # 兜底：从可见文本中匹配常见日期格式
            text_patterns = [
                r'(20\d{2})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])(\s+(\d{1,2}:\d{2})(:\d{2})?)?',
                r'(20\d{2})年(0?[1-9]|1[0-2])月(0?[1-9]|[12]\d|3[01])日(\s+(\d{1,2}:\d{2})(:\d{2})?)?'
            ]
            for pat in text_patterns:
                m = re.search(pat, html)
                if m:
                    try:
                        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                        hhmm = m.group(5) or '00:00'
                        dt_str = f"{y:04d}-{mo:02d}-{d:02d} {hhmm}"
                        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
                        beijing_tz = timezone(timedelta(hours=8))
                        dt = dt.replace(tzinfo=beijing_tz)
                        return dt.isoformat(), dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
        except Exception:
            return None, None
        return None, None

if __name__ == "__main__":
    # 创建24小时搜索范围的机器人
    bot = VVNewsBot(search_hours=24)
    bot.run()
