#!/usr/bin/env python

import codecs
import os
import re
import sys
from datetime import datetime, timedelta, tzinfo
from glob import glob
from urllib.request import urlretrieve
from urllib.parse import urljoin, urlparse
from xml.etree.ElementTree import ElementTree, TreeBuilder

import yaml
from bs4 import BeautifulSoup

from html2text import html2text_file

'''
exitwp - Wordpress xml exports to Jekykll blog format conversion

Tested with Wordpress 3.3.1 and jekyll 0.11.2

'''
######################################################
# Configuration
######################################################
with open('config.yaml', 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.SafeLoader)

wp_exports = glob(config['wp_exports'] + '/*.xml')  # Load XML files from config
build_dir = config['build_dir']
download_images = config['download_images']
target_format = config['target_format']
taxonomy_filter = set(config['taxonomies']['filter'])
taxonomy_entry_filter = config['taxonomies']['entry_filter']
taxonomy_name_mapping = config['taxonomies']['name_mapping']
item_type_filter = set(config['item_type_filter'])
item_field_filter = config['item_field_filter']
date_fmt = config['date_format']
body_replace = config['body_replace']

print(f'Looking for XML files in: {wp_exports}')  # Debugging print

# Time definitions
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# UTC support
class UTC(tzinfo):
    """UTC."""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return ZERO


def parse_wp_xml(file):
    tree = ElementTree()  # Initialize the ElementTree parser
    print(f'Reading XML file: {file}')  # Debugging print statement
    root = tree.parse(file)  # Parse the XML file

    # Define known namespaces (you can add more as needed)
    ns = {
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'wp': 'http://wordpress.org/export/1.2/',
    }

    c = root.find('channel')

    def parse_header():
        return {
            'title': str(c.find('title').text),
            'link': str(c.find('link').text),
            'description': str(c.find('description').text)
        }

    def parse_items():
        export_items = []
        xml_items = c.findall('item')
        print(f'Found {len(xml_items)} items in XML.')  # Debugging print statement

        for i in xml_items:
            taxanomies = i.findall('category')
            export_taxanomies = {}
            for tax in taxanomies:
                if 'domain' not in tax.attrib:
                    continue
                t_domain = str(tax.attrib['domain'])
                t_entry = str(tax.text)
                if (not (t_domain in taxonomy_filter) and
                    not (t_domain in taxonomy_entry_filter and
                         taxonomy_entry_filter[t_domain] == t_entry)):
                    if t_domain not in export_taxanomies:
                        export_taxanomies[t_domain] = []
                    export_taxanomies[t_domain].append(t_entry)

            def gi(q, unicode_wrap=True, empty=False):
                namespace = ''
                tag = ''
                if q.find(':') > 0:
                    namespace, tag = q.split(':', 1)
                else:
                    tag = q
                
                # Handle missing namespaces by defaulting to just the tag if the namespace isn't found
                try:
                    if namespace in ns:
                        result_element = i.find(f'{{{ns[namespace]}}}{tag}', ns)
                    else:
                        result_element = i.find(tag)
                    
                    # Handle cases where the element is not found or is None
                    if result_element is not None and result_element.text is not None:
                        result = result_element.text.strip()
                    else:
                        result = 'No Content Found' if not empty else ''
                except AttributeError:
                    result = 'No Content Found'
                    if empty:
                        result = ''
                
                if unicode_wrap:
                    result = str(result)
                
                return result

            body = gi('content:encoded')
            for key in body_replace:
                body = re.sub(key, body_replace[key], body)

            img_srcs = []
            if body is not None:
                try:
                    soup = BeautifulSoup(body, 'html.parser')
                    img_tags = soup.find_all('img')
                    for img in img_tags:
                        img_srcs.append(img['src'])
                except:
                    print('could not parse html: ' + body)

            excerpt = gi('excerpt:encoded', empty=True)

            export_item = {
                'title': gi('title'),
                'link': gi('link'),
                'author': gi('dc:creator'),
                'date': gi('wp:post_date_gmt'),
                'slug': gi('wp:post_name'),
                'status': gi('wp:status'),
                'type': gi('wp:post_type'),
                'wp_id': gi('wp:post_id'),
                'parent': gi('wp:post_parent'),
                'comments': gi('wp:comment_status') == 'open',
                'taxanomies': export_taxanomies,
                'body': body,
                'excerpt': excerpt,
                'img_srcs': img_srcs
            }

            print(f"Added item: {export_item['title']}")  # Debugging print statement

            export_items.append(export_item)

        return export_items

    return {
        'header': parse_header(),
        'items': parse_items(),
    }

# The get_item_uid function to handle unique file names for posts/pages
def get_item_uid(item, item_uids, date_prefix=False, namespace=''):
    result = None
    if namespace not in item_uids:
        item_uids[namespace] = {}

    # Check for the uid (based on wp_id) instead of namespace alone
    if item['wp_id'] in item_uids[namespace]:
        result = item_uids[namespace][item['wp_id']]
    else:
        uid = []
        if date_prefix:
            try:
                dt = datetime.strptime(item['date'], date_fmt)
            except:
                dt = datetime.today()
                print('Wrong date in', item['title'])
            uid.append(dt.strftime('%Y-%m-%d'))
            uid.append('-')
        s_title = item['slug']
        if s_title is None or s_title == '':
            s_title = item['title']
        if s_title is None or s_title == '':
            s_title = 'untitled'
        s_title = s_title.replace(' ', '_')
        s_title = re.sub('[^a-zA-Z0-9_-]', '', s_title)
        uid.append(s_title)
        fn = ''.join(uid)
        n = 1
        while fn in item_uids[namespace]:  # Check if the uid already exists
            n += 1
            fn = ''.join(uid) + '_' + str(n)
        item_uids[namespace][item['wp_id']] = fn  # Save the new uid
        result = fn
    return result

# Define the get_item_path function to generate paths for the items
def get_item_path(item, dir=''):
    full_dir = os.path.normpath(build_dir + '/' + dir)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
    filename_parts = [full_dir, '/']
    filename_parts.append(item['uid'])
    if item['type'] == 'page':
        if not os.path.exists(''.join(filename_parts)):
            os.makedirs(''.join(filename_parts))
        filename_parts.append('/index')
    filename_parts.append('.')
    filename_parts.append(target_format)
    return ''.join(filename_parts)

def write_jekyll(data, target_format):

    sys.stdout.write('Writing files...\n')  # Debugging print
    item_uids = {}
    attachments = {}

    def get_blog_path(data, path_infix='jekyll'):
        name = data['header']['link']
        name = re.sub('^https?', '', name)
        name = re.sub('[^A-Za-z0-9_.-]', '', name)
        return os.path.normpath(build_dir + '/' + path_infix + '/' + name)

    blog_dir = get_blog_path(data)

    def get_full_dir(dir):
        full_dir = os.path.normpath(blog_dir + '/' + dir)
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)
        print(f'Writing file to {full_dir}')  # Debugging print
        return full_dir

    def open_file(file):
        f = codecs.open(file, 'w', encoding='utf-8')
        return f

    for i in data['items']:
        skip_item = False

        for field, value in item_field_filter.items():
            if(i[field] == value):
                skip_item = True
                break

        if(skip_item):
            continue

        sys.stdout.write('.')
        sys.stdout.flush()
        out = None
        try:
            date = datetime.strptime(i['date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC())
        except:
            date = datetime.today()
            print('Wrong date in', i['title'])
        yaml_header = {
            'title': i['title'],
            'link': i['link'],
            'author': i['author'],
            'date': date,
            'slug': i['slug'],
            'wordpress_id': int(i['wp_id']),
            'comments': i['comments'],
        }
        if len(i['excerpt']) > 0:
            yaml_header['excerpt'] = i['excerpt']
        if i['status'] != 'publish':
            yaml_header['published'] = False

        if i['type'] == 'post':
            i['uid'] = get_item_uid(i, item_uids, date_prefix=True)  # Pass item_uids to get_item_uid
            fn = get_item_path(i, dir='_posts')
            out = open_file(fn)
            yaml_header['layout'] = 'post'
        elif i['type'] == 'page':
            i['uid'] = get_item_uid(i, item_uids)  # Pass item_uids to get_item_uid
            parentpath = ''
            item = i
            while item['parent'] != '0':
                item = next((parent for parent in data['items']
                             if parent['wp_id'] == item['parent']), None)
                if item:
                    parentpath = get_item_uid(item, item_uids) + '/' + parentpath
                else:
                    break
            fn = get_item_path(i, parentpath)
            out = open_file(fn)
            yaml_header['layout'] = 'page'
        elif i['type'] in item_type_filter:
            pass
        else:
            print('Unknown item type:', i['type'])

        if download_images:
            for img in i['img_srcs']:
                try:
                    urlretrieve(urljoin(data['header']['link'],
                                        img.encode('utf-8')),
                                get_attachment_path(img, i['uid']))
                except:
                    print('\n unable to download', urljoin(
                        data['header']['link'], img.encode('utf-8')))

        if out is not None:
            def toyaml(data):
                return yaml.safe_dump(data, allow_unicode=True,
                                      default_flow_style=False)

            tax_out = {}
            for taxonomy in i['taxanomies']:
                for tvalue in i['taxanomies'][taxonomy]:
                    t_name = taxonomy_name_mapping.get(taxonomy, taxonomy)
                    if t_name not in tax_out:
                        tax_out[t_name] = []
                    if tvalue in tax_out[t_name]:
                        continue
                    tax_out[t_name].append(tvalue)

            out.write('---\n')
            if len(yaml_header) > 0:
                out.write(toyaml(yaml_header))
            if len(tax_out) > 0:
                out.write(toyaml(tax_out))

            out.write('---\n\n')
            try:
                out.write(html2fmt(i['body'], target_format))
            except:
                print('\n Parse error on:', i['title'])

            out.close()
    print('\n')

wp_exports = glob(config['wp_exports'] + '/*.xml')
for wpe in wp_exports:
    data = parse_wp_xml(wpe)
    write_jekyll(data, target_format)

print('done')
