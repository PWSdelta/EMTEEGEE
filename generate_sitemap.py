#!/usr/bin/env python3
"""
MTG Card Sitemap Generator
Generates XML sitemap for all cards in the database
"""

import os
import sys
import django
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_mongodb_collection

def generate_sitemap():
    """Generate XML sitemap for all cards"""
    print("🗺️  Generating MTG Card Sitemap...")
    
    # Get cards collection
    cards = get_mongodb_collection('cards')
    
    # Base URL for your site
    BASE_URL = "https://mtgabyss.com"  # Change this to your actual domain
    
    # Create XML structure
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
    
    # Add homepage
    url_elem = ET.SubElement(urlset, 'url')
    ET.SubElement(url_elem, 'loc').text = BASE_URL
    ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    ET.SubElement(url_elem, 'changefreq').text = 'daily'
    ET.SubElement(url_elem, 'priority').text = '1.0'
    
    # Add main sections
    sections = [
        ('cards/', 'daily', '0.9'),
        ('cards/search/', 'daily', '0.8'),
        ('cards/random/', 'daily', '0.7'),
        ('cards/advanced/', 'weekly', '0.6'),
    ]
    
    for path, changefreq, priority in sections:
        url_elem = ET.SubElement(urlset, 'url')
        ET.SubElement(url_elem, 'loc').text = urljoin(BASE_URL, path)
        ET.SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        ET.SubElement(url_elem, 'changefreq').text = changefreq
        ET.SubElement(url_elem, 'priority').text = priority
    
    # Get all cards
    total_cards = cards.count_documents({})
    print(f"📊 Processing {total_cards:,} cards...")
    
    processed = 0
    batch_size = 1000
    
    # Process cards in batches
    for skip in range(0, total_cards, batch_size):
        card_batch = list(cards.find(
            {},
            {
                'name': 1,
                'uuid': 1,
                'analysis.analysis_date': 1,
                'analysis.fully_analyzed': 1,
                'colors': 1,
                'types': 1,
                'manaCost': 1
            }
        ).skip(skip).limit(batch_size))
        
        for card in card_batch:
            try:
                card_name = card.get('name', '').strip()
                if not card_name:
                    continue
                
                # Create URL-safe name (same logic as your card detail view)
                url_name = card_name.lower().replace(' ', '-').replace("'", '').replace(',', '').replace(':', '').replace('/', '-')
                card_url = urljoin(BASE_URL, f'cards/{url_name}/')
                
                # Create URL element
                url_elem = ET.SubElement(urlset, 'url')
                ET.SubElement(url_elem, 'loc').text = card_url
                
                # Set last modified date
                analysis_date = card.get('analysis', {}).get('analysis_date')
                if analysis_date:
                    if hasattr(analysis_date, 'strftime'):
                        lastmod = analysis_date.strftime('%Y-%m-%d')
                    else:
                        lastmod = datetime.now().strftime('%Y-%m-%d')
                else:
                    lastmod = datetime.now().strftime('%Y-%m-%d')
                
                ET.SubElement(url_elem, 'lastmod').text = lastmod
                
                # Set priority based on analysis status
                fully_analyzed = card.get('analysis', {}).get('fully_analyzed', False)
                if fully_analyzed:
                    priority = '0.8'  # High priority for analyzed cards
                    changefreq = 'weekly'
                else:
                    priority = '0.6'  # Lower priority for unanalyzed cards
                    changefreq = 'monthly'
                
                ET.SubElement(url_elem, 'changefreq').text = changefreq
                ET.SubElement(url_elem, 'priority').text = priority
                
                # Add image information if available
                image_elem = ET.SubElement(url_elem, 'image:image')
                ET.SubElement(image_elem, 'image:loc').text = f"https://cards.scryfall.io/normal/front/{card.get('uuid', '')[:1]}/{card.get('uuid', '')[:2]}/{card.get('uuid', '')}.jpg"
                ET.SubElement(image_elem, 'image:title').text = card_name
                ET.SubElement(image_elem, 'image:caption').text = f"MTG Card: {card_name}"
                
                processed += 1
                
            except Exception as e:
                print(f"❌ Error processing card {card.get('name', 'Unknown')}: {e}")
                continue
        
        # Progress update
        print(f"📈 Processed {processed:,} / {total_cards:,} cards ({processed/total_cards*100:.1f}%)")
    
    # Write sitemap to file
    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ", level=0)  # Pretty print (Python 3.9+)
    
    sitemap_path = 'sitemap.xml'
    tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ Sitemap generated successfully!")
    print(f"📁 File: {sitemap_path}")
    print(f"📊 Total URLs: {len(urlset):,}")
    print(f"📋 Cards included: {processed:,}")
    
    # Generate sitemap index if needed (for large sites)
    if processed > 40000:  # Google recommends max 50k URLs per sitemap
        generate_sitemap_index(processed)
    
    # Show file size
    file_size = os.path.getsize(sitemap_path) / (1024 * 1024)  # MB
    print(f"📏 File size: {file_size:.2f} MB")
    
    print(f"\n🌐 Next steps:")
    print(f"1. Upload sitemap.xml to your website root")
    print(f"2. Add to robots.txt: Sitemap: {BASE_URL}/sitemap.xml")
    print(f"3. Submit to Google Search Console")
    print(f"4. Submit to Bing Webmaster Tools")

def generate_sitemap_index(total_cards):
    """Generate sitemap index for large sites"""
    print("📚 Generating sitemap index for large site...")
    
    BASE_URL = "https://mtgabyss.com"
    
    sitemapindex = ET.Element('sitemapindex')
    sitemapindex.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # Calculate number of sitemaps needed (40k cards per sitemap)
    cards_per_sitemap = 40000
    num_sitemaps = (total_cards + cards_per_sitemap - 1) // cards_per_sitemap
    
    for i in range(num_sitemaps):
        sitemap_elem = ET.SubElement(sitemapindex, 'sitemap')
        sitemap_url = f"{BASE_URL}/sitemap_{i+1}.xml"
        ET.SubElement(sitemap_elem, 'loc').text = sitemap_url
        ET.SubElement(sitemap_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    
    # Write sitemap index
    tree = ET.ElementTree(sitemapindex)
    ET.indent(tree, space="  ", level=0)
    tree.write('sitemap_index.xml', encoding='utf-8', xml_declaration=True)
    
    print(f"✅ Sitemap index created: sitemap_index.xml")
    print(f"📚 Number of sitemaps: {num_sitemaps}")

def validate_sitemap():
    """Basic validation of the generated sitemap"""
    try:
        tree = ET.parse('sitemap.xml')
        root = tree.getroot()
        
        url_count = len(root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'))
        print(f"✅ Sitemap validation passed")
        print(f"📊 Total URLs found: {url_count:,}")
        
        # Check for common issues
        urls = [elem.text for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        unique_urls = set(urls)
        
        if len(urls) != len(unique_urls):
            print(f"⚠️  Warning: {len(urls) - len(unique_urls)} duplicate URLs found")
        else:
            print(f"✅ No duplicate URLs found")
        
        # Check URL format
        invalid_urls = [url for url in urls if not url.startswith('http')]
        if invalid_urls:
            print(f"❌ {len(invalid_urls)} invalid URLs found (not starting with http)")
        else:
            print(f"✅ All URLs properly formatted")
            
    except Exception as e:
        print(f"❌ Sitemap validation failed: {e}")

if __name__ == "__main__":
    print("🗺️  MTG Card Sitemap Generator")
    print("=" * 50)
    
    try:
        generate_sitemap()
        validate_sitemap()
        
        print("\n🎉 Sitemap generation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n🛑 Sitemap generation cancelled")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)