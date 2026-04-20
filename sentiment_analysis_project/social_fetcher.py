"""Social media account data fetcher — SentimentIQ | Sakshi Puri | UID: 24BET10158"""
import re, json, random, math
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta

try:
    from bs4 import BeautifulSoup
    BS4 = True
except ImportError:
    BS4 = False

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_count(text):
    if not text: return 0
    text = str(text).replace(',', '').strip().upper()
    m = re.match(r'([\d.]+)\s*([KMB]?)', text)
    if not m: return 0
    num, suf = float(m.group(1)), m.group(2)
    return int(num * {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}.get(suf, 1))

def _fmt(n):
    if not n: return '0'
    if n >= 1_000_000: return f'{n/1_000_000:.1f}M'
    if n >= 1_000:     return f'{n/1_000:.1f}K'
    return str(n)

# ── URL parser ─────────────────────────────────────────────────────────────────

def parse_url(url):
    url = url.strip().rstrip('/')
    if not url.startswith('http'): url = 'https://' + url
    p = urlparse(url)
    domain = p.netloc.lower().replace('www.', '')
    parts  = [x for x in p.path.strip('/').split('/') if x]

    if 'youtube.com' in domain or 'youtu.be' in domain:
        return 'YouTube',   url, (parts[0].lstrip('@') if parts else 'unknown')
    if 'instagram.com' in domain:
        return 'Instagram', url, (parts[0] if parts else 'unknown')
    if 'twitter.com' in domain or 'x.com' in domain:
        return 'Twitter/X', url, (parts[0] if parts else 'unknown')
    if 'facebook.com' in domain:
        return 'Facebook',  url, (parts[0] if parts else 'unknown')
    if 'reddit.com' in domain:
        handle = f'{parts[0]}/{parts[1]}' if len(parts) >= 2 else (parts[0] if parts else 'unknown')
        return 'Reddit',    url, handle
    if 'github.com' in domain:
        return 'GitHub',    url, (parts[0] if parts else 'unknown')
    if 'linkedin.com' in domain:
        return 'LinkedIn',  url, (parts[-1] if parts else 'unknown')
    return 'Unknown', url, (parts[0] if parts else 'unknown')

# ── Platform fetchers ──────────────────────────────────────────────────────────

def _youtube(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=14)
        name = sub_text = desc = avatar = ''
        sub_count = video_count = None

        # Parse embedded ytInitialData JSON
        m = re.search(r'var ytInitialData\s*=\s*(\{.+?\});\s*(?:</script>|var )', r.text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                ch   = (data.get('header', {}).get('c4TabbedHeaderRenderer') or
                        data.get('header', {}).get('pageHeaderRenderer', {}))
                name = ch.get('title', '')
                sub_obj  = ch.get('subscriberCountText', {})
                sub_text = (sub_obj.get('simpleText', '') or
                            (sub_obj.get('runs') or [{}])[0].get('text', ''))
                thumbs = ch.get('avatar', {}).get('thumbnails', [])
                avatar = thumbs[-1].get('url', '') if thumbs else ''

                # video count
                m2 = re.search(r'"videosCountText".*?"([\d,]+)"', r.text)
                if m2: video_count = _parse_count(m2.group(1))

                # description from About tab
                tabs = (data.get('contents', {})
                             .get('twoColumnBrowseResultsRenderer', {})
                             .get('tabs', []))
                for tab in tabs:
                    tr = tab.get('tabRenderer', {})
                    if tr.get('title') == 'About':
                        try:
                            items = (tr['content']['sectionListRenderer']
                                       ['contents'][0]['itemSectionRenderer']
                                       ['contents'][0])
                            d_obj = items.get('channelAboutFullMetadataRenderer', {}).get('description', {})
                            desc  = d_obj.get('simpleText', '') if isinstance(d_obj, dict) else ''
                        except Exception:
                            pass
                        break
            except Exception:
                pass

        # Fallback: meta tags
        if not name:
            if BS4:
                soup = BeautifulSoup(r.text, 'html.parser')
                og = soup.find('meta', property='og:title')
                if og: name = og.get('content', '').replace(' - YouTube', '').strip()
                og2 = soup.find('meta', property='og:description')
                if og2: desc = og2.get('content', '')
                img = soup.find('link', rel='image_src')
                if img: avatar = img.get('href', '')
            else:
                m3 = re.search(r'"title":"([^"]{3,80})"', r.text)
                if m3: name = m3.group(1)

        sub_count = _parse_count(sub_text.split(' ')[0]) if sub_text else None

        return {
            'platform': 'YouTube', 'success': bool(name),
            'name': name or 'Unknown Channel',
            'handle': url.split('/')[-1].lstrip('@'),
            'description': desc[:500],
            'followers': sub_count, 'followers_fmt': _fmt(sub_count) if sub_count else (sub_text or 'Hidden'),
            'following': None, 'posts_count': video_count, 'posts_label': 'Videos',
            'avatar_url': avatar, 'url': url,
            'extra': {'subscribers_raw': sub_text, 'videos': video_count},
        }
    except Exception as e:
        return {'platform': 'YouTube', 'success': False, 'error': str(e)}


def _reddit(url, handle):
    try:
        reddit_headers = {
            'User-Agent': 'SentimentIQ/1.0 (by /u/sentimentiq_project)',
            'Accept': 'application/json',
        }
        r    = requests.get(url.rstrip('/') + '/about.json',
                            headers=reddit_headers, timeout=8)
        body = r.json()
        kind = body.get('kind', '')
        d    = body.get('data', {})

        if kind == 't5':
            return {
                'platform': 'Reddit', 'success': True, 'type': 'subreddit',
                'name': d.get('display_name_prefixed', handle),
                'handle': handle,
                'description': (d.get('public_description') or d.get('description', ''))[:400],
                'followers': d.get('subscribers', 0),
                'followers_fmt': _fmt(d.get('subscribers', 0)),
                'following': None,
                'posts_count': d.get('accounts_active', 0), 'posts_label': 'Active Users',
                'avatar_url': (d.get('icon_img') or d.get('community_icon', '')).split('?')[0],
                'url': url,
                'extra': {'active': d.get('accounts_active', 0), 'nsfw': d.get('over18', False)},
            }
        if kind == 't2':
            return {
                'platform': 'Reddit', 'success': True, 'type': 'user',
                'name': d.get('name', handle), 'handle': handle, 'description': '',
                'followers': d.get('total_karma', 0),
                'followers_fmt': _fmt(d.get('total_karma', 0)),
                'following': None,
                'posts_count': d.get('link_karma', 0), 'posts_label': 'Post Karma',
                'avatar_url': d.get('icon_img', '').split('?')[0],
                'url': url,
                'extra': {'comment_karma': d.get('comment_karma', 0),
                          'link_karma':    d.get('link_karma', 0)},
            }
        return {'platform': 'Reddit', 'success': False, 'error': 'Unrecognised Reddit page type'}
    except Exception as e:
        return {'platform': 'Reddit', 'success': False, 'error': str(e)}


def _github(url, username):
    try:
        r = requests.get(f'https://api.github.com/users/{username}',
                         headers={**HEADERS, 'Accept': 'application/vnd.github.v3+json'}, timeout=8)
        if r.status_code != 200:
            return {'platform': 'GitHub', 'success': False, 'error': f'HTTP {r.status_code}'}
        d = r.json()

        rr = requests.get(f'https://api.github.com/users/{username}/repos?sort=stars&per_page=6',
                          headers={**HEADERS, 'Accept': 'application/vnd.github.v3+json'}, timeout=8)
        repos      = rr.json() if rr.status_code == 200 else []
        total_stars = sum(x.get('stargazers_count', 0) for x in repos)
        top_repos   = [{'name': x['name'], 'stars': x.get('stargazers_count', 0),
                        'forks': x.get('forks_count', 0),
                        'desc':  (x.get('description') or '')[:80]}
                       for x in repos[:5]]

        return {
            'platform': 'GitHub', 'success': True,
            'name': d.get('name') or d.get('login', username),
            'handle': username,
            'description': d.get('bio', '') or '',
            'followers': d.get('followers', 0), 'followers_fmt': _fmt(d.get('followers', 0)),
            'following': d.get('following', 0),
            'posts_count': d.get('public_repos', 0), 'posts_label': 'Repositories',
            'avatar_url': d.get('avatar_url', ''),
            'url': url,
            'extra': {'total_stars': total_stars, 'top_repos': top_repos,
                      'location': d.get('location', ''), 'company': d.get('company', '')},
        }
    except Exception as e:
        return {'platform': 'GitHub', 'success': False, 'error': str(e)}


def _instagram(url, username):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        followers = following = posts = 0
        name = username; desc = ''; avatar = ''

        if BS4:
            soup = BeautifulSoup(r.text, 'html.parser')
            og_t = soup.find('meta', property='og:title')
            og_d = soup.find('meta', property='og:description')
            og_i = soup.find('meta', property='og:image')
            if og_t: name   = og_t.get('content', username).split('(')[0].split('@')[0].strip()
            if og_i: avatar = og_i.get('content', '')
            if og_d:
                txt = og_d.get('content', '')
                mf = re.search(r'([\d,.]+[KMkMmBb]?)\s*Followers', txt, re.I)
                mg = re.search(r'([\d,.]+[KMkMmBb]?)\s*Following', txt, re.I)
                mp = re.search(r'([\d,.]+[KMkMmBb]?)\s*Posts',     txt, re.I)
                if mf: followers = _parse_count(mf.group(1))
                if mg: following = _parse_count(mg.group(1))
                if mp: posts     = _parse_count(mp.group(1))
        else:
            mf = re.search(r'([\d,.]+[KMkMmBb]?)\s*Followers', r.text, re.I)
            if mf: followers = _parse_count(mf.group(1))

        return {
            'platform': 'Instagram', 'success': True,
            'name': name, 'handle': username, 'description': desc,
            'followers': followers, 'followers_fmt': _fmt(followers) if followers else 'Private',
            'following': following,
            'posts_count': posts, 'posts_label': 'Posts',
            'avatar_url': avatar, 'url': url, 'partial': True,
            'extra': {'note': 'Instagram restricts public data — some stats may be unavailable'},
        }
    except Exception as e:
        return {'platform': 'Instagram', 'success': False, 'error': str(e)}


def _twitter(url, username):
    for host in ['https://nitter.net', 'https://nitter.privacydev.net', 'https://nitter.poast.org']:
        try:
            r = requests.get(f'{host}/{username}', headers=HEADERS, timeout=8)
            if r.status_code != 200 or not BS4: continue
            soup = BeautifulSoup(r.text, 'html.parser')
            name_el = soup.find('a', class_='profile-card-fullname')
            bio_el  = soup.find('p', class_='profile-bio')
            stats   = {}
            for li in soup.find_all('li', class_=re.compile('profile-stat')):
                val = li.find('span', class_='profile-stat-num')
                key = li.find('span', class_='profile-stat-header')
                if val and key: stats[key.text.lower().strip()] = _parse_count(val.text.strip())
            av_el  = soup.find('img', class_=re.compile('avatar'))
            avatar = ''
            if av_el:
                src = av_el.get('src', '')
                avatar = host + src if src.startswith('/') else src
            return {
                'platform': 'Twitter/X', 'success': True,
                'name': name_el.text.strip() if name_el else username,
                'handle': username,
                'description': bio_el.text.strip() if bio_el else '',
                'followers': stats.get('followers', 0),
                'followers_fmt': _fmt(stats.get('followers', 0)),
                'following': stats.get('following', 0),
                'posts_count': stats.get('tweets', 0), 'posts_label': 'Tweets',
                'avatar_url': avatar, 'url': url,
                'extra': {'likes': stats.get('likes', 0), 'source': 'nitter'},
            }
        except Exception:
            continue
    return {'platform': 'Twitter/X', 'success': False, 'handle': username, 'url': url,
            'error': 'Twitter/X requires API authentication. Nitter mirrors unreachable.'}


# ── Main entry ─────────────────────────────────────────────────────────────────

def fetch_account(url):
    platform, clean_url, handle = parse_url(url)
    dispatch = {
        'YouTube':   _youtube,
        'Reddit':    lambda u, _: _reddit(u, handle),
        'GitHub':    lambda u, _: _github(u, handle),
        'Instagram': lambda u, _: _instagram(u, handle),
        'Twitter/X': lambda u, _: _twitter(u, handle),
    }
    fn = dispatch.get(platform)
    if fn:
        return fn(clean_url, handle)
    return {'platform': platform, 'success': False, 'handle': handle, 'url': clean_url,
            'error': f'{platform} requires OAuth API access — direct public data not available.'}

# ── Analysis helpers ───────────────────────────────────────────────────────────

BENCHMARKS = {
    'YouTube':   {'followers': 1_000,   'eng': 4.0,  'posts_bench': 50,  'label': 'Subscribers'},
    'Instagram': {'followers': 10_000,  'eng': 3.0,  'posts_bench': 100, 'label': 'Followers'},
    'Twitter/X': {'followers': 1_000,   'eng': 0.5,  'posts_bench': 500, 'label': 'Followers'},
    'Reddit':    {'followers': 5_000,   'eng': 2.0,  'posts_bench': 50,  'label': 'Subscribers'},
    'GitHub':    {'followers': 50,      'eng': 10.0, 'posts_bench': 10,  'label': 'Followers'},
    'Facebook':  {'followers': 5_000,   'eng': 0.2,  'posts_bench': 200, 'label': 'Followers'},
}

def detect_issues(data, sentiment_result):
    issues    = []
    platform  = data.get('platform', '')
    followers = data.get('followers') or 0
    following = data.get('following') or 0
    posts     = data.get('posts_count') or 0
    desc      = (data.get('description') or '').strip()
    bench     = BENCHMARKS.get(platform, {})

    sent     = sentiment_result.get('final_sentiment', 'neutral')
    compound = sentiment_result.get('vader', {}).get('compound', 0)

    # 1. Bio quality
    if not desc or len(desc) < 15:
        issues.append({'severity': 'high', 'icon': 'file-text-fill', 'color': '#f97316',
            'title': 'Missing or Empty Bio/Description',
            'detail': 'Your profile has no description. New visitors cannot understand what your account is about — this is the #1 reason people do not follow.',
            'fix': 'Add a clear bio: who you are, what you post, and a call-to-action. Accounts with bios get 30% more follows.'})
    elif sent == 'negative':
        issues.append({'severity': 'high', 'icon': 'emoji-frown-fill', 'color': '#ef4444',
            'title': 'Negative Profile Bio Sentiment',
            'detail': f'Your bio/description has a negative sentiment score of {compound:.2f}. This repels new followers before they even see your content.',
            'fix': 'Rewrite with positive, value-driven language. Talk about what you offer, not complaints or frustrations.'})
    elif sent == 'neutral' and compound < 0.1:
        issues.append({'severity': 'medium', 'icon': 'emoji-neutral-fill', 'color': '#f59e0b',
            'title': 'Flat Bio — No Emotional Hook',
            'detail': f'Your bio reads as emotionless (score: {compound:.2f}). On {platform}, first impressions matter — a flat bio loses potential followers instantly.',
            'fix': 'Add personality, power words, or emojis (if platform allows). Tell people why they MUST follow you.'})

    # 2. Follower count vs benchmark
    if bench and followers < bench.get('followers', 0):
        issues.append({'severity': 'medium', 'icon': 'graph-down-arrow', 'color': '#8b5cf6',
            'title': f'Below-Average {platform} Reach',
            'detail': f'{_fmt(followers)} {bench.get("label","followers")} is below the typical active account level of {_fmt(bench["followers"])}+ on {platform}. Low reach means low organic discovery.',
            'fix': f'Post 3–5x per week, use trending hashtags/keywords on {platform}, collaborate with similar-sized accounts, and engage (comment) on top posts in your niche daily.'})

    # 3. Follower:Following ratio
    if following > 0 and followers > 0:
        ratio = followers / following
        if ratio < 0.3:
            issues.append({'severity': 'high', 'icon': 'people-fill', 'color': '#ef4444',
                'title': 'Critical Follower:Following Ratio',
                'detail': f'Following {_fmt(following)} accounts but only {_fmt(followers)} follow back — ratio is {ratio:.2f}:1. The {platform} algorithm flags this as spam-like behavior and reduces your reach.',
                'fix': 'Immediately audit your following list. Unfollow inactive/irrelevant accounts. Target a ratio of at least 1:1, ideally 2:1 or higher.'})
        elif ratio < 0.75:
            issues.append({'severity': 'medium', 'icon': 'person-dash-fill', 'color': '#f59e0b',
                'title': 'Unbalanced Follower:Following Ratio',
                'detail': f'Following {_fmt(following)}, followed by {_fmt(followers)} (ratio: {ratio:.2f}:1). Slightly unbalanced — can hurt credibility.',
                'fix': 'Clean up your following list over the next 2 weeks. Aim for a ratio above 1:1.'})

    # 4. Low content volume
    if bench and posts > 0 and posts < bench.get('posts_bench', 50):
        issues.append({'severity': 'low', 'icon': 'camera-fill', 'color': '#06b6d4',
            'title': 'Low Content Volume',
            'detail': f'Only {posts} {data.get("posts_label","posts")} detected. Active {platform} accounts average {bench.get("posts_bench",50)}+ for proper search discovery.',
            'fix': 'Create a content calendar. Batch-create content on weekends and schedule posts throughout the week.'})

    # 5. GitHub specific
    if platform == 'GitHub':
        extra = data.get('extra', {})
        stars = extra.get('total_stars', 0)
        if posts > 0 and stars < posts:
            issues.append({'severity': 'low', 'icon': 'star-fill', 'color': '#f59e0b',
                'title': 'Low Repository Stars',
                'detail': f'Your {posts} repos have only {stars} total stars. Low stars mean low project visibility in search.',
                'fix': 'Add a proper README with screenshots, share projects on Reddit r/programming, Hacker News, and Twitter/X dev community.'})

    if not issues:
        issues.append({'severity': 'good', 'icon': 'check-circle-fill', 'color': '#10b981',
            'title': 'Profile Looks Healthy!',
            'detail': 'No major issues detected. Your profile has a solid foundation.',
            'fix': 'Keep posting consistently. Reply to every comment within the first hour — this signals activity to the algorithm and boosts reach.'})

    return sorted(issues, key=lambda x: {'high': 0, 'medium': 1, 'low': 2, 'good': 3}.get(x['severity'], 4))


def estimate_engagement(data):
    platform  = data.get('platform', '')
    followers = data.get('followers') or 0
    posts     = data.get('posts_count') or 0
    extra     = data.get('extra', {})

    if followers == 0:
        return 0.0, 'unknown', BENCHMARKS.get(platform, {}).get('eng', 3.0)

    if platform == 'Reddit':
        karma = extra.get('comment_karma', 0) + extra.get('link_karma', 0)
        rate  = min((karma / max(followers, 1)) * 10, 40.0) if karma else 2.0
    elif platform == 'GitHub':
        stars = extra.get('total_stars', 0)
        rate  = min((stars / max(posts, 1)) * 5, 80.0) if stars else 1.0
    else:
        if followers > 1_000_000: rate = 1.2
        elif followers > 100_000: rate = 2.5
        elif followers > 10_000:  rate = 4.0
        elif followers > 1_000:   rate = 6.0
        else:                     rate = 9.0

    bench  = BENCHMARKS.get(platform, {}).get('eng', 3.0)
    status = ('excellent' if rate > bench * 1.5 else
              'good'      if rate > bench        else
              'average'   if rate > bench * 0.5  else 'low')
    return round(rate, 1), status, bench


def simulate_growth(current, platform, months=12):
    """Build a realistic historical follower growth curve ending at current count."""
    rates = {'YouTube': 0.09, 'Instagram': 0.07, 'Twitter/X': 0.05,
             'Reddit': 0.08, 'GitHub': 0.06, 'Facebook': 0.04}
    rate  = rates.get(platform, 0.06)
    start = max(current / ((1 + rate) ** months), 1)

    labels, values = [], []
    now = datetime.now()
    random.seed(current or 42)

    for i in range(months + 1):
        offset = months - i
        dt     = now - timedelta(days=30 * offset)
        labels.append(dt.strftime('%b %Y'))
        count  = start * ((1 + rate) ** i)
        noise  = random.uniform(0.97, 1.03)
        values.append(int(count * noise))

    values[-1] = current or 0
    return labels, values
