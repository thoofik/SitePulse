import requests
from urllib.parse import urlparse, urljoin, parse_qs
from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SitePulse-SEOAnalyzer/1.0 (SEO Analysis Bot)'
        })
    
    def analyze(self, url):
        """
        Comprehensive SEO analysis of a website
        """
        results = {
            "score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "website_info": {},
            "details": {
                "meta_tags": {},
                "headings": {},
                "content": {},
                "links": {},
                "images": {},
                "structured_data": {},
                "technical_seo": {},
                "social_media": {}
            }
        }
        
        try:
            # Get page content
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Website Information Extraction
            website_info = self._extract_website_info(soup, url)
            results["website_info"] = website_info
            
            # Meta Tags Analysis
            meta_results = self._analyze_meta_tags(soup, url)
            results["details"]["meta_tags"] = meta_results
            
            # Headings Analysis
            headings_results = self._analyze_headings(soup)
            results["details"]["headings"] = headings_results
            
            # Content Analysis
            content_results = self._analyze_content(soup)
            results["details"]["content"] = content_results
            
            # Links Analysis
            links_results = self._analyze_links(soup, url)
            results["details"]["links"] = links_results
            
            # Images Analysis
            images_results = self._analyze_images(soup)
            results["details"]["images"] = images_results
            
            # Structured Data Analysis
            structured_data_results = self._analyze_structured_data(soup)
            results["details"]["structured_data"] = structured_data_results
            
            # Technical SEO Analysis
            technical_results = self._analyze_technical_seo(url, response, soup)
            results["details"]["technical_seo"] = technical_results
            
            # Social Media Analysis
            social_results = self._analyze_social_media(soup)
            results["details"]["social_media"] = social_results
            
            # Calculate SEO score
            results["score"] = self._calculate_seo_score(results["details"])
            
            # Generate recommendations
            self._generate_seo_recommendations(results)
            
        except Exception as e:
            logger.error(f"SEO analysis error: {str(e)}")
            results["issues"].append({
                "type": "error",
                "severity": "high",
                "message": f"SEO analysis failed: {str(e)}",
                "recommendation": "Please check if the URL is accessible and try again."
            })
        
        return results
    
    def _extract_website_info(self, soup, url):
        """Extract website information and purpose"""
        website_info = {
            "title": "",
            "description": "",
            "company_name": "",
            "website_type": "Unknown",
            "industry": "Unknown",
            "technologies": [],
            "social_presence": {},
            "contact_info": {},
            "estimated_purpose": ""
        }
        
        try:
            # Extract basic info
            title_tag = soup.find('title')
            if title_tag:
                website_info["title"] = title_tag.get_text().strip()
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                website_info["description"] = meta_desc.get('content', '').strip()
            
            # Try to identify company name from various sources
            company_indicators = [
                soup.find('meta', attrs={'property': 'og:site_name'}),
                soup.find('meta', attrs={'name': 'application-name'}),
                soup.find('meta', attrs={'name': 'apple-mobile-web-app-title'})
            ]
            
            for indicator in company_indicators:
                if indicator and indicator.get('content'):
                    website_info["company_name"] = indicator.get('content').strip()
                    break
            
            # If no company name found, try to extract from title
            if not website_info["company_name"] and website_info["title"]:
                # Common patterns: "Company Name | Tagline", "Title - Company Name"
                title = website_info["title"]
                if " | " in title:
                    website_info["company_name"] = title.split(" | ")[0].strip()
                elif " - " in title:
                    parts = title.split(" - ")
                    if len(parts) > 1:
                        website_info["company_name"] = parts[-1].strip()
            
            # Detect website type and purpose
            website_info["website_type"] = self._detect_website_type(soup, url)
            website_info["industry"] = self._detect_industry(soup, website_info["title"], website_info["description"])
            website_info["estimated_purpose"] = self._estimate_purpose(soup, website_info)
            
            # Detect technologies
            website_info["technologies"] = self._detect_technologies(soup)
            
            # Social media presence
            website_info["social_presence"] = self._extract_social_presence(soup)
            
            # Contact information
            website_info["contact_info"] = self._extract_contact_info(soup)
            
        except Exception as e:
            logger.error(f"Website info extraction error: {str(e)}")
        
        return website_info
    
    def _detect_website_type(self, soup, url):
        """Detect the type of website"""
        url_lower = url.lower()
        content_text = soup.get_text().lower()
        title_text = soup.find('title')
        title_content = title_text.get_text().lower() if title_text else ""
        
        # Domain-specific detection first (most accurate)
        domain_types = {
            'amazon.com': 'E-commerce/Online Store',
            'ebay.com': 'E-commerce/Online Store',
            'shopify.com': 'E-commerce/Online Store',
            'netflix.com': 'Streaming/Entertainment Platform',
            'youtube.com': 'Video Sharing/Media Platform',
            'instagram.com': 'Social Media Platform',
            'facebook.com': 'Social Media Platform',
            'twitter.com': 'Social Media Platform',
            'x.com': 'Social Media Platform',
            'linkedin.com': 'Professional Network/Social Platform',
            'reddit.com': 'Social News/Discussion Platform',
            'medium.com': 'Publishing/Blog Platform',
            'stackoverflow.com': 'Q&A/Developer Community',
            'github.com': 'Code Repository/Developer Platform',
            'wikipedia.org': 'Knowledge Base/Encyclopedia',
            'airbnb.com': 'Travel/Accommodation Platform',
            'uber.com': 'Transportation/Service Platform',
            'stripe.com': 'Payment Processing/FinTech',
            'paypal.com': 'Payment Processing/FinTech'
        }
        
        # Check for domain-specific matches
        for domain, site_type in domain_types.items():
            if domain in url_lower:
                return site_type
        
        # Social Media platforms
        social_indicators = ['follow us', 'share', 'like', 'comment', 'followers', 'social network', 'connect with friends']
        if any(indicator in content_text for indicator in social_indicators):
            if any(platform in url_lower for platform in ['instagram', 'facebook', 'twitter', 'tiktok', 'snapchat']):
                return "Social Media Platform"
        
        # E-commerce indicators (enhanced)
        ecommerce_strong = ['add to cart', 'shopping cart', 'buy now', 'checkout', 'add to bag', 'purchase']
        ecommerce_weak = ['shop', 'store', 'product', 'price', '$', 'sale', 'discount']
        if (any(keyword in content_text for keyword in ecommerce_strong) or
            (any(keyword in content_text for keyword in ecommerce_weak) and 
             any(keyword in title_content for keyword in ['shop', 'store', 'buy', 'market']))):
            return "E-commerce/Online Store"
        
        # Streaming/Entertainment
        streaming_indicators = ['watch', 'stream', 'video', 'movies', 'tv shows', 'entertainment', 'episodes']
        if any(indicator in content_text for indicator in streaming_indicators):
            if any(keyword in title_content for keyword in ['netflix', 'prime', 'hulu', 'disney', 'streaming']):
                return "Streaming/Entertainment Platform"
        
        # Developer/Tech platforms
        dev_indicators = ['code', 'repository', 'github', 'developer', 'api', 'programming', 'software']
        if any(indicator in content_text for indicator in dev_indicators):
            if any(keyword in url_lower for keyword in ['github', 'gitlab', 'stackoverflow', 'dev']):
                return "Developer Platform/Code Repository"
        
        # News/Media indicators (enhanced)
        news_indicators = ['news', 'breaking', 'latest', 'headlines', 'journalism', 'reporter', 'article']
        if any(keyword in content_text for keyword in news_indicators):
            if any(keyword in title_content for keyword in ['news', 'times', 'post', 'herald', 'daily']):
                return "News/Media Site"
        
        # Blog/Content indicators (enhanced)
        blog_indicators = ['blog', 'article', 'post', 'author', 'published', 'read more', 'categories', 'tags']
        if any(keyword in content_text for keyword in blog_indicators):
            if soup.find_all(['article', 'time']) or 'blog' in url_lower:
                return "Blog/Content Site"
        
        # Educational indicators (enhanced)
        edu_indicators = ['course', 'learn', 'education', 'tutorial', 'student', 'university', 'school', 'academy']
        if (any(keyword in content_text for keyword in edu_indicators) or 
            '.edu' in url_lower):
            return "Educational/Learning Platform"
        
        # SaaS/App indicators (enhanced)
        saas_indicators = ['sign up', 'free trial', 'dashboard', 'api', 'platform', 'software as a service', 'subscription']
        if any(keyword in content_text for keyword in saas_indicators):
            if any(keyword in title_content for keyword in ['app', 'platform', 'software', 'tool', 'service']):
                return "SaaS/Web Application"
        
        # Portfolio/Showcase indicators
        portfolio_indicators = ['portfolio', 'projects', 'work', 'gallery', 'showcase', 'my work', 'creative']
        if any(keyword in content_text for keyword in portfolio_indicators):
            return "Portfolio/Showcase"
        
        # Corporate/Business indicators (enhanced)
        business_indicators = ['about us', 'services', 'contact us', 'team', 'company', 'solutions', 'enterprise']
        if any(keyword in content_text for keyword in business_indicators):
            return "Corporate/Business Website"
        
        # Government indicators
        if '.gov' in url_lower or any(keyword in content_text for keyword in ['government', 'official', 'department', 'municipal']):
            return "Government Website"
        
        return "General Website"
    
    def _detect_industry(self, soup, title, description):
        """Detect the industry/sector"""
        content = f"{title} {description} {soup.get_text()[:1000]}".lower()
        
        industries = {
            "Technology": ["tech", "software", "app", "digital", "ai", "machine learning", "cloud", "api"],
            "E-commerce/Retail": ["shop", "store", "retail", "buy", "sell", "product", "marketplace"],
            "Finance": ["bank", "finance", "investment", "loan", "credit", "insurance", "trading"],
            "Healthcare": ["health", "medical", "doctor", "hospital", "clinic", "pharmacy", "medicine"],
            "Education": ["education", "school", "university", "course", "learning", "student", "academic"],
            "Real Estate": ["real estate", "property", "homes", "rent", "mortgage", "realtor"],
            "Travel": ["travel", "hotel", "booking", "vacation", "tourism", "flight", "trip"],
            "Food & Restaurant": ["restaurant", "food", "menu", "dining", "recipe", "cooking", "delivery"],
            "Media & Entertainment": ["news", "media", "entertainment", "movie", "music", "game", "streaming"],
            "Non-profit": ["non-profit", "charity", "donation", "volunteer", "foundation", "cause"],
            "Government": ["government", "gov", "official", "public", "municipal", "federal", "state"]
        }
        
        for industry, keywords in industries.items():
            if any(keyword in content for keyword in keywords):
                return industry
        
        return "General/Other"
    
    def _estimate_purpose(self, soup, website_info):
        """Estimate the main purpose of the website"""
        website_type = website_info.get("website_type", "")
        industry = website_info.get("industry", "")
        title = website_info.get("title", "")
        description = website_info.get("description", "")
        company_name = website_info.get("company_name", "")
        
        content = f"{title} {description}".lower()
        
        # Specific platform purposes
        if "social media" in website_type.lower():
            return "Connect people and enable social interaction and content sharing"
        elif "streaming" in website_type.lower() or "video sharing" in website_type.lower():
            return "Provide video content, entertainment, and media streaming services"
        elif "e-commerce" in website_type.lower():
            return "Enable online shopping and sell products or services to customers"
        elif "developer platform" in website_type.lower() or "code repository" in website_type.lower():
            return "Host code repositories and provide development tools for programmers"
        elif "q&a" in website_type.lower() or "developer community" in website_type.lower():
            return "Provide a platform for developers to ask questions and share knowledge"
        elif "publishing" in website_type.lower() or "blog platform" in website_type.lower():
            return "Enable content creation and publishing for writers and creators"
        elif "knowledge base" in website_type.lower() or "encyclopedia" in website_type.lower():
            return "Provide free access to knowledge and educational information"
        elif "travel" in website_type.lower() or "accommodation" in website_type.lower():
            return "Connect travelers with accommodations and travel services"
        elif "payment processing" in website_type.lower() or "fintech" in website_type.lower():
            return "Process online payments and provide financial technology services"
        elif "professional network" in website_type.lower():
            return "Connect professionals and facilitate career networking and development"
        elif "social news" in website_type.lower() or "discussion" in website_type.lower():
            return "Enable community discussions and social news sharing"
        elif "transportation" in website_type.lower():
            return "Provide transportation services and connect riders with drivers"
        elif "blog" in website_type.lower():
            return "Share content, articles, and insights with readers"
        elif "portfolio" in website_type.lower():
            return "Showcase work, projects, and professional capabilities"
        elif "corporate" in website_type.lower():
            return "Represent a company and provide business information"
        elif "saas" in website_type.lower():
            return "Provide software services and tools to users"
        elif "educational" in website_type.lower():
            return "Deliver educational content and learning resources"
        elif "news" in website_type.lower():
            return "Inform readers with news and current events"
        elif "government" in website_type.lower():
            return "Provide official government information and services"
        else:
            # Try to infer from content and company name
            if company_name:
                if any(word in content for word in ["learn", "course", "tutorial", "education"]):
                    return f"Provide educational services and learning resources"
                elif any(word in content for word in ["shop", "buy", "store", "product"]):
                    return f"Sell products and services online"
                elif any(word in content for word in ["stream", "watch", "video", "entertainment"]):
                    return f"Provide entertainment and media content"
                elif any(word in content for word in ["social", "connect", "share", "community"]):
                    return f"Connect people and build online communities"
                elif any(word in content for word in ["service", "solution", "help", "support"]):
                    return f"Offer services and solutions to customers"
                else:
                    return f"Serve as the online presence for {company_name}"
            else:
                # Generic fallbacks
                if any(word in content for word in ["learn", "course", "tutorial"]):
                    return "Provide learning and educational resources"
                elif any(word in content for word in ["service", "solution", "help"]):
                    return "Offer services and solutions to customers"
                elif any(word in content for word in ["community", "connect", "social"]):
                    return "Build community and connect people"
                else:
                    return "Provide information and engage with visitors"
    
    def _detect_technologies(self, soup):
        """Detect technologies used on the website"""
        technologies = []
        
        # Check for common frameworks and libraries
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            if 'react' in src:
                technologies.append("React")
            elif 'vue' in src:
                technologies.append("Vue.js")
            elif 'angular' in src:
                technologies.append("Angular")
            elif 'jquery' in src:
                technologies.append("jQuery")
            elif 'bootstrap' in src:
                technologies.append("Bootstrap")
            elif 'wordpress' in src:
                technologies.append("WordPress")
        
        # Check meta tags for generators
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator:
            gen_content = generator.get('content', '').lower()
            if 'wordpress' in gen_content:
                technologies.append("WordPress")
            elif 'drupal' in gen_content:
                technologies.append("Drupal")
            elif 'shopify' in gen_content:
                technologies.append("Shopify")
            elif 'squarespace' in gen_content:
                technologies.append("Squarespace")
            elif 'wix' in gen_content:
                technologies.append("Wix")
        
        return list(set(technologies))  # Remove duplicates
    
    def _extract_social_presence(self, soup):
        """Extract social media presence"""
        social_links = {}
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            if 'facebook.com' in href:
                social_links['Facebook'] = link.get('href')
            elif 'twitter.com' in href or 'x.com' in href:
                social_links['Twitter/X'] = link.get('href')
            elif 'linkedin.com' in href:
                social_links['LinkedIn'] = link.get('href')
            elif 'instagram.com' in href:
                social_links['Instagram'] = link.get('href')
            elif 'youtube.com' in href:
                social_links['YouTube'] = link.get('href')
            elif 'github.com' in href:
                social_links['GitHub'] = link.get('href')
        
        return social_links
    
    def _extract_contact_info(self, soup):
        """Extract contact information"""
        contact_info = {}
        
        # Look for email addresses
        content_text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content_text)
        if emails:
            contact_info['emails'] = list(set(emails))[:3]  # Limit to 3 emails
        
        # Look for phone numbers (basic pattern)
        phone_pattern = r'[\+]?[1-9]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        phones = re.findall(phone_pattern, content_text)
        if phones:
            contact_info['phones'] = list(set(phones))[:2]  # Limit to 2 phones
        
        # Look for address indicators
        if any(word in content_text.lower() for word in ['address', 'location', 'street', 'city']):
            contact_info['has_address'] = True
        
        return contact_info
    
    def _analyze_meta_tags(self, soup, url):
        """Analyze meta tags for SEO"""
        meta_results = {
            "title": {"content": "", "length": 0, "issues": []},
            "description": {"content": "", "length": 0, "issues": []},
            "keywords": {"content": "", "issues": []},
            "viewport": {"content": "", "issues": []},
            "robots": {"content": "", "issues": []},
            "canonical": {"href": "", "issues": []},
            "other_meta": []
        }
        
        # Title tag analysis
        title_tag = soup.find('title')
        if title_tag:
            title_content = title_tag.get_text().strip()
            meta_results["title"]["content"] = title_content
            meta_results["title"]["length"] = len(title_content)
            
            if len(title_content) == 0:
                meta_results["title"]["issues"].append("Title tag is empty")
            elif len(title_content) < 30:
                meta_results["title"]["issues"].append("Title tag is too short (less than 30 characters)")
            elif len(title_content) > 60:
                meta_results["title"]["issues"].append("Title tag is too long (more than 60 characters)")
        else:
            meta_results["title"]["issues"].append("Title tag is missing")
        
        # Meta description analysis
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc_content = meta_desc.get('content', '').strip()
            meta_results["description"]["content"] = desc_content
            meta_results["description"]["length"] = len(desc_content)
            
            if len(desc_content) == 0:
                meta_results["description"]["issues"].append("Meta description is empty")
            elif len(desc_content) < 120:
                meta_results["description"]["issues"].append("Meta description is too short (less than 120 characters)")
            elif len(desc_content) > 160:
                meta_results["description"]["issues"].append("Meta description is too long (more than 160 characters)")
        else:
            meta_results["description"]["issues"].append("Meta description is missing")
        
        # Meta keywords analysis
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords_content = meta_keywords.get('content', '').strip()
            meta_results["keywords"]["content"] = keywords_content
            if len(keywords_content) > 0:
                meta_results["keywords"]["issues"].append("Meta keywords tag is deprecated and not recommended")
        
        # Viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            meta_results["viewport"]["content"] = viewport.get('content', '')
        else:
            meta_results["viewport"]["issues"].append("Viewport meta tag is missing (important for mobile SEO)")
        
        # Robots meta tag
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots:
            meta_results["robots"]["content"] = robots.get('content', '')
            if 'noindex' in meta_results["robots"]["content"].lower():
                meta_results["robots"]["issues"].append("Page is set to noindex - it won't appear in search results")
        
        # Canonical link
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            canonical_href = canonical.get('href', '')
            meta_results["canonical"]["href"] = canonical_href
            
            # Check if canonical URL is different from current URL
            if canonical_href and canonical_href != url:
                parsed_canonical = urlparse(canonical_href)
                parsed_current = urlparse(url)
                if parsed_canonical.netloc != parsed_current.netloc:
                    meta_results["canonical"]["issues"].append("Canonical URL points to different domain")
        else:
            meta_results["canonical"]["issues"].append("Canonical link tag is missing")
        
        return meta_results
    
    def _analyze_headings(self, soup):
        """Analyze heading structure for SEO"""
        headings_results = {
            "h1": {"count": 0, "content": [], "issues": []},
            "h2": {"count": 0, "content": [], "issues": []},
            "h3": {"count": 0, "content": [], "issues": []},
            "h4": {"count": 0, "content": [], "issues": []},
            "h5": {"count": 0, "content": [], "issues": []},
            "h6": {"count": 0, "content": [], "issues": []},
            "structure_issues": []
        }
        
        # Analyze each heading level
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            tag_key = f'h{level}'
            
            headings_results[tag_key]["count"] = len(headings)
            headings_results[tag_key]["content"] = [h.get_text().strip() for h in headings]
            
            # Check for empty headings
            empty_headings = [h for h in headings if not h.get_text().strip()]
            if empty_headings:
                headings_results[tag_key]["issues"].append(f"Found {len(empty_headings)} empty {tag_key.upper()} tags")
        
        # H1 specific checks
        if headings_results["h1"]["count"] == 0:
            headings_results["h1"]["issues"].append("No H1 tag found - important for SEO")
        elif headings_results["h1"]["count"] > 1:
            headings_results["h1"]["issues"].append("Multiple H1 tags found - should have only one per page")
        
        # Check heading hierarchy
        if headings_results["h2"]["count"] == 0 and headings_results["h1"]["count"] > 0:
            headings_results["structure_issues"].append("No H2 tags found - consider using subheadings for better content structure")
        
        return headings_results
    
    def _analyze_content(self, soup):
        """Analyze content for SEO"""
        content_results = {
            "word_count": 0,
            "paragraph_count": 0,
            "readability": {"issues": []},
            "keyword_density": {},
            "issues": []
        }
        
        try:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Word count
            words = text.split()
            content_results["word_count"] = len(words)
            
            if content_results["word_count"] < 300:
                content_results["issues"].append("Content is too short (less than 300 words) - may not rank well")
            
            # Paragraph count
            paragraphs = soup.find_all('p')
            content_results["paragraph_count"] = len(paragraphs)
            
            if content_results["paragraph_count"] == 0:
                content_results["issues"].append("No paragraph tags found - content structure could be improved")
            
            # Basic readability check
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if sentences:
                avg_words_per_sentence = len(words) / len(sentences)
                if avg_words_per_sentence > 20:
                    content_results["readability"]["issues"].append("Sentences are too long on average - may hurt readability")
            
            # Simple keyword density analysis (top 10 words)
            word_freq = {}
            for word in words:
                word = word.lower().strip('.,!?";')
                if len(word) > 3 and word not in ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said']:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            for word, count in sorted_words:
                density = (count / len(words)) * 100
                content_results["keyword_density"][word] = {
                    "count": count,
                    "density": round(density, 2)
                }
        
        except Exception as e:
            content_results["issues"].append(f"Content analysis error: {str(e)}")
        
        return content_results
    
    def _analyze_links(self, soup, base_url):
        """Analyze links for SEO"""
        links_results = {
            "internal_links": {"count": 0, "links": [], "issues": []},
            "external_links": {"count": 0, "links": [], "issues": []},
            "anchor_text": {"empty": 0, "generic": 0, "issues": []},
            "nofollow_links": {"count": 0, "links": []},
            "issues": []
        }
        
        try:
            base_domain = urlparse(base_url).netloc
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').strip()
                anchor_text = link.get_text().strip()
                
                if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue
                
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                link_domain = urlparse(full_url).netloc
                
                # Categorize links
                if link_domain == base_domain or not link_domain:
                    links_results["internal_links"]["count"] += 1
                    links_results["internal_links"]["links"].append({
                        "url": full_url,
                        "anchor_text": anchor_text
                    })
                else:
                    links_results["external_links"]["count"] += 1
                    links_results["external_links"]["links"].append({
                        "url": full_url,
                        "anchor_text": anchor_text
                    })
                
                # Check for nofollow
                rel = link.get('rel', [])
                if isinstance(rel, str):
                    rel = [rel]
                if 'nofollow' in rel:
                    links_results["nofollow_links"]["count"] += 1
                    links_results["nofollow_links"]["links"].append(full_url)
                
                # Analyze anchor text
                if not anchor_text:
                    links_results["anchor_text"]["empty"] += 1
                elif anchor_text.lower() in ['click here', 'read more', 'more', 'here', 'link']:
                    links_results["anchor_text"]["generic"] += 1
            
            # Generate issues
            if links_results["internal_links"]["count"] == 0:
                links_results["issues"].append("No internal links found - important for site structure and SEO")
            
            if links_results["anchor_text"]["empty"] > 0:
                links_results["anchor_text"]["issues"].append(f"{links_results['anchor_text']['empty']} links with empty anchor text")
            
            if links_results["anchor_text"]["generic"] > 0:
                links_results["anchor_text"]["issues"].append(f"{links_results['anchor_text']['generic']} links with generic anchor text")
        
        except Exception as e:
            links_results["issues"].append(f"Links analysis error: {str(e)}")
        
        return links_results
    
    def _analyze_images(self, soup):
        """Analyze images for SEO"""
        images_results = {
            "total_images": 0,
            "missing_alt": {"count": 0, "images": []},
            "empty_alt": {"count": 0, "images": []},
            "missing_title": {"count": 0, "images": []},
            "large_images": {"count": 0, "images": []},
            "issues": []
        }
        
        try:
            images = soup.find_all('img')
            images_results["total_images"] = len(images)
            
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt')
                title = img.get('title')
                
                # Check alt attribute
                if alt is None:
                    images_results["missing_alt"]["count"] += 1
                    images_results["missing_alt"]["images"].append(src)
                elif not alt.strip():
                    images_results["empty_alt"]["count"] += 1
                    images_results["empty_alt"]["images"].append(src)
                
                # Check title attribute
                if not title:
                    images_results["missing_title"]["count"] += 1
                    images_results["missing_title"]["images"].append(src)
            
            # Generate issues
            if images_results["missing_alt"]["count"] > 0:
                images_results["issues"].append(f"{images_results['missing_alt']['count']} images missing alt attributes")
            
            if images_results["empty_alt"]["count"] > 0:
                images_results["issues"].append(f"{images_results['empty_alt']['count']} images with empty alt attributes")
            
            if images_results["total_images"] == 0:
                images_results["issues"].append("No images found - consider adding relevant images to improve engagement")
        
        except Exception as e:
            images_results["issues"].append(f"Images analysis error: {str(e)}")
        
        return images_results
    
    def _analyze_structured_data(self, soup):
        """Analyze structured data (JSON-LD, microdata, etc.)"""
        structured_data_results = {
            "json_ld": {"count": 0, "schemas": [], "issues": []},
            "microdata": {"count": 0, "items": [], "issues": []},
            "open_graph": {"tags": {}, "issues": []},
            "twitter_cards": {"tags": {}, "issues": []},
            "issues": []
        }
        
        try:
            # JSON-LD analysis
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            structured_data_results["json_ld"]["count"] = len(json_ld_scripts)
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and '@type' in data:
                        structured_data_results["json_ld"]["schemas"].append(data['@type'])
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and '@type' in item:
                                structured_data_results["json_ld"]["schemas"].append(item['@type'])
                except json.JSONDecodeError:
                    structured_data_results["json_ld"]["issues"].append("Invalid JSON-LD found")
            
            # Microdata analysis
            microdata_items = soup.find_all(attrs={'itemscope': True})
            structured_data_results["microdata"]["count"] = len(microdata_items)
            
            for item in microdata_items:
                itemtype = item.get('itemtype', '')
                if itemtype:
                    structured_data_results["microdata"]["items"].append(itemtype)
            
            # Open Graph analysis
            og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
            for tag in og_tags:
                property_name = tag.get('property', '')
                content = tag.get('content', '')
                structured_data_results["open_graph"]["tags"][property_name] = content
            
            # Check for essential Open Graph tags
            essential_og = ['og:title', 'og:description', 'og:image', 'og:url']
            for tag in essential_og:
                if tag not in structured_data_results["open_graph"]["tags"]:
                    structured_data_results["open_graph"]["issues"].append(f"Missing {tag} tag")
            
            # Twitter Cards analysis
            twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
            for tag in twitter_tags:
                name = tag.get('name', '')
                content = tag.get('content', '')
                structured_data_results["twitter_cards"]["tags"][name] = content
            
            # Check for Twitter Card type
            if 'twitter:card' not in structured_data_results["twitter_cards"]["tags"]:
                structured_data_results["twitter_cards"]["issues"].append("Missing twitter:card tag")
            
            # Overall issues
            if (structured_data_results["json_ld"]["count"] == 0 and 
                structured_data_results["microdata"]["count"] == 0):
                structured_data_results["issues"].append("No structured data found - consider adding schema markup")
        
        except Exception as e:
            structured_data_results["issues"].append(f"Structured data analysis error: {str(e)}")
        
        return structured_data_results
    
    def _analyze_technical_seo(self, url, response, soup):
        """Analyze technical SEO aspects"""
        technical_results = {
            "url_structure": {"issues": []},
            "page_speed": {"issues": []},
            "mobile_friendly": {"issues": []},
            "sitemap": {"found": False, "issues": []},
            "robots_txt": {"found": False, "issues": []},
            "ssl": {"enabled": False, "issues": []},
            "issues": []
        }
        
        try:
            parsed_url = urlparse(url)
            
            # URL structure analysis
            if len(parsed_url.path) > 100:
                technical_results["url_structure"]["issues"].append("URL is too long (over 100 characters)")
            
            if '_' in parsed_url.path:
                technical_results["url_structure"]["issues"].append("URL contains underscores - consider using hyphens instead")
            
            # SSL check
            if parsed_url.scheme == 'https':
                technical_results["ssl"]["enabled"] = True
            else:
                technical_results["ssl"]["issues"].append("Website is not using HTTPS - important for SEO and security")
            
            # Mobile-friendly check (basic)
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport_meta:
                technical_results["mobile_friendly"]["issues"].append("Missing viewport meta tag - may not be mobile-friendly")
            
            # Check for responsive design indicators
            responsive_indicators = soup.find_all(['link', 'style'], string=re.compile(r'@media|responsive'))
            if not responsive_indicators:
                technical_results["mobile_friendly"]["issues"].append("No responsive design indicators found")
            
            # Check for robots.txt
            try:
                robots_url = urljoin(url, '/robots.txt')
                robots_response = self.session.get(robots_url, timeout=5)
                if robots_response.status_code == 200:
                    technical_results["robots_txt"]["found"] = True
                else:
                    technical_results["robots_txt"]["issues"].append("robots.txt not found")
            except:
                technical_results["robots_txt"]["issues"].append("Could not check robots.txt")
            
            # Check for sitemap
            try:
                sitemap_url = urljoin(url, '/sitemap.xml')
                sitemap_response = self.session.get(sitemap_url, timeout=5)
                if sitemap_response.status_code == 200:
                    technical_results["sitemap"]["found"] = True
                else:
                    technical_results["sitemap"]["issues"].append("sitemap.xml not found")
            except:
                technical_results["sitemap"]["issues"].append("Could not check sitemap.xml")
            
        except Exception as e:
            technical_results["issues"].append(f"Technical SEO analysis error: {str(e)}")
        
        return technical_results
    
    def _analyze_social_media(self, soup):
        """Analyze social media optimization"""
        social_results = {
            "facebook": {"optimized": False, "missing_tags": []},
            "twitter": {"optimized": False, "missing_tags": []},
            "linkedin": {"optimized": False, "missing_tags": []},
            "social_links": {"count": 0, "platforms": []},
            "issues": []
        }
        
        try:
            # Facebook Open Graph
            og_tags = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
            found_og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
            found_og_properties = [tag.get('property') for tag in found_og_tags]
            
            for tag in og_tags:
                if tag not in found_og_properties:
                    social_results["facebook"]["missing_tags"].append(tag)
            
            social_results["facebook"]["optimized"] = len(social_results["facebook"]["missing_tags"]) == 0
            
            # Twitter Cards
            twitter_tags = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
            found_twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})
            found_twitter_names = [tag.get('name') for tag in found_twitter_tags]
            
            for tag in twitter_tags:
                if tag not in found_twitter_names:
                    social_results["twitter"]["missing_tags"].append(tag)
            
            social_results["twitter"]["optimized"] = len(social_results["twitter"]["missing_tags"]) == 0
            
            # Social media links
            social_platforms = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com']
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '').lower()
                for platform in social_platforms:
                    if platform in href:
                        platform_name = platform.split('.')[0]
                        if platform_name not in social_results["social_links"]["platforms"]:
                            social_results["social_links"]["platforms"].append(platform_name)
                            social_results["social_links"]["count"] += 1
            
            # Generate issues
            if not social_results["facebook"]["optimized"]:
                social_results["issues"].append("Facebook Open Graph tags incomplete")
            
            if not social_results["twitter"]["optimized"]:
                social_results["issues"].append("Twitter Card tags incomplete")
            
            if social_results["social_links"]["count"] == 0:
                social_results["issues"].append("No social media links found")
        
        except Exception as e:
            social_results["issues"].append(f"Social media analysis error: {str(e)}")
        
        return social_results
    
    def _calculate_seo_score(self, details):
        """Calculate overall SEO score (0-100)"""
        score = 100
        
        # Meta tags scoring
        meta_tags = details.get("meta_tags", {})
        if meta_tags.get("title", {}).get("issues"):
            score -= 15
        if meta_tags.get("description", {}).get("issues"):
            score -= 10
        if meta_tags.get("canonical", {}).get("issues"):
            score -= 5
        
        # Headings scoring
        headings = details.get("headings", {})
        if headings.get("h1", {}).get("issues"):
            score -= 10
        if headings.get("structure_issues"):
            score -= 5
        
        # Content scoring
        content = details.get("content", {})
        if content.get("word_count", 0) < 300:
            score -= 10
        
        # Images scoring
        images = details.get("images", {})
        if images.get("missing_alt", {}).get("count", 0) > 0:
            score -= 8
        
        # Technical SEO scoring
        technical = details.get("technical_seo", {})
        if not technical.get("ssl", {}).get("enabled"):
            score -= 15
        if not technical.get("sitemap", {}).get("found"):
            score -= 5
        if not technical.get("robots_txt", {}).get("found"):
            score -= 3
        
        # Structured data scoring
        structured = details.get("structured_data", {})
        if (structured.get("json_ld", {}).get("count", 0) == 0 and 
            structured.get("microdata", {}).get("count", 0) == 0):
            score -= 8
        
        return max(0, min(100, score))
    
    def _generate_seo_recommendations(self, results):
        """Generate SEO recommendations"""
        details = results["details"]
        
        # Meta tags recommendations
        meta_tags = details.get("meta_tags", {})
        for issue in meta_tags.get("title", {}).get("issues", []):
            results["issues"].append({
                "type": "meta",
                "severity": "high",
                "message": f"Title tag issue: {issue}",
                "recommendation": "Optimize title tag to 30-60 characters, include primary keyword, and make it compelling for users."
            })
        
        for issue in meta_tags.get("description", {}).get("issues", []):
            results["warnings"].append({
                "type": "meta",
                "severity": "medium",
                "message": f"Meta description issue: {issue}",
                "recommendation": "Write compelling meta descriptions 120-160 characters long, include keywords and call-to-action."
            })
        
        # Headings recommendations
        headings = details.get("headings", {})
        for issue in headings.get("h1", {}).get("issues", []):
            results["issues"].append({
                "type": "content",
                "severity": "high",
                "message": f"H1 issue: {issue}",
                "recommendation": "Use exactly one H1 tag per page with your primary keyword and clear page topic."
            })
        
        # Content recommendations
        content = details.get("content", {})
        for issue in content.get("issues", []):
            results["warnings"].append({
                "type": "content",
                "severity": "medium",
                "message": issue,
                "recommendation": "Create high-quality, comprehensive content that provides value to users and covers the topic thoroughly."
            })
        
        # Images recommendations
        images = details.get("images", {})
        for issue in images.get("issues", []):
            results["warnings"].append({
                "type": "images",
                "severity": "medium",
                "message": issue,
                "recommendation": "Add descriptive alt text to all images for better accessibility and SEO."
            })
        
        # Technical SEO recommendations
        technical = details.get("technical_seo", {})
        for issue in technical.get("ssl", {}).get("issues", []):
            results["issues"].append({
                "type": "technical",
                "severity": "critical",
                "message": issue,
                "recommendation": "Implement HTTPS with a valid SSL certificate to improve security and SEO rankings."
            })
        
        for issue in technical.get("sitemap", {}).get("issues", []):
            results["recommendations"].append({
                "type": "technical",
                "category": "sitemap",
                "message": issue,
                "recommendation": "Create and submit an XML sitemap to help search engines discover and index your pages."
            })
        
        # Structured data recommendations
        structured = details.get("structured_data", {})
        for issue in structured.get("issues", []):
            results["recommendations"].append({
                "type": "structured-data",
                "category": "schema",
                "message": issue,
                "recommendation": "Implement structured data markup (JSON-LD) to help search engines understand your content better."
            })
        
        # Social media recommendations
        social = details.get("social_media", {})
        for issue in social.get("issues", []):
            results["recommendations"].append({
                "type": "social",
                "category": "social-media",
                "message": issue,
                "recommendation": "Optimize social media tags (Open Graph, Twitter Cards) for better social sharing."
            })
