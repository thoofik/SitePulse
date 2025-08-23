import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AccessibilityAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SitePulse-AccessibilityAnalyzer/1.0'
        })
    
    def analyze(self, url):
        """
        Comprehensive accessibility analysis based on WCAG guidelines
        """
        results = {
            "score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "details": {
                "images": {},
                "forms": {},
                "navigation": {},
                "color_contrast": {},
                "keyboard_navigation": {},
                "aria_labels": {},
                "semantic_html": {},
                "multimedia": {}
            }
        }
        
        try:
            # Get page content
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Image Accessibility Analysis
            images_results = self._analyze_images(soup)
            results["details"]["images"] = images_results
            
            # Forms Accessibility Analysis
            forms_results = self._analyze_forms(soup)
            results["details"]["forms"] = forms_results
            
            # Navigation Accessibility Analysis
            navigation_results = self._analyze_navigation(soup)
            results["details"]["navigation"] = navigation_results
            
            # Color and Contrast Analysis
            color_results = self._analyze_color_contrast(soup)
            results["details"]["color_contrast"] = color_results
            
            # Keyboard Navigation Analysis
            keyboard_results = self._analyze_keyboard_navigation(soup)
            results["details"]["keyboard_navigation"] = keyboard_results
            
            # ARIA Labels Analysis
            aria_results = self._analyze_aria_labels(soup)
            results["details"]["aria_labels"] = aria_results
            
            # Semantic HTML Analysis
            semantic_results = self._analyze_semantic_html(soup)
            results["details"]["semantic_html"] = semantic_results
            
            # Multimedia Accessibility Analysis
            multimedia_results = self._analyze_multimedia(soup)
            results["details"]["multimedia"] = multimedia_results
            
            # Calculate accessibility score
            results["score"] = self._calculate_accessibility_score(results["details"])
            
            # Generate recommendations
            self._generate_accessibility_recommendations(results)
            
        except Exception as e:
            logger.error(f"Accessibility analysis error: {str(e)}")
            results["issues"].append({
                "type": "error",
                "severity": "high",
                "message": f"Accessibility analysis failed: {str(e)}",
                "recommendation": "Please check if the URL is accessible and try again."
            })
        
        return results
    
    def _analyze_images(self, soup):
        """Analyze image accessibility (WCAG 1.1.1)"""
        images_results = {
            "total_images": 0,
            "missing_alt": {"count": 0, "images": []},
            "empty_alt": {"count": 0, "images": []},
            "decorative_images": {"count": 0, "images": []},
            "complex_images": {"count": 0, "images": []},
            "issues": []
        }
        
        try:
            images = soup.find_all('img')
            images_results["total_images"] = len(images)
            
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt')
                title = img.get('title', '')
                
                # Check for missing alt attribute
                if alt is None:
                    images_results["missing_alt"]["count"] += 1
                    images_results["missing_alt"]["images"].append(src)
                # Check for empty alt (decorative images)
                elif alt == "":
                    images_results["decorative_images"]["count"] += 1
                    images_results["decorative_images"]["images"].append(src)
                # Check for very short alt text that might not be descriptive
                elif len(alt.strip()) < 3:
                    images_results["empty_alt"]["count"] += 1
                    images_results["empty_alt"]["images"].append(src)
                
                # Check for complex images (charts, graphs, etc.)
                if any(keyword in src.lower() for keyword in ['chart', 'graph', 'diagram', 'infographic']):
                    images_results["complex_images"]["count"] += 1
                    images_results["complex_images"]["images"].append(src)
            
            # Generate issues
            if images_results["missing_alt"]["count"] > 0:
                images_results["issues"].append(f"{images_results['missing_alt']['count']} images missing alt attributes")
            
            if images_results["empty_alt"]["count"] > 0:
                images_results["issues"].append(f"{images_results['empty_alt']['count']} images with inadequate alt text")
            
        except Exception as e:
            images_results["issues"].append(f"Image accessibility analysis error: {str(e)}")
        
        return images_results
    
    def _analyze_forms(self, soup):
        """Analyze form accessibility (WCAG 1.3.1, 2.4.6, 3.3.1)"""
        forms_results = {
            "total_forms": 0,
            "total_inputs": 0,
            "missing_labels": {"count": 0, "inputs": []},
            "missing_fieldsets": {"count": 0, "forms": []},
            "missing_error_handling": {"count": 0, "forms": []},
            "placeholder_only": {"count": 0, "inputs": []},
            "issues": []
        }
        
        try:
            forms = soup.find_all('form')
            forms_results["total_forms"] = len(forms)
            
            all_inputs = soup.find_all(['input', 'textarea', 'select'])
            forms_results["total_inputs"] = len(all_inputs)
            
            # Check each input for proper labeling
            for input_elem in all_inputs:
                input_type = input_elem.get('type', 'text')
                input_id = input_elem.get('id', '')
                input_name = input_elem.get('name', '')
                placeholder = input_elem.get('placeholder', '')
                
                # Skip hidden inputs
                if input_type == 'hidden':
                    continue
                
                # Check for associated label
                label_found = False
                
                # Check for label with for attribute
                if input_id:
                    label = soup.find('label', attrs={'for': input_id})
                    if label:
                        label_found = True
                
                # Check for wrapping label
                if not label_found:
                    parent_label = input_elem.find_parent('label')
                    if parent_label:
                        label_found = True
                
                # Check for aria-label or aria-labelledby
                if not label_found:
                    if input_elem.get('aria-label') or input_elem.get('aria-labelledby'):
                        label_found = True
                
                if not label_found:
                    forms_results["missing_labels"]["count"] += 1
                    forms_results["missing_labels"]["inputs"].append(input_name or input_id or f"input[type='{input_type}']")
                
                # Check for placeholder-only labeling (accessibility anti-pattern)
                if placeholder and not label_found:
                    forms_results["placeholder_only"]["count"] += 1
                    forms_results["placeholder_only"]["inputs"].append(input_name or input_id or placeholder)
            
            # Check for fieldsets in forms with multiple related inputs
            for form in forms:
                form_inputs = form.find_all(['input', 'textarea', 'select'])
                radio_groups = {}
                checkbox_groups = {}
                
                for inp in form_inputs:
                    input_type = inp.get('type', 'text')
                    name = inp.get('name', '')
                    
                    if input_type == 'radio' and name:
                        radio_groups[name] = radio_groups.get(name, 0) + 1
                    elif input_type == 'checkbox' and name:
                        checkbox_groups[name] = checkbox_groups.get(name, 0) + 1
                
                # Check if radio/checkbox groups need fieldsets
                needs_fieldset = any(count > 1 for count in radio_groups.values()) or any(count > 1 for count in checkbox_groups.values())
                
                if needs_fieldset:
                    fieldset = form.find('fieldset')
                    if not fieldset:
                        forms_results["missing_fieldsets"]["count"] += 1
            
            # Generate issues
            if forms_results["missing_labels"]["count"] > 0:
                forms_results["issues"].append(f"{forms_results['missing_labels']['count']} form inputs missing proper labels")
            
            if forms_results["placeholder_only"]["count"] > 0:
                forms_results["issues"].append(f"{forms_results['placeholder_only']['count']} inputs using placeholder as label (accessibility issue)")
            
            if forms_results["missing_fieldsets"]["count"] > 0:
                forms_results["issues"].append(f"{forms_results['missing_fieldsets']['count']} forms with grouped inputs missing fieldsets")
        
        except Exception as e:
            forms_results["issues"].append(f"Form accessibility analysis error: {str(e)}")
        
        return forms_results
    
    def _analyze_navigation(self, soup):
        """Analyze navigation accessibility (WCAG 2.4.1, 2.4.3, 2.4.8)"""
        navigation_results = {
            "skip_links": {"found": False, "links": []},
            "main_navigation": {"found": False, "labeled": False},
            "breadcrumbs": {"found": False, "labeled": False},
            "focus_indicators": {"missing": 0, "elements": []},
            "heading_structure": {"proper": True, "issues": []},
            "issues": []
        }
        
        try:
            # Check for skip links
            skip_link_patterns = ['skip to main', 'skip to content', 'skip navigation', 'skip to main content']
            links = soup.find_all('a', href=True)
            
            for link in links:
                link_text = link.get_text().lower().strip()
                if any(pattern in link_text for pattern in skip_link_patterns):
                    navigation_results["skip_links"]["found"] = True
                    navigation_results["skip_links"]["links"].append(link_text)
            
            # Check for main navigation landmarks
            nav_elements = soup.find_all('nav')
            if nav_elements:
                navigation_results["main_navigation"]["found"] = True
                
                # Check if navigation is properly labeled
                for nav in nav_elements:
                    if nav.get('aria-label') or nav.get('aria-labelledby') or nav.find('h1, h2, h3, h4, h5, h6'):
                        navigation_results["main_navigation"]["labeled"] = True
                        break
            
            # Check for main landmark
            main_element = soup.find('main') or soup.find(attrs={'role': 'main'})
            if not main_element:
                navigation_results["issues"].append("No main landmark found - important for screen readers")
            
            # Check for breadcrumb navigation
            breadcrumb_indicators = soup.find_all(attrs={'aria-label': re.compile(r'breadcrumb', re.I)})
            breadcrumb_lists = soup.find_all('ol', class_=re.compile(r'breadcrumb', re.I))
            
            if breadcrumb_indicators or breadcrumb_lists:
                navigation_results["breadcrumbs"]["found"] = True
                navigation_results["breadcrumbs"]["labeled"] = bool(breadcrumb_indicators)
            
            # Check heading structure for logical navigation
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                heading_levels = [int(h.name[1]) for h in headings]
                
                # Check if headings skip levels
                for i in range(1, len(heading_levels)):
                    if heading_levels[i] > heading_levels[i-1] + 1:
                        navigation_results["heading_structure"]["proper"] = False
                        navigation_results["heading_structure"]["issues"].append(f"Heading level skipped: h{heading_levels[i-1]} to h{heading_levels[i]}")
            
            # Generate issues
            if not navigation_results["skip_links"]["found"]:
                navigation_results["issues"].append("No skip links found - important for keyboard navigation")
            
            if not navigation_results["main_navigation"]["labeled"]:
                navigation_results["issues"].append("Navigation elements not properly labeled")
            
            if not navigation_results["heading_structure"]["proper"]:
                navigation_results["issues"].extend(navigation_results["heading_structure"]["issues"])
        
        except Exception as e:
            navigation_results["issues"].append(f"Navigation accessibility analysis error: {str(e)}")
        
        return navigation_results
    
    def _analyze_color_contrast(self, soup):
        """Analyze color and contrast (WCAG 1.4.3, 1.4.6)"""
        color_results = {
            "color_only_indicators": {"found": False, "elements": []},
            "contrast_issues": {"potential": 0, "elements": []},
            "color_blind_friendly": {"score": 0, "issues": []},
            "issues": []
        }
        
        try:
            # Check for color-only indicators (links, buttons, etc.)
            # This is a simplified check - full analysis would require visual processing
            
            # Check for links without underlines (potential color-only indication)
            links = soup.find_all('a')
            for link in links:
                style = link.get('style', '')
                if 'text-decoration' in style and 'none' in style:
                    color_results["color_only_indicators"]["found"] = True
                    color_results["color_only_indicators"]["elements"].append("Links without underlines may rely on color alone")
            
            # Check for inline styles that might indicate color-only communication
            elements_with_color = soup.find_all(attrs={'style': re.compile(r'color\s*:', re.I)})
            if len(elements_with_color) > 5:  # Arbitrary threshold
                color_results["contrast_issues"]["potential"] = len(elements_with_color)
                color_results["issues"].append("Many elements use inline color styles - check contrast ratios")
            
            # Look for common accessibility issues
            red_text = soup.find_all(attrs={'style': re.compile(r'color\s*:\s*red', re.I)})
            if red_text:
                color_results["color_blind_friendly"]["issues"].append("Red text found - ensure sufficient contrast and don't rely on color alone")
            
            green_text = soup.find_all(attrs={'style': re.compile(r'color\s*:\s*green', re.I)})
            if green_text:
                color_results["color_blind_friendly"]["issues"].append("Green text found - ensure sufficient contrast and don't rely on color alone")
            
            # Generate overall issues
            if color_results["color_only_indicators"]["found"]:
                color_results["issues"].append("Potential color-only indicators found - ensure information is conveyed through other means")
        
        except Exception as e:
            color_results["issues"].append(f"Color contrast analysis error: {str(e)}")
        
        return color_results
    
    def _analyze_keyboard_navigation(self, soup):
        """Analyze keyboard navigation support (WCAG 2.1.1, 2.1.2)"""
        keyboard_results = {
            "focusable_elements": {"count": 0, "without_tabindex": 0},
            "tab_traps": {"potential": 0, "elements": []},
            "custom_controls": {"count": 0, "missing_keyboard": []},
            "issues": []
        }
        
        try:
            # Find focusable elements
            focusable_selectors = ['a[href]', 'button', 'input:not([type="hidden"])', 'textarea', 'select', '[tabindex]']
            focusable_elements = []
            
            for selector in focusable_selectors:
                elements = soup.select(selector)
                focusable_elements.extend(elements)
            
            keyboard_results["focusable_elements"]["count"] = len(focusable_elements)
            
            # Check for elements with negative tabindex (potential tab traps)
            negative_tabindex = soup.find_all(attrs={'tabindex': re.compile(r'^-\d+$')})
            keyboard_results["tab_traps"]["potential"] = len(negative_tabindex)
            
            # Check for custom interactive elements that might need keyboard support
            custom_interactive = soup.find_all(attrs={'onclick': True})
            custom_interactive.extend(soup.find_all(attrs={'role': re.compile(r'button|link|menuitem', re.I)}))
            
            for element in custom_interactive:
                if element.name not in ['button', 'a', 'input', 'textarea', 'select']:
                    # Check if it has keyboard event handlers or tabindex
                    if not (element.get('onkeydown') or element.get('onkeypress') or element.get('tabindex')):
                        keyboard_results["custom_controls"]["missing_keyboard"].append(element.name or 'unknown')
            
            keyboard_results["custom_controls"]["count"] = len(custom_interactive)
            
            # Generate issues
            if keyboard_results["tab_traps"]["potential"] > 0:
                keyboard_results["issues"].append(f"Potential keyboard traps found: {keyboard_results['tab_traps']['potential']} elements with negative tabindex")
            
            if keyboard_results["custom_controls"]["missing_keyboard"]:
                keyboard_results["issues"].append("Custom interactive elements may not be keyboard accessible")
        
        except Exception as e:
            keyboard_results["issues"].append(f"Keyboard navigation analysis error: {str(e)}")
        
        return keyboard_results
    
    def _analyze_aria_labels(self, soup):
        """Analyze ARIA labels and attributes (WCAG 4.1.2)"""
        aria_results = {
            "aria_labels": {"count": 0, "elements": []},
            "aria_describedby": {"count": 0, "elements": []},
            "aria_live": {"count": 0, "elements": []},
            "invalid_aria": {"count": 0, "attributes": []},
            "missing_aria": {"count": 0, "elements": []},
            "issues": []
        }
        
        try:
            # Count ARIA labels
            aria_label_elements = soup.find_all(attrs={'aria-label': True})
            aria_results["aria_labels"]["count"] = len(aria_label_elements)
            
            # Count aria-describedby
            aria_describedby_elements = soup.find_all(attrs={'aria-describedby': True})
            aria_results["aria_describedby"]["count"] = len(aria_describedby_elements)
            
            # Count aria-live regions
            aria_live_elements = soup.find_all(attrs={'aria-live': True})
            aria_results["aria_live"]["count"] = len(aria_live_elements)
            
            # Check for elements that should have ARIA labels
            buttons_without_text = soup.find_all('button', string=False)
            for button in buttons_without_text:
                if not (button.get('aria-label') or button.get('aria-labelledby') or button.find('img')):
                    aria_results["missing_aria"]["count"] += 1
                    aria_results["missing_aria"]["elements"].append('button without text or aria-label')
            
            # Check for images used as buttons without proper labeling
            clickable_images = soup.find_all('img', attrs={'onclick': True})
            for img in clickable_images:
                if not (img.get('alt') or img.get('aria-label')):
                    aria_results["missing_aria"]["count"] += 1
                    aria_results["missing_aria"]["elements"].append('clickable image without alt or aria-label')
            
            # Check for common ARIA validation issues
            all_elements = soup.find_all(attrs=lambda x: any(attr.startswith('aria-') for attr in x.keys()) if x else False)
            
            for element in all_elements:
                for attr in element.attrs:
                    if attr.startswith('aria-'):
                        # Basic validation (this could be expanded)
                        if attr in ['aria-hidden'] and element.attrs[attr] not in ['true', 'false']:
                            aria_results["invalid_aria"]["count"] += 1
                            aria_results["invalid_aria"]["attributes"].append(f"{attr}='{element.attrs[attr]}'")
            
            # Generate issues
            if aria_results["missing_aria"]["count"] > 0:
                aria_results["issues"].append(f"{aria_results['missing_aria']['count']} elements missing required ARIA labels")
            
            if aria_results["invalid_aria"]["count"] > 0:
                aria_results["issues"].append(f"{aria_results['invalid_aria']['count']} invalid ARIA attributes found")
        
        except Exception as e:
            aria_results["issues"].append(f"ARIA analysis error: {str(e)}")
        
        return aria_results
    
    def _analyze_semantic_html(self, soup):
        """Analyze semantic HTML usage (WCAG 1.3.1)"""
        semantic_results = {
            "landmarks": {"count": 0, "types": []},
            "headings": {"proper_structure": True, "issues": []},
            "lists": {"count": 0, "proper_markup": True, "issues": []},
            "tables": {"count": 0, "accessible": 0, "issues": []},
            "issues": []
        }
        
        try:
            # Check for semantic landmarks
            landmarks = ['header', 'nav', 'main', 'aside', 'footer', 'section', 'article']
            for landmark in landmarks:
                elements = soup.find_all(landmark)
                if elements:
                    semantic_results["landmarks"]["count"] += len(elements)
                    semantic_results["landmarks"]["types"].append(landmark)
            
            # Also check for ARIA landmarks
            aria_landmarks = soup.find_all(attrs={'role': re.compile(r'banner|navigation|main|complementary|contentinfo', re.I)})
            semantic_results["landmarks"]["count"] += len(aria_landmarks)
            
            # Check heading structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                heading_levels = [int(h.name[1]) for h in headings]
                
                # Check for proper heading hierarchy
                if not heading_levels or heading_levels[0] != 1:
                    semantic_results["headings"]["proper_structure"] = False
                    semantic_results["headings"]["issues"].append("Page should start with h1")
                
                # Check for skipped levels
                for i in range(1, len(heading_levels)):
                    if heading_levels[i] > heading_levels[i-1] + 1:
                        semantic_results["headings"]["proper_structure"] = False
                        semantic_results["headings"]["issues"].append(f"Heading level skipped from h{heading_levels[i-1]} to h{heading_levels[i]}")
            
            # Check lists
            lists = soup.find_all(['ul', 'ol', 'dl'])
            semantic_results["lists"]["count"] = len(lists)
            
            for list_elem in lists:
                if list_elem.name in ['ul', 'ol']:
                    # Check if list contains only li elements
                    direct_children = [child for child in list_elem.children if hasattr(child, 'name')]
                    non_li_children = [child for child in direct_children if child.name != 'li']
                    if non_li_children:
                        semantic_results["lists"]["proper_markup"] = False
                        semantic_results["lists"]["issues"].append(f"List contains non-li elements: {[child.name for child in non_li_children]}")
            
            # Check tables
            tables = soup.find_all('table')
            semantic_results["tables"]["count"] = len(tables)
            
            for table in tables:
                accessible_features = 0
                
                # Check for table headers
                if table.find('th'):
                    accessible_features += 1
                
                # Check for caption
                if table.find('caption'):
                    accessible_features += 1
                
                # Check for summary or aria-label
                if table.get('summary') or table.get('aria-label'):
                    accessible_features += 1
                
                if accessible_features > 0:
                    semantic_results["tables"]["accessible"] += 1
                else:
                    semantic_results["tables"]["issues"].append("Table without headers, caption, or summary")
            
            # Generate issues
            if semantic_results["landmarks"]["count"] == 0:
                semantic_results["issues"].append("No semantic landmarks found - use header, nav, main, footer elements")
            
            if not semantic_results["headings"]["proper_structure"]:
                semantic_results["issues"].extend(semantic_results["headings"]["issues"])
            
            if not semantic_results["lists"]["proper_markup"]:
                semantic_results["issues"].extend(semantic_results["lists"]["issues"])
            
            if semantic_results["tables"]["count"] > 0 and semantic_results["tables"]["accessible"] == 0:
                semantic_results["issues"].append("Tables found without accessibility features")
        
        except Exception as e:
            semantic_results["issues"].append(f"Semantic HTML analysis error: {str(e)}")
        
        return semantic_results
    
    def _analyze_multimedia(self, soup):
        """Analyze multimedia accessibility (WCAG 1.2.1, 1.2.2, 1.2.3)"""
        multimedia_results = {
            "videos": {"count": 0, "with_captions": 0, "with_transcripts": 0, "issues": []},
            "audio": {"count": 0, "with_transcripts": 0, "issues": []},
            "autoplay": {"count": 0, "elements": []},
            "issues": []
        }
        
        try:
            # Check videos
            videos = soup.find_all('video')
            multimedia_results["videos"]["count"] = len(videos)
            
            for video in videos:
                # Check for captions/subtitles
                if video.find('track', kind='captions') or video.find('track', kind='subtitles'):
                    multimedia_results["videos"]["with_captions"] += 1
                
                # Check for autoplay
                if video.get('autoplay'):
                    multimedia_results["autoplay"]["count"] += 1
                    multimedia_results["autoplay"]["elements"].append('video')
            
            # Check audio
            audio_elements = soup.find_all('audio')
            multimedia_results["audio"]["count"] = len(audio_elements)
            
            for audio in audio_elements:
                # Check for autoplay
                if audio.get('autoplay'):
                    multimedia_results["autoplay"]["count"] += 1
                    multimedia_results["autoplay"]["elements"].append('audio')
            
            # Check for embedded videos (YouTube, Vimeo, etc.)
            iframes = soup.find_all('iframe')
            video_embeds = 0
            for iframe in iframes:
                src = iframe.get('src', '').lower()
                if any(domain in src for domain in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                    video_embeds += 1
            
            multimedia_results["videos"]["count"] += video_embeds
            
            # Generate issues
            if multimedia_results["videos"]["count"] > 0:
                if multimedia_results["videos"]["with_captions"] == 0:
                    multimedia_results["videos"]["issues"].append("Videos found without captions or subtitles")
            
            if multimedia_results["audio"]["count"] > 0:
                if multimedia_results["audio"]["with_transcripts"] == 0:
                    multimedia_results["audio"]["issues"].append("Audio content should have transcripts")
            
            if multimedia_results["autoplay"]["count"] > 0:
                multimedia_results["issues"].append(f"Autoplay media found ({multimedia_results['autoplay']['count']} elements) - can be disorienting for users")
        
        except Exception as e:
            multimedia_results["issues"].append(f"Multimedia analysis error: {str(e)}")
        
        return multimedia_results
    
    def _calculate_accessibility_score(self, details):
        """Calculate overall accessibility score (0-100)"""
        score = 100
        
        # Images scoring
        images = details.get("images", {})
        missing_alt = images.get("missing_alt", {}).get("count", 0)
        total_images = images.get("total_images", 1)  # Avoid division by zero
        if missing_alt > 0:
            score -= min(30, (missing_alt / total_images) * 50)
        
        # Forms scoring
        forms = details.get("forms", {})
        missing_labels = forms.get("missing_labels", {}).get("count", 0)
        total_inputs = forms.get("total_inputs", 1)
        if missing_labels > 0:
            score -= min(25, (missing_labels / total_inputs) * 40)
        
        # Navigation scoring
        navigation = details.get("navigation", {})
        if not navigation.get("skip_links", {}).get("found"):
            score -= 10
        if not navigation.get("main_navigation", {}).get("labeled"):
            score -= 8
        
        # Semantic HTML scoring
        semantic = details.get("semantic_html", {})
        if semantic.get("landmarks", {}).get("count", 0) == 0:
            score -= 15
        if not semantic.get("headings", {}).get("proper_structure", True):
            score -= 10
        
        # ARIA scoring
        aria = details.get("aria_labels", {})
        if aria.get("missing_aria", {}).get("count", 0) > 0:
            score -= 12
        
        # Multimedia scoring
        multimedia = details.get("multimedia", {})
        if multimedia.get("autoplay", {}).get("count", 0) > 0:
            score -= 8
        
        return max(0, min(100, score))
    
    def _generate_accessibility_recommendations(self, results):
        """Generate accessibility recommendations"""
        details = results["details"]
        
        # Images recommendations
        images = details.get("images", {})
        for issue in images.get("issues", []):
            severity = "high" if "missing alt" in issue else "medium"
            results["issues"].append({
                "type": "accessibility",
                "severity": severity,
                "message": f"Image accessibility: {issue}",
                "recommendation": "Add descriptive alt text to all images. Use empty alt='' for decorative images."
            })
        
        # Forms recommendations
        forms = details.get("forms", {})
        for issue in forms.get("issues", []):
            results["issues"].append({
                "type": "accessibility",
                "severity": "high",
                "message": f"Form accessibility: {issue}",
                "recommendation": "Associate all form inputs with proper labels using <label> elements or aria-label attributes."
            })
        
        # Navigation recommendations
        navigation = details.get("navigation", {})
        for issue in navigation.get("issues", []):
            severity = "high" if "skip links" in issue else "medium"
            results["warnings"].append({
                "type": "accessibility",
                "severity": severity,
                "message": f"Navigation accessibility: {issue}",
                "recommendation": "Implement skip links and proper heading structure for better navigation."
            })
        
        # Semantic HTML recommendations
        semantic = details.get("semantic_html", {})
        for issue in semantic.get("issues", []):
            results["warnings"].append({
                "type": "accessibility",
                "severity": "medium",
                "message": f"Semantic HTML: {issue}",
                "recommendation": "Use semantic HTML elements (header, nav, main, footer) and proper heading hierarchy."
            })
        
        # ARIA recommendations
        aria = details.get("aria_labels", {})
        for issue in aria.get("issues", []):
            results["warnings"].append({
                "type": "accessibility",
                "severity": "medium",
                "message": f"ARIA: {issue}",
                "recommendation": "Add proper ARIA labels and attributes to interactive elements and custom controls."
            })
        
        # Multimedia recommendations
        multimedia = details.get("multimedia", {})
        for issue in multimedia.get("issues", []):
            results["recommendations"].append({
                "type": "accessibility",
                "category": "multimedia",
                "message": issue,
                "recommendation": "Provide captions for videos, transcripts for audio, and avoid autoplay media."
            })
        
        # Color and contrast recommendations
        color = details.get("color_contrast", {})
        for issue in color.get("issues", []):
            results["recommendations"].append({
                "type": "accessibility",
                "category": "color-contrast",
                "message": issue,
                "recommendation": "Ensure sufficient color contrast ratios and don't rely on color alone to convey information."
            })
