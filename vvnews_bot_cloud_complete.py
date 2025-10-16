#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VVNews 王敏奕新闻机器人 - 云端完整版本
功能: 支持所有香港新闻源，适合云端部署
"""

import requests
import feedparser
import re
import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VVNewsBotCloudComplete:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 邮件配置 - 从环境变量获取
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': os.getenv('GMAIL_EMAIL', 'chingkeiwong666@gmail.com'),
            'sender_password': os.getenv('GMAIL_PASSWORD', 'scjrjhnfyohdigem'),
            'recipient_email': os.getenv('GMAIL_EMAIL', 'chingkeiwong666@gmail.com'),
            'subject_prefix': '[VVNews] 王敏奕最新新闻'
        }
    
    def search_hk01(self, keyword):
        """搜索香港01"""
        results = []
        
        try:
            logging.info(f"搜索香港01: {keyword}")
            
            url = "https://www.hk01.com/zone/2/娛樂"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # 查找包含关键词的文章
                article_pattern = r'\{[^}]*"title":\s*"[^"]*' + keyword + r'[^"]*"[^}]*\}'
                matches = re.findall(article_pattern, content, re.IGNORECASE)
                
                for match in matches:
                    title_match = re.search(r'"title":\s*"([^"]*)"', match)
                    if title_match:
                        title = title_match.group(1)
                        
                        url_match = re.search(r'"canonicalUrl":\s*"([^"]*)"', match)
                        if url_match:
                            article_url = url_match.group(1)
                            if not article_url.startswith('http'):
                                article_url = 'https://www.hk01.com' + article_url
                        else:
                            id_match = re.search(r'"articleId":\s*(\d+)', match)
                            if id_match:
                                article_url = f"https://www.hk01.com/article/{id_match.group(1)}"
                            else:
                                continue
                        
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': '香港01',
                            'keyword': keyword
                        })
            
            logging.info(f"香港01 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索香港01时出错: {e}")
            return results
    
    def search_google_news(self, keyword):
        """搜索Google News"""
        results = []
        
        try:
            logging.info(f"搜索Google新闻: {keyword}")
            
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
        """搜索YouTube - RSS优先，支持多频道与时间窗口"""
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
            cutoff_hours = float(os.getenv('SEARCH_HOURS', '24'))
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
                        within_window = diff_hours <= float(cutoff_hours)

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
    
    def search_oncc(self, keyword):
        """搜索東網on.cc"""
        results = []
        
        try:
            logging.info(f"搜索東網on.cc: {keyword}")
            
            url = "https://hk.on.cc/hk/entertainment/index.html"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', href=True)
                
                for article in articles:
                    title = article.get_text().strip()
                    if keyword in title:
                        article_url = article.get('href')
                        if not article_url.startswith('http'):
                            article_url = 'https://hk.on.cc' + article_url
                        
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': '東網on.cc',
                            'keyword': keyword
                        })
            
            logging.info(f"東網on.cc 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索東網on.cc时出错: {e}")
            return results
    
    def search_singtao(self, keyword):
        """搜索星島娛樂"""
        results = []
        
        try:
            logging.info(f"搜索星島娛樂: {keyword}")
            
            url = "https://www.stheadline.com/entertainment/"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', href=True)
                
                for article in articles:
                    title = article.get_text().strip()
                    if keyword in title:
                        article_url = article.get('href')
                        if not article_url.startswith('http'):
                            article_url = 'https://www.stheadline.com' + article_url
                        
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': '星島娛樂',
                            'keyword': keyword
                        })
            
            logging.info(f"星島娛樂 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索星島娛樂时出错: {e}")
            return results
    
    def search_mingpao(self, keyword):
        """搜索明報"""
        results = []
        
        try:
            logging.info(f"搜索明報: {keyword}")
            
            url = "https://ol.mingpao.com/ldy/main.php"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', href=True)
                
                for article in articles:
                    title = article.get_text().strip()
                    if keyword in title:
                        article_url = article.get('href')
                        if not article_url.startswith('http'):
                            article_url = 'https://ol.mingpao.com' + article_url
                        
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': '明報',
                            'keyword': keyword
                        })
            
            logging.info(f"明報 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索明報时出错: {e}")
            return results
    
    def search_mpweekly(self, keyword):
        """搜索明周"""
        results = []
        
        try:
            logging.info(f"搜索明周: {keyword}")
            
            url = "https://www.mpweekly.com/entertainment/"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', href=True)
                
                for article in articles:
                    title = article.get_text().strip()
                    if keyword in title:
                        article_url = article.get('href')
                        if not article_url.startswith('http'):
                            article_url = 'https://www.mpweekly.com' + article_url
                        
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': '明周',
                            'keyword': keyword
                        })
            
            logging.info(f"明周 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索明周时出错: {e}")
            return results
    
    def search_wenweipo(self, keyword):
        """搜索香港文匯報"""
        results = []
        
        try:
            logging.info(f"搜索香港文匯報: {keyword}")
            
            url = "https://www.wenweipo.com/"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', href=True)
                
                for article in articles:
                    title = article.get_text().strip()
                    if keyword in title:
                        article_url = article.get('href')
                        if not article_url.startswith('http'):
                            article_url = 'https://www.wenweipo.com' + article_url
                        
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': '香港文匯報',
                            'keyword': keyword
                        })
            
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
            
            url = "https://www.tvb.com"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('a', href=True)
                
                for article in articles:
                    title = article.get_text().strip()
                    if keyword in title:
                        article_url = article.get('href')
                        if not article_url.startswith('http'):
                            article_url = 'https://www.tvb.com' + article_url
                        
                        # 尝试提取发布时间
                        pub_iso, pub_readable = self._extract_tvb_publish_time(article_url)
                        results.append({
                            'title': title,
                            'url': article_url,
                            'source': 'TVB',
                            'keyword': keyword,
                            'publish_time': pub_iso,
                            'publish_time_readable': pub_readable
                        })
            
            logging.info(f"TVB 搜索完成，找到 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"搜索TVB时出错: {e}")
            return results
    
    def search_all_sources(self, keyword):
        """搜索所有新闻源"""
        all_results = []
        
        # 搜索各个来源
        all_results.extend(self.search_hk01(keyword))
        all_results.extend(self.search_google_news(keyword))
        all_results.extend(self.search_youtube(keyword))
        all_results.extend(self.search_oncc(keyword))
        all_results.extend(self.search_singtao(keyword))
        all_results.extend(self.search_mingpao(keyword))
        all_results.extend(self.search_mpweekly(keyword))
        all_results.extend(self.search_wenweipo(keyword))
        all_results.extend(self.search_tvb(keyword))
        
        return all_results

    def is_within_time_range(self, news_item, hours=None):
        """检查新闻是否在指定时间范围内，TVB 无发布时间则排除。"""
        try:
            from datetime import timedelta, timezone
            beijing_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(beijing_tz)
            if hours is None:
                hours = float(os.getenv('SEARCH_HOURS', '24'))
            time_threshold = current_time - timedelta(hours=hours)

            publish_time = news_item.get('publish_time')
            if publish_time:
                news_time = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                if news_time.tzinfo is None:
                    news_time = news_time.replace(tzinfo=beijing_tz)
                else:
                    news_time = news_time.astimezone(beijing_tz)
                return news_time >= time_threshold

            # 对 TVB 更严格：没有时间就尝试提取，失败则排除
            url = (news_item.get('url') or '').lower()
            source = (news_item.get('source') or '').upper()
            if 'tvb.com' in url or source == 'TVB':
                pub_iso, _ = self._extract_tvb_publish_time(news_item.get('url') or '')
                if not pub_iso:
                    return False
                try:
                    news_time = datetime.fromisoformat(pub_iso.replace('Z', '+00:00'))
                    if news_time.tzinfo is None:
                        news_time = news_time.replace(tzinfo=beijing_tz)
                    else:
                        news_time = news_time.astimezone(beijing_tz)
                    return news_time >= time_threshold
                except Exception:
                    return False

            # 其他来源保守放行
            return True
        except Exception:
            return True

    def _extract_tvb_publish_time(self, article_url):
        """从 TVB 页面提取发布时间，返回(iso, readable)，失败返回(None, None)。"""
        if not article_url:
            return None, None
        try:
            resp = self.session.get(article_url, timeout=6)
            if resp.status_code != 200:
                return None, None
            html = resp.text
            # 常见 meta/JSON-LD 时间
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
            # 兜底：中文/数字日期文本
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
                        from datetime import datetime as _dt
                        dt = _dt.strptime(f"{y:04d}-{mo:02d}-{d:02d} {hhmm}", '%Y-%m-%d %H:%M')
                        beijing_tz = timezone(timedelta(hours=8))
                        dt = dt.replace(tzinfo=beijing_tz)
                        return dt.isoformat(), dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
        except Exception:
            return None, None
        return None, None
    
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
    
    def send_email(self, results):
        """发送邮件通知"""
        if not results:
            print("没有找到新闻，不发送邮件")
            return False
        
        # 检查邮箱配置
        if not self.email_config['sender_password']:
            print("邮箱密码未设置，跳过邮件发送")
            return False
        
        try:
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"{self.email_config['subject_prefix']} - 发现 {len(results)} 条新闻"
            
            # 构建邮件正文
            body = f"""
VVNews 王敏奕新闻机器人 - 云端完整版本新闻报告

搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
找到 {len(results)} 条最新新闻:

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
VVNews 王敏奕新闻机器人 (云端完整版本)
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            print("正在发送邮件通知...")
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ 邮件发送成功！")
            print(f"📧 邮件已发送到: {self.email_config['recipient_email']}")
            print(f"📊 包含 {len(results)} 条新闻")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {str(e)}")
            return False
    
    def save_results(self, results, filename=None):
        """保存结果到JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'vvnews_cloud_complete_{timestamp}.json'
        
        filepath = os.path.join('./results', filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logging.info(f"结果已保存到 {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"保存结果时出错: {str(e)}")
            return None
    
    def print_summary(self, results):
        """打印结果摘要"""
        print(f"\n🔍 搜索完成:")
        print(f"📊 总共找到: {len(results)} 条新闻")
        
        if results:
            # 按来源分类
            sources = {}
            for result in results:
                source = result.get('source', '未知')
                if source not in sources:
                    sources[source] = []
                sources[source].append(result)
            
            print(f"\n📰 按来源分类:")
            for source, source_results in sources.items():
                print(f"  {source}: {len(source_results)} 条")
        else:
            print("❌ 没有找到相关新闻")
    
    def run(self, keyword='王敏奕'):
        """运行机器人"""
        print(f"🎯 VVNews - 王敏奕新闻机器人 (云端完整版本)")
        print("=" * 60)
        print(f"开始搜索关于 {keyword} 的新闻...")
        print("=" * 60)
        
        # 搜索所有来源
        all_results = self.search_all_sources(keyword)
        
        # 时间过滤 + 去重
        filtered = [r for r in all_results if self.is_within_time_range(r, hours=float(os.getenv('SEARCH_HOURS','24')))]
        unique_results = self.remove_duplicates(filtered)
        
        # 保存结果
        if unique_results:
            self.save_results(unique_results)
        
        # 打印结果摘要
        self.print_summary(unique_results)
        
        # 发送邮件
        if unique_results:
            print("\n📧 发送邮件通知...")
            self.send_email(unique_results)
        
        print(f"\n🎉 VVNews 云端完整版本机器人运行完成！")
        return unique_results

if __name__ == "__main__":
    bot = VVNewsBotCloudComplete()
    bot.run()
