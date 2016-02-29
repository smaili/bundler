# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
#
#     /$$$$$$$                            /$$ /$$                    
#    | $$__  $$                          | $$| $$                    
#    | $$  \ $$ /$$   /$$ /$$$$$$$   /$$$$$$$| $$  /$$$$$$   /$$$$$$ 
#    | $$$$$$$ | $$  | $$| $$__  $$ /$$__  $$| $$ /$$__  $$ /$$__  $$
#    | $$__  $$| $$  | $$| $$  \ $$| $$  | $$| $$| $$$$$$$$| $$  \__/
#    | $$  \ $$| $$  | $$| $$  | $$| $$  | $$| $$| $$_____/| $$      
#    | $$$$$$$/|  $$$$$$/| $$  | $$|  $$$$$$$| $$|  $$$$$$$| $$      
#    |_______/  \______/ |__/  |__/ \_______/|__/ \_______/|__/
#
#     bundler.py
#     This is the main python file for bundling css and js assets
#     and deploying.
#
#   Java     sudo apt-get install default-jre
#   YUI      http://tml.github.io/yui/yuicompressor-2.4.8.jar
#   Closure  http://dl.google.com/closure-compiler/compiler-latest.zip
#   Poster   http://pypi.python.org/pypi/poster/
#
#------------------------------------------------------------------------


# Imports
#------------------------------------------------------------------------
import config, glob, os, poster, subprocess, sys, urllib2
execfile(config.APP_CONFIG)



# Functions
#------------------------------------------------------------------------
def compile_it(asset_type, src, dst):
    if asset_type == 'css':
        subprocess.call(['java', '-jar', config.CSS_COMPILER, src, '--type', 'css', '-o', dst ])
    else:
        subprocess.call(['java', '-jar', config.JS_COMPILER, '--compilation_level', 'ADVANCED_OPTIMIZATIONS', '--warning_level', 'QUIET', '--js', src, '--js_output_file', dst ])


def bundle_it(asset_type, page, files):
    filename = "%s/%s/%s.%s" % ( config.TEMP, asset_type, page, asset_type )
    f = open(filename, 'w')
    for asset in files:
        asset_filename = "%s%s_dev/%s.%s" % ( config.ASSETS, asset_type, asset, asset_type )
        with open(asset_filename, 'r') as asset_file:
            for line in asset_file:
                f.write(line)
    f.close()

    tmp_filename = "%s/%s/%s.min.%s" % ( config.TEMP, asset_type, page, asset_type )
    compile_it(asset_type, filename, tmp_filename)
    os.rename(tmp_filename, filename)


def deploy():
    files = glob.glob( config.TEMP + '/css/*' ) + glob.glob( config.TEMP + '/js/*' )

    for f in files:
        print "Uploading for file " + f
        upload(f)
        print "Uploading complete"
    remove(config.TEMP, False)


def upload(page):
    try:
        opener = poster.streaminghttp.register_openers()
        params = { 'u': config.DEPLOY_U, 'p': config.DEPLOY_P, 'f': open( page, 'rb' ) }
        datagen, headers = poster.encode.multipart_encode(params)
        response = opener.open( urllib2.Request( config.DEPLOY_URL, datagen, headers ), timeout=config.DEPLOY_TIMEOUT )
        #response.read()
    except:
        print "There was an error. Trying again..."
        upload(page)


def remove(name, confirm=True):
    if confirm and os.path.exists(name):
        print "Delete %s? y|n" % name
        while True:
            s = raw_input()
            if s in [ 'y', 'Y' ]:
                subprocess.call(['rm', '-fr', name ])
            break
    else:
        subprocess.call(['rm', '-fr', name ])


def bundle(asset, pages):
    if pages == 'all':
        pages = PAGES.keys()

    remove(config.TEMP)
    os.mkdir(config.TEMP)

    print ""
    print "Bundling %s assets for pages %s" % ( asset, ', '.join(pages) )
    print ""

    if asset == 'css' or asset == 'both':
        os.mkdir(config.TEMP + '/css')
        for page in pages:
            if page in PAGES_CSS:
                bundle_it( 'css', page, PAGES_CSS[page] )

    if asset == 'js' or asset == 'both':
        os.mkdir(config.TEMP + '/js')
        for page in pages:
            if page in PAGES_JS:
                bundle_it( 'js', page, PAGES_JS[page] )

    print "Bundle complete. Now deploying..."
    print ""
    deploy()
    print ""
    print "Deploying complete"
    print ""



# Main
#------------------------------------------------------------------------
if __name__=="__main__":
    try:
        args = sys.argv
        asset = args[1]
        pages = args[2]
        if pages != 'all':
            pages = []
            for i in range(2, len(args)):
                pages.append( args[i] )

        bundle(asset, pages)

    except:
        print ""
        print "To use: python bundle.py [css|js|both] <page>, <page>, ... , <page>"
        print ""