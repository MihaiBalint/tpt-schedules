#!/usr/bin/env python

import contextlib
import cssselect
import lxml.html
import re
import requests
from subprocess import call

known_pdfs = [
    '13a.pdf', '13b.pdf', '21a.pdf', '21b.pdf', '22a.pdf', '22b.pdf',
    '28a.pdf', '28b.pdf', '29a.pdf', '29b.pdf', '32a.pdf', '32b.pdf',
    '33.pdf', '33b-a.pdf', '33b-b.pdf', '40.pdf', '46a.pdf', '46b.pdf',
    '8b-a.pdf', '8b-b.pdf', 'e1a.pdf', 'e1b.pdf', 'e2a.pdf', 'e2b.pdf',
    'e3a.pdf', 'e3b.pdf', 'e4a.pdf', 'e4b.pdf', 'e4b-a.pdf', 'e4b-b.pdf',
    'e6.pdf', 'e6a.pdf', 'e6b.pdf', 'e7a.pdf', 'e7b.pdf',
    'e8a.pdf', 'e8b.pdf', 'm30.pdf', 'm35a.pdf', 'm35b.pdf',
    'm43a.pdf', 'm43b.pdf', 'm44.pdf', 'm45a.pdf', 'm45b.pdf']


def download_known_pdfs():
    for pdf in known_pdfs:
        r = requests.get('http://www.ratt.ro/grafice/{0}'.format(pdf),
                         stream=True)
        if not r.ok:
            print 'Failed for {0} with {1}'.format(pdf, r.status_code)
            continue
        with contextlib.closing(open("pdfs/{0}".format(pdf), "wb")) as f:
            for piece in r.iter_content(chunk_size=2048):
                if piece:
                    f.write(piece)
                    f.flush()


def convert_known_pdfs():
    for pdf in known_pdfs:
        call(['pdftotext', '-layout', '-q',
              'pdfs/{0}'.format(pdf),
              'txts/{0}.txt'.format(pdf)])


def parse_download_html(download_html):
    document = lxml.html.fromstring(download_html)
    expression = cssselect.GenericTranslator().css_to_xpath(
        'a[href^="/grafice/"][href$=".pdf"]')
    return sorted(set(a.get('href')[9:] for a in document.xpath(expression)))


def parse_grafice_html(grafice_html):
    matches = re.finditer('\'/grafice/.*\.pdf\'', grafice_html)
    results = [str(m.group(0)[10:-1]) for m in matches]
    # import ipdb; ipdb.set_trace()
    return sorted(set(results))


def compare_report(download_html, grafice_html):
    known = set(known_pdfs)
    print 'Comparing known_pdfs with download.html'
    print '\t    known_pdfs unique: {0}'.format(
        ', '.join(known - set(download_html)))
    print '\t download.html unique: {0}'.format(
        ', '.join(set(download_html) - known))

    print 'Comparing known_pdfs with grafice_XXX.html'
    print '\t    known_pdfs unique: {0}'.format(
        ', '.join(known - set(grafice_html)))
    print '\t grafice_.html unique: {0}'.format(
        ', '.join(set(grafice_html) - known))

    print 'Comparing grafice_XXX.html with download.html'
    print '\t grafice_.html unique: {0}'.format(
        ', '.join(set(grafice_html) - set(download_html)))
    print '\t download.html unique: {0}'.format(
        ', '.join(set(download_html) - set(grafice_html)))

    published = set(list(download_html) + list(grafice_html))
    print 'Comparing known_pdfs with published'
    print '\t known_pdfs unique: {0}'.format(
        ', '.join(known - published))
    print '\t  published unique: {0}'.format(
        ', '.join(published - known))
    return published != known


def main():
    d1 = parse_download_html(requests.get(
        'http://www.ratt.ro/download.html').text)
    d2 = parse_grafice_html(requests.get(
        'http://www.ratt.ro/grafice_scoala.html').text)
    if compare_report(d1, d2):
        print 'Exiting...'
        exit(1)
    download_known_pdfs()
    convert_known_pdfs()

if __name__ == '__main__':
    main()
